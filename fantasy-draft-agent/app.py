#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces
"""

import sys
import os

# Check if we're on Hugging Face Spaces and need to handle A2A deps
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
    
    # Try to import A2A components
    try:
        from any_agent.serving import A2AServingConfig
        print("✅ A2A dependencies already available")
    except ImportError:
        print("⚠️ A2A dependencies not found, attempting to install...")
        try:
            import subprocess
            # Try to install the full A2A package
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "a2a-sdk>=0.2.8"])
            print("✅ Installed a2a-sdk")
        except Exception as e:
            print(f"❌ Could not install A2A dependencies: {e}")
            print("ℹ️ A2A mode will not be available, but Basic Multiagent mode will work fine!")

# Import and run the enhanced app
from apps.app_enhanced import main

if __name__ == "__main__":
    main() 