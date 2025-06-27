# Alternative Approaches to Multi-Turn Conversations

## Overview

While Task IDs are effective, there are several alternative approaches to implementing multi-turn conversations in your fantasy draft app. Each has different trade-offs in terms of complexity, performance, and capabilities.

## 1. Context Injection (Stateless Approach)

Instead of relying on server-side state, pass the full conversation history with each request.

### Implementation

```python
class ContextInjectionManager:
    def __init__(self):
        self.conversation_history = {}  # Local storage
    
    async def get_pick(self, team_num: int, available_players: List[str], 
                      previous_picks: List[str], round_num: int = 1):
        # Build full context from history
        context = self._build_full_context(team_num)
        
        prompt = f"""
CONVERSATION HISTORY:
{context}

CURRENT SITUATION:
Round {round_num}
Available: {', '.join(available_players[:10])}
Your picks: {', '.join(previous_picks)}

Make your pick with reasoning and trash talk.
"""
        
        # No task_id needed - full context in prompt
        result = await self.agent_tools[team_num](prompt)
        
        # Store this interaction
        self._store_interaction(team_num, round_num, result)
        
        return result
    
    def _build_full_context(self, team_num: int) -> str:
        """Build complete conversation history."""
        history = self.conversation_history.get(team_num, [])
        return "\n".join([
            f"[{item['timestamp']}] {item['type']}: {item['content']}"
            for item in history
        ])
```

### Pros
- No server-side state management
- Easy to debug (all context visible)
- Works with any LLM API

### Cons
- Token usage increases with conversation length
- Context window limitations
- Slower as conversations grow

## 2. Shared Memory Store (Redis/Database)

Use a centralized memory store that all agents can access.

### Implementation

```python
import redis
import json
from datetime import datetime

class SharedMemoryManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379)
        self.agent_tools = {}
        
    async def get_pick(self, team_num: int, available_players: List[str], 
                      previous_picks: List[str], round_num: int = 1):
        # Get shared memories
        memories = self._get_relevant_memories(team_num)
        
        prompt = f"""
SHARED MEMORIES:
{json.dumps(memories, indent=2)}

YOUR TURN: Round {round_num}
Available: {', '.join(available_players[:10])}

Make your pick remembering past interactions.
"""
        
        result = await self.agent_tools[team_num](prompt)
        
        # Store in shared memory
        self._store_memory({
            'team': team_num,
            'round': round_num,
            'action': 'pick',
            'player': result.player_name,
            'trash_talk': result.trash_talk,
            'timestamp': datetime.now().isoformat(),
            'rivals_mentioned': self._extract_rival_mentions(result.trash_talk)
        })
        
        return result
    
    def _get_relevant_memories(self, team_num: int, limit: int = 10):
        """Get memories relevant to this team."""
        # Get direct memories
        team_memories = self.redis_client.lrange(f'team:{team_num}:memories', 0, limit)
        
        # Get rivalry memories
        rivalry_memories = self.redis_client.lrange(f'rivalries:{team_num}', 0, 5)
        
        return {
            'my_history': [json.loads(m) for m in team_memories],
            'rivalries': [json.loads(m) for m in rivalry_memories]
        }
    
    def _store_memory(self, memory: dict):
        """Store memory in Redis with multiple indexes."""
        memory_json = json.dumps(memory)
        
        # Store by team
        self.redis_client.lpush(f'team:{memory["team"]}:memories', memory_json)
        
        # Store rivalries
        for rival in memory.get('rivals_mentioned', []):
            self.redis_client.lpush(f'rivalries:{rival}', memory_json)
        
        # Store global timeline
        self.redis_client.zadd('draft:timeline', 
                              {memory_json: datetime.now().timestamp()})
```

### Pros
- Agents can access each other's memories
- Persistent across sessions
- Enables complex queries and relationships
- Scalable

### Cons
- Requires infrastructure (Redis/DB)
- More complex setup
- Potential consistency issues

## 3. Event-Driven Architecture

Use events to maintain conversation flow without explicit state.

### Implementation

```python
from asyncio import Queue
from typing import Dict, Any

class EventDrivenDraftManager:
    def __init__(self):
        self.event_queue = Queue()
        self.event_handlers = {}
        self.agent_subscriptions = {}
        
    async def start(self):
        """Start event processing loop."""
        asyncio.create_task(self._process_events())
        
    async def _process_events(self):
        """Process events from the queue."""
        while True:
            event = await self.event_queue.get()
            
            # Notify subscribed agents
            for team_num in self.agent_subscriptions.get(event['type'], []):
                if team_num != event.get('source_team'):
                    await self._notify_agent(team_num, event)
    
    async def make_pick(self, team_num: int, available_players: List[str]):
        # Publish pick request event
        await self.publish_event({
            'type': 'pick_request',
            'team': team_num,
            'available': available_players,
            'timestamp': datetime.now().isoformat()
        })
        
        # Agent makes pick
        result = await self.agent_tools[team_num](
            f"Make your pick from: {', '.join(available_players[:10])}"
        )
        
        # Publish pick made event
        await self.publish_event({
            'type': 'pick_made',
            'source_team': team_num,
            'player': result.player_name,
            'trash_talk': result.trash_talk,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    async def publish_event(self, event: Dict[str, Any]):
        """Publish an event to the queue."""
        await self.event_queue.put(event)
    
    async def _notify_agent(self, team_num: int, event: Dict[str, Any]):
        """Notify an agent about an event."""
        if event['type'] == 'pick_made':
            # Agent can react to picks
            prompt = f"""
Event: Team {event['source_team']} picked {event['player']}
They said: "{event['trash_talk']}"

React if you want to comment.
"""
            
            response = await self.agent_tools[team_num](prompt)
            
            if response.should_comment:
                await self.publish_event({
                    'type': 'comment_made',
                    'source_team': team_num,
                    'target_team': event['source_team'],
                    'comment': response.comment,
                    'timestamp': datetime.now().isoformat()
                })
```

### Pros
- Natural for reactive behaviors
- Agents can subscribe to relevant events
- Decoupled architecture
- Easy to add new event types

### Cons
- More complex to debug
- Potential race conditions
- Requires event ordering logic

## 4. Session-Based Approach

Create explicit session objects that maintain state.

### Implementation

```python
from uuid import uuid4

class DraftSession:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid4())
        self.teams = {}
        self.interactions = []
        self.round = 1
        
    def add_interaction(self, interaction: dict):
        """Add interaction to session history."""
        interaction['session_id'] = self.session_id
        interaction['sequence'] = len(self.interactions)
        self.interactions.append(interaction)
        
    def get_team_context(self, team_num: int) -> dict:
        """Get all context for a team."""
        return {
            'session_id': self.session_id,
            'round': self.round,
            'my_picks': self.teams.get(team_num, {}).get('picks', []),
            'my_interactions': [i for i in self.interactions 
                               if i.get('team') == team_num],
            'recent_events': self.interactions[-5:]
        }

class SessionBasedManager:
    def __init__(self):
        self.sessions = {}
        self.agent_tools = {}
        
    def create_session(self) -> DraftSession:
        """Create a new draft session."""
        session = DraftSession()
        self.sessions[session.session_id] = session
        return session
    
    async def make_pick(self, session_id: str, team_num: int, 
                       available_players: List[str]):
        session = self.sessions[session_id]
        context = session.get_team_context(team_num)
        
        prompt = f"""
SESSION: {context['session_id']}
ROUND: {context['round']}
YOUR PREVIOUS PICKS: {', '.join(context['my_picks'])}
RECENT EVENTS:
{json.dumps(context['recent_events'], indent=2)}

Available players: {', '.join(available_players[:10])}
Make your pick!
"""
        
        result = await self.agent_tools[team_num](prompt)
        
        # Record in session
        session.add_interaction({
            'type': 'pick',
            'team': team_num,
            'player': result.player_name,
            'reasoning': result.reasoning,
            'trash_talk': result.trash_talk
        })
        
        return result
```

### Pros
- Clean separation of sessions
- Easy to save/restore drafts
- Good for multiple concurrent drafts
- Natural state management

### Cons
- Session management overhead
- Need to pass session_id around
- Memory usage for active sessions

## 5. Conversation Memory with Embeddings

Use semantic memory for more intelligent context retrieval.

### Implementation

```python
import numpy as np
from typing import List, Tuple

class SemanticMemoryManager:
    def __init__(self):
        self.memories = []
        self.embeddings = []
        self.embedding_model = None  # Initialize your embedding model
        
    async def add_memory(self, content: str, metadata: dict):
        """Add a memory with its embedding."""
        embedding = await self._get_embedding(content)
        
        self.memories.append({
            'content': content,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })
        self.embeddings.append(embedding)
    
    async def get_relevant_memories(self, query: str, k: int = 5) -> List[dict]:
        """Get k most relevant memories for a query."""
        query_embedding = await self._get_embedding(query)
        
        # Calculate similarities
        similarities = [
            np.dot(query_embedding, emb) / 
            (np.linalg.norm(query_embedding) * np.linalg.norm(emb))
            for emb in self.embeddings
        ]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        return [self.memories[i] for i in top_indices]
    
    async def make_contextual_pick(self, team_num: int, available_players: List[str]):
        # Query for relevant memories
        query = f"Team {team_num} picking strategy rivalry {' '.join(available_players[:5])}"
        relevant_memories = await self.get_relevant_memories(query)
        
        prompt = f"""
RELEVANT MEMORIES:
{json.dumps(relevant_memories, indent=2)}

CURRENT PICK:
Available: {', '.join(available_players[:10])}

Make your pick considering past interactions.
"""
        
        result = await self.agent_tools[team_num](prompt)
        
        # Store this interaction
        await self.add_memory(
            f"Team {team_num} picked {result.player_name}: {result.trash_talk}",
            {'team': team_num, 'type': 'pick', 'player': result.player_name}
        )
        
        return result
```

### Pros
- Intelligent memory retrieval
- Handles long conversations well
- Finds semantically similar interactions
- Natural language queries

### Cons
- Requires embedding infrastructure
- Computational overhead
- Complex to debug

## 6. Hybrid Approach (Recommended)

Combine multiple approaches for optimal results.

```python
class HybridMultiturnManager:
    def __init__(self):
        # Use task IDs for agent continuity
        self.task_ids = {}
        
        # Local context for quick access
        self.recent_history = {}
        
        # Shared memory for cross-agent awareness
        self.shared_memory = {}
        
        # Session management
        self.current_session = None
        
    async def make_pick(self, team_num: int, available_players: List[str]):
        # 1. Get recent local context (fast)
        recent = self.recent_history.get(team_num, [])[-3:]
        
        # 2. Get relevant shared memories (rivalries)
        rivalries = self._get_rivalry_context(team_num)
        
        # 3. Build prompt with both
        prompt = f"""
RECENT HISTORY: {recent}
RIVALRIES: {rivalries}
AVAILABLE: {', '.join(available_players[:10])}

Make your pick!
"""
        
        # 4. Use task_id for agent state continuity
        result = await self.agent_tools[team_num](
            prompt, 
            task_id=self.task_ids.get(team_num)
        )
        
        # 5. Update all stores
        self._update_all_stores(team_num, result)
        
        return result
```

## Recommendation

For your fantasy draft app, I recommend:

1. **Keep Task IDs** for agent-side state management
2. **Add Context Injection** for explicit memory control
3. **Consider Shared Memory** for rivalry tracking
4. **Use Sessions** for draft management

This gives you the best of all worlds:
- Agent continuity (Task IDs)
- Explicit control (Context)
- Cross-agent awareness (Shared Memory)
- Clean draft management (Sessions) 