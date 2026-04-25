from core.state import AgenticCoderState
from langchain_core.messages import AIMessage

def coder_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Coder Agent: Writing code based on plan...")
    
    artifacts = state.get("code_artifacts", {})
    if not artifacts:
        artifacts["app.py"] = "def hello():\n    return 'Hello from AgenticCoder!'"
    
    return {
        "code_artifacts": artifacts,
        "status": "testing",
        "messages": [AIMessage(content="Generated initial code artifacts.")]
    }
