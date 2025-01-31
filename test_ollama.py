# test_ollama.py
from modules.ollama_client import OllamaClient
import json

def main():
    # Initialize client
    client = OllamaClient()
    
    # Test 1: Check availability
    print("\n=== Testing Ollama Server Availability ===")
    available = client.is_available()
    print(f"Ollama server available: {available}")
    
    if not available:
        print("Error: Ollama server is not available. Please make sure it's running.")
        return
    
    # Test 2: List models
    print("\n=== Testing List Models ===")
    try:
        models = client.list_models()
        print("Available models:")
        print(json.dumps(models, indent=2))
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Test 3: Get model info
    print("\n=== Testing Get Model Info ===")
    try:
        # Get first model name from list or use a default
        model_name = models[0]['name'] if models else "codellama"
        model_info = client.get_model_info(model_name)
        print(f"Info for model '{model_name}':")
        print(json.dumps(model_info, indent=2))
    except Exception as e:
        print(f"Error getting model info: {e}")
    
    # Test 4: Generate text
    print("\n=== Testing Text Generation ===")
    try:
        prompt = "Write a hello world program in Python"
        print(f"Prompt: {prompt}")
        response = client.generate(model_name, prompt)
        print("Response:")
        print(response)
    except Exception as e:
        print(f"Error generating text: {e}")

if __name__ == "__main__":
    main()