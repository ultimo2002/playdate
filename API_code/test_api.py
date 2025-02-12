from fastapi import FastAPI
from fastapi.testclient import TestClient
from .main import app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))  # Ensure current directory is in sys.path



client = TestClient(app)



def test_main():
    response = client.get("/")
    assert response.status_code == 200
