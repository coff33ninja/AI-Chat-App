from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QFrame,
    QMenuBar,
    QMenu,
    QMessageBox,
)
import sys
import subprocess
import logging
from datetime import datetime

from modules.speech_module import SpeechHandler, PYTTSX3_AVAILABLE, COQUI_TTS_AVAILABLE, STT_AVAILABLE
from modules.theme_manager import ThemeManager, Theme
from modules.model_config import ModelConfig
from modules.logger_config import setup_logging
from modules.chat_history import ChatHistory
from modules.shortcut_manager import ShortcutManager
from modules.tab_manager import TabManager

# Setup logging
loggers = setup_logging()
logger = loggers["main"]


class Worker(QThread):
    """Worker thread for running AI models"""
    result_ready = pyqtSignal(str)

    def __init__(self, query: str, model_name: str, model_config: ModelConfig):
        super().__init__()
        self.query = query
        self.model_name = model_name
        self.model_config = model_config
        self.logger = logging.getLogger("main.worker")
        self.logger.info(f"Worker initialized for model: {model_name}")

    def run(self):
        try:
            # Check if ollama is available
            self.logger.debug("Checking Ollama availability...")
            try:
                subprocess.run(["ollama", "list"], capture_output=True, text=True)
                self.logger.info("Ollama is available")
            except FileNotFoundError:
                error_msg = "Error: Ollama is not installed or not in PATH. Please install Ollama first."
                self.logger.error(error_msg)
                self.result_ready.emit(error_msg)
                return

            # Get model parameters
            self.logger.debug(f"Getting parameters for model: {self.model_name}")
            params = self.model_config.get_model_parameters(self.model_name)
            self.logger.debug(f"Model parameters: {params}")

            # Execute model query
            self.logger.info(f"Executing query with model {self.model_name}")
            self.logger.debug(f"Query text: {self.query[:100]}...")  # Log first 100 chars
            
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=self.query,
                text=True,
                capture_output=True,
                encoding="utf-8",
            )

            if result.returncode != 0:
                error_msg = f"Error: {result.stderr}"
                self.logger.error(f"Model execution failed: {error_msg}")
                self.result_ready.emit(error_msg)
                return

            response = result.stdout.strip()
            if not response:
                error_msg = "Error: No response from the model."
                self.logger.error(error_msg)
                self.result_ready.emit(error_msg)
                return

            self.logger.info("Successfully generated response")
            self.logger.debug(f"Response length: {len(response)} characters")
            self.result_ready.emit(response)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.logger.error(f"Unexpected error in worker thread: {str(e)}", exc_info=True)
            self.result_ready.emit(error_msg)


class DeepSeekApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat App")
        self.setGeometry(100, 100, 800, 600)

        # Initialize components
        self.speech_handler = SpeechHandler(self)
        self.theme_manager = ThemeManager()
        self.model_config = ModelConfig()
        self.chat_history = ChatHistory()
        self.shortcut_manager = ShortcutManager(self)

        # Initialize UI
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()

        # Apply default theme
        self.theme_manager.apply_theme(QApplication.instance(), Theme.LIGHT)
        
        logger.info("Application initialized")

    def setup_menu(self):
        """Setup the application menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        new_action = file_menu.addAction("New Chat")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_tab)
        
        save_action = file_menu.addAction("Save Chat")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_session)

        # View Menu
        view_menu = menubar.addMenu("View")
        theme_action = view_menu.addAction("Toggle Theme")
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)

        # Settings Menu
        settings_menu = menubar.addMenu("Settings")
        model_action = settings_menu.addAction("Model Settings")
        model_action.triggered.connect(self.show_model_settings)
        
        shortcuts_action = settings_menu.addAction("Keyboard Shortcuts")
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)

    def setup_ui(self):
        """Setup the UI components"""
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Top Controls Section
        self.setup_top_controls()

        # Tab Manager
        self.tab_manager = TabManager(self)
        self.layout.addWidget(self.tab_manager)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.shortcut_manager.register_shortcut("new_session", self.create_new_tab)
        self.shortcut_manager.register_shortcut("save_session", self.save_current_session)
        self.shortcut_manager.register_shortcut("clear_chat", self.clear_current_chat)
        self.shortcut_manager.register_shortcut("toggle_theme", self.toggle_theme)
        self.shortcut_manager.register_shortcut("toggle_tts", lambda: self.tts_toggle.setChecked(not self.tts_toggle.isChecked()))
        self.shortcut_manager.register_shortcut("stop_tts", self.stop_speaking)
        self.shortcut_manager.register_shortcut("start_stt", self.start_listening)

    def setup_top_controls(self):
        """Setup the top control panel"""
        top_controls = QFrame()
        top_controls.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        top_layout = QHBoxLayout(top_controls)

        # TTS Controls
        tts_group = QVBoxLayout()
        tts_methods = self.speech_handler.get_available_tts_methods()

        if tts_methods:
            self.tts_toggle = QCheckBox("Enable TTS")
            self.tts_toggle.stateChanged.connect(self.toggle_tts)
            tts_group.addWidget(self.tts_toggle)

            tts_label = QLabel("TTS Method:")
            self.tts_dropdown = QComboBox()
            self.tts_dropdown.addItems(tts_methods)
            tts_group.addWidget(tts_label)
            tts_group.addWidget(self.tts_dropdown)

            self.stop_button = QPushButton("Stop Speaking")
            self.stop_button.clicked.connect(self.stop_speaking)
            self.stop_button.setEnabled(False)
            tts_group.addWidget(self.stop_button)
        else:
            tts_label = QLabel("TTS not available.\nInstall TTS or pyttsx3.")
            tts_label.setStyleSheet("color: gray;")
            tts_group.addWidget(tts_label)

        top_layout.addLayout(tts_group)

        # STT Controls
        stt_group = QVBoxLayout()
        if STT_AVAILABLE:
            stt_label = QLabel("Speech-to-Text:")
            self.stt_button = QPushButton("🎤 Listen")
            self.stt_button.clicked.connect(self.start_listening)
            self.stt_status = QLabel("")
            self.stt_status.setStyleSheet("color: gray;")
            stt_group.addWidget(stt_label)
            stt_group.addWidget(self.stt_button)
            stt_group.addWidget(self.stt_status)
        else:
            stt_label = QLabel("STT not available.\nInstall whisper and\nsounddevice.")
            stt_label.setStyleSheet("color: gray;")
            stt_group.addWidget(stt_label)

        top_layout.addLayout(stt_group)
        self.layout.addWidget(top_controls)

        # Speaking Status
        self.speaking_indicator = QLabel("")
        self.speaking_indicator.setStyleSheet("color: gray;")
        self.layout.addWidget(self.speaking_indicator)

    def create_new_tab(self):
        """Create a new chat tab"""
        model_name = self.model_config.list_available_models()[0]  # Default to first model
        tab = self.tab_manager.create_model_tab(model_name)
        return tab

    def save_current_session(self):
        """Save the current chat session"""
        current_tab = self.tab_manager.get_current_tab()
        if current_tab:
            model_name = self.tab_manager.tabText(self.tab_manager.currentIndex())
            chat_text = current_tab.output_display.toPlainText()
            
            try:
                # Save to chat history
                session_name = f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                messages = []
                for line in chat_text.split('\n'):
                    if line.startswith("User: "):
                        messages.append({"role": "user", "content": line[6:]})
                    elif line.startswith("Assistant: "):
                        messages.append({"role": "assistant", "content": line[11:]})
                
                self.chat_history.current_session = messages
                if self.chat_history.save_session(session_name):
                    logger.info(f"Saved chat session to chat history: {session_name}")
            except Exception as e:
                logger.error(f"Error saving chat session: {e}")


    def clear_current_chat(self):
        """Clear the current chat tab"""
        current_tab = self.tab_manager.get_current_tab()
        if current_tab:
            current_tab.output_display.clear()
            logger.info("Cleared current chat")

    def show_shortcuts_dialog(self):
        """Show the keyboard shortcuts configuration dialog"""
        self.shortcut_manager.show_dialog()
        logger.debug("Opened shortcuts dialog")

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_theme = self.theme_manager.current_theme
        new_theme = Theme.DARK if current_theme == Theme.LIGHT else Theme.LIGHT
        self.theme_manager.apply_theme(QApplication.instance(), new_theme)

    def show_model_settings(self):
        """Show model settings dialog"""
        current_tab = self.tab_manager.get_current_tab()
        if current_tab:
            model_name = self.tab_manager.tabText(self.tab_manager.currentIndex())
            info = self.model_config.get_model_info(model_name)
            if info:
                current_tab.output_display.append("\nModel Information:")
                current_tab.output_display.append(f"Name: {info['name']}")
                current_tab.output_display.append(f"Description: {info['description']}")
                current_tab.output_display.append(f"Context Length: {info['context_length']}")
                current_tab.output_display.append("Parameters:")
                for k, v in info["parameters"].items():
                    current_tab.output_display.append(f"  {k}: {v}")
                current_tab.output_display.append("-" * 50)

    def toggle_tts(self, state):
        """Toggle TTS functionality"""
        self.tts_enabled = bool(state)
        self.stop_button.setEnabled(self.tts_enabled)
        status = "enabled" if self.tts_enabled else "disabled"
        current_tab = self.tab_manager.get_current_tab()
        if current_tab:
            current_tab.output_display.append(f"Text-to-Speech {status}")

    def stop_speaking(self):
        """Stop current TTS output"""
        self.speech_handler.stop_speaking()
        self.speaking_indicator.setText("")
        self.stop_button.setEnabled(False)

    def start_listening(self):
        """Start STT recording"""
        current_tab = self.tab_manager.get_current_tab()
        if not current_tab:
            return

        self.stt_button.setEnabled(False)
        self.stt_status.setText("Listening...")

        def stt_callback(text=None, status=None, error=None):
            if status:
                self.stt_status.setText(status)
            if text:
                current_tab.input_field.setText(text)
                self.stt_status.setText("Ready")
            if error:
                current_tab.output_display.append(f"STT Error: {error}")
                self.stt_status.setText("Ready")
            self.stt_button.setEnabled(True)

        self.speech_handler.start_listening(callback=stt_callback)

    def closeEvent(self, event):
        """Clean up before closing"""
        reply = QMessageBox.question(
            self,
            "Save Sessions",
            "Would you like to save all chat sessions before closing?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tab_manager.save_all_sessions()

        # Stop any ongoing TTS
        self.stop_speaking()
        
        # Close all tabs and cleanup workers
        for i in range(self.tab_manager.count()):
            tab = self.tab_manager.widget(i)
            if hasattr(tab, 'current_worker') and tab.current_worker and tab.current_worker.isRunning():
                tab.current_worker.quit()
                tab.current_worker.wait()
        
        event.accept()
        logger.info("Application closing")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeepSeekApp()
    window.show()
    sys.exit(app.exec())
