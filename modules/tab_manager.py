from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
)
from PyQt6.QtCore import (
    pyqtSignal,
    Qt,
    QThread,
)
from .chat_history import ChatHistory
import logging
import subprocess
import re
from typing import Optional

logger = logging.getLogger("ui.tabs")


class Worker(QThread):
    """Worker thread for running AI models"""

    result_ready = pyqtSignal(str)

    def __init__(self, query: str, model_name: str):
        super().__init__()
        self.query = query
        self.model_name = model_name

    def run(self):
        """Run the AI model query"""
        try:
            # Check if ollama is available
            try:
                subprocess.run(["ollama", "list"], capture_output=True, text=True)
            except FileNotFoundError:
                self.result_ready.emit("Error: Ollama is not installed or not in PATH")
                return

            # Run the query
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=self.query,
                text=True,
                capture_output=True,
                encoding="utf-8",
            )

            if result.returncode != 0:
                self.result_ready.emit(f"Error: {result.stderr}")
                return

            response = result.stdout.strip()
            if not response:
                self.result_ready.emit("Error: No response from the model")
                return

            self.result_ready.emit(response)

        except Exception as e:
            self.result_ready.emit(f"Error: {str(e)}")


class ChatTab(QWidget):
    """Individual chat tab widget"""

    message_sent = pyqtSignal(str, str)  # (message, model_name)

    def __init__(self, model_name: str, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.chat_history = ChatHistory()
        self.current_worker = None
        self.setup_ui()
        logger.debug(f"Created new chat tab with model: {model_name}")

    def setup_ui(self):
        """Setup the chat tab UI"""
        layout = QVBoxLayout(self)

        # Chat display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        # Input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)

        layout.addLayout(input_layout)

    def send_message(self):
        """Handle sending a message"""
        message = self.input_field.text().strip()
        if not message:
            return

        # Display user message
        self.output_display.append(f"You: {message}")
        self.chat_history.add_message("user", message)
        self.input_field.clear()

        # Start AI response worker
        self.current_worker = Worker(message, self.model_name)
        self.current_worker.result_ready.connect(self.handle_response)
        self.current_worker.start()

        logger.debug(f"Sent message to model {self.model_name}")

    def handle_response(self, response: str):
        """Handle AI response"""
        if response.startswith("Error:"):
            self.output_display.append(f"System: {response}")
            logger.error(f"AI response error: {response}")
            return

        # Clean response
        response = re.sub(r"<.*?>", "", response).strip()

        # Display response
        self.output_display.append(f"AI: {response}")
        self.chat_history.add_message("assistant", response)

        logger.debug("Received and displayed AI response")

    def clear_chat(self):
        """Clear the chat display"""
        reply = QMessageBox.question(
            self,
            "Clear Chat",
            "Are you sure you want to clear the chat? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.output_display.clear()
            logger.info("Chat cleared")

    def save_session(self):
        """Save the current chat session"""
        self.chat_history.save_session()
        logger.info("Chat session saved")


class TabManager(QTabWidget):
    """Manager for chat tabs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        # Add "+" button for new tabs
        self.addTab(QWidget(), "+")
        self.tabBarClicked.connect(self.handle_tab_click)

        logger.info("Tab manager initialized")

    def create_new_tab(self, model_name: str):
        """Create a new chat tab"""
        tab = ChatTab(model_name)
        index = self.count() - 1  # Insert before the "+" tab
        self.insertTab(index, tab, f"Chat {index + 1}")
        self.setCurrentIndex(index)
        logger.debug(f"Created new tab with model: {model_name}")
        return tab

    def close_tab(self, index: int):
        """Close a tab"""
        if self.count() > 2:  # Don't close if it's the last chat tab
            tab = self.widget(index)
            if isinstance(tab, ChatTab):
                reply = QMessageBox.question(
                    self,
                    "Save Session",
                    "Would you like to save this chat session?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    tab.save_session()

            self.removeTab(index)
            logger.debug(f"Closed tab at index: {index}")

    def handle_tab_click(self, index: int):
        """Handle tab clicks"""
        if index == self.count() - 1:
            # Clicked on "+" tab, create new tab
            self.create_new_tab("deepseek-coder")  # Default model
            logger.debug("Created new tab via '+' button")

    def save_all_sessions(self):
        """Save all active chat sessions"""
        for i in range(self.count() - 1):  # Exclude the "+" tab
            tab = self.widget(i)
            if isinstance(tab, ChatTab):
                tab.save_session()
        logger.info("Saved all chat sessions")

    def get_current_tab(self) -> Optional[ChatTab]:
        """Get the currently active chat tab"""
        current_widget = self.currentWidget()
        if isinstance(current_widget, ChatTab):
            return current_widget
        return None