"""
Main launcher script for the project
"""
import os
import sys
from pathlib import Path
from dependency_checker import DependencyChecker

def main():
    # Initialize dependency checker
    checker = DependencyChecker()
    
    # Check if this is first run
    if not os.path.exists(checker.settings_path):
        print("Welcome to the Project Launcher!")
        print("Running first-time setup...")
        if not checker.setup_project():
            print("Setup failed. Please check the errors and try again.")
            sys.exit(1)
    
    # Check dependencies
    if checker.settings["dependencies"]["check_on_startup"]:
        print("Checking dependencies...")
        if not checker.check_all_dependencies():
            if checker.settings["dependencies"]["auto_install"]:
                print("Attempting to fix dependencies...")
                if not checker.setup_project():
                    sys.exit(1)
            else:
                print("Dependency issues found. Please run setup to fix them.")
                sys.exit(1)
    
    # Launch the application
    print("Starting application...")
    checker.launch_application()

if __name__ == "__main__":
    main()