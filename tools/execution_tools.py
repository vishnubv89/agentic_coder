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
            ["python3", temp_file],
            cwd=config.PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return output
    except subprocess.TimeoutExpired:
        return "Execution failed: Script timed out after 15 seconds."
    except Exception as e:
        return f"Execution failed: {str(e)}"

@tool
def compile_and_run_cpp(code: str) -> str:
    """
    Compiles and executes C++ code. Use this to test .cpp files.
    """
    try:
        temp_src = os.path.join(config.PROJECT_ROOT, "temp_test.cpp")
        temp_bin = os.path.join(config.PROJECT_ROOT, "temp_test.out")
        
        with open(temp_src, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Compile
        compile_res = subprocess.run(
            ["g++", temp_src, "-o", temp_bin],
            cwd=config.PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if compile_res.returncode != 0:
            return f"Compilation Failed:\n{compile_res.stderr}"
            
        # Run
        run_res = subprocess.run(
            [temp_bin],
            cwd=config.PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = f"STDOUT:\n{run_res.stdout}\nSTDERR:\n{run_res.stderr}\nEXIT CODE: {run_res.returncode}"
        
        # Cleanup
        for f in [temp_src, temp_bin]:
            if os.path.exists(f): os.remove(f)
            
        return output
    except subprocess.TimeoutExpired:
        return "Execution failed: C++ program timed out."
    except Exception as e:
        return f"C++ Tool Error: {str(e)}"
