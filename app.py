from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Treatment, Doctor, Procedure, Factor, Review, WelcomeMessage, SessionLocal, CLINIC_DATA
from dotenv import load_dotenv
import os
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI(title="Clinic Review Kiosk", version="2.0.0")

# Add session middleware for language selection and other session data
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super-secret-key"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
# templates = Jinja2Templates(directory="templates")

# Initialize database with default data
def init_db():
    db = SessionLocal()
    try:
        # Allow disabling seeding for production/live deployments
        if os.getenv("SKIP_DB_SEED", "false").lower() in ("1", "true", "yes"): 
            return
        # Add default procedures if they don't exist
        existing_procedures = db.query(Procedure).count()
        if existing_procedures == 0:
            for procedure_data in CLINIC_DATA["procedures"]:
                procedure = Procedure(
                    name_en=procedure_data["name_en"],
                    name_ar=procedure_data["name_ar"]
                )
                db.add(procedure)
            db.commit()
        
        # Add default doctors if they don't exist
        existing_doctors = db.query(Doctor).count()
        if existing_doctors == 0:
            for doctor_data in CLINIC_DATA["doctors"]:
                doctor = Doctor(
                    name_en=doctor_data["name_en"],
                    name_ar=doctor_data["name_ar"]
                )
                db.add(doctor)
            db.commit()
        
        # Add default factors if they don't exist
        existing_factors = db.query(Factor).count()
        if existing_factors == 0:
            for factor_data in CLINIC_DATA["factors"]:
                factor = Factor(
                    name_en=factor_data["name_en"],
                    name_ar=factor_data["name_ar"]
                )
                db.add(factor)
            db.commit()
        
        # Add default welcome messages if they don't exist
        existing_messages = db.query(WelcomeMessage).count()
        if existing_messages == 0:
            for procedure_name, message in CLINIC_DATA["welcome_messages"].items():
                welcome_msg = WelcomeMessage(procedure_name=procedure_name, message=message)
                db.add(welcome_msg)
            db.commit()
        
        # Set up doctor-procedure relationships
        doctors = db.query(Doctor).all()
        procedures = db.query(Procedure).all()
        
        for doctor in doctors:
            if len(doctor.procedures) == 0:  # Only if not already set
                doctor_data = next((d for d in CLINIC_DATA["doctors"] if d["name_en"] == doctor.name_en), None)
                if doctor_data:
                    for procedure_name in doctor_data["procedures"]:
                        procedure = next((p for p in procedures if p.name_en == procedure_name), None)
                        if procedure:
                            doctor.procedures.append(procedure)
        
        # Keep legacy treatments for backwards compatibility
        existing_treatments = db.query(Treatment).count()
        if existing_treatments == 0:
            for procedure_data in CLINIC_DATA["procedures"]:
                treatment = Treatment(name=procedure_data["name_en"])
                db.add(treatment)
        
        db.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Import routes
from routes import router as routes_router
app.include_router(routes_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 