from core.state import AgenticCoderState
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS
from core.llm import get_llm

def coder_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Coder Agent: Writing code based on plan...")
    task = state.get("task_description", "")
    plan = state.get("plan", [])
    errors = state.get("errors", [])
    
    llm = get_llm(temperature=0.2)
    is_ollama = config.LLM_PROVIDER == "ollama"
    
    tool_prompt = ""
    if is_ollama:
        tool_prompt = """
        To use a tool, wrap your request in XML tags like this:
        <tool name="write_file">{"file_path": "path/to/file.py", "content": "print('hello')"}</tool>
        <tool name="read_file">{"file_path": "path/to/existing_file.py"}</tool>
        
        Available tools: write_file, read_file
        IMPORTANT: Before creating or modifying files, ALWAYS use 'read_file' to understand the existing code context if it's relevant.
        """
    
    system_prompt = f"""You are an Expert Coder Agent.
    Your goal is to implement the given task based on the provided plan.
    Task: {task}
    Plan: {plan}
    {tool_prompt}
    
    IMPORTANT: Only use Python standard library modules unless specifically told otherwise.
    If you encountered previous errors, they are listed here to fix: {errors}
    
    Call the necessary tools to write out the code. Once finished, explain what you wrote.
    """
    
    # Initialize variables for response handling
    response_content = ""
    tool_calls = []
    
    if is_ollama:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Please implement the code now. Use <tool name=\"tool_name\">{\"arg\": \"val\"}</tool> tags.")
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
                # Clean up potential markdown code blocks inside XML
                if args_str.startswith("```"):
                    args_str = re.sub(r'```[a-z]*\n(.*?)\n```', r'\1', args_str, flags=re.DOTALL)
                tool_calls.append({"name": name, "args": json.loads(args_str)})
            except Exception as e:
                print(f"Failed to parse tool args for {name}: {e}. Args string: {args_str}")
    else:
        llm_with_tools = llm.bind_tools(AGENT_TOOLS)
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Please implement the code now.")
        ])
        response_content = response.content
        if response.tool_calls:
            tool_calls = response.tool_calls

    code_artifacts = state.get("code_artifacts", {})
    if tool_calls:
        print(f"Coder Agent is using {len(tool_calls)} tools...")
        from tools.file_tools import write_file, read_file
        tool_map = {"write_file": write_file, "read_file": read_file}
        for tc in tool_calls:
            tool_fn = tool_map.get(tc["name"])
            if tool_fn:
                print(f"  -> Executing {tc['name']} with args {tc['args']}")
                try:
                    result = tool_fn.invoke(tc["args"])
                    if tc["name"] == "write_file":
                        file_path = tc["args"].get("file_path", "unknown.py")
                        content = tc["args"].get("content", "")
                        code_artifacts[file_path] = content
                    elif tc["name"] == "read_file":
                        # If we read a file, we should probably append it to context or just print it
                        print(f"  -> File content read: {len(result)} chars")
                except Exception as e:
                    print(f"  -> Tool error: {e}")
    
    return {
        "status": "testing",
        "messages": [response],
        "code_artifacts": code_artifacts,
        "retry_count": state.get("retry_count", 0)
    }
