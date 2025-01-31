import requests
import json
import logging
import subprocess
from typing import Dict, Optional

logger = logging.getLogger("main.ollama")

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def run_cli(self, model: str, prompt: str) -> Optional[str]:
        """Run the Ollama CLI command"""
        try:
            command = f"ollama run {model} \"{prompt}\""
            logger.debug(f"Running CLI command: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"CLI command failed: {result.stderr.strip()}")
                return None
        except Exception as e:
            logger.error(f"Error running CLI command: {str(e)}")
            return None

    def generate_response(self, model: str, prompt: str) -> Optional[str]:
        """Generate a response using the specified model via the API"""
        try:
            url = f"{self.base_url}/api/generate"
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt
            }
            
            logger.debug(f"Sending request to Ollama API for model {model}")
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "").strip()
            
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
