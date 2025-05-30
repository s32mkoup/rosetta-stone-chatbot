#!/usr/bin/env python3
"""
Setup environment for Rosetta Stone Agent
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/knowledge_base",
        "data/conversation_logs", 
        "data/persona_memories",
        "data/templates",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def check_environment_variables():
    """Check for required environment variables"""
    # Try to load .env file first
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📄 Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not available, checking system environment only")
    
    required_vars = ["HF_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Show partial token for verification
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✅ {var} found: {masked_value}")
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set your Hugging Face token:")
        print("export HF_TOKEN=hf_your_token_here")
        print("Or ensure it's in your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_imports():
    """Test if all required packages can be imported"""
    test_packages = [
        "huggingface_hub",
        "gradio", 
        "requests",
        "asyncio"
    ]
    
    failed_imports = []
    
    for package in test_packages:
        try:
            __import__(package)
            print(f"✅ {package} import successful")
        except ImportError:
            failed_imports.append(package)
            print(f"❌ {package} import failed")
    
    return len(failed_imports) == 0

def main():
    """Main setup function"""
    print("🏺 Rosetta Stone Agent - Environment Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Setup directories
    setup_directories()
    
    # Test imports
    if not test_imports():
        print("❌ Some imports failed. Please check your installation.")
        sys.exit(1)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    print("\n" + "=" * 50)
    if env_ok:
        print("🎉 Setup completed successfully!")
        print("You can now run:")
        print("  python interfaces/cli_chat.py")
        print("  python interfaces/gradio_app.py")
    else:
        print("⚠️  Setup completed with warnings.")
        print("Please configure environment variables before running the agent.")

if __name__ == "__main__":
    main()