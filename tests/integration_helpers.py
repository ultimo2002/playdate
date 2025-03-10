import os

from fastapi.testclient import TestClient
from tests.fill_database import fill_database
from src.api import API
from src.config import TextStyles
from src.database.models import App
from src.database.database import SessionLocal


POSSIBLE_GET_ENDPOINTS = ["/", "/apps", "/categories", "/tags", "/genres", "/app/{appid}", "/cats", "/apps/developer/{target_name}", "/apps/tag/{target_name}"]
ALL_APP_FIELDS = [field.name for field in App.__table__.columns]

# test app names for use in testing
test_names = ["Space Adventure Game",
              "Task Master Pro",
              "Learn Python Interactive",
              "Fitness Tracker Plus",
              "Movie Streamer",
              "Puzzle Quest",
              "Daily Planner",
              "Math Tutor AI",
              "Yoga & Meditation",
              "Music Studio Pro",
              "Racing Champions",
              "Expense Manager",
              "History Explorer",
              "Cooking Assistant",
              "Photo Editor Deluxe",
              ]
# test name array for fuzzy search, index corresponds to game id
wrong_test_names = [None,  # there is no 0 id
                    "sp8ce @tventurefe gm",  # Space Adventure Game
                    "Tks mSt Pr",  # Task Master Pro
                    "Learn Python",  # Learn Python Interactive
                    "F209348209348 tracker plus",  # Fitness Tracker Plus
                    "M0Vi3 Strmer",  # Movie Streamer
                    "pzzl qqwetst",  # Puzzle Quest
                    "delli plainer",  # Daily Planner
                    "Meth Tutor Jessie!",  # Math Tutor AI
                    "Yoga and meditation",  # Yoga & Meditation
                    "amazing music studio pro",  # Music Studio Pro
                    "Race championship",  # Racing Champions
                    "Expensive manager",  # Expense Manager
                    "History repeats",  # History Explorer
                    "We need to cook, Assistant!",  # Cooking Assistant
                    "photoshop"  # Photo Editor Deluxe
                    ]


api_instance = API()
api_instance.register_endpoints()
client = TestClient(api_instance.app)
STEEKPROEF_APPS = 10


def setup():

    #check database
    URL_DATABASE = os.getenv("URL_DATABASE")
    if "sqlite" in URL_DATABASE:
        print("in-memory database gevonden!")
    else:
        raise ValueError(f"Je gebruikt niet de in-memory database! (zocht \"sqlite\" in {URL_DATABASE})")

    #maak API voor testen
    global api_instance
    api_instance = API()
    api_instance.register_endpoints(all_endpoints=True)


    #richt database in met 15 testgames
    session = SessionLocal()
    fill_database(session)


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