def show_model_details(self):
    """Show the model details dialog"""
    # Check if the current model is set
    if self.current_model:
        # Create the model details dialog
        dialog = ModelDetailsDialog(self.current_model, self.model_config, self)
        # Execute the dialog
        dialog.exec()
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QScrollArea, QFrame, QToolButton, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QColor
from datetime import datetime
from .model_config import ModelConfig
from .worker import Worker
from .ollama_client import OllamaClient
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QPainter, QPainterPath
from datetime import datetime
import json
from .worker import Worker
from .speech_module import SpeechHandler
from .model_config import ModelConfig

class MessageBubble(QFrame):
    def __init__(self, text: str, timestamp: datetime, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp
        self.compact_mode = False

        # Setup layout
        self.main_layout = QHBoxLayout(self)
        self.updateMargins()

        # Create message content
        message_frame = QFrame()
        message_frame.setObjectName("userBubble" if is_user else "aiBubble")
        self.updateBubbleStyle(message_frame)

        message_layout = QVBoxLayout(message_frame)
        message_layout.setSpacing(2)

        # Message text with emoji support
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextFormat(Qt.TextFormat.RichText)  # Enable rich text for emoji
        text_label.setOpenExternalLinks(True)  # Make links clickable
        message_layout.addWidget(text_label)

        # Timestamp with tick marks (WhatsApp style)
        time_text = timestamp.strftime("%I:%M %p")
        if is_user:
            time_text += " ✓✓"  # Double tick for sent messages
        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            color: #8696a0;
            font-size: 11px;
            margin-top: 2px;
        """)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        message_layout.addWidget(time_label)

        # Add message frame to main layout with proper alignment
        if is_user:
            self.main_layout.addStretch()
            self.main_layout.addWidget(message_frame)
        else:
            self.main_layout.addWidget(message_frame)
            self.main_layout.addStretch()

    def updateMargins(self):
        """Update margins based on compact mode"""
        if self.main_layout:
            if self.compact_mode:
                self.main_layout.setContentsMargins(5, 2, 5, 2)
            else:
                self.main_layout.setContentsMargins(10, 5, 10, 5)

    def updateBubbleStyle(self, frame):
        """Update bubble style based on compact mode - WhatsApp style"""
        padding = "8px 12px" if not self.compact_mode else "6px 10px"
        if self.is_user:
            frame.setStyleSheet(f"""
                #userBubble {{
                    background-color: #d9fdd3;  /* WhatsApp green tint */
                    border-radius: 12px;
                    padding: {padding};
                    margin: 2px;
                }}
                #userBubble QLabel {{
                    color: #111b21;  /* WhatsApp dark text */
                    font-size: {13 if not self.compact_mode else 12}px;
                }}
            """)
        else:
            frame.setStyleSheet(f"""
                #aiBubble {{
                    background-color: #ffffff;  /* WhatsApp white */
                    border-radius: 12px;
                    padding: {padding};
                    margin: 2px;
                }}
                #aiBubble QLabel {{
                    color: #111b21;  /* WhatsApp dark text */
                    font-size: {13 if not self.compact_mode else 12}px;
                }}
            """)

    def setCompactMode(self, compact: bool):
        """Toggle compact mode"""
        if self.compact_mode != compact:
            self.compact_mode = compact
            self.updateMargins()
            for child in self.findChildren(QFrame):
                if child.objectName() in ["userBubble", "aiBubble"]:
                    self.updateBubbleStyle(child)

    def to_dict(self):
        """Convert message to dictionary for serialization"""
        return {
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "is_user": self.is_user
        }


class TypingIndicator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("typingIndicator")
        self.compact_mode = False
        self.updateStyle()

        self.main_layout = QHBoxLayout(self)
        self.updateMargins()

        # WhatsApp-style typing indicator
        self.dots = []
        for _ in range(3):
            dot = QLabel("•")
            dot.setStyleSheet("""
                color: #8696a0;
                font-size: 24px;
                margin: 0px 2px;
            """)
            self.main_layout.addWidget(dot)
            self.dots.append(dot)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_dots)
        self.animation_step = 0

        self.main_layout.addStretch()
        self.hide()

    def updateStyle(self):
        """Update indicator style - WhatsApp style"""
        padding = "6px 10px" if self.compact_mode else "8px 12px"
        self.setStyleSheet(f"""
            #typingIndicator {{
                background-color: #ffffff;
                border-radius: 12px;
                padding: {padding};
                margin: 2px;
                max-width: 100px;
            }}
        """)

    def updateMargins(self):
        """Update margins based on compact mode"""
        if self.main_layout:
            self.main_layout.setContentsMargins(
                6 if self.compact_mode else 8,
                3 if self.compact_mode else 4,
                6 if self.compact_mode else 8,
                3 if self.compact_mode else 4
            )

    def animate_dots(self):
        """WhatsApp-style typing animation"""
        opacities = ["0.3", "0.6", "1.0"]
        for i, dot in enumerate(self.dots):
            opacity = opacities[(self.animation_step + i) % 3]
            dot.setStyleSheet(f"""
                color: #8696a0;
                font-size: {20 if self.compact_mode else 24}px;
                margin: 0px 2px;
                opacity: {opacity};
            """)
        self.animation_step = (self.animation_step + 1) % 3

    def setCompactMode(self, compact: bool):
        """Toggle compact mode"""
        if self.compact_mode != compact:
            self.compact_mode = compact
            self.updateStyle()
            self.updateMargins()
            # Update dot sizes
            self.animate_dots()  # This will update the dot styles with new sizes

    def start_animation(self):
        self.show()
        self.timer.start(500)  # Slower animation like WhatsApp

    def stop_animation(self):
        self.timer.stop()
        self.hide()


class SpeechIndicator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("speechIndicator")
        self.compact_mode = False
        self.updateStyle()

        self.main_layout = QHBoxLayout(self)
        self.updateMargins()

        # Speech indicator icon and text
        self.icon_label = QLabel("🎙️")
        self.text_label = QLabel("Listening...")
        
        self.icon_label.setStyleSheet("""
            font-size: 16px;
            margin-right: 4px;
        """)
        
        self.text_label.setStyleSheet("""
            color: #8696a0;
            font-size: 13px;
        """)

        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)
        self.main_layout.addStretch()
        self.hide()

    def updateStyle(self):
        """Update indicator style"""
        padding = "6px 10px" if self.compact_mode else "8px 12px"
        self.setStyleSheet(f"""
            #speechIndicator {{
                background-color: #ffffff;
                border-radius: 12px;
                padding: {padding};
                margin: 2px;
                max-width: 150px;
            }}
        """)

    def updateMargins(self):
        """Update margins based on compact mode"""
        if self.main_layout:
            self.main_layout.setContentsMargins(
                6 if self.compact_mode else 8,
                3 if self.compact_mode else 4,
                6 if self.compact_mode else 8,
                3 if self.compact_mode else 4
            )

    def setCompactMode(self, compact: bool):
        """Toggle compact mode"""
        if self.compact_mode != compact:
            self.compact_mode = compact
            self.updateStyle()
            self.updateMargins()

    def start_listening(self):
        """Show listening indicator"""
        self.text_label.setText("Listening...")
        self.show()

    def start_processing(self):
        """Show processing indicator"""
        self.text_label.setText("Processing speech...")
        self.show()

    def stop(self):
        """Hide the indicator"""
        self.hide()


class ChatDisplay(QScrollArea):
    COMPACT_WIDTH_THRESHOLD = 600
    status_changed = pyqtSignal(str)  # Signal for status updates

    def __init__(self, model_config: ModelConfig, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.compact_mode = False
        self.chat_name = "New Chat"
        
        # Initialize model config and worker
        self.model_config = model_config
        # Initialize model info button
        self.model_info_button = QPushButton("Model Info")
        self.model_info_button.setStyleSheet("""
            QPushButton {
                background-color: #00a884;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #008f6f;
            }
        """)
        self.model_info_button.clicked.connect(self.show_model_details)
        self.model_info_button.hide()  # Hidden by default
        
        # Sync models with Ollama
        try:
            self.model_config.sync_models()
        except Exception as e:
            print(f"Error syncing models: {e}")
        
        self.current_model = None
        self.worker = None
        self.current_status = "offline"

        # Main widget and layout
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #efeae2;  /* WhatsApp chat background color */
            }
        """)
        
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        # Add model info button to the top
        model_info_layout = QHBoxLayout()
        model_info_layout.addStretch()
        model_info_layout.addWidget(self.model_info_button)
        self.content_layout.addLayout(model_info_layout)

        # Status label (WhatsApp style)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #8696a0;
                font-size: 13px;
                margin-bottom: 8px;
            }
        """)
        self.content_layout.addWidget(self.status_label)
        self.update_status("offline")  # Initial status

        self.content_layout.addStretch()

        # Typing indicator
        self.typing_indicator = TypingIndicator()
        self.content_layout.addWidget(self.typing_indicator)

        # Speech indicator
        self.speech_indicator = SpeechIndicator()
        self.content_layout.addWidget(self.speech_indicator)

        self.setWidget(self.content_widget)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #efeae2;
            }
            QScrollBar:vertical {
                border: none;
                background: #00000000;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #bfbfbf;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def add_message(self, text: str, is_user: bool = False):
        """Add a message to the chat"""
        # Remove stretch if it exists
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.spacerItem():
                self.content_layout.removeItem(item)
                break

        # Add new message
        message = MessageBubble(text, datetime.now(), is_user)
        message.setCompactMode(self.compact_mode)
        self.content_layout.addWidget(message)

        # Add stretch back
        self.content_layout.addStretch()

        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def update_status(self, status: str):
        """Update the AI's status display"""
        self.current_status = status
        status_text = ""
        status_color = "#8696a0"  # Default gray

        if status == "online":
            status_text = "online"
            status_color = "#00a884"  # WhatsApp green
        elif status == "offline":
            status_text = "offline"
        elif status == "typing":
            status_text = "typing..."
            status_color = "#00a884"  # WhatsApp green
        elif status == "listening":
            status_text = "listening..."
            status_color = "#00a884"  # WhatsApp green
        elif status == "processing":
            status_text = "processing speech..."
            status_color = "#00a884"  # WhatsApp green

        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                font-size: 13px;
                margin-bottom: 8px;
            }}
        """)
        self.status_label.setText(status_text)
        self.status_changed.emit(status)

    def show_speech_indicator(self, state="listening"):
        """Show the speech indicator"""
        if state == "listening":
            self.speech_indicator.start_listening()
            self.update_status("listening")
        elif state == "processing":
            self.speech_indicator.start_processing()
            self.update_status("processing")
        self.scroll_to_bottom()

    def hide_speech_indicator(self):
        """Hide the speech indicator"""
        self.speech_indicator.stop()
        if self.current_status in ["listening", "processing"]:
            self.update_status("online")

    def set_current_model(self, model_name: str):
        """Set the current AI model"""
        self.current_model = model_name
        
        # Try to sync with Ollama first
        try:
            if self.model_config.check_ollama_available():
                self.model_config.sync_models()
            
            model_info = self.model_config.get_model_info(model_name)
            if model_info and isinstance(model_info, dict):  # Ensure model_info is a dictionary
                self.update_status("online")
                welcome_msg = [
                    f"👋 Welcome! I'm {model_name}, your AI assistant.",
                    model_info.get('description', 'No description available.')
                ]
                
                # Add Ollama metadata if available
                metadata = model_info.get('ollama_metadata', {})
                if metadata and isinstance(metadata, dict):
                    if metadata.get('system_prompt'):
                        welcome_msg.append("\nSystem Prompt:")
                        welcome_msg.append(metadata['system_prompt'])
                
                self.add_message("\n".join(welcome_msg), is_user=False)
                self.model_info_button.show()
            else:
                self.update_status("offline")
                self.model_info_button.hide()
                self.add_message(f"Error: Could not load information for model {model_name}", is_user=False)
        except Exception as e:
            print(f"Error setting current model: {e}")
            self.update_status("offline")
            self.model_info_button.hide()
            self.add_message(f"Error: Failed to initialize model {model_name}: {str(e)}", is_user=False)

    def show_model_details(self):
        """Show detailed information about the current model"""
        if not self.current_model:
            return
            
        try:
            model_info = self.model_config.get_model_info(self.current_model)
            if not model_info:
                QMessageBox.warning(
                    self,
                    "Model Information",
                    f"No information available for model {self.current_model}"
                )
                return
                
            # Create a formatted message with model details
            details = [f"Model: {self.current_model}"]
            
            # Add description if available
            if 'description' in model_info:
                details.append(f"\nDescription:\n{model_info['description']}")
            
            # Add Ollama metadata if available
            metadata = model_info.get('ollama_metadata', {})
            if metadata and isinstance(metadata, dict):
                details.append("\nModel Details:")
                if 'parameter_size' in metadata:
                    details.append(f"Parameter Size: {metadata['parameter_size']}")
                if 'architecture' in metadata:
                    details.append(f"Architecture: {metadata['architecture']}")
                if 'license' in metadata:
                    details.append(f"License: {metadata['license']}")
                if 'system_prompt' in metadata:
                    details.append(f"\nSystem Prompt:\n{metadata['system_prompt']}")
            
            # Show the information in a message box
            QMessageBox.information(
                self,
                f"{self.current_model} Information",
                "\n".join(details)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to fetch model information: {str(e)}"
            )

    def send_message(self, text: str):
        """Send a message and handle the response in a thread-safe way"""
        if not text.strip() or not self.current_model:
            return

        try:
            # Add user message to chat
            self.add_message(text, is_user=True)
            
            # Show typing indicator and update status
            self.show_typing_indicator()
            self.update_status("typing")
            
            # Attempt to use CLI first
            cli_response = self.ollama_client.run_cli(self.current_model, text)
            if cli_response:
                self.add_message(cli_response, is_user=False)
                self.hide_typing_indicator()
                self.update_status("online")
                return
            
            # If CLI fails, use the worker for API interaction
            self.worker = Worker(text, self.current_model, self.model_config)
            
            # Connect signals
            self.worker.result_ready.connect(self.handle_response)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.finished.connect(self.cleanup_worker)
            
            # Start worker thread
            self.worker.start()
            
        except Exception as e:
            self.hide_typing_indicator()
            self.update_status("online")
            self.add_message(f"Error sending message: {str(e)}", is_user=False)

    def handle_response(self, response: str):
        """Handle the response from the worker thread"""
        self.hide_typing_indicator()
        self.update_status("online")
        self.add_message(response, is_user=False)
        
    def handle_error(self, error_message: str):
        """Handle any errors from the worker thread"""
        self.hide_typing_indicator()
        self.update_status("offline")
        self.add_message(f"Error: {error_message}", is_user=False)
        
    def cleanup_worker(self):
        """Clean up the worker thread"""
        if self.worker:
            self.worker.stop()
            self.worker.deleteLater()
            self.worker = None
            if self.current_status == "typing":
                self.update_status("online")

    def show_typing_indicator(self):
        """Show the typing indicator"""
        self.typing_indicator.setCompactMode(self.compact_mode)
        self.typing_indicator.start_animation()
        self.scroll_to_bottom()

    def hide_typing_indicator(self):
        """Hide the typing indicator"""
        self.typing_indicator.stop_animation()

    def clear_messages(self):
        """Clear all messages from the chat"""
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget and not isinstance(widget, (TypingIndicator, SpeechIndicator, QLabel)):
                    widget.deleteLater()
                elif item.spacerItem():
                    self.content_layout.removeItem(item)

        # Add back the stretch
        self.content_layout.addStretch()

    def get_messages(self):
        """Get all messages as a list of dictionaries"""
        messages = []
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, MessageBubble):
                    messages.append(widget.to_dict())
        return messages

    def set_chat_name(self, name: str):
        """Set the chat name"""
        self.chat_name = name

    def get_chat_name(self) -> str:
        """Get the chat name"""
        return self.chat_name

    def export_chat(self, format: str = "txt") -> str:
        """Export chat in the specified format"""
        messages = self.get_messages()

        if format == "json":
            chat_data = {
                "name": self.chat_name,
                "messages": messages
            }
            return json.dumps(chat_data, indent=2)
        else:  # txt format
            lines = [f"Chat: {self.chat_name}\n"]
            for msg in messages:
                sender = "You" if msg["is_user"] else "AI"
                timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %I:%M %p")
                lines.append(f"[{timestamp}] {sender}: {msg['text']}\n")
            return "".join(lines)

    def closeEvent(self, event):
        """Handle closure of the chat display"""
        self.update_status("offline")
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        super().closeEvent(event)
