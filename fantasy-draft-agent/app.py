#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces
"""

import sys
import os

# Check if we're on Hugging Face Spaces
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
    print("ℹ️ Note: A2A mode is experimental on HF Spaces due to dependency issues.")
    print("ℹ️ Basic Multiagent mode is recommended and provides the full experience!")
    
    # Quick test to see if A2A imports work
    try:
        # Test the specific imports that fail
        import a2a  # This is what usually fails
        from any_agent.serving import A2AServingConfig
        print("✅ Surprisingly, full A2A dependencies are available! You can try A2A mode.")
    except ImportError as e:
        print(f"⚠️ Full A2A dependencies not available: {e}")
        # Check if lightweight A2A can work
        try:
            import httpx
            import fastapi
            import uvicorn
            print("✅ Lightweight A2A dependencies available! A2A mode will work using HTTP-only.")
            os.environ["A2A_MODE"] = "lightweight"
        except ImportError:
            print("✅ No problem! Basic Multiagent mode works perfectly and is recommended.")

# Import and run the enhanced app
from apps.app_enhanced import main

if __name__ == "__main__":
    main() 