from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from shared import templates, render_lang
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
import PyPDF2

load_dotenv()

# OpenAI configuration
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Place ID for reviews
GOOGLE_PLACE_ID = os.getenv("GOOGLE_PLACE_ID", "")

# Load PDF content for knowledge base
def load_pdf_knowledge_base():
    """Load and extract text from the PDF knowledge base."""
    try:
        pdf_path = "data/BH_CL.pdf"
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error loading PDF knowledge base: {e}")
        return ""

# Cache the PDF content to avoid reading it multiple times
PDF_KNOWLEDGE_BASE = load_pdf_knowledge_base()

# Helper function to generate AI reviews
async def generate_ai_reviews(patient_name: str, procedure_names: list, doctor_name: str, rating: int, selected_factors: list, selected_staff: list = [], all_staff_selected: bool = False, additional_comments: str = "", language: str = "English") -> list:
    """Generate AI-powered review suggestions based on patient feedback."""
    try:
        # Build context from factors
        factors_text = ", ".join(selected_factors) if selected_factors else ""
        
        # Format procedures for display
        if len(procedure_names) == 1:
            procedure_text = procedure_names[0]
            procedure_mention = f"my {procedure_text} procedure"
        else:
            procedure_text = ", ".join(procedure_names)
            procedure_mention = f"my {procedure_text} procedures"
        
        # Determine language specifications
        if language.lower().startswith("arab"):
            language_instruction = "Write the reviews in Arabic using the Saudi dialect. The reviews should sound natural and authentic as if written by a Saudi patient."
            fallback_language = "Arabic (Saudi dialect)"
        else:
            language_instruction = "Write the reviews in English."
            fallback_language = "English"
        # Build staff thank you text
        staff_thank_you = ""
        if selected_staff:
            if all_staff_selected:
                staff_thank_you = f"Thank you to {doctor_name} and her team"
            else:
                selected_staff.remove("doctor")
                if len(selected_staff) == 1:
                    staff_thank_you = f"Thank you to {doctor_name}"
                elif len(selected_staff) == 2:
                    staff_thank_you = f"Thank you to {doctor_name} and {selected_staff[0]}"
        
        # Create prompt with PDF knowledge base and staff thank you
        prompt = f"""
        You are an expert at writing authentic Google reviews for medical clinics. Use the following knowledge base of past reviews as a guide for style, tone, and formatting:
        
        KNOWLEDGE BASE OF PAST REVIEWS:
        {PDF_KNOWLEDGE_BASE}...
        
        Based on the above examples and this patient feedback, generate 4 different Google review texts:
        - Patient: {patient_name}
        - Procedure(s): {procedure_text}
        - Doctor: {doctor_name}
        - Rating: {rating}/5 stars
        - What stood out: {factors_text}
        - Staff to thank: {staff_thank_you}
        - Additional comments: {additional_comments}
        
        LANGUAGE REQUIREMENT: {language_instruction}
        
        Each review should be:
        - Natural and authentic (1-3 sentences)
        - Positive and professional
        - Mention specific aspects from the feedback
        - Include the staff thank you appropriately in the review
        - Written in first person
        - Different in tone and style from the others
        - Follow the style and format patterns shown in the knowledge base examples
        - If the doctor, coordinator, or nursing team are mentioned, make sure to thank the doctor and the team and not all separately
        
        Return only the review texts, one per line, no numbering or formatting.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant that writes authentic, positive Google reviews for medical clinics based on patient feedback. Always write in {fallback_language} as specified in the user's request."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        reviews = [review.strip() for review in content.split('\n') if review.strip()]
        
        # Ensure we have exactly 4 reviews
        if len(reviews) < 4:
            if language.lower().startswith("arab"):
                # Arabic fallback reviews (Saudi dialect)
                reviews.extend([
                    f"تجربة ممتازة مع الدكتور {doctor_name} في {procedure_text}. الموظفين محترفين والنتائج فاقت توقعاتي.",
                    f"أنصح بشدة بهذه العيادة! علاج {procedure_text} كان مريح والفريق كان متعاون جداً.",
                    f"تجربة رائعة في هذه العيادة. الدكتور {doctor_name} قام بعمل ممتاز في {procedure_text}.",
                    f"خدمة مهنية ونتائج ممتازة. سعيد جداً بعلاج {procedure_text}."
                ])
            else:
                # English fallback reviews
                reviews.extend([
                    f"Had an excellent experience with {doctor_name} for {procedure_mention}. The staff was professional and the results exceeded my expectations.",
                    f"Highly recommend this clinic! The {procedure_text} treatment was comfortable and the team was very caring.",
                    f"Great experience at this clinic. {doctor_name} did an amazing job with {procedure_mention}.",
                    f"Professional service and excellent results. Very happy with my {procedure_text} treatment."
                ])
        
        return reviews[:4]  # Return only first 4
        
    except Exception as e:
        print(f"Error generating AI reviews: {e}")
        # Return fallback reviews based on language
        if language.lower().startswith("arab"):
            return [
                f"تجربة ممتازة مع الدكتور {doctor_name} في {procedure_text}. الموظفين محترفين والنتائج فاقت توقعاتي.",
                f"أنصح بشدة بهذه العيادة! علاج {procedure_text} كان مريح والفريق كان متعاون جداً.",
                f"تجربة رائعة في هذه العيادة. الدكتور {doctor_name} قام بعمل ممتاز في {procedure_text}.",
                f"خدمة مهنية ونتائج ممتازة. سعيد جداً بعلاج {procedure_text}."
            ]
        else:
            return [
                f"Had an excellent experience with {doctor_name} for {procedure_mention}. The staff was professional and the results exceeded my expectations.",
                f"Highly recommend this clinic! The {procedure_text} treatment was comfortable and the team was very caring.",
                f"Great experience at this clinic. {doctor_name} did an amazing job with {procedure_mention}.",
                f"Professional service and excellent results. Very happy with my {procedure_text} treatment."
            ]

router = APIRouter()
# templates = Jinja2Templates(directory="templates")

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
    procedure_ids: List[int] = Form(...),
    message_to_doctor: str = Form(""),
    language: str = Form("English"),
    db: Session = Depends(get_db)
):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    # Store language in session
    lang_code = "ar" if language.lower().startswith("arab") else "en"
    request.session["lang"] = lang_code
    # Get doctor and procedure details
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    procedures = db.query(Procedure).filter(Procedure.id.in_(procedure_ids)).all()
    if not doctor or not procedures:
        raise HTTPException(status_code=404, detail="Doctor or procedures not found")
    
    # Build procedure names for display
    procedure_names = [proc.name for proc in procedures]
    procedure_names_str = ", ".join(procedure_names)
    
    # Generate a kind, general welcome message that handles multiple procedures
    if len(procedure_names) == 1:
        welcome_text = f"Thank you for choosing our clinic for your {procedure_names[0]} treatment. We're delighted to have you with us today and hope you had a comfortable experience."
    else:
        # For multiple procedures, create a more elegant message
        if len(procedure_names) == 2:
            procedures_text = f"{procedure_names[0]} and {procedure_names[1]}"
        else:
            # For 3+ procedures: "A, B, and C"
            procedures_text = ", ".join(procedure_names[:-1]) + f", and {procedure_names[-1]}"
        
        welcome_text = f"Thank you for choosing our clinic for your {procedures_text} treatments. We're delighted to have you with us today and hope you had a comfortable experience with all your procedures."
    
    # Store session data for the survey
    session_data = {
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "procedure_ids": procedure_ids,
        "procedure_id": procedure_ids[0] if procedure_ids else None,  # Keep for backward compatibility
        "message_to_doctor": message_to_doctor,
        "doctor_name": doctor.name,
        "procedure_names": procedure_names,
        "procedure_name": procedure_names_str,  # Keep for backward compatibility
        "language": language,
        "lang_code": lang_code
    }
    return render_lang(request, "patient_welcome.html", {
        "patient_name": patient_name,
        "welcome_message": welcome_text,
        "session_data": session_data
    })

@router.get("/patient-survey", response_class=HTMLResponse)
async def patient_survey(request: Request, session_data: str = "", db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    factors = db.query(Factor).all()
    return render_lang(request, "patient_survey.html", {
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
    selected_staff: List[str] = Form([]),
    all_staff_selected: str = Form("false"),
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
        "selected_staff": selected_staff,
        "all_staff_selected": all_staff_selected,
        "additional_comments": additional_comments
    }
    
    return render_lang(request, "review_generating.html", {
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
    selected_staff: List[str] = Form([]),
    all_staff_selected: str = Form("false"),
    additional_comments: str = Form(""),
    message_to_doctor: str = Form(""),
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
    
    required_fields = ["patient_name", "doctor_name"]
    for field in required_fields:
        if field not in session_info:
            print(f"ERROR: Missing required field '{field}' in session_info: {session_info}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Check for procedures (support both old and new format)
    procedure_names = []
    if "procedure_names" in session_info:
        procedure_names = session_info["procedure_names"]
    elif "procedure_name" in session_info:
        procedure_names = [session_info["procedure_name"]]
    else:
        raise HTTPException(status_code=400, detail="Missing procedure information")
    
    # Get language from session data
    language = session_info.get("language", "English")
    
    # Generate AI reviews
    ai_reviews = await generate_ai_reviews(
        patient_name=session_info["patient_name"],
        procedure_names=procedure_names,
        doctor_name=session_info["doctor_name"],
        rating=rating,
        selected_factors=selected_factors,
        selected_staff=selected_staff,
        all_staff_selected=all_staff_selected.lower() == "true",
        additional_comments=additional_comments,
        language=language
    )
    
    # Store review data
    review_data = {
        **session_info,
        "rating": rating,
        "selected_factors": selected_factors,
        "selected_staff": selected_staff,
        "all_staff_selected": all_staff_selected.lower() == "true",
        "additional_comments": additional_comments,
        "message_to_doctor": message_to_doctor,
        "ai_reviews": ai_reviews
    }
    
    return render_lang(request, "review_selection.html", {
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
    # Handle both old and new format for procedures
    procedure_id = None
    procedure_ids = None
    
    if "procedure_ids" in review_info:
        procedure_ids = json.dumps(review_info["procedure_ids"])
        procedure_id = review_info["procedure_ids"][0] if review_info["procedure_ids"] else None
    elif "procedure_id" in review_info:
        procedure_id = review_info["procedure_id"]
        procedure_ids = json.dumps([procedure_id]) if procedure_id else None
    
    review = Review(
        patient_name=review_info["patient_name"],
        doctor_id=review_info["doctor_id"],
        procedure_id=procedure_id,
        procedure_ids=procedure_ids,
        rating=review_info["rating"],
        feedback=review_info["additional_comments"],
        message_to_doctor=review_info["message_to_doctor"],
        selected_factors=json.dumps(review_info["selected_factors"]),
        selected_staff=json.dumps(review_info.get("selected_staff", [])),
        all_staff_selected=review_info.get("all_staff_selected", False),
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
    
    return render_lang(request, "qr_code.html", {
        "qr_code": qr_code,
        "selected_review": selected_review,
        "review_url": review_url
    })

@router.get("/review-helper", response_class=HTMLResponse)
async def review_helper(request: Request, review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return render_lang(request, "review_helper.html", {
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
    
    # Create stats object for template
    stats = {
        "total_reviews": total_reviews,
        "average_rating": round(avg_rating, 1),
        "most_common_factors": {
            "positive": ["Professional staff", "Clean facility", "Good communication"],
            "negative": ["Long wait times", "High costs"]
        }
    }
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "doctors": doctors,
        "procedures": procedures,
        "factors": factors,
        "recent_reviews": reviews,
        "treatments": db.query(Treatment).all(),
        "stats": stats
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

# ============== ADMIN FORM HANDLING ROUTES ==============

@router.post("/add_treatment")
async def add_treatment_form(name: str = Form(...), db: Session = Depends(get_db)):
    treatment = Treatment(name=name)
    db.add(treatment)
    db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/delete_treatment/{treatment_id}")
async def delete_treatment_form(treatment_id: int, db: Session = Depends(get_db)):
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if treatment:
        db.delete(treatment)
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/add_doctor")
async def add_doctor_form(name: str = Form(...), db: Session = Depends(get_db)):
    doctor = Doctor(name=name)
    db.add(doctor)
    db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/delete_doctor/{doctor_id}")
async def delete_doctor_form(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor:
        db.delete(doctor)
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/add_procedure")
async def add_procedure_form(name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    procedure = Procedure(name=name, description=description)
    db.add(procedure)
    db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/delete_procedure/{procedure_id}")
async def delete_procedure_form(procedure_id: int, db: Session = Depends(get_db)):
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if procedure:
        db.delete(procedure)
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/add_factor")
async def add_factor_form(name: str = Form(...), db: Session = Depends(get_db)):
    factor = Factor(name=name)
    db.add(factor)
    db.commit()
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/delete_factor/{factor_id}")
async def delete_factor_form(factor_id: int, db: Session = Depends(get_db)):
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if factor:
        db.delete(factor)
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)

# ============== ADMIN SUB-PAGE ROUTES ==============

@router.get("/admin/doctors", response_class=HTMLResponse)
async def admin_doctors(request: Request, db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    doctors = db.query(Doctor).all()
    all_procedures = db.query(Procedure).all()
    
    return templates.TemplateResponse("admin_doctors.html", {
        "request": request,
        "doctors": doctors,
        "all_procedures": all_procedures
    })

@router.get("/admin/survey", response_class=HTMLResponse)
async def admin_survey(request: Request, db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    factors = db.query(Factor).all()
    procedures = db.query(Procedure).all()
    welcome_messages = db.query(WelcomeMessage).all()
    
    return templates.TemplateResponse("admin_survey.html", {
        "request": request,
        "factors": factors,
        "procedures": procedures,
        "welcome_messages": welcome_messages
    })

@router.get("/admin/reviews", response_class=HTMLResponse)
async def admin_reviews(request: Request, db: Session = Depends(get_db)):
    auth_result = check_auth(request)
    if auth_result:
        return auth_result
    
    reviews = db.query(Review).order_by(Review.created_at.desc()).all()
    
    # Calculate stats
    total_reviews = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0
    
    # Count this month's reviews
    from datetime import datetime, timedelta
    this_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_count = len([r for r in reviews if r.created_at >= this_month])
    
    stats = {
        "total_reviews": total_reviews,
        "average_rating": round(avg_rating, 1),
        "this_month": this_month_count
    }
    
    return templates.TemplateResponse("admin_reviews.html", {
        "request": request,
        "reviews": reviews,
        "stats": stats
    })

# ============== ADDITIONAL FORM ROUTES ==============

@router.post("/add_welcome_message")
async def add_welcome_message_form(procedure_name: str = Form(...), message: str = Form(...), db: Session = Depends(get_db)):
    welcome_msg = WelcomeMessage(procedure_name=procedure_name, message=message)
    db.add(welcome_msg)
    db.commit()
    return RedirectResponse(url="/admin/survey", status_code=302)

@router.post("/delete_welcome_message/{message_id}")
async def delete_welcome_message_form(message_id: int, db: Session = Depends(get_db)):
    message = db.query(WelcomeMessage).filter(WelcomeMessage.id == message_id).first()
    if message:
        db.delete(message)
        db.commit()
    return RedirectResponse(url="/admin/survey", status_code=302)

@router.post("/delete_review/{review_id}")
async def delete_review_form(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if review:
        db.delete(review)
        db.commit()
    return RedirectResponse(url="/admin/reviews", status_code=302)

# Update existing form routes to redirect to correct pages
@router.post("/add_doctor")
async def add_doctor_form(name: str = Form(...), db: Session = Depends(get_db)):
    doctor = Doctor(name=name)
    db.add(doctor)
    db.commit()
    return RedirectResponse(url="/admin/doctors", status_code=302)

@router.post("/delete_doctor/{doctor_id}")
async def delete_doctor_form(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor:
        db.delete(doctor)
        db.commit()
    return RedirectResponse(url="/admin/doctors", status_code=302)

@router.post("/add_procedure")
async def add_procedure_form(name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    procedure = Procedure(name=name, description=description)
    db.add(procedure)
    db.commit()
    return RedirectResponse(url="/admin/doctors", status_code=302)

@router.post("/delete_procedure/{procedure_id}")
async def delete_procedure_form(procedure_id: int, db: Session = Depends(get_db)):
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if procedure:
        db.delete(procedure)
        db.commit()
    return RedirectResponse(url="/admin/doctors", status_code=302)

@router.post("/add_factor")
async def add_factor_form(name: str = Form(...), db: Session = Depends(get_db)):
    factor = Factor(name=name)
    db.add(factor)
    db.commit()
    return RedirectResponse(url="/admin/survey", status_code=302)

@router.post("/delete_factor/{factor_id}")
async def delete_factor_form(factor_id: int, db: Session = Depends(get_db)):
    factor = db.query(Factor).filter(Factor.id == factor_id).first()
    if factor:
        db.delete(factor)
        db.commit()
    return RedirectResponse(url="/admin/survey", status_code=302)

# Doctor-procedure assignment routes
@router.post("/add_doctor_procedure/{doctor_id}")
async def add_doctor_procedure_form(doctor_id: int, procedure_id: int = Form(...), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    
    if doctor and procedure and procedure not in doctor.procedures:
        doctor.procedures.append(procedure)
        db.commit()
    
    return RedirectResponse(url="/admin/doctors", status_code=302)

@router.post("/remove_doctor_procedure/{doctor_id}/{procedure_id}")
async def remove_doctor_procedure_form(doctor_id: int, procedure_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    
    if doctor and procedure and procedure in doctor.procedures:
        doctor.procedures.remove(procedure)
        db.commit()
    
    return RedirectResponse(url="/admin/doctors", status_code=302)