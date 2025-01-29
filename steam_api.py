import json
import os

import requests
import time

from config import STEAMAPI_BASE_URL, STEAMSTORE_BASE_URL, fetch_from_api, APPS_LIST_CACHE_FILE, CACHE_EXPIRATION_TIME


def get_app_details(appid):
    """Fetch details for a specific app (game) from the Steam store API."""
    try:
        data = fetch_from_api(f"{STEAMSTORE_BASE_URL}appdetails?appids={appid}")
        if data and data[str(appid)]["success"]:
            return data[str(appid)]["data"]

    except Exception as e:
        print(f"Error fetching details for appid {appid}: {e}")

    return False

def fetch_app_list():
    """Fetch the list of all the apps (games) from the Steam API."""

    # Create the cache directory if it doesn't exist
    os.makedirs(os.path.dirname(APPS_LIST_CACHE_FILE), exist_ok=True)

    # Check if the cache file exists and if it's still valid
    if os.path.exists(APPS_LIST_CACHE_FILE):
        # Get the timestamp of when the cache was saved
        cache_timestamp = os.path.getmtime(APPS_LIST_CACHE_FILE)
        current_time = time.time()

        # If the cache is still valid, return the cached list
        if current_time - cache_timestamp < CACHE_EXPIRATION_TIME:
            with open(APPS_LIST_CACHE_FILE, 'r') as cache_file:
                print("Loading app list from cache file...")
                return json.load(cache_file)

    # Fetch the app list from the Steam API
    data = fetch_from_api(f"{STEAMAPI_BASE_URL}ISteamApps/GetAppList/v2/")

    if data:
        # Save the fetched list to the cache file
        with open(APPS_LIST_CACHE_FILE, 'w') as cache_file:
            print("Saving app list to cache...")
            json.dump(data["applist"]["apps"], cache_file)

        return data["applist"]["apps"]
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

    return False

if __name__ == "__main__":
    # Fetch and process each app
    print("Fetching app list...")
    app_list = fetch_app_list()

    if not app_list or len(app_list) == 0:
        exit("No games found. Exiting the application.")

    for app in app_list:
        appid = app["appid"]
        name = app["name"]

        # when name is empty, skip to the next app
        if not name:
            continue

        print(f"Processing appid {appid}: {name}")
        details = get_app_details(appid)

        if details:
            categories = get_app_categories(details)
            category_names = ", ".join([cat["description"] for cat in categories])

            # Print data instead of saving to database
            print(f"AppID: {appid}, Name: {name}, Categories: {category_names}")

        # player_count = get_current_player_count(appid)
        # if player_count:
        #     print(f"Player count for {name}: {player_count}")

        # Sleep to prevent rate limits
        time.sleep(0.5)

    print("Done fetching app data.")

