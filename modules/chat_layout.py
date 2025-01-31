from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QFrame,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QToolButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from .chat_ui import ChatDisplay
from .chat_sidebar import ChatSidebar
from .model_config import ModelConfig
from .worker import Worker
from .speech_module import SpeechHandler
import json
import os
from datetime import datetime
from typing import Dict, Optional


class ChatLayout(QWidget):
    def __init__(self, model_config: ModelConfig, parent=None):
        super().__init__(parent)
        self.model_config = model_config
        self.chat_displays = {}  # Store chat displays for each model
        self.current_model = None
        self.sidebar_visible = True
        self.speech_handler = SpeechHandler(self)
        self.current_worker: Optional[Worker] = None  # Track current worker
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = ChatSidebar(self.model_config)
        self.sidebar.model_selected.connect(self.switch_chat)
        self.sidebar.setFixedWidth(300)  # Fixed width for sidebar
        layout.addWidget(self.sidebar)

        # Chat area
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Chat header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f0f2f5;
                border-bottom: 1px solid #d1d7db;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)

        # Model info in header
        self.header_title = QLabel("Welcome to AI Chat")
        self.header_title.setStyleSheet("""
            color: #111b21;
            font-size: 16px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.header_title)

        # Header buttons
        header_buttons = QHBoxLayout()
        header_buttons.setSpacing(8)

        # TTS controls
        tts_controls = QHBoxLayout()
        tts_controls.setSpacing(4)

        # TTS toggle button
        self.tts_toggle = QToolButton()
        self.tts_toggle.setText("🔊")
        self.tts_toggle.setCheckable(True)
        self.tts_toggle.setToolTip("Toggle Text-to-Speech")
        self.tts_toggle.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 8px;
                border-radius: 20px;
                font-size: 16px;
            }
            QToolButton:hover {
                background-color: #e9edef;
            }
            QToolButton:checked {
                background-color: #128C7E;
                color: white;
            }
        """)
        self.tts_toggle.clicked.connect(self.toggle_tts)
        tts_controls.addWidget(self.tts_toggle)

        # Speaking indicator
        self.speaking_indicator = QLabel("")
        self.speaking_indicator.setStyleSheet("""
            QLabel {
                color: #8696a0;
                font-size: 13px;
                margin-left: 4px;
            }
        """)
        tts_controls.addWidget(self.speaking_indicator)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_speaking)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.stop_button.hide()
        tts_controls.addWidget(self.stop_button)

        header_buttons.addLayout(tts_controls)

        # More options button
        more_btn = QToolButton()
        more_btn.setText("⋮")  # Using dots instead of icon
        more_btn.setIconSize(QSize(24, 24))
        more_btn.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 8px;
                border-radius: 20px;
                font-size: 16px;
            }
            QToolButton:hover {
                background-color: #e9edef;
            }
        """)
        header_buttons.addWidget(more_btn)

        header_layout.addLayout(header_buttons)
        chat_layout.addWidget(header)

        # Stacked widget for different chats
        self.chat_stack = QStackedWidget()
        self.chat_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #efeae2;
            }
        """)

        # Welcome screen
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("👋 Welcome to AI Chat!")
        welcome_label.setStyleSheet("""
            QLabel {
                color: #111b21;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        welcome_layout.addWidget(welcome_label)

        instruction_label = QLabel("Select an AI model from the sidebar to start chatting")
        instruction_label.setStyleSheet("""
            QLabel {
                color: #667781;
                font-size: 16px;
            }
        """)
        welcome_layout.addWidget(instruction_label)

        self.chat_stack.addWidget(welcome_widget)
        chat_layout.addWidget(self.chat_stack)

        # Input area (hidden initially)
        self.input_frame = QFrame()
        self.input_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f2f5;
                border-top: 1px solid #d1d7db;
                padding: 5px;
            }
        """)
        self.input_frame.hide()

        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(16, 10, 16, 10)
        input_layout.setSpacing(8)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 8px;
                padding: 9px 12px;
                background-color: white;
                font-size: 15px;
                color: #111b21;
            }
            QLineEdit:focus {
                outline: none;
            }
            QLineEdit::placeholder {
                color: #8696a0;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        # Voice input button
        self.voice_input_btn = QToolButton()
        self.voice_input_btn.setText("🎙️")
        self.voice_input_btn.setToolTip("Hold to record voice input")
        self.voice_input_btn.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 8px;
                border-radius: 20px;
                font-size: 16px;
            }
            QToolButton:hover {
                background-color: #e9edef;
            }
            QToolButton:pressed {
                background-color: #128C7E;
                color: white;
            }
        """)
        self.voice_input_btn.pressed.connect(self.start_voice_input)
        self.voice_input_btn.released.connect(self.stop_voice_input)
        input_layout.addWidget(self.voice_input_btn)

        chat_layout.addWidget(self.input_frame)
        layout.addWidget(chat_container, stretch=1)

    def cleanup_worker(self):
        """Clean up the current worker thread"""
        if self.current_worker:
            try:
                self.current_worker.stop()  # Stop the worker
                self.current_worker.wait()  # Wait for it to finish
                self.current_worker.deleteLater()  # Schedule for deletion
                self.current_worker = None
            except Exception as e:
                print(f"Error cleaning up worker: {str(e)}")

    def send_message(self):
        """Handle sending a message"""
        if not self.current_model:
            return

        text = self.input_field.text().strip()
        if not text:
            return

        chat_display = self.chat_displays[self.current_model]
        self.input_field.clear()

        # Display user message
        chat_display.add_message(text, True)

        # Show typing indicator
        chat_display.show_typing_indicator()

        # Stop any existing worker
        self.cleanup_worker()

        # Start new worker thread
        self.current_worker = Worker(text, self.current_model, self.model_config)
        self.current_worker.result_ready.connect(self.handle_response)
        self.current_worker.error_occurred.connect(self.handle_error)
        self.current_worker.start()

    def handle_response(self, response: str):
        """Handle AI response"""
        if not self.current_model or self.current_model not in self.chat_displays:
            return

        chat_display = self.chat_displays[self.current_model]
        chat_display.hide_typing_indicator()
        chat_display.add_message(response, False)

        # If TTS is enabled, speak the response
        if self.tts_toggle.isChecked():
            self.speaking_indicator.setText("Speaking...")
            self.stop_button.setEnabled(True)
            self.speech_handler.text_to_speech(response, "pyttsx3 (System)", 
                callback=lambda: self.speaking_indicator.setText("TTS Ready"))

        # Cleanup worker after successful response
        self.cleanup_worker()

    def handle_error(self, error: str):
        """Handle error from worker thread"""
        if not self.current_model or self.current_model not in self.chat_displays:
            return

        chat_display = self.chat_displays[self.current_model]
        chat_display.hide_typing_indicator()
        chat_display.add_message(f"Error: {error}", False)
        
        # Cleanup worker after error
        self.cleanup_worker()

    def toggle_tts(self, enabled: bool):
        """Toggle text-to-speech functionality"""
        if enabled:
            # Check if TTS is available
            tts_methods = self.speech_handler.get_available_tts_methods()
            if not tts_methods:
                QMessageBox.warning(
                    self,
                    "TTS Not Available",
                    "Text-to-speech is not available. Please install required dependencies."
                )
                self.tts_toggle.setChecked(False)
                return

            self.speaking_indicator.setText("TTS Enabled")
            self.stop_button.show()
            # Test TTS with a short message using first available method
            self.speech_handler.text_to_speech(
                "Text-to-speech enabled", 
                tts_methods[0],
                callback=lambda: self.speaking_indicator.setText("TTS Ready")
            )
        else:
            self.speaking_indicator.setText("")
            self.stop_button.hide()
            self.speech_handler.stop_speaking()
        # Cleanup worker after successful response
        self.cleanup_worker()

    def handle_error(self, error: str):
        """Handle error from worker thread"""
        if not self.current_model or self.current_model not in self.chat_displays:
            return

        chat_display = self.chat_displays[self.current_model]
        chat_display.hide_typing_indicator()
        chat_display.add_message(f"Error: {error}", False)
        
        # Cleanup worker after error
        self.cleanup_worker()

    def toggle_tts(self, enabled: bool):
        """Toggle text-to-speech functionality"""
        if enabled:
            self.speaking_indicator.setText("TTS Enabled")
            self.stop_button.show()
            self.speech_handler.text_to_speech("Text-to-speech enabled", "pyttsx3 (System)")
        else:
            self.speaking_indicator.setText("")
            self.stop_button.hide()
            self.speech_handler.stop_speaking()

    def stop_speaking(self):
        """Stop current TTS playback"""
        self.speech_handler.stop_speaking()
        self.speaking_indicator.setText("")
        self.stop_button.setEnabled(False)

    def start_voice_input(self):
        """Start recording voice input"""
        self.voice_input_btn.setToolTip("Recording... Release to stop")
        self.speech_handler.start_listening(
            duration=5,
            callback=self.handle_voice_input
        )

    def stop_voice_input(self):
        """Stop recording voice input"""
        self.voice_input_btn.setToolTip("Hold to record voice input")

    def handle_voice_input(self, **kwargs):
        """Handle voice input results"""
        if 'error' in kwargs:
            QMessageBox.warning(self, "Voice Input Error", kwargs['error'])
        elif 'text' in kwargs:
            self.input_field.setText(kwargs['text'])
            self.send_message()

    def switch_chat(self, model_name: str):
        """Switch to the chat for the selected model"""
        try:
            # Cleanup current worker before switching
            self.cleanup_worker()

            if model_name not in self.chat_displays:
                # Create new chat display for this model
                chat_display = ChatDisplay(model_config=self.model_config)
                chat_display.set_current_model(model_name)
                self.chat_displays[model_name] = chat_display
                self.chat_stack.addWidget(chat_display)

            # Switch to the selected chat
            display = self.chat_displays[model_name]
            if display:
                self.chat_stack.setCurrentWidget(display)
                self.current_model = model_name
                self.header_title.setText(model_name)
                self.input_frame.show()
                self.input_field.setPlaceholderText(f"Message {model_name}")
                self.input_field.setFocus()
        except Exception as e:
            print(f"Error switching chat: {str(e)}")

    def new_chat(self):
        """Create a new chat session"""
        if self.current_model:
            # Cleanup current worker before creating new chat
            self.cleanup_worker()
            
            # Create new chat display for current model
            chat_display = ChatDisplay(model_config=self.model_config)
            chat_display.set_current_model(self.current_model)

            # Replace existing chat display
            old_display = self.chat_displays[self.current_model]
            self.chat_stack.removeWidget(old_display)
            old_display.deleteLater()

            self.chat_displays[self.current_model] = chat_display
            self.chat_stack.addWidget(chat_display)
            self.chat_stack.setCurrentWidget(chat_display)

    def save_chat(self):
        """Save current chat history"""
        if not self.current_model or self.current_model not in self.chat_displays:
            return

        chat_display = self.chat_displays[self.current_model]
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Chat History",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                chat_data = {
                    "model": self.current_model,
                    "name": chat_display.get_chat_name(),
                    "messages": chat_display.get_messages()
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, indent=2)

                QMessageBox.information(self, "Success", "Chat history saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save chat history: {str(e)}")

    def load_chat(self):
        """Load a saved chat history"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Chat History",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)

                model_name = chat_data.get("model")
                if not model_name:
                    raise ValueError("Invalid chat file: missing model name")

                # Cleanup current worker before loading chat
                self.cleanup_worker()

                # Create new chat display
                chat_display = ChatDisplay(model_config=self.model_config)
                chat_display.set_current_model(model_name)
                chat_display.set_chat_name(chat_data.get("name", "Loaded Chat"))

                # Load messages
                for msg in chat_data.get("messages", []):
                    timestamp = datetime.fromisoformat(msg["timestamp"])
                    chat_display.add_message(msg["text"], msg["is_user"])

                # Replace existing chat display if it exists
                if model_name in self.chat_displays:
                    old_display = self.chat_displays[model_name]
                    self.chat_stack.removeWidget(old_display)
                    old_display.deleteLater()

                self.chat_displays[model_name] = chat_display
                self.chat_stack.addWidget(chat_display)
                self.current_model = model_name
                self.chat_stack.setCurrentWidget(chat_display)
                self.input_frame.show()
                self.header_title.setText(model_name)

                QMessageBox.information(self, "Success", "Chat history loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load chat history: {str(e)}")

    def export_chat(self, format="txt"):
        """Export current chat"""
        if not self.current_model or self.current_model not in self.chat_displays:
            return

        chat_display = self.chat_displays[self.current_model]
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chat",
            "",
            "Text Files (*.txt);;JSON Files (*.json)"
        )

        if file_path:
            try:
                # Determine format from file extension
                format = "json" if file_path.lower().endswith(".json") else "txt"

                # Get exported content
                content = chat_display.export_chat(format)

                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                QMessageBox.information(self, "Success", "Chat exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export chat: {str(e)}")

    def clear_chat(self):
        """Clear current chat"""
        if self.current_model and self.current_model in self.chat_displays:
            # Cleanup current worker before clearing chat
            self.cleanup_worker()
            
            chat_display = self.chat_displays[self.current_model]
            chat_display.clear_messages()
            chat_display.add_message(f"👋 Welcome! I'm {self.current_model}, your AI assistant.", False)
            chat_display.add_message("How can I help you today?", False)

    def rename_chat(self, new_name: str):
        """Rename current chat"""
        if self.current_model and self.current_model in self.chat_displays:
            chat_display = self.chat_displays[self.current_model]
            chat_display.set_chat_name(new_name)
            self.header_title.setText(new_name)

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar.setVisible(self.sidebar_visible)

    def closeEvent(self, event):
        """Handle widget closure"""
        self.cleanup_worker()  # Ensure worker is cleaned up
        super().closeEvent(event)
