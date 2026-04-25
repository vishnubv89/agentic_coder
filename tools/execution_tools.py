import subprocess
from langchain_core.tools import tool

@tool
def execute_python_code(code: str) -> str:
    """
    Executes Python code in an isolated subprocess and returns the output.
    Use this to run tests or verify scripts.
    """
    try:
        # Write code to a temporary file
        with open("temp_exec.py", "w") as f:
            f.write(code)
            
        # Execute it
        result = subprocess.run(
            ["python", "temp_exec.py"],
            capture_output=True,
            text=True,
            timeout=10 # 10 second timeout
        )
        
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
        return output
    except subprocess.TimeoutExpired:
        return "Execution failed: Script timed out after 10 seconds."
    except Exception as e:
        return f"Execution failed: {str(e)}"
