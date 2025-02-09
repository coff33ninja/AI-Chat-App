import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from modules.main_window import MainWindow

# Configure logging with a valid datetime format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # Fixed datetime format
)

logger = logging.getLogger("run_app")

def show_error_dialog(message, details=None):
    """Show an error dialog to the user"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(message)
    msg.setWindowTitle("Application Error")
    if details:
        msg.setDetailedText(details)
    msg.exec()

def exception_handler(exctype, value, tb):
    """Global exception handler"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.error(f"Uncaught exception:\n{error_msg}")

    # Show error dialog to user
    show_error_dialog(
        "An unexpected error occurred.",
        f"Error Type: {exctype.__name__}\nError Message: {str(value)}\n\nTraceback:\n{error_msg}"
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Running dependency check...")

    # List of dependencies to check
    dependencies = {
        "speech_module": {
            "Python packages": {
                "Text-to-Speech (Coqui TTS)": "TTS",
                "Text-to-Speech (System)": "pyttsx3",
                "Speech-to-Text (OpenAI Whisper)": "whisper",
                "Audio recording": "sounddevice",
                "Numerical computations": "numpy",
                "GUI framework": "PyQt6"
            },
            "System dependencies": {
                "FFmpeg audio playback": "ffplay"
            }
        },
        "chat_history": {
            "Python packages": {
                "JSON handling": "json",
                "Date and time handling": "datetime"
            }
        },
        "model_config": {
            "Python packages": {
                "JSON handling": "json",
                "Type hints": "typing"
            }
        },
        "shortcut_manager": {
            "Python packages": {
                "GUI framework": "PyQt6"
            }
        },
        "tab_manager": {
            "Python packages": {
                "GUI framework": "PyQt6"
            }
        },
        "theme_manager": {
            "Python packages": {
                "GUI framework": "PyQt6",
                "JSON handling": "json"
            }
        }
    }

    logger.info("Checking dependencies...")
    missing_deps = []

    for module, categories in dependencies.items():
        logger.info(f"\nChecking dependencies for {module}:")

        for category, deps in categories.items():
            logger.info(f"\n{category}:")
            for dep_name, dep_package in deps.items():
                try:
                    if category == "Python packages":
                        __import__(dep_package)
                    elif category == "System dependencies":
                        if dep_package == "ffplay":
                            import shutil
                            if not shutil.which("ffplay"):
                                raise FileNotFoundError
                    logger.info(f"[OK] {dep_name}: {dep_package}")
                except ImportError:
                    logger.error(f"[FAIL] {dep_name}: {dep_package}")
                    missing_deps.append(f"{dep_name} ({dep_package})")
                except FileNotFoundError:
                    logger.error(f"[FAIL] {dep_name}: {dep_package}")
                    missing_deps.append(f"{dep_name} ({dep_package})")

    if not missing_deps:
        logger.info("\n[OK] All dependencies are satisfied!")
        return True
    else:
        error_msg = "The following dependencies are missing:\n- " + "\n- ".join(missing_deps)
        logger.error(f"\n[FAIL] {error_msg}")
        show_error_dialog("Missing Dependencies", error_msg)
        return False

def main():
    """Main application entry point"""
    try:
        logger.info("Starting the application setup process...")

        # Set up global exception handler
        sys.excepthook = exception_handler

        # Create QApplication instance
        app = QApplication(sys.argv)

        # Enable High DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        # Check dependencies
        logger.info("Running dependency check...")
        if not check_dependencies():
            logger.error("Dependency check failed. Please install missing dependencies.")
            sys.exit(1)

        # Start the application
        logger.info("All dependencies are satisfied. Starting the main application...")
        window = MainWindow()
        window.show()

        # Start event loop
        sys.exit(app.exec())

    except Exception as e:
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Failed to start application:\n{error_msg}")
        show_error_dialog(
            "Failed to start application",
            f"Error: {str(e)}\n\nTraceback:\n{error_msg}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
