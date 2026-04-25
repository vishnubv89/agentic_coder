from langgraph.graph import StateGraph, END, START
from core.state import AgenticCoderState
from agents.planner import planner_node
from agents.coder import coder_node
from agents.tester import tester_node

def route_tester_output(state: AgenticCoderState):
    status = state.get("status")
    if status == "failed":
        return "coder"
    return END

def build_graph():
    builder = StateGraph(AgenticCoderState)
    
    # Add nodes
    builder.add_node("planner", planner_node)
    builder.add_node("coder", coder_node)
    builder.add_node("tester", tester_node)
    
    # Add edges
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "coder")
    builder.add_edge("coder", "tester")
    
    builder.add_conditional_edges(
        "tester",
        route_tester_output,
        {"coder": "coder", END: END}
    )
    
    return builder.compile()
