# Implementing Dynamic A2A for Multi-User Support

## Quick Integration Guide

To enable multi-user A2A support in `app_enhanced.py`:

### 1. Import the Dynamic Manager
```python
from core.dynamic_a2a_manager import DynamicA2AAgentManager, cleanup_session
```

### 2. Update EnhancedFantasyDraftApp
```python
class EnhancedFantasyDraftApp:
    def __init__(self):
        self.current_draft = None
        self.draft_output = ""
        # Use dynamic manager instead
        self.a2a_manager = None  # Will be created with session ID
        self.use_real_a2a = False
        self.a2a_status = "Not initialized"
        self.session_id = None
    
    async def toggle_a2a_mode(self, use_a2a: bool):
        """Toggle between simulated and real A2A."""
        self.use_real_a2a = use_a2a
        
        if use_a2a:
            # Generate unique session ID if needed
            if not self.session_id:
                import uuid
                self.session_id = str(uuid.uuid4())[:8]
            
            # Create new dynamic manager for this session
            self.a2a_manager = DynamicA2AAgentManager(self.session_id)
            
            try:
                await self.a2a_manager.start_agents()
                self.a2a_status = f"✅ Real A2A Mode Active (Session: {self.session_id})"
            except RuntimeError as e:
                self.a2a_status = f"❌ Failed to start A2A: {str(e)}"
                self.use_real_a2a = False
        else:
            if self.a2a_manager:
                await cleanup_session(self.a2a_manager)
                self.a2a_manager = None
            self.a2a_status = "✅ Simulated Mode Active"
        
        return self.a2a_status
```

### 3. Add Cleanup on Session End
```python
# In create_gradio_interface(), add cleanup handling
def create_gradio_interface():
    # ... existing code ...
    
    # Add session cleanup
    async def cleanup_on_unload(app):
        """Clean up resources when user leaves."""
        if app and app.a2a_manager:
            await cleanup_session(app.a2a_manager)
    
    # Register cleanup (Gradio 4.x)
    demo.unload(cleanup_on_unload, inputs=[app_state])
```

### 4. Update UI to Show Port Info
```python
mode_info = gr.Markdown(
    """
    **Simulated**: Fast, single-process execution (✅ Multi-user safe)
    **Real A2A**: Distributed agents with dynamic ports (✅ Multi-user safe with port allocation)
    
    *Each A2A session gets unique ports in the 5000-9000 range.*
    """
)
```

## Benefits

1. **True Multi-User Support**: Each user gets agents on different ports
2. **Automatic Port Management**: Finds available ports automatically
3. **Session Isolation**: Each session has a unique ID
4. **Resource Cleanup**: Ports are released when sessions end
5. **Fallback Handling**: Falls back to simulated if ports unavailable

## Limitations

- **Port Range**: Limited to ports 5000-9000 (configurable)
- **Max Concurrent Sessions**: ~800 sessions (5 ports per session)
- **Hugging Face Spaces**: May have firewall restrictions on port ranges
- **Resource Usage**: Each session runs 5 agent servers

## Testing

```python
# Test concurrent sessions
async def test_concurrent_sessions():
    managers = []
    
    # Create 3 concurrent sessions
    for i in range(3):
        manager = DynamicA2AAgentManager(f"test_session_{i}")
        await manager.start_agents()
        managers.append(manager)
        print(f"Session {i} using ports: {manager.allocated_ports}")
    
    # Cleanup
    for manager in managers:
        await cleanup_session(manager)
```

## Production Considerations

For production deployment:

1. **Set Port Limits**: Configure min/max port range based on server
2. **Add Monitoring**: Track port usage and session counts
3. **Implement Timeouts**: Auto-cleanup inactive sessions
4. **Rate Limiting**: Limit A2A sessions per user/IP
5. **Health Checks**: Monitor agent server health

This approach provides the best balance of functionality and practicality for multi-user A2A support! 