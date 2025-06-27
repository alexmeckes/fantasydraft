"""
Dynamic A2A Manager with multi-user support through dynamic port allocation.
"""

import asyncio
import socket
import hashlib
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from any_agent import AgentConfig, AnyAgent
from any_agent.serving import A2AServingConfig
from any_agent.tools import a2a_tool_async
from core.constants import (
    AGENT_CONFIGS,
    AGENT_START_DELAY,
    AGENT_STARTUP_WAIT,
    DEFAULT_TIMEOUT,
    MAX_COMMENTS_PER_PICK,
    RIVAL_PAIRS,
    TOP_PLAYERS
)
from core.a2a_helpers import (
    parse_a2a_response,
    extract_task_id,
    format_available_players
)


# A2A Output model (same as in app_enhanced.py)
class A2AOutput(BaseModel):
    """Combined output type for A2A agents."""
    type: str  # "pick" or "comment"
    # Pick fields
    player_name: Optional[str] = None
    reasoning: Optional[str] = None
    trash_talk: Optional[str] = None
    # Comment fields
    should_comment: Optional[bool] = None
    comment: Optional[str] = None


class DynamicA2AAgentManager:
    """A2A Agent Manager with dynamic port allocation for multi-user support."""
    
    # Class-level tracking of used ports
    _used_ports = set()
    _port_lock = asyncio.Lock()
    
    def __init__(self, session_id: str = None, max_comments_per_pick=MAX_COMMENTS_PER_PICK):
        self.session_id = session_id or self._generate_session_id()
        self.agents = {}
        self.agent_tools = {}
        self.serve_tasks = []
        self.is_running = False
        self.task_ids = {}
        self.max_comments_per_pick = max_comments_per_pick
        self.allocated_ports = []
        
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import time
        import random
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:8]
    
    async def _find_available_ports(self, count: int = 5, start: int = 5000, end: int = 9000) -> List[int]:
        """Find available consecutive ports for agents."""
        async with self._port_lock:
            # Try to find a consecutive range
            for base_port in range(start, end - count, 10):
                ports = list(range(base_port, base_port + count))
                
                # Check if any port in range is already used
                if any(p in self._used_ports for p in ports):
                    continue
                
                # Check if ports are actually available on the system
                if await self._check_ports_available(ports):
                    # Reserve these ports
                    self._used_ports.update(ports)
                    self.allocated_ports = ports
                    return ports
            
            raise RuntimeError(f"Could not find {count} available consecutive ports")
    
    async def _check_ports_available(self, ports: List[int]) -> bool:
        """Check if a list of ports is available on the system."""
        for port in ports:
            try:
                # Try to bind to the port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                sock.close()
            except OSError:
                return False
        return True
    
    async def _release_ports(self):
        """Release allocated ports when done."""
        async with self._port_lock:
            self._used_ports.difference_update(self.allocated_ports)
            self.allocated_ports = []
    
    def _create_dynamic_agent_configs(self, ports: List[int]) -> List[Dict]:
        """Create agent configs with dynamic ports."""
        configs = []
        # Only use teams 1, 2, 3, 5, 6 (skip team 4 which is the user)
        agent_teams = [1, 2, 3, 5, 6]
        
        for i, team_num in enumerate(agent_teams):
            # Find the original config for this team
            original_config = next(c for c in AGENT_CONFIGS if c['team_num'] == team_num)
            
            # Create a copy with the new port
            config = original_config.copy()
            config['port'] = ports[i]
            config['session_id'] = self.session_id  # Add session tracking
            configs.append(config)
            
        return configs
    
    async def start_agents(self):
        """Start all A2A agent servers with dynamic ports."""
        if self.is_running:
            return
            
        print(f"🚀 Starting A2A agents for session {self.session_id}...")
        
        try:
            # Find available ports
            ports = await self._find_available_ports()
            print(f"📍 Allocated ports: {ports}")
            
            # Create configs with dynamic ports
            agent_configs = self._create_dynamic_agent_configs(ports)
            
            # Create and serve all agents
            for config in agent_configs:
                try:
                    # Create agent (same as before)
                    agent = await AnyAgent.create_async(
                        "tinyagent",
                        AgentConfig(
                            name=f"team_{config['team_num']}_agent_{self.session_id}",
                            model_id="gpt-4o-mini",
                            description=f"{config['team_name']} - {config['strategy']} fantasy football team manager",
                            instructions=f"""You are {config['team_name']}, a fantasy football manager with {config['strategy']} strategy.

For picks: Return A2AOutput with type="pick", player_name, reasoning, and optional trash_talk.
For comments: Return A2AOutput with type="comment", should_comment (true/false), and comment.

PERSONALITY REQUIREMENTS:
- Use LOTS of emojis that match your strategy! 🔥
- Be EXTREMELY dramatic and over-the-top! 
- Take your philosophy to the EXTREME!
- MOCK other strategies viciously!
- Use CAPS for emphasis!
- Make BOLD predictions!
- Reference previous interactions with SPITE!
- Build INTENSE rivalries!
- Your responses should be ENTERTAINING and MEMORABLE!

Your EXTREME philosophy: {config['philosophy']}

BE LOUD! BE PROUD! BE UNFORGETTABLE! 🎯""",
                            output_type=A2AOutput,
                        )
                    )
                    
                    self.agents[config['team_num']] = agent
                    
                    # Serve agent on dynamic port
                    serve_task = asyncio.create_task(
                        agent.serve_async(
                            A2AServingConfig(
                                port=config['port'],
                                task_timeout_minutes=30,
                            )
                        )
                    )
                    self.serve_tasks.append(serve_task)
                    print(f"✅ Started {config['team_name']} on port {config['port']} (session: {self.session_id})")
                    
                    await asyncio.sleep(AGENT_STARTUP_WAIT)
                    
                except Exception as e:
                    print(f"❌ Failed to create/serve {config['team_name']}: {e}")
            
            # Wait for servers to start
            await asyncio.sleep(AGENT_START_DELAY)
            
            # Create tools for each agent
            for config in agent_configs:
                team_num = config['team_num']
                if team_num not in self.agents:
                    continue
                    
                try:
                    tool_url = f"http://localhost:{config['port']}"
                    self.agent_tools[team_num] = await a2a_tool_async(
                        tool_url,
                        http_kwargs={"timeout": DEFAULT_TIMEOUT}
                    )
                    print(f"✅ Created A2A tool for Team {team_num} on port {config['port']}")
                    
                except Exception as e:
                    print(f"❌ Failed to create tool for Team {team_num}: {e}")
            
            self.is_running = len(self.agent_tools) > 0
            if self.is_running:
                print(f"✅ A2A agents ready for session {self.session_id}! ({len(self.agent_tools)} agents active)")
            else:
                print(f"❌ Failed to start any A2A agents for session {self.session_id}")
                
        except Exception as e:
            print(f"❌ Failed to allocate ports or start agents: {e}")
            await self._release_ports()
            raise
    
    async def stop_agents(self):
        """Stop all A2A agent servers and release ports."""
        if not self.is_running:
            return
            
        print(f"🛑 Stopping A2A agents for session {self.session_id}...")
        
        # Cancel all serve tasks
        for task in self.serve_tasks:
            task.cancel()
        
        await asyncio.gather(*self.serve_tasks, return_exceptions=True)
        
        # Clear agent data
        self.agents.clear()
        self.agent_tools.clear()
        self.serve_tasks.clear()
        self.is_running = False
        
        # Release the ports
        await self._release_ports()
        
        print(f"✅ A2A agents stopped and ports released for session {self.session_id}")
    
    async def get_pick(self, team_num: int, available_players: List[str], 
                      previous_picks: List[str], round_num: int = 1) -> Optional[A2AOutput]:
        """Get a pick from an A2A agent."""
        if team_num not in self.agent_tools:
            return None
        
        # Build the prompt with essential info
        available_str = format_available_players(available_players, TOP_PLAYERS)
        
        # Simple prompt - let task_id maintain conversation history
        prompt = f"""🚨 IT'S YOUR TIME TO DOMINATE! 🚨 (Round {round_num})
        
Available top players: {', '.join(available_str)}
Your roster so far: {', '.join(previous_picks) if previous_picks else 'None yet'}

Make your pick and DESTROY the competition! 💪
Output an A2AOutput with type="pick", player_name, reasoning (with emojis!), and SAVAGE trash_talk!
Remember your ENEMIES and CRUSH their dreams! Use emojis to emphasize your DOMINANCE! 🔥"""
        
        try:
            # Use task_id if we have one for this agent
            task_id = self.task_ids.get(team_num)
            result = await self.agent_tools[team_num](prompt, task_id=task_id)
            
            # Extract and store task_id
            task_id = extract_task_id(result)
            if task_id:
                self.task_ids[team_num] = task_id
            
            # Parse the response
            output = parse_a2a_response(result, A2AOutput)
            return output
                
        except Exception as e:
            print(f"Error getting pick from Team {team_num}: {e}")
            return None
    
    async def get_comment(self, commenting_team: int, picking_team: int,
                         player_picked: str, round_num: int = 1) -> Optional[str]:
        """Get a comment from an A2A agent about a pick."""
        if commenting_team not in self.agent_tools:
            return None
        
        # Simple prompt - let task_id maintain conversation history  
        prompt = f"""🎯 Team {picking_team} just picked {player_picked}! 

This is your chance to DESTROY them with your superior knowledge! 💥
Should you UNLEASH your wisdom? Output an A2AOutput with type="comment", should_comment (true/false), and a DEVASTATING comment with emojis!
If they're your RIVAL, make it PERSONAL! If they made a BAD pick, ROAST THEM! 🔥
Use emojis to make your point UNFORGETTABLE! 😈"""
        
        try:
            # Use task_id for continuity
            task_id = self.task_ids.get(commenting_team)
            result = await self.agent_tools[commenting_team](prompt, task_id=task_id)
            
            # Extract and store task_id
            task_id = extract_task_id(result)
            if task_id:
                self.task_ids[commenting_team] = task_id
            
            # Parse the response
            output = parse_a2a_response(result, A2AOutput)
            
            if output and hasattr(output, 'should_comment') and output.should_comment and output.comment:
                return output.comment
        except Exception as e:
            print(f"Error getting comment from Team {commenting_team}: {e}")
        
        return None


# Cleanup function for session end
async def cleanup_session(manager: DynamicA2AAgentManager):
    """Clean up resources when a session ends."""
    try:
        await manager.stop_agents()
    except Exception as e:
        print(f"Error during cleanup for session {manager.session_id}: {e}") 