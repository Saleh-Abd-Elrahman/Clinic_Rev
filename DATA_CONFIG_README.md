# Clinic Data Configuration Guide

## 📁 Location
All clinic-specific data is centralized in: `public/js/data.js`

## 🎯 Purpose
This file makes it easy to modify treatments, doctors, messages, and UI text without touching multiple files.

## 📝 How to Modify

### 1. **Adding/Removing Treatments**
```javascript
treatments: [
    "Morpheus",
    "New Treatment",     // Add new - super simple!
    // "Old Treatment",  // Remove by commenting out
]
```

### 2. **Adding/Removing Doctors**
```javascript
practitioners: [
    "Dr. Sarah",
    "Dr. John",         // Add new doctor - just a string!
]
```

### 3. **Updating Welcome Messages**
```javascript
welcomeMessages: {
    'Morpheus': (name) => `Hi ${name}! Custom message for Morpheus treatment.`,
    'New Treatment': (name) => `Hi ${name}! Welcome message for new treatment.`,
}
```

### 4. **Modifying Experience Highlights**
```javascript
highlights: [
    "Professional staff",
    "New highlight",     // Add new option - just a string!
]
```

### 5. **Changing UI Text**
```javascript
labels: {
    loginTitle: "Staff Login",           // Change login screen title
    submitButton: "Generate Reviews",    // Change button text
    clinicName: "Your Clinic Name",      // Change main title
}
```

### 6. **Updating Error Messages**
```javascript
errorMessages: {
    invalidPassword: "Wrong password!",  // Customize error messages
    connectionError: "Network issue!",
}
```

### 7. **Adjusting Timing**
```javascript
timing: {
    resetTimerMinutes: 3,    // Change auto-reset time (in minutes)
    suggestionDelay: 1000,   // Change QR code delay (in milliseconds)
}
```

## 🔄 How It Works

1. **data.js** - Contains all configuration
2. **content-loader.js** - Reads data.js and populates HTML dynamically
3. **Other modules** - Import and use data for messages, errors, etc.

## ✅ Benefits

- **Single Source of Truth**: All clinic data in one place
- **Easy Updates**: Change treatments/doctors without editing multiple files
- **Consistent Messaging**: Centralized error messages and labels
- **No Code Changes**: Modify content without touching logic files

## 🚀 Making Changes

1. Edit `public/js/data.js`
2. Save the file
3. Refresh the browser
4. Changes appear automatically!

## 📋 Quick Checklist for New Clinic Setup

- [ ] Update `treatments` array with your procedures
- [ ] Update `practitioners` array with your doctors  
- [ ] Customize `welcomeMessages` for each treatment
- [ ] Add/remove `highlights` based on your clinic's strengths
- [ ] Update `clinicName` and other `labels`
- [ ] Adjust `timing` preferences
- [ ] Test all functionality

## 🎨 Example: Complete Setup

```javascript
export const CLINIC_DATA = {
    clinicName: "Beautiful Skin Clinic",
    
    treatments: [
        "Botox",
        "Filler", 
        "Laser Treatment",
        "Microneedling",
    ],
    
    practitioners: [
        "Dr. Smith",
        "Dr. Jones",
    ],
    
    highlights: [
        "Professional staff",
        "Clean facility", 
        "Amazing results",
        "Great value",
    ],
    
    welcomeMessages: {
        'Botox': (name) => `Hi ${name}! Hope your Botox treatment was comfortable!`,
        'Filler': (name) => `Hi ${name}! Hope you love your new look!`,
        'Laser Treatment': (name) => `Hi ${name}! Hope your laser treatment went smoothly!`,
    },
    
    // ... rest of configuration
};
```

## 🔧 Advanced: Mixed String/Object Format

If you ever need different display text vs stored value, you can mix formats:

```javascript
treatments: [
    "Botox",                    // Simple string
    "Filler",                   // Simple string  
    { value: "pdrn", label: "Salmon PDRN Therapy" },  // Object when needed
]
```

The system automatically handles both formats!

This approach makes maintaining your clinic review system incredibly simple! 