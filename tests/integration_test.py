import dotenv
from tests.integration_helpers import *
dotenv.load_dotenv()
def test_root():
    response = client.get("/")

    # Test if the response status src is 200 (Good)
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
    assert_common_app_tests(response, ["id", "name"],entries_count=9)

def test_apps_all_fields():
    """
    Test the GET "/apps" endpoint for a list of all the apps with all fields in the database.
    """
    response = client.get("/apps?all_fields=true")
    assert_common_app_tests(response, ALL_APP_FIELDS, entries_count=9)

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
    response = client.get("/app/1")
    check_app_response(response)
    assert response.json()["name"] == "Space Adventure Game"

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
    In this test, we will test the endpoint with all 15 apps. And test if the app id is expected.
    """

    #loop through the names and compare against the id of their real counterpart
    for i in range(1,16):
        response = client.get(f"/app/{wrong_test_names[i]}") #found in integration helpers
        assert check_response(response, 200) and is_json(response)
        assert response.json()["id"] == i

def test_app_fuzzy_search_without_fuzzy():
    """
    Test the GET "/app/{appid}" endpoint for fuzzy search without fuzzy matching (404 response).
    """
    for app_name in test_names: #found in integration helpers
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

def test_app_recommend():
    """
    Test the GET "/recommend" endpoint.
    """

    response = client.get("/recommend?games=12")
    assert check_response(response, 200) and not is_json(response)
    assert is_html(response)

    assert "background-image" in response.text
    image_url = response.text.split("background-image: url(")[1].split(")")[0].strip()
    assert "bg" in image_url

    assert "Recommended Games" in response.text
    assert "Logo of Expense Manager" in response.text
    assert "game-image" in response.text

def test_apps_get_tags():
    """
    Test the GET "/apps/tag/{target_name}" endpoint for valid apps based on the tag name.
    """
    response = client.get("/apps/tag/Multiplayer")
    check_list_of_items(response, ["id", "name"])
    # Check if Space Adventure Game is in the response (game has the tag "Pool")
    assert any(app["name"] == "Space Adventure Game" for app in response.json())

    # Test when using a tag that does not exist with fuzzy=false
    response = client.get("/apps/tag/Pools?fuzzy=false") # Pools does not exist
    assert check_response(response, 404) and is_json(response)
    assert response.json()["detail"].startswith("No apps found for tag")

    # Test if the response contains app details
    for app_name in test_names:
        # get tags for each app in TEST_APPS
        response = client.get(f"/app/{app_name}/tags")
        check_list_of_items(response, ["id", "name"])

def test_apps_from_developer():
    """
    Test the GET "/apps/developer/{target_name}" endpoint to get all apps from a specific developer.
    """
    response = client.get("/apps/developer/Speed Demons Studio") # Valve is a developer, it does fuzzy matching to find the developer "Valve"
    assert check_response(response, 200) and is_json(response)
    check_list_of_items(response, ["id", "name"])
    # Check if Racing Champions is in the response (game is developed by Valve)
    assert any(app["name"] == "Racing Champions" for app in response.json())

    #Dit moet weg. We testen fuzzy alleen in de fuzzy test, anders falen alle tests als fuzzy het niet doet

    # # Test when using fuzzy=false and the developer does not exist
    # response = client.get("/apps/developer/Vaalv?fuzzy=false") # Vaalv does not exist, Valve does, but fuzzy is disabled this time
    # assert check_response(response, 404) and is_json(response)
    # assert "No apps found for developer" in response.json()["detail"]

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
    response = client.get("/recommend?games=14")
    assert check_response(response, 200) and not is_json(response)
    assert is_html(response)
    assert "Fitness Tracker Plus" in response.text
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

# def test_random_apps():
#     """
#     Test the GET "/random_apps" endpoint for a dictionary containing random app names and app IDs.
#     """
#     NUMBER_OF_RANDOM_APPS = 3
#
#     response = client.get(f"/apps/random?count={NUMBER_OF_RANDOM_APPS}")
#     assert check_response(response, 200) and is_json(response)
#
#     response_json = response.json()
#
#     # Test if the response contains the correct number of random apps
#     assert len(response_json) == NUMBER_OF_RANDOM_APPS
#
#     # Result for 1 random app
#     # {
#     #   "StmbleGuys": {
#     #     "expected_appid": 1677740,
#     #     "expected_name": "Stumble Guys"
#     #   }
#     # }
#
#     # Test if the response contains the expected app names and app IDs with the correct data types
#     # for app_name, app in response_json.items():
#     #     assert app_name in response_json
#     #     assert isinstance(app["expected_appid"], int)
#     #     assert isinstance(app["expected_name"], str)
#
#     # short version of the above src
#     assert all(isinstance(app["expected_appid"], int) and isinstance(app["expected_name"], str) for app in response_json.values())
#
#     # test that if we ask for more than 1000 apps we only get 25 apps back
#     response = client.get("/apps/random?count=1000")
#     assert check_response(response, 200) and is_json(response)
#     assert len(response.json()) == 25
#
#     # test that if we ask for less than 1 app we get 1 app back
#     response = client.get("/apps/random?count=0")
#     assert check_response(response, 200) and is_json(response)
#     assert len(response.json()) == 1