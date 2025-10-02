from fastapi import FastAPI, HTTPException, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from uuid import UUID
import os
import requests

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://program:test@localhost:5432/rentals")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class Rental(Base):
    __tablename__ = "rental"
    
    id = Column(Integer, primary_key=True, index=True)
    rental_uid = Column(PostgresUUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    username = Column(String(80), nullable=False)
    payment_uid = Column(PostgresUUID(as_uuid=True), nullable=False)
    car_uid = Column(PostgresUUID(as_uuid=True), nullable=False)
    date_from = Column(DateTime, nullable=False)
    date_to = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="IN_PROGRESS")

# Pydantic models
class RentalRequest(BaseModel):
    carUid: UUID
    dateFrom: str
    dateTo: str

class RentalResponse(BaseModel):
    rentalUid: UUID
    status: str
    dateFrom: str
    dateTo: str
    car: dict
    payment: dict

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str
        }

class RentalListResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: List[RentalResponse]

# Create tables (will be created when first request comes)
# Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Rental Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    # Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
    except:
        pass  # Tables might already exist
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_username(x_user_name: str = Header(None)):
    if not x_user_name:
        raise HTTPException(status_code=400, detail="X-User-Name header is required")
    return x_user_name

@app.get("/manage/health")
async def health_check():
    return {"status": "OK"}

@app.get("/api/v1/rental", response_model=RentalListResponse)
async def get_rentals(
    username: str = Depends(get_username),
    page: int = 0,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Get all rentals for user"""
    query = db.query(Rental).filter(Rental.username == username)
    total = query.count()
    rentals = query.offset(page * page_size).limit(page_size).all()
    
    items = []
    for rental in rentals:
        # Get car info from Cars Service
        try:
            car_response = requests.get(f"http://cars-service:8070/api/v1/cars/{rental.car_uid}")
            car_data = car_response.json() if car_response.status_code == 200 else {}
        except:
            car_data = {}
        
        # Get payment info from Payment Service
        try:
            payment_response = requests.get(f"http://payment-service:8050/api/v1/payments/{rental.payment_uid}")
            payment_data = payment_response.json() if payment_response.status_code == 200 else {}
        except:
            payment_data = {}
        
        items.append(RentalResponse(
            rentalUid=rental.rental_uid,
            status=rental.status,
            dateFrom=rental.date_from.isoformat(),
            dateTo=rental.date_to.isoformat(),
            car=car_data,
            payment=payment_data
        ))
    
    return RentalListResponse(
        page=page,
        pageSize=page_size,
        totalElements=total,
        items=items
    )

@app.get("/api/v1/rental/{rental_uid}", response_model=RentalResponse)
async def get_rental(
    rental_uid: UUID,
    username: str = Depends(get_username),
    db: Session = Depends(get_db)
):
    """Get rental by UID"""
    rental = db.query(Rental).filter(
        Rental.rental_uid == rental_uid,
        Rental.username == username
    ).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Get car info from Cars Service
    try:
        car_response = requests.get(f"http://cars-service:8070/api/v1/cars/{rental.car_uid}")
        car_data = car_response.json() if car_response.status_code == 200 else {}
    except:
        car_data = {}
    
    # Get payment info from Payment Service
    try:
        payment_response = requests.get(f"http://payment-service:8050/api/v1/payments/{rental.payment_uid}")
        payment_data = payment_response.json() if payment_response.status_code == 200 else {}
    except:
        payment_data = {}
    
    return RentalResponse(
        rentalUid=rental.rental_uid,
        status=rental.status,
        dateFrom=rental.date_from.isoformat(),
        dateTo=rental.date_to.isoformat(),
        car=car_data,
        payment=payment_data
    )

@app.post("/api/v1/rental", response_model=RentalResponse)
async def create_rental(
    rental_request: RentalRequest,
    username: str = Depends(get_username),
    db: Session = Depends(get_db)
):
    """Create new rental"""
    # Check if car exists and is available
    try:
        car_response = requests.get(f"http://cars-service:8070/api/v1/cars/{rental_request.carUid}")
        if car_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Car not found")
        car_data = car_response.json()
        if not car_data.get("available", False):
            raise HTTPException(status_code=400, detail="Car is not available")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Cars service unavailable")
    
    # Calculate rental days and price
    date_from = datetime.fromisoformat(rental_request.dateFrom.replace('Z', '+00:00'))
    date_to = datetime.fromisoformat(rental_request.dateTo.replace('Z', '+00:00'))
    rental_days = (date_to - date_from).days
    total_price = car_data["price"] * rental_days
    
    # Create payment
    try:
        payment_data = {"price": total_price}
        payment_response = requests.post(
            "http://payment-service:8050/api/v1/payments",
            json=payment_data
        )
        if payment_response.status_code != 201:
            raise HTTPException(status_code=503, detail="Payment service unavailable")
        payment_info = payment_response.json()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    # Reserve car
    try:
        requests.patch(
            f"http://cars-service:8070/api/v1/cars/{rental_request.carUid}/availability",
            params={"available": False}
        )
    except requests.RequestException:
        # Rollback payment if car reservation fails
        try:
            requests.delete(f"http://payment-service:8050/api/v1/payments/{payment_info['paymentUid']}")
        except:
            pass
        raise HTTPException(status_code=503, detail="Cars service unavailable")
    
    # Create rental record
    rental = Rental(
        username=username,
        payment_uid=payment_info["paymentUid"],
        car_uid=rental_request.carUid,
        date_from=date_from,
        date_to=date_to,
        status="IN_PROGRESS"
    )
    
    db.add(rental)
    db.commit()
    db.refresh(rental)
    
    return RentalResponse(
        rentalUid=rental.rental_uid,
        status=rental.status,
        dateFrom=rental.date_from.isoformat(),
        dateTo=rental.date_to.isoformat(),
        car=car_data,
        payment=payment_info
    )

@app.post("/api/v1/rental/{rental_uid}/finish")
async def finish_rental(
    rental_uid: UUID,
    username: str = Depends(get_username),
    db: Session = Depends(get_db)
):
    """Finish rental"""
    rental = db.query(Rental).filter(
        Rental.rental_uid == rental_uid,
        Rental.username == username
    ).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    if rental.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Rental is not in progress")
    
    # Release car
    try:
        requests.patch(
            f"http://cars-service:8070/api/v1/cars/{rental.car_uid}/availability",
            params={"available": True}
        )
    except requests.RequestException:
        pass  # Continue even if car service is unavailable
    
    # Update rental status
    rental.status = "FINISHED"
    db.commit()
    
    return Response(status_code=204)

@app.delete("/api/v1/rental/{rental_uid}")
async def cancel_rental(
    rental_uid: UUID,
    username: str = Depends(get_username),
    db: Session = Depends(get_db)
):
    """Cancel rental"""
    rental = db.query(Rental).filter(
        Rental.rental_uid == rental_uid,
        Rental.username == username
    ).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    if rental.status == "CANCELED":
        raise HTTPException(status_code=400, detail="Rental already canceled")
    
    # Release car
    try:
        requests.patch(
            f"http://cars-service:8070/api/v1/cars/{rental.car_uid}/availability",
            params={"available": True}
        )
    except requests.RequestException:
        pass
    
    # Cancel payment
    try:
        requests.delete(f"http://payment-service:8050/api/v1/payments/{rental.payment_uid}")
    except requests.RequestException:
        pass
    
    # Update rental status
    rental.status = "CANCELED"
    db.commit()
    
    return Response(status_code=204)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8060)
