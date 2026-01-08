"""
Professional logging configuration for ARCA parsers.

This module provides centralized logging configuration with:
- Structured log format with timestamps
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Context-aware logging for different parser modules
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ParserLogger:
    """
    Centralized logger for ARCA parser system.
    
    Provides consistent logging format across all parser modules
    with automatic file output and console display.
    """
    
    def __init__(
        self,
        name: str,
        log_dir: Optional[Path] = None,
        level: int = logging.DEBUG,
        console_output: bool = True
    ):
        """
        Initialize parser logger.
        
        Args:
            name: Logger name (typically module name)
            log_dir: Directory for log files (None = no file output)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Enable console output
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear any existing handlers
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f"{name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            self.logger.info(f"Log file created: {log_file}")
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


def get_logger(name: str, log_dir: Optional[Path] = None) -> ParserLogger:
    """
    Factory function to create parser logger.
    
    Args:
        name: Logger name
        log_dir: Optional directory for log files
    
    Returns:
        Configured ParserLogger instance
    """
    return ParserLogger(name, log_dir)