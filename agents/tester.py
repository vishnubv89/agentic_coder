from core.state import AgenticCoderState
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS
from core.llm import get_llm

def tester_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Tester Agent: Testing code artifacts...")
    
    code_artifacts = state.get("code_artifacts", {})
    
    # Build a direct summary of the code for the tester — no guessing, no file listing
    if not code_artifacts:
        return {
            "test_results": "No code artifacts found to test.",
            "status": "failed",
            "errors": ["Coder agent produced no files."]
        }
    
    code_summary = "\n\n".join([
        f"### File: {fname}\n```python\n{code}\n```"
        for fname, code in code_artifacts.items()
    ])
    
    llm = get_llm(temperature=0)
    is_ollama = config.LLM_PROVIDER == "ollama"
    
    tool_prompt = ""
    if is_ollama:
        tool_prompt = """
        To use the execution tool, wrap your request in XML tags:
        <tool name="execute_python_code">{"code": "print('test')"}</tool>
        """
    
    system_prompt = f"""You are a QA Tester Agent.
    Your ONLY job is to call the `execute_python_code` tool with the code provided to you.
    {tool_prompt}
    After execution, evaluate stdout/stderr. 
    If the code ran without errors, reply with 'PASSED: <summary of output>'.
    If there were errors, reply with 'FAILED: <reason>'."""
    
    # Initialize variables for response handling
    response_content = ""
    tool_calls = []
    
    if is_ollama:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please execute and test this code now using <tool> tags:\n\n{code_summary}")
        ])
        response_content = response.content
        import re
        matches = re.findall(r'<tool name="(.*?)">(.*?)</tool>', response_content, re.DOTALL)
        for name, args_str in matches:
            try:
                tool_calls.append({"name": name, "args": json.loads(args_str)})
            except:
                print(f"Failed to parse tool args: {args_str}")
    else:
        llm_with_tools = llm.bind_tools(AGENT_TOOLS)
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please execute and test this code now:\n\n{code_summary}")
        ])
        response_content = response.content
        if response.tool_calls:
            tool_calls = response.tool_calls
    
    execution_logs = []
    if tool_calls:
        print(f"Tester Agent is using {len(tool_calls)} tools...")
        from tools.execution_tools import execute_python_code
        from tools.file_tools import read_file, write_file, list_directory
        tool_map = {
            "execute_python_code": execute_python_code,
            "read_file": read_file,
            "write_file": write_file,
            "list_directory": list_directory
        }
        for tc in tool_calls:
            print(f"  -> Tool call requested: {tc['name']}")
            tool_fn = tool_map.get(tc['name'])
            if tool_fn:
                try:
                    tool_result = tool_fn.invoke(tc["args"])
                    execution_logs.append(f"> Running code sandbox...\n{tool_result}")
                    print(f"  -> Execution output: {tool_result}")
                except Exception as e:
                    execution_logs.append(f"> Execution error:\n{e}")
                    print(f"  -> Execution tool error: {e}")
    
    content = response_content
    if isinstance(content, list):
        content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
    elif not isinstance(content, str):
        content = str(content)

    # Determine pass/fail from execution output (reliable) or LLM conclusion (fallback)
    combined_logs = "\n".join(execution_logs)
    if execution_logs:
        # Trust exit code from the sandbox output
        if "EXIT CODE: 0" in combined_logs and "Error" not in combined_logs and "Traceback" not in combined_logs:
            status = "completed"
            print("Tester approved the code!")
            errors = []
        else:
            status = "failed"
            print(f"Tester found issues in execution output.")
            errors = [combined_logs]
    else:
        # Fallback: trust LLM text conclusion if no tool was called
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
        final_results = "\n\n".join(execution_logs) + ("\n\nAgent Conclusion:\n" + content if content.strip() else "")

    return {
        "test_results": final_results,
        "status": status,
        "messages": [response],
        "errors": errors
    }
