import ast
import os
import networkx as nx
from typing import List, Dict

class CodebaseGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_file(self, file_path: str, content: str):
        self.graph.add_node(file_path, type="file")
        
        # Only parse AST for Python files
        if not file_path.endswith(".py"):
            return

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = f"{file_path}::{node.name}"
                    self.graph.add_node(func_name, type="function")
                    self.graph.add_edge(file_path, func_name, relation="contains")
                elif isinstance(node, ast.ClassDef):
                    class_name = f"{file_path}::{node.name}"
                    self.graph.add_node(class_name, type="class")
                    self.graph.add_edge(file_path, class_name, relation="contains")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.graph.add_edge(file_path, alias.name, relation="imports")
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.graph.add_edge(file_path, node.module, relation="imports_from")
        except:
            # Silent fail for broken python files or non-python content
            pass

    def get_context(self, entity_name: str) -> str:
        context = []
        for node in self.graph.nodes:
            if isinstance(node, str) and entity_name in node:
                neighbors = list(self.graph.neighbors(node))
                if neighbors:
                    context.append(f"Entity '{node}' is related to: {', '.join(map(str, neighbors))}")
        return "\n".join(context) if context else f"No structural context found for '{entity_name}'."
