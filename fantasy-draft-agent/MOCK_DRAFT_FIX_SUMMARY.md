# Mock Draft "User Picks Twice" Bug Fix

## The Issue
User was picking twice in Round 1:
- Once at position #2 (should be Team 2's pick)
- Once at position #4 (correct user position)

## Root Cause
In `multiagent_scenarios.py`, the code was checking:
```python
if waiting_for_user:
    # Wait for user input
```

But `waiting_for_user` contains:
- `None` when it's the user's turn
- Player name (string) when it's an AI's turn

So `if waiting_for_user:` was **backwards** - it would be:
- False (skip) when it's the user's turn (None)
- True (execute) when it's an AI's turn (player name)

## The Fix
Changed the check to:
```python
if waiting_for_user is None:
    # Wait for user input (None means it's the user's turn)
```

Now it correctly identifies when `simulate_draft_turn` returns `None` as the signal for user input.

## Result
- Team 2 now makes its own pick
- User only picks once per round at position 4
- Draft order follows proper 6-team snake draft pattern 