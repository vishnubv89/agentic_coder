from core.state import AgenticCoderState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS

def tester_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Tester Agent: Testing code artifacts...")
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", google_api_key=config.GEMINI_API_KEY, temperature=0)
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
    
    execution_logs = []
    if response.tool_calls:
        print(f"Tester Agent is using {len(response.tool_calls)} tools...")
        from tools.execution_tools import execute_python_code
        tool_map = {"execute_python_code": execute_python_code}
        for tc in response.tool_calls:
            tool_fn = tool_map.get(tc["name"])
            if tool_fn:
                try:
                    tool_result = tool_fn.invoke(tc["args"])
                    execution_logs.append(f"> Running code sandbox...\n{tool_result}")
                    print(f"  -> Execution output: {tool_result}")
                except Exception as e:
                    execution_logs.append(f"> Execution error:\n{e}")
                    print(f"  -> Execution tool error: {e}")
    
    content = response.content
    if isinstance(content, list):
        content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
    elif not isinstance(content, str):
        content = str(content)
        
    content_upper = content.upper()
    if "FAILED" in content_upper:
        status = "failed"
        print(f"Tester found issues: {content}")
        errors = [content]
    else:
        status = "completed"
        print("Tester approved the code!")
        errors = []
        
    final_results = content
    if execution_logs:
        final_results = "\n\n".join(execution_logs) + "\n\nAgent Conclusion:\n" + content
        
    return {
        "test_results": final_results,
        "status": status,
        "messages": [response],
        "errors": errors
    }
