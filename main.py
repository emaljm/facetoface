# from fastapi import FastAPI, Header, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from typing import List
# import uuid
# import os
# import logging

# # Enable logging
# logging.basicConfig(level=logging.INFO)

# app = FastAPI()

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins for now
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Secret token (use Render dashboard to set "secret_key")
# SECRET_TOKEN = os.getenv("Bearer secret_key", "default_token")

# # SQLite DB config
# DATABASE_URL = "sqlite:///./appointments.db"
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Base = declarative_base()
# SessionLocal = sessionmaker(bind=engine)

# # SQLAlchemy model
# class Appointment(Base):
#     __tablename__ = "appointments"
#     appointment_id = Column(String, primary_key=True, index=True)
#     name = Column(String)
#     date = Column(String)
#     time = Column(String)
#     service = Column(String)

# # Create table
# Base.metadata.create_all(bind=engine)

# # Request model
# class AppointmentRequest(BaseModel):
#     name: str
#     date: str
#     time: str
#     service: str

# # Response model for booking
# class AppointmentResponse(BaseModel):
#     success: bool
#     message: str
#     appointment_id: str

# # Response model for GET /appointments
# class AppointmentOut(BaseModel):
#     appointment_id: str
#     name: str
#     date: str
#     time: str
#     service: str

# # POST /book endpoint
# @app.post("/book", response_model=AppointmentResponse)
# def book_appointment(request: AppointmentRequest, authorization: str = Header(...)):
#     logging.info(f"Request: {request.dict()}")
#     logging.info(f"Authorization: {authorization}")

#     if authorization != f"Bearer {SECRET_TOKEN}":
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     appointment_id = str(uuid.uuid4())

#     db = SessionLocal()
#     appointment = Appointment(
#         appointment_id=appointment_id,
#         name=request.name,
#         date=request.date,
#         time=request.time,
#         service=request.service
#     )
#     db.add(appointment)
#     db.commit()
#     db.close()

#     return JSONResponse(
#         content={
#             "success": True,
#             "message": "Appointment booked successfully.",
#             "appointment_id": appointment_id
#         }
#     )

# # GET /appointments endpoint
# @app.get("/appointments", response_model=List[AppointmentOut])
# def get_all_appointments(authorization: str = Header(...)):
#     if authorization != f"Bearer {SECRET_TOKEN}":
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     db = SessionLocal()
#     appointments = db.query(Appointment).all()
#     db.close()

#     return [
#         AppointmentOut(
#             appointment_id=a.appointment_id,
#             name=a.name,
#             date=a.date,
#             time=a.time,
#             service=a.service
#         ) for a in appointments
#     ]
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
import uuid
import os
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correct secret token handling
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "secret_key")

# SQLite DB setup
DATABASE_URL = "sqlite:///./appointments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# SQLAlchemy model
class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    service = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class AppointmentRequest(BaseModel):
    name: str
    date: str
    time: str
    service: str

class AppointmentResponse(BaseModel):
    success: bool
    message: str
    appointment_id: str

class AppointmentOut(BaseModel):
    appointment_id: str
    name: str
    date: str
    time: str
    service: str

# POST /book
@app.post("/book", response_model=AppointmentResponse)
def book_appointment(request: AppointmentRequest, authorization: str = Header(...)):
    logging.info(f"Incoming appointment request: {request.dict()}")
    logging.info(f"Authorization received: {authorization}")

    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    appointment_id = str(uuid.uuid4())

    db = SessionLocal()
    try:
        appointment = Appointment(
            appointment_id=appointment_id,
            name=request.name,
            date=request.date,
            time=request.time,
            service=request.service
        )
        db.add(appointment)
        db.commit()
    finally:
        db.close()

    return JSONResponse(
        content={
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment_id": appointment_id
        }
    )



# GET /appointmentss
@app.get("/appointments", response_model=List[AppointmentOut])
def get_all_appointments(authorization: str = Header(...)):
    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = SessionLocal()
    try:
        appointments = db.query(Appointment).all()
    finally:
        db.close()

    return [
        AppointmentOut(
            appointment_id=a.appointment_id,
            name=a.name,
            date=a.date,
            time=a.time,
            service=a.service
        ) for a in appointments
    ]
