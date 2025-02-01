"""
Enhanced Portable Dependency Checker
"""
import sys
import subprocess
import importlib.util
import shutil
import json
import os
import venv
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from requirements_manager import RequirementsManager
from installers import DependencyInstaller

class DependencyChecker:
    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = settings_path
        self.settings = self.load_settings()
        self.root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.requirements_manager = RequirementsManager()
        self.installer = DependencyInstaller(settings_path)

# Define module dependencies
def load_module_dependencies() -> Dict:
    """Load module dependencies from a JSON file."""
    with open('portable/module_dependencies.json', 'r') as f:
        return json.load(f)

MODULE_DEPENDENCIES = load_module_dependencies()

def check_module(module_name: str) -> bool:
    """Check if a Python module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def check_command(command: str) -> bool:
    """Check if a command is available in PATH"""
    return shutil.which(command) is not None

from typing import Optional

def get_missing_dependencies(module_name: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Get a list of missing dependencies for a specific module or all modules

    Returns:
        Dict with keys 'packages' and 'commands' containing lists of missing dependencies
    """
    missing = {'packages': [], 'commands': []}

    if module_name:
        if module_name not in MODULE_DEPENDENCIES:
            print(f"Warning: No dependency information for module '{module_name}'")
            return missing
        modules_to_check = {module_name: MODULE_DEPENDENCIES[module_name]}
    else:
        modules_to_check = MODULE_DEPENDENCIES

    for mod_name, deps in modules_to_check.items():
        # Check packages
        for package in deps.get('packages', {}):
            if not check_module(package):
                missing['packages'].append(package)

        # Check commands
        for command in deps.get('commands', {}):
            if not check_command(command):
                missing['commands'].append(command)

    return missing

def check_venv_exists() -> bool:
    """Check if a virtual environment exists in the root directory."""
    return os.path.exists('venv') or os.path.exists('env')

def install_missing_packages(missing: Dict[str, List[str]]):
    """Install missing packages in the virtual environment if it exists."""
    if check_venv_exists():
        for package in missing['packages']:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package])
    else:
        print("No virtual environment found. Please create one and install the packages manually.")

def check_all_dependencies(module_name: Optional[str] = None, verbose: bool = True) -> bool:
    """
    Check all dependencies for a specific module or all modules

    Args:
        module_name: Optional name of specific module to check
        verbose: Whether to print status messages

    Returns:
        bool: True if all dependencies are satisfied
    """
    # Fix console encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if verbose:
        print("Checking dependencies...")

    if module_name:
        if module_name not in MODULE_DEPENDENCIES:
            if verbose:
                print(f"Warning: No dependency information for module '{module_name}'")
            return True
        modules_to_check = {module_name: MODULE_DEPENDENCIES[module_name]}
    else:
        modules_to_check = MODULE_DEPENDENCIES

    all_ok = True

    for mod_name, deps in modules_to_check.items():
        if verbose:
            print(f"\nChecking dependencies for {mod_name}:")

        # Check packages
        if verbose:
            print("\nPython packages:")
        for package, description in deps.get('packages', {}).items():
            if check_module(package):
                if verbose:
                    print(f"[OK] {description}: {package}")
            else:
                if verbose:
                    print(f"[X] {description}: {package}")
                    print(f"   To install: pip install {package}")
                all_ok = False

        # Check commands
        commands = deps.get('commands', {})
        if commands and verbose:
            print("\nSystem dependencies:")
        for command, description in commands.items():
            if check_command(command):
                if verbose:
                    print(f"[OK] {description}: {command}")
            else:
                if verbose:
                    print(f"[X] {description}: {command}")
                    if command == 'ffplay':
                        print("   Download FFmpeg from: https://ffmpeg.org/download.html")
                        print("   Make sure to add it to your system PATH")
                all_ok = False

    if verbose:
        if all_ok:
            print("\n[OK] All dependencies are satisfied!")
        else:
            print("\n[X] Some dependencies are missing. Please install them and try again.")

    return all_ok

def check_pip_installed() -> bool:
    """Check if pip is installed."""
    return subprocess.call([sys.executable, '-m', 'pip', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def install_pip():
    """Install pip using get-pip.py."""
    print("pip is not installed. Installing pip...")
    subprocess.run([sys.executable, 'portable/get-pip.py'])

def automated_scan():
    # Check if pip is installed
    if not check_pip_installed():
        install_pip()
    """Automate the dependency scanning process."""
    missing = get_missing_dependencies()

    if missing['packages'] or missing['commands']:
        print("\nMissing dependencies found:")
        if missing['packages']:
            print("Packages:")
            for package in missing['packages']:
                print(f" - {package}")
        if missing['commands']:
            print("Commands:")
            for command in missing['commands']:
                print(f" - {command}")

        use_venv = check_venv_exists()
        if use_venv:
            print("\nYou are currently using a virtual environment.")
            print("It is recommended to install packages in the virtual environment to avoid conflicts.")
        else:
            print("\nYou are not using a virtual environment.")
            print("Using a virtual environment is recommended to manage dependencies separately.")

        install_choice = input("Do you want to create a dedicated virtual environment for this project? (y/n): ").strip().lower()
        if install_choice == 'y':
            print("Creating a virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'])
            print("Virtual environment created. Activating it...")
            activate_script = 'venv\\Scripts\\activate' if os.name == 'nt' else 'venv/bin/activate'
            print(f"Run '{activate_script}' to activate the virtual environment.")

        install_choice = input("Do you want to install the missing packages? (y/n): ").strip().lower()
        if install_choice == 'y':
            install_missing_packages(missing)
    else:
        print("[OK] All dependencies are satisfied!")

if __name__ == "__main__":
    automated_scan()
    # If run directly, check all dependencies
    sys.exit(0 if check_all_dependencies() else 1)
