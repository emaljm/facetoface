from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
import os

app = FastAPI()

# Environment variable from Render
SECRET_TOKEN = os.getenv("secret_key", "default_token")

# Database setup
DATABASE_URL = "sqlite:///./appointments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB Model
class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    service = Column(String)

Base.metadata.create_all(bind=engine)

# Request schema
class AppointmentRequest(BaseModel):
    name: str
    date: str
    time: str
    type: str

# Response schema
class AppointmentResponse(BaseModel):
    success: bool
    message: str
    appointment_id: str

# Route to book appointment
@app.post("/book", response_model=AppointmentResponse)
def book_appointment(
    request: AppointmentRequest,
    authorization: str = Header(...)
):
    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    appointment_id = str(uuid.uuid4())

    # Save to DB
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

    return {
        "success": True,
        "message": "Appointment booked successfully.",
        "appointment_id": appointment_id
    }
