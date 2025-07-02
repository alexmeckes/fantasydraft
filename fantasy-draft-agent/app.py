#!/usr/bin/env python3
"""
Entry point for the Fantasy Draft Multi-Agent application.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simple startup message
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
else:
    print("🖥️ Running locally...")

# Import and run the main app
from apps.app import main

if __name__ == "__main__":
    main() 