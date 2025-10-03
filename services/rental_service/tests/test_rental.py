import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
import os

# Set test environment variable to avoid database connection
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

# Mock the database connection
with patch('services.rental_service.main.engine'), patch('services.rental_service.main.SessionLocal'):
    from services.rental_service.main import app

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

def test_create_rental_endpoint():
    """Test rental creation endpoint structure"""
    rental_data = {
        "carUid": str(uuid.uuid4()),
        "dateFrom": "2024-01-01",
        "dateTo": "2024-01-05"
    }
    response = client.post("/api/v1/rental", json=rental_data, headers={"X-User-Name": "testuser"})
    # Should either work or fail with service unavailable
    assert response.status_code in [200, 503]
