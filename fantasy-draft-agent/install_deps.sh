#!/bin/bash
# Install script for Hugging Face Spaces
# Ensures a2a-sdk is properly installed before starting the app

echo "=== Installing Dependencies for Fantasy Draft Demo ==="
echo "Python version: $(python --version)"

# Upgrade pip first
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install a2a-sdk explicitly
echo "Installing a2a-sdk..."
python -m pip install a2a-sdk==0.2.9 --verbose

# Verify a2a is importable
echo "Testing a2a import..."
python -c "import a2a; print('✅ a2a module imports successfully!')" || {
    echo "❌ Failed to import a2a, trying alternative install..."
    # Try installing without cache
    python -m pip install --no-cache-dir a2a-sdk==0.2.9
}

# Install any-agent with both a2a and openai extras
echo "Installing any-agent with a2a and openai extras..."
python -m pip install "any-agent[a2a,openai]==0.21.1"

# Install other dependencies
echo "Installing remaining dependencies..."
python -m pip install -r requirements.txt

# Final test
echo "Final import test..."
python test_a2a_import.py

echo "=== Installation Complete ===" 