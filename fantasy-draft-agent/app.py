#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces
"""

import sys
import os
import subprocess

# Check if we're on Hugging Face Spaces
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
    print("ℹ️ Checking A2A dependencies...")
    
    # Try to import a2a, install if needed
    try:
        import a2a
        print("✅ a2a module already available")
    except ImportError:
        print("⚠️ a2a module not found, attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "a2a-sdk==0.2.9"])
            import a2a
            print("✅ Successfully installed and imported a2a!")
        except Exception as e:
            print(f"❌ Failed to install a2a-sdk: {e}")
    
    # Now test the full A2A imports
    try:
        from any_agent.serving import A2AServingConfig
        from any_agent.tools import a2a_tool_async
        print("✅ Full A2A dependencies are available! A2A mode will work.")
    except ImportError as e:
        print(f"⚠️ A2A components not available from any_agent: {e}")
        # Try to fix by reinstalling any-agent with a2a extra
        print("📦 Attempting to install any-agent[a2a]...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "any-agent[a2a,openai]>=0.22.0", "--force-reinstall"])
            # Try import again
            from any_agent.serving import A2AServingConfig
            from any_agent.tools import a2a_tool_async
            print("✅ Successfully installed! A2A mode will work.")
        except Exception as e2:
            print(f"❌ Failed to install any-agent[a2a]: {e2}")
            print("✅ Basic Multiagent mode will be used instead.")
            
else:
    # Not on HF Spaces
    print("🖥️ Running locally...")

# Import and run the enhanced app
from apps.app_enhanced import main

if __name__ == "__main__":
    main() 