from rag.retriever import hybrid_retriever

code_content = """
def hello_world():
    print("Hello, world!")

class Greeter:
    def greet(self):
        hello_world()
"""

hybrid_retriever.index_file("example.py", code_content)
print(hybrid_retriever.retrieve(query="print hello", entity_name="example.py::Greeter"))
