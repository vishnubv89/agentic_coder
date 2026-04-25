from core.state import AgenticCoderState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import config
from tools import AGENT_TOOLS

def coder_node(state: AgenticCoderState) -> AgenticCoderState:
    print("Coder Agent: Writing code based on plan...")
    task = state.get("task_description", "")
    plan = state.get("plan", [])
    errors = state.get("errors", [])
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=config.GEMINI_API_KEY, temperature=0.2)
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    
    system_prompt = f"""You are an Expert Coder Agent.
    Your goal is to implement the given task based on the provided plan.
    Task: {task}
    Plan: {plan}
    
    You have access to file writing tools to generate the code artifacts.
    If you encountered previous errors, they are listed here to fix: {errors}
    
    Call the necessary tools to write out the code. Once finished, explain what you wrote.
    """
    
    response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Please implement the code now.")
    ])
    
    if response.tool_calls:
        print(f"Coder Agent is using {len(response.tool_calls)} tools...")
        from tools.file_tools import write_file, read_file
        tool_map = {
            "write_file": write_file,
            "read_file": read_file
        }
        for tc in response.tool_calls:
            tool_fn = tool_map.get(tc["name"])
            if tool_fn:
                print(f"  -> Executing {tc['name']} with args {tc['args']}")
                try:
                    tool_fn.invoke(tc["args"])
                except Exception as e:
                    print(f"  -> Tool error: {e}")
    
    return {
        "status": "testing",
        "messages": [response]
    }
