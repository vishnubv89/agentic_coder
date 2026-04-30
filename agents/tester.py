from core.state import AgenticCoderState
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS
from core.llm import get_llm
import json
import re

async def tester_node(state: AgenticCoderState) -> AgenticCoderState:
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
        Available tools:
        1. <tool name="execute_python_code">{"code": "from filename import function; print(function())"}</tool>
        2. <tool name="compile_and_run_cpp">{"code": "#include <iostream>\\n..."}</tool>
        
        CRITICAL: Inside the JSON, you MUST escape newlines as \\n and double quotes as \\".
        Do NOT use triple quotes (\"\"\") inside the JSON.
        """

    def clean_json(s):
        # Remove potential markdown code blocks
        s = s.strip()
        if s.startswith("```json"): s = s[7:-3]
        elif s.startswith("```"): s = s[3:-3]
        s = s.strip()
        
        # Handle the common mistake of triple quotes inside JSON
        s = s.replace('"""', '"') 
        
        # Try to fix unescaped newlines inside JSON strings
        import re
        # Find the content of "code": "..." values and fix newlines
        def fix_newlines(match):
            val = match.group(2)
            fixed = val.replace('\n', '\\n').replace('\r', '')
            return f'"{match.group(1)}": "{fixed}"'
        
        s = re.sub(r'"(code)":\s*"(.*?)"', fix_newlines, s, flags=re.DOTALL)
        return s

    system_prompt = f"""You are a QA Tester Agent.
    Your task is to verify the code artifacts below.
    Code to test:
    {code_summary}

    To test, use the appropriate tool:
    - For Python: use `execute_python_code`. IMPORT the functions from their modules.
    - For C++: use `compile_and_run_cpp`. Provide the full test code including a `main()` that tests the relevant parts.
    
    {tool_prompt}
    Evaluate stdout/stderr. If exit code is 0 and output is correct, reply 'PASSED'. Otherwise 'FAILED' with reason."""
    
    # Initialize variables for response handling
    response_content = ""
    tool_calls = []
    execution_logs = []
    
    if is_ollama:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please execute and test this code now using the appropriate <tool name=\"...\">{{\"code\": \"...\"}}</tool> tags.")
        ])
        response_content = response.content
        # Robust manual parsing
        import re
        # Match <tool name="...">content</tool>
        matches = re.finditer(r'<tool\s+name=["\'](.*?)["\']\s*>(.*?)</tool>', response_content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            name = match.group(1).strip()
            args_str = match.group(2).strip()
            try:
                cleaned_args = clean_json(args_str)
                tool_calls.append({"name": name, "args": json.loads(cleaned_args)})
            except Exception as e:
                error_msg = f"Failed to parse tool args for {name}: {e}. Args: {args_str}"
                print(error_msg)
                execution_logs.append(error_msg)
    else:
        llm_with_tools = llm.bind_tools(AGENT_TOOLS)
        try:
            response = await llm_with_tools.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Please execute and test this code now:\n\n{code_summary}")
            ])
            response_content = response.content
            if response.tool_calls:
                tool_calls = response.tool_calls
        except Exception as e:
            execution_logs.append(f"LLM Tool Call Error: {str(e)}")
            response = None
    
    if tool_calls:
        print(f"Tester Agent is using {len(tool_calls)} tools...")
        from tools.execution_tools import execute_python_code, compile_and_run_cpp
        from tools.file_tools import read_file, write_file, list_directory
        tool_map = {
            "execute_python_code": execute_python_code,
            "compile_and_run_cpp": compile_and_run_cpp,
            "read_file": read_file,
            "write_file": write_file,
            "list_directory": list_directory
        }
        
        for tc in tool_calls:
            t_name = tc["name"]
            t_args = tc["args"]
            if t_name in tool_map:
                try:
                    res = tool_map[t_name].invoke(t_args)
                    execution_logs.append(f"TOOL [{t_name}] OUTPUT:\n{res}")
                except Exception as e:
                    execution_logs.append(f"TOOL [{t_name}] CRASHED: {str(e)}")
            else:
                execution_logs.append(f"TOOL ERROR: Unknown tool '{t_name}'")
    
    content = response_content
    if isinstance(content, list):
        content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
    elif not isinstance(content, str):
        content = str(content)

    # Determine pass/fail from execution output (reliable) or LLM conclusion (fallback)
    combined_logs = "\n".join(execution_logs)
    if execution_logs:
        # Trust exit code from the sandbox output
        # If any tool output contains "EXIT CODE: 1" or "Compilation Failed" or "Error" or "Crashed", it's a failure
        failed_indicators = ["EXIT CODE: 1", "Compilation Failed", "Error", "Traceback", "CRASHED", "Failed to parse", "Unknown tool"]
        if any(ind in combined_logs for ind in failed_indicators):
            status = "failed"
            print(f"Tester found issues in execution output.")
            errors = [combined_logs]
        elif "EXIT CODE: 0" in combined_logs or "PASSED" in content.upper():
            status = "completed"
            print("Tester approved the code!")
            errors = []
        else:
            # Ambiguous output but tool was called
            status = "failed"
            errors = ["Ambiguous execution output. Please verify manually or refine tests."]
    else:
        # Fallback: trust LLM text conclusion if no tool was called
        content_upper = content.upper()
        if "FAILED" in content_upper or "ISSUE" in content_upper:
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

    retries = state.get("retry_count", 0)
    if status == "failed":
        retries += 1

    return {
        "test_results": final_results,
        "status": status,
        "messages": [response],
        "errors": errors,
        "retry_count": 1 if status == "failed" else 0,
        "thought": "Test suite passed. Implementation verified." if status == "completed" else "Test failed. Re-analyzing code..."
    }
