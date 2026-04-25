import os
from langchain_core.tools import tool

@tool
def read_file(file_path: str) -> str:
    """Reads the contents of a file from the file system."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Writes content to a file. Overwrites the file if it exists."""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"

@tool
def list_directory(directory_path: str = ".") -> str:
    """Lists all files and directories in the given path."""
    try:
        return "\n".join(os.listdir(directory_path))
    except Exception as e:
        return f"Error listing directory {directory_path}: {str(e)}"
