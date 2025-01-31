from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional, Dict
from .model_config import ModelConfig

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
                # TODO: Implement actual model inference here
                # For now, return a placeholder response
                response = f"Response from {self.model_name} (placeholder)"
                
                if self._is_running:
                    self.result_ready.emit(response)
            except ConnectionError as ce:
                self.error_occurred.emit(f"Connection Error: Could not connect to the AI model. Please check your internet connection.")
            except TimeoutError as te:
                self.error_occurred.emit(f"Timeout Error: The request to the AI model took too long.")
            except Exception as model_error:
                self.error_occurred.emit(f"Model Error: {str(model_error)}")
                
        except Exception as e:
            error_info = ''.join(traceback.format_exception(*sys.exc_info()))
            self.error_occurred.emit(f"System Error: {str(e)}\n{error_info}")
        finally:
            self.finished.emit()
            
    def __del__(self):
        """Ensure thread is properly cleaned up"""
        self.stop()
        self.wait()
