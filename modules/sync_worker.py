from PyQt6.QtCore import QThread, pyqtSignal
import logging
from typing import Dict, List
from .model_config import ModelConfig
from .ollama_client import OllamaClient

logger = logging.getLogger("main.sync_worker")

class ModelSyncWorker(QThread):
    """Worker thread for synchronizing Ollama models"""
    sync_complete = pyqtSignal(bool)  # True if successful, False if failed
    error_occurred = pyqtSignal(str)
    models_updated = pyqtSignal(list)  # List of available model names
    
    def __init__(self, model_config: ModelConfig):
        super().__init__()
        self.model_config = model_config
        self.ollama_client = OllamaClient()
        self._is_running = True
        
    def stop(self):
        """Safely stop the worker thread"""
        self._is_running = False
        self.wait()
        
    def run(self) -> None:
        """Execute the model synchronization in a separate thread"""
        try:
            if not self._is_running:
                return

            # Fetch available models from Ollama
            try:
                models = self.ollama_client.list_models()
                if not models:
                    self.error_occurred.emit("No models found in Ollama")
                    self.sync_complete.emit(False)
                    return

                updated = False
                for model in models:
                    if not self._is_running:
                        return
                        
                    model_name = model.get("name")
                    if not model_name:
                        continue

                    # Get model details from Ollama
                    try:
                        details = self.ollama_client.get_model_details(model_name)
                        if details:
                            # Extract relevant information
                            model_config = {
                                "name": model_name,
                                "description": details.get("description", "Ollama model"),
                                "context_length": details.get("context_length", 4096),
                                "parameters": {
                                    "temperature": 0.7,
                                    "top_p": 0.95,
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
                            
                            # Update model in configuration
                            if model_name not in self.model_config.models:
                                self.model_config.add_model(
                                    name=model_name,
                                    description=model_config["description"],
                                    context_length=model_config["context_length"],
                                    parameters=model_config["parameters"]
                                )
                            else:
                                # Update existing model metadata
                                current_model = self.model_config.models[model_name]
                                current_model["ollama_metadata"] = model_config["ollama_metadata"]
                                current_model["description"] = model_config["description"]
                                current_model["context_length"] = model_config["context_length"]
                                current_model["parameters"].update(model_config["parameters"])
                            
                            updated = True
                            
                    except Exception as detail_error:
                        logger.error(f"Error getting details for {model_name}: {detail_error}")
                        continue

                if updated:
                    self.model_config.save_config()
                
                # Emit the list of available models
                self.models_updated.emit(self.model_config.list_available_models())
                self.sync_complete.emit(True)

            except ConnectionError:
                self.error_occurred.emit(
                    "Could not connect to Ollama service. "
                    "Please make sure Ollama is running by executing 'ollama serve'"
                )
                self.sync_complete.emit(False)
            except Exception as e:
                self.error_occurred.emit(f"Error syncing models: {str(e)}")
                self.sync_complete.emit(False)
                
        except Exception as e:
            logger.error(f"Sync worker thread error: {str(e)}")
            self.error_occurred.emit(f"System Error: {str(e)}")
            self.sync_complete.emit(False)
            
    def __del__(self):
        """Ensure thread is properly cleaned up"""
        self.stop()
        self.wait()