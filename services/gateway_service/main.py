from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import os

# FastAPI app
app = FastAPI(title="Gateway Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
CARS_SERVICE_URL = os.getenv("CARS_SERVICE_URL", "http://cars-service:8070")
RENTAL_SERVICE_URL = os.getenv("RENTAL_SERVICE_URL", "http://rental-service:8060")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8050")

# Pydantic models
class RentalRequest(BaseModel):
    carUid: str
    dateFrom: str
    dateTo: str

def get_username(x_user_name: str = Header(None)):
    if not x_user_name:
        raise HTTPException(status_code=400, detail="X-User-Name header is required")
    return x_user_name

@app.get("/manage/health")
async def health_check():
    return {"status": "OK"}

@app.get("/api/v1/cars")
async def get_cars(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    show_all: bool = Query(False)
):
    """Get list of available cars"""
    try:
        # Convert page from 1-based to 0-based for internal services
        internal_page = page - 1 if page > 0 else 0
        response = requests.get(
            f"{CARS_SERVICE_URL}/api/v1/cars",
            params={"page": internal_page, "pageSize": size, "showAll": show_all}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Cars service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Cars service unavailable")

@app.get("/api/v1/cars/{car_uid}")
async def get_car(car_uid: str):
    """Get car by UID"""
    try:
        response = requests.get(f"{CARS_SERVICE_URL}/api/v1/cars/{car_uid}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Car not found")
        else:
            raise HTTPException(status_code=response.status_code, detail="Cars service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Cars service unavailable")

@app.get("/api/v1/rental")
async def get_rentals(
    username: str = Depends(get_username),
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get all rentals for user"""
    try:
        response = requests.get(
            f"{RENTAL_SERVICE_URL}/api/v1/rental",
            params={"page": page, "pageSize": page_size},
            headers={"X-User-Name": username}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Rental service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Rental service unavailable")

@app.get("/api/v1/rental/{rental_uid}")
async def get_rental(rental_uid: str, username: str = Depends(get_username)):
    """Get rental by UID"""
    try:
        response = requests.get(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            headers={"X-User-Name": username}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        else:
            raise HTTPException(status_code=response.status_code, detail="Rental service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Rental service unavailable")

@app.post("/api/v1/rental")
async def create_rental(rental_request: RentalRequest, username: str = Depends(get_username)):
    """Create new rental"""
    try:
        response = requests.post(
            f"{RENTAL_SERVICE_URL}/api/v1/rental",
            json=rental_request.dict(),
            headers={"X-User-Name": username}
        )
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Rental service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Rental service unavailable")

@app.post("/api/v1/rental/{rental_uid}/finish")
async def finish_rental(rental_uid: str, username: str = Depends(get_username)):
    """Finish rental"""
    try:
        response = requests.post(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}/finish",
            headers={"X-User-Name": username}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        else:
            raise HTTPException(status_code=response.status_code, detail="Rental service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Rental service unavailable")

@app.delete("/api/v1/rental/{rental_uid}")
async def cancel_rental(rental_uid: str, username: str = Depends(get_username)):
    """Cancel rental"""
    try:
        response = requests.delete(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            headers={"X-User-Name": username}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        else:
            raise HTTPException(status_code=response.status_code, detail="Rental service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Rental service unavailable")

@app.delete("/api/v1/rental/{rental_uid}")
async def cancel_rental(
    rental_uid: str,
    username: str = Depends(get_username)
):
    """Cancel rental"""
    try:
        response = requests.delete(
            f"{RENTAL_SERVICE_URL}/api/v1/rental/{rental_uid}",
            headers={"X-User-Name": username}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rental not found")
        else:
            raise HTTPException(status_code=response.status_code, detail="Rental service error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Rental service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
