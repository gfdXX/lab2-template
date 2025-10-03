import pytest
from fastapi.testclient import TestClient
from services.gateway_service.main import app
import uuid

client = TestClient(app)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_get_rentals_missing_header():
    """Test rentals endpoint without required header"""
    response = client.get("/api/v1/rental")
    assert response.status_code == 400

def test_get_rental_missing_header():
    """Test single rental endpoint without required header"""
    test_uuid = uuid.uuid4()
    response = client.get(f"/api/v1/rental/{test_uuid}")
    assert response.status_code == 400

def test_get_cars_endpoint():
    """Test cars endpoint through gateway"""
    response = client.get("/api/v1/cars")
    # Should either work or fail with service unavailable
    assert response.status_code in [200, 503]
