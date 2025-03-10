import os

from fastapi.testclient import TestClient

from src.api import API
from tests.integration_helpers import check_response, is_json, is_html, POSSIBLE_GET_ENDPOINTS

api_instance = API()
api_instance.register_endpoints(all_endpoints=True)
client = TestClient(api_instance.app)

def test_openapi():
    response = client.get("/openapi.json")

    # Test if the response status src is 200 (Good)
    assert check_response(response, 200) and is_json(response)

    paths = response.json()["paths"]

    # Test if the response contains the OpenAPI schema and has paths
    assert "openapi" in response.json() and paths

    # Test if there are possible GET endpoints defined
    assert not len(POSSIBLE_GET_ENDPOINTS) == 0

    # for endpoint in POSSIBLE_GET_ENDPOINTS:
    #     assert endpoint in paths
    #     # Test if the endpoint has a GET method
    #     assert "get" in paths[endpoint]

    # test if there is an GET, POST, PUT and DELETE endpoint in the response
    # RESPONSE_TEXT = response.text
    # RESPONSE_TYPES = ["GET", "POST", "PUT", "DELETE"]
    # for response_type in RESPONSE_TYPES:
    #     assert response_type in RESPONSE_TEXT

def test_docs():
    response = client.get("/docs")

    # Test if the response status src is 200 (Good)
    assert check_response(response, 200) and not is_json(response)

    assert is_html(response)

    # Swagger UI is the documentation tool used by FastAPI
    assert "Swagger UI" in response.text

def test_redoc():
    response = client.get("/redoc")

    # Test if the response status src is 200 (Good)
    assert check_response(response, 200) and not is_json(response)

    assert is_html(response)

    # ReDoc is another documentation tool used by FastAPI
    assert "ReDoc" in response.text