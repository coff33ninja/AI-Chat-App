import logging
import logging.handlers
import subprocess
import sys
import os
from datetime import datetime
from dependency_checker.dependency_checker import automated_scan, check_all_dependencies

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger("run_app")



def main():
    """Main function to run the application with comprehensive dependency checking."""
    try:
        logger.info("Starting the application setup process...")
        
        # Check Python version
        python_version = sys.version_info
        min_version = (3, 10)
        if python_version < min_version:
            logger.error(f"Python {min_version[0]}.{min_version[1]} or higher is required")
            return 1

        logger.info("Running dependency check...")
        
        # Check and install dependencies
        try:
            automated_scan()
        except Exception as e:
            logger.error(f"Failed to run automated dependency scan: {e}")
            return 1

        if not check_all_dependencies():
            logger.error("Required dependencies are not satisfied. Please check the logs for details.")
            return 1

        logger.info("All dependencies are satisfied. Starting the main application...")

        # Run the main application
        result = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Application exited with error: {result.stderr}")
            return 1
            
        return 0

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return 1



if __name__ == "__main__":
    sys.exit(main())
