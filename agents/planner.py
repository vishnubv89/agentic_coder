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
    
    # Session History: Files modified in this session
    code_artifacts = state.get("code_artifacts", {})
    history = "\n".join([f"- {f}" for f in code_artifacts.keys()]) if code_artifacts else "None"
    
    llm = get_llm(temperature=0)
    
    system_prompt = f"""You are an Expert Technical Planner. 
    Your task is to create a logical, step-by-step implementation plan for the user's request.

    --- CURRENT CODEBASE CONTEXT ---
    Directory Structure:
    {dir_tree}

    Files modified in current session:
    {history}

    Relevant Code Snippets:
    {context}
    --- END CONTEXT ---

    Instructions:
    1. Analyze the request and the existing codebase.
    2. Create a plan that is modular, simple, and follows best practices.
    3. Return ONLY a JSON array of strings representing the steps.
    Example: ["1. Create utility.py", "2. Update main.py to use utility"]"""
    
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
