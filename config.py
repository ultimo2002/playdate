import requests

import sys
import subprocess
import traceback

STEAMAPI_BASE_URL = 'https://api.steampowered.com/'
STEAMSTORE_BASE_URL = 'https://store.steampowered.com/api/'

def fetch_from_api(endpoint):
    """Make a GET request to the specified API endpoint and return the JSON data.
    :return: JSON data from the API, Exit when an error occurs.
    """
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except Exception:
        print("Error fetching data from the API. Is your internet connection working?")
        exit("Exiting the application.")

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

def get_git_author(filename, lineno):
    """Try to get the author of a specific line using `git blame`."""
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
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)

    # Extract the last traceback entry (filename + line number)
    last_call = traceback.extract_tb(exc_traceback)[-1]
    filename = last_call.filename
    lineno = last_call.lineno

    # Try to get the author of the error line
    author = get_git_author(filename, lineno)
    author = f"{author}" if author else ""

    # Print original traceback except last line
    sys.stderr.write("".join(tb[:-1]))

    if author:
        sys.stderr.write(f"Womp womp skill issue, error from: {author}. {tb[-1]}")
    else:
        sys.stderr.write(f"Womp womp, error: {tb[-1]}")

if __name__ == "__main__":
    # Set the custom exception hook
    sys.excepthook = womp_exception_hook
    # Trigger an error
    print(1 / 0)  # This will trigger a ZeroDivisionError