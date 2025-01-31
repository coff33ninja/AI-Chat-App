import os
import json
import logging
import requests
from typing import Dict, List, Optional
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class ModelConfig:
    def __init__(self, config_file: str = "config/model_config.json"):
        # Default models configuration
        self.default_models = {
            "llama2": {
                "name": "llama2",
                "description": "Llama 2 is a state-of-the-art large language model.",
                "context_length": 4096,
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "repeat_penalty": 1.1
                }
            },
            "mistral": {
                "name": "mistral",
                "description": "Mistral is an efficient and powerful language model.",
                "context_length": 8192,
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "repeat_penalty": 1.1
                }
            }
        }
        
        self.config_file = config_file
        self.ollama_client = OllamaClient()
        logger.info(f"Initializing ModelConfig with config file: {config_file}")
        try:
            self.load_config()
            # Sync models at initialization
            if self.check_ollama_available():
                logger.info("Ollama is available, syncing models...")
                self.sync_models()
            else:
                logger.warning("Ollama is not available, using default models")
            logger.debug("Model configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model configuration: {str(e)}", exc_info=True)
            raise

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
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self.models, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            return False

    def check_ollama_available(self) -> bool:
        """Check if Ollama server is available"""
        return self.ollama_client.is_available()

    def get_model_details(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a model from Ollama"""
        try:
            model_info = self.ollama_client.get_model_info(model_name)
            if model_info:
                return {
                    "name": model_name,
                    "description": model_info.get('description', 'No description available'),
                    "context_length": model_info.get('context_length', 4096),
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "repeat_penalty": 1.1
                    }
                }
        except Exception as e:
            logger.error(f"Error getting details for {model_name}: {str(e)}")
        return None

    def sync_models(self) -> tuple[bool, str]:
        """Synchronize available models with Ollama
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Check Ollama availability first
            if not self.check_ollama_available():
                msg = "Ollama service is not available. Please ensure Ollama is running."
                logger.warning(msg)
                return False, msg

            # Get models from Ollama client
            models = self.ollama_client.list_models()
            if not models:
                msg = "No models found in Ollama. Please install some models first."
                logger.warning(msg)
                return False, msg

            updated = False
            synced_models = []
            failed_models = []
            
            # Create a copy of current models to preserve custom settings
            current_models = self.models.copy()

            for model in models:
                if not isinstance(model, dict):
                    continue
                    
                model_name = model.get("name")
                if not model_name:
                    continue

                try:
                    # Get model details using the dedicated method
                    model_details = self.get_model_details(model_name)
                    if not model_details:
                        failed_models.append(model_name)
                        continue

                    # Preserve existing model settings if available
                    if model_name in current_models:
                        existing_model = current_models[model_name]
                        if isinstance(existing_model, dict):
                            # Keep existing parameters but update metadata
                            model_details["parameters"] = existing_model.get("parameters", model_details["parameters"])
                            model_details["description"] = existing_model.get("description", model_details["description"])

                    self.models[model_name] = model_details
                    synced_models.append(model_name)
                    updated = True
                    
                except Exception as model_error:
                    logger.error(f"Error syncing model {model_name}: {str(model_error)}")
                    failed_models.append(model_name)

            if updated:
                self.save_config()
                
            # Prepare status message
            if synced_models and not failed_models:
                msg = f"Successfully synced {len(synced_models)} models: {', '.join(synced_models)}"
                logger.info(msg)
                return True, msg
            elif synced_models and failed_models:
                msg = f"Partially synced models.\nSuccessful: {', '.join(synced_models)}\nFailed: {', '.join(failed_models)}"
                logger.warning(msg)
                return True, msg
            else:
                msg = "Failed to sync any models"
                logger.error(msg)
                return False, msg

        except Exception as e:
            msg = f"Error syncing models: {str(e)}"
            logger.error(msg)
            return False, msg
    def check_ollama_available(self) -> tuple[bool, str]:
        """Check if Ollama server is available
        Returns:
            tuple: (available: bool, message: str)
        """
        try:
            if self.ollama_client.is_available():
                return True, "Ollama service is available"
            return False, "Ollama service is not responding"
        except Exception as e:
            return False, f"Error checking Ollama availability: {str(e)}"


    def get_model_details(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a model from Ollama"""
        try:
            model_info = self.ollama_client.get_model_info(model_name)
            if model_info:
                return {
                    "name": model_name,
                    "description": model_info.get('description', 'No description available'),
                    "context_length": model_info.get('context_length', 4096),
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "repeat_penalty": 1.1
                    }
                }
        except Exception as e:
            logger.error(f"Error getting details for {model_name}: {str(e)}")
        return None

    def sync_models(self) -> bool:
        """Synchronize available models with Ollama"""
        try:
            # Get models from Ollama client
            models = self.ollama_client.list_models()
            if not models:
                logger.warning("No models found from Ollama")
                return False

            updated = False
            # Create a copy of current models to preserve custom settings
            current_models = self.models.copy()

            for model in models:
                if not isinstance(model, dict):
                    continue
                    
                model_name = model.get("name")
                if not model_name:
                    continue

                # Get model details using the dedicated method
                model_details = self.get_model_details(model_name)
                if not model_details:
                    continue

                # Preserve existing model settings if available
                if model_name in current_models:
                    existing_model = current_models[model_name]
                    if isinstance(existing_model, dict):
                        # Keep existing parameters but update metadata
                        model_details["parameters"] = existing_model.get("parameters", model_details["parameters"])
                        model_details["description"] = existing_model.get("description", model_details["description"])

                self.models[model_name] = model_details
                updated = True

            if updated:
                self.save_config()
                
            return True

        except Exception as e:
            logger.error(f"Error syncing models: {str(e)}")
            return False

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
