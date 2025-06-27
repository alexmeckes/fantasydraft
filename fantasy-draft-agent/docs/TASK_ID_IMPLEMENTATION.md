# Task ID Implementation Guide

## Overview

We've enhanced the A2A implementation in `app_enhanced.py` to use Task IDs for maintaining conversation context across multiple agent interactions. This enables:

- 🧠 **Memory**: Agents remember previous picks, comments, and trash talk
- 🎭 **Rivalries**: Agents build ongoing feuds based on past interactions
- 💬 **Contextual Responses**: Comments reference specific previous events
- 📈 **Escalation**: Trash talk intensifies based on history

## Implementation Details

### 1. Task ID Storage

```python
class A2AAgentManager:
    def __init__(self):
        # ... existing code ...
        self.task_ids = {}  # Track task IDs for multi-turn conversations
        self.conversation_history = {}  # Store key moments for reference
```

### 2. Using Task IDs in Requests

```python
async def get_pick(self, team_num: int, available_players: List[str], 
                  previous_picks: List[str], round_num: int = 1):
    # Use existing task_id if available
    task_id = self.task_ids.get(team_num)
    result = await self.agent_tools[team_num](prompt, task_id=task_id)
    
    # Store task_id from response
    if isinstance(result, dict) and 'task_id' in result:
        self.task_ids[team_num] = result['task_id']
```

### 3. Context Building

The implementation adds context from previous interactions:

```python
# Add context from previous interactions
context = ""
if team_num in self.conversation_history:
    recent_history = self.conversation_history[team_num][-3:]  # Last 3 interactions
    if recent_history:
        context = "\nRecent history:\n" + "\n".join(recent_history) + "\n"
```

### 4. History Tracking

Important moments are stored for future reference:

```python
# Store important moments in history
if output.trash_talk:
    if team_num not in self.conversation_history:
        self.conversation_history[team_num] = []
    self.conversation_history[team_num].append(
        f"Round {round_num}: Picked {output.player_name}, said '{output.trash_talk}'"
    )
```

## Benefits

### Before Task IDs
- **Team 1**: "I'm taking Justin Jefferson! WRs win championships!"
- **Team 3**: "RBs are more important than WRs."
- *(No memory of previous interaction)*

### After Task IDs
- **Team 1**: "I'm taking Justin Jefferson! WRs win championships!"
- **Team 3**: "Another WR? Typical Zero RB nonsense. Your team will collapse by week 4."
- **Team 1** *(Round 2)*: "CeeDee Lamb! How's that McCaffrey pick looking now that I have two elite WRs?"
- **Team 3**: "Still better than your WR-heavy team that can't run the ball!"

## Usage

### Running the Enhanced App

```bash
cd fantasy-draft-agent
source venv/bin/activate
python apps/app_enhanced.py
```

Then toggle to "Real A2A Mode" in the UI to see contextual interactions.

### Testing Task IDs

Run the demo script to see Task IDs in action:

```bash
python demos/test_taskid_demo.py
```

## Technical Details

### Task ID Flow

1. **First Interaction**: No task_id sent, agent creates new conversation
2. **Response**: Contains task_id in response metadata
3. **Storage**: Task ID stored in `self.task_ids[team_num]`
4. **Subsequent Calls**: task_id included to continue conversation
5. **Agent Memory**: Agent maintains full conversation history

### Conversation History Structure

```python
self.conversation_history = {
    1: [  # Team 1
        "Round 1: Picked Justin Jefferson, said 'Zero RB is the way!'",
        "Round 1: Commented to Team 3 about McCaffrey: 'Enjoy the injury report!'",
        "Round 2: Team 3 said: 'Your WRs can't block'"
    ],
    3: [  # Team 3
        "Round 1: Picked McCaffrey, said 'RBs win championships'",
        "Round 1: Team 1 said: 'Enjoy the injury report!'",
        "Round 2: Commented to Team 1: 'Your WRs can't block'"
    ]
}
```

## Future Enhancements

1. **Persistent Storage**: Save task IDs and history between sessions
2. **Advanced Context**: Include draft trends and team composition
3. **Learning**: Agents adapt strategies based on opponent patterns
4. **Alliances**: Agents team up against common rivals
5. **Memory Limits**: Implement sliding window for very long drafts

## Troubleshooting

### Task IDs Not Working?
- Ensure agents are properly served and responding
- Check that task_id is extracted from responses
- Verify the a2a_tool is configured correctly

### No Contextual Responses?
- Confirm conversation_history is being populated
- Check that context is included in prompts
- Ensure agents have memory-aware instructions

## Conclusion

Task IDs transform the draft from isolated interactions into an evolving narrative with:
- Persistent rivalries
- Escalating trash talk
- Strategic mind games
- Memorable moments

This creates a more engaging and realistic draft experience! 