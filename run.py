#!/usr/bin/env python3
"""
Simple startup script for Clinic Review Kiosk
"""

import os
import sys

def main():
    print("🏥 Starting Clinic Review Kiosk...")
    print("📱 Access at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("📝 Please create .env file with your API keys")
        print("💡 Copy env.sample to .env and update values")
        print()
    
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
    except ImportError:
        print("❌ Error: Missing dependencies")
        print("📦 Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 