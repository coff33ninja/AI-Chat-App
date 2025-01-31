from typing import Optional, Union, Any, Protocol, TypeVar, cast, Callable
from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFrame,
    QLabel,
    QComboBox,
)
from PyQt6.QtCore import QObject
from datetime import datetime
import logging
from .model_config import ModelConfig
from .chat_history import ChatHistory
from .chat_ui import ChatDisplay, MessageBubble
from .worker import Worker  # Updated import from new worker module


TTSCallback = Callable[[Optional[str]], None]


class SpeechHandlerProtocol(Protocol):
    """Protocol for speech handler interface"""
    @property
    def is_speaking(self) -> bool:
        ...
    
    @property
    def speech_queue(self) -> list[str]:
        ...
    
    def text_to_speech(self, text: str, voice: str, callback: TTSCallback) -> None:
        ...


class MainWindow(QWidget):
    """Type hint for main window to access TTS attributes"""
    tts_enabled: bool
    speech_handler: SpeechHandlerProtocol
    speaking_indicator: QLabel
    stop_button: QPushButton
    tts_dropdown: QComboBox


class ChatTab(QWidget):
    """Custom tab class to store chat-specific attributes"""
    def __init__(self, model_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.model_name: str = model_name
        self.chat_display: Optional[ChatDisplay] = None
        self.input_field: Optional[QLineEdit] = None
        self.submit_button: Optional[QPushButton] = None
        self.clear_button: Optional[QPushButton] = None
        self.current_worker: Optional[Worker] = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the UI components for this tab"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Chat display
        self.chat_display = ChatDisplay(self)
        layout.addWidget(self.chat_display)

        # Input section
        input_frame = QFrame(self)
        input_frame.setFrameStyle(QFrame.Shape.NoFrame)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border-top: 1px solid #CCCCCC;
                padding: 10px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 5, 10, 5)

        # Input field
        self.input_field = QLineEdit(input_frame)
        self.input_field.setPlaceholderText(f"Type your message for {self.model_name} here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 20px;
                padding: 8px 16px;
                background-color: white;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #128C7E;
            }
        """)
        input_layout.addWidget(self.input_field)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.submit_button = QPushButton("Send", input_frame)
        self.clear_button = QPushButton("Clear", input_frame)
        
        button_style = """
            QPushButton {
                background-color: #128C7E;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 16px;
                min-width: 70px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #075E54;
            }
            QPushButton:pressed {
                background-color: #0E7165;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """
        
        self.submit_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)
        
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.clear_button)
        input_layout.addLayout(button_layout)
        
        layout.addWidget(input_frame)


class TabManager(QTabWidget):
    def __init__(self, parent: Optional[MainWindow] = None):
        super().__init__(parent)
        self._parent: Optional[MainWindow] = parent
        self.logger = logging.getLogger("main.tab_manager")
        self.logger.info("Initializing TabManager")
        
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.model_config = ModelConfig()
        self.chat_history = ChatHistory()
        
        # Set tab bar styling
        self.setStyleSheet("""
            QTabBar::tab {
                background: #F0F0F0;
                border: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #128C7E;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #E0E0E0;
            }
        """)
        
        self.initialize_model_tabs()

    def initialize_model_tabs(self) -> None:
        """Create initial tabs for each installed model"""
        self.logger.info("Initializing model tabs")
        available_models = self.model_config.list_available_models()
        for model in available_models:
            self.create_model_tab(model)
        self.logger.info(f"Created {len(available_models)} model tabs")

    def create_model_tab(self, model_name: str) -> ChatTab:
        """Create a new tab for a specific model"""
        self.logger.info(f"Creating new tab for model: {model_name}")
        
        # Create new tab with custom class
        tab = ChatTab(model_name, self)
        
        if tab.submit_button and tab.clear_button and tab.input_field and tab.chat_display:
            # Connect signals
            tab.submit_button.clicked.connect(lambda: self.handle_query(tab))
            tab.clear_button.clicked.connect(lambda: self.clear_chat(tab))
            tab.input_field.returnPressed.connect(lambda: self.handle_query(tab))

            # Add welcome messages
            tab.chat_display.add_message(f"Welcome to {model_name} chat!", False)
            tab.chat_display.add_message("Type your message and press Enter or click Send.", False)

        # Add tab
        self.addTab(tab, model_name)
        self.logger.debug(f"Tab created successfully for model: {model_name}")
        return tab

    def handle_query(self, tab: ChatTab) -> None:
        """Handle query from the current tab"""
        if not tab.input_field or not tab.chat_display:
            return

        query = tab.input_field.text().strip()
        if not query:
            self.logger.debug("Empty query received, ignoring")
            return

        # Clear input field
        tab.input_field.clear()

        # Display user message
        tab.chat_display.add_message(query, True)
        
        # Show typing indicator
        tab.chat_display.show_typing_indicator()

        # Start worker thread
        worker = Worker(query, tab.model_name, self.model_config)
        worker.result_ready.connect(lambda response: self.handle_response(tab, response))
        worker.start()
        self.logger.debug(f"Started worker thread for model {tab.model_name}")

        # Store worker reference
        tab.current_worker = worker

    def handle_response(self, tab: ChatTab, response: str) -> None:
        """Handle AI response in the current tab"""
        if not tab.chat_display:
            return

        self.logger.info(f"Received response from model {tab.model_name}: {response[:50]}...")
        
        # Hide typing indicator
        tab.chat_display.hide_typing_indicator()
        
        # Display AI response
        tab.chat_display.add_message(response, False)

        # Handle TTS if enabled
        if (isinstance(self._parent, MainWindow) and 
            hasattr(self._parent, "tts_enabled") and 
            self._parent.tts_enabled):
            
            if not self._parent.speech_handler.is_speaking:
                self.logger.debug("Initiating text-to-speech for response")
                self._parent.speaking_indicator.setText("🔊 AI is speaking...")
                self._parent.stop_button.setEnabled(True)

                def tts_callback(error: Optional[str] = None) -> None:
                    if isinstance(self._parent, MainWindow):
                        self._parent.speaking_indicator.setText("")
                        self._parent.stop_button.setEnabled(False)
                        if error and tab.chat_display:
                            self.logger.error(f"TTS error: {error}")
                            tab.chat_display.add_message(f"TTS Error: {error}", False)

                self._parent.speech_handler.text_to_speech(
                    response, 
                    self._parent.tts_dropdown.currentText(),
                    tts_callback
                )
            else:
                self.logger.debug("Adding response to speech queue")
                self._parent.speech_handler.speech_queue.append(response)

    def clear_chat(self, tab: ChatTab) -> None:
        """Clear the chat display"""
        if not tab.chat_display or not hasattr(tab.chat_display, "content_layout"):
            return

        if hasattr(tab.chat_display, "typing_indicator"):
            tab.chat_display.content_layout.removeWidget(tab.chat_display.typing_indicator)
        
        while tab.chat_display.content_layout.count():
            item = tab.chat_display.content_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QWidget):
                    widget.deleteLater()
        
        tab.chat_display.content_layout.addStretch()
        if hasattr(tab.chat_display, "typing_indicator"):
            tab.chat_display.content_layout.addWidget(tab.chat_display.typing_indicator)
        
        self.logger.info("Cleared chat display")

    def close_tab(self, index: int) -> None:
        """Close the specified tab"""
        tab = self.widget(index)
        if not isinstance(tab, ChatTab):
            return
            
        self.logger.info(f"Closing tab for model: {tab.model_name}")
        
        # Stop any running worker
        if tab.current_worker:
            self.logger.debug(f"Stopping worker thread for model: {tab.model_name}")
            tab.current_worker.quit()
            tab.current_worker.wait()
        
        self.removeTab(index)

        # Don't allow closing the last tab
        if self.count() == 0:
            model_name = self.model_config.list_available_models()[0]
            self.logger.info(f"Creating default tab for model: {model_name}")
            self.create_model_tab(model_name)

    def get_current_tab(self) -> Optional[ChatTab]:
        """Get the currently active tab"""
        current_tab = self.currentWidget()
        if isinstance(current_tab, ChatTab):
            self.logger.debug(f"Current active tab: {current_tab.model_name}")
            return current_tab
        return None

    def save_all_sessions(self) -> None:
        """Save chat history from all tabs"""
        self.logger.info("Saving all chat sessions")
        for i in range(self.count()):
            tab = self.widget(i)
            if not isinstance(tab, ChatTab) or not tab.chat_display:
                continue
                
            try:
                # Get messages from chat display
                messages = []
                for j in range(tab.chat_display.content_layout.count()):
                    item = tab.chat_display.content_layout.itemAt(j)
                    widget = item.widget() if item else None
                    if isinstance(widget, MessageBubble):
                        messages.append({
                            "role": "user" if widget.is_user else "assistant",
                            "content": widget.text
                        })
                
                if messages:
                    # Save to chat history
                    session_name = f"{tab.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self.chat_history.current_session = messages
                    if self.chat_history.save_session(session_name):
                        self.logger.info(f"Saved chat session to chat history: {session_name}")
            except Exception as e:
                self.logger.error(f"Error saving chat session for model {tab.model_name}: {str(e)}")
