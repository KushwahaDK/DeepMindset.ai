"""
Logging utilities module

This module sets up logging for the application.
"""
import logging
import os
import sys
from datetime import datetime


def setup_logging(log_level=logging.INFO):
    """
    Set up logging for the application.
    
    Args:
        log_level: The logging level to use (default: INFO)
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Set up filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join("logs", f"deepmindset_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log application start
    logging.info("DeepMindset.ai application started")
    
    return logging.getLogger(__name__) 