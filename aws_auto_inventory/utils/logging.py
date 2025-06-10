"""
Logging utilities for AWS Auto Inventory.
"""
import os
import logging
from datetime import datetime
from typing import Optional


def setup_logging(
    log_dir: str, 
    log_level: str = "INFO", 
    log_file_prefix: str = "aws_auto_inventory"
) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_dir: Directory to store log files.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file_prefix: Prefix for log file name.
        
    Returns:
        Configured logger.
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().isoformat(timespec="minutes").replace(":", "-")
    log_filename = f"{log_file_prefix}_{timestamp}.log"
    log_file = os.path.join(log_dir, log_filename)
    
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Get logger for this module
    logger = logging.getLogger("aws_auto_inventory")
    logger.setLevel(numeric_level)
    
    logger.info(f"Logging initialized at level {log_level}")
    logger.info(f"Log file: {log_file}")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name. If None, returns the root logger.
        
    Returns:
        Logger instance.
    """
    if name is None:
        return logging.getLogger("aws_auto_inventory")
    else:
        return logging.getLogger(f"aws_auto_inventory.{name}")