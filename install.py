#!/usr/bin/env python3
"""
Installation script for Clinic Review Kiosk FastAPI version
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies:")
        print(stderr)
        return False

def check_installation():
    """Check if FastAPI is properly installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import qrcode
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def main():
    print("🏥 Clinic Review Kiosk - FastAPI Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Verify installation
    if not check_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\nTo start the application:")
    print("  python app.py")
    print("\nOr using uvicorn directly:")
    print("  uvicorn app:app --reload --host 0.0.0.0 --port 8000")
    print("\nThen open: http://localhost:8000")
    print("Login password: letmein")

if __name__ == "__main__":
    main() 