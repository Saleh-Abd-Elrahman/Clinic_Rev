# 🏥 Clinic Review Kiosk

A kiosk-style web app that runs full-screen on an iPad and guides clinic patients from a short survey to posting a Google Maps review.

## 🚀 Features

- **Staff Authentication**: Password-protected access
- **Patient Intake**: Name and treatment type collection
- **Personalized Welcome**: Custom messages based on treatment
- **Smart Survey**: Star ratings, practitioner selection, and experience highlights
- **AI-Powered Reviews**: OpenAI generates 4 review options based on feedback
- **QR Code Generation**: Patients scan to access review helper page
- **Auto-Reset**: Kiosk resets after 2 minutes or manual 'R' key press
- **Mobile-Optimized**: Works seamlessly on phones and tablets

## 📋 Prerequisites

- Node.js 18+ 
- OpenAI API key
- Google Place ID for your clinic
- HTTPS deployment (required for clipboard functionality on iOS)

## ⚡ Quick Start

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd clinic-review-kiosk
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   PLACE_ID=ChIJXXXXXXXXXXXXXXXXXX
   ACCESS_PASSWORD=your-secure-password
   PORT=3000
   ```

3. **Get Your Google Place ID**
   - Visit [Google Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id)
   - Search for your clinic and copy the Place ID

4. **Start the Server**
   ```bash
   npm run dev
   ```

5. **Open in Browser**
   Navigate to `http://localhost:3000`

## 🌐 Deployment

### Option 1: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 2: Render
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically on push

### Option 3: Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch
fly deploy
```

## 📱 iPad Kiosk Setup

1. **Configure iPad**
   - Enable Guided Access (Settings > Accessibility > Guided Access)
   - Set Safari to full-screen mode
   - Disable sleep/auto-lock

2. **Open the App**
   - Navigate to your deployed URL
   - Tap the share button → "Add to Home Screen"
   - Open from home screen for full-screen experience

3. **Staff Training**
   - Password: Enter your `ACCESS_PASSWORD`
   - Reset: Press 'R' at any time to restart
   - Auto-reset occurs after 2 minutes of inactivity

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for review generation | `sk-...` |
| `PLACE_ID` | Google Place ID for your clinic | `ChIJ...` |
| `ACCESS_PASSWORD` | Staff login password | `letmein` |
| `PORT` | Server port (optional) | `3000` |

### Customization

**Treatment Types**: Edit the `<select>` options in `public/index.html`

**Practitioners**: Modify the practitioner dropdown in the survey section

**Welcome Messages**: Update the `generateWelcomeMessage()` function in `public/js/main.js`

**Styling**: Customize CSS in the `<style>` sections of HTML files

## 🛠️ Troubleshooting

### Common Issues

**QR Code Not Generating**
- Check browser console for errors
- Ensure QRCode library loads from CDN
- Verify stable internet connection

**AI Suggestions Failing**
- Confirm OpenAI API key is valid and has credits
- Check server logs for API errors
- Fallback suggestions will show if AI fails

**Clipboard Not Working on iOS**
- Ensure site is served over HTTPS
- Check iOS Safari settings for clipboard access
- Use the manual copy button if automatic copy fails

**Auto-Reset Not Working**
- Check browser console for JavaScript errors
- Verify event listeners are properly attached
- Use manual 'R' key reset as fallback

## 📊 Usage Flow

1. **Staff Login** → Enter password
2. **Patient Details** → Name and treatment type
3. **Welcome Message** → Personalized greeting
4. **Survey** → Rating, practitioner, highlights
5. **AI Suggestions** → Choose preferred review
6. **QR Code** → Patient scans with phone
7. **Review Helper** → Copy text and open Google
8. **Auto Reset** → Back to login after 2 minutes

## 🔒 Security

- Environment variables for sensitive data
- Password authentication for staff access
- No patient data stored persistently
- Session-only data retention
- Auto-reset clears all information

## 🚧 Future Enhancements

- [ ] PWA + Service Worker for offline operation
- [ ] Admin dashboard for analytics
- [ ] Multiple language support
- [ ] Custom branding themes
- [ ] Integration with practice management systems
- [ ] Automated email summaries for staff

## 📝 License

ISC - See package.json for details

## 🤝 Support

For setup assistance or customization requests, please contact your development team.

---

**Built with ❤️ for better patient feedback collection** 