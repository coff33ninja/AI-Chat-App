from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

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
                border-bottom: 1px solid #E0E0E0;
                padding: 10px;
            }
            #contactItem:hover {
                background-color: #F5F5F5;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Avatar/Icon
        avatar = QLabel("🤖")
        avatar.setStyleSheet("""
            QLabel {
                background-color: #128C7E;
                color: white;
                border-radius: 20px;
                padding: 8px;
                font-size: 18px;
            }
        """)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar)
        
        # Model info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(model_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #666666; font-size: 12px;")
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        layout.addLayout(info_layout, stretch=1)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.model_name)


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
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #128C7E;
                color: white;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("AI Chat Models")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Scroll area for contacts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
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
        for model_name in self.model_config.list_available_models():
            model_info = self.model_config.get_model_info(model_name)
            if model_info:
                contact = ContactItem(
                    model_name,
                    model_info.get('description', 'No description available')
                )
                contact.clicked.connect(self.model_selected.emit)
                self.contacts_layout.addWidget(contact)
