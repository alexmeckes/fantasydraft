#!/bin/bash
# Share script that properly activates venv

echo "🏈 Fantasy Draft App - Share Mode"
echo "================================="
echo ""

# Check if we're already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment already active"
else
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
    if [[ "$?" -eq 0 ]]; then
        echo "✅ Virtual environment activated"
    else
        echo "❌ Failed to activate venv, using direct path"
        echo "   Running: ./venv/bin/python app.py --share"
        ./venv/bin/python app.py --share
        exit
    fi
fi

echo ""
echo "🌐 Starting app with public sharing..."
echo "📡 Your public URL will appear below:"
echo "===================================="
echo ""

# Run with activated venv
python app.py --share 