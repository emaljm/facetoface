from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
import os
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS middleware to allow frontend like Vapi to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["https://studio.vapi.ai"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret token from environment variable (set this in Render dashboard)
SECRET_TOKEN = os.getenv("secret_key", "default_token")

# SQLite database setup
DATABASE_URL = "sqlite:///./appointments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database model
class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    service = Column(String)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# Pydantic models for request and response
class AppointmentRequest(BaseModel):
    name: str
    date: str
    time: str
    service: str

class AppointmentResponse(BaseModel):
    success: bool
    message: str
    appointment_id: str

# Endpoint to book appointment
@app.post("/book", response_model=AppointmentResponse)
def book_appointment(
    request: AppointmentRequest,
    authorization: str = Header(...)
):
    # Logging the request
    logging.info(f"Request: {request.dict()}")
    logging.info(f"Authorization: {authorization}")

    # Validate the token
    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Generate appointment ID
    appointment_id = str(uuid.uuid4())

    # Save to database
    db = SessionLocal()
    appointment = Appointment(
        appointment_id=appointment_id,
        name=request.name,
        date=request.date,
        time=request.time,
        service=request.service
    )
    db.add(appointment)
    db.commit()
    db.close()

    # Return the response
    return JSONResponse(
        content={
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment_id": appointment_id
        }
    )
