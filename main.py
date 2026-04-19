"""
main.py
--------
Entry point for the Agentic AI Workflow Automation System.

This file:
- Validates environment setup
- Initializes all components
- Runs quick system health check
- Launches Streamlit UI
- OR runs a direct CLI test

Run options:
    streamlit run ui/app.py     → Launch full web UI
    python main.py              → Run CLI test mode
    python main.py --check      → System health check only
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# ---------------------------
# Load Environment Variables
# ---------------------------
load_dotenv()

# ---------------------------
# Logger Setup
# ---------------------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/agent_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Console logger (for CLI output)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)s → %(message)s"))
logging.getLogger("").addHandler(console)


# ============================================================
# SYSTEM HEALTH CHECK
# ============================================================
def run_health_check() -> dict:
    """
    Checks that all required components are ready.

    Verifies:
    - Required Python packages installed
    - .env file exists
    - GROQ_API_KEY is set (minimum requirement)
    - Supabase credentials present
    - Optional tool credentials present

    Returns:
        dict : {
            "status"  : "ready" | "partial" | "failed",
            "checks"  : list of check result dicts,
            "summary" : human-readable summary string
        }
    """
    print("\n" + "=" * 55)
    print("   🤖 Agentic AI Workflow — System Health Check")
    print("=" * 55)

    checks = []

    # --- Check 1: .env file exists ---
    env_exists = os.path.exists(".env")
    checks.append({
        "name": ".env file",
        "status": "✅ Found" if env_exists else "❌ Missing — copy .env.example to .env",
        "required": True,
        "passed": env_exists
    })

    # --- Check 2: Groq API Key ---
    groq_key = os.getenv("GROQ_API_KEY")
    groq_ok = bool(groq_key and groq_key != "your_groq_api_key_here")
    checks.append({
        "name": "GROQ_API_KEY",
        "status": "✅ Set" if groq_ok else "❌ Missing — get free key at console.groq.com",
        "required": True,
        "passed": groq_ok
    })

    # --- Check 3: Supabase URL ---
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_url_ok = bool(supabase_url and "supabase.co" in supabase_url)
    checks.append({
        "name": "SUPABASE_URL",
        "status": "✅ Set" if supabase_url_ok else "⚠️  Missing — using local memory fallback",
        "required": False,
        "passed": supabase_url_ok
    })

    # --- Check 4: Supabase Key ---
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase_key_ok = bool(supabase_key and supabase_key != "your_supabase_anon_key_here")
    checks.append({
        "name": "SUPABASE_KEY",
        "status": "✅ Set" if supabase_key_ok else "⚠️  Missing — using local memory fallback",
        "required": False,
        "passed": supabase_key_ok
    })

    # --- Check 5: Gmail (Optional) ---
    gmail_ok = bool(os.getenv("GMAIL_SENDER_EMAIL") and os.getenv("GMAIL_APP_PASSWORD"))
    checks.append({
        "name": "Gmail Credentials",
        "status": "✅ Set" if gmail_ok else "⚠️  Missing — EmailTool in dry run mode",
        "required": False,
        "passed": gmail_ok
    })

    # --- Check 6: Google Calendar (Optional) ---
    calendar_ok = bool(os.getenv("GOOGLE_CALENDAR_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
    checks.append({
        "name": "Google Calendar",
        "status": "✅ Set" if calendar_ok else "⚠️  Missing — CalendarTool in dry run mode",
        "required": False,
        "passed": calendar_ok
    })

    # --- Check 7: Slack (Optional) ---
    slack_ok = bool(os.getenv("SLACK_WEBHOOK_URL"))
    checks.append({
        "name": "Slack Webhook",
        "status": "✅ Set" if slack_ok else "⚠️  Missing — SlackTool in dry run mode",
        "required": False,
        "passed": slack_ok
    })

    # --- Check 8: Required packages ---
    required_packages = ["crewai", "streamlit", "supabase", "langchain_groq", "dotenv"]
    missing_packages = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)

    packages_ok = len(missing_packages) == 0
    checks.append({
        "name": "Python Packages",
        "status": (
            "✅ All installed"
            if packages_ok
            else f"❌ Missing: {', '.join(missing_packages)} — run: pip install -r requirements.txt"
        ),
        "required": True,
        "passed": packages_ok
    })

    # --- Print Results ---
    print()
    for check in checks:
        tag = "[REQUIRED]" if check["required"] else "[OPTIONAL]"
        print(f"  {check['status']:<50} {tag}")

    print()

    # --- Determine Overall Status ---
    required_checks = [c for c in checks if c["required"]]
    required_passed = all(c["passed"] for c in required_checks)
    optional_passed = all(c["passed"] for c in checks if not c["required"])

    if required_passed and optional_passed:
        status = "ready"
        summary = "✅ All systems ready. Full functionality available."
    elif required_passed:
        status = "partial"
        summary = "⚠️  Core ready. Some tools in dry run mode (optional credentials missing)."
    else:
        status = "failed"
        summary = "❌ Setup incomplete. Add missing required credentials to .env."

    print(f"  Status: {summary}")
    print("=" * 55 + "\n")

    logger.info(f"Health check complete. Status: {status}")

    return {
        "status": status,
        "checks": checks,
        "summary": summary
    }


# ============================================================
# CLI TEST MODE
# ============================================================
def run_cli_test(test_input: str = None):
    """
    Runs the workflow system directly from command line.
    Useful for testing without launching Streamlit.

    Args:
        test_input : Custom input string to test with.
                     Uses default test if None.
    """
    print("\n" + "=" * 55)
    print("   🤖 Running CLI Test Mode")
    print("=" * 55)

    # Default test input
    if not test_input:
        test_input = (
            "Schedule a product team meeting for next Monday, "
            "send follow-up emails to all members, and create "
            "a task list for the Q2 product launch preparation."
        )

    print(f"\n📝 Test Input:\n{test_input}\n")
    print("-" * 55)

    try:
        # Import WorkflowManager
        from workflows.workflow_manager import WorkflowManager

        print("⚙️  Initializing WorkflowManager...")
        manager = WorkflowManager()
        print("✅ WorkflowManager ready.\n")

        # Run the workflow
        print("🚀 Running agents...\n")
        start_time = datetime.now()

        result = manager.run(test_input)

        end_time = datetime.now()
        duration = (end_time - start_time).seconds

        # Print result
        print("\n" + "=" * 55)
        print("   📤 Agent Output")
        print("=" * 55)
        print(result)
        print("=" * 55)
        print(f"\n⏱️  Completed in {duration} seconds.")

        # Show memory count
        history = manager.get_history()
        print(f"💾 Total records in memory: {len(history)}")

        logger.info(f"CLI test completed in {duration}s.")

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("   Make sure all files are in the correct folders.")
        logger.error(f"CLI test import error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Workflow Error: {e}")
        logger.error(f"CLI test failed: {e}")
        sys.exit(1)


# ============================================================
# SHOW PROJECT INFO
# ============================================================
def show_project_info():
    """
    Prints project info banner when main.py starts.
    """
    print("""
╔═══════════════════════════════════════════════════════╗
║       🤖 Agentic AI Workflow Automation System        ║
║                                                       ║
║   Stack  : CrewAI + Groq + Supabase + Streamlit       ║
║   Agents : Meeting · Email · Task                     ║
║   Tools  : Gmail · Google Calendar · Slack            ║
╚═══════════════════════════════════════════════════════╝
    """)


# ============================================================
# ARGUMENT PARSER
# ============================================================
def parse_args():
    """
    Parses command line arguments.

    Modes:
        python main.py              → CLI test with default input
        python main.py --check      → Health check only
        python main.py --input "X"  → CLI test with custom input
        streamlit run ui/app.py     → Full Streamlit web UI
    """
    parser = argparse.ArgumentParser(
        description="Agentic AI Workflow Automation System",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python main.py                         Run CLI test (default input)
  python main.py --check                 Health check only
  python main.py --input "Send meeting summary to team"
  streamlit run ui/app.py                Launch web dashboard
        """
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Run system health check only (no agents)"
    )

    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Custom input text to test the workflow"
    )

    return parser.parse_args()


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    """
    Main entry point.

    Flow:
    1. Show project banner
    2. Parse arguments
    3. Run health check always
    4. If --check only → stop here
    5. If health check fails → stop with error
    6. Run CLI test with given or default input
    """

    # Step 1: Show banner
    show_project_info()

    # Step 2: Parse arguments
    args = parse_args()

    # Step 3: Always run health check first
    health = run_health_check()

    # Step 4: If only --check flag, stop here
    if args.check:
        print("Health check complete. Exiting.")
        sys.exit(0 if health["status"] != "failed" else 1)

    # Step 5: Stop if required setup is missing
    if health["status"] == "failed":
        print("❌ Cannot run — fix required credentials first.")
        print("   Edit your .env file and try again.\n")
        sys.exit(1)

    # Step 6: Run CLI test
    run_cli_test(test_input=args.input)

    # Final tip
    print("\n💡 TIP: To launch the full web UI, run:")
    print("   streamlit run ui/app.py\n")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    main()