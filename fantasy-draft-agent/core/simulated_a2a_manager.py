"""
Simulated A2A Manager for environments where real A2A won't work (like HF Spaces).
Provides the same interface and experience as real A2A but uses in-process communication.
"""

import asyncio
import time
import random
from typing import Optional, List, Dict
from core.agent import FantasyDraftAgent
from core.constants import AGENT_CONFIGS, MAX_COMMENTS_PER_PICK


class SimulatedA2AResponse:
    """Simulated response that looks like an A2A response"""
    def __init__(self, player_name: str, reasoning: str, trash_talk: Optional[str] = None):
        self.type = "pick"
        self.player_name = player_name
        self.reasoning = reasoning
        self.trash_talk = trash_talk


class SimulatedA2AAgentManager:
    """
    Simulates A2A behavior without actual HTTP servers.
    Provides the same interface as DynamicA2AAgentManager but runs in-process.
    """
    
    def __init__(self, session_id: str = "sim", max_comments_per_pick=MAX_COMMENTS_PER_PICK, custom_prompts=None):
        self.session_id = session_id
        self.agents: Dict[int, FantasyDraftAgent] = {}
        self.running = False
        self.max_comments_per_pick = max_comments_per_pick
        self.custom_prompts = custom_prompts or {}
        # Simulate port allocation
        self.allocated_ports = [5001, 5002, 5003, 5004, 5005, 5006]
        
    async def start_agents(self):
        """Initialize agents (simulated startup)"""
        print(f"🚀 Starting simulated A2A agents for session {self.session_id}...")
        
        # Simulate startup delay
        await asyncio.sleep(0.5)
        
        # Create agents
        for team_num in [1, 2, 3, 5, 6]:
            config = AGENT_CONFIGS[team_num]
            self.agents[team_num] = FantasyDraftAgent(
                team_name=config["team_name"],
                strategy=config["strategy"],
                traits=config["traits"],
                rival_teams=config.get("rival_teams", [])
            )
        
        # Simulate server startup messages
        for team_num, port in zip([1, 2, 3, 5, 6], self.allocated_ports):
            await asyncio.sleep(0.1)
            print(f"✅ Agent {team_num} ready on simulated port {port}")
        
        self.running = True
        print(f"✅ All simulated A2A agents ready!")
        
    async def get_pick(self, team_num: int, available_players: List[str], 
                      previous_picks: List[str], round_num: int) -> Optional[SimulatedA2AResponse]:
        """Get pick from agent (simulated A2A call)"""
        if team_num not in self.agents:
            return None
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        agent = self.agents[team_num]
        
        # Get pick decision
        player = agent.make_pick(available_players, round_num)
        
        # Get reasoning
        reasoning = agent.explain_pick(player, round_num)
        
        # Maybe add trash talk
        trash_talk = None
        if random.random() < 0.3:  # 30% chance of trash talk
            responses = [
                f"Easy choice. Can't believe {player} was still available!",
                f"You all sleeping? {player} is a steal here!",
                f"Building a championship team, one pick at a time.",
                "This is how you draft, take notes everyone."
            ]
            trash_talk = random.choice(responses)
        
        return SimulatedA2AResponse(player, reasoning, trash_talk)
        
    async def get_comment(self, commenting_team: int, picking_team: int, 
                         player: str, round_num: int) -> Optional[str]:
        """Get comment from another agent (simulated A2A call)"""
        if commenting_team not in self.agents:
            return None
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        agent = self.agents[commenting_team]
        
        # Higher chance of comment if they're rivals
        if picking_team in agent.rival_teams:
            if random.random() < 0.8:  # 80% chance for rivals
                return agent.react_to_pick(
                    self.agents[picking_team].team_name,
                    player,
                    round_num
                )
        else:
            if random.random() < 0.3:  # 30% chance for non-rivals
                return agent.react_to_pick(
                    self.agents[picking_team].team_name,
                    player,
                    round_num
                )
        
        return None
        
    async def cleanup(self):
        """Cleanup simulated agents"""
        if self.running:
            print(f"🛑 Stopping simulated A2A agents for session {self.session_id}...")
            # Simulate shutdown
            await asyncio.sleep(0.2)
            self.agents.clear()
            self.running = False
            print(f"✅ Simulated A2A session {self.session_id} cleaned up")


# Provide same cleanup function interface
async def cleanup_session(manager: SimulatedA2AAgentManager):
    """Clean up a simulated A2A session"""
    if manager:
        await manager.cleanup() 