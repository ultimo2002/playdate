from fastapi.testclient import TestClient
from code.api import API
from code.config import TextStyles
import code.database.models as models
import sys

POSSIBLE_GET_ENDPOINTS = ["/", "/apps", "/categories", "/tags", "/genres", "/app/{appid}", "/cats", "/apps/developer/{target_name}", "/apps/tag/{target_name}"]
ALL_APP_FIELDS = [field.name for field in models.App.__table__.columns]

# Default test apps with app names and app IDs and typos (to be later appended with random apps (als steekproef))
TEST_APPS = {
    "Hallo%20Night": {"expected_appid": 367520, "expected_name": "Hollow Knight"},
    "The Sims™ Legacy Collection": {"expected_appid": 3314060, "expected_name": "The Sims™ Legacy Collection"},
    "terraria": {"expected_appid": 105600, "expected_name": "Terraria"},
    "Putt+Putt+Circus": {"expected_appid": 294690, "expected_name": "Putt-Putt® Joins the Circus"},
    "3314070": {"expected_appid": 3314070, "expected_name": "The Sims™ 2 Legacy Collection"},
    "heeldrivers": {"expected_appid": 553850, "expected_name": "HELLDIVERS™ 2"},
}

# Save the default test apps for later use (e.g., if the random apps cannot be fetched)
DEFAULT_TEST_APPS = TEST_APPS.copy()

STEEKPROEF_APPS = 10

def is_imported_from(filename):
    stack = sys._getframe().f_back
    while stack:
        if stack.f_code.co_filename.endswith(filename):
            return True
        stack = stack.f_back
    return False

api_instance = API()
api_instance.register_endpoints()
client = TestClient(api_instance.app)
try:
    # only fetch random apps if this file is imported from integration_test.py, else it is not good for testing performance
    # if the integration_helpers.py file is imported from another file
    if not is_imported_from("integration_test.py"):
        raise Exception("Not imported from integration_test.py")

    # Fill the TEST_APPS with random apps
    # Om een steekproef te nemen van een aantal willekeurige apps, Die worden gebruikt in de test van "integration_test.py"
    reponse_random_apps = client.get(f"/apps/random?count={STEEKPROEF_APPS}")

    if reponse_random_apps.status_code == 200 and "application/json" in reponse_random_apps.headers["content-type"]:
        for app_name_key, app in reponse_random_apps.json().items():
            TEST_APPS[app_name_key] = app

    print(f"{TextStyles.bold}Total test apps: {TextStyles.reset}{TextStyles.green}{TextStyles.bold}{len(TEST_APPS)} apps{TextStyles.reset}")
    del reponse_random_apps
except Exception as e:
    print(f"{TextStyles.bold}Error fetching random apps: {TextStyles.reset}{e}")
    print("Setting TEST_APPS to the DEFAULT_TEST_APPS.")
    TEST_APPS = DEFAULT_TEST_APPS
finally:
    # close the client and delete the API instance and client
    client.close()
    del api_instance
    del client

TEST_APP_NAMES = list(TEST_APPS.keys())

def test_configs():
    """
    Test if the configuration values are set correctly.
    """
    assert len(ALL_APP_FIELDS) > 0 and "id" in ALL_APP_FIELDS # Check if the ALL_APP_FIELDS list is not empty and contains an "id" field

    import code.config as config # Test the configuration values from config.py.

    assert all(value is not None for value in config.DB_CONFIG.values()) # Check if all DB_CONFIG values are set

    from code.database.database import URL_DATABASE

    # Test if database URL is set and not empty or postgresql://user:password@localhost:5432/database
    assert URL_DATABASE is not None and len(URL_DATABASE) > 0 and URL_DATABASE != "postgresql://user:password@localhost:5432/database"

    # Remove the imported modules from memory
    del config
    del URL_DATABASE

def check_response(response, status_code=200):
    """"
    Check if the response status code matches the expected status code.
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

def assert_common_app_tests(response, expected_fields):
    """
    A helper function that asserts common conditions for app responses:
    - Response status code is 200
    - Response is in JSON format
    - List of apps has more than given entries
    - All apps contain the expected fields (id, name, other fields)
    """
    # Test if the response status code is 200 and is JSON
    assert check_response(response, 200) and is_json(response)

    # Test if the list of apps is higher than 100
    assert len(response.json()) > 100

    # Test if the response contains a list of apps with the expected fields
    assert all(key in response.json()[0] for key in expected_fields)