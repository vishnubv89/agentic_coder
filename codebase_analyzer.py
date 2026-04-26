import re
from collections import Counter

class CodebaseStats:
    """
    Analyzes a context string to extract term frequencies and unique file paths.
    """
    def __init__(self, context: str):
        self.context = context

    def calculate_term_frequency(self):
        """
        Calculates the frequency of 'Vector' and 'Graph' (case-insensitive).
        """
        # Use regex to find words, ignoring case
        words = re.findall(r'\b\w+\b', self.context, re.IGNORECASE)
        counts = Counter(word.lower() for word in words)
        
        return {
            "Vector": counts.get("vector", 0),
            "Graph": counts.get("graph", 0)
        }

    def extract_unique_file_paths(self):
        """
        Identifies unique file paths ending in .py.
        """
        # Regex to find common file path patterns ending in .py
        # Matches strings like 'path/to/file.py', 'src/module.py', etc.
        pattern = r'[\w./-]+\.py'
        paths = re.findall(pattern, self.context)
        return sorted(list(set(paths)))

    def get_stats(self):
        """
        Returns a dictionary containing the term frequencies and unique file paths.
        """
        return {
            "term_frequencies": self.calculate_term_frequency(),
            "unique_file_paths": self.extract_unique_file_paths()
        }

if __name__ == "__main__":
    # Mock context string mimicking HybridRetriever output
    mock_context = """
    The HybridRetriever retrieved documents from rag/retriever.py and core/state.py.
    The Vector search identified relevant chunks in rag/retriever.py.
    The Graph search identified relationships in core/state.py and utils/helpers.py.
    We need to ensure Vector and Graph indices are updated.
    """

    analyzer = CodebaseStats(mock_context)
    stats = analyzer.get_stats()

    print("--- Codebase Statistics ---")
    print(f"Term Frequencies: {stats['term_frequencies']}")
    print(f"Unique File Paths: {stats['unique_file_paths']}")
