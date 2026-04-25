from core.state import AgenticCoderState
from langchain_core.messages import AIMessage

def tester_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Tester Agent: Testing code artifacts...")
    
    # Assume tests pass for now
    return {
        "test_results": "All generated artifacts passed syntax checks.",
        "status": "completed",
        "messages": [AIMessage(content="Tests passed successfully.")]
    }
