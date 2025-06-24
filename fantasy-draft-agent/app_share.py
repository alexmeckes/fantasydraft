#!/usr/bin/env python3
"""
Quick share version of the app - creates a public URL for 72 hours
"""

# Import the main app
from app import create_gradio_interface
import os

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("\n⚠️  Warning: OPENAI_API_KEY not found!")
    print("Set it using: export OPENAI_API_KEY='your-key-here'\n")

# Launch with sharing enabled
print("🚀 Launching with public sharing...")
print("📡 A public URL will be generated that works for 72 hours\n")

demo = create_gradio_interface()
demo.launch(share=True) 