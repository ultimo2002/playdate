from API_code import api
from fastapi.testclient import TestClient
client = TestClient(api.API.app)

def test_run():
    response = client.get("/")
    assert response.status_code == 200