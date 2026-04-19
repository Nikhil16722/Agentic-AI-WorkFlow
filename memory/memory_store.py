"""
memory/memory_store.py
-----------------------
Persistent memory system for all agents.
Connected to Supabase as the database.
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Optional

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="logs/agent_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Persistent memory for the entire agentic system.
    Storage: Supabase (PostgreSQL)
    Fallback: local in-memory dict if Supabase fails.
    """

    TABLE_NAME = "agent_memory"

    def __init__(self):
        self.supabase: Optional[Client] = None
        self._local_memory: dict = {}
        self._use_local = False
        self._connect_supabase()

    def _connect_supabase(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not found. Using local memory.")
            self._use_local = True
            return

        try:
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("Supabase connected successfully.")
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}. Using local memory.")
            self._use_local = True

    def save(self, key: str, value: Any) -> bool:
        serialized_value = (
            json.dumps(value) if isinstance(value, dict) else str(value)
        )
        agent_name = value.get("agent", "unknown") if isinstance(value, dict) else "unknown"

        if not self._use_local:
            try:
                self.supabase.table(self.TABLE_NAME).upsert({
                    "key": key,
                    "value": serialized_value,
                    "agent_name": agent_name,
                    "created_at": datetime.now().isoformat()
                }).execute()
                logger.info(f"[MemoryStore] Saved to Supabase: key='{key}'")
                return True
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase save failed: {e}.")
                self._use_local = True

        self._local_memory[key] = {
            "key": key,
            "value": serialized_value,
            "agent_name": agent_name,
            "created_at": datetime.now().isoformat()
        }
        logger.info(f"[MemoryStore] Saved to local memory: key='{key}'")
        return True

    def get(self, key: str) -> Optional[dict]:
        if not self._use_local:
            try:
                response = self.supabase.table(self.TABLE_NAME).select("*").eq("key", key).execute()
                if response.data:
                    record = response.data[0]
                    record["value"] = self._deserialize(record["value"])
                    return record
                return None
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase get failed: {e}.")
                self._use_local = True

        record = self._local_memory.get(key)
        if record:
            record["value"] = self._deserialize(record["value"])
            return record
        return None

    def get_all(self) -> list:
        if not self._use_local:
            try:
                response = self.supabase.table(self.TABLE_NAME).select("*").order("created_at", desc=True).execute()
                records = response.data or []
                for record in records:
                    record["value"] = self._deserialize(record["value"])
                return records
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase get_all failed: {e}.")
                self._use_local = True

        records = list(self._local_memory.values())
        records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        for record in records:
            record["value"] = self._deserialize(record["value"])
        return records

    def get_by_agent(self, agent_name: str) -> list:
        if not self._use_local:
            try:
                response = self.supabase.table(self.TABLE_NAME).select("*").eq("agent_name", agent_name).order("created_at", desc=True).execute()
                records = response.data or []
                for record in records:
                    record["value"] = self._deserialize(record["value"])
                return records
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase get_by_agent failed: {e}.")
                self._use_local = True

        records = [r for r in self._local_memory.values() if r.get("agent_name") == agent_name]
        for record in records:
            record["value"] = self._deserialize(record["value"])
        return records

    def delete(self, key: str) -> bool:
        if not self._use_local:
            try:
                self.supabase.table(self.TABLE_NAME).delete().eq("key", key).execute()
                logger.info(f"[MemoryStore] Deleted: key='{key}'")
                return True
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase delete failed: {e}.")
                self._use_local = True

        if key in self._local_memory:
            del self._local_memory[key]
            return True
        return False

    def clear_all(self) -> bool:
        if not self._use_local:
            try:
                self.supabase.table(self.TABLE_NAME).delete().neq("key", "").execute()
                logger.warning("[MemoryStore] ALL records cleared from Supabase.")
                return True
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase clear_all failed: {e}.")
                self._use_local = True

        self._local_memory.clear()
        logger.warning("[MemoryStore] ALL records cleared from local memory.")
        return True

    def count(self) -> int:
        if not self._use_local:
            try:
                response = self.supabase.table(self.TABLE_NAME).select("key", count="exact").execute()
                return response.count or 0
            except Exception as e:
                logger.error(f"[MemoryStore] Supabase count failed: {e}.")
                self._use_local = True

        return len(self._local_memory)

    def get_storage_mode(self) -> str:
        return "local" if self._use_local else "supabase"

    def _deserialize(self, value: str) -> Any:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def __repr__(self) -> str:
        return f"MemoryStore(mode={self.get_storage_mode()}, records={self.count()})"