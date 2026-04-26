import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import json

class Config:
    def __init__(self):
        # Default Workspace
        self.PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agent_config.json")
        
        # LLM Settings
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini") # "gemini" or "ollama"
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
        
        # Load persisted state
        self._load_persisted_state()
        
        # Gemini
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
        # Ollama
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # LangChain Tracing
        self.LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self.LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
        self.LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
        self.LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

    def _load_persisted_state(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    state = json.load(f)
                    self.PROJECT_ROOT = state.get("PROJECT_ROOT", self.PROJECT_ROOT)
                    self.LLM_PROVIDER = state.get("LLM_PROVIDER", self.LLM_PROVIDER)
                    self.OLLAMA_MODEL = state.get("OLLAMA_MODEL", self.OLLAMA_MODEL)
                    print(f"Config: Loaded persisted state from {self.CONFIG_FILE}")
            except Exception as e:
                print(f"Config: Failed to load persisted state: {e}")

    def save_state(self):
        state = {
            "PROJECT_ROOT": self.PROJECT_ROOT,
            "LLM_PROVIDER": self.LLM_PROVIDER,
            "OLLAMA_MODEL": self.OLLAMA_MODEL
        }
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(state, f, indent=4)
            print(f"Config: Saved state to {self.CONFIG_FILE}")
        except Exception as e:
            print(f"Config: Failed to save state: {e}")
    
    def validate(self):
        if self.LLM_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            print("⚠️ WARNING: GEMINI_API_KEY is not set but LLM_PROVIDER is 'gemini'.")

# Instantiate config
config = Config()
