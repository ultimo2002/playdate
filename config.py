import requests

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