#!/usr/bin/env python3
"""Setup script to ensure a2a-sdk is properly installed and importable."""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("Setting up A2A dependencies...")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Step 1: Ensure pip is up to date
    print("\n1. Updating pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Step 2: Install a2a-sdk first
    print("\n2. Installing a2a-sdk...")
    if not install_package("a2a-sdk==0.2.9"):
        print("Failed to install a2a-sdk, trying without version pin...")
        install_package("a2a-sdk")
    
    # Step 3: Test if a2a imports
    print("\n3. Testing a2a import...")
    try:
        import a2a
        print("✅ a2a module imports successfully!")
        print(f"   Location: {a2a.__file__ if hasattr(a2a, '__file__') else 'No __file__'}")
    except ImportError as e:
        print(f"❌ Failed to import a2a: {e}")
        
        # Try to diagnose the issue
        print("\n   Checking installed packages...")
        result = subprocess.run([sys.executable, "-m", "pip", "show", "a2a-sdk"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   a2a-sdk is installed:")
            print("   " + result.stdout.replace("\n", "\n   "))
        else:
            print("   a2a-sdk is NOT installed!")
    
    # Step 4: Install any-agent with both a2a and openai extras
    print("\n4. Installing any-agent with a2a and openai extras...")
    install_package("any-agent[a2a,openai]>=0.21.0")
    
    print("\n✅ Setup complete!")

if __name__ == "__main__":
    main() 