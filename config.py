
import os

import requests

API_HOST_URL = '0.0.0.0'

API_HOST_PORT = 8000

STEAMAPI_BASE_URL = 'https://api.steampowered.com/'
STEAMSTORE_BASE_URL = 'https://store.steampowered.com/api/'

APPS_LIST_CACHE_FILE = 'cache/apps_list.json'

ADDED_GAMES_LIST_CACHE_FILE = 'cache/added_games_list.txt'

CACHE_EXPIRATION_TIME = 604800  # Time in seconds (604800 seconds = 1 week)

def fetch_from_api(endpoint):
    """Make a GET request to the specified API endpoint and return the JSON data.
    :return: JSON data from the API, Exit when an error occurs.
    """
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except Exception:
        print("Error fetching data from the API. Is your internet connection working?")
        # exit("Exiting the application.")

    return None

class TextStyles:
    """Text styles for the console."""
    red = "\u001b[0;31m"
    green = "\u001b[0;32m"
    yellow = "\u001b[0;33m"
    blue = "\u001b[0;34m"
    magenta = "\u001b[0;35m"
    cyan = "\u001b[0;36m"
    white = "\u001b[0;37m"
    grey = "\u001b[0;90m"
    underline = "\u001b[4m"
    bold = "\u001b[1m"
    inverse = "\u001b[7m"
    reset = "\u001b[0m"


import sys
import subprocess
import traceback

def get_git_author(filename, lineno):
    """Try to get the author of a specific line using `git blame`.
    :return: Author name if successful, otherwise an empty string.
    """
    try:
        git_blame_output = subprocess.check_output(
            ["git", "blame", f"-L{lineno},{lineno}", filename],
            stderr=subprocess.DEVNULL,
            text=True
        )
        return git_blame_output.split('(')[1].split()[0]  # Extract author name
    except Exception:
        return ''  # If blame fails, return empty string


def womp_exception_hook(exc_type, exc_value, exc_traceback):
    """Custom exception hook to add womp womp and the git author name from the error causing code."""
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)

    # Extract the last traceback entry (filename + line number)
    last_call = traceback.extract_tb(exc_traceback)[-1]
    filename = last_call.filename
    lineno = last_call.lineno

    # Try to get the author of the error line
    author = get_git_author(filename, lineno)

    # Print original traceback except last line
    sys.stderr.write("".join(tb[:-1]))

    if author:
        sys.stderr.write(f"Womp womp skill issue, from: {author}. {tb[-1]}")
    else:
        sys.stderr.write(f"Womp womp, error: {tb[-1]}")

def set_womp_exception(enabled):
    """Enable or disable the custom womp womp exception hook."""
    if enabled:
        sys.excepthook = womp_exception_hook
    else:
        sys.excepthook = sys.__excepthook__


def load_env():
    """Load environment variables from the .env file."""
    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
                # update DB_CONFIG
                if key in DB_CONFIG:
                    DB_CONFIG[key] = value

DB_CONFIG = {
    "DB_USER": None,
    "DB_PASSWORD": None,
    "DB_NAME": None,
    "DB_HOST": None,
    "DB_PORT": None,
}


# Set the custom exception hook
set_womp_exception(True)

# Only execute this code when this script is run directly, not when it's imported
# We don't want ZeroDivisionError when this file is imported
if __name__ == "__main__":
    print(1 / 0)  # This will trigger a ZeroDivisionError