from fastapi.testclient import TestClient

from code.api import API
from code.config import TextStyles
from tests.integration_helpers import check_response, is_json, check_list_of_items, check_app_response, is_html, \
    TEST_APP_NAMES, \
    ALL_APP_FIELDS, assert_common_app_tests, contains_form, TEST_APPS, DEFAULT_TEST_APPS, check_h1_tag

api_instance = API()
api_instance.register_endpoints(all_endpoints=True)
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

    assert check_h1_tag(response)

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
    In this test, we will test the endpoint with multiple (steekproef) apps. And test if the app name and app id are expected.
    """
    # Test one case with fuzzy search, and the expected name.
    response = client.get("/app/Hallo%20Night")
    check_app_response(response)
    assert response.json()["name"] == "Hollow Knight"

    # Some apps can fail the test, because of the typo algorithm and fuzzy, I don't want to fail the test if a litle bit of apps fail
    TEST_MARGIN = 3 # Amount of apps can fail the test

    # the key of the dictionary is the app name set the app_name to the key from new TEST_APPS
    for app_name, app in TEST_APPS.items():
        assert TEST_MARGIN >= 0

        response = client.get(f"/app/{app_name}")

        if response.status_code == 404:
            TEST_MARGIN -= 1
            print(f"{TextStyles.red}Failed app: {app_name} - Expected: {app['expected_name']} - Got: 404{TextStyles.reset}")
            continue

        assert check_response(response, 200) and is_json(response)

        if app_name.isdigit(): # Edge case when given an app id, must return the same app id
            assert response.json()["id"] == int(app_name)

        # Test if the app name from the response is the same as the expected app name
        if response.json()["name"] != app["expected_name"] and TEST_MARGIN > 0:
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

def test_app_recommend_image_cache():
    """
    Test the GET "/recommend" endpoint for image caching.
    """
    # enable image caching temporarily for this test in the environment variables
    import os
    initial_env = os.environ.get("CACHE_IMAGES", "false")
    os.environ["CACHE_IMAGES"] = "true"

    response = client.get("/recommend?game=Among+Us")
    assert check_response(response, 200) and not is_json(response)
    assert is_html(response)

    assert "background-image" in response.text
    image_url = response.text.split("background-image: url(")[1].split(")")[0].strip()
    assert "bg_" in image_url

    assert "Logo of Among Us" in response.text
    assert "game-image" in response.text
    assert "hi_" in response.text

    # reset the environment variable to the initial value, and delete imported modules from memory
    os.environ["CACHE_IMAGES"] = initial_env

    # delete the cached images
    os.remove("code/static/cache/bg_945360.jpg")
    os.remove("code/static/cache/hi_945360.jpg")
    try:
        # remove the cache directory if it is empty
        os.rmdir("code/static/cache")
    except OSError:
        pass # directory is not empty so we can't remove it
    del os

def test_apps_get_tags():
    """
    Test the GET "/apps/tag/{target_name}" endpoint for valid apps based on the tag name.
    """
    response = client.get("/apps/tag/Pools") # Pool is a tag, it does fuzzy matching to find the tag "Pool"
    check_list_of_items(response, ["id", "name"])
    # Check if Planet Coaster 2 is in the response (game has the tag "Pool")
    assert any(app["name"] == "Planet Coaster 2" for app in response.json())

    # Test when using a tag that does not exist with fuzzy=false
    response = client.get("/apps/tag/Pools?fuzzy=false") # Pools does not exist, Pool does
    assert check_response(response, 404) and is_json(response)
    assert response.json()["detail"].startswith("No apps found for tag")

    # Five nights at freddy's has the tag "Horror", there are multiple games of Five nights at freddy's so we can test if it returns multiple FNAF games
    response = client.get("/apps/tag/Horror")
    check_list_of_items(response, ["id", "name"])
    response_json = response.json()
    # check if list contains a part of "Five Nights at Freddy's"
    assert any(app["name"].lower().startswith("five nights at freddy") for app in response_json)

    # Test if five nights at freddy's has more than 1 app with the tag "Horror"
    assert len([app for app in response_json if app["name"].lower().startswith("five nights at freddy")]) > 1
    del response_json

    # Test if the response contains app details
    for app_name, app in DEFAULT_TEST_APPS.items():
        # get tags for each app in TEST_APPS
        response = client.get(f"/app/{app_name}/tags")
        check_list_of_items(response, ["id", "name"])

def test_apps_from_developer():
    """
    Test the GET "/apps/developer/{target_name}" endpoint to get all apps from a specific developer.
    """
    response = client.get("/apps/developer/Vaalv") # Valve is a developer, it does fuzzy matching to find the developer "Valve"
    assert check_response(response, 200) and is_json(response)
    check_list_of_items(response, ["id", "name"])
    # Check if Portal 2 is in the response (game is developed by Valve)
    assert any(app["name"] == "Portal 2" for app in response.json())

    # Test when using fuzzy=false and the developer does not exist
    response = client.get("/apps/developer/Vaalv?fuzzy=false") # Vaalv does not exist, Valve does, but fuzzy is disabled this time
    assert check_response(response, 404) and is_json(response)
    assert "No apps found for developer" in response.json()["detail"]

def test_get_app_recommend_input_rerurn_frontpage():
    """
    Test the GET "/recommend" endpoint without query parameters,
    ensuring it returns the front page.
    """
    response = client.get("/recommend")
    assert check_response(response, 200) and not is_json(response)
    assert is_html(response)
    assert contains_form(response, method="GET")
    # Check if the background image is set and overlay class is on the page
    assert "background-image" in response.text and "overlay" in response.text
    # Ensure there is exactly one h1 tag on the page
    assert check_h1_tag(response)


def test_get_app_recommend_input_with_game_query():
    """
    Test the GET "/recommend" endpoint with a 'game_input' query parameter,
    ensuring the correct game is selected and the proper elements are present.
    """
    response = client.get("/recommend?game=Among+Sus")
    assert check_response(response, 200) and not is_json(response)
    assert is_html(response)
    # "Among Sus" is a typo so the expected output should correct it to "Among Us"
    assert "Among Us" in response.text
    assert contains_form(response, method="GET")  # The form should still be present
    assert "Home</a>" in response.text
    assert "<h2>Selected Game</h2>" in response.text
    # Ensure there is exactly one h1 tag on the page
    assert check_h1_tag(response)


def test_post_app_recommend_post_input_not_allowed():
    """
    Test the POST method on "/recommend" endpoint, which should return an error
    since POST is not allowed.
    """
    response = client.post("/recommend", data={"game": "Among Sus"})
    assert check_response(response, 405) and is_json(response)
    assert response.json()["detail"] == "Method Not Allowed"

def test_developers():
    """
    Test the GET "/developers" endpoint for a list of all developers in the database. with name.
    """
    response = client.get("/developers")
    assert check_response(response, 200) and is_json(response)
    check_list_of_items(response, ["name"])

    response = client.get("/developers?apps=true")
    assert check_response(response, 200) and is_json(response)
    # Test if the response contains a list of developers with the expected fields
    assert all(key in response.json()[0] for key in ["name", "apps"])
    assert all(key in response.json()[0]["apps"][0] for key in ["id", "name"])

def test_random_apps():
    """
    Test the GET "/random_apps" endpoint for a dictionary containing random app names and app IDs.
    """
    NUMBER_OF_RANDOM_APPS = 3

    response = client.get(f"/apps/random?count={NUMBER_OF_RANDOM_APPS}")
    assert check_response(response, 200) and is_json(response)

    response_json = response.json()

    # Test if the response contains the correct number of random apps
    assert len(response_json) == NUMBER_OF_RANDOM_APPS

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

    # test that if we ask for more than 1000 apps we only get 25 apps back
    response = client.get("/apps/random?count=1000")
    assert check_response(response, 200) and is_json(response)
    assert len(response.json()) == 25

    # test that if we ask for less than 1 app we get 1 app back
    response = client.get("/apps/random?count=0")
    assert check_response(response, 200) and is_json(response)
    assert len(response.json()) == 1