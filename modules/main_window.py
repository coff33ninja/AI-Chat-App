from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame, QMenu, QToolButton,
    QMessageBox, QDialog, QTabWidget, QSpinBox, QCheckBox,
    QColorDialog, QFileDialog, QInputDialog, QGroupBox,
    QSlider
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
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        # Create tab widget
        tabs = QTabWidget()

        # Model Settings Tab
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)

        # Model Configuration Group
        model_group = QGroupBox("Model Configuration")
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

        # Max tokens
        tokens_layout = QHBoxLayout()
        tokens_label = QLabel("Max Tokens:")
        tokens_label.setToolTip("Maximum length of generated responses")
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(100, 4000)
        self.tokens_spin.setValue(2000)
        tokens_layout.addWidget(tokens_label)
        tokens_layout.addWidget(self.tokens_spin)
        model_group_layout.addLayout(tokens_layout)

        # Context window
        context_layout = QHBoxLayout()
        context_label = QLabel("Context Window:")
        context_label.setToolTip("Number of previous messages to consider")
        self.context_spin = QSpinBox()
        self.context_spin.setRange(1, 20)
        self.context_spin.setValue(5)
        context_layout.addWidget(context_label)
        context_layout.addWidget(self.context_spin)
        model_group_layout.addLayout(context_layout)

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
        tabs.addTab(model_tab, "Model")

        # Theme Settings Tab
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)

        # Appearance Group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()

        # Theme Mode
        theme_mode_layout = QHBoxLayout()
        theme_mode_label = QLabel("Theme Mode:")
        self.theme_mode_combo = QComboBox()
        self.theme_mode_combo.addItems(["Light", "Dark", "System"])
        theme_mode_layout.addWidget(theme_mode_label)
        theme_mode_layout.addWidget(self.theme_mode_combo)
        appearance_layout.addLayout(theme_mode_layout)

        # Color Scheme
        colors_group = QGroupBox("Color Scheme")
        colors_layout = QVBoxLayout()

        # Primary Color
        primary_layout = QHBoxLayout()
        primary_label = QLabel("Primary Color:")
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setFixedSize(30, 30)
        self.primary_color_btn.clicked.connect(lambda: self.choose_color("primary"))
        self.set_button_color(self.primary_color_btn, "#128C7E")
        primary_layout.addWidget(primary_label)
        primary_layout.addWidget(self.primary_color_btn)
        colors_layout.addLayout(primary_layout)

        # Secondary Color
        secondary_layout = QHBoxLayout()
        secondary_label = QLabel("Secondary Color:")
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setFixedSize(30, 30)
        self.secondary_color_btn.clicked.connect(lambda: self.choose_color("secondary"))
        self.set_button_color(self.secondary_color_btn, "#075E54")
        secondary_layout.addWidget(secondary_label)
        secondary_layout.addWidget(self.secondary_color_btn)
        colors_layout.addLayout(secondary_layout)

        # Accent Color
        accent_layout = QHBoxLayout()
        accent_label = QLabel("Accent Color:")
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setFixedSize(30, 30)
        self.accent_color_btn.clicked.connect(lambda: self.choose_color("accent"))
        self.set_button_color(self.accent_color_btn, "#25D366")
        accent_layout.addWidget(accent_label)
        accent_layout.addWidget(self.accent_color_btn)
        colors_layout.addLayout(accent_layout)

        colors_group.setLayout(colors_layout)
        appearance_layout.addWidget(colors_group)

        # Font Settings
        font_group = QGroupBox("Font Settings")
        font_layout = QVBoxLayout()

        # Font Size
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spin)
        font_layout.addLayout(font_size_layout)

        # Font Family
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Font Family:")
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["System Default", "Arial", "Helvetica", "Times New Roman"])
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(self.font_family_combo)
        font_layout.addLayout(font_family_layout)

        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)

        appearance_group.setLayout(appearance_layout)
        theme_layout.addWidget(appearance_group)

        # Chat Appearance
        chat_appearance_group = QGroupBox("Chat Appearance")
        chat_layout = QVBoxLayout()

        self.show_timestamps = QCheckBox("Show Message Timestamps")
        self.show_timestamps.setChecked(True)
        chat_layout.addWidget(self.show_timestamps)

        self.compact_messages = QCheckBox("Compact Message Display")
        chat_layout.addWidget(self.compact_messages)

        self.show_avatars = QCheckBox("Show User Avatars")
        self.show_avatars.setChecked(True)
        chat_layout.addWidget(self.show_avatars)

        chat_appearance_group.setLayout(chat_layout)
        theme_layout.addWidget(chat_appearance_group)

        theme_layout.addStretch()
        tabs.addTab(theme_tab, "Theme")

        # Behavior Settings Tab
        behavior_tab = QWidget()
        behavior_layout = QVBoxLayout(behavior_tab)

        # Input Settings
        input_group = QGroupBox("Input Settings")
        input_layout = QVBoxLayout()

        self.send_on_enter = QCheckBox("Send Message on Enter")
        self.send_on_enter.setChecked(True)
        input_layout.addWidget(self.send_on_enter)

        self.spell_check = QCheckBox("Enable Spell Check")
        self.spell_check.setChecked(True)
        input_layout.addWidget(self.spell_check)

        self.auto_complete = QCheckBox("Enable Auto-Complete")
        self.auto_complete.setChecked(True)
        input_layout.addWidget(self.auto_complete)

        input_group.setLayout(input_layout)
        behavior_layout.addWidget(input_group)

        # Notification Settings
        notification_group = QGroupBox("Notifications")
        notification_layout = QVBoxLayout()

        self.desktop_notifications = QCheckBox("Enable Desktop Notifications")
        notification_layout.addWidget(self.desktop_notifications)

        self.sound_notifications = QCheckBox("Enable Sound Notifications")
        notification_layout.addWidget(self.sound_notifications)

        notification_group.setLayout(notification_layout)
        behavior_layout.addWidget(notification_group)

        # Privacy Settings
        privacy_group = QGroupBox("Privacy")
        privacy_layout = QVBoxLayout()

        self.save_history = QCheckBox("Save Chat History")
        self.save_history.setChecked(True)
        privacy_layout.addWidget(self.save_history)

        self.anonymous_usage = QCheckBox("Send Anonymous Usage Data")
        privacy_layout.addWidget(self.anonymous_usage)

        privacy_group.setLayout(privacy_layout)
        behavior_layout.addWidget(privacy_group)

        behavior_layout.addStretch()
        tabs.addTab(behavior_tab, "Behavior")

        # Speech Settings Tab
        speech_tab = QWidget()
        speech_layout = QVBoxLayout(speech_tab)

        # TTS Settings
        tts_group = QGroupBox("Text-to-Speech")
        tts_layout = QVBoxLayout()

        # TTS Engine
        tts_engine_layout = QHBoxLayout()
        tts_engine_label = QLabel("TTS Engine:")
        self.tts_engine_combo = QComboBox()
        self.tts_engine_combo.addItems(["System Default", "Coqui TTS", "pyttsx3"])
        tts_engine_layout.addWidget(tts_engine_label)
        tts_engine_layout.addWidget(self.tts_engine_combo)
        tts_layout.addLayout(tts_engine_layout)

        # Voice Selection
        voice_layout = QHBoxLayout()
        voice_label = QLabel("Voice:")
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Default Voice", "Male", "Female"])
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        tts_layout.addLayout(voice_layout)

        # Speech Rate
        rate_layout = QHBoxLayout()
        rate_label = QLabel("Speech Rate:")
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(50, 200)
        self.rate_slider.setValue(100)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.rate_slider)
        tts_layout.addLayout(rate_layout)

        tts_group.setLayout(tts_layout)
        speech_layout.addWidget(tts_group)

        # STT Settings
        stt_group = QGroupBox("Speech-to-Text")
        stt_layout = QVBoxLayout()

        # STT Engine
        stt_engine_layout = QHBoxLayout()
        stt_engine_label = QLabel("STT Engine:")
        self.stt_engine_combo = QComboBox()
        self.stt_engine_combo.addItems(["OpenAI Whisper", "System Default"])
        stt_engine_layout.addWidget(stt_engine_label)
        stt_engine_layout.addWidget(self.stt_engine_combo)
        stt_layout.addLayout(stt_engine_layout)

        # Language
        language_layout = QHBoxLayout()
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        stt_layout.addLayout(language_layout)

        stt_group.setLayout(stt_layout)
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
