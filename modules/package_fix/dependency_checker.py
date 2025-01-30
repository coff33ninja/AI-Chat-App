"""
Dependency checker for AI-Chat-App modules
"""
import sys
import subprocess
import importlib.util
import shutil
from typing import Dict, List, Tuple
import json
import os
from pathlib import Path

# Define module dependencies
MODULE_DEPENDENCIES = {
    'speech_module': {
        'packages': {
            'TTS': 'Text-to-Speech (Coqui TTS)',
            'pyttsx3': 'Text-to-Speech (System)',
            'whisper': 'Speech-to-Text (OpenAI Whisper)',
            'sounddevice': 'Audio recording',
            'numpy': 'Numerical computations',
            'PyQt6': 'GUI framework'
        },
        'commands': {
            'ffplay': 'FFmpeg audio playback'
        }
    },
    'chat_history': {
        'packages': {
            'json': 'JSON handling',
            'datetime': 'Date and time handling'
        }
    },
    'model_config': {
        'packages': {
            'json': 'JSON handling',
            'typing': 'Type hints'
        }
    },
    'shortcut_manager': {
        'packages': {
            'PyQt6': 'GUI framework'
        }
    },
    'tab_manager': {
        'packages': {
            'PyQt6': 'GUI framework'
        }
    },
    'theme_manager': {
        'packages': {
            'PyQt6': 'GUI framework',
            'json': 'JSON handling'
        }
    }
}

def check_module(module_name: str) -> bool:
    """Check if a Python module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def check_command(command: str) -> bool:
    """Check if a command is available in PATH"""
    return shutil.which(command) is not None

def get_missing_dependencies(module_name: str = None) -> Dict[str, List[str]]:
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

def check_all_dependencies(module_name: str = None, verbose: bool = True) -> bool:
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
        sys.stdout.reconfigure(encoding='utf-8')
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
                    print(f"✅ {description}: {package}")
            else:
                if verbose:
                    print(f"❌ {description}: {package}")
                    print(f"   To install: pip install {package}")
                all_ok = False
        
        # Check commands
        commands = deps.get('commands', {})
        if commands and verbose:
            print("\nSystem dependencies:")
        for command, description in commands.items():
            if check_command(command):
                if verbose:
                    print(f"✅ {description}: {command}")
            else:
                if verbose:
                    print(f"❌ {description}: {command}")
                    if command == 'ffplay':
                        print("   Download FFmpeg from: https://ffmpeg.org/download.html")
                        print("   Make sure to add it to your system PATH")
                all_ok = False
    
    if verbose:
        if all_ok:
            print("\n✅ All dependencies are satisfied!")
        else:
            print("\n❌ Some dependencies are missing. Please install them and try again.")
    
    return all_ok

if __name__ == "__main__":
    # If run directly, check all dependencies
    sys.exit(0 if check_all_dependencies() else 1)