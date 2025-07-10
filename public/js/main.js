// Generic helper function
const $ = (id) => document.getElementById(id);

// State management
let patientData = {
    name: '',
    operation: ''
};

let surveyAnswers = {};
let selectedSuggestion = '';
let resetTimer = null;

// Show specific sections, hide others
function show(...sectionIds) {
    const allSections = [
        'login-section',
        'patient-section', 
        'welcome-section',
        'survey-section',
        'suggestions-section',
        'qr-section'
    ];
    
    allSections.forEach(id => {
        const element = $(id);
        if (element) {
            if (sectionIds.includes(id)) {
                element.classList.remove('hidden');
            } else {
                element.classList.add('hidden');
            }
        }
    });
}

// Staff login functionality
async function handleLogin() {
    const password = $('password').value;
    const loginError = $('login-error');
    
    if (!password) {
        loginError.textContent = 'Please enter a password.';
        loginError.classList.remove('hidden');
        return;
    }
    
    try {
        const response = await fetch('/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });
        
        if (response.ok) {
            loginError.classList.add('hidden');
            show('patient-section');
            // Clear password field
            $('password').value = '';
        } else {
            loginError.textContent = 'Invalid password. Please try again.';
            loginError.classList.remove('hidden');
            // Clear password field
            $('password').value = '';
        }
    } catch (error) {
        console.error('Login error:', error);
        loginError.textContent = 'Connection error. Please try again.';
        loginError.classList.remove('hidden');
    }
}

// Patient details and welcome message
function handlePatientDetails() {
    const name = $('patient-name').value.trim();
    const operation = $('operation').value;
    
    if (!name) {
        alert('Please enter the patient\'s name.');
        return;
    }
    
    if (!operation) {
        alert('Please select a treatment type.');
        return;
    }
    
    // Store patient data
    patientData.name = name;
    patientData.operation = operation;
    
    // Generate personalized welcome message
    const welcomeMessage = generateWelcomeMessage(name, operation);
    $('welcome-message').innerHTML = welcomeMessage;
    
    // Show welcome section
    show('welcome-section');
}

// Generate personalized welcome message
function generateWelcomeMessage(name, operation) {
    const messages = {
        'Hip Replacement': `Hi ${name}! We hope your hip replacement went smoothly and you're recovering well. Your feedback helps us continue providing excellent orthopedic care.`,
        'Knee Replacement': `Hi ${name}! We hope your knee replacement was successful and you're feeling better. Your experience matters to us and future patients.`,
        'Shoulder Surgery': `Hi ${name}! We hope your shoulder surgery went well and you're on the path to recovery. Thank you for choosing our clinic for your care.`,
        'Spine Surgery': `Hi ${name}! We hope your spine surgery was successful and you're healing comfortably. Your feedback helps us improve our specialized care.`,
        'General Consultation': `Hi ${name}! Thank you for visiting us for your consultation. We hope we provided the guidance and care you needed.`,
        'Physical Therapy': `Hi ${name}! We hope your physical therapy sessions have been helpful in your recovery journey. Your progress is our priority.`,
        'Diagnostic Imaging': `Hi ${name}! Thank you for coming in for your imaging appointment. We hope everything went smoothly and quickly for you.`,
        'Other': `Hi ${name}! Thank you for visiting our clinic. We hope you received the care and attention you deserved.`
    };
    
    return messages[operation] || messages['Other'];
}

// Survey form handling
async function handleSurvey(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const rating = formData.get('rating');
    const practitioner = formData.get('practitioner');
    const highlights = formData.getAll('highlights');
    
    if (!rating) {
        alert('Please select a rating.');
        return;
    }
    
    // Prepare survey answers
    surveyAnswers = {
        patientName: patientData.name,
        operation: patientData.operation,
        rating: parseInt(rating),
        practitioner: practitioner || 'Not specified',
        highlights: highlights.length ? highlights : ['General positive experience']
    };
    
    // Disable submit button and show loading
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Generating suggestions...';
    
    try {
        // Call AI suggestion endpoint
        const response = await fetch('/suggest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers: surveyAnswers })
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySuggestions(data.suggestions);
            show('suggestions-section');
        } else {
            throw new Error('Failed to generate suggestions');
        }
    } catch (error) {
        console.error('Error generating suggestions:', error);
        alert('Unable to generate suggestions. Please try again.');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Display AI-generated suggestions
function displaySuggestions(suggestions) {
    const container = $('suggestions-container');
    container.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <p>${suggestion}</p>
        `;
        
        card.addEventListener('click', () => {
            // Remove selection from other cards
            container.querySelectorAll('.card').forEach(c => c.classList.remove('selected'));
            // Select this card
            card.classList.add('selected');
            selectedSuggestion = suggestion;
            
            // Generate QR code after a brief delay
            setTimeout(() => {
                generateQRCode(suggestion);
                show('qr-section');
                startResetTimer();
            }, 500);
        });
        
        container.appendChild(card);
    });
}

// Generate QR code
function generateQRCode(reviewText) {
    const qrContainer = $('qr');
    const reviewPreview = $('selected-review');
    
    // Clear previous QR code
    qrContainer.innerHTML = '';
    
    // Set review preview
    reviewPreview.textContent = reviewText;
    
    // Generate QR code URL
    const origin = window.location.origin;
    const qrUrl = `${origin}/review.html?t=${encodeURIComponent(reviewText)}`;
    
    // Check if qrcode library is available
    if (typeof qrcode === 'undefined') {
        console.error('QRCode library not loaded');
        qrContainer.innerHTML = `
            <div style="padding: 40px; border: 2px dashed #ccc; text-align: center;">
                <p style="margin-bottom: 15px;"><strong>QR Code Generation Failed</strong></p>
                <p style="font-size: 14px; color: #666;">Manual Link:</p>
                <input type="text" value="${qrUrl}" style="width: 100%; padding: 8px; margin-top: 10px; font-size: 12px;" readonly onclick="this.select()">
                <p style="font-size: 12px; color: #888; margin-top: 10px;">Copy this link and open on your phone</p>
            </div>
        `;
        return;
    }
    
    try {
        // Generate QR code using qrcode-generator library
        const qr = qrcode(0, 'M'); // Error correction level M
        qr.addData(qrUrl);
        qr.make();
        
        // Create the QR code as an image
        const qrImage = qr.createDataURL(4, 4); // cell size 4, margin 4
        
        // Display as image
        qrContainer.innerHTML = `<img src="${qrImage}" alt="QR Code" style="max-width: 220px; max-height: 220px;">`;
        
        console.log('✅ QR Code generated successfully');
    } catch (error) {
        console.error('QR code generation error:', error);
        qrContainer.innerHTML = `
            <div style="padding: 40px; border: 2px dashed #ccc; text-align: center;">
                <p style="margin-bottom: 15px;"><strong>QR Code Generation Failed</strong></p>
                <p style="font-size: 14px; color: #666;">Manual Link:</p>
                <input type="text" value="${qrUrl}" style="width: 100%; padding: 8px; margin-top: 10px; font-size: 12px;" readonly onclick="this.select()">
                <p style="font-size: 12px; color: #888; margin-top: 10px;">Copy this link and open on your phone</p>
            </div>
        `;
    }
}

// Auto-reset functionality
function startResetTimer() {
    // Clear any existing timer
    if (resetTimer) {
        clearTimeout(resetTimer);
    }
    
    // Set 2-minute (120 seconds) timer
    resetTimer = setTimeout(() => {
        resetKiosk();
    }, 120000);
}

// Reset kiosk to initial state
function resetKiosk() {
    // Clear all data
    patientData = { name: '', operation: '' };
    surveyAnswers = {};
    selectedSuggestion = '';
    
    // Clear form fields
    $('password').value = '';
    $('patient-name').value = '';
    $('operation').value = '';
    
    // Reset survey form
    const surveyForm = $('survey-form');
    if (surveyForm) {
        surveyForm.reset();
        // Re-select 5-star rating as default
        const fiveStarRadio = surveyForm.querySelector('input[name="rating"][value="5"]');
        if (fiveStarRadio) {
            fiveStarRadio.checked = true;
        }
    }
    
    // Clear suggestions and QR code
    $('suggestions-container').innerHTML = '';
    $('qr').innerHTML = '';
    $('selected-review').textContent = '';
    
    // Hide error messages
    $('login-error').classList.add('hidden');
    
    // Show login section
    show('login-section');
    
    // Clear reset timer
    if (resetTimer) {
        clearTimeout(resetTimer);
        resetTimer = null;
    }
    
    console.log('Kiosk reset to initial state');
}

// Keyboard shortcut for staff reset
function handleKeyboardShortcuts(event) {
    // Press 'R' to reset (case insensitive) - Only works when NOT in input fields
    if (event.key.toLowerCase() === 'r' && !isInputFocused()) {
        console.log('Staff reset triggered by R key');
        resetKiosk();
    }
}

// Helper function to check if user is typing in an input field
function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
        activeElement.tagName === 'INPUT' || 
        activeElement.tagName === 'TEXTAREA' || 
        activeElement.tagName === 'SELECT'
    );
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Staff login
    $('loginBtn').addEventListener('click', handleLogin);
    $('password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    });
    
    // Patient details
    $('beginSurvey').addEventListener('click', handlePatientDetails);
    
    // Welcome to survey transition
    $('toSurveyBtn').addEventListener('click', () => {
        show('survey-section');
    });
    
    // Survey form
    $('survey-form').addEventListener('submit', handleSurvey);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Initial state
    show('login-section');
    
    console.log('🏥 Clinic Review Kiosk initialized');
});

// Handle page visibility for auto-reset
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, pause any timers if needed
        console.log('Kiosk hidden');
    } else {
        // Page is visible again
        console.log('Kiosk visible');
    }
});

// Prevent accidental page refresh
window.addEventListener('beforeunload', (e) => {
    // Only prevent if we're not on the login screen
    const loginSection = $('login-section');
    if (loginSection && loginSection.classList.contains('hidden')) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        show,
        handleLogin,
        handlePatientDetails,
        generateWelcomeMessage,
        resetKiosk
    };
} 