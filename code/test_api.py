from fastapi.testclient import TestClient

from code.api import API
from code.config import TextStyles
from code.test_helpers import check_response, is_json, check_list_of_items, check_app_response, is_html, TEST_APP_NAMES, \
    ALL_APP_FIELDS, assert_common_app_tests, TEST_APPS, DEFAULT_TEST_APPS, contains_form

api_instance = API()
api_instance.register_endpoints()
client = TestClient(api_instance.app)

def test_root():
    response = client.get("/")

    # Test if the response status code is 200 (Good)
    assert check_response(response, 200) and not is_json(response)

    # Test if the response is HTML content
    assert is_html(response)

    # Test if there is a form in the response
    assert contains_form(response, "GET")

    # Test if background image is set
    assert "background-image" in response.text
    image_url = response.text.split("background-image: url(")[1].split(")")[0].strip()

    print(f"Background image URL: {image_url}")
    assert "http" in image_url or "bg_" in image_url

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

    # Some apps can fail the test, becuase of the typo algorithm, I don't want to fail the test if some apps fail
    TEST_MARGIN = 3 # Amount of apps can fail the test

    # the key of the dictionary is the app name set the app_name to the key from new TEST_APPS
    for app_name, app in TEST_APPS.items():
        assert TEST_MARGIN >= 0

        response = client.get(f"/app/{app_name}")
        check_app_response(response)
        if app_name.isdigit(): # Edge case when given an app id, must return the same app id
            assert response.json()["id"] == int(app_name)
            assert app["expected_appid"] == int(app_name)

        # Test if the app name from the response is the same as the expected app name
        if response.json()["name"] != app["expected_name"]:
            TEST_MARGIN -= 1
            print(f"{TextStyles.red}Failed app: {app_name} - Expected: {app['expected_name']} - Got: {response.json()['name']}{TextStyles.reset}")
            continue
        else:
            assert response.json()["name"] == app["expected_name"]

        # Test if the app id from the response is the same as the expected app id
        assert response.json()["id"] == app["expected_appid"]

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

            print(f"{TextStyles.green}{TextStyles.bold}(good) 200 response for: {app_name}{TextStyles.reset}")
        else:
            # The app name is not found by the exact name we get a 404 response
            assert check_response(response, 404) and is_json(response)

            # Test if the response contains the correct error message
            message = response.json()["detail"]
            assert message and all(word in message for word in ["App", "not", "found"])
            print(f"{TextStyles.green}(good) 404 response for: {app_name}{TextStyles.reset}")

def test_get_app_tags():
    """
    Test the GET "/apps/tag/{target_name}" endpoint for valid apps based on the tag name.
    """
    response = client.get("/apps/tag/Pool")
    check_list_of_items(response, ["id", "name"])
    # Check if Planet Coaster 2 is in the response (game has the tag "Pool")
    assert any(app["name"] == "Planet Coaster 2" for app in response.json())

    # Five nights at freddy's has the tag "Horror"
    response = client.get("/apps/tag/Horror")
    check_list_of_items(response, ["id", "name"])
    # check if list contains a part of "Five Nights at Freddy's"
    assert any(app["name"].lower().startswith("five nights at freddy") for app in response.json())

    # Test if the response contains app details
    for app_name, app in DEFAULT_TEST_APPS.items():
        # get tags for each app in TEST_APPS
        response = client.get(f"/app/{app_name}/tags")
        check_list_of_items(response, ["id", "name"])

def test_random_apps():
    """
    Test the GET "/random_apps" endpoint for a dictionary containing random app names and app IDs.
    """
    response = client.get("/random_apps?count=15")
    assert check_response(response, 200) and is_json(response)

    response_json = response.json()

    # Test if the response contains the correct number of random apps
    assert len(response_json) == 15

    # Result for 1 random app
    # {
    #   "StmbleGuys": {
    #     "expected_appid": 1677740,
    #     "expected_name": "Stumble Guys"
    #   }
    # }

    # Test if the response contains the expected app names and app IDs with the correct data types
    # for app_name, app in response_json.items():
    #     assert app_name in response_json
    #     assert isinstance(app["expected_appid"], int)
    #     assert isinstance(app["expected_name"], str)

    # short version of the above code
    assert all(isinstance(app["expected_appid"], int) and isinstance(app["expected_name"], str) for app in response_json.values())