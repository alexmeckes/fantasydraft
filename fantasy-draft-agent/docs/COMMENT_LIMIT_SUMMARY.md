# Comment Limiting Summary 💬

## What We Changed

Limited comments from **4+ per pick** to **2 per pick** with smart prioritization!

## Current Behavior

When an AI team makes a pick:
- **Maximum 2 agents** can comment (instead of all 4-5)
- **Natural rivals** get priority (Zero RB vs Robust RB)
- **More focused drama** without overwhelming spam

## Configuration

```python
# Default: 2 comments per pick
manager = A2AAgentManager()

# Custom: 1 comment per pick (minimal)
manager = A2AAgentManager(max_comments_per_pick=1)

# Custom: 3 comments per pick (chattier)
manager = A2AAgentManager(max_comments_per_pick=3)
```

## Example

**Before (Too Many):**
```
Team 1 picks Jefferson
Team 2: "Good value"
Team 3: "Should've taken RB"
Team 5: "Too safe"
Team 6: "Nice pick"
```

**After (Focused Drama):**
```
Team 1 picks Jefferson
Team 3: "🚜 ANOTHER Zero RB FOOL! My RBs will BULLDOZE your WRs! 💥"
Team 5: "🎰 BORING! Where's the CEILING? Enjoy 4th place! 💣"
```

## Benefits

✅ **Better pacing** - Not overwhelming
✅ **Focused rivalries** - Natural enemies clash
✅ **Enhanced drama** - Quality over quantity
✅ **Configurable** - Adjust to taste

The draft is now more engaging without being spammy! 🎯 