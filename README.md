# 🤖 Agentic AI Workflow Automation

> An intelligent multi-agent system that automates meeting summaries, email drafting, and task management — powered by CrewAI, Groq, Supabase, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![CrewAI](https://img.shields.io/badge/CrewAI-0.28.8-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-green?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-Database-darkgreen?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🚀 Live Demo

🔗 **[View Live Project →](https://agentic-ai-workflow-6ocqpmz8qqs73vysmhapkh.streamlit.app)**

---

## 📌 What This Project Does

You type a task. AI agents figure out what to do and do it.

**Example inputs:**
- *"Summarize today's product meeting and create action items"*
- *"Send a follow-up email to the design team about the deadline"*
- *"Create a task list for launching our new feature next week"*

The system automatically routes your request to the right agents, executes the workflow, saves everything to memory, and shows you the result.

---

## 🧠 How It Works

```
User Input (Streamlit UI)
        ↓
Workflow Manager (Brain)
        ↓ detects intent
┌───────┬───────┬────────┐
│Meeting│ Email │  Task  │
│ Agent │ Agent │ Agent  │
└───┬───┴───┬───┴────┬───┘
    ↓       ↓        ↓
Calendar  Gmail    Slack
  Tool    Tool     Tool
    ↓       ↓        ↓
        Memory
       (Supabase)
        ↓
   Output → UI
```

---

## ✨ Features

- **🤖 Multi-Agent System** — Three specialized AI agents work together
- **🧠 Intent Detection** — Automatically picks the right agent for your task
- **📋 Meeting Summaries** — Extracts action items, decisions, and next steps
- **📧 Email Drafting** — Creates professional emails with correct tone detection
- **✅ Task Management** — Generates prioritized task lists with owners and deadlines
- **💾 Persistent Memory** — All results saved to Supabase across sessions
- **🔌 Tool Integrations** — Gmail, Google Calendar, Slack
- **🛡️ Dry Run Mode** — Works without API credentials for testing
- **📊 Live Dashboard** — Real-time agent status in Streamlit sidebar
- **📝 Agent Logging** — Every agent action logged automatically

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Agent Framework** | CrewAI | Multi-agent orchestration |
| **LLM** | Groq (LLaMA 3) | Free, fast AI reasoning |
| **Database** | Supabase | Persistent agent memory |
| **UI** | Streamlit | Live web dashboard |
| **Email** | Gmail API | Send follow-up emails |
| **Calendar** | Google Calendar API | Create meeting events |
| **Notifications** | Slack Webhooks | Team task alerts |
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
│   ├── email_tool.py          # Gmail integration
│   ├── calendar_tool.py       # Google Calendar integration
│   └── slack_tool.py          # Slack notifications
│
├── memory/
│   └── memory_store.py        # Supabase memory system
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
├── config/
│   └── settings.py            # App configuration
│
├── main.py                    # Entry point
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/agentic-ai-workflow.git
cd agentic-ai-workflow
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example file
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

### 6. Get Your Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → Create API Key
3. Add to `.env` as `GROQ_API_KEY`

### 7. Run the App

```bash
streamlit run ui/app.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set your environment variables in Streamlit secrets
5. Click **Deploy** → Get your live link 🔗

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Free LLM API key |
| `SUPABASE_URL` | ✅ Yes | Supabase project URL |
| `SUPABASE_KEY` | ✅ Yes | Supabase anon key |
| `GMAIL_SENDER_EMAIL` | Optional | Gmail address for sending |
| `GMAIL_APP_PASSWORD` | Optional | Gmail app password |
| `GOOGLE_CALENDAR_ID` | Optional | Calendar ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Optional | Path to JSON key file |
| `SLACK_WEBHOOK_URL` | Optional | Slack incoming webhook |
| `SLACK_DEFAULT_CHANNEL` | Optional | Default Slack channel |

> ⚠️ Tools without credentials run in **dry run mode** — they simulate actions without executing them. The app never crashes.

---

## 🧪 Example Usage

### Input
```
Schedule a Q2 planning meeting for next Monday at 2pm,
send invites to the team, and create action items for
the product launch.
```

### Output
```
## 📋 Meeting Summary
Meeting Topic: Q2 Planning — Product Launch

Key Discussion Points:
- Product roadmap review
- Launch timeline confirmation
- Team responsibility assignments

Action Items:
| # | Task              | Owner      | Deadline   |
|---|-------------------|------------|------------|
| 1 | Finalize roadmap  | PM Team    | Friday     |
| 2 | Prepare demo      | Dev Team   | Next Mon   |

## 📧 Drafted Email
Subject: Q2 Planning Meeting — Action Items

Dear Team,
Please find the action items from today's session...

## ✅ Task Breakdown
🔴 High: Finalize product roadmap — PM — 3 days
🟡 Medium: Prepare staging demo — Dev — 5 days
🟢 Low: Update documentation — Writer — 1 week
```

---

## 🗺️ Roadmap

- [x] Multi-agent workflow system
- [x] Groq LLM integration
- [x] Supabase persistent memory
- [x] Gmail, Calendar, Slack tools
- [x] Streamlit live dashboard
- [ ] Streaming output (typing effect)
- [ ] Voice input support
- [ ] WhatsApp notifications
- [ ] Multi-language support
- [ ] Agent performance analytics

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Built With

- [CrewAI](https://github.com/joaomdmoura/crewAI) — Multi-agent framework
- [Groq](https://groq.com) — Ultra-fast free LLM API
- [Supabase](https://supabase.com) — Open source Firebase alternative
- [Streamlit](https://streamlit.io) — Python web app framework

---

> ⭐ If this project helped you, give it a star on GitHub!