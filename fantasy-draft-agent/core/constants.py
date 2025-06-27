"""
Constants for the Fantasy Draft A2A implementation.
"""

# Timing constants (in seconds)
TYPING_DELAY_SECONDS = 0.5
MESSAGE_DELAY_SECONDS = 1.0
AGENT_START_DELAY = 5.0  # Increased from 3.0 to give agents more time to fully initialize
AGENT_STARTUP_WAIT = 1.0  # Increased from 0.5 to ensure each agent is ready
DEFAULT_TIMEOUT = 30.0

# Comment configuration
MAX_COMMENTS_PER_PICK = 2

# Natural rivalry pairs for prioritizing comments
RIVAL_PAIRS = {
    1: 3,      # Zero RB vs Robust RB - natural enemies!
    3: 1,      # Robust RB vs Zero RB
    5: [2, 6], # Upside Hunter vs BPA agents
    2: 5,      # BPA vs Upside Hunter
    6: 5,      # BPA vs Upside Hunter
}

# A2A Agent configurations
AGENT_CONFIGS = [
    {
        "team_name": "Team 1",
        "team_num": 1,
        "strategy": "Zero RB",
        "port": 5001,
        "philosophy": "RBs are INJURY MAGNETS! 🏥 WRs are the future! I'm building an AIR RAID OFFENSE that will DESTROY your pathetic ground game! 💨✈️",
        "emoji_style": ["✈️", "💨", "🏥", "🎯"],
    },
    {
        "team_name": "Team 2",
        "team_num": 2,
        "strategy": "BPA",
        "port": 5002,
        "philosophy": "I am the VALUE VULTURE! 🦅 I feast on your emotional reaches while I build a CHAMPIONSHIP ROSTER with pure analytics! 📊📈",
        "emoji_style": ["🦅", "📊", "📈", "💰"],
    },
    {
        "team_name": "Team 3",
        "team_num": 3,
        "strategy": "Robust RB",
        "port": 5003,
        "philosophy": "GROUND AND POUND, BABY! 💪 Your fancy WRs will be watching from the sidelines while my RBs BULLDOZE their way to victory! 🚜💥",
        "emoji_style": ["💪", "🚜", "💥", "🏃"],
    },
    {
        "team_name": "Team 5",
        "team_num": 5,
        "strategy": "Upside Hunter",
        "port": 5005,
        "philosophy": "BOOM OR BUST! 🎰🚀 Safe picks are for COWARDS! I'm swinging for the fences while you play it safe like a SCARED LITTLE MOUSE! 🐭💣",
        "emoji_style": ["🎰", "🚀", "💣", "⚡"],
    },
    {
        "team_name": "Team 6",
        "team_num": 6,
        "strategy": "BPA",
        "port": 5006,
        "philosophy": "Another spreadsheet warrior here to EXPLOIT your terrible decisions! 🤓💻 My algorithm laughs at your 'gut feelings'! 🤖📉",
        "emoji_style": ["🤓", "💻", "🤖", "📉"],
    },
] 