from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from core.config import config

def get_llm(temperature=0):
    """Returns the configured LLM (Gemini or Ollama)."""
    if config.LLM_PROVIDER == "ollama":
        print(f"Using Local Ollama: {config.OLLAMA_MODEL}")
        return ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=temperature
        )
    else:
        # Default to Gemini
        return ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview",
            google_api_key=config.GEMINI_API_KEY,
            temperature=temperature
        )
