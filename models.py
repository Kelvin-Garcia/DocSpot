from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Changed to String to match frontend "doc_1", "pac_1"
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # In a real app, this would be hashed
    role = Column(String, nullable=False) # "doctor" or "paciente"
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    clinic = Column(String, nullable=True) # Only for doctors

    appointments_as_doctor = relationship("Appointment", back_populates="doctor", foreign_keys="[Appointment.doctor_id]")
    appointments_as_patient = relationship("Appointment", back_populates="patient", foreign_keys="[Appointment.patient_id]")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', role='{self.role}')>"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, index=True) # Changed to String to match frontend "apt_1"
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    doctor_name = Column(String, nullable=False)
    clinic = Column(String, nullable=False)
    service = Column(String, nullable=False)
    time = Column(String, nullable=False) # Consider using DateTime for better handling
    date = Column(String, nullable=False) # Consider using Date for better handling
    price = Column(Float, nullable=False)
    commission = Column(Float, nullable=False, default=2.0)
    status = Column(String, nullable=False, default="available") # "available", "reserved", "completed"
    patient_id = Column(String, ForeignKey("users.id"), nullable=True)
    patient_name = Column(String, nullable=True)
    payment_status = Column(String, nullable=True) # "paid", "pending" (mocked)
    payment_date = Column(DateTime, nullable=True)

    doctor = relationship("User", back_populates="appointments_as_doctor", foreign_keys=[doctor_id])
    patient = relationship("User", back_populates="appointments_as_patient", foreign_keys=[patient_id])

    def __repr__(self):
        return f"<Appointment(id='{self.id}', doctor_id='{self.doctor_id}', service='{self.service}', status='{self.status}')>"
