# Fantasy Draft Multi-Agent Demo 🏈

A focused demonstration of AI agents with distinct strategies competing in a mock draft, showcasing agent-to-agent communication and multi-turn memory capabilities using the any-agent framework.

## Overview

This project showcases:
- **Multi-Turn Conversations**: AI agents that maintain context across multiple interactions
- **Multi-Agent Mock Drafts**: Six AI agents with distinct strategies competing in real-time
- **Agent Communication**: Agents comment on and respond to each other's picks
- **Interactive Web Interface**: Beautiful Gradio UI with multiple tabs for different features

## Key Features

### 🤖 AI Agent Capabilities
- Built with any-agent framework (tinyagent by default)
- Maintains conversation history and draft state
- Provides contextual advice based on draft flow
- Remembers previous interactions and strategies

### 🎯 Draft Strategies
- **Zero RB Strategy**: Prioritizes WRs early, RBs later
- **Best Player Available (BPA)**: Always takes the highest-ranked player
- **Robust RB**: Loads up on RBs in early rounds
- **Upside Hunter**: Targets high-ceiling breakout candidates

### 💬 Multi-Agent Features
- Real-time agent debates about picks
- Strategy-aware commentary
- Memory indicators showing what agents remember
- Commissioner announcements and draft management

## Quick Start

> **Note for Hugging Face Spaces**: The `requirements.txt` at the repository root is for HF Spaces deployment. The main application code is in `fantasy-draft-agent/`.

1. **Clone the repository**
   ```bash
   git clone https://github.com/alexmeckes/fantasydraft.git
   cd fantasydraft/fantasy-draft-agent
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the Gradio app**
   ```bash
   python app.py
   ```

5. **Or try the CLI demos**
   ```bash
   python demo.py          # Interactive CLI
   python demo_clean_multiturn.py  # Clean multi-turn demo
   ```

## Project Structure

```
fantasy-draft-agent/
├── agent.py              # Core FantasyDraftAgent class
├── app.py                # Gradio web interface
├── data.py               # Static NFL player database
├── demo.py               # CLI demonstration
├── multiagent_draft.py   # Multi-agent mock draft implementation
└── multiagent_scenarios.py # Agent communication scenarios
```

## Documentation

- [ENV_SETUP.md](fantasy-draft-agent/ENV_SETUP.md) - API key configuration
- [MULTIAGENT_DEMO.md](fantasy-draft-agent/MULTIAGENT_DEMO.md) - Multi-agent features
- [MULTITURN_VISUALS.md](fantasy-draft-agent/MULTITURN_VISUALS.md) - Visualization guide

## Video Demos

Perfect for LinkedIn demonstrations:
1. **Multi-Turn Conversations**: Shows context retention across interactions
2. **Mock Draft**: Interactive 6-team draft with agent communication
3. **Quick Demo**: Agents debating strategy in real-time

## Technical Details

- Built in < 100 lines of core agent code
- No external data dependencies (uses static player data)
- Multiple interfaces (CLI, Gradio web, real-time demos)
- Clear visual indicators for context retention
- Streaming output for real-time effect

## License

This project is open source and available under the MIT License. 