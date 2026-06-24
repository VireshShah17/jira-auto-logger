# utils/logger.py
import logging

class ColoredFormatter(logging.Formatter):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"

    # Added time and logger name for better traceability
    BASE_FORMAT = "%(asctime)s - [%(name)s] - %(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: BLUE + BASE_FORMAT + RESET,
        logging.INFO: GREEN + BASE_FORMAT + RESET,
        logging.WARNING: YELLOW + BASE_FORMAT + RESET,
        logging.ERROR: RED + BOLD + BASE_FORMAT + RESET,
        logging.CRITICAL: RED + BOLD + BASE_FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        # Use ISO-like date format
        formatter = logging.Formatter(log_fmt, datefmt = "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def get_logger(name: str, level = logging.INFO):
    """
    Returns a named logger instance configured with the ColoredFormatter.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if handlers already exist to prevent duplicate log outputs
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
        
    # Prevent logs from propagating to the root logger if it has conflicting handlers
    logger.propagate = False
    
    return logger