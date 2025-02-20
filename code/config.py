import os
import sys

import requests
from dotenv import load_dotenv

API_HOST_URL = '0.0.0.0'
API_HOST_PORT = 8000

STEAMAPI_BASE_URL = 'https://api.steampowered.com/'
STEAMSTORE_BASE_URL = 'https://store.steampowered.com/api/'

APPS_LIST_CACHE_FILE = 'cache/apps_list.json'
ADDED_GAMES_LIST_CACHE_FILE = 'cache/added_games_list.txt'
CACHE_EXPIRATION_TIME = 604800  # Time in seconds (604800 seconds = 1 week)
IMAGE_CACHE_PATH = "code/static/cache"

BLOCKED_CONTENT_TAGS = ["NSFW", "Nudity", "Mature", "Sexual Content", "Hentai"]


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
    pink = "\u001b[0;95m"
    underline = "\u001b[4m"
    bold = "\u001b[1m"
    inverse = "\u001b[7m"
    reset = "\u001b[0m"

def set_host():
    # Docker-specific adjustments (Linux platform)
    if sys.platform.startswith("linux"):
        print('Detected Linux platform (possibly Docker). Setting API_HOST_URL to "0.0.0.0".')
        global API_HOST_URL
        API_HOST_URL = "0.0.0.0"

    # Cache images from environment
    set_cache_images()

def handle_specific_env_vars(key, value):
    """Handle specific environment variables with custom logic."""
    global API_HOST_URL, API_HOST_PORT
    if key == "API_HOST_URL":
        API_HOST_URL = value
    elif key == "API_HOST_PORT":
        try:
            API_HOST_PORT = int(value)
        except ValueError:
            print(f"Invalid API_HOST_PORT value. Using default port 8000.")
            API_HOST_PORT = 8000

def set_cache_images():
    """Set cache images from the environment."""
    cache_env = os.getenv("CACHE_IMAGES")
    if cache_env:
        caching = cache_env.strip().lower()[0] in ("t", "1", "y")
        os.environ["CACHE_IMAGES"] = str(caching).lower() if caching else ""
        print(f"CACHE_IMAGES set to {caching}")

load_dotenv()

# loop over the environment variables from the .env file and set them
for key, value in os.environ.items():
    handle_specific_env_vars(key, value)

set_host()