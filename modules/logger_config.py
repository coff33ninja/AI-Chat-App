import logging
import logging.handlers
import os
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""

    COLORS = {
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[0;35m",  # Purple
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        if not hasattr(record, "color"):
            record.color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            record.reset = self.COLORS["RESET"]
        return super().format(record)


def setup_logging(app_name="AI-Chat-App"):
    """Setup application-wide logging configuration"""

    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Generate log filename with timestamp
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, f"{app_name}_{current_time}.log")

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = CustomFormatter(
        "%(color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s"
    )

    # Create handlers
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Create loggers for different components
    loggers = {
        "main": logging.getLogger("main"),
        "ai": logging.getLogger("ai"),
        "tts": logging.getLogger("tts"),
        "stt": logging.getLogger("stt"),
        "ui": logging.getLogger("ui"),
    }

    # Set levels for component loggers
    for logger in loggers.values():
        logger.setLevel(logging.DEBUG)

    return loggers
