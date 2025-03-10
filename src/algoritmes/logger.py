import ipaddress
import logging
import re
import sys
import time
from collections import deque

import requests

# Global log buffer (this will collect all logs and intercepted prints)
MAX_LOG_BUFFER_SIZE = 100  # Define the maximum size of the log buffer
LOG_BUFFER = deque(maxlen=MAX_LOG_BUFFER_SIZE)  # A deque will automatically discard the oldest logs when it reaches maxlen

# Custom logging handler that appends each formatted log message to LOG_BUFFER
class BufferHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        LOG_BUFFER.append(log_entry)

# Configure the root logger
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# Define a common formatter (with timestamp and level)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

# 1. Console handler: prints to the terminal (using the original sys.__stdout__)
console_handler = logging.StreamHandler(sys.__stdout__)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 3. Buffer handler: appends logs to LOG_BUFFER (to serve from /logs)
buffer_handler = BufferHandler()
buffer_handler.setLevel(logging.DEBUG)
buffer_handler.setFormatter(formatter)
logger.addHandler(buffer_handler)

# Interceptor for print statements
class StreamInterceptor:
    def __init__(self, stream):
        self.stream = stream

    def write(self, message):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        grey_color_code = "\x1B[90m"
        reset_code = "\x1B[0m"

        message = f"{grey_color_code}{current_time}{reset_code} {message}"

        self.stream.write(message)
        self.stream.flush()
        if message.strip():
            LOG_BUFFER.append(message.strip())

    def flush(self):
        self.stream.flush()

    def isatty(self):
        return self.stream.isatty()

# ANSI Escape Code Pattern (Matches color codes like `[32m`)
ANSI_ESCAPE_PATTERN = re.compile(r'(\x1B\[[0-9;]*m)')

# Color map for ANSI codes
ANSI_COLORS = {
    "30": "black",
    "31": "red",
    "32": "green",
    "33": "yellow",
    "34": "blue",
    "35": "magenta",
    "36": "cyan",
    "37": "white",
    "90": "grey",
    "0": "reset",  # No color
}

def convert_ansi_to_html(text):
    """Converts ANSI color codes to HTML <span> with inline styles."""
    def replace_ansi(match):
        """Replaces ANSI escape codes with corresponding HTML <span> tags."""
        code = match.group(0)[2:-1]  # Remove `\x1B[` and `m`
        color = ANSI_COLORS.get(code, "reset")
        if color == "reset":
            return "</span>"  # Close the previous span when reset code appears
        return f'<span style="color:{color}">'

    # Replace ANSI codes with the corresponding HTML <span> and ensure proper closing
    text = ANSI_ESCAPE_PATTERN.sub(replace_ansi, text)
    # If any `reset` code is left unclosed, we manually close it
    text = text.replace("[0m", "</span>")
    return text

# Override stdout and stderr to intercept print() outputs
sys.stdout = StreamInterceptor(sys.__stdout__)
sys.stderr = StreamInterceptor(sys.__stderr__)