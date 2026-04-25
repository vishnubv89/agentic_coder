import os
from dotenv import load_dotenv

load_dotenv()

from agents.coder import coder_node

initial_state = {
    "messages": [("user", "Build a simple python calculator function")],
    "task_description": "Build a simple python calculator function",
    "plan": ["1. Write a calculator in calculator.py"],
    "current_step": 0,
    "code_artifacts": {},
    "test_results": "",
    "errors": [],
    "status": "coding"
}

try:
    print("Testing coder node...")
    result = coder_node(initial_state)
    print("Success! Coder returned:")
    print(result.get("code_artifacts"))
except Exception as e:
    print(f"Error testing node: {e}")
