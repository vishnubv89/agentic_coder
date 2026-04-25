from rag.vector_store import VectorStoreManager
from rag.graph_store import CodebaseGraph

class HybridRetriever:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.graph_store = CodebaseGraph()

    def index_file(self, file_path: str, content: str):
        # Index in Vector RAG
        self.vector_store.add_documents(
            ids=[file_path],
            documents=[content],
            metadatas=[{"source": file_path}]
        )
        # Index in GraphRAG
        self.graph_store.add_file(file_path, content)

    def retrieve(self, query: str, entity_name: str = None) -> str:
        # Retrieve semantic chunks
        vector_results = self.vector_store.search(query)
        semantic_context = "\n\n".join(vector_results)
        
        # Retrieve structural graph context
        graph_context = ""
        if entity_name:
            graph_context = self.graph_store.get_context(entity_name)
            
        combined = "--- SEMANTIC CONTEXT (Vector DB) ---\n" + (semantic_context if semantic_context else "No semantic matches.") + "\n\n"
        combined += "--- STRUCTURAL CONTEXT (GraphRAG) ---\n" + (graph_context if graph_context else "No structural matches.")
        
        return combined

# Global instance for agents to use
hybrid_retriever = HybridRetriever()
