"""
Project structure and dependency checker for AI-Chat-App
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .dependency_checker import check_module, check_command

# Define required project structure
PROJECT_STRUCTURE = {
    'root': {
        'required_files': {
            'main.py': 'Main application entry point',
            'requirements.txt': 'Python package dependencies',
            'model_config.json': 'AI model configuration',
        },
        'required_dirs': {
            'modules': 'Core application modules',
            'chat_history': 'Directory for saved chat sessions',
        }
    },
    'modules': {
        'required_files': {
            '__init__.py': 'Package initialization',
            'speech_module.py': 'Speech synthesis and recognition',
            'chat_history.py': 'Chat history management',
            'logger_config.py': 'Logging configuration',
            'model_config.py': 'Model configuration handler',
            'shortcut_manager.py': 'Keyboard shortcuts manager',
            'tab_manager.py': 'Tab interface manager',
            'theme_manager.py': 'UI theme management',
        }
    }
}

# Define required system dependencies
SYSTEM_DEPENDENCIES = {
    'ollama': 'Ollama AI model runner',
    'ffplay': 'FFmpeg audio playback (for TTS)',
}

class ProjectChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.missing_files: List[Tuple[str, str]] = []
        self.missing_dirs: List[Tuple[str, str]] = []
        self.missing_packages: List[Tuple[str, str]] = []
        self.missing_system_deps: List[Tuple[str, str]] = []
        self.warnings: List[str] = []

    def check_directory_structure(self) -> bool:
        """Check if all required directories exist"""
        all_ok = True
        
        # Check root directory requirements
        for dirname, description in PROJECT_STRUCTURE['root']['required_dirs'].items():
            dir_path = self.project_root / dirname
            if not dir_path.is_dir():
                self.missing_dirs.append((dirname, description))
                all_ok = False

        return all_ok

    def check_file_structure(self) -> bool:
        """Check if all required files exist"""
        all_ok = True

        # Check root directory files
        for filename, description in PROJECT_STRUCTURE['root']['required_files'].items():
            file_path = self.project_root / filename
            if not file_path.is_file():
                self.missing_files.append((filename, description))
                all_ok = False

        # Check modules directory files
        modules_dir = self.project_root / 'modules'
        if modules_dir.is_dir():
            for filename, description in PROJECT_STRUCTURE['modules']['required_files'].items():
                file_path = modules_dir / filename
                if not file_path.is_file():
                    self.missing_files.append((f"modules/{filename}", description))
                    all_ok = False

        return all_ok

    def check_python_packages(self) -> bool:
        """Check required Python packages from requirements.txt"""
        all_ok = True
        req_file = self.project_root / 'requirements.txt'
        
        if not req_file.is_file():
            self.warnings.append("requirements.txt not found, skipping package checks")
            return False

        try:
            with open(req_file, 'r') as f:
                requirements = [
                    line.strip().split('>=')[0].split('==')[0]
                    for line in f.readlines()
                    if line.strip() and not line.startswith('#')
                ]

            for package in requirements:
                if not check_module(package):
                    self.missing_packages.append((package, f"Required by requirements.txt"))
                    all_ok = False

        except Exception as e:
            self.warnings.append(f"Error reading requirements.txt: {str(e)}")
            return False

        return all_ok

    def check_system_dependencies(self) -> bool:
        """Check required system dependencies"""
        all_ok = True
        
        for cmd, description in SYSTEM_DEPENDENCIES.items():
            if not check_command(cmd):
                self.missing_system_deps.append((cmd, description))
                all_ok = False

        return all_ok

    def check_all(self, verbose: bool = True) -> bool:
        """
        Check everything: directories, files, packages, and system dependencies
        
        Returns:
            bool: True if all checks pass
        """
        if verbose:
            print("Checking project structure and dependencies...")

        dir_ok = self.check_directory_structure()
        file_ok = self.check_file_structure()
        pkg_ok = self.check_python_packages()
        sys_ok = self.check_system_dependencies()

        if verbose:
            self._print_report()

        return dir_ok and file_ok and pkg_ok and sys_ok

    def fix_project_structure(self, verbose: bool = True) -> bool:
        """
        Try to fix project structure issues
        
        Returns:
            bool: True if all fixes were successful
        """
        if verbose:
            print("Attempting to fix project structure...")

        all_ok = True

        # Create missing directories
        for dirname, _ in self.missing_dirs:
            try:
                (self.project_root / dirname).mkdir(parents=True, exist_ok=True)
                if verbose:
                    print(f"✅ Created directory: {dirname}")
            except Exception as e:
                if verbose:
                    print(f"❌ Failed to create directory {dirname}: {str(e)}")
                all_ok = False

        # Create missing files with templates
        for filepath, _ in self.missing_files:
            try:
                file = self.project_root / filepath
                file.parent.mkdir(parents=True, exist_ok=True)
                
                if filepath == "requirements.txt":
                    template = self._get_requirements_template()
                elif filepath == "model_config.json":
                    template = self._get_model_config_template()
                elif filepath.endswith("__init__.py"):
                    template = '"""Package initialization"""\n'
                else:
                    template = f'"""Module: {filepath}"""\n'
                
                with open(file, 'w') as f:
                    f.write(template)
                
                if verbose:
                    print(f"✅ Created file: {filepath}")
            except Exception as e:
                if verbose:
                    print(f"❌ Failed to create file {filepath}: {str(e)}")
                all_ok = False

        return all_ok

    def _get_requirements_template(self) -> str:
        """Get template for requirements.txt"""
        return """# Core dependencies
PyQt6>=6.4.0
numpy>=1.24.0

# Speech synthesis and recognition
TTS>=0.17.6
pyttsx3>=2.90
openai-whisper>=20231117
sounddevice>=0.4.6
"""

    def _get_model_config_template(self) -> str:
        """Get template for model_config.json"""
        return """{
    "models": {
        "deepseek-coder:6.7b": {
            "name": "DeepSeek Coder 6.7B",
            "description": "Code generation and analysis model",
            "context_length": 8192,
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0
            }
        }
    }
}"""

    def _print_report(self):
        """Print detailed check results"""
        print("\nProject Structure Check Report")
        print("=============================")

        if self.missing_dirs:
            print("\nMissing Directories:")
            for dirname, desc in self.missing_dirs:
                print(f"❌ {dirname}: {desc}")
        
        if self.missing_files:
            print("\nMissing Files:")
            for filename, desc in self.missing_files:
                print(f"❌ {filename}: {desc}")
        
        if self.missing_packages:
            print("\nMissing Python Packages:")
            for package, desc in self.missing_packages:
                print(f"❌ {package}: {desc}")
                print(f"   To install: pip install {package}")
        
        if self.missing_system_deps:
            print("\nMissing System Dependencies:")
            for dep, desc in self.missing_system_deps:
                print(f"❌ {dep}: {desc}")
                if dep == 'ollama':
                    print("   Install from: https://ollama.ai")
                elif dep == 'ffplay':
                    print("   Install FFmpeg from: https://ffmpeg.org/download.html")
                    print("   Make sure to add it to your system PATH")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"⚠️ {warning}")

        if not any([self.missing_dirs, self.missing_files, self.missing_packages, 
                   self.missing_system_deps, self.warnings]):
            print("\n✅ All checks passed! Project structure is complete.")
        else:
            print("\n❌ Some checks failed. Run with --fix to attempt automatic fixes.")

def check_project(project_root: str = None, verbose: bool = True, fix: bool = False) -> bool:
    """
    Check project structure and dependencies
    
    Args:
        project_root: Path to project root directory
        verbose: Whether to print status messages
        fix: Whether to attempt fixing issues
    
    Returns:
        bool: True if all checks pass (after fixes if fix=True)
    """
    if project_root is None:
        project_root = os.getcwd()

    checker = ProjectChecker(project_root)
    checks_ok = checker.check_all(verbose=verbose)

    if not checks_ok and fix:
        if verbose:
            print("\nAttempting to fix issues...")
        checker.fix_project_structure(verbose=verbose)
        # Recheck after fixes
        checks_ok = checker.check_all(verbose=verbose)

    return checks_ok

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Check AI-Chat-App project structure')
    parser.add_argument('--path', help='Path to project root')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    parser.add_argument('--fix', action='store_true', help='Try to fix issues')
    
    args = parser.parse_args()
    sys.exit(0 if check_project(args.path, not args.quiet, args.fix) else 1)