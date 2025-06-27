#!/bin/bash

# Run A2A Draft Demo Script

echo "🏈 Fantasy Draft A2A Demo"
echo "========================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activating virtual environment..."
    source venv/bin/activate
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY is not set!"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

# Run the demo
echo "🚀 Starting A2A Draft Demo..."
echo ""
echo "This will:"
echo "  1. Start 4 agent servers on ports 5001-5004"
echo "  2. Run a 2-round draft with A2A communication"
echo "  3. Show agent comments and trash talk"
echo ""
echo "Press Ctrl+C to stop at any time"
echo ""

python demos/a2a_draft_demo.py 