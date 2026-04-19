"""
memory/supabase_client.py
--------------------------
Supabase client singleton.
Shared across the entire project.
Import this wherever you need direct Supabase access.
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------
# Supabase Singleton
# ---------------------------
class SupabaseClient:
    """
    Single shared Supabase client instance.
    Used by MemoryStore and any other file
    that needs direct database access.

    Usage:
        from memory.supabase_client import get_supabase_client
        client = get_supabase_client()
        client.table("agent_memory").select("*").execute()
    """

    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Returns the shared Supabase client.
        Creates it once and reuses it.

        Returns:
            Client : Supabase client instance
                     or None if credentials missing
        """
        if cls._instance is not None:
            return cls._instance

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.warning(
                "[SupabaseClient] SUPABASE_URL or SUPABASE_KEY "
                "not found in .env. Returning None."
            )
            return None

        try:
            cls._instance = create_client(url, key)
            logger.info("[SupabaseClient] Connected successfully.")
            return cls._instance

        except Exception as e:
            logger.error(f"[SupabaseClient] Connection failed: {e}")
            return None

    @classmethod
    def reset(cls):
        """
        Resets the client instance.
        Useful for testing or reconnecting.
        """
        cls._instance = None
        logger.info("[SupabaseClient] Client reset.")


# ---------------------------
# Helper Function
# ---------------------------
def get_supabase_client() -> Client:
    """
    Quick helper to get Supabase client anywhere.

    Usage:
        from memory.supabase_client import get_supabase_client
        db = get_supabase_client()
    """
    return SupabaseClient.get_client()