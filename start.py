#!/usr/bin/env python3
"""
Clinic Review Kiosk Startup Script
Checks environment variables and starts the FastAPI application
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please create a .env file with the following variables:")
        print()
        print("OPENAI_API_KEY=sk-your-openai-api-key-here")
        print("GOOGLE_PLACE_ID=ChIJ_your_google_place_id_here")
        print("ADMIN_PASSWORD=your-secure-admin-password-here")
        print("SECRET_KEY=your-secret-key-for-sessions-here")
        print()
        print("💡 You can copy .env.sample to .env and update the values")
        return False
    
    # Load and check required variables
    required_vars = ['OPENAI_API_KEY', 'ADMIN_PASSWORD', 'SECRET_KEY']
    missing_vars = []
    
    with open(env_file) as f:
        env_content = f.read()
        for var in required_vars:
            if f"{var}=" not in env_content or f"{var}=your-" in env_content or f"{var}=sk-your-" in env_content:
                missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or incomplete environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("📝 Please update your .env file with real values")
        return False
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import openai
        import qrcode
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install dependencies with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🏥 Clinic Review Kiosk - Starting Up...")
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment variables
    if not check_env_file():
        sys.exit(1)
    
    print("✅ Environment check passed!")
    print("🚀 Starting FastAPI server...")
    print()
    print("📱 Access the application at: http://localhost:8000")
    print("🔑 Use the ADMIN_PASSWORD from your .env file to login")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 