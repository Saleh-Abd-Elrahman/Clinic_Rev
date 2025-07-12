# 🏥 Clinic Review Kiosk - FastAPI Version

A FastAPI-based kiosk application for collecting patient reviews and generating Google review QR codes, designed for iPad kiosks in medical clinics.

## 🚀 Features

- **Admin Authentication**: Secure password-protected access
- **Doctor-Procedure Management**: Many-to-many relationship management
- **Patient Review Flow**: Name entry → Doctor/Procedure selection → Survey → AI review generation
- **AI-Powered Reviews**: OpenAI generates 4 customizable review options
- **QR Code Generation**: Patients scan to access mobile review helper
- **Mobile Review Helper**: Copy-to-clipboard + Google Reviews integration
- **Admin Dashboard**: Complete CRUD operations for doctors, procedures, and factors
- **Auto-Reset Kiosk**: 2-minute timeout with manual reset options
- **iPad Optimized**: Touch-friendly interface designed for tablet kiosks

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Google Place ID for your clinic
- HTTPS deployment (required for clipboard functionality on iOS)

## ⚡ Quick Start

### 1. Clone and Setup
   ```bash
   git clone <repository-url>
cd clinic-review-kiosk
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### 2. Environment Configuration
Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Places Configuration  
GOOGLE_PLACE_ID=ChIJ_your_google_place_id_here

# Application Security
ADMIN_PASSWORD=your-secure-admin-password-here
SECRET_KEY=your-secret-key-for-sessions-here

# Optional: Database Configuration (defaults to SQLite)
# DATABASE_URL=sqlite:///./clinic_reviews.db

# Optional: Server Configuration
# PORT=8000
# HOST=0.0.0.0
```

### 3. Get Your Google Place ID
- Visit [Google Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id)
- Search for your clinic and copy the Place ID

### 4. Initialize Database
   ```bash
   python app.py
   ```
The database will be automatically created with default data on first run.
   
### 5. Start the Server
   ```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

### 6. Access the Application
Navigate to `http://localhost:8000`

## 🏗️ Database Structure

### Core Models
- **Doctor**: Healthcare providers with many-to-many procedure relationships
- **Procedure**: Medical procedures that can be performed by multiple doctors
- **Factor**: Aspects that can impress patients (cleanliness, staff, etc.)
- **Review**: Patient feedback with AI-generated reviews and QR codes
- **WelcomeMessage**: Customizable messages per procedure type

### Relationships
- Doctors ↔ Procedures (Many-to-Many)
- Reviews → Doctor (Many-to-One)
- Reviews → Procedure (Many-to-One)
- WelcomeMessage → Procedure (One-to-One)

## 🎯 Application Flow

### Admin Dashboard
1. **Login** → Enter admin password
2. **Main Menu** → Choose Patient Review or Admin Dashboard
3. **Admin Functions**:
   - Manage Doctors (add/edit/delete + assign procedures)
   - Manage Procedures (add/edit/delete with descriptions)
   - Manage Factors (what impressed patients options)
   - View Analytics (review statistics and recent feedback)

### Patient Review Flow
1. **Patient Info** → Name, doctor selection, procedure selection
2. **Optional Message** → Hidden field for doctor feedback
3. **Welcome Message** → Personalized thank you message
4. **Survey** → Star rating + factor selection + optional comments
5. **AI Review Generation** → 4 AI-generated review options
6. **Review Selection** → Choose and optionally edit reviews
7. **QR Code** → Generate QR code linking to mobile helper
8. **Auto Reset** → 2-minute countdown returns to main menu

### Mobile Experience (Post-QR Scan)
1. **Review Display** → Show selected review text
2. **Copy Function** → One-click copy to clipboard
3. **Google Integration** → Direct link to clinic's Google Reviews
4. **Help Section** → Troubleshooting and tips
5. **Edit Option** → Double-click to modify review

## 🌐 Deployment

### Option 1: Railway
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Option 2: Render
1. Connect your GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically

### Option 3: Docker
```bash
docker build -t clinic-review-kiosk .
docker run -p 8000:8000 --env-file .env clinic-review-kiosk
```

### Option 4: VPS/Cloud Server
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# Setup application
git clone <repo>
cd clinic-review-kiosk
pip3 install -r requirements.txt

# Configure nginx reverse proxy
sudo nano /etc/nginx/sites-available/clinic-review

# Start with systemd service
sudo systemctl enable clinic-review
sudo systemctl start clinic-review
```

## 📱 iPad Kiosk Setup

### 1. Configure iPad
- **Guided Access**: Settings → Accessibility → Guided Access (Enable)
- **Auto-Lock**: Settings → Display & Brightness → Auto-Lock (Never)
- **Safari**: Use full-screen mode
- **Home Screen**: Add web app to home screen for full-screen experience

### 2. Kiosk Mode Setup
- Navigate to your deployed URL
- Tap Share button → "Add to Home Screen"
- Open from home screen for app-like experience
- Enable Guided Access to lock the app

### 3. Staff Training
- **Login**: Use configured admin password
- **Reset**: Press 'R' key or wait for auto-reset
- **Emergency**: Triple-click home button to exit Guided Access

## 🔧 API Endpoints

### Authentication
- `POST /login` - Admin login
- `POST /logout` - Admin logout

### Patient Flow
- `GET /patient-start` - Patient information form
- `POST /patient-details` - Process patient info
- `GET /patient-survey` - Survey form  
- `POST /generate-reviews` - AI review generation
- `POST /finalize-review` - Save review and generate QR
- `GET /review-helper` - Mobile review helper page

### Admin Management
- `GET /admin` - Admin dashboard
- `GET|POST|PUT|DELETE /api/doctors` - Doctor CRUD
- `GET|POST|PUT|DELETE /api/procedures` - Procedure CRUD
- `GET|POST|PUT|DELETE /api/factors` - Factor CRUD
- `POST|DELETE /api/doctors/{id}/procedures/{id}` - Manage doctor-procedure relationships

### Analytics
- `GET /api/analytics` - Review statistics and recent reviews

## 🎨 Customization

### Welcome Messages
Edit welcome messages for each procedure type in the admin dashboard or directly in the database.

### Styling
Modify CSS in templates or create custom themes by editing the style blocks in each template.

### AI Prompts
Customize the AI review generation prompt in `app.py` → `generate_ai_reviews()` function.

### Default Data
Modify `CLINIC_DATA` in `models.py` to change default doctors, procedures, and factors.

## 🛠️ Troubleshooting

### Common Issues

**Database Errors**
- Ensure SQLite file permissions are correct
- Check if database directory is writable
- Restart application to reinitialize tables

**AI Review Generation Fails**
- Verify OpenAI API key is valid and has credits
- Check internet connection
- Review API rate limits

**QR Code Not Displaying**
- Ensure Pillow package is installed correctly
- Check base64 encoding in browser developer tools
- Verify QR code library is functioning

**Mobile Copy Function Not Working**
- Ensure site is served over HTTPS
- Check iOS Safari clipboard permissions
- Use manual text selection as fallback

**Auto-Reset Not Working**
- Check JavaScript console for errors
- Verify event listeners are properly attached
- Use manual 'R' key reset as backup

### Debug Mode
Set `DEBUG=true` in environment variables for detailed error logging.

## 🔒 Security

- **Environment Variables**: All sensitive data in environment files
- **Password Authentication**: Admin access protection
- **Session Management**: Secure cookie-based sessions
- **Data Privacy**: No persistent patient data storage
- **Auto-Reset**: Automatic session clearing after timeout

## 📈 Analytics & Monitoring

### Built-in Analytics
- Total review count
- Average ratings
- Top procedures
- Recent reviews with timestamps
- Doctor/procedure performance metrics

### External Integration
Add your preferred analytics service by modifying the tracking scripts in templates.

## 🚧 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Email notifications for reviews
- [ ] Custom branding themes  
- [ ] Practice management system integration
- [ ] Offline mode with sync capability
- [ ] Advanced AI prompt customization
- [ ] Review sentiment analysis

## 📝 License

ISC License - See package.json for details

## 🤝 Support

For technical support or customization requests:
1. Check troubleshooting section
2. Review error logs
3. Contact your development team

---

**Built with FastAPI for reliable, high-performance patient feedback collection** 🚀 