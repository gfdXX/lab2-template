import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_get_rentals_missing_header():
    response = client.get("/api/v1/rental")
    assert response.status_code == 400

def test_get_rental_missing_header():
    response = client.get("/api/v1/rental/test-uid")
    assert response.status_code == 400
