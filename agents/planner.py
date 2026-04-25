from core.state import AgenticCoderState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from rag.retriever import hybrid_retriever
import json

def planner_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Planner Agent: Analyzing task and creating plan...")
    task = state.get("task_description", "")
    
    # RAG: Retrieve context from codebase
    print(f"Planner Agent: Retrieving codebase context for task: {task}...")
    context = hybrid_retriever.retrieve(task)
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", google_api_key=config.GEMINI_API_KEY, temperature=0)
    
    system_prompt = f"""You are the Lead Technical Planner of an AI Agentic Coding System.
    Your job is to break down the user's coding request into a clear, step-by-step implementation plan.
    
    --- CODEBASE CONTEXT ---
    {context}
    --- END CONTEXT ---

    Use the context above to ensure your plan aligns with existing code structures and dependencies.
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
