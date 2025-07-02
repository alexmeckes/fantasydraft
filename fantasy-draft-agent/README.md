---
title: fantasy-draft-demo
emoji: 🏈
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.36.0
app_file: app.py
pinned: false
license: mit
python_version: 3.11
---

# 🏈 Fantasy Football Multi-Agent Draft System

An interactive fantasy football draft simulation featuring 6 AI agents with distinct personalities and strategies, built using the `any-agent` framework.

## ✨ Features

- **Interactive Mock Draft**: Play as Team 4 with 5 AI opponents
- **Distinct Agent Strategies**: Zero RB, Robust RB, Best Player Available, Upside Hunter
- **Multi-Turn Memory**: Agents remember picks and conversations throughout the draft
- **Agent Communication**: Agents comment on and respond to each other's picks
- **Strategic Advisor**: AI advisor helps you make informed draft decisions
- **Visual Draft Board**: Track all picks with a beautiful, real-time updated interface
- **Customizable Personalities**: Modify each agent's personality and trash-talk style

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd fantasy-draft-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-key-here'  # On Windows: set OPENAI_API_KEY=your-key-here
```

### Running the Application

```bash
cd apps
python app.py
```

Then open your browser to `http://localhost:7860`

## 🎮 How to Play

1. **Start the Draft**: Click "🏈 Start Mock Draft"
2. **Watch AI Picks**: Agents draft in snake order with commentary
3. **Make Your Pick**: When it's your turn (Position 4), type a player name
4. **Get Advice**: Your AI advisor provides recommendations based on available players
5. **Enjoy the Banter**: Watch agents trash-talk and defend their strategies

## 🤖 The Agents

- **Team 1 - Zero RB** 📘🤓: Avoids RBs early, loads up on WRs
- **Team 2 - BPA** 📗🧑‍💼: Pure value drafting, mocks reaching
- **Team 3 - Robust RB** 📙🧔: Old-school RB-heavy approach
- **Team 4 - YOU** 👤: Your position with AI advisor
- **Team 5 - Upside Hunter** 📓🤠: High risk/reward picks
- **Team 6 - BPA** 📗👨‍🏫: Another value drafter

## 🛠️ Technical Details

Built with:
- **any-agent**: Lightweight multi-agent framework
- **Gradio**: Interactive web interface
- **OpenAI GPT-4**: Powers agent decision-making
- **Multi-turn memory**: Agents maintain conversation history

## 📁 Project Structure

```
fantasy-draft-agent/
├── apps/
│   ├── app.py                   # Main Gradio interface
│   ├── multiagent_draft.py      # Core draft logic
│   └── multiagent_scenarios.py  # Agent communication scenarios
├── core/
│   ├── agent.py                 # Base agent implementation
│   ├── data.py                  # Player data and rankings
│   └── constants.py             # Configuration constants
└── requirements.txt
```

## 🎯 Key Features Explained

### Multi-Agent System
- Each agent runs independently with its own strategy
- Agents maintain memory of all interactions
- Natural rivalries create engaging commentary

### Interactive Gameplay
- Real-time draft board visualization
- Strategic advisor provides contextual recommendations
- Customizable agent personalities

### Memory System
- Agents remember previous picks and conversations
- References to earlier interactions create continuity
- Strategic adaptation based on draft flow

## 🚦 Deployment

The application is designed to run locally or on cloud platforms like Hugging Face Spaces. The single-process architecture ensures reliable performance without complex networking requirements.

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

[View Source Code](https://github.com/alexmeckes/fantasydraft) 