import os
from rag.retriever import hybrid_retriever

# All file types that are useful to index for a full-stack project
INDEXABLE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".scss",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt", ".sh",
    ".env.example",
}

from core.config import config

def index_codebase(root_dir: str = None):
    """Walks the codebase and indexes all useful files into Hybrid RAG."""
    if root_dir is None:
        root_dir = config.PROJECT_ROOT
    
    # Clear existing index for fresh start
    hybrid_retriever.clear_index()
        
    print(f"Starting codebase indexing in {root_dir}...")
    
    # Files to ignore
    ignore_dirs = {".git", "venv", "__pycache__", "chroma_db", "node_modules", ".gemini"}
    
    indexed_count = 0
    for root, dirs, files in os.walk(root_dir):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in INDEXABLE_EXTENSIONS or file == ".env.example":
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

def index_single_file(file_path: str, root_dir: str = None):
    """Indexes or re-indexes a single file into the RAG."""
    if root_dir is None:
        root_dir = config.PROJECT_ROOT
        
    ext = os.path.splitext(file_path)[1].lower()
    if ext in INDEXABLE_EXTENSIONS or os.path.basename(file_path) == ".env.example":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            rel_path = os.path.relpath(file_path, root_dir)
            hybrid_retriever.index_file(rel_path, content)
            print(f"RAG Updated: Indexed {rel_path}")
        except Exception as e:
            print(f"Error re-indexing {file_path}: {e}")

if __name__ == "__main__":
    index_codebase()
