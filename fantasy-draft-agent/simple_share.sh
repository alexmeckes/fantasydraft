#!/bin/bash
# Simple share script - uses venv Python

echo "🌐 Starting app with public sharing..."
echo "📡 Your public URL will appear below:"
echo "===================================="

# Use venv Python directly (avoids activation issues)
./venv/bin/python app.py --share 