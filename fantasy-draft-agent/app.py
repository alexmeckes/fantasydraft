#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces and local deployment.
All dependencies should be installed via requirements.txt.
"""

import os

# Simple startup message
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
else:
    print("🖥️ Running locally...")

# Import and run the main app
from apps.app import main

if __name__ == "__main__":
    main() 