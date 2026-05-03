import os
import json
from agents.coder import coder_node
from agents.planner import planner_node
from core.state import AgenticCoderState
from core.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

WHATSAPP_DIR = "/Users/vishnubv/Vishnu/AnitGravity/Whatsapp"
REPORT_FILE = os.path.join(WHATSAPP_DIR, "self_heal_report.json")

async def run_autonomous_healing():
    """
    Scans for failed runs in the news suite and attempts to heal the code.
    """
    if not os.path.exists(REPORT_FILE):
        print("🏥 Healer: No self-heal reports found. System is healthy.")
        return

    with open(REPORT_FILE, "r") as f:
        reports = json.load(f)

    pending = [r for r in reports if r.get("status") == "pending_healing"]
    if not pending:
        print("🏥 Healer: No pending reports to heal.")
        return

    report = pending[-1] # Tackle the latest one
    print(f"🏥 Healer: Analyzing failure from {report['timestamp']}...")
    print(f"🏥 Error: {report['error']}")

    # ── Phase 1: Planning the Fix ──────────────────────────────────────
    task_description = f"""
    The WhatsApp News Broadcast suite failed with this error:
    Error: {report['error']}
    Traceback: {report['traceback']}
    Context: {report['context']}
    
    TASK: Analyze 'agents/__init__.py' and 'tasks.py' in {WHATSAPP_DIR}.
    Identify why the LLM might be returning 'None or empty' or failing.
    PROPOSE and APPLY a fix (e.g., prompt adjustment, safety setting tweak, or logic change).
    """

    state: AgenticCoderState = {
        "task_description": task_description,
        "plan": [],
        "code_artifacts": {},
        "errors": [],
        "status": "planning",
        "messages": [],
        "thought": "Starting autonomous healing process."
    }

    # Use existing planner to decide what to do
    print("🏥 Healer: Planning the repair...")
    planner_res = await planner_node(state)
    state.update(planner_res)

    # Use existing coder to apply the fix
    print("🏥 Healer: Applying the autonomous patch...")
    coder_res = await coder_node(state)
    state.update(coder_res)

    # Mark as healed
    report["status"] = "healed"
    report["healing_timestamp"] = report["timestamp"]
    with open(REPORT_FILE, "w") as f:
        json.dump(reports, f, indent=4)

    print("✅ Healer: Autonomous patch applied successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_autonomous_healing())
