"""
Constants for the Fantasy Draft Multi-Agent implementation.
"""

# Timing constants (in seconds)
TYPING_DELAY_SECONDS = 0.5
MESSAGE_DELAY_SECONDS = 1.0

# Comment configuration
MAX_COMMENTS_PER_PICK = 1  # Reduced for more concise draft flow

# Natural rivalry pairs for prioritizing comments
RIVAL_PAIRS = {
    1: 3,      # Zero RB vs Robust RB - natural enemies!
    3: 1,      # Robust RB vs Zero RB
    5: [2, 6], # Upside Hunter vs BPA agents
    2: 5,      # BPA vs Upside Hunter
    6: 5,      # BPA vs Upside Hunter
} 