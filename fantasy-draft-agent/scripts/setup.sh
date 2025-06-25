#!/bin/bash

echo "🏈 Fantasy Draft App - Setup & Share"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if gradio is installed
if ! python -c "import gradio" 2>/dev/null; then
    echo "📥 Installing required packages..."
    pip install gradio openai python-dotenv
    echo "✅ Packages installed"
    echo ""
else
    echo "✅ Required packages already installed"
    echo ""
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not found!"
    echo ""
    echo "To set it temporarily for this session:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "  OPENAI_API_KEY=your-api-key-here"
    echo ""
    read -p "Press Enter to continue anyway..."
    echo ""
fi

echo "🌐 Starting app with public sharing..."
echo "📡 Your public URL will appear below:"
echo "===================================="
echo ""

# Run the app with sharing
python app.py --share 