import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from services.gateway_service.main import app
import uuid

client = TestClient(app)

def test_health_check():
    """Test health endpoint returns OK status"""
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_get_rentals_missing_header():
    """Test rentals endpoint without required X-User-Name header"""
    response = client.get("/api/v1/rental")
    assert response.status_code == 400
    assert "X-User-Name header is required" in response.json()["detail"]

def test_get_cars_through_gateway():
    """Test cars endpoint through gateway with mocked service response"""
    mock_cars_data = {
        "page": 1,
        "pageSize": 20,
        "totalElements": 1,
        "items": [
            {
                "carUid": "109b42f3-198d-4c89-9276-a7520a7120ab",
                "brand": "Mercedes Benz",
                "model": "GLA 250",
                "registrationNumber": "ЛО777Х799",
                "power": 249,
                "price": 3500,
                "type": "SEDAN",
                "available": True
            }
        ]
    }
    
    with patch('services.gateway_service.main.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_cars_data
        mock_get.return_value = mock_response
        
        response = client.get("/api/v1/cars?page=1&size=20&show_all=false")
        
        assert response.status_code == 200
        data = response.json()
        assert data["totalElements"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["brand"] == "Mercedes Benz"
        assert data["items"][0]["available"] == True

def test_create_rental_through_gateway():
    """Test rental creation through gateway with mocked service response"""
    rental_data = {
        "carUid": "109b42f3-198d-4c89-9276-a7520a7120ab",
        "dateFrom": "2024-01-01",
        "dateTo": "2024-01-05"
    }
    
    mock_rental_response = {
        "rentalUid": str(uuid.uuid4()),
        "status": "IN_PROGRESS",
        "dateFrom": "2024-01-01",
        "dateTo": "2024-01-05",
        "carUid": "109b42f3-198d-4c89-9276-a7520a7120ab",
        "car": {
            "carUid": "109b42f3-198d-4c89-9276-a7520a7120ab",
            "brand": "Mercedes Benz",
            "model": "GLA 250",
            "price": 3500
        },
        "payment": {
            "paymentUid": str(uuid.uuid4()),
            "status": "PAID",
            "price": 14000
        }
    }
    
    with patch('services.gateway_service.main.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_rental_response
        mock_post.return_value = mock_response
        
        response = client.post(
            "/api/v1/rental", 
            json=rental_data, 
            headers={"X-User-Name": "testuser"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
        assert data["car"]["brand"] == "Mercedes Benz"
        assert data["payment"]["status"] == "PAID"
