"""Mock a2a module for environments where a2a-sdk won't install properly"""

class AgentSkill:
    """Mock AgentSkill class for compatibility"""
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name  
        self.description = description


class PickResponse:
    """Mock response for pick operations"""
    def __init__(self, player_name: str, reasoning: str, trash_talk: str = None):
        self.type = "pick"
        self.player_name = player_name
        self.reasoning = reasoning
        self.trash_talk = trash_talk


# Create a mock module structure
import sys
import types

# Create mock a2a module
a2a_module = types.ModuleType('a2a')
sys.modules['a2a'] = a2a_module

# Create mock a2a.types submodule
a2a_types = types.ModuleType('a2a.types')
a2a_types.AgentSkill = AgentSkill
sys.modules['a2a.types'] = a2a_types
a2a_module.types = a2a_types

print("Mock a2a module installed into sys.modules") 