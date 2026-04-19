"""
agents/meeting_agent.py
------------------------
Handles everything related to meetings:
- Summarizes meeting descriptions
- Extracts action items
- Identifies decisions made
- Lists next steps
Extends BaseAgent
"""

from agents.base_agent import BaseAgent
from langchain_groq import ChatGroq
from memory.memory_store import MemoryStore
from tools.calendar_tool import CalendarTool


class MeetingAgent(BaseAgent):
    """
    Meeting Agent — Specializes in:
    - Summarizing meetings
    - Extracting action items
    - Identifying key decisions
    - Suggesting next steps
    """

    def __init__(self, llm: ChatGroq, memory: MemoryStore):
        super().__init__(llm=llm, memory=memory)

    # ---------------------------
    # Agent Name
    # ---------------------------
    @property
    def agent_name(self) -> str:
        return "MeetingAgent"

    # ---------------------------
    # Register Tools
    # ---------------------------
    def _register_tools(self):
        """
        MeetingAgent uses CalendarTool
        to check and create calendar events.
        """
        self.tools.append(CalendarTool())

    # ---------------------------
    # Build Prompt
    # ---------------------------
    def _build_prompt(self, input_data: str) -> str:
        """
        Builds a structured prompt for the LLM
        specifically designed for meeting tasks.
        """
        return f"""
You are an expert Meeting Coordinator AI agent.

Your job is to analyze the following meeting request or description
and produce a structured, professional meeting summary.

User Input:
{input_data}

Your response MUST follow this exact structure:

## 📋 Meeting Summary

**Meeting Topic:** [Extract or infer the topic]

**Key Discussion Points:**
- [Point 1]
- [Point 2]
- [Point 3]

**Decisions Made:**
- [Decision 1]
- [Decision 2]

**Action Items:**
| # | Task | Owner | Deadline |
|---|------|-------|----------|
| 1 | [Task] | [Person/Team] | [Date/ASAP] |
| 2 | [Task] | [Person/Team] | [Date/ASAP] |

**Next Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Follow-up Meeting Needed:** [Yes/No — and suggested date if yes]

Be professional, concise, and actionable in your response.
"""

    # ---------------------------
    # Core Run Method
    # ---------------------------
    def run(self, input_data: str) -> str:
        """
        Main logic for MeetingAgent.

        Steps:
        1. Build structured meeting prompt
        2. Call Groq LLM
        3. Return formatted meeting summary

        Args:
            input_data : User's meeting description or request

        Returns:
            str : Formatted meeting summary
        """
        # Build the meeting-specific prompt
        prompt = self._build_prompt(input_data)

        # Call Groq LLM using base class helper
        result = self._call_llm(prompt)

        return result