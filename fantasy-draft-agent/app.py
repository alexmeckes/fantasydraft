#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces
"""

import sys
import os
import subprocess

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
            # First, ensure a2a-sdk is properly installed (it provides the 'a2a' module)
            print("Installing a2a-sdk first...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--force-reinstall",
                "a2a-sdk>=0.2.8"
            ])
            
            # Verify the a2a module is available
            try:
                import a2a
                print("✅ a2a module now available")
            except:
                print("❌ a2a module still not available after installing a2a-sdk")
            
            # Now install any-agent[a2a] without --no-deps so it gets what it needs
            print("Installing any-agent[a2a]...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--force-reinstall",
                "any-agent[a2a]"
            ])
            
            # Test the import again
            from any_agent.serving import A2AServingConfig
            print("✅ A2A components now available!")
                    
        except Exception as e:
            print(f"❌ Could not install A2A dependencies: {e}")
            print("ℹ️ A2A mode will not be available, but Basic Multiagent mode will work fine!")

# Try patching the import check before importing the app
if os.getenv("SPACE_ID"):
    try:
        # Import a2a_sdk first to ensure it's available
        import a2a_sdk
        print("✅ a2a_sdk imported successfully")
        
        # Now try to patch any_agent if needed
        import any_agent
        # Some versions might have a flag we can set
        if hasattr(any_agent, '_A2A_AVAILABLE'):
            any_agent._A2A_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Patching attempt: {e}")

# Import and run the enhanced app
from apps.app_enhanced import main

if __name__ == "__main__":
    main() 