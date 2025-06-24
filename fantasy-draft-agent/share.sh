#!/bin/bash

echo "🚀 Fantasy Draft App - Public Share Mode"
echo "======================================="
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not found!"
    echo ""
    echo "To set it temporarily for this session:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to your shell profile for permanent use."
    echo ""
    read -p "Press Enter to continue anyway (app will fail without key)..."
fi

echo "🌐 Starting app with public sharing enabled..."
echo "📡 A public URL will be generated in a moment..."
echo ""

# Run the app with sharing enabled
python app.py --share 