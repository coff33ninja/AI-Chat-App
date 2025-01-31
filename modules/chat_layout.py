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
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from .chat_ui import ChatDisplay
from .chat_sidebar import ChatSidebar
from .model_config import ModelConfig
from .worker import Worker
import json
import os
from datetime import datetime


class ChatLayout(QWidget):
    def __init__(self, model_config: ModelConfig, parent=None):
        super().__init__(parent)
        self.model_config = model_config
        self.chat_displays = {}  # Store chat displays for each model
        self.current_model = None
        self.sidebar_visible = True
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

        # Stacked widget for different chats
        self.chat_stack = QStackedWidget()
        self.chat_stack.setStyleSheet("background-color: #E5DDD5;")

        # Welcome screen
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("👋 Welcome to AI Chat!")
        welcome_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        welcome_layout.addWidget(welcome_label)

        instruction_label = QLabel("Select an AI model from the sidebar to start chatting")
        instruction_label.setStyleSheet("""
            QLabel {
                color: #666666;
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
                background-color: #F0F0F0;
                border-top: 1px solid #CCCCCC;
            }
        """)
        self.input_frame.hide()

        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
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
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #128C7E;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #075E54;
            }
            QPushButton:pressed {
                background-color: #0E7165;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addWidget(self.input_frame)
        layout.addWidget(chat_container, stretch=1)

    def switch_chat(self, model_name: str):
        """Switch to the chat for the selected model"""
        if model_name not in self.chat_displays:
            # Create new chat display for this model
            chat_display = ChatDisplay()
            chat_display.add_message(f"Welcome to {model_name} chat!", False)
            chat_display.add_message("Type your message and press Enter or click Send.", False)
            self.chat_displays[model_name] = chat_display
            self.chat_stack.addWidget(chat_display)

        # Switch to the selected chat
        self.chat_stack.setCurrentWidget(self.chat_displays[model_name])
        self.current_model = model_name
        self.input_frame.show()
        self.input_field.setPlaceholderText(f"Type your message for {model_name} here...")

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

        # Start worker thread
        worker = Worker(text, self.current_model, self.model_config)
        worker.result_ready.connect(lambda response: self.handle_response(response))
        worker.start()

    def handle_response(self, response: str):
        """Handle AI response"""
        if not self.current_model or self.current_model not in self.chat_displays:
            return

        chat_display = self.chat_displays[self.current_model]
        chat_display.hide_typing_indicator()
        chat_display.add_message(response, False)

    def new_chat(self):
        """Create a new chat session"""
        if self.current_model:
            # Create new chat display for current model
            chat_display = ChatDisplay()
            chat_display.add_message(f"Welcome to {self.current_model} chat!", False)
            chat_display.add_message("Type your message and press Enter or click Send.", False)

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

                # Create new chat display
                chat_display = ChatDisplay()
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
            chat_display = self.chat_displays[self.current_model]
            chat_display.clear_messages()
            chat_display.add_message(f"Welcome to {self.current_model} chat!", False)
            chat_display.add_message("Type your message and press Enter or click Send.", False)

    def rename_chat(self, new_name: str):
        """Rename current chat"""
        if self.current_model and self.current_model in self.chat_displays:
            chat_display = self.chat_displays[self.current_model]
            chat_display.set_chat_name(new_name)

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar.setVisible(self.sidebar_visible)
