"""
Logging configuration for the Pexels downloader
"""
import os
import sys
from loguru import logger
from . import config

def setup_logger():
    """Configure logging for the application"""
    # Remove default logger
    logger.remove()
    
    # Create logs directory
    logs_dir = os.path.join(config.BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Configure file logging for all logs
    logger.add(
        os.path.join(logs_dir, "pexels_{time:YYYY-MM-DD}.log"),
        rotation="00:00",  # Create new file at midnight
        retention="30 days",  # Keep logs for 30 days
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    # Configure file logging for errors only
    logger.add(
        os.path.join(logs_dir, "errors_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        level="ERROR",
        backtrace=True,
        diagnose=True
    )
    
    # Configure file logging for failed downloads
    logger.add(
        os.path.join(logs_dir, "failed_downloads_{time:YYYY-MM-DD}.log"),
        rotation="00:00",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: "FAILED_DOWNLOAD" in record["extra"],
        level="INFO"
    )

def log_failed_download(url, category, error):
    """Log failed downloads with context"""
    logger.bind(FAILED_DOWNLOAD=True).info(
        f"URL: {url} | Category: {category} | Error: {str(error)}"
    )
