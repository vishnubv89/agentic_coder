import sys
from core.graph import build_graph

def main():
    print("Welcome to AgenticCoder - Multi-Agent AI System")
    print("Type 'exit' or 'quit' to stop.")
    
    graph = build_graph()
    
    while True:
        user_input = input("\nEnter your coding task: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        print("\n--- Processing Task ---")
        initial_state = {
            "messages": [("user", user_input)],
            "task_description": user_input,
            "plan": [],
            "current_step": 0,
            "code_artifacts": {},
            "test_results": "",
            "errors": [],
            "status": "planning"
        }
        
        for event in graph.stream(initial_state, stream_mode="values"):
            if "status" in event:
                print(f"[{event['status'].upper()}] - Progress updated")
            
        print("\n--- Task Completed ---")
        
if __name__ == "__main__":
    main()
