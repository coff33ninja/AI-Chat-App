from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QFrame,
)
from datetime import datetime
import logging
from .model_config import ModelConfig


class TabManager(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("main.tab_manager")
        self.logger.info("Initializing TabManager")
        
        self.parent = parent
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.model_config = ModelConfig()
        self.initialize_model_tabs()

    def initialize_model_tabs(self):
        """Create initial tabs for each installed model"""
        self.logger.info("Initializing model tabs")
        available_models = self.model_config.list_available_models()
        for model in available_models:
            self.create_model_tab(model)
        self.logger.info(f"Created {len(available_models)} model tabs")

    def create_model_tab(self, model_name):
        """Create a new tab for a specific model"""
        self.logger.info(f"Creating new tab for model: {model_name}")
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Chat display
        output_display = QTextEdit()
        output_display.setReadOnly(True)
        layout.addWidget(output_display)

        # Input section
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        input_layout = QHBoxLayout(input_frame)

        input_field = QLineEdit()
        input_field.setPlaceholderText(f"Type your message for {model_name} here...")
        input_layout.addWidget(input_field)

        # Buttons
        button_layout = QHBoxLayout()
        submit_button = QPushButton("Send")
        clear_button = QPushButton("Clear")
        
        button_layout.addWidget(submit_button)
        button_layout.addWidget(clear_button)
        input_layout.addLayout(button_layout)
        
        layout.addWidget(input_frame)

        # Store references to widgets
        tab.output_display = output_display
        tab.input_field = input_field
        tab.submit_button = submit_button
        tab.clear_button = clear_button

        # Connect signals
        submit_button.clicked.connect(lambda: self.handle_query(tab))
        clear_button.clicked.connect(output_display.clear)
        input_field.returnPressed.connect(lambda: self.handle_query(tab))

        # Add welcome message
        output_display.append(f"Welcome to {model_name} chat!")
        output_display.append("Type your message and press Enter or click Send.")
        output_display.append("-" * 50)

        # Add tab
        self.addTab(tab, model_name)
        self.logger.debug(f"Tab created successfully for model: {model_name}")
        return tab

    def handle_query(self, tab):
        """Handle query from the current tab"""
        query = tab.input_field.text().strip()
        if not query:
            self.logger.debug("Empty query received, ignoring")
            return

        # Clear input field
        tab.input_field.clear()

        # Get model name from tab text
        model_name = self.tabText(self.indexOf(tab))
        self.logger.info(f"Processing query for model {model_name}: {query[:50]}...")

        # Display query
        tab.output_display.append(f"\nYou: {query}")

        # Start worker thread
        from main import Worker  # Import here to avoid circular import
        worker = Worker(query, model_name, self.model_config)
        worker.result_ready.connect(lambda response: self.handle_response(tab, response))
        worker.start()
        self.logger.debug(f"Started worker thread for model {model_name}")

        # Store worker reference to prevent garbage collection
        tab.current_worker = worker

    def handle_response(self, tab, response: str):
        """Handle AI response in the current tab"""
        model_name = self.tabText(self.indexOf(tab))
        self.logger.info(f"Received response from model {model_name}: {response[:50]}...")
        
        tab.output_display.append(f"\nAI: {response}")

        # Handle TTS if enabled
        if hasattr(self.parent, "tts_enabled") and self.parent.tts_enabled:
            if not self.parent.speech_handler.is_speaking:
                self.logger.debug("Initiating text-to-speech for response")
                self.parent.speaking_indicator.setText("🔊 AI is speaking...")
                self.parent.stop_button.setEnabled(True)

                def tts_callback(error=None):
                    self.parent.speaking_indicator.setText("")
                    self.parent.stop_button.setEnabled(False)
                    if error:
                        self.logger.error(f"TTS error: {error}")
                        tab.output_display.append(f"TTS Error: {error}")

                self.parent.speech_handler.text_to_speech(
                    response, 
                    self.parent.tts_dropdown.currentText(), 
                    callback=tts_callback
                )
            else:
                self.logger.debug("Adding response to speech queue")
                self.parent.speech_handler.speech_queue.append(response)

    def close_tab(self, index):
        """Close the specified tab"""
        tab = self.widget(index)
        model_name = self.tabText(index)
        self.logger.info(f"Closing tab for model: {model_name}")
        
        # Stop any running worker
        if hasattr(tab, 'current_worker') and tab.current_worker:
            self.logger.debug(f"Stopping worker thread for model: {model_name}")
            tab.current_worker.quit()
            tab.current_worker.wait()
        
        self.removeTab(index)

        # Don't allow closing the last tab
        if self.count() == 0:
            model_name = self.model_config.list_available_models()[0]
            self.logger.info(f"Creating default tab for model: {model_name}")
            self.create_model_tab(model_name)

    def get_current_tab(self):
        """Get the currently active tab"""
        current_tab = self.currentWidget()
        if current_tab:
            model_name = self.tabText(self.currentIndex())
            self.logger.debug(f"Current active tab: {model_name}")
        return current_tab

    def save_all_sessions(self):
        """Save chat history from all tabs"""
        self.logger.info("Saving all chat sessions")
        for i in range(self.count()):
            tab = self.widget(i)
            model_name = self.tabText(i)
            chat_text = tab.output_display.toPlainText()
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{model_name}_{timestamp}.txt"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(chat_text)
                self.logger.info(f"Saved chat session for model {model_name} to {filename}")
            except Exception as e:
                self.logger.error(f"Error saving chat session for model {model_name}: {str(e)}")
