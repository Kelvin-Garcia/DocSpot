from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid # For generating unique IDs
from datetime import datetime

import models, schemas
from database import SessionLocal, engine, get_db
# Create all tables defined in models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permite peticiones desde estos orígenes
    allow_credentials=True,       # Permite cookies/headers de autenticación
    allow_methods=["*"],          # Permite todos los métodos (GET, POST, DELETE, etc.)
    allow_headers=["*"],          # Permite todos los headers
)

@app.get("/")
async def root():
    return {"message": "Backend DocSpot Odonto is running!"}

# Test endpoint to check database connection
@app.get("/test-db")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"message": "Database connection successful!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database connection failed: {e}")

@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    # For a real application, passwords should be hashed (e.g., using bcrypt)
    # Here, we store it in plaintext as per the mockup nature of the project.
    new_user_id = str(uuid.uuid4())
    if user.role == "doctor":
        new_user_id = f"doc_{uuid.uuid4().hex[:8]}" # Shorter ID for demo purpose
    elif user.role == "paciente":
        new_user_id = f"pac_{uuid.uuid4().hex[:8]}" # Shorter ID for demo purpose

    db_user = models.User(
        id=new_user_id,
        username=user.username,
        password=user.password, # Storing plaintext password for mockup
        role=user.role,
        name=user.name,
        email=user.email,
        phone=user.phone,
        clinic=user.clinic if user.role == "doctor" else None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.User)
async def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user_credentials.username).first()

    if not db_user or db_user.password != user_credentials.password or db_user.role != user_credentials.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials or role")
    
    return db_user

# --- Appointment Endpoints ---

@app.post("/appointments", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    # Check if doctor exists and is actually a doctor
    doctor = db.query(models.User).filter(models.User.id == appointment.doctor_id, models.User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found or is not a doctor")

    new_appointment_id = f"apt_{uuid.uuid4().hex[:8]}"
    db_appointment = models.Appointment(
        id=new_appointment_id,
        doctor_id=appointment.doctor_id,
        doctor_name=doctor.name,
        clinic=doctor.clinic,
        service=appointment.service,
        time=appointment.time,
        date=appointment.date,
        price=appointment.price,
        commission=appointment.commission,
        status="available",
        patient_id=None,
        patient_name=None,
        payment_status=None,
        payment_date=None,
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/doctors/{doctor_id}/appointments", response_model=List[schemas.Appointment])
async def get_doctor_appointments(doctor_id: str, db: Session = Depends(get_db)):
    doctor = db.query(models.User).filter(models.User.id == doctor_id, models.User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    appointments = db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()
    return appointments

@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    # Optional: Add logic to check if the current user is the doctor who owns the appointment
    # For now, any doctor can cancel any appointment.

    db.delete(db_appointment)
    db.commit()
    return {"message": "Appointment cancelled successfully"}

@app.get("/appointments", response_model=List[schemas.Appointment])
async def get_available_appointments(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Appointment)
    if status:
        query = query.filter(models.Appointment.status == status)
    
    appointments = query.all()
    return appointments

@app.get("/patients/{patient_id}/appointments", response_model=List[schemas.Appointment])
async def get_patient_reservations(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(models.User).filter(models.User.id == patient_id, models.User.role == "paciente").first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found or is not a patient")
    
    reservations = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()
    return reservations

@app.post("/appointments/{appointment_id}/reserve", response_model=schemas.Appointment)
async def reserve_appointment(appointment_id: str, reservation_details: schemas.AppointmentReserve, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    if db_appointment.status != "available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment is not available for reservation")
    
    patient = db.query(models.User).filter(models.User.id == reservation_details.patient_id, models.User.role == "paciente").first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found or is not a patient")

    db_appointment.status = "reserved"
    db_appointment.patient_id = reservation_details.patient_id
    db_appointment.patient_name = patient.name
    db_appointment.payment_status = reservation_details.payment_status
    db_appointment.payment_date = reservation_details.payment_date
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment