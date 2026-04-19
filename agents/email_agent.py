"""
agents/email_agent.py
----------------------
Handles everything related to emails:
- Drafts professional follow-up emails
- Creates subject lines
- Formats email body
- Adds proper greeting and signature
Extends BaseAgent
"""

from agents.base_agent import BaseAgent
from langchain_groq import ChatGroq
from memory.memory_store import MemoryStore
from tools.email_tool import EmailTool


class EmailAgent(BaseAgent):
    """
    Email Agent — Specializes in:
    - Drafting professional emails
    - Writing clear subject lines
    - Structuring email body
    - Adding call to action
    - Professional tone and signature
    """

    def __init__(self, llm: ChatGroq, memory: MemoryStore):
        super().__init__(llm=llm, memory=memory)

    # ---------------------------
    # Agent Name
    # ---------------------------
    @property
    def agent_name(self) -> str:
        return "EmailAgent"

    # ---------------------------
    # Register Tools
    # ---------------------------
    def _register_tools(self):
        """
        EmailAgent uses EmailTool
        to send drafted emails via Gmail API.
        """
        self.tools.append(EmailTool())

    # ---------------------------
    # Detect Email Tone
    # ---------------------------
    def _detect_tone(self, input_data: str) -> str:
        """
        Detects the required tone based on input keywords.

        Returns:
            str : "formal", "friendly", or "urgent"
        """
        input_lower = input_data.lower()

        if any(word in input_lower for word in ["urgent", "asap", "immediately", "critical"]):
            return "urgent"
        elif any(word in input_lower for word in ["team", "colleague", "hi", "hey"]):
            return "friendly"
        else:
            return "formal"

    # ---------------------------
    # Build Prompt
    # ---------------------------
    def _build_prompt(self, input_data: str, tone: str) -> str:
        """
        Builds a structured prompt for the LLM
        specifically designed for email drafting.
        """
        tone_instruction = {
            "formal": "Use a formal, professional business tone.",
            "friendly": "Use a warm, friendly but still professional tone.",
            "urgent": "Use a clear, direct, and urgent tone while remaining professional."
        }.get(tone, "Use a professional tone.")

        return f"""
You are an expert Email Communication AI agent.

Your job is to draft a complete, professional email based on
the following request. {tone_instruction}

User Request:
{input_data}

Your response MUST follow this exact structure:

## 📧 Drafted Email

**Subject:** [Write a clear, specific subject line]

---

Dear [Recipient Name/Team],

[Opening paragraph — state the purpose clearly in 1-2 sentences]

[Main body — key points, information, or requests. Use bullet points if multiple items.]

[Closing paragraph — summarize what you need from them or what happens next]

[Call to Action — specific action you want the recipient to take]

Best regards,
[Your Name]
[Your Title]
[Your Contact Information]

---

**📝 Email Notes:**
- Tone Used: {tone.capitalize()}
- Estimated Read Time: [X seconds/minutes]
- Priority Level: [High/Medium/Low]
- Suggested Send Time: [Immediate/Morning/Afternoon]

Make the email clear, actionable, and appropriately concise.
"""

    # ---------------------------
    # Core Run Method
    # ---------------------------
    def run(self, input_data: str) -> str:
        """
        Main logic for EmailAgent.

        Steps:
        1. Detect required email tone
        2. Build email-specific prompt
        3. Call Groq LLM
        4. Return complete drafted email

        Args:
            input_data : User's email request or context

        Returns:
            str : Complete drafted email with subject and body
        """
        # Detect tone from input
        tone = self._detect_tone(input_data)

        # Build the email-specific prompt
        prompt = self._build_prompt(input_data, tone)

        # Call Groq LLM using base class helper
        result = self._call_llm(prompt)

        return result