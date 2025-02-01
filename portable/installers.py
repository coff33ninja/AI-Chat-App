"""
Enhanced installation utilities for the portable dependency checker
"""
import subprocess
import sys
import os
import platform
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class DependencyInstaller:
    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = settings_path
        self.python_exe = sys.executable
        self.platform = platform.system().lower()

    def fix_console_encoding(self):
        """Fix console encoding for Windows"""
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')

    def install_pip_package(self, package: str, version: Optional[str] = None) -> bool:
        """
        Install a Python package using pip
        
        Args:
            package: Package name
            version: Optional version specification
            
        Returns:
            bool: True if installation was successful
        """
        try:
            cmd = [self.python_exe, "-m", "pip", "install"]
            if version:
                cmd.append(f"{package}{version}")
            else:
                cmd.append(package)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error installing {package}:")
                print(result.stderr)
                return False
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            return False

    def install_from_requirements(self, requirements_file: str) -> bool:
        """
        Install packages from requirements.txt
        
        Returns:
            bool: True if all installations were successful
        """
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "install", "-r", requirements_file],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("Error installing from requirements.txt:")
                print(result.stderr)
                return False
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install from requirements.txt: {e}")
            return False

    def check_system_dependencies(self) -> Dict[str, bool]:
        """
        Check system dependencies like ffplay
        
        Returns:
            Dict[str, bool]: Dictionary of dependencies and their availability
        """
        dependencies = {
            'ffplay': self._check_ffmpeg(),
        }
        return dependencies

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        return shutil.which('ffplay') is not None

    def install_system_dependencies(self) -> Tuple[bool, str]:
        """
        Provide instructions for installing system dependencies
        
        Returns:
            Tuple[bool, str]: Success status and instructions/error message
        """
        missing = []
        instructions = []

        sys_deps = self.check_system_dependencies()
        
        if not sys_deps['ffplay']:
            missing.append('FFmpeg')
            if self.platform == 'windows':
                instructions.extend([
                    "FFmpeg installation instructions:",
                    "1. Download from: https://ffmpeg.org/download.html",
                    "2. Extract the archive",
                    "3. Add the bin folder to your system PATH",
                    "4. Restart your terminal/IDE"
                ])
            elif self.platform == 'darwin':  # macOS
                instructions.extend([
                    "FFmpeg installation instructions:",
                    "1. Install Homebrew if not installed: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
                    "2. Run: brew install ffmpeg"
                ])
            else:  # Linux
                instructions.extend([
                    "FFmpeg installation instructions:",
                    "Ubuntu/Debian: sudo apt-get install ffmpeg",
                    "Fedora: sudo dnf install ffmpeg",
                    "Arch Linux: sudo pacman -S ffmpeg"
                ])

        if missing:
            return False, "\n".join(instructions)
        return True, "All system dependencies are installed."

    def install_all_dependencies(self, requirements_file: str) -> bool:
        """
        Install all dependencies (both Python packages and system dependencies)
        
        Args:
            requirements_file: Path to requirements.txt
            
        Returns:
            bool: True if all installations were successful
        """
        self.fix_console_encoding()
        
        print("Checking system dependencies...")
        sys_ok, sys_msg = self.install_system_dependencies()
        if not sys_ok:
            print("\nSystem dependencies need to be installed:")
            print(sys_msg)
        
        print("\nInstalling Python packages...")
        if not os.path.exists(requirements_file):
            print(f"Error: Requirements file not found: {requirements_file}")
            return False
        
        if not self.install_from_requirements(requirements_file):
            print("Failed to install some Python packages.")
            return False
        
        if not sys_ok:
            print("\nPlease install the system dependencies manually.")
            return False
        
        print("\n✅ All dependencies installed successfully!")
        return True

    def verify_installation(self, package: str) -> bool:
        """
        Verify that a package was installed correctly
        
        Args:
            package: Package name to verify
            
        Returns:
            bool: True if package is installed and importable
        """
        try:
            subprocess.run(
                [self.python_exe, "-c", f"import {package}"],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_installed_version(self, package: str) -> Optional[str]:
        """
        Get the installed version of a package
        
        Args:
            package: Package name
            
        Returns:
            Optional[str]: Version string or None if package is not installed
        """
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "show", package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
            return None
        except subprocess.CalledProcessError:
            return None