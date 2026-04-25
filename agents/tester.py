from core.state import AgenticCoderState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS

def tester_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Tester Agent: Testing code artifacts...")
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", google_api_key=config.GEMINI_API_KEY, temperature=0)
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    
    system_prompt = """You are a QA Tester Agent.
    Your job is to test the code written by the Coder Agent.
    Use the `execute_python_code` tool to run the code.
    Evaluate the output. If it fails or has errors, reply with 'FAILED: <reason>'. 
    If it passed, reply with 'PASSED: <reason>'."""
    
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Please test the generated code.")
    ])
    
    if response.tool_calls:
        print(f"Tester Agent is using {len(response.tool_calls)} tools...")
        from tools.execution_tools import execute_python_code
        tool_map = {"execute_python_code": execute_python_code}
        for tc in response.tool_calls:
            tool_fn = tool_map.get(tc["name"])
            if tool_fn:
                try:
                    tool_result = tool_fn.invoke(tc["args"])
                    print(f"  -> Execution output: {tool_result}")
                except Exception as e:
                    print(f"  -> Execution tool error: {e}")
    
    content = response.content.upper()
    if "FAILED" in content:
        status = "failed"
        print(f"Tester found issues: {response.content}")
        errors = [response.content]
    else:
        status = "completed"
        print("Tester approved the code!")
        errors = []
        
    return {
        "test_results": response.content,
        "status": status,
        "messages": [response],
        "errors": errors
    }
