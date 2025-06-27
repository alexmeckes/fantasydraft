# A2A Quick Start Guide

## 🚀 Running Real A2A Fantasy Draft

This guide shows you how to run the fantasy draft with **real Agent-to-Agent (A2A)** communication using the any-agent framework.

## Prerequisites

1. **Activate Virtual Environment**
```bash
cd fantasy-draft-agent
source venv/bin/activate
```

2. **Set OpenAI API Key**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. **Install Dependencies** (if not already installed)
```bash
pip install any-agent httpx pydantic nest-asyncio
```

## Option 1: Standalone A2A Demo

The simplest way to see real A2A in action:

```bash
# Make script executable (first time only)
chmod +x run_a2a_demo.sh

# Run the demo
./run_a2a_demo.sh
```

Or directly:
```bash
python demos/a2a_draft_demo.py
```

### What Happens:
- 4 agent servers start on ports 5001-5004
- Each agent has its own strategy and personality
- Agents communicate via HTTP using A2A protocol
- You'll see picks and real-time trash talk
- Servers shut down cleanly when done

### Example Output:
```
🚀 Starting A2A Draft Demo...

📡 Serving Team 1 - Zero RB on port 5001...
📡 Serving Team 2 - BPA on port 5002...
📡 Serving Team 3 - Robust RB on port 5003...
📡 Serving Team 4 - Upside on port 5004...

✅ All agents ready! Starting draft...

📍 ROUND 1
🎯 Team 1 is on the clock...
📋 Team 1 selects: **Justin Jefferson** (WR)
   💭 "Elite WR talent wins championships!"
   🗣️  "Let the RB-drafters reach for injury risks!"

   💬 Team 3: "Passing on McCaffrey? Your loss!"
```

## Option 2: Gradio App with A2A Toggle

Run the enhanced app that supports both modes:

```bash
python apps/app_with_a2a.py
```

### Features:
- Toggle between "Simulated" and "Real A2A" modes
- Visual comparison of both approaches
- Same UI, different backend
- See the performance difference

### Using the App:
1. Open http://localhost:7860
2. Select "Real A2A" mode
3. Click "Start Draft"
4. Watch agents communicate via real servers!

## Understanding the Architecture

### Simulated (Original):
```
App → DraftAgent → LLM → Response
 ↓
All agents in same process
```

### Real A2A:
```
App → HTTP → Agent Server 1 (port 5001) → LLM
     → HTTP → Agent Server 2 (port 5002) → LLM
     → HTTP → Agent Server 3 (port 5003) → LLM
     → HTTP → Agent Server 4 (port 5004) → LLM
```

## Key Differences You'll Notice

1. **Startup Time**: A2A takes ~2 seconds to start servers
2. **Communication**: Each message goes over HTTP
3. **True Isolation**: Agents can't share memory
4. **Scalability**: Could run on different machines
5. **Production Ready**: This is how real systems work

## Troubleshooting

### "Port already in use"
```bash
# Kill any existing processes on the ports
lsof -ti:5001-5005 | xargs kill -9
```

### "Module not found"
```bash
# Ensure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### "API key not found"
```bash
export OPENAI_API_KEY='sk-...'
```

## Advanced: Customizing Agents

Edit `demos/a2a_draft_demo.py` to modify:

1. **Agent Strategies**:
```python
agent_configs = [
    ("Team 1 - Zero RB", "Zero RB Strategy", 5001, 
     "Your custom personality here"),
    # Add more agents...
]
```

2. **Port Numbers**:
```python
port = 5010  # Use any available port
```

3. **Number of Rounds**:
```python
await demo.run_draft(rounds=3)  # Run 3 rounds
```

## Next Steps

1. **Explore the Code**: 
   - `core/real_a2a_draft.py` - Full implementation
   - `core/a2a_with_tools.py` - Simpler patterns
   - `docs/A2A_IMPLEMENTATION_GUIDE.md` - Technical details

2. **Build Your Own**:
   - Use the patterns to create your own A2A agents
   - Experiment with different frameworks (openai, langchain, etc.)
   - Deploy agents to different servers

3. **Production Considerations**:
   - Add authentication to agent endpoints
   - Use environment-specific ports
   - Implement health checks
   - Add logging and monitoring

## Summary

You've now seen the difference between simulated and real A2A communication! The real A2A approach provides:

- ✅ True distributed architecture
- ✅ Agent isolation and independence  
- ✅ HTTP-based communication
- ✅ Production-ready patterns
- ✅ Scalable multi-agent systems

Happy drafting with real A2A! 🏈 