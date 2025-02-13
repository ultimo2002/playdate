
from fastapi.testclient import TestClient
from code.api import API


api_instance = API()
api_instance.register_endpoints()
client = TestClient(api_instance.app)



def test_():
    response = client.get("/")
    assert response.status_code == 200