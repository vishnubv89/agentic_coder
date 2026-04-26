from typing import Annotated, TypedDict, List, Dict, Any, Optional
import operator
from langchain_core.messages import BaseMessage

class AgenticCoderState(TypedDict):
    """
    State for the AgenticCoder LangGraph.
    
    Attributes:
        messages: The history of messages between the user and agents.
        task_description: The original task description.
        plan: The execution plan created by the Planner Agent.
        current_step: The current step of the plan being executed.
        code_artifacts: Dictionary of created/modified files {filename: content}.
        test_results: Results from the Tester Agent.
        errors: Any errors encountered during execution.
        status: The current status ('planning', 'coding', 'testing', 'completed', 'failed').
    """
    messages: Annotated[List[BaseMessage], operator.add]
    task_description: str
    plan: List[str]
    current_step: int
    code_artifacts: Dict[str, str]
    test_results: str
    errors: List[str]
    status: str
    retry_count: int
    thought: str
