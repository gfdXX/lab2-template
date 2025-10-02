import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

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

def test_get_payment_not_found():
    # Use a random UUID that doesn't exist in the database
    test_uuid = uuid.uuid4()
    response = client.get(f"/api/v1/payments/{test_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"
