from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Table, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./clinic_reviews.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for many-to-many relationship between doctors and procedures
doctor_procedure_association = Table(
    'doctor_procedures',
    Base.metadata,
    Column('doctor_id', Integer, ForeignKey('doctors.id'), primary_key=True),
    Column('procedure_id', Integer, ForeignKey('procedures.id'), primary_key=True)
)

# Database Models
class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Many-to-many relationship with procedures
    procedures = relationship("Procedure", secondary=doctor_procedure_association, back_populates="doctors")

class Procedure(Base):
    __tablename__ = "procedures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship with doctors
    doctors = relationship("Doctor", secondary=doctor_procedure_association, back_populates="procedures")

class Factor(Base):
    __tablename__ = "factors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    procedure_id = Column(Integer, ForeignKey('procedures.id'))
    rating = Column(Integer)
    feedback = Column(Text, nullable=True)
    additional_comments = Column(Text, nullable=True)
    message_to_doctor = Column(Text, nullable=True)
    selected_factors = Column(Text, nullable=True)  # JSON string of selected factor IDs
    ai_generated_reviews = Column(Text, nullable=True)  # JSON string of AI-generated reviews
    selected_review = Column(Text, nullable=True)  # Final selected review
    qr_code_data = Column(Text, nullable=True)  # QR code data/URL
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = relationship("Doctor")
    procedure = relationship("Procedure")

class WelcomeMessage(Base):
    __tablename__ = "welcome_messages"
    id = Column(Integer, primary_key=True, index=True)
    procedure_name = Column(String, unique=True, index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Legacy Treatment table for backwards compatibility
class Treatment(Base):
    __tablename__ = "treatments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "letmein")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Default clinic data
CLINIC_DATA = {
    "procedures": [
        "Morpheus", "Endolift (face)", "Endolift (neck)", "Endolift (body)",
        "Filler", "Botox", "Bloom", "Profhilo", "Volite", "Innovyal",
        "Fractional", "Radiesse", "Sculptra", "Rich", "Salmon PDRN",
        "Subcision", "Other"
    ],
    "doctors": [
        {"name": "Dr. Sarah", "procedures": ["Morpheus", "Endolift (face)", "Endolift (neck)", "Endolift (body)", "Filler", "Botox", "Bloom", "Profhilo", "Volite", "Innovyal", "Fractional", "Radiesse", "Sculptra", "Rich", "Salmon PDRN", "Subcision", "Other"]},
        {"name": "Other", "procedures": ["Other"]}
    ],
    "factors": [
        "Professional staff", "Clean facility", "Short wait times",
        "Clear communication", "Comfortable environment", "Modern equipment",
        "Friendly reception", "Thorough care", "Pain-free procedure",
        "Excellent results", "Great value", "Follow-up care"
    ],
    "welcome_messages": {
        "Morpheus": "Hi {name}! We hope your Morpheus treatment was comfortable and you're happy with the results.",
        "Endolift (face)": "Hi {name}! We hope your Endolift facial treatment went smoothly and you're pleased with the outcome.",
        "Endolift (neck)": "Hi {name}! We hope your Endolift neck treatment was successful and you're satisfied with the results.",
        "Endolift (body)": "Hi {name}! We hope your Endolift body treatment met your expectations and you're happy with the results.",
        "Filler": "Hi {name}! We hope your filler treatment went well and you're pleased with the natural-looking results.",
        "Botox": "Hi {name}! We hope your Botox treatment was comfortable and you're satisfied with the outcome.",
        "Bloom": "Hi {name}! We hope your Bloom treatment was a positive experience and you're happy with the results.",
        "Profhilo": "Hi {name}! We hope your Profhilo treatment went smoothly and you're pleased with the skin improvement.",
        "Volite": "Hi {name}! We hope your Volite treatment was comfortable and you're satisfied with the results.",
        "Innovyal": "Hi {name}! We hope your Innovyal treatment met your expectations and you're happy with the outcome.",
        "Fractional": "Hi {name}! We hope your Fractional treatment went well and you're pleased with the skin rejuvenation.",
        "Radiesse": "Hi {name}! We hope your Radiesse treatment was successful and you're satisfied with the results.",
        "Sculptra": "Hi {name}! We hope your Sculptra treatment was comfortable and you're happy with the gradual improvements.",
        "Rich": "Hi {name}! We hope your Rich treatment exceeded your expectations and you're pleased with the results.",
        "Salmon PDRN": "Hi {name}! We hope your Salmon PDRN treatment was comfortable and you're satisfied with the skin rejuvenation.",
        "Subcision": "Hi {name}! We hope your Subcision treatment went smoothly and you're pleased with the improvement in skin texture.",
        "Other": "Hi {name}! Thank you for visiting our clinic. We hope you received excellent care and attention."
    }
} 