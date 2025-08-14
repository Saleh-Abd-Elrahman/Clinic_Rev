from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Table, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinic_reviews.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
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
    name_en = Column(String, index=True)
    name_ar = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Many-to-many relationship with procedures
    procedures = relationship("Procedure", secondary=doctor_procedure_association, back_populates="doctors")
    
    # Helper method to get name in specific language
    def get_name(self, language="en"):
        if language == "ar":
            return self.name_ar or self.name_en
        return self.name_en or self.name_ar

class Procedure(Base):
    __tablename__ = "procedures"
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String, index=True)
    name_ar = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship with doctors
    doctors = relationship("Doctor", secondary=doctor_procedure_association, back_populates="procedures")
    
    # Helper method to get name in specific language
    def get_name(self, language="en"):
        if language == "ar":
            return self.name_ar or self.name_en
        return self.name_en or self.name_ar

class Factor(Base):
    __tablename__ = "factors"
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String, index=True)
    name_ar = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Helper method to get name in specific language
    def get_name(self, language="en"):
        if language == "ar":
            return self.name_ar or self.name_en
        return self.name_en or self.name_ar

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    procedure_id = Column(Integer, ForeignKey('procedures.id'))  # Keep for backward compatibility
    procedure_ids = Column(Text, nullable=True)  # JSON string of multiple procedure IDs
    rating = Column(Integer)
    feedback = Column(Text, nullable=True)
    additional_comments = Column(Text, nullable=True)
    message_to_doctor = Column(Text, nullable=True)
    selected_factors = Column(Text, nullable=True)  # JSON string of selected factor IDs
    selected_staff = Column(Text, nullable=True)  # JSON string of selected staff (doctor, coordinator, nursing_team)
    all_staff_selected = Column(Boolean, default=False)  # True if all staff are selected (for "Dr. Name and her team" logic)
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

# Default clinic data - now with bilingual structure
CLINIC_DATA = {
    "procedures": [
        {"name_en": "Morpheus", "name_ar": "مورفيوس"},
        {"name_en": "Endolift (face)", "name_ar": "اندولفت (الوجه)"},
        {"name_en": "Endolift (neck)", "name_ar": "اندولفت (الرقبة)"},
        {"name_en": "Endolift (body)", "name_ar": "اندولفت (الجسم)"},
        {"name_en": "Filler", "name_ar": "فيلر"},
        {"name_en": "Botox", "name_ar": "بوتوكس"},
        {"name_en": "Bloom", "name_ar": "بلوم"},
        {"name_en": "Profhilo", "name_ar": "بروفايلو"},
        {"name_en": "Volite", "name_ar": "فولايت"},
        {"name_en": "Innovyal", "name_ar": "انوفيال"},
        {"name_en": "Fractional", "name_ar": "فراكشنال"},
        {"name_en": "Radiesse", "name_ar": "رادييس"},
        {"name_en": "Sculptra", "name_ar": "سكلبترا"},
        {"name_en": "Rich", "name_ar": "ريتش"},
        {"name_en": "Salmon PDRN", "name_ar": "سالمون"},
        {"name_en": "Subcision", "name_ar": "تقطيع ندبات"},
        {"name_en": "Growth Factors", "name_ar": "محفزات نمو"},
        {"name_en": "Magellan", "name_ar": "ماجيلان"},
        {"name_en": "Regenera", "name_ar": "ريجينيرا"},
        {"name_en": "Exosome", "name_ar": "اكسوزوم"},
        {"name_en": "Minoxidil", "name_ar": "مينوكسديل"},
        {"name_en": "Dutasteride", "name_ar": "دوتاستيرايد"},
        {"name_en": "Other", "name_ar": "أخرى"}
    ],
    "doctors": [
        {"name_en": "Dr. Sarah", "name_ar": "دكتورة سارة", "procedures": ["Morpheus", "Endolift (face)", "Endolift (neck)", "Endolift (body)", "Filler", "Botox", "Bloom", "Profhilo", "Volite", "Innovyal", "Fractional", "Radiesse", "Sculptra", "Rich", "Salmon PDRN", "Subcision", "Growth Factors", "Magellan", "Regenera", "Exosome", "Minoxidil", "Dutasteride", "Other"]},
        {"name_en": "Other", "name_ar": "أخرى", "procedures": ["Other"]}
    ],
    "factors": [
        {"name_en": "Professional staff", "name_ar": "طاقم مهني"},
        {"name_en": "Clean facility", "name_ar": "منشأة نظيفة"},
        {"name_en": "Short wait times", "name_ar": "أوقات انتظار قصيرة"},
        {"name_en": "Clear communication", "name_ar": "تواصل واضح"},
        {"name_en": "Comfortable environment", "name_ar": "بيئة مريحة"},
        {"name_en": "Modern equipment", "name_ar": "معدات حديثة"},
        {"name_en": "Friendly reception", "name_ar": "استقبال ودود"},
        {"name_en": "Thorough care", "name_ar": "رعاية شاملة"},
        {"name_en": "Pain-free procedure", "name_ar": "إجراء خالي من الألم"},
        {"name_en": "Excellent results", "name_ar": "نتائج ممتازة"},
        {"name_en": "Great value", "name_ar": "قيمة رائعة"},
        {"name_en": "Follow-up care", "name_ar": "رعاية المتابعة"}
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