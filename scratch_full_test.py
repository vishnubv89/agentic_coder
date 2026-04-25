import os
from dotenv import load_dotenv

load_dotenv()

from core.graph import build_graph

graph = build_graph()
initial_state = {
    "messages": [("user", "Create a Python script named data_analyzer.py. The script should contain a function that takes a list of numbers and calculates the mean, median, and mode without using any external libraries. Return a formatted string. Handle empty lists. Write a test block at the bottom with [10, 2, 38, 23, 38, 23, 21].")],
    "task_description": "Create a Python script named data_analyzer.py...",
    "plan": [],
    "current_step": 0,
    "code_artifacts": {},
    "test_results": "",
    "errors": [],
    "status": "planning"
}

print("Running graph...")
final_test_results = ""
for event in graph.stream(initial_state, stream_mode="values"):
    print("--- STATE UPDATE ---")
    print("STATUS:", event.get("status"))
    if event.get("test_results"):
        final_test_results = event.get("test_results")

print("FINAL TEST RESULTS:")
print(final_test_results)
