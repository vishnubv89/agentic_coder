from core.state import AgenticCoderState
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS
from core.llm import get_llm
import json
import re

async def coder_node(state: AgenticCoderState) -> AgenticCoderState:
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
        
        CRITICAL: Inside the JSON, you MUST escape newlines as \\n and double quotes as \\".
        Do NOT use triple quotes (\"\"\") inside the JSON.
        Available tools: write_file, read_file
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
        # This is tricky, but we can look for newlines that are NOT preceded by a backslash
        # and are inside what looks like a value string
        import re
        # Find the content of "content": "..." values and fix newlines
        def fix_newlines(match):
            val = match.group(2)
            fixed = val.replace('\n', '\\n').replace('\r', '')
            return f'"{match.group(1)}": "{fixed}"'
        
        s = re.sub(r'"(content|code)":\s*"(.*?)"', fix_newlines, s, flags=re.DOTALL)
        return s

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
        response = await llm.ainvoke([
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
                cleaned_args = clean_json(args_str)
                tool_calls.append({"name": name, "args": json.loads(cleaned_args)})
            except Exception as e:
                print(f"Failed to parse tool args for {name}: {e}. Args string: {args_str}")
    else:
        llm_with_tools = llm.bind_tools(AGENT_TOOLS)
        response = await llm_with_tools.ainvoke([
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
        "thought": f"Implemented code for {len(code_artifacts)} files. Proceeding to verification."
    }
