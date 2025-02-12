from fastapi import FastAPI
from fastapi.testclient import TestClient
import code.api as api
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))  # Ensure current directory is in sys.path


api_instance = api.API()
api_instance.register_endpoints()
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))  # Ensure current directory is in sys.path
client = TestClient(api_instance.app)



def test_():
    response = client.get("/")
    assert response.status_code == 200