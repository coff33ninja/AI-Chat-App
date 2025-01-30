from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
)
from typing import Dict, Callable
import logging

logger = logging.getLogger("ui.shortcuts")


class ShortcutManager:
    """Manages application keyboard shortcuts"""

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.shortcuts: Dict[str, QShortcut] = {}
        self.actions: Dict[str, Callable] = {}
        self.default_shortcuts = {
            "new_session": "Ctrl+N",
            "save_session": "Ctrl+S",
            "load_session": "Ctrl+O",
            "export_session": "Ctrl+E",
            "toggle_theme": "Ctrl+T",
            "settings": "Ctrl+,",
            "clear_chat": "Ctrl+L",
            "focus_input": "Ctrl+I",
            "stop_tts": "Ctrl+.",
            "toggle_tts": "Ctrl+Alt+T",
            "start_stt": "Ctrl+M",
        }
        self.load_shortcuts()
        logger.info("Shortcut manager initialized")

    def load_shortcuts(self):
        """Load shortcuts from settings"""
        settings = QSettings("AI-Chat-App", "Shortcuts")
        shortcuts_data = settings.value("shortcuts", {})

        # Use defaults for missing shortcuts
        self.current_shortcuts = self.default_shortcuts.copy()
        self.current_shortcuts.update(shortcuts_data)
        logger.debug("Loaded shortcuts from settings")

    def save_shortcuts(self):
        """Save shortcuts to settings"""
        settings = QSettings("AI-Chat-App", "Shortcuts")
        settings.setValue("shortcuts", self.current_shortcuts)
        logger.debug("Saved shortcuts to settings")

    def register_shortcut(self, action_name: str, callback: Callable):
        """Register a new shortcut"""
        if action_name in self.current_shortcuts:
            shortcut = QShortcut(
                QKeySequence(self.current_shortcuts[action_name]), self.parent
            )
            shortcut.activated.connect(callback)
            self.shortcuts[action_name] = shortcut
            self.actions[action_name] = callback
            logger.debug(f"Registered shortcut for {action_name}")

    def update_shortcut(self, action_name: str, new_sequence: str):
        """Update existing shortcut"""
        if action_name in self.shortcuts:
            self.current_shortcuts[action_name] = new_sequence
            self.shortcuts[action_name].setKey(QKeySequence(new_sequence))
            self.save_shortcuts()
            logger.debug(f"Updated shortcut for {action_name}")

    def trigger(self, action_name: str):
        """Trigger a shortcut action by name"""
        if action_name in self.actions:
            self.actions[action_name]()
            logger.debug(f"Triggered action {action_name}")

    def reset_to_defaults(self):
        """Reset all shortcuts to default values"""
        self.current_shortcuts = self.default_shortcuts.copy()
        for action_name, shortcut in self.shortcuts.items():
            shortcut.setKey(QKeySequence(self.default_shortcuts[action_name]))
        self.save_shortcuts()
        logger.info("Reset all shortcuts to defaults")

    def show_dialog(self):
        """Show the shortcut configuration dialog"""
        dialog = ShortcutDialog(self)
        dialog.exec()


class ShortcutDialog(QDialog):
    """Dialog for configuring keyboard shortcuts"""

    def __init__(self, shortcut_manager: ShortcutManager, parent=None):
        super().__init__(parent)
        self.shortcut_manager = shortcut_manager
        self.setup_ui()
        logger.debug("Opened shortcut configuration dialog")

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

        # Populate table
        self.table.setRowCount(len(self.shortcut_manager.current_shortcuts))
        for i, (action, shortcut) in enumerate(
            self.shortcut_manager.current_shortcuts.items()
        ):
            action_item = QTableWidgetItem(action.replace("_", " ").title())
            shortcut_item = QTableWidgetItem(shortcut)
            self.table.setItem(i, 0, action_item)
            self.table.setItem(i, 1, shortcut_item)

        layout.addWidget(self.table)

        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_shortcuts)
        layout.addWidget(reset_button)

    def reset_shortcuts(self):
        """Reset shortcuts to defaults"""
        self.shortcut_manager.reset_to_defaults()
        self.close()
        logger.info("Reset shortcuts to defaults via dialog")
