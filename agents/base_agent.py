"""
agents/base_agent.py
---------------------
Parent class for ALL agents in the system.
Every agent (Meeting, Email, Task) extends this class.

Rules:
- Every agent MUST have tools + memory
- Every agent MUST implement run() method
- Every agent logs its actions automatically
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from langchain_groq import ChatGroq
from memory.memory_store import MemoryStore

# ---------------------------
# Logger Setup
# ---------------------------
logging.basicConfig(
    filename="logs/agent_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ---------------------------
# BaseAgent Class
# ---------------------------
class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Every child agent (MeetingAgent, EmailAgent, TaskAgent)
    MUST extend this class and implement:
        - run(input_data) method
        - agent_name property

    Built-in features:
        - LLM access (Groq)
        - Memory access (Supabase)
        - Tool registration
        - Automatic logging
        - Error handling
        - Input validation
        - Result formatting
    """

    def __init__(self, llm: ChatGroq, memory: MemoryStore):
        """
        Initialize base agent with LLM and memory.

        Args:
            llm      : Groq LLM instance from WorkflowManager
            memory   : MemoryStore instance for save/get/get_all
        """
        self.llm = llm
        self.memory = memory
        self.tools = []               # List of tools this agent can use
        self.last_run_time = None     # Timestamp of last execution
        self.run_count = 0            # How many times this agent has run
        self.last_result = None       # Stores last output

        # Register tools when agent is created
        self._register_tools()

        logger.info(f"[{self.agent_name}] Agent initialized.")

    # ---------------------------
    # Agent Name (Must Override)
    # ---------------------------
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """
        Every child agent must define its own name.

        Example:
            @property
            def agent_name(self):
                return "MeetingAgent"
        """
        pass

    # ---------------------------
    # Run Method (Must Override)
    # ---------------------------
    @abstractmethod
    def run(self, input_data: str) -> str:
        """
        Core execution method.
        Every child agent must implement this.

        Args:
            input_data : The task/prompt from WorkflowManager

        Returns:
            str        : The agent's output/result

        Example:
            def run(self, input_data):
                result = self.llm.invoke(input_data)
                return result.content
        """
        pass

    # ---------------------------
    # Register Tools (Override if needed)
    # ---------------------------
    def _register_tools(self):
        """
        Register tools this agent can use.
        Child agents override this to add their specific tools.

        Example in EmailAgent:
            def _register_tools(self):
                self.tools.append(EmailTool())
        """
        pass  # Base has no tools — child agents add theirs

    # ---------------------------
    # Safe Execute (Wraps run())
    # ---------------------------
    def execute(self, input_data: str) -> dict:
        """
        Safe wrapper around run().
        Handles:
            - Input validation
            - Logging before and after
            - Error catching
            - Memory saving
            - Result formatting

        Args:
            input_data : Raw input string

        Returns:
            dict : {
                "agent"     : agent name,
                "status"    : "success" or "failed",
                "output"    : result string,
                "timestamp" : execution time,
                "run_count" : how many times run
            }
        """
        # Validate input
        if not input_data or not input_data.strip():
            logger.warning(f"[{self.agent_name}] Empty input received.")
            return self._format_result(
                status="failed",
                output="Error: Input cannot be empty."
            )

        # Log start
        logger.info(f"[{self.agent_name}] Starting execution...")
        logger.info(f"[{self.agent_name}] Input: {input_data[:100]}...")

        try:
            # Track run time
            self.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.run_count += 1

            # Call child agent's run() method
            output = self.run(input_data)

            # Store in memory
            self._save_to_memory(input_data, output)

            # Store last result
            self.last_result = output

            # Log success
            logger.info(f"[{self.agent_name}] Execution successful. Run #{self.run_count}")

            return self._format_result(
                status="success",
                output=output
            )

        except Exception as e:
            error_msg = f"[{self.agent_name}] Execution failed: {str(e)}"
            logger.error(error_msg)

            return self._format_result(
                status="failed",
                output=f"Error: {str(e)}"
            )

    # ---------------------------
    # Save Result to Memory
    # ---------------------------
    def _save_to_memory(self, input_data: str, output: str):
        """
        Automatically saves every agent result to memory.
        Uses agent name + timestamp as unique key.

        Args:
            input_data : What was passed to the agent
            output     : What the agent produced
        """
        memory_key = f"{self.agent_name}_{self.last_run_time}"
        memory_value = {
            "agent": self.agent_name,
            "input": input_data,
            "output": output,
            "timestamp": self.last_run_time,
            "run_number": self.run_count
        }

        self.memory.save(key=memory_key, value=memory_value)
        logger.info(f"[{self.agent_name}] Result saved to memory: {memory_key}")

    # ---------------------------
    # Format Result
    # ---------------------------
    def _format_result(self, status: str, output: str) -> dict:
        """
        Formats agent result into a standard dictionary.
        WorkflowManager and UI use this structure.

        Args:
            status : "success" or "failed"
            output : The result string

        Returns:
            dict : Standardized result object
        """
        return {
            "agent": self.agent_name,
            "status": status,
            "output": output,
            "timestamp": self.last_run_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "run_count": self.run_count
        }

    # ---------------------------
    # Call LLM Directly
    # ---------------------------
    def _call_llm(self, prompt: str) -> str:
        """
        Helper method to call the Groq LLM directly.
        Child agents use this inside their run() method.

        Args:
            prompt : The prompt to send to Groq

        Returns:
            str : LLM response text
        """
        logger.info(f"[{self.agent_name}] Calling Groq LLM...")
        response = self.llm.invoke(prompt)
        logger.info(f"[{self.agent_name}] Groq LLM responded.")
        return response.content

    # ---------------------------
    # Get Past Results from Memory
    # ---------------------------
    def get_history(self) -> list:
        """
        Returns all past results for THIS agent from memory.

        Returns:
            list : All memory records where agent = self.agent_name
        """
        all_records = self.memory.get_all()
        agent_records = [
            record for record in all_records
            if record.get("agent") == self.agent_name
        ]
        return agent_records

    # ---------------------------
    # Agent Status Info
    # ---------------------------
    def get_status(self) -> dict:
        """
        Returns current status of this agent.
        Used by Streamlit sidebar to show agent info.

        Returns:
            dict : Agent status information
        """
        return {
            "agent_name": self.agent_name,
            "run_count": self.run_count,
            "last_run_time": self.last_run_time or "Never",
            "tools_available": len(self.tools),
            "tool_names": [tool.__class__.__name__ for tool in self.tools],
            "last_result_preview": (
                str(self.last_result)[:100] + "..."
                if self.last_result else "No runs yet"
            )
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self) -> str:
        return (
            f"{self.agent_name}("
            f"runs={self.run_count}, "
            f"tools={len(self.tools)}, "
            f"last_run={self.last_run_time or 'Never'})"
        )