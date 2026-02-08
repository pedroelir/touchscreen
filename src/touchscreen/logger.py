import logging
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Generate log filename with timestamp
LOG_FILENAME = LOGS_DIR / f"touchscreen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logger
logger = logging.getLogger("touchUI")
logger.setLevel(logging.DEBUG)

# Console handler with format: [LEVEL] - [python module] [line number] - message
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("[%(levelname)s] - [%(module)s:%(lineno)d] - %(message)s")
console_handler.setFormatter(console_formatter)

# File handler with format: [timestamp] [LEVEL] - [python module] [line number] - message
file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] - [%(module)s:%(lineno)d] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)

# Add handlers to logger
# logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Global logger instance
__all__ = ["logger"]
