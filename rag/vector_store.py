import os
import chromadb
from typing import List, Dict, Any

class VectorStoreManager:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensures the collection reference is valid."""
        try:
            self.collection = self.client.get_or_create_collection(name="codebase")
        except Exception as e:
            print(f"VectorStore: Error ensuring collection: {e}")
            # Fallback/Retry logic if needed

    def clear_collection(self):
        """Wipes the current collection for a fresh index."""
        try:
            self.client.delete_collection(name="codebase")
        except:
            pass # Already deleted or doesn't exist
        self._ensure_collection()

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]] = None):
        if not documents:
            return
        self._ensure_collection()
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas or [{} for _ in documents]
            )
        except Exception as e:
            print(f"VectorStore: Error adding docs: {e}")

    def search(self, query: str, n_results: int = 3) -> List[str]:
        self._ensure_collection()
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            if results and results['documents']:
                return results['documents'][0]
        except Exception as e:
            print(f"VectorStore: Search error: {e}")
        return []
