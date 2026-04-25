import os
from rag.retriever import hybrid_retriever

def index_codebase(root_dir: str = "."):
    """Walks the codebase and indexes all python files into Hybrid RAG."""
    print(f"Starting codebase indexing in {root_dir}...")
    
    # Files to ignore
    ignore_dirs = {".git", "venv", "__pycache__", "chroma_db", "node_modules", ".gemini"}
    
    indexed_count = 0
    for root, dirs, files in os.walk(root_dir):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Use relative path as ID
                    rel_path = os.path.relpath(file_path, root_dir)
                    hybrid_retriever.index_file(rel_path, content)
                    indexed_count += 1
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
                    
    print(f"Indexing complete. Indexed {indexed_count} files.")

if __name__ == "__main__":
    index_codebase()
