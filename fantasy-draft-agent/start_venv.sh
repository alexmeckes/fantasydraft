#!/bin/bash
# Fantasy Draft Agent - Virtual Environment Setup Script

echo "🏈 Fantasy Draft Agent - Virtual Environment Setup"
echo "=================================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! pip show any-agent > /dev/null 2>&1; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  Warning: OPENAI_API_KEY not found in environment"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

echo ""
echo "🎉 Virtual environment is ready!"
echo ""
echo "To start the web interface:"
echo "   python app.py"
echo ""
echo "To start the CLI:"
echo "   python demo.py --interactive"
echo ""
echo "To deactivate the venv later:"
echo "   deactivate"
echo "" 