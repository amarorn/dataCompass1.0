#!/usr/bin/env python3
"""
Quick start script for DataCompass 2.0
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    print("✅ Python version OK")

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found, copying from .env.example")
        example_file = Path(".env.example")
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("✅ .env file created - Please edit with your credentials")
        else:
            print("❌ .env.example not found")
            sys.exit(1)
    else:
        print("✅ .env file found")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed")

def run_application():
    """Run the FastAPI application"""
    print("🚀 Starting DataCompass 2.0...")
    print("-" * 50)
    print("📱 WhatsApp Analytics Platform with PyWA")
    print("🌐 Server: http://localhost:3000")
    print("📚 Docs: http://localhost:3000/docs")
    print("🔧 Health: http://localhost:3000/health")
    print("-" * 50)
    
    # Set Python path
    os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")
    
    # Run with uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.main:app",
        "--host", "0.0.0.0",
        "--port", "3000",
        "--reload"
    ])

def main():
    """Main entry point"""
    print("🎯 DataCompass 2.0 - Python Version with PyWA")
    print("=" * 50)
    
    check_python_version()
    check_env_file()
    
    # Ask to install dependencies
    response = input("\n📦 Install/update dependencies? (y/n): ")
    if response.lower() == 'y':
        install_dependencies()
    
    print("\n")
    run_application()

if __name__ == "__main__":
    main()