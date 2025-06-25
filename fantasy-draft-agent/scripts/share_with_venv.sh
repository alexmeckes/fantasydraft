#!/bin/bash
# Share script that properly activates venv

echo "🏈 Fantasy Draft App - Share Mode"
echo "================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if we're already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment already active"
else
    echo "🔄 Activating virtual environment..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        if [[ "$?" -eq 0 ]]; then
            echo "✅ Virtual environment activated"
        else
            echo "❌ Failed to activate venv, using direct path"
            echo "   Running: venv/bin/python apps/app.py --share"
            venv/bin/python apps/app.py --share
            exit
        fi
    else
        echo "❌ Virtual environment not found!"
        echo "   Please run: python -m venv venv && pip install -r requirements.txt"
        exit 1
    fi
fi

echo ""
echo "🌐 Starting app with public sharing..."
echo "📡 Your public URL will appear below:"
echo "===================================="
echo ""

# Run with activated venv
python apps/app.py --share 