import logging
import re

class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;2;79;195;205m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    green = '\x1b[38;5;40m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
            logging.NOTSET: self.fmt,
        }
        # Regex pattern to identify success messages
        self.success_pattern = re.compile(r'success|successfully', re.IGNORECASE)

    def format(self, record):
        message = record.getMessage()
        
        if record.levelno == logging.INFO and self.success_pattern.search(message):
            log_fmt = self.green + self.fmt + self.reset
        else:
            log_fmt = self.FORMATS.get(record.levelno)
            
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)