# Fantasy Draft Agent MVP - One Week Build Plan

## Simplified Scope

### What We're Building
A demo-focused NFL Fantasy Draft AI Agent that showcases Any-Agent's multi-turn conversation capabilities through 3-5 pre-crafted scenarios. No live drafting, no real-time data - just compelling conversational demos.

### What We're NOT Building (Yet)
- Live draft integration
- Real-time data feeds
- Full 15-round draft simulation
- Multiple league type support
- Trade analyzer
- Season-long features

## Day-by-Day Plan

### Day 1: Setup & Basic Agent
**Goal**: Get Any-Agent running with basic fantasy knowledge

```python
from any_agent import AnyAgent, AgentConfig

# Simple agent with hardcoded knowledge
fantasy_agent = AnyAgent.create(
    "tinyagent",
    AgentConfig(
        model_id="gpt-4-turbo",
        instructions="""You are a fantasy football draft assistant.
        You know about NFL players, positions, and basic strategy.
        Remember what the user tells you about their league and picks.""",
        tools=[]  # No tools yet - just conversation
    )
)
```

**Deliverables**:
- [ ] Any-Agent installed and working
- [ ] Basic agent responding to fantasy questions
- [ ] Simple conversation test working

### Day 2: Add Static Data & Context
**Goal**: Give the agent knowledge about top players and maintain conversation state

```python
# Hardcoded top 50 players with simple stats
TOP_PLAYERS = {
    "Christian McCaffrey": {"pos": "RB", "adp": 1.2, "tier": 1},
    "CeeDee Lamb": {"pos": "WR", "adp": 2.5, "tier": 1},
    "Tyreek Hill": {"pos": "WR", "adp": 3.1, "tier": 1},
    # ... top 50 players
}

# Simple mock tool
def get_player_info(player_name: str) -> dict:
    return TOP_PLAYERS.get(player_name, {})
```

**Deliverables**:
- [ ] Static player data (top 50-100 players)
- [ ] Agent can access player information
- [ ] Multi-turn memory working (remembers user's picks)

### Day 3: Create Demo Scenarios
**Goal**: Build 4 specific conversation scenarios that showcase multi-turn capabilities

```python
scenarios = {
    "scenario_1": {
        "name": "The Opening Pick",
        "setup": "User has 5th pick, top 4 RBs are gone",
        "turns": 3,
        "showcases": "Strategy adaptation"
    },
    "scenario_2": {
        "name": "The Position Run",
        "setup": "Round 3, all QBs being drafted",
        "turns": 4,
        "showcases": "Patience and value finding"
    },
    "scenario_3": {
        "name": "The Sleeper Question",
        "setup": "Round 10, looking for upside",
        "turns": 3,
        "showcases": "Deep knowledge + context"
    },
    "scenario_4": {
        "name": "The Stack Builder",
        "setup": "Has Mahomes, wants receivers",
        "turns": 3,
        "showcases": "Correlation strategy"
    }
}
```

**Deliverables**:
- [ ] 4 scripted scenarios with expected flows
- [ ] Each scenario demonstrates different agent capabilities
- [ ] Clean conversation transcripts for each

### Day 4: Visual Demo Components
**Goal**: Create simple visuals for LinkedIn demo

```python
def create_player_card(player_name: str) -> str:
    """Generate ASCII or simple HTML player card"""
    player = TOP_PLAYERS[player_name]
    return f"""
    ╔═══════════════════════╗
    ║ {player_name:<19} ║
    ║ Position: {player['pos']:<12} ║
    ║ ADP: {player['adp']:<16} ║
    ║ Tier: {player['tier']:<15} ║
    ╚═══════════════════════╝
    """

def create_draft_board_snapshot(picks: list) -> str:
    """Simple visual draft board"""
    # Basic 12-team board showing first 3 rounds
```

**Deliverables**:
- [ ] Player card visualizer
- [ ] Simple draft board display
- [ ] Decision comparison visuals
- [ ] Results summary generator

### Day 5: Demo Recording & Optimization
**Goal**: Create the actual LinkedIn demo content

**Demo Script Structure**:
```
1. Hook (5s): "Watch AI navigate a tough draft decision"
2. Scenario 1 (15s): Show multi-turn conversation
3. Scenario 2 (15s): Show context retention
4. Results (10s): "AI's pick outscored consensus by 23%"
5. Tech (5s): "Built with Any-Agent in <100 lines"
```

**Deliverables**:
- [ ] Record all scenarios
- [ ] Create visual assets
- [ ] Write LinkedIn post copy
- [ ] Prepare code snippets

### Day 6: Polish & Edge Cases
**Goal**: Make it bulletproof for demo

**Focus Areas**:
- Clean up conversation flows
- Handle basic edge cases
- Optimize response time
- Add error handling
- Create setup instructions

**Deliverables**:
- [ ] GitHub repo ready
- [ ] README with clear instructions
- [ ] 3-5 example conversations
- [ ] "Try it yourself" guide

### Day 7: Launch Prep
**Goal**: Final testing and launch materials

- [ ] Final demo video (60 seconds)
- [ ] LinkedIn carousel (5-6 slides)
- [ ] Blog post draft
- [ ] Share in relevant communities

## Simplified Code Structure

```
fantasy-draft-agent/
├── agent.py           # Core Any-Agent setup
├── data.py           # Static player data
├── scenarios.py      # Demo scenarios
├── visualizer.py     # Simple visualizations
├── demo.py          # Run demonstrations
└── README.md        # Setup and usage
```

### Core Agent (agent.py)
```python
from any_agent import AnyAgent, AgentConfig
from data import TOP_PLAYERS

class FantasyDraftAgent:
    def __init__(self):
        self.agent = AnyAgent.create(
            "tinyagent",
            AgentConfig(
                model_id="gpt-4-turbo",
                instructions=self.load_instructions(),
                tools=[]  # Keep it simple
            )
        )
        self.draft_state = {
            "my_picks": [],
            "all_picks": [],
            "round": 1
        }
    
    def run_scenario(self, scenario_id: str):
        # Run pre-defined scenario
        pass
```

### Data Structure (data.py)
```python
# Just hardcode top players - no API needed
TOP_PLAYERS = {
    # Top 10 RBs
    "Christian McCaffrey": {"pos": "RB", "adp": 1.2, "ppg_2023": 22.1},
    "Austin Ekeler": {"pos": "RB", "adp": 4.5, "ppg_2023": 18.7},
    
    # Top 10 WRs  
    "Tyreek Hill": {"pos": "WR", "adp": 3.1, "ppg_2023": 20.2},
    "CeeDee Lamb": {"pos": "WR", "adp": 2.5, "ppg_2023": 19.8},
    
    # Top 5 QBs
    "Josh Allen": {"pos": "QB", "adp": 24.3, "ppg_2023": 24.6},
    
    # Top 3 TEs
    "Travis Kelce": {"pos": "TE", "adp": 12.4, "ppg_2023": 16.4},
}
```

## What Makes This MVP Compelling

### 1. **Focused Scenarios**
Instead of building everything, we create 4 perfect demonstrations of multi-turn capability

### 2. **No External Dependencies**
- No API keys needed
- No real-time data
- Just Any-Agent + hardcoded knowledge

### 3. **Clear Value Proposition**
Each scenario shows a specific benefit:
- Scenario 1: Adapts to draft flow
- Scenario 2: Maintains strategy across turns
- Scenario 3: Remembers user preferences
- Scenario 4: Builds on previous picks

### 4. **LinkedIn-Optimized**
- Quick, visual demos
- Clear before/after comparisons
- Relatable decisions every fantasy player faces

## Success Metrics

- [ ] 4 working scenarios with 3-4 turns each
- [ ] Clean conversation flows showing context retention
- [ ] 60-second demo video
- [ ] <100 lines of core code
- [ ] Anyone can run it in 5 minutes

## Post-MVP Expansion

After the successful demo, we can add:
- Week 2: Real player data integration
- Week 3: Full draft simulation
- Week 4: Live draft support
- Month 2: Trade analyzer, waiver wire assistant

This MVP focuses on demonstrating Any-Agent's multi-turn capabilities with minimal complexity while creating compelling content for LinkedIn. The key is showing clear value through conversation context, not building a complete fantasy platform.