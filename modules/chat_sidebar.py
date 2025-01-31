from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QStackedWidget,
    QToolButton,
    QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette

class ContactItem(QFrame):
    clicked = pyqtSignal(str)  # Signal to emit model name when clicked

    def __init__(self, model_name: str, description: str, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.setup_ui(model_name, description)
        
    def setup_ui(self, model_name: str, description: str):
        self.setObjectName("contactItem")
        self.setStyleSheet("""
            #contactItem {
                background-color: white;
                border: none;
                padding: 8px 12px;
            }
            #contactItem:hover {
                background-color: #f0f2f5;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Avatar container with WhatsApp style
        avatar_container = QFrame()
        avatar_container.setFixedSize(49, 49)
        avatar_container.setStyleSheet("""
            QFrame {
                background-color: #00a884;
                border-radius: 24px;
                margin: 0;
            }
        """)
        
        avatar_layout = QHBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Avatar/Icon with emoji
        avatar = QLabel("🤖")
        avatar.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
            }
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(avatar)
        
        layout.addWidget(avatar_container)
        
        # Contact info container
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                border-bottom: 1px solid #e9edef;
                padding-bottom: 8px;
            }
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Model name with WhatsApp style
        name_label = QLabel(model_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #111b21;
                font-size: 17px;
                font-weight: normal;
            }
        """)
        
        # Description with WhatsApp style
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #667781;
                font-size: 14px;
            }
        """)
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        layout.addWidget(info_container, stretch=1)

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit(self.model_name)
                # Add visual feedback
                self.setStyleSheet("""
                    #contactItem {
                        background-color: #e9edef;
                        border: none;
                        padding: 8px 12px;
                    }
                """)
            super().mousePressEvent(event)
        except Exception as e:
            print(f"Error in mousePressEvent: {str(e)}")

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # Restore normal style
                self.setStyleSheet("""
                    #contactItem {
                        background-color: white;
                        border: none;
                        padding: 8px 12px;
                    }
                    #contactItem:hover {
                        background-color: #f0f2f5;
                    }
                """)
            super().mouseReleaseEvent(event)
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {str(e)}")


class ChatSidebar(QWidget):
    model_selected = pyqtSignal(str)  # Signal to emit when a model is selected
    
    def __init__(self, model_config, parent=None):
        super().__init__(parent)
        self.model_config = model_config
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with WhatsApp style
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f0f2f5;
                border-right: 1px solid #d1d7db;
                border-bottom: 1px solid #d1d7db;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        
        # Profile section
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(12)
        
        # Profile avatar
        profile_avatar = QLabel("🤖")
        profile_avatar.setStyleSheet("""
            QLabel {
                background-color: #00a884;
                color: white;
                font-size: 22px;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
            }
        """)
        profile_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_layout.addWidget(profile_avatar)
        
        header_layout.addLayout(profile_layout)
        
        # Header buttons
        header_buttons = QHBoxLayout()
        header_buttons.setSpacing(8)
        
        # Refresh button
        refresh_btn = QToolButton()
        refresh_btn.setText("🔄")  # Using emoji instead of icon
        refresh_btn.setIconSize(QSize(24, 24))
        refresh_btn.setToolTip("Refresh Models")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.refresh_contacts)
        header_buttons.addWidget(refresh_btn)
        
        # New chat button
        new_chat_btn = QToolButton()
        new_chat_btn.setText("➕")  # Using emoji instead of icon
        new_chat_btn.setIconSize(QSize(24, 24))
        new_chat_btn.setStyleSheet("""
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
        header_buttons.addWidget(new_chat_btn)
        
        # Menu button
        menu_btn = QToolButton()
        menu_btn.setText("⋮")  # Using dots instead of icon
        menu_btn.setIconSize(QSize(24, 24))
        menu_btn.setStyleSheet("""
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
        header_buttons.addWidget(menu_btn)
        
        header_layout.addLayout(header_buttons)
        layout.addWidget(header)
        
        # Search bar with WhatsApp style
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: #f0f2f5;
                border-right: 1px solid #d1d7db;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(8, 8, 8, 8)
        
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search or start new chat")
        search_box.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 12px 9px 32px;
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
        search_layout.addWidget(search_box)
        layout.addWidget(search_container)
        
        # Scroll area for contacts with WhatsApp style
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
                border-right: 1px solid #d1d7db;
            }
            QScrollBar:vertical {
                border: none;
                background: #ffffff;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        contacts_widget = QWidget()
        self.contacts_layout = QVBoxLayout(contacts_widget)
        self.contacts_layout.setContentsMargins(0, 0, 0, 0)
        self.contacts_layout.setSpacing(0)
        
        # Add model contacts
        self.populate_contacts()
        
        # Add stretch at the bottom
        self.contacts_layout.addStretch()
        
        scroll.setWidget(contacts_widget)
        layout.addWidget(scroll)
        
    def populate_contacts(self):
        """Populate the sidebar with available models"""
        try:
            # Clear existing contacts first
            while self.contacts_layout.count() > 0:
                item = self.contacts_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Add model contacts
            for model_name in self.model_config.list_available_models():
                model_info = self.model_config.get_model_info(model_name)
                if model_info:
                    contact = ContactItem(
                        model_name,
                        model_info.get('description', 'No description available')
                    )
                    contact.clicked.connect(lambda name=model_name: self.model_selected.emit(name))
                    self.contacts_layout.addWidget(contact)

            # Add stretch at the bottom
            self.contacts_layout.addStretch()
        except Exception as e:
            print(f"Error populating contacts: {str(e)}")

    def refresh_contacts(self):
        """Refresh the contacts list"""
        try:
            # Sync models first
            if self.model_config.check_ollama_available():
                self.model_config.sync_models()
            # Repopulate contacts
            self.populate_contacts()
        except Exception as e:
            print(f"Error refreshing contacts: {str(e)}")
