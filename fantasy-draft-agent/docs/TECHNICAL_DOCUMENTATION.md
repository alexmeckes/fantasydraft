# Technical Documentation

## System Architecture

### Overview

The Fantasy Draft Multi-Agent Demo showcases a sophisticated multi-agent system where AI agents with distinct personalities compete in a mock fantasy football draft. The system supports two execution modes:

1. **Basic Multiagent Mode**: Single-process, shared memory, direct method calls
2. **A2A (Agent-to-Agent) Mode**: Distributed agents on HTTP servers, true isolation

### Core Components

```
fantasy-draft-agent/
├── apps/
│   ├── app.py                   # Main Gradio interface with A2A support
│   ├── multiagent_draft.py      # Core draft logic and agent management
│   └── multiagent_scenarios.py  # UI formatting and visualization
├── core/
│   ├── agent.py                 # Base agent classes and strategies
│   ├── constants.py             # Configuration constants
│   ├── data.py                  # Player data and rankings
│   ├── dynamic_a2a_manager.py   # Dynamic port allocation for A2A
│   └── a2a_helpers.py           # A2A communication utilities
```

## A2A Implementation

### Dynamic Port Allocation

The system uses dynamic port allocation to support multiple concurrent A2A sessions:

```python
class DynamicA2AAgentManager:
    PORT_RANGE = (5000, 9000)  # Available port range
    active_sessions = {}       # Track active sessions
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.allocated_ports = self._allocate_ports()
```

Each session gets 6 consecutive ports for the 6 agents, ensuring no conflicts between users.

### A2A Communication Protocol

Agents communicate using the any-agent framework's A2A protocol:

1. **Agent Registration**: Each agent starts an HTTP server
2. **Message Format**: Structured requests/responses with task_id for context
3. **Async Communication**: Non-blocking calls between agents

Example A2A interaction:
```python
# Agent makes a pick
result = await a2a_tool_async(
    f"http://localhost:{port}/make_pick",
    model=agent_config.model,
    task_id=task_id,  # Maintains conversation context
    params={
        "available_players": available,
        "round_number": round_num
    }
)
```

### Task ID and Context Management

The A2A framework uses `task_id` to maintain conversation continuity:

- Each draft session has a unique task_id
- Agents automatically maintain conversation history per task_id
- No manual conversation tracking needed in A2A mode
- Enables true stateless HTTP communication

## Multi-User Support

### Session-Based Architecture

The app uses Gradio's `gr.State` to maintain separate sessions:

```python
# Each user gets their own app instance
app_state = gr.State(None)

def run_draft(mode, app):
    if app is None:
        app = EnhancedFantasyDraftApp()
    # ... rest of logic
    return output, app  # Return updated state
```

### Concurrency Handling

- **Basic Mode**: Full multi-user support, each user has isolated state
- **A2A Mode**: Dynamic ports prevent conflicts between sessions
- **Resource Management**: Automatic cleanup when sessions end

### Limitations

- A2A mode requires available ports in the 5000-9000 range
- Each A2A session uses ~6 ports (one per agent)
- Maximum concurrent A2A sessions limited by port range

## Agent Architecture

### Base Agent Design

```python
class FantasyDraftAgent(TinyAgent):
    def __init__(self, team_num, team_name, strategy, personality):
        super().__init__(
            name=f"Team {team_num} - {team_name}",
            instructions=self._build_instructions(),
            model="gpt-4",
            temperature=0.7
        )
```

### Strategy Implementation

Each agent has a distinct drafting strategy:

1. **Zero RB**: Avoids RBs early, loads up on WRs
2. **Best Player Available (BPA)**: Pure value drafting
3. **Robust RB**: Prioritizes RBs in early rounds
4. **Upside Hunter**: Seeks high-risk, high-reward players

### Memory and Context

Agents maintain context through:
- Conversation history (automatic in any-agent)
- Draft state passed with each request
- Strategy-specific decision making

## Communication Flow

### Pick Phase
1. Commissioner announces current picker
2. Agent evaluates available players
3. Agent makes selection with reasoning
4. Commissioner confirms pick
5. Other agents may comment (limited by MAX_COMMENTS_PER_PICK)

### Comment System
- Rivals prioritized for comments
- Maximum 2-3 comments per pick (configurable)
- Natural conversation flow with trash talk

## Performance Optimization

### Typing Effects
- Configurable delays for realistic feel
- TYPING_DELAY_SECONDS: Time showing "..."
- MESSAGE_DELAY_SECONDS: Pause between messages

### Parallel Processing
- A2A agents process independently
- Async communication prevents blocking
- Dynamic timeout handling (30s default)

### Resource Management
- Automatic port cleanup on session end
- Graceful fallback from A2A to simulation
- Memory-efficient state management

## Error Handling

### A2A Failures
- Automatic fallback to simulation mode
- Clear error messages in UI
- Session cleanup on errors

### Port Allocation
- Retry logic for port binding
- Session tracking prevents conflicts
- Cleanup of abandoned sessions

## Security Considerations

- API keys never exposed to frontend
- Each session isolated from others
- Port range restrictions for A2A
- No direct file system access from agents

## Future Enhancements

Potential improvements:
- WebSocket support for real-time updates
- Database persistence for draft history
- Custom model support beyond GPT-4
- Extended player database
- League customization options 