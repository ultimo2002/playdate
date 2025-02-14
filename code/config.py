import os
import sys

import requests

API_HOST_URL = '0.0.0.0'
API_HOST_PORT = 8000

STEAMAPI_BASE_URL = 'https://api.steampowered.com/'
STEAMSTORE_BASE_URL = 'https://store.steampowered.com/api/'

APPS_LIST_CACHE_FILE = 'cache/apps_list.json'
ADDED_GAMES_LIST_CACHE_FILE = 'cache/added_games_list.txt'
CACHE_EXPIRATION_TIME = 604800  # Time in seconds (604800 seconds = 1 week)
IMAGE_CACHE_PATH = "code/static/cache"

BLOCKED_CONTENT_TAGS = ["NSFW", "Nudity", "Mature", "Sexual Content", "Hentai"]

DB_CONFIG = {
    "DB_USER": None,
    "DB_PASSWORD": None,
    "DB_NAME": None,
    "DB_HOST": None,
    "DB_PORT": None,
}

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

def load_env():
    """Load environment variables from the .env file."""
    # Read the .env file and process lines
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.split("=", 1)
                os.environ[key] = value

                # Update DB_CONFIG if necessary
                if key in DB_CONFIG:
                    DB_CONFIG[key] = value

                # Handle specific environment variables
                handle_specific_env_vars(key, value)

    # Docker-specific adjustments (Linux platform)
    if sys.platform.startswith("linux"):
        print('Detected Linux platform (possibly Docker). Setting API_HOST_URL to "0.0.0.0".')
        global API_HOST_URL
        API_HOST_URL = "0.0.0.0"
        configure_docker_network()

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

def configure_docker_network():
    """Configure Docker network settings."""
    network_url = os.getenv("NETWORK_URL")
    if network_url:
        print(f"Detected NETWORK_URL, setting DB_HOST to {network_url}")
        DB_CONFIG["DB_HOST"] = network_url

def set_cache_images():
    """Set cache images from the environment."""
    cache_env = os.getenv("CACHE_IMAGES")
    if cache_env:
        caching = cache_env.strip().lower()[0] in ("t", "1", "y")
        os.environ["CACHE_IMAGES"] = str(caching).lower() if caching else ""
        print(f"CACHE_IMAGES set to {caching}")