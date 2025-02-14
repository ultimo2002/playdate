POSSIBLE_GET_ENDPOINTS = ["/apps", "/categories", "/tags", "/genres", "/app/{appid}", "/cats", "/apps/developer/{target_name}", "/apps/tag/{target_name}"]
TEST_APP_NAMES = ["Hallo%20Night", "The Sims™ Legacy Collection", "Terraria", "Putt+Putt+Circus", "3314070"]
ALL_APP_FIELDS = ["id", "name", "short_description", "price", "developer", "background_image", "header_image"]


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