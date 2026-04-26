import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self):
        # Workspace
        self.PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # LLM Settings
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini") # "gemini" or "ollama"
        
        # Gemini
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
        # Ollama
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
        
        # LangChain Tracing
        self.LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
        self.LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
        self.LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
    
    def validate(self):
        if self.LLM_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            print("⚠️ WARNING: GEMINI_API_KEY is not set but LLM_PROVIDER is 'gemini'.")

# Instantiate config
config = Config()
