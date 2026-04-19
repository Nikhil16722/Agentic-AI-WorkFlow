"""
agents/task_agent.py
---------------------
Handles everything related to task management:
- Creates structured task lists
- Assigns priorities
- Estimates time
- Suggests owners
- Identifies dependencies
Extends BaseAgent
"""

from agents.base_agent import BaseAgent
from langchain_groq import ChatGroq
from memory.memory_store import MemoryStore
from tools.slack_tool import SlackTool


class TaskAgent(BaseAgent):
    """
    Task Agent — Specializes in:
    - Breaking down complex goals into tasks
    - Assigning priority levels (High/Medium/Low)
    - Estimating time for each task
    - Suggesting task owners
    - Identifying task dependencies
    - Sending task notifications via Slack
    """

    def __init__(self, llm: ChatGroq, memory: MemoryStore):
        super().__init__(llm=llm, memory=memory)

    # ---------------------------
    # Agent Name
    # ---------------------------
    @property
    def agent_name(self) -> str:
        return "TaskAgent"

    # ---------------------------
    # Register Tools
    # ---------------------------
    def _register_tools(self):
        """
        TaskAgent uses SlackTool
        to notify team members about new tasks.
        """
        self.tools.append(SlackTool())

    # ---------------------------
    # Detect Complexity
    # ---------------------------
    def _detect_complexity(self, input_data: str) -> str:
        """
        Detects task complexity from input.

        Returns:
            str : "simple", "medium", or "complex"
        """
        input_lower = input_data.lower()
        word_count = len(input_lower.split())

        if word_count < 15:
            return "simple"
        elif word_count < 40:
            return "medium"
        else:
            return "complex"

    # ---------------------------
    # Build Prompt
    # ---------------------------
    def _build_prompt(self, input_data: str, complexity: str) -> str:
        """
        Builds a structured prompt for the LLM
        specifically designed for task management.
        """
        complexity_instruction = {
            "simple": "Create 3-5 clear, straightforward tasks.",
            "medium": "Create 5-8 well-structured tasks with subtasks where needed.",
            "complex": "Create 8-12 detailed tasks with subtasks, dependencies, and milestones."
        }.get(complexity, "Create a comprehensive task list.")

        return f"""
You are an expert Task Management AI agent.

Your job is to analyze the following request and create a structured,
actionable task list. {complexity_instruction}

User Request:
{input_data}

Your response MUST follow this exact structure:

## ✅ Task Breakdown

**Project/Goal:** [Extract or summarize the main goal]
**Total Estimated Time:** [Sum of all tasks]
**Complexity Level:** {complexity.capitalize()}

---

### 🔴 High Priority Tasks
| # | Task | Owner | Est. Time | Deadline |
|---|------|-------|-----------|----------|
| 1 | [Task name] | [Team/Person] | [Xh/Xd] | [Date] |

### 🟡 Medium Priority Tasks
| # | Task | Owner | Est. Time | Deadline |
|---|------|-------|-----------|----------|
| 1 | [Task name] | [Team/Person] | [Xh/Xd] | [Date] |

### 🟢 Low Priority Tasks
| # | Task | Owner | Est. Time | Deadline |
|---|------|-------|-----------|----------|
| 1 | [Task name] | [Team/Person] | [Xh/Xd] | [Date] |

---

### 🔗 Task Dependencies
- [Task A] must be completed before [Task B]
- [Task C] depends on [Task D]

### 📊 Progress Tracking Milestones
1. **Milestone 1:** [Description] — Target: [Date]
2. **Milestone 2:** [Description] — Target: [Date]
3. **Final Milestone:** [Description] — Target: [Date]

### 💡 Recommendations
- [Recommendation 1 for faster completion]
- [Recommendation 2 for better efficiency]
- [Risk or blocker to watch out for]

Be specific, realistic with time estimates, and practical in your recommendations.
"""

    # ---------------------------
    # Core Run Method
    # ---------------------------
    def run(self, input_data: str) -> str:
        """
        Main logic for TaskAgent.

        Steps:
        1. Detect task complexity
        2. Build task-specific prompt
        3. Call Groq LLM
        4. Return structured task list

        Args:
            input_data : User's goal or project description

        Returns:
            str : Structured task list with priorities,
                  owners, estimates, and milestones
        """
        # Detect complexity of the request
        complexity = self._detect_complexity(input_data)

        # Build the task-specific prompt
        prompt = self._build_prompt(input_data, complexity)

        # Call Groq LLM using base class helper
        result = self._call_llm(prompt)

        return result