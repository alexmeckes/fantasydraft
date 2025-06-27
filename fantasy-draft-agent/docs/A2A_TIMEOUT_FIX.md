# A2A Timeout Issue and Fix

## Problem
When running the fantasy draft app with Real A2A mode, you may see errors like:
```
Error getting pick from Team 2: HTTP Error 503: Network communication error: 
httpcore.ReadTimeout
```

However, the draft continues because the app has a fallback mechanism.

## Root Causes
1. **Agent Response Time**: A2A agents using LLMs can take several seconds to respond
2. **Default Timeout**: The default HTTP timeout may be too short
3. **Complex Instructions**: Verbose agent instructions increase response time

## Solutions Implemented

### 1. Increased Timeout
Added 30-second timeout to A2A tool creation:
```python
self.agent_tools[team_num] = await a2a_tool_async(
    tool_url,
    http_kwargs={"timeout": 30.0}  # 30 second timeout
)
```

### 2. Server Health Checks
Added verification that agent servers are responding before creating tools:
```python
# Test that servers are responsive
response = await client.get(f"http://localhost:{port}/agent-card")
```

### 3. Simplified Instructions
Reduced agent instruction complexity for faster responses:
- Removed verbose explanations
- Made instructions more concise
- Kept personality but reduced processing time

### 4. Better Error Handling
- Clear error messages indicating timeout vs other errors
- UI notification when fallback to simulation occurs
- Graceful degradation maintains user experience

### 5. Startup Improvements
- Added delay between starting agents
- Increased initial wait time for servers to stabilize

## Testing Agent Responsiveness
Use the provided test script:
```bash
python test_a2a_agents.py
```

This will:
- Check if each agent server is running
- Test response times
- Identify which agents might timeout

## Expected Behavior
- Agents should respond within 5-10 seconds
- Timeout errors trigger automatic fallback to simulation
- User sees warning when fallback occurs
- Draft continues smoothly either way

## If Issues Persist
1. Check agent server logs for errors
2. Verify OPENAI_API_KEY is set
3. Try using a faster model (gpt-3.5-turbo)
4. Increase timeout further if needed
5. Ensure no firewall blocking localhost ports

## Architecture Note
The fallback mechanism ensures the draft always completes:
- **Real A2A Success**: Uses actual distributed agents
- **Real A2A Timeout**: Falls back to simulation for that pick
- **Mixed Mode**: Some picks may use A2A, others simulation

This hybrid approach provides the best user experience while demonstrating both architectures. 