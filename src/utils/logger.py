"""
Logger Utility - Handles application logging
"""

import os
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(log_dir="logs", level=logging.INFO):
    """Setup application logger"""
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"file_manager_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger for this application
    logger = logging.getLogger('PerfectFileManager')
    logger.setLevel(level)
    
    return logger

def get_logger(name=None):
    """Get a logger instance"""
    if name:
        return logging.getLogger(f'PerfectFileManager.{name}')
    else:
        return logging.getLogger('PerfectFileManager')