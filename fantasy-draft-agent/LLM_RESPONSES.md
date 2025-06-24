# LLM-Powered Dynamic Responses

## Overview

The Fantasy Draft Multi-Agent system now features **fully dynamic, LLM-powered responses** for all agent interactions. Instead of using canned responses, each agent generates unique, contextual commentary based on:

- Their specific draft strategy
- Current draft situation
- Previous picks and conversations
- Other teams' strategies and picks

## Key Features

### 1. Dynamic Pick Reasoning
Each agent explains their picks using the LLM, considering:
- Their strategy (Zero RB, BPA, Robust RB, Upside Hunter)
- Round number and draft position
- Previous picks made
- Available players

Example:
```python
# Instead of: "Sticking to my Zero RB build!"
# Now generates: "With Jefferson already on board, pairing him with Chase gives me 
# an elite WR duo that'll carry my team while others fight over injury-prone RBs!"
```

### 2. Contextual Commentary
Agents comment on other teams' picks based on:
- The specific player selected
- How it relates to their own strategy
- The current state of the draft

Example:
```python
# Zero RB agent seeing a RB picked early might say:
# "McCaffrey's elite, but I'll take the WR depth while everyone 
# chases last year's RB1 who's played 17 games once in five years."
```

### 3. Conversation Memory
Agents remember previous interactions and reference them:
- Stores recent conversation history
- References past comments when responding
- Builds ongoing draft narrative

### 4. Strategic Advisor
The user's advisor provides LLM-generated advice considering:
- User's current roster construction
- What other teams are doing
- Position scarcity
- Best available value

## Implementation Details

### Base Agent Class
```python
def comment_on_pick(self, team: str, player: str, player_info: Dict) -> Optional[str]:
    """Generate commentary using LLM with full context."""
    context = f"""You are {self.team_name}, following {self.strategy}.
    Your picks: {self.picks}
    {team} just picked {player} ({player_info['pos']})..."""
    
    return self.agent.run(context).strip()
```

### Memory System
```python
def respond_to_comment(self, commenter: str, comment: str) -> Optional[str]:
    """Respond using conversation history."""
    recent_memory = self.conversation_memory[-5:]
    context = f"""Previous conversation: {recent_memory}
    {commenter} said: "{comment}"
    Respond naturally..."""
    
    return self.agent.run(context).strip()
```

## Benefits

1. **Unique Every Time**: No two drafts have the same commentary
2. **Contextually Aware**: Responses consider the full draft situation
3. **Strategy-Specific**: Each agent stays true to their draft philosophy
4. **Natural Banter**: Creates realistic draft room atmosphere
5. **Adaptive**: Agents adjust commentary based on how draft unfolds

## Example Output

```
📙 Robust RB on WR pick: "While you're collecting receivers, I'm cornering 
the RB market. Good luck starting WRs in your RB slots come bye weeks!"

📘 Zero RB responds: "That's exactly why I'm avoiding the RB injury carousel. 
My WR studs will be playing all 17 games while your 'workhorses' miss half the season!"
```

## Testing

Run the test script to see dynamic responses in action:
```bash
python test_llm_responses.py
```

This demonstrates how each agent generates unique, contextual responses rather than repeating canned phrases. 