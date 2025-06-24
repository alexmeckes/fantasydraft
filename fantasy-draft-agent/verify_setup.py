#!/usr/bin/env python3
"""
Verify that your Fantasy Draft Agent setup is complete.
"""

import os
import sys
from dotenv import load_dotenv

print("🔍 Fantasy Draft Agent - Setup Verification")
print("=" * 45)

# Load .env file
load_dotenv()

# Check Python version
print(f"\n✅ Python {sys.version.split()[0]} detected")

# Check .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
else:
    print("❌ .env file NOT found - run: cp .env.example .env")

# Check API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    if api_key == 'your-openai-api-key-here':
        print("⚠️  API key found but still using placeholder value!")
        print("   Edit .env and replace with your actual key")
    else:
        # Mask the key for security
        masked_key = api_key[:7] + "*" * 20 + api_key[-4:]
        print(f"✅ OpenAI API key loaded: {masked_key}")
else:
    print("❌ OpenAI API key NOT found in environment")

# Check required packages
print("\n📦 Checking dependencies...")
try:
    import any_agent
    print("✅ any-agent installed")
except ImportError:
    print("❌ any-agent NOT installed - run: pip install -r requirements.txt")

try:
    import gradio
    print("✅ gradio installed")
except ImportError:
    print("❌ gradio NOT installed - run: pip install -r requirements.txt")

try:
    import pydantic
    print("✅ pydantic installed")
except ImportError:
    print("❌ pydantic NOT installed - run: pip install -r requirements.txt")

# Summary
print("\n" + "=" * 45)
if api_key and api_key != 'your-openai-api-key-here':
    print("✅ Setup looks good! You're ready to run:")
    print("   python app.py         # For web interface")
    print("   python demo.py        # For command line")
else:
    print("⚠️  Please complete setup:")
    print("   1. Edit .env file")
    print("   2. Add your OpenAI API key")
    print("   3. Run this script again to verify")

print("\n📚 Documentation:")
print("   - ENV_SETUP.md    # API key setup guide")
print("   - VENV_GUIDE.md   # Virtual environment guide")
print("   - README.md       # General documentation") 