import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QComboBox,
    QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from modules.worker import Worker
from modules.model_config import ModelConfig

class SimpleChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat Test")
        self.setMinimumSize(800, 600)
        
        # Initialize model config
        self.model_config = ModelConfig()
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Model selection area
        model_layout = QHBoxLayout()
        
        model_label = QLabel("Select Model:")
        model_layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        for model_name in self.model_config.list_available_models():
            model_info = self.model_config.get_model_info(model_name)
            self.model_selector.addItem(
                f"{model_name} - {model_info['description']}", 
                userData=model_name
            )
        self.model_selector.currentIndexChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_selector, stretch=1)
        
        layout.addLayout(model_layout)
        
        # Status indicator
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green;")
        layout.addWidget(self.status_label)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Add initial message
        self.chat_display.append("Welcome to the AI Chat Test Application!")
        self.chat_display.append("\nAvailable Models:")
        for model_name in self.model_config.list_available_models():
            model_info = self.model_config.get_model_info(model_name)
            self.chat_display.append(f"• {model_name}: {model_info['description']}")
        self.chat_display.append("\nSelect a model and start chatting!")
        
        # Initialize worker as None
        self.worker = None
        
    def on_model_changed(self, index):
        """Handle model selection change"""
        model_name = self.model_selector.currentData()
        model_info = self.model_config.get_model_info(model_name)
        self.status_label.setText(f"Selected: {model_name} - {model_info['description']}")
        
    def set_input_enabled(self, enabled: bool):
        """Enable or disable input controls"""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.model_selector.setEnabled(enabled)
            
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        model_name = self.model_selector.currentData()
        
        # Disable input while processing
        self.set_input_enabled(False)
        self.status_label.setText("Status: Processing request...")
        self.status_label.setStyleSheet("color: orange;")
        
        # Display user message
        self.chat_display.append(f"\nYou: {text}")
        self.input_field.clear()
        
        # Create and start worker
        self.worker = Worker(text, model_name, self.model_config)
        self.worker.result_ready.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished.connect(self.on_request_finished)
        self.worker.start()
        
    def handle_response(self, response: str):
        """Handle successful response"""
        self.chat_display.append(f"\nAI: {response}")
        
    def handle_error(self, error: str):
        """Handle error response"""
        self.chat_display.append(f"\nError: {error}")
        self.status_label.setText("Status: Error occurred")
        self.status_label.setStyleSheet("color: red;")
        
    def on_request_finished(self):
        """Handle request completion"""
        self.set_input_enabled(True)
        if self.status_label.text().startswith("Status: Processing"):
            self.status_label.setText("Status: Ready")
            self.status_label.setStyleSheet("color: green;")
        
    def closeEvent(self, event):
        """Handle application closure"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = SimpleChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
