#!/usr/bin/env python3
"""Debug script to understand a2a import issues on HF Spaces"""

import sys
import os
import subprocess
import importlib.util
import site

def debug_a2a():
    """Comprehensive a2a debug information"""
    print("=== A2A Import Debug Report ===\n")
    
    # 1. Python info
    print("1. Python Environment:")
    print(f"   Python: {sys.version}")
    print(f"   Executable: {sys.executable}")
    print(f"   Platform: {sys.platform}")
    print(f"   PATH: {os.environ.get('PATH', 'Not set')[:200]}...")
    print()
    
    # 2. Site packages
    print("2. Site Packages:")
    for path in site.getsitepackages():
        print(f"   - {path}")
    print(f"   User site: {site.getusersitepackages()}")
    print()
    
    # 3. Check if a2a-sdk is installed
    print("3. Package Installation:")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "a2a-sdk"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ a2a-sdk is installed")
            print("   " + result.stdout.split('\n')[1])  # Version line
            print("   " + result.stdout.split('\n')[7])  # Location line
        else:
            print("   ❌ a2a-sdk NOT installed")
    except Exception as e:
        print(f"   ❌ Error checking pip: {e}")
    print()
    
    # 4. Try to find a2a module
    print("4. Module Search:")
    a2a_spec = importlib.util.find_spec("a2a")
    if a2a_spec:
        print(f"   ✅ a2a module found at: {a2a_spec.origin}")
    else:
        print("   ❌ a2a module NOT found by importlib")
    
    # Manual search in site-packages
    print("   Manual search in site-packages:")
    found = False
    for path in site.getsitepackages() + [site.getusersitepackages()]:
        if os.path.exists(path):
            a2a_path = os.path.join(path, "a2a")
            if os.path.exists(a2a_path):
                print(f"   ✅ Found a2a directory at: {a2a_path}")
                found = True
                # Check contents
                if os.path.exists(os.path.join(a2a_path, "types.py")):
                    print(f"      ✅ types.py exists")
                else:
                    print(f"      ❌ types.py missing")
    if not found:
        print("   ❌ No a2a directory found in any site-packages")
    print()
    
    # 5. Try importing step by step
    print("5. Import Tests:")
    
    # Test 1: Import a2a
    try:
        import a2a
        print(f"   ✅ import a2a: Success ({a2a.__file__})")
    except Exception as e:
        print(f"   ❌ import a2a: {type(e).__name__}: {e}")
    
    # Test 2: Import a2a.types
    try:
        import a2a.types
        print(f"   ✅ import a2a.types: Success")
    except Exception as e:
        print(f"   ❌ import a2a.types: {type(e).__name__}: {e}")
    
    # Test 3: Import AgentSkill from a2a.types
    try:
        from a2a.types import AgentSkill
        print(f"   ✅ from a2a.types import AgentSkill: Success")
    except Exception as e:
        print(f"   ❌ from a2a.types import AgentSkill: {type(e).__name__}: {e}")
    
    # Test 4: Import any_agent
    try:
        import any_agent
        print(f"   ✅ import any_agent: Success")
    except Exception as e:
        print(f"   ❌ import any_agent: {type(e).__name__}: {e}")
    
    # Test 5: Import any_agent.serving
    try:
        from any_agent.serving import A2AServingConfig
        print(f"   ✅ from any_agent.serving import A2AServingConfig: Success")
    except Exception as e:
        print(f"   ❌ from any_agent.serving import A2AServingConfig: {type(e).__name__}: {e}")
    print()
    
    # 6. sys.path
    print("6. Python sys.path:")
    for i, path in enumerate(sys.path[:10]):
        print(f"   [{i}] {path}")
    if len(sys.path) > 10:
        print(f"   ... and {len(sys.path) - 10} more")
    print()
    
    # 7. Environment variables
    print("7. Relevant Environment Variables:")
    for var in ["PYTHONPATH", "SPACE_ID", "HOME", "PWD", "VIRTUAL_ENV"]:
        val = os.environ.get(var, "Not set")
        if len(val) > 100:
            val = val[:100] + "..."
        print(f"   {var}: {val}")
    print()
    
    # 8. Try reinstalling a2a-sdk
    print("8. Installation Test:")
    print("   Attempting to install a2a-sdk...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "a2a-sdk", "--no-deps"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("   ✅ Install succeeded (no deps)")
            # Try import again
            try:
                import importlib
                if 'a2a' in sys.modules:
                    importlib.reload(sys.modules['a2a'])
                else:
                    import a2a
                print("   ✅ Import after install: Success")
            except Exception as e:
                print(f"   ❌ Import after install: {e}")
        else:
            print(f"   ❌ Install failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Install error: {e}")
    
    print("\n=== End Debug Report ===")


if __name__ == "__main__":
    debug_a2a() 