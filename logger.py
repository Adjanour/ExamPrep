import logging
import os
from datetime import datetime

class CustomLogger:
    def __init__(self, log_file="app.log"):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create a custom logger
        self.logger = logging.getLogger("CustomLogger")
        self.logger.setLevel(logging.DEBUG)
        
        # Create handlers
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatters and add them to handlers
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def debug(self, message):
        self.logger.debug(message)

    def critical(self, message):
        self.logger.critical(message)

# Example usage
logger = CustomLogger(log_file="logs/app.log")

logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.debug("This is a debug message")
logger.critical("This is a critical message")

print(f"Logs have been written to {os.path.abspath('logs/app.log')}")
