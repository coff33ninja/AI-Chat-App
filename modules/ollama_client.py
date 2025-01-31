import requests
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger("main.ollama")

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def generate_response(self, messages: list) -> Optional[str]:
        """Generate a response using the chat completion API"""
        try:
            url = f"{self.base_url}/api/chat"
            
            # Prepare request payload for chat completion
            payload = {
                "model": messages[0].get("model", "llama2"),
                "messages": messages,
                "stream": False
            }
                
            logger.debug(f"Sending chat request to Ollama API")
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if "message" in data:
                return data["message"]["content"]
            return "Error: Unexpected response format"
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama service")
            raise ConnectionError("Could not connect to Ollama service. Make sure it's running.")
        except requests.exceptions.Timeout:
            logger.error("Request to Ollama service timed out")
            raise TimeoutError("Request to Ollama service timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Ollama service: {str(e)}")
            raise Exception(f"Error communicating with Ollama service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {str(e)}")
            raise
            
    def list_models(self) -> list:
        """Get list of available models"""
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
            
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
            
    def check_model_exists(self, model_name: str) -> bool:
        """Check if a model exists"""
        try:
            models = self.list_models()
            return model_name in models
        except:
            return False
