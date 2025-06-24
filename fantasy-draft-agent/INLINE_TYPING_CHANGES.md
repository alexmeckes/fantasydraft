# Inline Typing Changes

## Summary
Replaced separate typing indicator messages with inline "..." that transforms into the actual message.

## What Changed

### Before:
```
💭 Team 1 is typing...
📘🤓 Team 1: "Zero RB is the way!"
```
Two separate messages cluttering the chat.

### After:
```
📘🤓 Team 1: ...
(0.5s delay)
📘🤓 Team 1: "Zero RB is the way!"
```
The "..." appears first, then is replaced by the actual message.

## Implementation

1. **app.py Changes**:
   - Skip typing indicator messages entirely (`continue` if `agent.startswith("typing_")`)
   - Show agent message with "..." first
   - After 0.5s delay, replace "..." with actual message
   - Keeps the human typing feel without extra clutter

2. **No changes needed in multiagent_draft.py**:
   - Still generates typing indicators (for backwards compatibility)
   - app.py handles them by skipping and showing inline instead

## Benefits
- **Less clutter**: No separate typing messages
- **Same human feel**: Still see agents "typing"
- **Cleaner flow**: Each pick has 3-6 messages instead of 5-10
- **Better readability**: Easier to follow the conversation

## Result
Combined with the 1-2 comment limit, the draft now flows much more naturally without overwhelming the user. 