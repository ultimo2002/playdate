import os

from fastapi.testclient import TestClient

from src.api import API
from src.config import TextStyles
from src.database.models import *
from src.database.database import SessionLocal
from src.database import models
POSSIBLE_GET_ENDPOINTS = ["/", "/apps", "/categories", "/tags", "/genres", "/app/{appid}", "/cats", "/apps/developer/{target_name}", "/apps/tag/{target_name}"]
ALL_APP_FIELDS = [field.name for field in App.__table__.columns]

# Default test apps with app names and app IDs and typos (to be later appended with random apps (als steekproef))
APPS = {
    "Hallo%20Night": {"expected_appid": 367520, "expected_name": "Hollow Knight"},
    "The Sims™ Legacy Collection": {"expected_appid": 3314060, "expected_name": "The Sims™ Legacy Collection"},
    "terraria": {"expected_appid": 105600, "expected_name": "Terraria"},
    "Putt+Putt+Circus": {"expected_appid": 294690, "expected_name": "Putt-Putt® Joins the Circus"},
    "3314070": {"expected_appid": 3314070, "expected_name": "The Sims™ 2 Legacy Collection"},
    "heeldrivers": {"expected_appid": 553850, "expected_name": "HELLDIVERS™ 2"},
}

# Save the default test apps for later use (e.g., if the random apps cannot be fetched)
DEFAULT_APPS = APPS.copy()
api_instance = API()
api_instance.register_endpoints()
client = TestClient(api_instance.app)
STEEKPROEF_APPS = 10


def setup():

    #check database
    URL_DATABASE = os.getenv("URL_DATABASE")
    if "sqlite" in URL_DATABASE:
        print("in-memory database gevonden"
              "")
    # else:
    #     raise ValueError(f"Je gebruikt niet de in-memory database! (zocht \"sqlite\" in {URL_DATABASE})")

    #maak API voor testen
    global api_instance
    api_instance = API()
    api_instance.register_endpoints(all_endpoints=True)


    #richt database in met 15 testgames
    session = SessionLocal()
    fill_database(session)
def fill_database(db):
    # List of apps to insert
    entries = [
        App(id=365670, name="Blender", short_description="Blender is the free and open source 3D creation suite.",
            price=None, developer="Blender Foundation",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/365670/header.jpg?t=1732033230",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/365670/page_bg_generated_v6b.jpg?t=1732033230"),
        App(id=1174180, name="Red Dead Redemption 2", short_description="Winner of over 175 Game of the Year Awards...",
            price="€ 59,99", developer="Rockstar Games",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1174180/header.jpg?t=1720558643",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1174180/page_bg_generated_v6b.jpg?t=1720558643"),
        App(id=35140, name="Batman: Arkham Asylum GOTY Edition",
            short_description="Experience what it’s like to be Batman...", price="€ 19,99",
            developer="Rocksteady Studios",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/35140/header.jpg?t=1702934705",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/35140/page_bg_generated_v6b.jpg?t=1702934705"),
        App(id=570, name="Dota 2", short_description="Every day, millions of players worldwide enter battle...",
            price=None, developer="Valve",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/570/header.jpg?t=1731544174",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/570/page_bg_generated_v6b.jpg?t=1731544174"),
        App(id=812140, name="Assassin's Creed Odyssey",
            short_description="Assassin's Creed Odyssey is an action-adventure game...", price="€ 59,99",
            developer="Ubisoft Quebec",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/812140/header.jpg?t=1736257794",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/812140/page_bg_generated_v6b.jpg?t=1736257794"),
        App(id=524220, name="NieR:Automata™",
            short_description="NieR: Automata tells the story of androids 2B, 9S and A2...", price="CDN$ 21.40",
            developer="Square Enix",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/524220/header.jpg?t=1734624625",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/524220/page_bg_generated_v6b.jpg?t=1734624625"),
        App(id=3188910, name="Waifu", short_description="💗 Idler Clicker + Dating Sim 💗 Earn rare Waifus...",
            price=None, developer="Team Waifu",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3188910/header.jpg?t=1737031359",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3188910/page_bg_generated_v6b.jpg?t=1737031359"),
        App(id=403640, name="Dishonored 2",
            short_description="Reprise your role as a supernatural assassin in Dishonored 2...", price="€ 29,99",
            developer="Arkane Studios",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/403640/header.jpg?t=1726161101",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/403640/page_bg_generated_v6b.jpg?t=1726161101"),
        App(id=460930, name="Tom Clancy's Ghost Recon® Wildlands",
            short_description="Create a team with up to 3 friends...", price="€ 49,99", developer="Ubisoft Paris",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/460930/header.jpg?t=1734366779",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/460930/page_bg_generated_v6b.jpg?t=1734366779"),
        App(id=2904000, name="The Spell Brigade",
            short_description="Survivors-like with ONLINE CO-OP for 1-4 players...", price="€ 9,75",
            developer="Bolt Blaster Games",
            header_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2904000/header.jpg?t=1738335681",
            background_image="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2904000/page_bg_generated_v6b.jpg?t=1738335681")
        Category(id=63, name="Steam Timeline")
    ]
    # Add apps to the session and commit
    db.add_all(entries)
    db.commit()
    for entry in db.query(models.App).all():
        print(entry.name)





try:
    # Fill the APPS with random apps
    # Om een steekproef te nemen van een aantal willekeurige apps, Die worden gebruikt in de test van "integration_test.py"
    reponse_random_apps = API.get_random_apps(count=STEEKPROEF_APPS)

    if reponse_random_apps.status_code == 200 and "application/json" in reponse_random_apps.headers["content-type"]:
        for app_name_key, app in reponse_random_apps.json().items():
            APPS[app_name_key] = app

    print(f"{TextStyles.bold}Total test apps: {TextStyles.reset}{TextStyles.green}{TextStyles.bold}{len(APPS)} apps{TextStyles.reset}")
    del reponse_random_apps
except Exception as e:
    print(f"{TextStyles.bold}Error fetching random apps: {TextStyles.reset}{e}")
    print("Setting APPS to the DEFAULT_APPS.")
    APPS = DEFAULT_APPS


APP_NAMES = list(APPS.keys())

def check_response(response, status_code=200):
    """"
    Check if the response status src matches the expected status src.
    :return: Boolean
    """
    return response.status_code == status_code

def is_json(response):
    """
    Check if the response is in JSON format.
    :return: Boolean
    """
    return "application/json" in response.headers["content-type"]

def is_html(response):
    """
    Check if the response is in HTML format.
    :return: Boolean
    """
    return "text/html" in response.headers["content-type"] and "<!DOCTYPE html>" in response.text

def contains_form(response, method: str = "GET"):
    """
    Check if the response contains a form element. and if it has the given method.
    :return: Boolean
    """
    assert method in ["GET", "POST"]

    response_text = response.text.lower()

    return "<form" in response_text and f"method=\"{method}\"".lower() in response_text

def number_of_h1_tags(response):
    """
    Check if the response contains two H1 tags. A page may only contain one H1 tag.
    :return: (int) Number of H1 tags found
    """
    return response.text.lower().count("<h1>")

def check_h1_tag(response):
    """
    Check if the response contains only one or none H1 tag.
    :return: Boolean
    """
    return number_of_h1_tags(response) <= 1

def check_list_of_items(response, expected_keys):
    """
    Check if the response contains a list of items with the expected keys.
    :return: Asserts (Returns nothing)
    """
    assert all(key in response.json()[0] for key in expected_keys)

def check_app_response(response):
    """
    Check if the response contains app details. (id, name, short_description, price, developer, background_image, header_image)
    :return: Asserts (Returns nothing)
    """
    assert check_response(response, 200) and is_json(response)
    assert all(key in response.json() for key in ALL_APP_FIELDS)

def assert_common_app_tests(response, expected_fields, entries_count=100):
    """
    A helper function that asserts common conditions for app responses:
    - Response status src is 200
    - Response is in JSON format
    - List of apps has more than given entries (default=100)
    - All apps contain the expected fields (id, name, other fields)
    """
    # Test if the response status src is 200 and is JSON
    assert check_response(response, 200)
    assert is_json(response)

    # Test if the list of apps is higher than given number
    assert len(response.json()) > entries_count

    # Test if the response contains a list of apps with the expected fields
    assert all(key in response.json()[0] for key in expected_fields)
setup()