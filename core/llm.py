from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from core.config import config

def get_llm(temperature=0, use_tools=False):
    """Returns the configured LLM with automatic fallback to local Ollama if Gemini fails."""
    
    # Initialize Ollama as the local fallback
    ollama_llm = ChatOllama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=temperature
    )
    
    if config.LLM_PROVIDER == "ollama":
        print(f"Using Local Ollama: {config.OLLAMA_MODEL}")
        return ollama_llm
    
    # Default to Gemini with Ollama as fallback
    print(f"Using Gemini (3.1 Flash Lite) with Local Fallback ({config.OLLAMA_MODEL})")
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview",
        google_api_key=config.GEMINI_API_KEY,
        temperature=temperature,
        safety_settings={
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            "HARM_CATEGORY_CIVIC_INTEGRITY": "BLOCK_NONE",
        }
    )
    
    # Configure automatic fallback
    return gemini_llm.with_fallbacks([ollama_llm])
