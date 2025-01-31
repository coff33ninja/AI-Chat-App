from enum import Enum
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"


class ThemeManager:
    def __init__(self):
        self.current_theme = Theme.LIGHT

    def apply_theme(self, app: QApplication, theme: Theme):
        """Apply the specified theme to the application"""
        self.current_theme = theme
        palette = QPalette()

        if theme == Theme.DARK:
            # Dark theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(127, 127, 127))
        else:
            # Light theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 231, 227))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Text, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(127, 127, 127))


        app.setPalette(palette)
