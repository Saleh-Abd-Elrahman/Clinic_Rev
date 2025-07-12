from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import get_db, Treatment, Doctor, Procedure, Factor, Review, WelcomeMessage, ADMIN_PASSWORD, CLINIC_DATA
import qrcode
import io
import base64
import json
from datetime import datetime
from typing import List, Optional
import urllib.parse
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI configuration
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Place ID for reviews
GOOGLE_PLACE_ID = os.getenv("GOOGLE_PLACE_ID", "")

# Helper function to generate AI reviews
async def generate_ai_reviews(patient_name: str, procedure_name: str, doctor_name: str, rating: int, selected_factors: list, additional_comments: str = "") -> list:
    """Generate AI-powered review suggestions based on patient feedback."""
    try:
        # Build context from factors
        factors_text = ", ".join(selected_factors) if selected_factors else ""
        
        # Create prompt
        prompt = f"""
        Generate 4 different Google review texts for a medical clinic based on this patient feedback:
        - Patient: {patient_name}
        - Procedure: {procedure_name}
        - Doctor: {doctor_name}
        - Rating: {rating}/5 stars
        - What stood out: {factors_text}
        - Additional comments: {additional_comments}
        
        Each review should be:
        - Natural and authentic (1-3 sentences)
        - Positive and professional
        - Mention specific aspects from the feedback
        - Written in first person
        - Different in tone and style from the others
        
        Return only the review texts, one per line, no numbering or formatting.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes authentic, positive Google reviews for medical clinics based on patient feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        reviews = [review.strip() for review in content.split('\n') if review.strip()]
        
        # Ensure we have exactly 4 reviews
        if len(reviews) < 4:
            reviews.extend([
                f"Had an excellent experience with {doctor_name} for my {procedure_name} procedure. The staff was professional and the results exceeded my expectations.",
                f"Highly recommend this clinic! The {procedure_name} treatment was comfortable and the team was very caring.",
                f"Great experience at this clinic. {doctor_name} did an amazing job with my {procedure_name} procedure.",
                f"Professional service and excellent results. Very happy with my {procedure_name} treatment."
            ])
        
        return reviews[:4]  # Return only first 4
        
    except Exception as e:
        print(f"Error generating AI reviews: {e}")
        # Return fallback reviews
        return [
            f"Had an excellent experience with {doctor_name} for my {procedure_name} procedure. The staff was professional and the results exceeded my expectations.",
            f"Highly recommend this clinic! The {procedure_name} treatment was comfortable and the team was very caring.",
            f"Great experience at this clinic. {doctor_name} did an amazing job with my {procedure_name} procedure.",
            f"Professional service and excellent results. Very happy with my {procedure_name} treatment."
        ]

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Helper function to generate QR code
def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Helper function to check authentication
def check_auth(request: Request):
    if not request.cookies.get("authenticated"):
        return RedirectResponse(url="/", status_code=302)

# ============== MAIN ROUTES ==============

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/main-selection", status_code=302)
        response.set_cookie(key="authenticated", value="true", httponly=True, secure=False, samesite="lax")
        return response
    else:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "error": "Invalid password. Please try again."
        })

@router.get("/main-selection", response_class=HTMLResponse)
async def main_selection(request: Request):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    return templates.TemplateResponse("main_selection.html", {"request": request})

@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("authenticated", httponly=True)
    return response

# ============== PATIENT FLOW ROUTES ==============

@router.get("/patient-start", response_class=HTMLResponse)
async def patient_start(request: Request, db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    doctors = db.query(Doctor).all()
    
    # Check if there's only one doctor
    auto_select_doctor = len(doctors) == 1
    auto_doctor = doctors[0] if auto_select_doctor else None
    
    # Check if there's only one procedure for the auto-selected doctor
    auto_select_procedure = False
    auto_procedure = None
    if auto_doctor and len(auto_doctor.procedures) == 1:
        auto_select_procedure = True
        auto_procedure = auto_doctor.procedures[0]
    
    return templates.TemplateResponse("patient_start.html", {
        "request": request,
        "doctors": doctors,
        "auto_select_doctor": auto_select_doctor,
        "auto_doctor": auto_doctor,
        "auto_select_procedure": auto_select_procedure,
        "auto_procedure": auto_procedure
    })

@router.post("/patient-details")
async def patient_details(
    request: Request,
    patient_name: str = Form(...),
    doctor_id: int = Form(...),
    procedure_id: int = Form(...),
    message_to_doctor: str = Form(""),
    db: Session = Depends(get_db)
):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    # Get doctor and procedure details
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    
    if not doctor or not procedure:
        raise HTTPException(status_code=404, detail="Doctor or procedure not found")
    
    # Get welcome message
    welcome_msg = db.query(WelcomeMessage).filter(WelcomeMessage.procedure_name == procedure.name).first()
    welcome_text = welcome_msg.message.format(name=patient_name) if welcome_msg else f"Hi {patient_name}! Thank you for visiting our clinic."
    
    # Store session data for the survey
    session_data = {
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "procedure_id": procedure_id,
        "message_to_doctor": message_to_doctor,
        "doctor_name": doctor.name,
        "procedure_name": procedure.name
    }
    
    return templates.TemplateResponse("patient_welcome.html", {
        "request": request,
        "welcome_message": welcome_text,
        "session_data": session_data
    })

@router.get("/patient-survey", response_class=HTMLResponse)
async def patient_survey(request: Request, session_data: str = "", db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    factors = db.query(Factor).all()
    return templates.TemplateResponse("patient_survey.html", {
        "request": request,
        "factors": factors,
        "session_data": session_data
    })

@router.get("/review-generating", response_class=HTMLResponse)
async def review_generating(request: Request, db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    # Redirect to main menu if accessed directly
    return RedirectResponse(url="/main-selection", status_code=302)

@router.post("/review-generating")
async def review_generating_post(
    request: Request,
    session_data: str = Form(...),
    rating: int = Form(...),
    selected_factors: List[str] = Form([]),
    additional_comments: str = Form(""),
    db: Session = Depends(get_db)
):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    # Parse session data to get procedure and doctor names for the transition page
    try:
        session_info = json.loads(session_data)
        procedure_name = session_info.get("procedure_name", "your procedure")
        doctor_name = session_info.get("doctor_name", "your doctor")
    except:
        procedure_name = "your procedure"
        doctor_name = "your doctor"
    
    # Store form data in session for the transition page to use
    form_data = {
        "session_data": session_data,
        "rating": rating,
        "selected_factors": selected_factors,
        "additional_comments": additional_comments
    }
    
    return templates.TemplateResponse("review_generating.html", {
        "request": request,
        "procedure_name": procedure_name,
        "doctor_name": doctor_name,
        "form_data": form_data
    })

@router.post("/generate-reviews")
async def generate_reviews(
    request: Request,
    session_data: str = Form(...),
    rating: int = Form(...),
    selected_factors: List[str] = Form([]),
    additional_comments: str = Form(""),
    db: Session = Depends(get_db)
):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    # Parse session data
    print(f"DEBUG: Raw session_data received: {session_data}")
    print(f"DEBUG: Type of session_data: {type(session_data)}")
    
    # Try to parse the session data as JSON
    session_info = None
    try:
        session_info = json.loads(session_data)
        print(f"DEBUG: Successfully parsed session_info")
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON decode error parsing session_data")
        print(f"ERROR: Data: {session_data}")
        print(f"ERROR: JSON decode error details: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid session data format: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error parsing session_data: {session_data}")
        print(f"ERROR: Exception details: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing session data: {e}")
    
    print(f"DEBUG: Final session_info: {session_info}")
    print(f"DEBUG: Type of session_info: {type(session_info)}")
    
    # Validate that session_info is a dictionary and has required fields
    if not isinstance(session_info, dict):
        print(f"ERROR: session_info is not a dictionary: {type(session_info)}")
        raise HTTPException(status_code=400, detail="Session data must be a JSON object")
    
    required_fields = ["patient_name", "procedure_name", "doctor_name"]
    for field in required_fields:
        if field not in session_info:
            print(f"ERROR: Missing required field '{field}' in session_info: {session_info}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Generate AI reviews
    ai_reviews = await generate_ai_reviews(
        patient_name=session_info["patient_name"],
        procedure_name=session_info["procedure_name"],
        doctor_name=session_info["doctor_name"],
        rating=rating,
        selected_factors=selected_factors,
        additional_comments=additional_comments
    )
    
    # Store review data
    review_data = {
        **session_info,
        "rating": rating,
        "selected_factors": selected_factors,
        "additional_comments": additional_comments,
        "ai_reviews": ai_reviews
    }
    
    return templates.TemplateResponse("review_selection.html", {
        "request": request,
        "ai_reviews": ai_reviews,
        "review_data": json.dumps(review_data)
    })

@router.post("/finalize-review")
async def finalize_review(
    request: Request,
    review_data: str = Form(...),
    selected_review: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    # Parse review data
    try:
        review_info = json.loads(review_data)
    except json.JSONDecodeError as e:
        print(f"Error parsing review_data: {review_data}")
        print(f"JSON decode error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid review data format: {e}")
    except Exception as e:
        print(f"Unexpected error parsing review_data: {review_data}")
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing review data: {e}")
    
    # Save review to database
    review = Review(
        patient_name=review_info["patient_name"],
        doctor_id=review_info["doctor_id"],
        procedure_id=review_info["procedure_id"],
        rating=review_info["rating"],
        feedback=review_info["additional_comments"],
        message_to_doctor=review_info["message_to_doctor"],
        selected_factors=json.dumps(review_info["selected_factors"]),
        ai_generated_reviews=json.dumps(review_info["ai_reviews"]),
        selected_review=selected_review
    )
    db.add(review)
    db.commit()
    
    # Generate QR code for the review
    review_url = f"{request.base_url}review-helper?review_id={review.id}"
    qr_code = generate_qr_code(review_url)
    
    # Update review with QR code data
    review.qr_code_data = review_url
    db.commit()
    
    return templates.TemplateResponse("qr_code.html", {
        "request": request,
        "qr_code": qr_code,
        "selected_review": selected_review,
        "review_url": review_url
    })

@router.get("/review-helper", response_class=HTMLResponse)
async def review_helper(request: Request, review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return templates.TemplateResponse("review_helper.html", {
        "request": request,
        "review_text": review.selected_review,
        "google_place_id": GOOGLE_PLACE_ID
    })

# ============== ADMIN DASHBOARD ROUTES ==============

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    # Get all data for dashboard
    doctors = db.query(Doctor).all()
    procedures = db.query(Procedure).all()
    factors = db.query(Factor).all()
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(10).all()
    
    # Calculate analytics
    total_reviews = db.query(Review).count()
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
    
    # Get top procedure
    top_procedure = db.query(Procedure.name, func.count(Review.id).label('count'))\
        .join(Review, Procedure.id == Review.procedure_id)\
        .group_by(Procedure.name)\
        .order_by(func.count(Review.id).desc())\
        .first()
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "doctors": doctors,
        "procedures": procedures,
        "factors": factors,
        "reviews": reviews,
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 1),
        "top_procedure": top_procedure.name if top_procedure else "None"
    })

# ============== API ENDPOINTS ==============

# Doctor API
@router.get("/api/doctors")
async def get_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return [{"id": d.id, "name": d.name, "procedures": [{"id": p.id, "name": p.name} for p in d.procedures]} for d in doctors]

@router.get("/api/doctors/{doctor_id}/procedures")
async def get_doctor_procedures(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return [{"id": p.id, "name": p.name} for p in doctor.procedures]

@router.post("/api/doctors")
async def add_doctor(name: str = Form(...), db: Session = Depends(get_db)):
    doctor = Doctor(name=name)
    db.add(doctor)
    db.commit()
    return {"message": "Doctor added successfully", "id": doctor.id}

@router.put("/api/doctors/{doctor_id}")
async def update_doctor(doctor_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.name = name
    db.commit()
    return {"message": "Doctor updated successfully"}

@router.delete("/api/doctors/{doctor_id}")
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}

# Procedure API
@router.get("/api/procedures")
async def get_procedures(db: Session = Depends(get_db)):
    procedures = db.query(Procedure).all()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in procedures]

@router.post("/api/procedures")
async def add_procedure(name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    procedure = Procedure(name=name, description=description)
    db.add(procedure)
    db.commit()
    return {"message": "Procedure added successfully", "id": procedure.id}

@router.put("/api/procedures/{procedure_id}")
async def update_procedure(procedure_id: int, name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    procedure.name = name
    procedure.description = description
    db.commit()
    return {"message": "Procedure updated successfully"}

@router.delete("/api/procedures/{procedure_id}")
async def delete_procedure(procedure_id: int, db: Session = Depends(get_db)):
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    db.delete(procedure)
    db.commit()
    return {"message": "Procedure deleted successfully"}

# Factor API
@router.get("/api/factors")
async def get_factors(db: Session = Depends(get_db)):
    factors = db.query(Factor).all()
    return [{"id": f.id, "name": f.name, "description": f.description} for f in factors]

@router.post("/api/factors")
async def add_factor(name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    factor = Factor(name=name, description=description)
    db.add(factor)
    db.commit()
    return {"message": "Factor added successfully", "id": factor.id}

@router.put("/api/factors/{factor_id}")
async def update_factor(factor_id: int, name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")
    
    factor.name = name
    factor.description = description
    db.commit()
    return {"message": "Factor updated successfully"}

@router.delete("/api/factors/{factor_id}")
async def delete_factor(factor_id: int, db: Session = Depends(get_db)):
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")
    
    db.delete(factor)
    db.commit()
    return {"message": "Factor deleted successfully"}

# Doctor-Procedure Association API
@router.post("/api/doctors/{doctor_id}/procedures/{procedure_id}")
async def add_doctor_procedure(doctor_id: int, procedure_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    
    if not doctor or not procedure:
        raise HTTPException(status_code=404, detail="Doctor or procedure not found")
    
    if procedure not in doctor.procedures:
        doctor.procedures.append(procedure)
        db.commit()
    
    return {"message": "Procedure added to doctor successfully"}

@router.delete("/api/doctors/{doctor_id}/procedures/{procedure_id}")
async def remove_doctor_procedure(doctor_id: int, procedure_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    
    if not doctor or not procedure:
        raise HTTPException(status_code=404, detail="Doctor or procedure not found")
    
    if procedure in doctor.procedures:
        doctor.procedures.remove(procedure)
        db.commit()
    
    return {"message": "Procedure removed from doctor successfully"}

# Analytics API
@router.get("/api/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    total_reviews = db.query(Review).count()
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
    
    # Get recent reviews with relationships
    recent_reviews = db.query(Review).order_by(Review.created_at.desc()).limit(10).all()
    
    return {
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 1),
        "recent_reviews": [
            {
                "id": r.id,
                "patient_name": r.patient_name,
                "doctor_name": r.doctor.name if r.doctor else "Unknown",
                "procedure_name": r.procedure.name if r.procedure else "Unknown",
                "rating": r.rating,
                "feedback": r.feedback,
                "created_at": r.created_at.isoformat()
            }
            for r in recent_reviews
        ]
    }

# ============== LEGACY TREATMENT ROUTES (for backwards compatibility) ==============

@router.get("/api/treatments")
async def get_treatments(db: Session = Depends(get_db)):
    treatments = db.query(Treatment).all()
    return [{"id": t.id, "name": t.name} for t in treatments]

@router.post("/api/treatments")
async def add_treatment(name: str = Form(...), db: Session = Depends(get_db)):
    treatment = Treatment(name=name)
    db.add(treatment)
    db.commit()
    return {"message": "Treatment added successfully"}

@router.put("/api/treatments/{treatment_id}")
async def update_treatment(treatment_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    
    treatment.name = name
    db.commit()
    return {"message": "Treatment updated successfully"}

@router.delete("/api/treatments/{treatment_id}")
async def delete_treatment(treatment_id: int, db: Session = Depends(get_db)):
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    
    db.delete(treatment)
    db.commit()
    return {"message": "Treatment deleted successfully"}