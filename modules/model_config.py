import json
import os
import requests
from typing import Dict, List, Optional


class ModelConfig:
    def __init__(self):
        self.config_file = "model_config.json"
        self.ollama_api_base = "http://localhost:11434/api"
        self.default_models = {
            "deepseek-coder": {
                "name": "deepseek-coder",
                "description": "Code-specialized model",
                "context_length": 8192,
                "parameters": {"temperature": 0.7, "top_p": 0.95},
            },
            "deepseek-r1": {
                "name": "deepseek-r1",
                "description": "General purpose model",
                "context_length": 4096,
                "parameters": {"temperature": 0.7, "top_p": 0.95},
            },
            "mistral": {
                "name": "mistral",
                "description": "Balanced model",
                "context_length": 4096,
                "parameters": {"temperature": 0.7, "top_p": 0.95},
            },
            "llama2": {
                "name": "llama2",
                "description": "General purpose model",
                "context_length": 4096,
                "parameters": {"temperature": 0.7, "top_p": 0.95},
            },
        }
        self.load_config()

    def load_config(self):
        """Load model configuration from file or create with defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    self.models = json.load(f)
            except:
                self.models = self.default_models
        else:
            self.models = self.default_models
            self.save_config()

    def save_config(self):
        """Save current model configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.models, f, indent=4)
            return True
        except:
            return False

    def fetch_ollama_models(self) -> List[Dict]:
        """Fetch available models from Ollama API"""
        try:
            response = requests.get(f"{self.ollama_api_base}/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            return []

    def get_ollama_model_details(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a specific Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_api_base}/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching model details for {model_name}: {e}")
            return None

    def sync_ollama_models(self) -> bool:
        """Synchronize available Ollama models with local configuration"""
        ollama_models = self.fetch_ollama_models()
        updated = False

        for model in ollama_models:
            model_name = model.get("name")
            if model_name:
                # Get detailed information about the model
                details = self.get_ollama_model_details(model_name)
                if details:
                    # Extract relevant information from details
                    model_config = {
                        "name": model_name,
                        "description": details.get("description", "Ollama model"),
                        "context_length": details.get("context_length", 4096),
                        "parameters": {
                            "temperature": 0.7,
                            "top_p": 0.95,
                            # Add any model-specific parameters from details
                            **details.get("parameters", {})
                        },
                        "ollama_metadata": {
                            "size": details.get("size"),
                            "digest": details.get("digest"),
                            "modified_at": details.get("modified_at"),
                            "system_prompt": details.get("system", ""),
                            "template": details.get("template", ""),
                        }
                    }
                    
                    if model_name not in self.models:
                        self.models[model_name] = model_config
                        updated = True
                    else:
                        # Update existing model metadata
                        self.models[model_name]["ollama_metadata"] = model_config["ollama_metadata"]
                        updated = True

        if updated:
            self.save_config()
        return updated

    def list_available_models(self) -> List[str]:
        """Return list of available model names"""
        return list(self.models.keys())

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get full model information"""
        return self.models.get(model_name)

    def get_model_parameters(self, model_name: str) -> Dict:
        """Get model parameters for inference"""
        model = self.models.get(model_name)
        if model:
            return model.get("parameters", {})
        return {}

    def update_model_parameters(self, model_name: str, parameters: Dict) -> bool:
        """Update parameters for a specific model"""
        if model_name in self.models:
            self.models[model_name]["parameters"].update(parameters)
            return self.save_config()
        return False

    def add_model(
        self, name: str, description: str, context_length: int, parameters: Dict
    ) -> bool:
        """Add a new model configuration"""
        if name not in self.models:
            self.models[name] = {
                "name": name,
                "description": description,
                "context_length": context_length,
                "parameters": parameters,
            }
            return self.save_config()
        return False

    def remove_model(self, name: str) -> bool:
        """Remove a model configuration"""
        if name in self.models:
            del self.models[name]
            return self.save_config()
        return False

    def get_ollama_metadata(self, model_name: str) -> Optional[Dict]:
        """Get Ollama-specific metadata for a model"""
        model = self.models.get(model_name)
        if model:
            return model.get("ollama_metadata")
        return None