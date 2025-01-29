import requests
import time

from config import STEAMAPI_BASE_URL, STEAMSTORE_BASE_URL, fetch_from_api

def get_app_details(appid):
    """Fetch details for a specific app (game) from the Steam store API."""
    try:
        response = requests.get(f"{STEAMSTORE_BASE_URL}appdetails?appids={appid}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data[str(appid)]["success"]:
            return data[str(appid)]["data"]

    except Exception as e:
        print(f"Error fetching details for appid {appid}: {e}")
    return None

# Function to fetch the app list
def fetch_app_list():
    app_list_response = fetch_from_api(f"{STEAMAPI_BASE_URL}ISteamApps/GetAppList/v2/")
    return app_list_response["applist"]["apps"]


if __name__ == "__main__":
    # Fetch and process each app
    print("Fetching app list...")
    app_list = fetch_app_list()

    for app in app_list:
        appid = app["appid"]
        name = app["name"]

        # when name is empty, skip to the next app
        if not name:
            continue

        print(f"Processing appid {appid}: {name}")
        details = get_app_details(appid)

        if details:
            categories = details.get("categories", [])
            category_names = ", ".join([cat["description"] for cat in categories])

            # Print data instead of saving to database
            print(f"AppID: {appid}, Name: {name}, Categories: {category_names}")

        # Sleep to prevent rate limits
        time.sleep(0.5)

    print("Done fetching app data.")

