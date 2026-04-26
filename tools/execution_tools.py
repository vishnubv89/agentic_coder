import subprocess
import os
from langchain_core.tools import tool
from core.config import config

@tool
def execute_python_code(code: str) -> str:
    """
    Executes Python code in the workspace and returns the output.
    """
    try:
        temp_file = os.path.join(config.PROJECT_ROOT, "temp_exec.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)
            
        result = subprocess.run(
            ["python", temp_file],
            cwd=config.PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return output
    except subprocess.TimeoutExpired:
        return "Execution failed: Script timed out after 15 seconds."
    except Exception as e:
        return f"Execution failed: {str(e)}"
