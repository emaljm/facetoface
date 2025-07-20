from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

# Replace this with your actual token (to be generated later)
SECRET_TOKEN = "your_secret_token_here"

class AppointmentRequest(BaseModel):
    customer_name: str
    appointment_date: str
    appointment_time: str
    service_type: str

class AppointmentResponse(BaseModel):
    success: bool
    message: str
    appointment_id: str

@app.post("/book", response_model=AppointmentResponse)
def book_appointment(request: AppointmentRequest, authorization: str = Header(...)):
    # Check token
    if authorization != f"Bearer {SECRET_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Generate appointment ID
    appointment_id = str(uuid.uuid4())

    # Here you'd normally save the appointment to a database

    return {
        "success": True,
        "message": "Appointment booked successfully.",
        "appointment_id": appointment_id
    }
