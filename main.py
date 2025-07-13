"""
Simple startup script for Clinic Review Kiosk
"""

import os
import sys

if __name__ == "__main__":
    import uvicorn
    from app import app  # Import the app instance

    print("🏥 Starting Clinic Review Kiosk...")
    print("📱 Access at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning"
    ) 