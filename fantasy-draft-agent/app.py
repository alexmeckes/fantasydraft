#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces and local deployment.
All dependencies should be installed via requirements.txt.
"""

import os
import sys

# Simple startup message
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
    
    # Check A2A installation
    print("🔍 Checking A2A installation...")
    try:
        import any_agent
        print(f"✅ any-agent version: {getattr(any_agent, '__version__', 'unknown')}")
        
        # Check if serving module exists
        import importlib.util
        spec = importlib.util.find_spec("any_agent.serving")
        if spec:
            print("✅ any_agent.serving module found")
            from any_agent.serving import A2AServingConfig
            print("✅ A2A components available!")
        else:
            print("❌ any_agent.serving module NOT found")
            print("📦 This suggests any-agent was installed without [a2a] extra")
            
            # Show what's actually in any_agent
            import any_agent
            import os
            agent_dir = os.path.dirname(any_agent.__file__)
            print(f"   any_agent location: {agent_dir}")
            print(f"   Contents: {os.listdir(agent_dir)}")
            if os.path.exists(os.path.join(agent_dir, 'serving')):
                print("   ⚠️ 'serving' directory exists but not importable")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        
else:
    print("🖥️ Running locally...")

# Import and run the main app
from apps.app import main

if __name__ == "__main__":
    main() 