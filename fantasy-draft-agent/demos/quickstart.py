#!/usr/bin/env python3
"""
Fantasy Draft Agent - Quick Start Script
Checks dependencies and launches the web interface.
"""

import subprocess
import sys
import os


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   You have Python {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor} detected")


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = {
        'any_agent': 'any-agent[openai]',
        'gradio': 'gradio',
        'pydantic': 'pydantic',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    for import_name, install_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {install_name} is installed")
        except ImportError:
            missing.append(install_name)
            print(f"❌ {install_name} is not installed")
    
    return missing


def install_dependencies(packages):
    """Install missing packages."""
    print("\n📦 Installing missing dependencies...")
    for package in packages:
        print(f"   Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("✅ All dependencies installed!")


def check_api_key():
    """Check if OpenAI API key is set."""
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key found")
        return True
    else:
        print("\n⚠️  OpenAI API key not found!")
        print("\nTo set your API key:")
        print("  1. Get your key from: https://platform.openai.com/api-keys")
        print("  2. Set it using one of these methods:")
        print("     - Export: export OPENAI_API_KEY='your-key-here'")
        print("     - Create .env file with: OPENAI_API_KEY=your-key-here")
        print("\nThe app will still launch, but agent responses will fail without a key.")
        return False


def launch_app():
    """Launch the Gradio web interface."""
    print("\n🚀 Launching Fantasy Draft Agent Web Interface...")
    print("📡 Opening http://localhost:7860 in your browser...\n")
    
    # Try to import and run the app
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from apps.app import main
        main()
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        print("\nTry running directly: python apps/app.py")
        sys.exit(1)


def main():
    """Main quickstart function."""
    print("🏈 Fantasy Draft Agent - Quick Start")
    print("="*40)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    missing = check_dependencies()
    
    # Install missing dependencies
    if missing:
        response = input("\n🤔 Would you like to install missing dependencies? (y/n): ")
        if response.lower() == 'y':
            install_dependencies(missing)
        else:
            print("\n❌ Cannot proceed without dependencies.")
            print("   Run: pip install -r requirements.txt")
            sys.exit(1)
    
    # Check API key
    check_api_key()
    
    # Prompt to continue
    print("\n" + "="*40)
    response = input("🎯 Ready to launch the web interface? (y/n): ")
    if response.lower() != 'y':
        print("\n👋 Goodbye! Run 'python app.py' when you're ready.")
        sys.exit(0)
    
    # Launch the app
    launch_app()


if __name__ == "__main__":
    main() 