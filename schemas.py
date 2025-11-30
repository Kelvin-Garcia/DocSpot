from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr
    phone: str
    role: str # "doctor" or "paciente"

class UserCreate(UserBase):
    password: str
    clinic: Optional[str] = None # Only for doctors

class UserLogin(BaseModel):
    username: str
    password: str
    role: str

class User(UserBase):
    id: str
    clinic: Optional[str] = None

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    doctor_id: str
    doctor_name: str
    clinic: str
    service: str
    time: str
    date: str
    price: float
    commission: float = 2.0
    status: str = "available" # "available", "reserved", "completed"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentReserve(BaseModel):
    patient_id: str
    patient_name: str
    payment_status: str = "paid" # Mocked for now
    payment_date: datetime = datetime.now()

class Appointment(AppointmentBase):
    id: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    payment_status: Optional[str] = None
    payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True
