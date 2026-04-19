"""
workflows/workflow_manager.py
------------------------------
The BRAIN of the Agentic AI Workflow System.
Orchestrates all agents using CrewAI + Groq.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from crewai import Crew, Task, Agent, Process
from langchain_groq import ChatGroq

from agents.meeting_agent import MeetingAgent
from agents.email_agent import EmailAgent
from agents.task_agent import TaskAgent
from memory.memory_store import MemoryStore

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

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
# WorkflowManager Class
# ---------------------------
class WorkflowManager:
    """
    Central orchestrator that:
    - Initializes the LLM (Groq)
    - Loads all agents
    - Decides which agents to trigger
    - Runs CrewAI workflow
    - Saves results to memory
    - Returns final output
    """

    def __init__(self):
        # Load Groq LLM
        self.llm = self._load_llm()

        # Initialize memory store
        self.memory = MemoryStore()

        # Initialize all agents (passing LLM + memory)
        self.meeting_agent = MeetingAgent(llm=self.llm, memory=self.memory)
        self.email_agent = EmailAgent(llm=self.llm, memory=self.memory)
        self.task_agent = TaskAgent(llm=self.llm, memory=self.memory)

        logger.info("WorkflowManager initialized successfully.")

    # ---------------------------
    # Load Groq LLM
    # ---------------------------
    def _load_llm(self) -> ChatGroq:
        """
        Loads the Groq LLM using API key from .env
        Model: llama3-8b-8192 (fast + free on Groq)
        """
        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not found. "
                "Please add it to your .env file."
            )

        llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.1-8b-instant",   # Free model on Groq
            temperature=0.4,           # Balanced creativity
            max_tokens=2048
        )

        logger.info("Groq LLM loaded: llama-3.1-8b-instant")
        return llm

    # ---------------------------
    # Detect Intent from User Input
    # ---------------------------
    def _detect_intent(self, user_input: str) -> list:
        """
        Reads user input and decides which agents to trigger.
        Returns a list of agent names to activate.

        Logic:
        - If 'meeting' or 'schedule' → MeetingAgent
        - If 'email' or 'send' or 'follow up' → EmailAgent
        - If 'task' or 'assign' or 'todo' → TaskAgent
        - Default → All agents
        """
        user_input_lower = user_input.lower()
        agents_to_run = []

        if any(word in user_input_lower for word in ["meeting", "schedule", "call", "invite"]):
            agents_to_run.append("meeting")

        if any(word in user_input_lower for word in ["email", "send", "follow up", "mail", "notify"]):
            agents_to_run.append("email")

        if any(word in user_input_lower for word in ["task", "assign", "todo", "action", "create"]):
            agents_to_run.append("task")

        # Default: run all agents if nothing matched
        if not agents_to_run:
            agents_to_run = ["meeting", "email", "task"]

        logger.info(f"Intent detected: {agents_to_run} for input: '{user_input}'")
        return agents_to_run

    # ---------------------------
    # Build CrewAI Agents
    # ---------------------------
    def _build_crew_agents(self, agent_names: list) -> list:
        """
        Builds CrewAI Agent objects from selected agent names.
        Each agent has a role, goal, and backstory.
        """
        crew_agents = []

        if "meeting" in agent_names:
            crew_agents.append(
                Agent(
                    role="Meeting Coordinator",
                    goal="Summarize meetings and extract key action items clearly",
                    backstory=(
                        "You are an expert meeting coordinator with years of experience "
                        "in summarizing discussions, identifying decisions, and creating "
                        "structured action plans from conversations."
                    ),
                    llm=self.llm,
                    verbose=True,
                    allow_delegation=False
                )
            )

        if "email" in agent_names:
            crew_agents.append(
                Agent(
                    role="Email Communication Specialist",
                    goal="Draft professional, clear, and concise follow-up emails",
                    backstory=(
                        "You are a professional communication expert who specializes in "
                        "crafting impactful emails that are clear, actionable, and "
                        "appropriately formal for business contexts."
                    ),
                    llm=self.llm,
                    verbose=True,
                    allow_delegation=False
                )
            )

        if "task" in agent_names:
            crew_agents.append(
                Agent(
                    role="Task Management Expert",
                    goal="Create structured, prioritized, and assignable task lists",
                    backstory=(
                        "You are a project management specialist who excels at breaking "
                        "down complex objectives into clear, actionable tasks with "
                        "priorities, deadlines, and ownership assignments."
                    ),
                    llm=self.llm,
                    verbose=True,
                    allow_delegation=False
                )
            )

        return crew_agents

    # ---------------------------
    # Build CrewAI Tasks
    # ---------------------------
    def _build_crew_tasks(self, user_input: str, agent_names: list, crew_agents: list) -> list:
        """
        Builds CrewAI Task objects linked to each agent.
        Each task has a clear description and expected output.
        """
        tasks = []
        agent_index = 0

        if "meeting" in agent_names:
            tasks.append(
                Task(
                    description=(
                        f"Analyze the following user request and provide a detailed "
                        f"meeting summary with key points, decisions made, and action items:\n\n"
                        f"User Request: {user_input}"
                    ),
                    expected_output=(
                        "A structured meeting summary containing:\n"
                        "1. Key discussion points\n"
                        "2. Decisions made\n"
                        "3. Action items with owners\n"
                        "4. Next steps"
                    ),
                    agent=crew_agents[agent_index]
                )
            )
            agent_index += 1

        if "email" in agent_names:
            tasks.append(
                Task(
                    description=(
                        f"Based on the following request, draft a professional follow-up email "
                        f"with subject line, greeting, body, and signature:\n\n"
                        f"User Request: {user_input}"
                    ),
                    expected_output=(
                        "A complete professional email containing:\n"
                        "1. Subject line\n"
                        "2. Greeting\n"
                        "3. Email body with key points\n"
                        "4. Call to action\n"
                        "5. Professional signature"
                    ),
                    agent=crew_agents[agent_index]
                )
            )
            agent_index += 1

        if "task" in agent_names:
            tasks.append(
                Task(
                    description=(
                        f"Create a structured, prioritized task list based on the following request. "
                        f"Include priority levels (High/Medium/Low), estimated time, and suggested owner:\n\n"
                        f"User Request: {user_input}"
                    ),
                    expected_output=(
                        "A structured task list containing:\n"
                        "1. Task name and description\n"
                        "2. Priority level (High/Medium/Low)\n"
                        "3. Estimated completion time\n"
                        "4. Suggested owner/team\n"
                        "5. Dependencies (if any)"
                    ),
                    agent=crew_agents[agent_index]
                )
            )

        return tasks

    # ---------------------------
    # MAIN RUN METHOD
    # ---------------------------
    def run(self, user_input: str) -> str:
        """
        Main entry point called by Streamlit UI.

        Flow:
        1. Detect intent from user input
        2. Build relevant agents
        3. Build tasks for each agent
        4. Create CrewAI Crew
        5. Execute workflow
        6. Save result to memory
        7. Return final output string
        """
        try:
            logger.info(f"Workflow started for input: '{user_input}'")

            # Step 1: Detect which agents to use
            agent_names = self._detect_intent(user_input)

            # Step 2: Build CrewAI Agent objects
            crew_agents = self._build_crew_agents(agent_names)

            # Step 3: Build CrewAI Task objects
            crew_tasks = self._build_crew_tasks(user_input, agent_names, crew_agents)

            # Step 4: Create the Crew
            crew = Crew(
                agents=crew_agents,
                tasks=crew_tasks,
                process=Process.sequential,  # Agents run one after another
                verbose=True
            )

            # Step 5: Execute the workflow
            result = crew.kickoff()

            # Step 6: Save to memory
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.memory.save(
                key=f"workflow_{timestamp}",
                value={
                    "input": user_input,
                    "agents_used": agent_names,
                    "output": str(result),
                    "timestamp": timestamp
                }
            )

            logger.info(f"Workflow completed successfully. Agents used: {agent_names}")

            # Step 7: Return result
            return str(result)

        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    # ---------------------------
    # Get Workflow History
    # ---------------------------
    def get_history(self) -> list:
        """
        Returns all past workflow runs from memory.
        Used by Streamlit UI to show history.
        """
        return self.memory.get_all()