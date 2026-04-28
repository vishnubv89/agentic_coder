import os
from langchain_core.tools import tool
from core.config import config

def get_safe_path(rel_path: str) -> str:
    # Ensure rel_path is indeed relative
    if os.path.isabs(rel_path):
        # If it's already in PROJECT_ROOT, keep it
        if rel_path.startswith(config.PROJECT_ROOT):
            return rel_path
        # Otherwise, take just the basename or relative part
        rel_path = os.path.basename(rel_path)
    return os.path.normpath(os.path.join(config.PROJECT_ROOT, rel_path))

@tool
def read_file(file_path: str) -> str:
    """Reads the contents of a file from the workspace."""
    safe_path = get_safe_path(file_path)
    try:
        if not os.path.exists(safe_path):
            return f"Error: File {file_path} not found at {safe_path}"
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Writes content to a file in the workspace."""
    safe_path = get_safe_path(file_path)
    try:
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Real-time indexing for RAG memory
        try:
            from rag.indexer import index_single_file
            index_single_file(safe_path)
        except Exception as re_idx_err:
            print(f"Non-critical: Failed to re-index {file_path}: {re_idx_err}")
            
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"

@tool
def list_directory(directory_path: str = ".") -> str:
    """Lists files and directories in the workspace."""
    safe_path = get_safe_path(directory_path)
    try:
        items = os.listdir(safe_path)
        return f"Contents of {directory_path}:\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing directory {directory_path}: {str(e)}"
