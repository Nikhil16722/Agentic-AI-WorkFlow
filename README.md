# ⚡ NeuralFlow — Agentic AI Workflow Automation

> Multi-agent AI system that automates meetings, emails, and task management — powered by Groq LLaMA 3.1, Supabase, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-orange?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-Database-darkgreen?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🔗 Live Demo

**[→ Open NeuralFlow Live](https://agentic-ai-workflow-6ocqpmz8qqs73vysmhapkh.streamlit.app)**

---

## 🚀 How to Use

Using NeuralFlow is simple — just describe your task in plain English and the AI agents handle everything automatically.

### Step 1 — Open the App
Go to the live link above or run locally with `streamlit run ui/app.py`

### Step 2 — Type Your Task
In the text box, describe what you need. You can mention meetings, emails, tasks — or all three at once.

### Step 3 — Click "Run Agents"
The system detects your intent and routes to the right agent automatically. Results appear in seconds.

---

## 💡 Example Queries & Outputs

### 🗓 Meeting Summary

**You type:**
```
Summarize a product team meeting where we discussed the Q2 launch 
timeline, assigned development tasks to 3 engineers, and decided 
to delay the release by one week due to QA issues.
```

**You get:**
```
## Meeting Summary

Meeting Topic: Q2 Product Launch Planning

Key Discussion Points:
- Q2 launch timeline review
- Task assignments for engineering team
- QA blockers and mitigation strategy

Decisions Made:
- Release delayed by 1 week to allow QA completion

Action Items:
| Task              | Owner          | Deadline   |
|-------------------|----------------|------------|
| Fix QA blockers   | Engineering    | Friday     |
| Update roadmap    | Product Lead   | Monday     |
| Notify clients    | Sales Team     | Tuesday    |

Next Steps:
1. Schedule QA review session
2. Send updated timeline to stakeholders
```

---

### 📧 Email Draft

**You type:**
```
Send a professional email to the client informing them that 
their project is delayed by 2 weeks due to unexpected 
technical issues.
```

**You get:**
```
## Drafted Email

Subject: Project Update — Revised Delivery Timeline

Dear [Client Name],

I hope this message finds you well. I am writing to inform 
you that due to unforeseen technical challenges, we are 
extending the project timeline by two weeks.

Our team is working diligently to resolve these issues and 
ensure the final deliverable meets our agreed standards.

New delivery date: [Original Date + 2 weeks]

Please feel free to reach out if you have any questions.

Best regards,
[Your Name]
Project Manager

Email Notes: Tone: Formal | Priority: High
```

---

### ✅ Task Breakdown

**You type:**
```
Create a task list for launching a mobile app next month 
including design, development, testing, marketing and deployment.
```

**You get:**
```
## Task Breakdown

Goal: Mobile App Launch
Total Estimated Time: 4 weeks

### High Priority
| Task                  | Owner      | Est. Time | Deadline  |
|-----------------------|------------|-----------|-----------|
| Finalize UI designs   | Design     | 3 days    | Week 1    |
| Complete core features| Dev Team   | 1 week    | Week 2    |
| QA & bug fixing       | QA Team    | 4 days    | Week 3    |

### Medium Priority  
| Task                  | Owner      | Est. Time | Deadline  |
|-----------------------|------------|-----------|-----------|
| App store assets      | Design     | 2 days    | Week 2    |
| Marketing campaign    | Marketing  | 1 week    | Week 3    |

### Low Priority
| Task                  | Owner      | Est. Time | Deadline  |
|-----------------------|------------|-----------|-----------|
| Documentation         | Dev Team   | 2 days    | Week 4    |

Milestones:
1. Design complete — End of Week 1
2. Development complete — End of Week 2
3. Launch ready — End of Week 4
```

---

### 🔥 Combined (All Agents at Once)

**You type:**
```
We had a team meeting about our new SaaS product launch next month. 
Send follow-up emails to all stakeholders, and create a task list 
for the development and marketing teams.
```

**You get:** Meeting summary + Full email draft + Complete task list — all in one response.

---

## 🧠 How It Works

```
Your Input (plain English)
        ↓
Intent Detection
        ↓
┌──────────────────────────┐
│  Meeting  Email   Task   │
│  Agent    Agent   Agent  │
└──────────────────────────┘
        ↓
  Groq LLaMA 3.1
        ↓
  Saved to Supabase
        ↓
  Output on Screen
```

---

## ✨ Features

- **3 Specialized AI Agents** — Meeting, Email, and Task agents working together
- **Smart Intent Detection** — Automatically picks the right agent for your request
- **Groq LLaMA 3.1** — Fast, free LLM powering all agents
- **Supabase Memory** — Every result saved and accessible in Run History
- **Premium Dark UI** — Professional futuristic interface
- **Dry Run Mode** — Works without optional API keys (Gmail, Calendar, Slack)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | Groq LLaMA 3.1 | Free, fast AI reasoning |
| **Framework** | LangChain | Agent orchestration |
| **Database** | Supabase | Persistent memory |
| **UI** | Streamlit | Web dashboard |
| **Email** | Gmail API | Send emails (optional) |
| **Calendar** | Google Calendar API | Create events (optional) |
| **Notifications** | Slack Webhooks | Team alerts (optional) |
| **Language** | Python 3.10+ | Core language |

---

## 📁 Project Structure

```
agentic-ai-workflow/
│
├── agents/
│   ├── base_agent.py          # Parent class for all agents
│   ├── meeting_agent.py       # Summarizes meetings
│   ├── email_agent.py         # Drafts emails
│   └── task_agent.py          # Creates task lists
│
├── tools/
│   ├── base_tool.py           # Parent class for all tools
│   ├── email_tool.py          # Gmail integration
│   ├── calendar_tool.py       # Google Calendar integration
│   └── slack_tool.py          # Slack notifications
│
├── memory/
│   ├── memory_store.py        # Supabase memory system
│   └── supabase_client.py     # Supabase connection
│
├── workflows/
│   └── workflow_manager.py    # Central brain / orchestrator
│
├── ui/
│   └── app.py                 # Streamlit dashboard
│
├── logs/
│   └── agent_logs.txt         # Auto-generated action logs
│
├── main.py                    # Entry point + health check
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## ⚙️ Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/nikhil16722/agentic-ai-workflow.git
cd agentic-ai-workflow
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
cp .env.example .env
# Open .env and fill in your credentials
```

### 5. Set Up Supabase Table
Run this SQL in your Supabase SQL editor:
```sql
CREATE TABLE agent_memory (
  id         SERIAL PRIMARY KEY,
  key        TEXT UNIQUE NOT NULL,
  value      TEXT,
  agent_name TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Get Free Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → Create API Key
3. Add to `.env` as `GROQ_API_KEY`

### 7. Run the App
```bash
python -m streamlit run ui/app.py
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Free LLM API from Groq |
| `SUPABASE_URL` | ✅ Yes | Supabase project URL |
| `SUPABASE_KEY` | ✅ Yes | Supabase anon key |
| `GMAIL_SENDER_EMAIL` | Optional | Gmail for sending emails |
| `GMAIL_APP_PASSWORD` | Optional | Gmail 16-char app password |
| `GOOGLE_CALENDAR_ID` | Optional | Calendar ID |
| `SLACK_WEBHOOK_URL` | Optional | Slack incoming webhook |

> Tools without credentials run in **dry run mode** — they simulate actions without executing. The app never crashes.

---

## 🗺️ Roadmap

- [x] Multi-agent workflow system
- [x] Groq LLaMA 3.1 integration
- [x] Supabase persistent memory
- [x] Gmail, Calendar, Slack tools
- [x] Premium Streamlit dashboard
- [x] Live deployment on Streamlit Cloud
- [ ] Streaming output (typing effect)
- [ ] Voice input support
- [ ] WhatsApp notifications
- [ ] Agent performance analytics dashboard

---

## 👨‍💻 Built With

- [Groq](https://groq.com) — Ultra-fast free LLM API
- [LangChain](https://langchain.com) — LLM orchestration framework
- [Supabase](https://supabase.com) — Open source Firebase alternative
- [Streamlit](https://streamlit.io) — Python web app framework

---

> ⭐ If this project helped you, give it a star on GitHub!