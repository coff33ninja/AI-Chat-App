from PyQt6.QtCore import QThread, pyqtSignal
from .model_config import ModelConfig
from .ollama_client import OllamaClient
from .logger_helper import get_module_logger

# Initialize module logger
logger = get_module_logger(__name__)

class Worker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)  # New signal for streaming updates
    
    def __init__(self, prompt: str, model_name: str, model_config: ModelConfig):
        super().__init__()
        self.prompt = prompt
        self.model_name = model_name
        self.model_config = model_config
        self.ollama_client = None
        self.should_stop = False
        logger.debug(f"Worker initialized with model: {model_name}")
    
    def run(self):
        try:
            if self.should_stop:
                return

            # Initialize client in the thread
            self.ollama_client = OllamaClient()

            # Get model parameters
            params = self.model_config.get_model_parameters(self.model_name)
            
            logger.info(f"Running model {self.model_name} with parameters: {params}")
            
            # Generate response
            logger.debug(f"Generating response for prompt: {self.prompt[:50]}...")
            
            try:
                response = self.ollama_client.generate(
                    model=self.model_name,
                    prompt=self.prompt,
                    **params
                )
                
                if not self.should_stop and response:
                    logger.info("Response generated successfully")
                    logger.debug(f"Response: {response[:50]}...")
                    self.result_ready.emit(response)
                    
            except Exception as e:
                if "connection" in str(e).lower():
                    raise Exception("Failed to connect to Ollama. Please ensure the service is running.")
                else:
                    raise
                
        except Exception as e:
            if not self.should_stop:
                logger.error(f"Error in worker thread: {str(e)}")
                self.error_occurred.emit(str(e))
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.ollama_client:
            try:
                logger.debug("Cleaning up Ollama client")
                self.ollama_client.close()
                self.ollama_client = None
            except Exception as e:
                logger.error(f"Error cleaning up Ollama client: {str(e)}")
    
    def stop(self):
        """Stop the worker thread"""
        logger.info("Stopping worker thread")
        self.should_stop = True
        self.cleanup()
        if self.isRunning():
            logger.debug("Waiting for thread to finish")
            self.wait()  # Wait for the thread to finish
        
    def __del__(self):
        """Cleanup when the worker is deleted"""
        self.stop()
