# logger_config.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """
    Creates a logger with the specified name and log file using RotatingFileHandler.

    Args:
        name (str): Name of the logger.
        log_file (str): File path for the log file.
        level (int): Logging level.

    Returns:
        Logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent logging messages from being propagated to the root logger
    logger.propagate = False

    # Create handlers
    # Removed StreamHandler to prevent console logging
    f_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)  # 5 MB per file
    f_handler.setLevel(level)

    # Create formatters and add them to handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    if not logger.hasHandlers():
        logger.addHandler(f_handler)

    return logger

