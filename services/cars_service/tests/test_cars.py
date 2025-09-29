import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid

# Mock the database connection
with patch('main.engine'), patch('main.SessionLocal'):
    from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

@patch('main.get_db')
def test_get_cars(mock_get_db):
    # Mock database session
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_query.count.return_value = 0
    mock_query.offset.return_value.limit.return_value.all.return_value = []
    mock_session.query.return_value = mock_query
    mock_get_db.return_value.__enter__.return_value = mock_session
    
    response = client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "pageSize" in data
    assert "totalElements" in data
    assert "items" in data

@patch('main.get_db')
def test_get_car_not_found(mock_get_db):
    # Mock database session
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query
    mock_get_db.return_value.__enter__.return_value = mock_session
    
    test_uuid = uuid.uuid4()
    response = client.get(f"/api/v1/cars/{test_uuid}")
    assert response.status_code == 404
