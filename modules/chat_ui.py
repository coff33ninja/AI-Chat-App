from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QScrollBar
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QTimer, QRect
from PyQt6.QtGui import QPalette, QColor, QPainter, QPainterPath, QResizeEvent
from datetime import datetime
import json
from .worker import Worker

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

        # Message text
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextFormat(Qt.TextFormat.PlainText)
        message_layout.addWidget(text_label)

        # Timestamp
        time_label = QLabel(timestamp.strftime("%I:%M %p"))
        time_label.setStyleSheet("color: #444444; font-size: 10px;")
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
        """Update bubble style based on compact mode"""
        padding = "4px" if self.compact_mode else "8px"
        frame.setStyleSheet(f"""
            #userBubble {{
                background-color: #C0C0C0;
                border-radius: {8 if self.compact_mode else 10}px;
                padding: {padding};
            }}
            #userBubble QLabel {{
                color: #000000;
                font-size: {11 if self.compact_mode else 12}px;
            }}
            #aiBubble {{
                background-color: #E8E8E8;
                border-radius: {8 if self.compact_mode else 10}px;
                padding: {padding};
            }}
            #aiBubble QLabel {{
                color: #000000;
                font-size: {11 if self.compact_mode else 12}px;
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

        # Create dots
        self.dots = []
        for _ in range(3):
            dot = QLabel("•")
            dot.setStyleSheet(self.getDotStyle())
            self.main_layout.addWidget(dot)
            self.dots.append(dot)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_dots)
        self.animation_step = 0

        self.main_layout.addStretch()
        self.hide()

    def updateStyle(self):
        """Update indicator style based on compact mode"""
        self.setStyleSheet(f"""
            #typingIndicator {{
                background-color: #E0E0E0;
                border-radius: {8 if self.compact_mode else 10}px;
                padding: {4 if self.compact_mode else 8}px;
                margin: {2 if self.compact_mode else 5}px;
            }}
        """)

    def updateMargins(self):
        """Update margins based on compact mode"""
        if self.main_layout:
            self.main_layout.setContentsMargins(
                5 if self.compact_mode else 10,
                2 if self.compact_mode else 5,
                5 if self.compact_mode else 10,
                2 if self.compact_mode else 5
            )

    def getDotStyle(self):
        """Get dot style based on compact mode"""
        size = "20px" if self.compact_mode else "24px"
        return f"color: #444444; font-size: {size};"

    def setCompactMode(self, compact: bool):
        """Toggle compact mode"""
        if self.compact_mode != compact:
            self.compact_mode = compact
            self.updateStyle()
            self.updateMargins()
            for dot in self.dots:
                dot.setStyleSheet(self.getDotStyle())

    def animate_dots(self):
        base_sizes = [24, 20, 16] if not self.compact_mode else [20, 16, 12]
        styles = [
            f"color: #444444; font-size: {size}px;"
            for size in base_sizes
        ]

        for i, dot in enumerate(self.dots):
            style_index = (self.animation_step + i) % 3
            dot.setStyleSheet(styles[style_index])

        self.animation_step = (self.animation_step + 1) % 3

    def start_animation(self):
        self.show()
        self.timer.start(300)

    def stop_animation(self):
        self.timer.stop()
        self.hide()


class ChatDisplay(QScrollArea):
    COMPACT_WIDTH_THRESHOLD = 600

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.compact_mode = False
        self.chat_name = "New Chat"

        # Main widget and layout
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.updateLayoutSpacing()
        self.content_layout.addStretch()

        # Typing indicator
        self.typing_indicator = TypingIndicator()
        self.content_layout.addWidget(self.typing_indicator)

        self.setWidget(self.content_widget)
        self.updateStyle()

    def updateStyle(self):
        """Update scroll area style based on compact mode"""
        scrollbar_width = "8px" if self.compact_mode else "10px"
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: #E5DDD5;
            }}
            QScrollBar:vertical {{
                border: none;
                background: #F0F0F0;
                width: {scrollbar_width};
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #AAAAAA;
                min-height: 20px;
                border-radius: {4 if self.compact_mode else 5}px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

    def updateLayoutSpacing(self):
        """Update layout spacing based on compact mode"""
        if self.content_layout:
            self.content_layout.setSpacing(5 if self.compact_mode else 10)
            self.content_layout.setContentsMargins(
                5 if self.compact_mode else 10,
                5 if self.compact_mode else 10,
                5 if self.compact_mode else 10,
                5 if self.compact_mode else 10
            )

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to toggle compact mode"""
        super().resizeEvent(event)
        new_compact_mode = event.size().width() < self.COMPACT_WIDTH_THRESHOLD

        if new_compact_mode != self.compact_mode:
            self.compact_mode = new_compact_mode
            self.updateStyle()
            self.updateLayoutSpacing()

            # Update all message bubbles
            for i in range(self.content_layout.count()):
                item = self.content_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, (MessageBubble, TypingIndicator)):
                        widget.setCompactMode(self.compact_mode)

    def add_message(self, text: str, is_user: bool = False):
        """Add a message to the chat display"""
        # Get the scroll bar
        scrollbar = self.verticalScrollBar()
        if not scrollbar:
            return

        # Remove the stretch if it exists
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.spacerItem():
                self.content_layout.removeItem(item)
                break

        # Create and add the message bubble
        bubble = MessageBubble(text, datetime.now(), is_user)
        bubble.setCompactMode(self.compact_mode)  # Set initial compact mode
        self.content_layout.addWidget(bubble)

        # Add stretch back
        self.content_layout.addStretch()

        # Ensure scrollbar exists before trying to scroll
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def send_message(self, text: str):
        """Send a message and handle the response in a thread-safe way"""
        try:
            # Add user message to chat
            self.add_message(text, is_user=True)
            
            # Show typing indicator
            self.show_typing_indicator()
            
            # Create and configure worker thread
            self.worker = Worker(text, self.current_model, self.model_config)
            
            # Connect signals
            self.worker.result_ready.connect(self.handle_response)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.finished.connect(self.cleanup_worker)
            
            # Start worker thread
            self.worker.start()
            
        except Exception as e:
            self.hide_typing_indicator()
            self.add_message(f"Error sending message: {str(e)}", is_user=False)
            
    def handle_response(self, response: str):
        """Handle the response from the worker thread"""
        self.hide_typing_indicator()
        self.add_message(response, is_user=False)
        
    def handle_error(self, error_message: str):
        """Handle any errors from the worker thread"""
        self.hide_typing_indicator()
        self.add_message(error_message, is_user=False)
        
    def cleanup_worker(self):
        """Clean up the worker thread"""
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.worker.deleteLater()
            del self.worker

    def show_typing_indicator(self):
        """Show the typing indicator"""
        self.typing_indicator.setCompactMode(self.compact_mode)  # Ensure correct mode
        self.typing_indicator.start_animation()
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def hide_typing_indicator(self):
        """Hide the typing indicator"""
        self.typing_indicator.stop_animation()

    def clear_messages(self):
        """Clear all messages from the chat"""
        # Remove all widgets except the typing indicator and stretch
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget and not isinstance(widget, TypingIndicator):
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