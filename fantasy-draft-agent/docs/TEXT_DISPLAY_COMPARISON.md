# Text Display Comparison: Simulated vs A2A Mode

## Overview
Both modes use identical text display logic, but A2A mode is slower due to network overhead and sequential API calls.

## Display Timing (Both Modes)

### Constants
```python
TYPING_DELAY_SECONDS = 0.5    # Time showing "..."
MESSAGE_DELAY_SECONDS = 1.0   # Time after showing message
```

### Display Flow
1. Show "..." placeholder → Wait 0.5s
2. Replace with actual message → Wait 1.0s  
3. After all messages → Wait 0.5s

**Total time per message**: 1.5 seconds
**Additional delay after turn**: 0.5 seconds

## Performance Comparison

### Simulated Mode
```
simulate_draft_turn() → All messages instantly
↓
For each message:
  - Display "..." (0.5s)
  - Display message (1.0s)
```

**Time breakdown for typical turn (4 messages)**:
- Data generation: ~0ms (in-memory)
- Display time: 4 × 1.5s + 0.5s = 6.5 seconds

### A2A Mode
```
run_a2a_draft_turn() → Sequential API calls
↓
1. Get pick from agent → HTTP request
2. For each commenter → HTTP request (sequential)
↓
For each message:
  - Display "..." (0.5s)
  - Display message (1.0s)
```

**Time breakdown for typical turn (4 messages)**:
- Pick request: ~1-2 seconds (HTTP + AI generation)
- Comment requests: 2 × ~1-2 seconds (sequential)
- Display time: 4 × 1.5s + 0.5s = 6.5 seconds
- **Total**: ~10-12 seconds vs 6.5 seconds

## Key Performance Issues in A2A

### 1. Sequential Comment Collection
```python
for other_team in potential_commenters:
    if comment_count >= max_comments:
        break
    comment = await self.a2a_manager.get_comment(...)  # Sequential!
```

### 2. Network Overhead
- Each HTTP request adds latency
- Timeout set to 30 seconds (DEFAULT_TIMEOUT)
- No connection pooling

### 3. No Parallelization
Comments could be requested in parallel but are done sequentially.

## Optimization Opportunities

### 1. Parallel Comment Requests
```python
# Current (sequential)
for team in commenters:
    comment = await get_comment(team)

# Optimized (parallel)
comment_tasks = [get_comment(team) for team in commenters[:max_comments]]
comments = await asyncio.gather(*comment_tasks)
```

### 2. Reduce Display Delays for A2A
```python
# For A2A mode, could use shorter delays
if self.use_real_a2a:
    typing_delay = 0.2  # Faster since we already waited for network
    message_delay = 0.5
```

### 3. Pre-fetch Comments
Start fetching comments while displaying pick messages.

### 4. Connection Pooling
Reuse HTTP connections to reduce handshake overhead.

## Visual Experience Comparison

### Simulated Mode
- Smooth, consistent pacing
- 1.5s per message feels natural
- No unexpected delays

### A2A Mode  
- Initial delay before messages start
- Same display pacing once messages arrive
- Feels slower due to upfront wait

## Recommendations

1. **Keep current display timing** - It provides good UX
2. **Parallelize A2A comment requests** - Biggest improvement
3. **Add loading indicator** for A2A network calls
4. **Consider streaming** - Show messages as they arrive rather than batching

## Summary
The text display logic is identical between modes. A2A is slower because:
- Network requests add 3-6 seconds before display starts
- Comments are fetched sequentially, not in parallel
- Same 6.5s display time is added on top of network time

The perceived slowness is mainly from waiting for all messages to be collected before any display begins. 