from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from .model_config import ModelConfig
import humanize
from datetime import datetime

class ModelDetailsDialog(QDialog):
    def __init__(self, model_name: str, model_config: ModelConfig, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.model_config = model_config
        
        self.setWindowTitle(f"Model Details - {model_name}")
        self.setMinimumSize(500, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Model info
        model_info = self.model_config.get_model_info(model_name)
        if model_info:
            # Basic info section
            basic_info = self._create_section("Basic Information")
            self._add_info_row(basic_info, "Name:", model_name)
            self._add_info_row(basic_info, "Description:", model_info.get("description", "N/A"))
            self._add_info_row(basic_info, "Context Length:", str(model_info.get("context_length", "N/A")))
            content_layout.addWidget(basic_info)
            
            # Parameters section
            params = model_info.get("parameters", {})
            if params:
                param_section = self._create_section("Parameters")
                for key, value in params.items():
                    self._add_info_row(param_section, f"{key}:", str(value))
                content_layout.addWidget(param_section)
            
            # Ollama metadata section
            metadata = model_info.get("ollama_metadata", {})
            if metadata:
                meta_section = self._create_section("Ollama Metadata")
                
                # Format size if available
                if metadata.get("size"):
                    size_str = humanize.naturalsize(metadata["size"])
                    self._add_info_row(meta_section, "Size:", size_str)
                
                # Format timestamp if available
                if metadata.get("modified_at"):
                    try:
                        timestamp = datetime.fromtimestamp(metadata["modified_at"])
                        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        self._add_info_row(meta_section, "Last Modified:", time_str)
                    except:
                        self._add_info_row(meta_section, "Last Modified:", str(metadata["modified_at"]))
                
                # Add other metadata
                if metadata.get("digest"):
                    self._add_info_row(meta_section, "Digest:", metadata["digest"])
                
                if metadata.get("system_prompt"):
                    self._add_info_row(meta_section, "System Prompt:", metadata["system_prompt"])
                
                if metadata.get("template"):
                    self._add_info_row(meta_section, "Template:", metadata["template"])
                
                content_layout.addWidget(meta_section)
        
        # Add content to scroll area
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                margin: 8px;
            }
            QLabel {
                color: #111b21;
            }
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
        """)
    
    def _create_section(self, title: str) -> QFrame:
        """Create a section frame with title"""
        section = QFrame()
        section.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(section)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #111b21;
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        return section
    
    def _add_info_row(self, parent: QFrame, label: str, value: str):
        """Add an information row to a section"""
        row = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            font-weight: bold;
            min-width: 120px;
        """)
        row.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_widget.setWordWrap(True)
        row.addWidget(value_widget, stretch=1)
        
        parent.layout().addLayout(row)