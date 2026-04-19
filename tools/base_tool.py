"""
tools/base_tool.py
-------------------
Parent class for ALL tools in the system.
Every tool (EmailTool, CalendarTool, SlackTool)
extends this class.

Rules:
- Every tool MUST implement execute() method
- Every tool MUST have a tool_name property
- Every tool logs automatically
- Every tool handles dry run mode
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


# ---------------------------
# BaseTool Class
# ---------------------------
class BaseTool(ABC):
    """
    Abstract base class for all tools.

    Every child tool MUST implement:
        - tool_name  (property)
        - execute()  (method)

    Built-in features:
        - Automatic logging
        - Dry run mode detection
        - Result formatting
        - Error handling
        - Run counter
    """

    def __init__(self):
        self.run_count    = 0
        self.last_run     = None
        self.last_result  = None

        logger.info(f"[{self.tool_name}] Tool initialized.")

    # ---------------------------
    # Tool Name (Must Override)
    # ---------------------------
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """
        Every child tool must define its name.

        Example:
            @property
            def tool_name(self):
                return "EmailTool"
        """
        pass

    # ---------------------------
    # Execute (Must Override)
    # ---------------------------
    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """
        Core action method.
        Every child tool must implement this.

        Returns:
            dict : {
                "status"  : "success" | "dry_run" | "failed",
                "message" : description of what happened
            }
        """
        pass

    # ---------------------------
    # Is Live Mode
    # ---------------------------
    @abstractmethod
    def _is_live(self) -> bool:
        """
        Returns True if real credentials exist.
        Returns False if running in dry run mode.
        Child tools implement this based on their credentials.
        """
        pass

    # ---------------------------
    # Safe Run Wrapper
    # ---------------------------
    def safe_run(self, **kwargs) -> dict:
        """
        Safe wrapper around execute().
        Adds logging, error handling, run tracking.

        Returns:
            dict : Standardized result from execute()
        """
        logger.info(f"[{self.tool_name}] Running...")
        self.run_count += 1
        self.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            result = self.execute(**kwargs)
            self.last_result = result
            logger.info(f"[{self.tool_name}] Run #{self.run_count} complete. Status: {result.get('status')}")
            return result

        except Exception as e:
            error_result = self._format_result(
                status="failed",
                message=f"Unexpected error: {str(e)}"
            )
            logger.error(f"[{self.tool_name}] Run #{self.run_count} failed: {e}")
            return error_result

    # ---------------------------
    # Format Result
    # ---------------------------
    def _format_result(self, status: str, message: str, **extra) -> dict:
        """
        Formats tool result into standard structure.

        Args:
            status  : "success" | "dry_run" | "failed"
            message : Human readable description
            extra   : Any additional fields to include

        Returns:
            dict : Standardized result
        """
        result = {
            "tool": self.tool_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "run_count": self.run_count,
            "mode": "live" if self._is_live() else "dry_run"
        }
        result.update(extra)
        return result

    # ---------------------------
    # Get Status
    # ---------------------------
    def get_status(self) -> dict:
        """
        Returns current tool status.
        Used by Streamlit sidebar.

        Returns:
            dict : Tool status information
        """
        return {
            "tool_name": self.tool_name,
            "mode": "live" if self._is_live() else "dry_run",
            "run_count": self.run_count,
            "last_run": self.last_run or "Never"
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self) -> str:
        mode = "live" if self._is_live() else "dry_run"
        return f"{self.tool_name}(mode={mode}, runs={self.run_count})"