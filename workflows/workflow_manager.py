"""
workflows/workflow_manager.py
------------------------------
Brain of the system — NO CrewAI dependency.
Uses LangChain + Groq directly.
Works on Python 3.14 / Streamlit Cloud.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from memory.memory_store import MemoryStore

load_dotenv()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/agent_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Central orchestrator.
    Detects intent → runs the right agent prompt → saves to memory.
    No CrewAI — uses LangChain + Groq directly.
    """

    def __init__(self):
        self.llm = self._load_llm()
        self.memory = MemoryStore()
        logger.info("WorkflowManager initialized.")

    def _load_llm(self) -> ChatGroq:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file.")
        return ChatGroq(
            api_key=groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0.4,
            max_tokens=2048
        )

    def _detect_intent(self, user_input: str) -> list:
        text = user_input.lower()
        agents = []
        if any(w in text for w in ["meeting", "schedule", "call", "invite", "summarize", "summary"]):
            agents.append("meeting")
        if any(w in text for w in ["email", "send", "follow up", "mail", "notify", "write"]):
            agents.append("email")
        if any(w in text for w in ["task", "assign", "todo", "action", "create", "list", "breakdown"]):
            agents.append("task")
        if not agents:
            agents = ["meeting", "email", "task"]
        logger.info(f"Intent detected: {agents}")
        return agents

    def _run_meeting_agent(self, user_input: str) -> str:
        system = SystemMessage(content="""You are an expert Meeting Coordinator AI.
Analyze the user's request and produce a structured meeting summary.
Always respond with this exact format:

## Meeting Summary

**Meeting Topic:** [topic]

**Key Discussion Points:**
- [point 1]
- [point 2]

**Decisions Made:**
- [decision 1]

**Action Items:**
| Task | Owner | Deadline |
|------|-------|----------|
| [task] | [person] | [date] |

**Next Steps:**
1. [step 1]
2. [step 2]""")
        human = HumanMessage(content=f"User Request: {user_input}")
        response = self.llm.invoke([system, human])
        return response.content

    def _run_email_agent(self, user_input: str) -> str:
        text = user_input.lower()
        tone = "urgent" if any(w in text for w in ["urgent", "asap", "immediately"]) else \
               "friendly" if any(w in text for w in ["team", "colleague", "hi"]) else "formal"

        system = SystemMessage(content=f"""You are an expert Email Communication AI.
Draft a complete professional email. Use a {tone} tone.
Always respond with this exact format:

## Drafted Email

**Subject:** [clear subject line]

Dear [Recipient],

[Opening paragraph]

[Main body with key points]

[Call to action]

Best regards,
[Your Name]
[Your Title]

---
**Email Notes:** Tone: {tone.capitalize()} | Priority: [High/Medium/Low]""")
        human = HumanMessage(content=f"User Request: {user_input}")
        response = self.llm.invoke([system, human])
        return response.content

    def _run_task_agent(self, user_input: str) -> str:
        system = SystemMessage(content="""You are an expert Task Management AI.
Break down the user's request into a structured, prioritized task list.
Always respond with this exact format:

## Task Breakdown

**Goal:** [main goal]
**Total Estimated Time:** [total]

### High Priority Tasks
| Task | Owner | Est. Time | Deadline |
|------|-------|-----------|----------|
| [task] | [owner] | [time] | [date] |

### Medium Priority Tasks
| Task | Owner | Est. Time | Deadline |
|------|-------|-----------|----------|
| [task] | [owner] | [time] | [date] |

### Low Priority Tasks
| Task | Owner | Est. Time | Deadline |
|------|-------|-----------|----------|
| [task] | [owner] | [time] | [date] |

### Milestones
1. [milestone 1]
2. [milestone 2]

### Recommendations
- [recommendation 1]
- [recommendation 2]""")
        human = HumanMessage(content=f"User Request: {user_input}")
        response = self.llm.invoke([system, human])
        return response.content

    def run(self, user_input: str) -> str:
        """Main entry point called by Streamlit UI."""
        try:
            logger.info(f"Workflow started: '{user_input[:80]}'")
            agents = self._detect_intent(user_input)
            outputs = []

            if "meeting" in agents:
                logger.info("Running MeetingAgent...")
                outputs.append(self._run_meeting_agent(user_input))

            if "email" in agents:
                logger.info("Running EmailAgent...")
                outputs.append(self._run_email_agent(user_input))

            if "task" in agents:
                logger.info("Running TaskAgent...")
                outputs.append(self._run_task_agent(user_input))

            result = "\n\n---\n\n".join(outputs)

            # Save to memory
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.memory.save(
                key=f"workflow_{ts}",
                value={
                    "input": user_input,
                    "agents_used": agents,
                    "output": result[:500],
                    "timestamp": ts,
                    "agent": "WorkflowManager"
                }
            )

            logger.info(f"Workflow completed. Agents used: {agents}")
            return result

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise Exception(f"Workflow failed: {str(e)}")

    def get_history(self) -> list:
        return self.memory.get_all()