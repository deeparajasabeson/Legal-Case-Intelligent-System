#!/usr/bin/env python3
"""
Legal AI System - Production Runner
Complete legal research platform with AI agents and privilege protection
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")

    try:
        import flask
        import google.generativeai
        import sqlite3
        print("✅ Backend dependencies OK")
    except ImportError as e:
        print(f"❌ Missing backend dependency: {e}")
        print("Run: pip install -r backend/requirements.txt")
        return False

    # Check if node_modules exists
    frontend_deps = Path("frontend/node_modules")
    if not frontend_deps.exists():
        print("❌ Frontend dependencies missing")
        print("Run: cd frontend && npm install")
        return False

    print("✅ Frontend dependencies OK")
    return True

def initialize_database():
    """Initialize legal database with schema and sample data"""
    print("🗄️ Initializing legal database...")

    try:
        os.chdir("backend")
        result = subprocess.run([sys.executable, "init_database.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Database initialized successfully")
            print(result.stdout)
        else:
            print(f"❌ Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False
    finally:
        os.chdir("..")

    return True

def check_environment():
    """Check environment variables"""
    print("🔑 Checking environment configuration...")

    env_file = Path("backend/.env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating template...")
        template = """# Legal AI System Environment Configuration
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
DATABASE_URL=sqlite:///database/legal_data.db
SECRET_KEY=your_secret_key_here
"""
        with open("backend/.env", "w") as f:
            f.write(template)
        print("📝 Template .env created. Please add your Gemini API key.")
        return False

    # Check for Gemini API key
    from dotenv import load_dotenv
    load_dotenv("backend/.env")

    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not configured")
        print("Please add your Gemini API key to backend/.env")
        return False

    print("✅ Environment configuration OK")
    return True

def start_backend():
    """Start Flask backend server"""
    print("🚀 Starting legal AI backend...")

    try:
        os.chdir("backend")
        # Start Flask server in background
        process = subprocess.Popen([sys.executable, "app.py"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        print("✅ Backend server starting on http://localhost:5000")
        return process
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        return None
    finally:
        os.chdir("..")

def start_frontend():
    """Start React frontend server"""
    print("🌐 Starting legal AI frontend...")

    try:
        os.chdir("frontend")
        # Start React development server
        process = subprocess.Popen(["npm", "start"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        print("✅ Frontend server starting on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Frontend startup failed: {e}")
        return None
    finally:
        os.chdir("..")

def main():
    """Main runner for Legal AI system"""
    print("⚖️  LEGAL AI CASE INTELLIGENCE SYSTEM")
    print("=" * 50)

    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)

    if not check_environment():
        sys.exit(1)

    if not initialize_database():
        sys.exit(1)

    print("\n🎯 Starting Legal AI Platform...")

    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)

    # Wait for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)

    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)

    print("\n" + "=" * 50)
    print("✅ Legal AI System Running Successfully!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:5000")
    print("📊 Legal Research: http://localhost:3000/research")
    print("⚖️  Case Analysis: http://localhost:3000/case-analysis")
    print("📄 Document Review: http://localhost:3000/document-review")
    print("🔍 Precedent Finder: http://localhost:3000/precedent-finder")
    print("🛡️  Ethics Monitor: http://localhost:3000/ethics")
    print("\n⚠️  IMPORTANT: All communications are protected by attorney-client privilege")
    print("📋 Ensure compliance with ABA Model Rules of Professional Conduct")
    print("\n🛑 Press Ctrl+C to stop the system")

    try:
        # Keep processes running
        while True:
            time.sleep(1)

            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break

            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Legal AI System...")

        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")

        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend server stopped")

        print("👋 Legal AI System shutdown complete")

if __name__ == "__main__":
    main()