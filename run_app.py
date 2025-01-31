import sys
import logging
from PyQt6.QtWidgets import QApplication
from modules.main_window import MainWindow

# Configure logging with a valid datetime format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # Fixed datetime format
)

logger = logging.getLogger("run_app")

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

    print("Checking dependencies...")
    all_satisfied = True

    for module, categories in dependencies.items():
        print(f"\nChecking dependencies for {module}:")
        
        for category, deps in categories.items():
            print(f"\n{category}:")
            for dep_name, dep_package in deps.items():
                try:
                    if category == "Python packages":
                        __import__(dep_package)
                    elif category == "System dependencies":
                        if dep_package == "ffplay":
                            import shutil
                            if not shutil.which("ffplay"):
                                raise FileNotFoundError
                    print(f"[OK] {dep_name}: {dep_package}")
                except ImportError:
                    print(f"[FAIL] {dep_name}: {dep_package}")
                    all_satisfied = False
                except FileNotFoundError:
                    print(f"[FAIL] {dep_name}: {dep_package}")
                    all_satisfied = False

    if all_satisfied:
        print("\n[OK] All dependencies are satisfied!")
        logger.info("All dependencies are satisfied")
    else:
        print("\n[FAIL] Some dependencies are missing!")
        logger.error("Some dependencies are missing")
        
    return all_satisfied

def main():
    """Main application entry point"""
    logger.info("Starting the application setup process...")
    
    # Check dependencies
    logger.info("Running dependency check...")
    if not check_dependencies():
        logger.error("Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Start the application
    logger.info("All dependencies are satisfied. Starting the main application...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
