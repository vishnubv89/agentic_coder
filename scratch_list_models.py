import requests
import json

def list_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if not models:
                print("No models found in Ollama.")
            else:
                print("Available Ollama models:")
                for m in models:
                    print(f" - {m['name']}")
        else:
            print(f"Failed to connect to Ollama. Status: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")

if __name__ == "__main__":
    list_ollama_models()
