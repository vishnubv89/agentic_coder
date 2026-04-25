from core.state import AgenticCoderState
from langchain_core.messages import AIMessage

def planner_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Planner Agent: Analyzing task and creating plan...")
    task = state.get("task_description", "")
    
    # Placeholder logic - in reality, we'd call an LLM here
    plan = [
        "1. Analyze requirements.",
        "2. Scaffold application structure.",
        "3. Implement code and tests."
    ]
    
    return {
        "plan": plan,
        "status": "coding",
        "messages": [AIMessage(content=f"Plan created with {len(plan)} steps.")]
    }
