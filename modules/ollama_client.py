import requests
from typing import Dict, Any, Optional, List
from .logger_helper import get_module_logger

logger = get_module_logger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        logger.info(f"Initializing OllamaClient with base URL: {base_url}")
        
    def generate(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        """Generate a response using the Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        data = {
            "model": model,
            "prompt": prompt,
            **kwargs
        }
        
        logger.debug(f"Generating response for model {model} with parameters: {kwargs}")
        
        try:
            response = self.session.post(url, json=data, stream=True)
            response.raise_for_status()
            
            # Stream the response and concatenate
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        # Decode the line and parse JSON
                        json_response = response.json()
                        if "response" in json_response:
                            full_response += json_response["response"]
                    except Exception as e:
                        # Skip lines that can't be parsed
                        continue

            logger.info(f"Successfully generated response from {model}")
            return full_response
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Ollama API: {str(e)}", exc_info=True)
            raise Exception("Failed to connect to Ollama. Is the service running?")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Ollama API: {str(e)}", exc_info=True)
            raise Exception(f"Ollama API error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error during generation: {str(e)}", exc_info=True)
            raise
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            models = data.get('models', [])
            # Ensure each model has the required structure
            formatted_models = []
            for model in models:
                if isinstance(model, str):
                    # If model is just a string, create a basic model info structure
                    formatted_models.append({
                        'name': model,
                        'description': f'Model {model}',
                        'details': {'name': model}
                    })
                elif isinstance(model, dict):
                    formatted_models.append(model)
            return formatted_models
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        try:
            # First try to get model details from tags
            models = self.list_models()
            for model in models:
                if isinstance(model, dict) and model.get('name') == model_name:
                    return {
                        'name': model_name,
                        'description': model.get('description', f'Model {model_name}'),
                        'details': model
                    }
                elif isinstance(model, str) and model == model_name:
                    return {
                        'name': model_name,
                        'description': f'Model {model_name}',
                        'details': {'name': model_name}
                    }
            
            # If not found in tags, try the show endpoint
            url = f"{self.base_url}/api/show"
            response = self.session.post(url, json={"name": model_name})
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, str):
                # Handle case where response is a string
                return {
                    'name': model_name,
                    'description': f'Model {model_name}',
                    'details': {'name': model_name}
                }
            else:
                return {
                    'name': model_name,
                    'description': data.get('description', f'Model {model_name}'),
                    'details': data
                }
            
        except Exception as e:
            logger.error(f"Error getting model info for {model_name}: {str(e)}")
            # Return a basic info object instead of raising an error
            return {
                'name': model_name,
                'description': f'Model {model_name}',
                'details': {'name': model_name}
            }

    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            url = f"{self.base_url}/api/version"
            response = self.session.get(url)
            response.raise_for_status()
            return True
        except:
            return False

    def close(self):
        """Close the requests session"""
        try:
            if hasattr(self, 'session') and self.session:
                logger.info("Closing Ollama client session")
                self.session.close()
        except Exception as e:
            logger.error(f"Error closing Ollama client session: {str(e)}")

    def __del__(self):
        """Cleanup when the client is deleted"""
        self.close()
