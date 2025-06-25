# 🏈 Fantasy Draft Agent MVP

An AI-powered fantasy football draft assistant built with [any-agent](https://github.com/any-agent/any-agent) framework. This MVP demonstrates multi-turn conversation capabilities through pre-crafted scenarios, showcasing how AI can maintain context and provide strategic draft advice.

## 🎯 Features

- **Multi-turn Conversations**: Maintains context across multiple interactions
- **Strategic Draft Advice**: Provides recommendations based on draft position and available players
- **Position Analysis**: Evaluates scarcity and tier breakdowns
- **Team Stacking**: Identifies QB-receiver correlations
- **Interactive Mode**: Real-time draft assistance
- **Demo Scenarios**: 4 pre-built scenarios showcasing different capabilities
- **Web Interface**: Beautiful Gradio UI for easy interaction
- **Multi-Agent Mock Draft**: Watch AI agents communicate and compete in a live draft

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (or compatible LLM API)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd fantasy-draft-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key (recommended method):
```bash
# Create .env file from template
cp .env.example .env

# Edit .env and add your OpenAI API key
# The file should contain:
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

Alternative method (less secure):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Test Installation

```bash
python demo.py --test
```

## 🔑 API Key Setup

The app uses `python-dotenv` to automatically load your API key from a `.env` file:

1. **Create `.env` file**: `cp .env.example .env`
2. **Edit `.env`**: Add your key: `OPENAI_API_KEY=sk-proj-xxxxx`
3. **Never commit `.env`**: It's already in `.gitignore`

See [ENV_SETUP.md](ENV_SETUP.md) for detailed instructions.

## 🎮 Usage

### Web Interface (Recommended)

Launch the Gradio web interface for the best experience:

```bash
python apps/app.py
```

Then open http://localhost:7860 in your browser.

The web interface includes:
- **💬 Draft Assistant**: Interactive chat with context retention
- **📊 Player Analysis**: Compare players and analyze positions
- **🎯 Available Players**: Browse and filter available players
- **🎬 Demo Scenarios**: Run pre-built conversation scenarios
- **📋 Draft Board**: View the current draft state

### Command Line Interface

Quick demo:

```bash
python demos/cli_demo.py --quick
```

Interactive mode:

```bash
python demos/cli_demo.py --interactive
```

Commands in interactive mode:
- Ask any draft question
- `pick <player>` - Draft a player
- `roster` - View your current roster
- `reset` - Start a new draft
- `quit` - Exit

Run demo scenarios:

```bash
python demos/cli_demo.py --scenario 1  # Run "The Opening Pick" scenario
python demos/cli_demo.py --all-scenarios  # Run all scenarios
```

## 🎮 Running Demos

### Basic Demo
```bash
python demos/cli_demo.py
```

### Multi-Turn Demos
```bash
# Clean multi-turn demo (recommended)
python demos/multiturn_demo.py

# Quick start helper
python demos/quickstart.py
```

### Web Interface
```bash
python apps/app.py
# Then open http://localhost:7860
```

### Quick Start
The quickstart script will check dependencies and launch the web interface:
```bash
python demos/quickstart.py
```

## 📚 Demo Scenarios

1. **The Opening Pick** - User has 5th pick, top 4 players gone. Shows strategy adaptation.
2. **The Position Run** - Round 3, QB run happening. Shows patience and value finding.
3. **The Sleeper Question** - Round 10, looking for upside. Shows deep knowledge.
4. **The Stack Builder** - Has Mahomes, wants receivers. Shows correlation strategy.

## 🏗️ Architecture

```
fantasy-draft-agent/
├── core/                 # Core functionality
│   ├── agent.py         # FantasyDraftAgent class using any-agent
│   ├── data.py          # Static player data (top 50 players)
│   ├── scenarios.py     # Pre-crafted demo scenarios
│   └── visualizer.py    # ASCII visualizations for demos
├── apps/                 # Application interfaces
│   ├── app.py          # Gradio web interface
│   ├── multiagent_draft.py     # Multi-agent mock draft
│   └── multiagent_scenarios.py # A2A communication scenarios
├── demos/               # Demo scripts
│   ├── cli_demo.py     # Command-line interface
│   ├── multiturn_demo.py # Multi-turn demonstration
│   └── quickstart.py   # Quick start helper
├── docs/                # Documentation
│   ├── ENV_SETUP.md    # Environment setup guide
│   ├── MULTIAGENT_DEMO.md # Multi-agent features
│   └── ...             # Other documentation
├── scripts/             # Utility scripts
│   ├── setup.sh        # Setup script
│   └── start_venv.sh   # Virtual environment starter
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Key Components

- **FantasyDraftAgent**: Main agent class with conversation memory
- **Tools**: Player stats, best available, position analysis, stacking options
- **ScenarioRunner**: Manages and executes demo scenarios
- **Visualizer**: Creates ASCII player cards and draft boards
- **FantasyDraftApp**: Gradio interface wrapper

## 💡 Example Usage

```python
from agent import FantasyDraftAgent

# Create agent
agent = FantasyDraftAgent()

# Ask for advice
response = agent.run("I have the 5th pick. Who should I target?")
print(response)

# Follow-up question (maintains context)
response = agent.run("What about in round 2?")
print(response)
```

## 🔧 Customization

### Change the LLM Model

Edit `agent.py`:

```python
self.agent = AnyAgent.create(
    framework="openai",  # or "langchain", "llama_index", etc.
    AgentConfig(
        model_id="gpt-4",  # Change model here
        # ...
    )
)
```

### Add More Players

Edit `data.py` to add more players to the `TOP_PLAYERS` dictionary.

### Create New Scenarios

Add new scenarios to `SCENARIOS` in `scenarios.py`.

### Customize the Web Interface

Edit `app.py` to modify the Gradio interface, add new tabs, or change the styling.

## 📊 Visual Components

The agent includes ASCII visualizations for:
- Player cards with stats
- Side-by-side player comparisons
- Draft board snapshots
- Roster summaries
- Decision summaries

## 🎯 MVP Scope

This MVP focuses on:
- ✅ Multi-turn conversation capabilities
- ✅ Context retention across interactions
- ✅ Strategic draft advice
- ✅ Demo-ready scenarios
- ✅ Visual web interface

Not included (future enhancements):
- ❌ Live draft integration
- ❌ Real-time data feeds
- ❌ Full 15-round drafts
- ❌ Trade analysis
- ❌ Season-long management

## 🤝 Contributing

This is an MVP demonstration. For production features, consider:
- Adding real-time player data APIs
- Implementing live draft room integration
- Expanding to other fantasy sports
- Adding machine learning for player projections

## 📝 License

MIT License - feel free to use and modify for your own projects!

## 🙏 Acknowledgments

Built with [any-agent](https://github.com/any-agent/any-agent) - a unified interface for AI agent frameworks.

---

**Built in < 100 lines of core agent code!** 🚀

## 📚 Documentation

- `README.md` - This file
- `ENV_SETUP.md` - Environment and API key setup guide
- `VENV_GUIDE.md` - Virtual environment instructions  
- `MULTITURN_VISUALS.md` - Guide to multi-turn visualization features
- `MULTIAGENT_DEMO.md` - Multi-agent mock draft documentation
- `screenshots.md` - Visual examples of the app in action
