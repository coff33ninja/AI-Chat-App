from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame, QMenu, QToolButton,
    QMessageBox, QDialog, QTabWidget, QSpinBox, QCheckBox,
    QColorDialog, QFileDialog, QInputDialog, QGroupBox,
    QSlider, QTableWidget, QTableWidgetItem, QHeaderView,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QColor
from .model_config import ModelConfig
from .chat_layout import ChatLayout
from .speech_module import SpeechHandler
from .theme_manager import ThemeManager
from .shortcut_manager import ShortcutManager
import logging
import json
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.model_config = ModelConfig()

        layout = QVBoxLayout(self)

        # Create tab widget
        tabs = QTabWidget()

        # Model Settings Tab
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)

        # Sync Models Button
        sync_layout = QHBoxLayout()
        sync_button = QPushButton("🔄 Sync Models from Ollama")
        sync_button.clicked.connect(self.sync_models)
        sync_layout.addWidget(sync_button)
        sync_layout.addStretch()
        model_layout.addLayout(sync_layout)

        # Models Table
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(5)
        self.models_table.setHorizontalHeaderLabels([
            "Model Name", 
            "Family",
            "Parameters",
            "Quantization",
            "Size"
        ])
        header = self.models_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        model_layout.addWidget(self.models_table)

        # Model Configuration Group
        model_group = QGroupBox("Model Parameters")
        model_group_layout = QVBoxLayout()

        # Temperature
        temp_layout = QHBoxLayout()
        temp_label = QLabel("Temperature:")
        temp_label.setToolTip("Controls randomness in responses (0 = deterministic, 100 = creative)")
        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(0, 100)
        self.temp_spin.setValue(70)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_spin)
        model_group_layout.addLayout(temp_layout)

        # Top P
        top_p_layout = QHBoxLayout()
        top_p_label = QLabel("Top P:")
        top_p_label.setToolTip("Nucleus sampling threshold")
        self.top_p_spin = QSpinBox()
        self.top_p_spin.setRange(1, 100)
        self.top_p_spin.setValue(95)
        top_p_layout.addWidget(top_p_label)
        top_p_layout.addWidget(self.top_p_spin)
        model_group_layout.addLayout(top_p_layout)

        # Top K
        top_k_layout = QHBoxLayout()
        top_k_label = QLabel("Top K:")
        top_k_label.setToolTip("Number of tokens to consider for sampling")
        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(1, 100)
        self.top_k_spin.setValue(40)
        top_k_layout.addWidget(top_k_label)
        top_k_layout.addWidget(self.top_k_spin)
        model_group_layout.addLayout(top_k_layout)

        # Repeat Penalty
        repeat_layout = QHBoxLayout()
        repeat_label = QLabel("Repeat Penalty:")
        repeat_label.setToolTip("Penalty for repeating tokens")
        self.repeat_spin = QDoubleSpinBox()
        self.repeat_spin.setRange(1.0, 2.0)
        self.repeat_spin.setSingleStep(0.1)
        self.repeat_spin.setValue(1.1)
        repeat_layout.addWidget(repeat_label)
        repeat_layout.addWidget(self.repeat_spin)
        model_group_layout.addLayout(repeat_layout)

        model_group.setLayout(model_group_layout)
        model_layout.addWidget(model_group)

        # Response Settings Group
        response_group = QGroupBox("Response Settings")
        response_layout = QVBoxLayout()

        self.stream_responses = QCheckBox("Stream Responses")
        self.stream_responses.setToolTip("Show responses as they are generated")
        self.stream_responses.setChecked(True)
        response_layout.addWidget(self.stream_responses)

        self.auto_scroll = QCheckBox("Auto-scroll Chat")
        self.auto_scroll.setToolTip("Automatically scroll to new messages")
        self.auto_scroll.setChecked(True)
        response_layout.addWidget(self.auto_scroll)

        response_group.setLayout(response_layout)
        model_layout.addWidget(response_group)

        model_layout.addStretch()
        tabs.addTab(model_tab, "Models")

        # Theme Settings Tab
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)

        # Color Theme Group
        color_group = QGroupBox("Color Theme")
        color_layout = QVBoxLayout()

        # Primary Color
        primary_layout = QHBoxLayout()
        primary_label = QLabel("Primary Color:")
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.clicked.connect(lambda: self.choose_color("primary"))
        self.set_button_color(self.primary_color_btn, "#128C7E")  # WhatsApp green
        primary_layout.addWidget(primary_label)
        primary_layout.addWidget(self.primary_color_btn)
        color_layout.addLayout(primary_layout)

        # Secondary Color
        secondary_layout = QHBoxLayout()
        secondary_label = QLabel("Secondary Color:")
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.clicked.connect(lambda: self.choose_color("secondary"))
        self.set_button_color(self.secondary_color_btn, "#075E54")  # WhatsApp dark green
        secondary_layout.addWidget(secondary_label)
        secondary_layout.addWidget(self.secondary_color_btn)
        color_layout.addLayout(secondary_layout)

        # Background Color
        bg_layout = QHBoxLayout()
        bg_label = QLabel("Background Color:")
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.clicked.connect(lambda: self.choose_color("bg"))
        self.set_button_color(self.bg_color_btn, "#FFFFFF")
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_color_btn)
        color_layout.addLayout(bg_layout)

        # Text Color
        text_layout = QHBoxLayout()
        text_label = QLabel("Text Color:")
        self.text_color_btn = QPushButton()
        self.text_color_btn.clicked.connect(lambda: self.choose_color("text"))
        self.set_button_color(self.text_color_btn, "#000000")
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_color_btn)
        color_layout.addLayout(text_layout)

        color_group.setLayout(color_layout)
        theme_layout.addWidget(color_group)

        # Theme Options Group
        theme_options_group = QGroupBox("Theme Options")
        theme_options_layout = QVBoxLayout()

        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.setToolTip("Enable dark mode theme")
        theme_options_layout.addWidget(self.dark_mode)

        self.custom_css = QCheckBox("Use Custom CSS")
        self.custom_css.setToolTip("Enable custom CSS styling")
        theme_options_layout.addWidget(self.custom_css)

        theme_options_group.setLayout(theme_options_layout)
        theme_layout.addWidget(theme_options_group)

        theme_layout.addStretch()
        tabs.addTab(theme_tab, "Theme")

        # Speech Settings Tab
        speech_tab = QWidget()
        speech_layout = QVBoxLayout(speech_tab)

        # TTS Settings Group
        tts_group = QGroupBox("Text-to-Speech Settings")
        tts_group_layout = QVBoxLayout()

        # TTS Engine Selection
        engine_layout = QHBoxLayout()
        engine_label = QLabel("TTS Engine:")
        self.tts_engine = QComboBox()
        self.tts_engine.addItems(["System TTS", "Coqui TTS"])
        engine_layout.addWidget(engine_label)
        engine_layout.addWidget(self.tts_engine)
        tts_group_layout.addLayout(engine_layout)

        # Voice Selection
        voice_layout = QHBoxLayout()
        voice_label = QLabel("Voice:")
        self.voice_select = QComboBox()
        self.voice_select.addItems(["Default"])  # Will be populated based on engine
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_select)
        tts_group_layout.addLayout(voice_layout)

        # Speed Control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speech Speed:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(25)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        tts_group_layout.addLayout(speed_layout)

        tts_group.setLayout(tts_group_layout)
        speech_layout.addWidget(tts_group)

        # STT Settings Group
        stt_group = QGroupBox("Speech-to-Text Settings")
        stt_group_layout = QVBoxLayout()

        # Recording Duration
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Recording Duration (seconds):")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(5)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spin)
        stt_group_layout.addLayout(duration_layout)

        # Auto-detect Language
        self.auto_detect = QCheckBox("Auto-detect Language")
        self.auto_detect.setChecked(True)
        stt_group_layout.addWidget(self.auto_detect)

        # Continuous Listening
        self.continuous = QCheckBox("Continuous Listening Mode")
        self.continuous.setToolTip("Automatically start new recording after each transcription")
        stt_group_layout.addWidget(self.continuous)

        stt_group.setLayout(stt_group_layout)
        speech_layout.addWidget(stt_group)

        speech_layout.addStretch()
        tabs.addTab(speech_tab, "Speech")

        layout.addWidget(tabs)

        # Add OK/Cancel buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        # Initialize models table
        self.refresh_models_table()

    def sync_models(self):
        """Sync models from Ollama"""
        try:
            self.model_config.sync_models()
            self.refresh_models_table()
            QMessageBox.information(self, "Success", "Successfully synced models from Ollama!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to sync models: {str(e)}")

    def refresh_models_table(self):
        """Refresh the models table with current data"""
        self.models_table.setRowCount(0)
        for model_name, model_info in self.model_config.models.items():
            details = model_info.get("details", {})
            row = self.models_table.rowCount()
            self.models_table.insertRow(row)
            
            # Model Name
            self.models_table.setItem(row, 0, QTableWidgetItem(model_name))
            
            # Family
            family = details.get("family", "").title()
            self.models_table.setItem(row, 1, QTableWidgetItem(family))
            
            # Parameters
            param_size = details.get("parameter_size", "")
            self.models_table.setItem(row, 2, QTableWidgetItem(param_size))
            
            # Quantization
            quant = details.get("quantization_level", "")
            self.models_table.setItem(row, 3, QTableWidgetItem(quant))
            
            # Size
            size_bytes = model_info.get("size", 0)
            size_gb = size_bytes / (1024 * 1024 * 1024)  # Convert to GB
            size_text = f"{size_gb:.2f} GB"
            self.models_table.setItem(row, 4, QTableWidgetItem(size_text))

    def set_button_color(self, button: QPushButton, color: str):
        """Set the background color of a button"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 5px;
            }}
        """)

    def choose_color(self, color_type: str):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            button = getattr(self, f"{color_type}_color_btn")
            self.set_button_color(button, color.name())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("main.window")
        self.logger.info("Initializing main window")

        # Initialize components
        self.model_config = ModelConfig()
        self.speech_handler = SpeechHandler(self)
        self.theme_manager = ThemeManager()
        self.shortcut_manager = ShortcutManager(self)

        # TTS state
        self.tts_enabled = False

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        self.setWindowTitle("AI Chat App")
        self.setMinimumSize(800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top toolbar for TTS controls and menu
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border-bottom: 1px solid #CCCCCC;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # TTS toggle
        tts_layout = QHBoxLayout()
        tts_layout.setSpacing(5)

        tts_label = QLabel("Text-to-Speech:")
        tts_layout.addWidget(tts_label)

        self.tts_toggle = QPushButton("Enable TTS")
        self.tts_toggle.setCheckable(True)
        self.tts_toggle.setStyleSheet("""
            QPushButton {
                background-color: #CCCCCC;
                border: none;
                border-radius: 10px;
                padding: 5px 10px;
                color: white;
            }
            QPushButton:checked {
                background-color: #128C7E;
            }
        """)
        self.tts_toggle.clicked.connect(self.toggle_tts)
        tts_layout.addWidget(self.tts_toggle)

        # Voice selection
        self.tts_dropdown = QComboBox()
        self.tts_dropdown.addItems(self.speech_handler.get_available_tts_methods())
        self.tts_dropdown.setEnabled(False)
        tts_layout.addWidget(self.tts_dropdown)

        # Speaking indicator and stop button
        self.speaking_indicator = QLabel("")
        tts_layout.addWidget(self.speaking_indicator)

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
        tts_layout.addWidget(self.stop_button)

        toolbar_layout.addLayout(tts_layout)
        toolbar_layout.addStretch()

        # Add menu button to top right
        menu_button = QToolButton(self)
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-size: 20px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
            QToolButton::menu-indicator {
                image: none;
            }
        """)
        menu_button.setText("☰")  # Hamburger menu icon
        menu_button.setFixedSize(32, 32)

        # Create popup menu
        menu = QMenu(self)

        # File menu
        file_menu = QMenu("File", self)
        new_action = QAction("New Chat", self)
        new_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_action)

        save_action = QAction("Save Chat", self)
        save_action.triggered.connect(self.save_chat)
        file_menu.addAction(save_action)

        load_action = QAction("Load Chat", self)
        load_action.triggered.connect(self.load_chat)
        file_menu.addAction(load_action)

        export_action = QAction("Export Chat", self)
        export_action.triggered.connect(self.export_chat)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        menu.addMenu(file_menu)

        # Edit menu
        edit_menu = QMenu("Edit", self)
        clear_action = QAction("Clear Chat", self)
        clear_action.triggered.connect(self.clear_chat)
        edit_menu.addAction(clear_action)

        rename_action = QAction("Rename Chat", self)
        rename_action.triggered.connect(self.rename_chat)
        edit_menu.addAction(rename_action)

        menu.addMenu(edit_menu)

        # Settings menu
        settings_menu = QMenu("Settings", self)
        model_settings_action = QAction("Settings", self)
        model_settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(model_settings_action)

        menu.addMenu(settings_menu)

        # View menu
        view_menu = QMenu("View", self)
        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        menu.addMenu(view_menu)

        # Help menu
        help_menu = QMenu("Help", self)
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)

        keyboard_shortcuts_action = QAction("Keyboard Shortcuts", self)
        keyboard_shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(keyboard_shortcuts_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        menu.addMenu(help_menu)

        menu_button.setMenu(menu)
        toolbar_layout.addWidget(menu_button)

        layout.addWidget(toolbar)

        # Chat layout
        self.chat_layout = ChatLayout(self.model_config)
        layout.addWidget(self.chat_layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.shortcut_manager.register_shortcut("Ctrl+Q", self.close)
        self.shortcut_manager.register_shortcut("Ctrl+N", self.new_chat)
        self.shortcut_manager.register_shortcut("Ctrl+S", self.save_chat)
        self.shortcut_manager.register_shortcut("Ctrl+O", self.load_chat)

    def toggle_tts(self, enabled: bool):
        """Toggle text-to-speech functionality"""
        self.tts_enabled = enabled
        self.tts_dropdown.setEnabled(enabled)
        self.tts_toggle.setText("Disable TTS" if enabled else "Enable TTS")

    def stop_speaking(self):
        """Stop current TTS playback"""
        self.speech_handler.stop_speaking()
        self.speaking_indicator.setText("")
        self.stop_button.setEnabled(False)

    def new_chat(self):
        """Create a new chat"""
        self.chat_layout.new_chat()

    def save_chat(self):
        """Save current chat"""
        self.chat_layout.save_chat()

    def load_chat(self):
        """Load a saved chat"""
        self.chat_layout.load_chat()

    def export_chat(self):
        """Export chat to file"""
        self.chat_layout.export_chat()

    def clear_chat(self):
        """Clear current chat"""
        reply = QMessageBox.question(
            self,
            "Clear Chat",
            "Are you sure you want to clear the current chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_layout.clear_chat()

    def rename_chat(self):
        """Rename current chat"""
        text, ok = QInputDialog.getText(
            self,
            "Rename Chat",
            "Enter new name:",
            text="New Chat"
        )
        if ok and text:
            self.chat_layout.rename_chat(text)

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # TODO: Apply settings
            pass

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        self.chat_layout.toggle_sidebar()

    def show_documentation(self):
        """Show documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation viewer coming soon!\n\n"
            "Features:\n"
            "- Chat with AI models\n"
            "- Text-to-Speech support\n"
            "- Multiple chat sessions\n"
            "- Customizable settings\n"
            "- Keyboard shortcuts"
        )

    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            "Keyboard Shortcuts:\n\n"
            "Ctrl+N: New Chat\n"
            "Ctrl+S: Save Chat\n"
            "Ctrl+O: Load Chat\n"
            "Ctrl+Q: Exit"
        )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About",
            "AI Chat App\n\n"
            "Version: 1.0.0\n\n"
            "A sophisticated chat application that leverages AI models through Ollama integration, "
            "featuring a modern PyQt6 interface with support for text-to-speech and speech-to-text capabilities.\n\n"
            "Features:\n"
            "- Multiple AI model support\n"
            "- Text-to-Speech\n"
            "- Speech-to-Text\n"
            "- Theme customization\n"
            "- Keyboard shortcuts"
        )

    def closeEvent(self, event):
        """Handle application closure"""
        self.logger.info("Closing application")
        self.speech_handler.stop_speaking()
        event.accept()
