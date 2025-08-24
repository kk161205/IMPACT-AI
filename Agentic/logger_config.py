import logging
import os
from logging.handlers import RotatingFileHandler

# Optional: Use colorlog for colored console output
try:
    from colorlog import ColoredFormatter
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set lowest level to capture all logs

    # Formatter for file logs
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Formatter for console logs (colored if available)
    if COLORLOG_AVAILABLE:
        console_formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s | %(white)s%(message)s",
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            }
        )
    else:
        console_formatter = logging.Formatter('%(levelname)-8s | %(message)s')

    # File handler (rotating logs)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{name}.log"), maxBytes=1_000_000, backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger