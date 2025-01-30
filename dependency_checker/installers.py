"""
Dependency installation utilities for AI-Chat-App
"""
import subprocess
import sys
import os
from typing import List, Dict
from .dependency_checker import get_missing_dependencies

def install_pip_package(package: str) -> bool:
    """
    Install a Python package using pip
    
    Returns:
        bool: True if installation was successful
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def install_dependencies(module_name: str = None, verbose: bool = True) -> bool:
    """
    Install missing dependencies for a specific module or all modules
    
    Args:
        module_name: Optional name of specific module to check
        verbose: Whether to print status messages
    
    Returns:
        bool: True if all installations were successful
    """
    # Fix console encoding for Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    missing = get_missing_dependencies(module_name)
    all_ok = True
    
    if verbose:
        print("Installing missing dependencies...")
    
    # Install Python packages
    for package in missing['packages']:
        if verbose:
            print(f"\nInstalling {package}...")
        if install_pip_package(package):
            if verbose:
                print(f"✅ Successfully installed {package}")
        else:
            if verbose:
                print(f"❌ Failed to install {package}")
            all_ok = False
    
    # Handle system dependencies
    if missing['commands']:
        if verbose:
            print("\nSystem dependencies that need to be installed manually:")
            if 'ffplay' in missing['commands']:
                print("\nFFmpeg:")
                print("1. Download from: https://ffmpeg.org/download.html")
                print("2. Add to system PATH")
                print("3. Restart your terminal/IDE")
            for cmd in missing['commands']:
                if cmd != 'ffplay':
                    print(f"\n{cmd} is missing and needs to be installed")
        all_ok = False
    
    if verbose:
        if all_ok:
            print("\n✅ All dependencies installed successfully!")
        else:
            print("\n⚠️ Some dependencies need manual installation. See instructions above.")
    
    return all_ok

if __name__ == "__main__":
    # If run directly, install all dependencies
    sys.exit(0 if install_dependencies() else 1)