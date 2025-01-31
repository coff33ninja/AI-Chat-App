from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional, Dict
import sys
import traceback
import logging
from .model_config import ModelConfig
from .ollama_client import OllamaClient

logger = logging.getLogger("main.worker")

class Worker(QThread):
    """Worker thread for handling model queries"""
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, query: str, model_name: str, model_config: ModelConfig):
        super().__init__()
        self.query = query
        self.model_name = model_name
        self.model_config = model_config
        self._is_running = True
        self.ollama_client = OllamaClient()
        
    def stop(self):
        """Safely stop the worker thread"""
        self._is_running = False
        self.wait()
        
    def run(self) -> None:
        """Execute the model query in a separate thread"""
        try:
            if not self._is_running:
                return

            # Get model parameters
            params: Dict = self.model_config.get_model_parameters(self.model_name)
            model_info = self.model_config.get_model_info(self.model_name)
            
            if not model_info:
                self.error_occurred.emit(f"Error: Model {self.model_name} not found in configuration")
                return
                
            if not params:
                self.error_occurred.emit(f"Error: Parameters for model {self.model_name} not found")
                return

            if not self._is_running:
                return

            try:
                # Check if model exists in Ollama
                if not self.ollama_client.check_model_exists(self.model_name):
                    self.error_occurred.emit(
                        f"Model {self.model_name} not found in Ollama. "
                        "Please run 'ollama pull {self.model_name}' to download it."
                    )
                    return

                # Generate response using Ollama
                logger.debug(f"Generating response for query: {self.query}")
                response = self.ollama_client.generate(
                    model=self.model_name,
                    prompt=self.query,
                    params=params
                )
                
                if self._is_running and response:
                    self.result_ready.emit(response)
                else:
                    self.error_occurred.emit("No response generated")

            except ConnectionError as ce:
                self.error_occurred.emit(
                    "Could not connect to Ollama service. "
                    "Please make sure Ollama is running by executing 'ollama serve'"
                )
            except TimeoutError as te:
                self.error_occurred.emit("Request to Ollama service timed out")
            except Exception as model_error:
                self.error_occurred.emit(f"Model Error: {str(model_error)}")
                
        except Exception as e:
            error_info = ''.join(traceback.format_exception(*sys.exc_info()))
            logger.error(f"Worker thread error: {error_info}")
            self.error_occurred.emit(f"System Error: {str(e)}\n{error_info}")
        finally:
            self.finished.emit()
            
    def __del__(self):
        """Ensure thread is properly cleaned up"""
        self.stop()
        self.wait()
