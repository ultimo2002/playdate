import json
import os

import time

from API_code.config import STEAMAPI_BASE_URL, STEAMSTORE_BASE_URL, fetch_from_api, APPS_LIST_CACHE_FILE, CACHE_EXPIRATION_TIME


def get_app_details(appid):
    """Fetch details for a specific app (game) from the Steam store API."""
    try:
        data = fetch_from_api(f"{STEAMSTORE_BASE_URL}appdetails?appids={appid}")
        if data and data[str(appid)]["success"]:
            return data[str(appid)]["data"]

    except Exception as e:
        print(f"Error fetching details for appid {appid}: {e}")

    return False

def is_cache_valid(cache_file, expiration_time):
    """Check if the cache file is valid based on its timestamp."""
    if os.path.exists(cache_file):
        cache_timestamp = os.path.getmtime(cache_file)
        current_time = time.time()
        return current_time - cache_timestamp < expiration_time
    return False

def load_cache(cache_file):
    """Load data from the cache file."""
    with open(cache_file, 'r') as cache_file_obj:
        print("Loading app list from cache file...")

        loaded_data = json.load(cache_file_obj)

        # Remove all double appids from the list
        app_ids = set()
        loaded_data = [app for app in loaded_data if app["appid"] not in app_ids and not app_ids.add(app["appid"])]

        # order the apps by appid
        loaded_data.sort(key=lambda x: x["appid"])

        return loaded_data

def save_cache(cache_file, data):
    """Save data to the cache file."""
    with open(cache_file, 'w') as cache_file_obj:
        print("Saving app list to cache...")
        json.dump(data, cache_file_obj)


def fetch_app_list():
    """Fetch the list of all the apps (games) from the Steam API."""

    # Ensure cache directory exists
    os.makedirs(os.path.dirname(APPS_LIST_CACHE_FILE), exist_ok=True)

    # Check if cache is valid and return from cache if possible
    if is_cache_valid(APPS_LIST_CACHE_FILE, CACHE_EXPIRATION_TIME):
        return load_cache(APPS_LIST_CACHE_FILE)

    # Fetch the app list from the Steam API
    data = fetch_from_api(f"{STEAMAPI_BASE_URL}ISteamApps/GetAppList/v2/")

    if data:
        save_cache(APPS_LIST_CACHE_FILE, data["applist"]["apps"])

        apps = data["applist"]["apps"]

        # Remove all double appids from the list
        app_ids = set()
        apps = [app for app in apps if app["appid"] not in app_ids and not app_ids.add(app["appid"])]

        # order the apps by appid
        apps.sort(key=lambda x: x["appid"])

        return apps

    return False

def get_app_categories(details):
    """Extract the categories from the app details."""
    if details and details.get("categories"):
        return details["categories"]

    return []

def get_current_player_count(appid):
    """Fetch the current player count for a app (game) from the Steam API."""
    data = fetch_from_api(f"{STEAMAPI_BASE_URL}ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}")

    try:
        if data and data["response"]:
            return int(data["response"]["player_count"])
    except (KeyError, ValueError):
        pass

    return 0

from bs4 import BeautifulSoup
import requests

def get_steam_tags(appid, tries: int = 0):
    if tries >= 5:
        print(f"Too many requests. Skipping tag request for appid: {appid}")
        return None
    elif tries >= 3:
        print(f"Too many requests for appid: {appid}. Waiting for 15 seconds...")
        time.sleep(15)

    session = requests.Session()
    url = f"https://store.steampowered.com/app/{appid}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    headers["Accept-Language"] = "en-US,en;q=0.5"

    # First request to get the session ID and cookies
    response = session.get(url, headers=headers)

    # When visited too many times, Steam will block the request
    if response.status_code == 429:
        print("Too many requests. Waiting for 30 seconds...")
        time.sleep(30)
        tries += 1
        return get_steam_tags(appid, tries)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # when login screen is detected, we skip the request
    if soup.select(".login"):
        print("Login screen detected. Skipping request.")
        return None

    # Check if the age gate exists then we give a age and continue
    if soup.select("#app_agegate"):
        # Extract the session ID from cookies
        session_id = session.cookies.get("sessionid", "")

        print("Age gate detected. Verifying age...")

        age_gate_url = f"https://store.steampowered.com/agecheckset/app/{appid}/"
        payload = {
            "sessionid": session_id,  # Use the session ID from cookies
            "ageDay": 5,
            "ageMonth": "March",
            "ageYear": "1999",
        }

        # Send the age verification request
        session.post(age_gate_url, headers=headers, data=payload)

        response = session.get(url, headers=headers)

        if response.status_code != 200:
            tries += 1
            return get_steam_tags(appid, tries)

    # Parse the updated page
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the "Popular user-defined tags" section
    popular_tags_section = soup.select_one(".popular_tags")
    if not popular_tags_section:
        return None  # Return None if the section isn't found

    tags = [tag.text.strip() for tag in soup.select(".app_tag")[:5]] # Get the first 5 tags

    if not tags:
        tries += 1
        return get_steam_tags(appid, tries)

    return tags


if __name__ == "__main__":
    game_id = 271590  # Example: GTA V
    try:
        tags = get_steam_tags(game_id)
        print(tags)
    except Exception as e:
        print(e)