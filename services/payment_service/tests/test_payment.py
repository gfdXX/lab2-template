import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid

# Mock the database connection at import time
with patch('main.engine'), patch('main.SessionLocal'):
    from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

# def test_create_payment():
#     response = client.post("/api/v1/payments", json={"price": 1000})
#     assert response.status_code == 201
#     data = response.json()
#     assert "paymentUid" in data
#     assert data["price"] == 1000
#     assert data["status"] == "PAID"

@patch('main.get_db')
def test_get_payment_not_found(mock_get_db):
    # Mock database session to return None (payment not found)
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None
    
    test_uuid = uuid.uuid4()
    response = client.get(f"/api/v1/payments/{test_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"
