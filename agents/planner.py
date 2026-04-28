from core.state import AgenticCoderState
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from rag.retriever import hybrid_retriever
from core.llm import get_llm
import json
import os

def get_directory_tree(path, indent=""):
    """Generates a text representation of the directory tree."""
    tree = ""
    ignore = {".git", "venv", "__pycache__", "chroma_db", "node_modules", ".gemini"}
    try:
        for item in sorted(os.listdir(path)):
            if item in ignore or item.startswith('.'):
                continue
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                tree += f"{indent}📁 {item}/\n"
                tree += get_directory_tree(full_path, indent + "  ")
            else:
                tree += f"{indent}📄 {item}\n"
    except:
        pass
    return tree

async def planner_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Planner Agent: Analyzing task and creating plan...")
    task = state.get("task_description", "")
    
    # RAG: Retrieve context and directory structure
    print(f"Planner Agent: Retrieving codebase context and structure...")
    context = hybrid_retriever.retrieve(task)
    dir_tree = get_directory_tree(config.PROJECT_ROOT)
    print(f"Planner Agent: Context retrieved ({len(context)} chars). Preview: {context[:200]}...")
    
    # Working Memory: Code written in the current session
    code_artifacts = state.get("code_artifacts", {})
    working_memory = "\n".join([f"### File: {f}\n{c[:500]}..." for f, c in code_artifacts.items()]) if code_artifacts else "None yet."
    
    llm = get_llm(temperature=0)
    
    system_prompt = f"""You are the Lead Technical Planner of an AI Agentic Coding System.
    Your job is to break down the user's coding request into a clear, step-by-step implementation plan.
    
    --- WORKING MEMORY (Code written in this session) ---
    {working_memory}
    
    --- PROJECT DIRECTORY STRUCTURE ---
    {dir_tree}
    
    --- RELEVANT CODE CONTEXT (RAG) ---
    {context}
    --- END CONTEXT ---

    CRITICAL RULES:
    1. PRIORITIZE the 'WORKING MEMORY' code. If the user asks to modify something you just wrote, use the memory, NOT the RAG context which might be outdated.
    2. IGNORE irrelevant boilerplate or unrelated 'CPU/Memory monitoring' code if it doesn't apply to the task.
    3. Use the directory structure and code context above to ensure your plan aligns with existing architecture.
    Return ONLY a JSON array of strings, where each string is a step in the plan.
    Example: ["1. Set up the Python project.", "2. Write the main logic in app.py", "3. Write tests in test_app.py"]"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Task: {task}")
    ]
    
    response = await llm.ainvoke(messages)
    
    try:
        content = response.content
        if isinstance(content, list):
            content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
        elif not isinstance(content, str):
            content = str(content)
            
        # Robust extraction: Find the first [ and last ]
        import re
        match = re.search(r'(\[.*\])', content, re.DOTALL)
        if match:
            json_str = match.group(1)
            # Clean up unescaped newlines which cause JSON errors
            # Only replace newlines that are NOT part of a string (this is hard, 
            # but usually LLMs put them everywhere)
            # Simple approach: Replace literal newlines with \n if they are between quotes
            # or just clean up the whole thing for common mistakes
            try:
                plan = json.loads(json_str)
            except json.JSONDecodeError:
                # If first attempt fails, try a more aggressive cleanup
                cleaned_json = json_str.replace('\n', '\\n').replace('\r', '')
                # Fix cases where it replaced needed newlines
                cleaned_json = cleaned_json.replace('\\n{', '{').replace('\\n}', '}').replace('[\\n', '[').replace('\\n]', ']').replace(',\\n', ',')
                plan = json.loads(cleaned_json)
        else:
            raise ValueError("No JSON array found in response")

        if not isinstance(plan, list):
            plan = [str(plan)]
    except Exception as e:
        print(f"Failed to parse plan JSON: {e}. Raw output: {response.content}")
        plan = ["1. Implement the requested feature.", "2. Test the implementation."]
        
    return {
        "plan": plan,
        "status": "coding",
        "messages": [response],
        "retry_count": 0,
        "thought": f"Created a {len(plan)}-step execution plan. Transitioning to Coding phase."
    }
