# Multi-Agent Mock Draft Demo

This demo showcases any-agent's powerful **Agent-to-Agent (A2A)** communication capabilities through an interactive fantasy football mock draft.

## 🎯 Key Features Demonstrated

### 1. **Agent-to-Agent Communication**
- Agents directly address and respond to each other
- Natural conversation flow between AI agents
- Context-aware responses based on other agents' strategies

### 2. **Multi-Turn Memory**
- Agents remember previous conversations
- Reference earlier picks and statements
- Build strategies based on draft history

### 3. **Visual Clarity**
Each agent has distinct visual styling:
- 📘 **Team 1** (Blue) - Zero RB Strategy
- 📗 **Team 2** (Green) - Best Player Available
- 📙 **Team 3** (Orange) - Robust RB Strategy
- 📕 **Your Advisor** (Red) - Helps you make picks
- 📓 **Team 5** (Yellow) - Upside Hunter
- 📜 **Commissioner** (Gold) - Manages the draft

## 🏃 Running the Demo

### In the Gradio App
1. Launch the app: `python app.py`
2. Navigate to the "🤝 Multi-Agent Demos" tab
3. Select "Quick A2A Demo" from the dropdown
4. Click "▶️ Run Multi-Agent Demo"

### Example Output
```
📘 Team 1: I'm taking Justin Jefferson with the first pick. Zero RB all the way!
📙 Team 3 → Team 1: Leaving McCaffrey on the board? That's a mistake!
📘 Team 1 → Team 3: RBs get injured. I'll take my chances with elite WRs.
📗 Team 2: Interesting debate! I'll take whoever falls to me.
```

## 🧠 How It Works

### Agent Architecture
Each agent has:
- **Strategy**: Defined approach to drafting
- **Memory**: Conversation history with other agents
- **Decision Logic**: Strategy-specific pick selection
- **Communication Skills**: Ability to comment and respond

### A2A Communication Flow
1. Agent makes a pick
2. Other agents analyze and potentially comment
3. Original agent can respond to comments
4. All agents remember the exchange
5. Future decisions influenced by past conversations

### Memory Demonstration
The demo shows memory indicators:
```
💭 DRAFT MEMORY (Round 2)
• Team 1 committed to Zero RB strategy
• Team 3 prefers RB-heavy approach
• Teams are aware of each other's strategies
```

## 🔧 Technical Implementation

### Multi-Agent Setup
```python
agents = {
    1: ZeroRBAgent("Team 1"),
    2: BPAAgent("Team 2"), 
    3: RobustRBAgent("Team 3"),
    5: UpsideAgent("Team 5")
}
```

### A2A Message Format
```python
# Agent-to-Agent communication
message = {
    "speaker": "Team 3",
    "recipient": "Team 1", 
    "message": "Leaving McCaffrey on the board? That's a mistake!",
    "type": "comment"
}
```

### Visual Formatting
Each message is wrapped in a styled div with:
- Background color matching agent theme
- Border color for visual distinction
- Clear sender → recipient notation
- Proper spacing and padding

## 🎬 Demo Scenarios

### Quick A2A Demo
- Fast demonstration of agent communication
- Shows debate about first pick
- Highlights memory and strategy awareness
- ~30 seconds runtime

### Full Mock Draft (Coming Soon)
- Interactive 3-round draft
- User participates with AI advisor
- Real-time agent reactions
- Complete draft board visualization

## 💡 Key Takeaways

1. **Natural A2A Communication**: Agents communicate like real draft participants
2. **Strategic Awareness**: Each agent understands others' strategies
3. **Memory Persistence**: Past conversations influence future decisions
4. **Visual Clarity**: Easy to follow who's talking to whom
5. **Any-Agent Power**: Built with simple, clean agent definitions

This demonstrates how any-agent makes it easy to create sophisticated multi-agent systems with natural communication patterns! 