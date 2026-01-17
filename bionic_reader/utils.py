import logging
import sys

def setup_logging(verbose: bool = False):
    """
    Configure logging for the application.
    
    Args:
        verbose (bool): If True, set log level to DEBUG, else INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logger
    logger = logging.getLogger("bionic_reader")
    logger.setLevel(level)
    
    # Create console handler and set level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to ch
    ch.setFormatter(formatter)
    
    # Add ch to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger

def get_logger():
    """Get the bionic_reader logger."""
    return logging.getLogger("bionic_reader")
