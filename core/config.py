import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini") # "gemini" or "ollama"
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    
    # LangChain Tracing
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
    
    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            print("⚠️ WARNING: GEMINI_API_KEY is not set but LLM_PROVIDER is 'gemini'.")

# Instantiate config
config = Config()
