# Clinic Review Kiosk - Project Structure

## 🏥 Overview
A FastAPI-based clinic review kiosk system that guides patients through feedback collection and generates Google review suggestions.

---

## 📁 File Organization

### 🐍 **Core Python Files**

#### **`app.py`**
- **Main FastAPI application entry point**
- **Mounts static files** (`/static` directory)
- **Configures Jinja2 templates**
- **Initializes database** with default clinic data
- **Includes AI review generation** functionality
- **Runs on port 8000** with uvicorn

#### **`models.py`**
- **Database models** (SQLAlchemy ORM)
- **Defines tables**: Doctor, Procedure, Factor, Review, WelcomeMessage, Treatment
- **Database configuration** (SQLite)
- **Default clinic data** (procedures, doctors, factors, welcome messages)
- **Session management** functions

#### **`routes.py`**
- **All API endpoints** and web routes
- **Patient flow routes** (start → survey → review generation)
- **Admin dashboard routes** (CRUD operations)
- **QR code generation** functionality
- **Authentication** and session management

### 🛠️ **Utility Scripts**

#### **`start.py`**
- **Environment validation** script
- **Dependency checking** (FastAPI, uvicorn, etc.)
- **Starts the server** with proper configuration
- **User-friendly startup** with status messages

#### **`install.py`**
- **Automated installation** script
- **Python version checking** (3.8+)
- **Dependency installation** (`pip install -r requirements.txt`)
- **Installation verification**

### 📦 **Configuration Files**

#### **`requirements.txt`**
- **Python dependencies** list
- **FastAPI, SQLAlchemy, OpenAI, QR code** libraries
- **Version specifications** for stability

#### **`.gitignore`**
- **Git ignore patterns**
- **Excludes**: `.env`, `__pycache__`, `.venv`, database files
- **Keeps repository clean**

### 🗄️ **Data Files**

#### **`clinic_reviews.db`**
- **SQLite database** file
- **Stores all clinic data**: reviews, doctors, procedures, factors
- **Auto-created** on first run

### 🎨 **Frontend Assets**

#### **`static/css/style.css`**
- **Complete CSS styling** for the entire application
- **Modern, responsive design**
- **Professional medical clinic** aesthetic
- **Mobile-friendly** layout

### 📄 **HTML Templates**

#### **`templates/base.html`**
- **Base template** with common HTML structure
- **CSS and meta tag** inclusion
- **Template inheritance** foundation

#### **`templates/index.html`**
- **Login page** for admin access
- **Password authentication** form

#### **`templates/main_selection.html`**
- **Main menu** after login
- **Patient review** and **admin dashboard** options

#### **`templates/patient_start.html`**
- **Patient information** collection
- **Doctor and procedure** selection

#### **`templates/patient_welcome.html`**
- **Welcome message** display
- **Personalized greeting** based on procedure

#### **`templates/patient_survey.html`**
- **Rating system** (1-5 stars)
- **Factor selection** checkboxes
- **Additional comments** field

#### **`templates/review_selection.html`**
- **AI-generated review** options display
- **Review selection** interface

#### **`templates/qr_code.html`**
- **QR code display** for review sharing
- **Review preview** and **countdown timer**

#### **`templates/review_helper.html`**
- **Review copying** functionality
- **Google review** posting instructions
- **Step-by-step** guidance

#### **`templates/admin.html`**
- **Admin dashboard** interface
- **CRUD operations** for doctors, procedures, factors
- **Analytics** and **recent reviews** display

### 📚 **Documentation**

#### **`README.md`**
- **Main project documentation**
- **Setup instructions** and **usage guide**

#### **`README_FASTAPI.md`**
- **FastAPI-specific** documentation
- **API endpoints** reference
- **Technical details**

#### **`DATA_CONFIG_README.md`**
- **Data configuration** guide
- **Clinic data** customization instructions

---

## 🚀 **Quick Start**

1. **Install dependencies**: `python install.py`
2. **Set up environment**: Create `.env` file with API keys
3. **Start application**: `python start.py` or `python app.py`
4. **Access**: http://localhost:8000
5. **Login**: Use password from `.env` file

---

## 🔧 **Environment Variables** (`.env`)

- `OPENAI_API_KEY` - OpenAI API key for AI review generation
- `GOOGLE_PLACE_ID` - Google Place ID for reviews
- `ADMIN_PASSWORD` - Admin login password
- `SECRET_KEY` - Session security key

---

## 📱 **Features**

- **Patient feedback collection** with star ratings
- **AI-powered review generation** using OpenAI
- **QR code generation** for easy review sharing
- **Admin dashboard** for data management
- **Responsive design** for kiosk use
- **Google review integration**

---

## 🏗️ **Architecture**

- **FastAPI** backend with **SQLAlchemy** ORM
- **SQLite** database for data persistence
- **Jinja2** templating for HTML generation
- **Static file serving** for CSS/assets
- **Session-based authentication**
- **OpenAI integration** for AI features 