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
    # appointment_id = str(uuid.uuid4())
    appointment_id = 12345
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




#check

# Pydantic model for checking appointment
class CheckRequest(BaseModel):
    appointment_id: str

class CheckResponse(BaseModel):
    success: bool
    message: str
    appointment_details: dict | None = None

# Endpoint to check appointment
@app.post("/check", response_model=CheckResponse)
def check_appointment(
    request: CheckRequest,
    authorization: str = Header(...)
):
    logging.info(f"Check Request: {request.dict()}")
    logging.info(f"Authorization: {authorization}")

    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = SessionLocal()
    appointment = db.query(Appointment).filter(Appointment.appointment_id == request.appointment_id).first()
    db.close()

    if not appointment:
        return JSONResponse(
            content={
                "success": False,
                "message": "Appointment not found.",
                "appointment_details": None
            }
        )

    return JSONResponse(
        content={
            "success": True,
            "message": "Appointment found.",
            "appointment_details": {
                "name": appointment.name,
                "date": appointment.date,
                "time": appointment.time,
                "service": appointment.service
            }
        }
    )


#cancel
# Pydantic model for cancel request and response
class CancelRequest(BaseModel):
    appointment_id: str

class CancelResponse(BaseModel):
    success: bool
    message: str

# Endpoint to cancel appointment
@app.post("/cancel", response_model=CancelResponse)
def cancel_appointment(
    request: CancelRequest,
    authorization: str = Header(...)
):
    logging.info(f"Cancel Request: {request.dict()}")
    logging.info(f"Authorization: {authorization}")

    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = SessionLocal()
    appointment = db.query(Appointment).filter(Appointment.appointment_id == request.appointment_id).first()

    if not appointment:
        db.close()
        return JSONResponse(
            content={
                "success": False,
                "message": "Appointment not found."
            }
        )

    db.delete(appointment)
    db.commit()
    db.close()

    return JSONResponse(
        content={
            "success": True,
            "message": "Appointment cancelled successfully."
        }
    )
#reschedule
from typing import Optional

# Pydantic model for reschedule request and response
class RescheduleRequest(BaseModel):
    appointment_id: str
    name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    service: Optional[str] = None
class RescheduleResponse(BaseModel):
    success: bool
    message: str
    updated_details: dict | None = None

@app.post("/reschedule", response_model=RescheduleResponse)
def reschedule_appointment(
    request: RescheduleRequest,
    authorization: str = Header(...)
):
    logging.info(f"Reschedule Request: {request.dict()}")
    logging.info(f"Authorization: {authorization}")

    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = SessionLocal()
    appointment = db.query(Appointment).filter(Appointment.appointment_id == request.appointment_id).first()

    # Just in case — fail silently if not found
    if not appointment:
        db.close()
        return JSONResponse(
            content={
                "success": False,
                "message": "Something went wrong. Could not update.",
                "updated_details": None
            }
        )

    # Update only the fields provided
    updated_fields = {}
    if request.name is not None:
        appointment.name = request.name
        updated_fields["name"] = request.name
    else:
        updated_fields["name"] = appointment.name

    if request.date is not None:
        appointment.date = request.date
        updated_fields["date"] = request.date
    else:
        updated_fields["date"] = appointment.date

    if request.time is not None:
        appointment.time = request.time
        updated_fields["time"] = request.time
    else:
        updated_fields["time"] = appointment.time

    if request.service is not None:
        appointment.service = request.service
        updated_fields["service"] = request.service
    else:
        updated_fields["service"] = appointment.service

    db.commit()
    db.refresh(appointment)
    db.close()

    return JSONResponse(
        content={
            "success": True,
            "message": "Appointment updated successfully.",
            "updated_details": updated_fields
        }
    )
