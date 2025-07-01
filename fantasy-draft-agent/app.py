#!/usr/bin/env python3
"""
Entry point for Hugging Face Spaces and local deployment.
All dependencies should be installed via requirements.txt.
"""

import os
import sys

# Apply typing compatibility patch for Python 3.11 BEFORE any other imports
from datetime import datetime
print(f"\n===== Application Startup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typing_patch

# Simple startup message
if os.getenv("SPACE_ID"):
    print("🤗 Running on Hugging Face Spaces...")
    
    # Check A2A installation
    print("🔍 Checking A2A installation...")
    
    # Check any-agent version
    try:
        import any_agent
        print(f"✅ any-agent version: {any_agent.__version__}")
    except ImportError as e:
        print(f"❌ any-agent not installed: {e}")

    # Check for httpx
    try:
        import httpx
        print(f"✅ httpx version: {httpx.__version__}")
    except ImportError as e:
        print(f"❌ httpx not installed: {e}")

    # Check for a2a module
    try:
        import a2a
        import importlib.metadata
        a2a_version = importlib.metadata.version('a2a-sdk')
        print(f"✅ a2a module found (a2a-sdk version: {a2a_version})")
    except ImportError as e:
        print(f"❌ a2a module not found: {e}")

    # Check if any_agent.serving exists
    try:
        import any_agent.serving
        print("✅ any_agent.serving module found")
    except ImportError as e:
        print(f"❌ any_agent.serving module not found: {e}")
        
    # Check for AgentSkill specifically
    try:
        from a2a.types import AgentSkill
        print("✅ AgentSkill import successful")
    except ImportError as e:
        print(f"❌ AgentSkill import failed: {e}")
        
    # Check for server dependencies
    print("\n🔍 Checking server dependencies:")
    try:
        import uvicorn
        print(f"✅ uvicorn found: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ uvicorn not found: {e}")
        
    try:
        import starlette
        print(f"✅ starlette found: {starlette.__version__}")
    except ImportError as e:
        print(f"❌ starlette not found: {e}")
        
    try:
        from a2a.server import apps
        print("✅ a2a.server.apps found")
    except ImportError as e:
        print(f"❌ a2a.server.apps not found: {e}")
        
    try:
        import sse_starlette
        print("✅ sse-starlette found")
    except ImportError as e:
        print(f"❌ sse-starlette not found: {e}")
        
    # Test the specific imports that any_agent.serving tries
    print("\n🔍 Testing any_agent.serving imports:")
    
    # Test A2AServingConfig import
    try:
        from any_agent.serving.a2a.config_a2a import A2AServingConfig
        print("✅ A2AServingConfig direct import successful")
    except ImportError as e:
        print(f"❌ A2AServingConfig direct import failed: {e}")
        
    # Test server_a2a imports
    try:
        from any_agent.serving.a2a.server_a2a import serve_a2a
        print("✅ serve_a2a direct import successful")
    except ImportError as e:
        print(f"❌ serve_a2a direct import failed: {e}")
        
    # Test other imports from server_a2a
    try:
        from any_agent.serving.a2a.server_a2a import (
            _get_a2a_app,
            _get_a2a_app_async,
            serve_a2a_async,
        )
        print("✅ All server_a2a imports successful")
    except ImportError as e:
        print(f"❌ server_a2a imports failed: {e}")
        import traceback
        traceback.print_exc()

    # Try to import A2AServingConfig with more detailed error handling
    try:
        from any_agent.serving import A2AServingConfig
        print("✅ A2AServingConfig import successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        # Try to get more details
        try:
            import traceback
            print("Full traceback:")
            traceback.print_exc()
        except:
            pass
        
else:
    print("🖥️ Running locally...")

# Import and run the main app
from apps.app import main

if __name__ == "__main__":
    main() 