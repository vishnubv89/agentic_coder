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

def planner_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Planner Agent: Analyzing task and creating plan...")
    task = state.get("task_description", "")
    
    # RAG: Retrieve context and directory structure
    print(f"Planner Agent: Retrieving codebase context and structure...")
    context = hybrid_retriever.retrieve(task)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_tree = get_directory_tree(project_root)
    print(f"Planner Agent: Context retrieved ({len(context)} chars). Preview: {context[:200]}...")
    
    llm = get_llm(temperature=0)
    
    system_prompt = f"""You are the Lead Technical Planner of an AI Agentic Coding System.
    Your job is to break down the user's coding request into a clear, step-by-step implementation plan.
    
    --- PROJECT DIRECTORY STRUCTURE ---
    {dir_tree}
    
    --- RELEVANT CODE CONTEXT ---
    {context}
    --- END CONTEXT ---

    Use the directory structure and code context above to ensure your plan aligns with existing architecture and dependencies.
    Return ONLY a JSON array of strings, where each string is a step in the plan.
    Example: ["1. Set up the Python project.", "2. Write the main logic in app.py", "3. Write tests in test_app.py"]"""
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Create a plan for this task: {task}")
    ])
    
    try:
        content = response.content
        if isinstance(content, list):
            content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
        elif not isinstance(content, str):
            content = str(content)
            
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        plan = json.loads(content.strip())
        if not isinstance(plan, list):
            plan = [str(plan)]
    except Exception as e:
        print(f"Failed to parse plan JSON. Raw output: {response.content}")
        plan = ["1. Implement the requested feature.", "2. Test the implementation."]
        
    return {
        "plan": plan,
        "status": "coding",
        "messages": [response]
    }
