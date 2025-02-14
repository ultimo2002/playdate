from fastapi.testclient import TestClient

from code.api import API
from code.test_helpers import check_response, is_json, check_list_of_items, check_app_response, is_html, TEST_APP_NAMES, \
    ALL_APP_FIELDS, assert_common_app_tests

api_instance = API()
api_instance.register_endpoints()
client = TestClient(api_instance.app)

def test_root():
    response = client.get("/")

    # Test if the response status code is 200 (Good)
    assert check_response(response, 200) and not is_json(response)

    # Test if the response is HTML content
    assert "html" in response.headers["content-type"] and "<!DOCTYPE html>" in response.text

    # Test if there is a form in the response
    assert "<form" in response.text

def test_apps():
    """
    Test the GET "/apps" endpoint for a list of all the apps with id and name in the database.
    """
    response = client.get("/apps")
    assert_common_app_tests(response, ["id", "name"])

def test_apps_all_fields():
    """
    Test the GET "/apps" endpoint for a list of all the apps with all fields in the database.
    """
    response = client.get("/apps?all_fields=true")
    assert_common_app_tests(response, ALL_APP_FIELDS)

def test_cats():
    """
    Test the GET endpoints for valid categories, tags, and genres.
    Also test the GET "/cats" endpoint for a dictionary containing all categories, tags, and genres.
    """
    for endpoint in ["/categories", "/tags", "/genres"]:
        response = client.get(endpoint)
        assert check_response(response, 200) and is_json(response)
        assert len(response.json()) > 0
        check_list_of_items(response, ["id", "name"])

    response = client.get("/cats")
    assert check_response(response, 200) and is_json(response)

    # Test if the response contains categories, tags, and genres as direct keys
    assert all(key in response.json() for key in ["categories", "tags", "genres"])

def test_app_details():
    """
    Test the GET "/app/{appid}" endpoint for valid app details.
    """
    response = client.get("/app/367520")
    check_app_response(response)
    assert response.json()["name"] == "Hollow Knight"

def test_app_invalid_app_id():
    """
    Test the GET "/app/{appid}" endpoint for an invalid app ID (404 response).
    """
    response = client.get("/app/0")
    assert check_response(response, 404) and is_json(response)
    assert response.json() == {"detail": "App not found."}

def test_app_fuzzy_search():
    """
    Test the GET "/app/{appid}" endpoint for fuzzy search.
    """
    # Test one case with fuzzy search
    response = client.get("/app/Hallo%20Night")
    check_app_response(response)
    assert response.json()["name"] == "Hollow Knight"

    for app_name in TEST_APP_NAMES:
        response = client.get(f"/app/{app_name}")
        check_app_response(response)
        if app_name.isdigit(): # Edge case when given an app id, must return the same app id
            assert response.json()["id"] == int(app_name)

def test_app_fuzzy_search_without_fuzzy():
    """
    Test the GET "/app/{appid}" endpoint for fuzzy search without fuzzy matching (404 response).
    """
    for app_name in TEST_APP_NAMES:
        response = client.get(f"/app/{app_name}?fuzzy=false")
        if response.status_code == 200:
            # It is possible to enter the exact name of the app (or id) without fuzzy matching

            if app_name.isdigit():
                # If the given app name is not a number (Can also be a number (appid))
                assert response.json()["id"] == int(app_name)
            else:
                assert response.json()["name"].strip().lower() == app_name.strip().lower() # Test if the given name is the same

            # Test if the response contains app details
            check_app_response(response)
        else:
            # The app name is not found by the exact name we get a 404 response
            assert check_response(response, 404) and is_json(response)
            assert response.json() == {"detail": f"App {app_name.replace('%20', ' ').strip().capitalize()} not found"}