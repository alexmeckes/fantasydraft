# Enhanced Fantasy Draft App with A2A Integration

## Overview

The enhanced app (`app_enhanced.py`) combines the superior UI from the main app with real A2A (Agent-to-Agent) communication capabilities.

## Features

### 1. **Superior UI Preserved**
- Beautiful agent cards with distinct visual styles
- Clean, professional layout
- Comprehensive "How It Works" documentation
- All original formatting and styling

### 2. **A2A Communication Toggle**
Choose between two communication modes:

- **Simulated Mode** (Default)
  - Fast, single-process execution
  - Direct method calls between agents
  - Perfect for demos and development
  - No additional setup required

- **Real A2A Mode**
  - Distributed architecture
  - Each agent runs on its own HTTP server
  - True isolation with HTTP communication
  - Production-ready scalability
  - Agents on ports 5001, 5002, 5003, 5005, 5006

### 3. **Seamless Integration**
- Toggle modes without restarting the app
- Same user experience in both modes
- Automatic fallback if A2A agents fail
- Visual status indicators

## Usage

### Running the Enhanced App

1. **Activate Virtual Environment**
   ```bash
   cd fantasy-draft-agent
   source venv/bin/activate
   ```

2. **Set API Key**
   ```bash
   export OPENAI_API_KEY='your-key-here'
   ```

3. **Run the App**
   ```bash
   python apps/app_enhanced.py
   ```

4. **Access the UI**
   - Open browser to http://localhost:7860
   - Choose communication mode (Simulated or Real A2A)
   - Click "Start Mock Draft"

### Communication Modes

#### Simulated Mode
- No additional setup
- Agents communicate via direct method calls
- Fast execution
- Good for demos and testing

#### Real A2A Mode
- Automatically starts agent servers when selected
- Each agent runs independently on its own port
- True distributed communication
- Shows real-world A2A capabilities

### Architecture

```
┌─────────────────┐
│   Gradio UI     │
│  (Port 7860)    │
└────────┬────────┘
         │
┌────────┴────────┐
│ Enhanced App    │
│ - UI Management │
│ - Mode Toggle   │
│ - A2A Manager   │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Mode?   │
    └────┬────┘
         │
┌────────┴────────┬─────────────────┐
│ Simulated       │ Real A2A        │
│ - In-memory     │ - HTTP servers  │
│ - Direct calls  │ - Ports 5001-6  │
│ - Single proc   │ - Distributed   │
└─────────────────┴─────────────────┘
```

### Benefits

1. **Development**: Use simulated mode for fast iteration
2. **Testing**: Switch to A2A mode to test distributed behavior
3. **Demo**: Show both architectures to stakeholders
4. **Production**: A2A mode demonstrates production readiness

### Troubleshooting

#### Port Already in Use
If you see "address already in use" errors:
```bash
# Kill processes on the ports
lsof -ti:7860 | xargs kill -9
lsof -ti:5001 | xargs kill -9
lsof -ti:5002 | xargs kill -9
# ... etc for other ports
```

#### A2A Agents Not Responding
- Check console for agent startup messages
- Ensure OPENAI_API_KEY is set
- Try toggling back to Simulated mode

#### Performance
- Simulated mode is faster (no network overhead)
- A2A mode has slight delays due to HTTP communication
- Both modes provide the same user experience

## Next Steps

### To Replace Main App
If you want to make this the default app:
```bash
cp apps/app.py apps/app_original.py
cp apps/app_enhanced.py apps/app.py
```

### To Run Side-by-Side
Keep both versions and run whichever you prefer:
- `python apps/app.py` - Original app
- `python apps/app_enhanced.py` - Enhanced with A2A

### Customization
- Modify agent strategies in `A2AAgentManager.start_agents()`
- Adjust ports if needed
- Add more agents by extending the configs list
- Customize UI elements while preserving A2A functionality 