import os
import chromadb
from typing import List, Dict, Any

class VectorStoreManager:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="codebase")

    def clear_collection(self):
        """Wipes the current collection for a fresh index."""
        self.client.delete_collection(name="codebase")
        self.collection = self.client.get_or_create_collection(name="codebase")

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]] = None):
        if not documents:
            return
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas or [{} for _ in documents]
        )

    def search(self, query: str, n_results: int = 3) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if results and results['documents']:
            return results['documents'][0]
        return []
