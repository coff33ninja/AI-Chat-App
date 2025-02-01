import sys
import platform
import subprocess
import importlib.util
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from modules.logger_helper import get_module_logger

# Initialize module logger
logger = get_module_logger(__name__)

class ModuleChecker:
    """Class to check dependencies for a specific module"""

    def __init__(self, module_name: str, required_packages: Dict[str, str],
                 system_commands: Optional[List[str]] = None,
                 additional_instructions: Optional[Dict[str, str]] = None):
        self.module_name = module_name
        self.required_packages = required_packages
        self.system_commands = system_commands or []
        self.additional_instructions = additional_instructions or {}
        self.missing_dependencies = []
        self.installation_instructions = []
        logger.info(f"Initializing dependency checker for {module_name}")

    def check_module(self, module_name: str) -> bool:
        """Check if a Python module is installed"""
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                logger.warning(f"Module {module_name} is not installed")
                return False
            logger.debug(f"Module {module_name} is installed")
            return True
        except Exception as e:
            logger.error(f"Error checking module {module_name}: {str(e)}")
            return False

    def check_command(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            if shutil.which(command) is None:
                logger.warning(f"Command {command} not found in PATH")
                return False
            logger.debug(f"Command {command} is available")
            return True
        except Exception as e:
            logger.error(f"Error checking command {command}: {str(e)}")
            return False

    def check(self) -> bool:
        """Check all dependencies for this module"""
        print(f"\nChecking dependencies for {self.module_name}:")
        all_ok = True

        # Check Python packages
        print("\nRequired Python packages:")
        for package, description in self.required_packages.items():
            print(f"\nChecking {description}:")
            if not self.check_module(package):
                all_ok = False
                print(f"To install: pip install {package}")
                if package in self.additional_instructions:
                    print(self.additional_instructions[package])

        # Check system commands
        if self.system_commands:
            print("\nRequired system commands:")
            for command in self.system_commands:
                if not self.check_command(command):
                    all_ok = False
                    if command in self.additional_instructions:
                        print(self.additional_instructions[command])

        return all_ok


    def check_system_dependencies(self):
        """Check system-level dependencies"""
        if platform.system() == "Windows":
            # Check for Visual C++ Redistributable
            try:
                import ctypes

                ctypes.CDLL("vcruntime140.dll")
                logger.info("Microsoft Visual C++ Redistributable is installed")
            except OSError:
                logger.warning("Microsoft Visual C++ Redistributable is missing")
                self.missing_dependencies.append("Microsoft Visual C++ Redistributable")
                # Provide installation instructions
                self.installation_instructions.append(
                    "Please install Microsoft Visual C++ Redistributable from: "
                    "https://aka.ms/vs/17/release/vc_redist.x64.exe"
                )
        else:
            # Check for ffmpeg
            try:
                subprocess.run(["ffplay", "-version"], check=True)
                logger.info("ffmpeg is installed")
            except subprocess.CalledProcessError:
                logger.warning("ffmpeg is missing")
                self.missing_dependencies.append("ffmpeg")
                # Provide installation instructions
                self.installation_instructions.append(
                    "Please install ffmpeg from: https://ffmpeg.org/download.html"
                    )
                return self.missing_dependencies, self.installation_instructions


def check_all_dependencies() -> bool:
    """Check dependencies for all modules"""
    checkers = [
        # Speech Module Dependencies
        ModuleChecker(
            "speech_module",
            {
                'TTS': 'Text-to-Speech (Coqui TTS)',
                'pyttsx3': 'Text-to-Speech (System)',
                'whisper': 'Speech-to-Text (OpenAI Whisper)',
                'sounddevice': 'Audio recording',
                'numpy': 'Numerical computations'
            },
            system_commands=['ffplay'],
            additional_instructions={
                'TTS': 'Note: This is a large package and may take a while to install',
                'whisper': 'Note: This is a large package and may take a while to install',
                'ffplay': 'Download FFmpeg from: https://ffmpeg.org/download.html\nMake sure to add it to your system PATH'
            }
        ),

        # GUI Dependencies
        ModuleChecker(
            "gui",
            {
                'PyQt6': 'GUI framework'
            }
        ),

        # Model Config Dependencies
        ModuleChecker(
            "model_config",
            {
                'json': 'JSON handling',
                'typing': 'Type hints'
            }
        ),

        # Logger Dependencies
        ModuleChecker(
            "logger_config",
            {
                'logging': 'Logging framework'
            }
        ),

        # Theme Manager Dependencies
        ModuleChecker(
            "theme_manager",
            {
                'PyQt6': 'GUI framework',
                'json': 'JSON handling'
            }
        ),

        # Tab Manager Dependencies
        ModuleChecker(
            "tab_manager",
            {
                'PyQt6': 'GUI framework'
            }
        ),

        # Shortcut Manager Dependencies
        ModuleChecker(
            "shortcut_manager",
            {
                'PyQt6': 'GUI framework'
            }
        )
    ]

    all_ok = True
    for checker in checkers:
        if not checker.check():
            all_ok = False

    if all_ok:
        print("\n✅ All dependencies are installed!")
    else:
        print("\n❌ Some dependencies are missing. Please install them and try again.")

    return all_ok

def main():
    """Main entry point for dependency checking"""
    success = check_all_dependencies()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
