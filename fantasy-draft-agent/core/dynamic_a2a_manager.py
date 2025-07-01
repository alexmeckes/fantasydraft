"""
Dynamic A2A Manager with multi-user support through dynamic port allocation.
"""

import asyncio
import socket
import hashlib
import os
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
    RIVAL_PAIRS
)
from core.data import TOP_PLAYERS
from core.a2a_helpers import (
    parse_a2a_response,
    extract_task_id,
    format_available_players
)


# A2A Output model (same as in apps/app.py)
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
    
    def __init__(self, session_id: str = None, max_comments_per_pick=MAX_COMMENTS_PER_PICK, custom_prompts=None):
        self.session_id = session_id or self._generate_session_id()
        self.agents = {}
        self.agent_tools = {}
        self.serve_tasks = []
        self.is_running = False
        self.task_ids = {}
        self.max_comments_per_pick = max_comments_per_pick
        self.allocated_ports = []
        self.custom_prompts = custom_prompts or {}  # Store custom prompts
        
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import time
        import random
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:8]
    
    async def _find_available_ports(self, count: int = 5, start: int = 5000, end: int = 9000) -> List[int]:
        """Find available consecutive ports for agents."""
        async with self._port_lock:
            # On HF Spaces, try different port ranges
            port_ranges = [(8000, 9000), (5000, 6000), (7000, 8000), (9000, 10000)] if os.getenv("SPACE_ID") else [(start, end)]
            
            for range_start, range_end in port_ranges:
                # Try to find a consecutive range
                for base_port in range(range_start, range_end - count, 10):
                    ports = list(range(base_port, base_port + count))
                    
                    # Check if any port in range is already used
                    if any(p in self._used_ports for p in ports):
                        continue
                    
                    # Check if ports are actually available on the system
                    if await self._check_ports_available(ports):
                        # Reserve these ports
                        self._used_ports.update(ports)
                        self.allocated_ports = ports
                        print(f"✅ Found available ports in range {range_start}-{range_end}: {ports}")
                        return ports
            
            raise RuntimeError(f"Could not find {count} available consecutive ports in any range")
    
    async def _check_ports_available(self, ports: List[int]) -> bool:
        """Check if a list of ports is available on the system."""
        for port in ports:
            try:
                # Try to bind to the port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # On HF Spaces, try different bind addresses
                bind_addresses = ['localhost', '127.0.0.1', '0.0.0.0']
                bound = False
                
                for addr in bind_addresses:
                    try:
                        sock.bind((addr, port))
                        bound = True
                        break
                    except OSError:
                        continue
                
                sock.close()
                if not bound:
                    print(f"Port {port} not available on any interface")
                    return False
            except Exception as e:
                print(f"Error checking port {port}: {e}")
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
                    # Critical instructions that MUST be included
                    critical_instructions = """CRITICAL OUTPUT INSTRUCTIONS (DO NOT MODIFY):
For picks: You MUST return a JSON object with type="pick", player_name (from available list), reasoning, and optional trash_talk.
For comments: You MUST return a JSON object with type="comment", should_comment (true/false), and comment.

NEVER respond with plain text when asked to make a pick! Always use the structured format!

Example pick format:
{"type": "pick", "player_name": "CeeDee Lamb", "reasoning": "Elite WR with huge upside!", "trash_talk": "Your RBs will be crying!"}

Example comment format:
{"type": "comment", "should_comment": true, "comment": "Terrible pick! He's overrated!"}

---END CRITICAL INSTRUCTIONS---

"""
                    
                    # Use custom prompt if provided, otherwise use default
                    team_num = config['team_num']
                    if team_num in self.custom_prompts:
                        # Use custom prompt BUT always prepend critical instructions
                        personality_prompt = self.custom_prompts[team_num]
                        instructions = critical_instructions + personality_prompt
                    else:
                        # Use default prompt with critical instructions
                        default_personality = f"""You are {config['team_name']}, a fantasy football manager with {config['strategy']} strategy.

PERSONALITY & STRATEGY:
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

BE LOUD! BE PROUD! BE UNFORGETTABLE! 🎯"""
                        instructions = critical_instructions + default_personality
                    
                    # Create agent
                    agent = await AnyAgent.create_async(
                        "tinyagent",
                        AgentConfig(
                            name=f"team_{config['team_num']}_agent_{self.session_id}",
                            model_id="gpt-4o-mini",
                            description=f"{config['team_name']} - {config['strategy']} fantasy football team manager",
                            instructions=instructions,
                            output_type=A2AOutput,
                            # Force JSON output mode
                            agent_args={
                                "temperature": 0.8,
                                "response_format": {"type": "json_object"}
                            }
                        )
                    )
                    
                    self.agents[config['team_num']] = agent
                    
                    # Serve agent on dynamic port
                    # On HF Spaces, we might need to bind to 0.0.0.0
                    host = "0.0.0.0" if os.getenv("SPACE_ID") else "localhost"
                    
                    # Serving config for HF Spaces
                    serving_config = A2AServingConfig(
                        port=config['port'],
                        host=host,
                        task_timeout_minutes=30,
                    )
                    
                    serve_task = asyncio.create_task(
                        agent.serve_async(serving_config)
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
                    # On HF Spaces, we might need to use 127.0.0.1 for internal communication
                    host = "127.0.0.1" if os.getenv("SPACE_ID") else "localhost"
                    tool_url = f"http://{host}:{config['port']}"
                    # Use httpx timeout with longer settings for HF Spaces
                    import httpx
                    timeout_config = httpx.Timeout(
                        timeout=DEFAULT_TIMEOUT,
                        connect=30.0,  # Connection timeout
                        read=60.0,     # Read timeout
                        write=30.0,    # Write timeout
                        pool=30.0      # Pool timeout
                    )
                    self.agent_tools[team_num] = await a2a_tool_async(
                        tool_url,
                        http_kwargs={"timeout": timeout_config}
                    )
                    print(f"✅ Created A2A tool for Team {team_num} at {tool_url}")
                    
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
        
        # Simplified prompt for Team 5 to reduce processing time
        if team_num == 5:
            # Team 5 gets a shorter prompt to process faster
            prompt = f"""Round {round_num} - PICK NOW! 🚨

Available: {', '.join(available_str[:8])}
Your picks: {', '.join(previous_picks) if previous_picks else 'None'}

OUTPUT JSON:
{{"type": "pick", "player_name": "[PLAYER]", "reasoning": "UPSIDE! 🚀", "trash_talk": "BOOM!"}}

Pick the highest UPSIDE player! 💥"""
        else:
            # Normal prompt for other teams
            prompt = f"""🚨 IT'S YOUR TIME TO DOMINATE! 🚨 (Round {round_num})
        
Available top players: {', '.join(available_str)}
Your roster so far: {', '.join(previous_picks) if previous_picks else 'None yet'}

Make your pick and DESTROY the competition! 💪

IMPORTANT: You MUST output a valid A2AOutput JSON object with:
- type: "pick" (REQUIRED - this is a PICK, not a comment!)
- player_name: Choose ONE player from the available list above
- reasoning: Your strategy explanation with emojis
- trash_talk: Optional savage comment

Example format:
{{"type": "pick", "player_name": "CeeDee Lamb", "reasoning": "BOOM! 💥 Getting the most EXPLOSIVE WR!", "trash_talk": "Safe picks are for LOSERS!"}}

Remember your ENEMIES and CRUSH their dreams! Use emojis to emphasize your DOMINANCE! 🔥"""
        
        # Retry logic with reduced delays for HF Spaces
        max_retries = 2  # Reduced from 3
        retry_delay = 0.5  # Reduced from 2.0
        
        # For Team 5 specifically, reduce retries to avoid long delays
        if team_num == 5:
            max_retries = 1
        
        for attempt in range(max_retries):
            try:
                # Use task_id if we have one for this agent
                task_id = self.task_ids.get(team_num)
                result = await self.agent_tools[team_num](prompt, task_id=task_id)
                
                # Extract and store task_id
                new_task_id = extract_task_id(result)
                if new_task_id:
                    self.task_ids[team_num] = new_task_id
                
                # Parse the response
                output = parse_a2a_response(result, A2AOutput)
                if output:
                    print(f"✅ Team {team_num} pick: {output.player_name}")
                    return output
                else:
                    print(f"❌ Failed to parse response from Team {team_num}")
                    if isinstance(result, str):
                        print(f"   Raw response: {result[:200]}...")
                        # Try to extract player name from plain text as fallback
                        for player in available_players[:20]:
                            if player in str(result):
                                print(f"   Fallback: Found {player} in response, creating pick")
                                return A2AOutput(
                                    type="pick",
                                    player_name=player,
                                    reasoning="[Agent response was not in correct format]",
                                    trash_talk=None
                                )
                    return None
                    
            except Exception as e:
                error_name = type(e).__name__
                is_timeout = "timeout" in str(e).lower() or "readtimeout" in error_name.lower()
                
                if attempt < max_retries - 1 and is_timeout:
                    print(f"⚠️ Timeout for Team {team_num} (attempt {attempt + 1}/{max_retries}), retrying quickly...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # For Team 5, don't print full traceback to reduce log spam
                    if team_num == 5:
                        print(f"⚠️ Team {team_num} timeout - falling back to simulation")
                    else:
                        print(f"❌ Error getting pick from Team {team_num}: {error_name}")
                        if attempt == 0:  # Only print traceback on first failure
                            import traceback
                            traceback.print_exc()
                    return None
        
        return None
    
    async def get_comment(self, commenting_team: int, picking_team: int,
                         player_picked: str, round_num: int = 1) -> Optional[str]:
        """Get a comment from an A2A agent about a pick."""
        if commenting_team not in self.agent_tools:
            return None
        
        # Simple prompt - let task_id maintain conversation history  
        prompt = f"""🎯 Team {picking_team} just picked {player_picked}! 

This is your chance to DESTROY them with your superior knowledge! 💥

IMPORTANT: Output a valid A2AOutput JSON object with:
- type: "comment" (REQUIRED)
- should_comment: true or false (do you want to comment?)
- comment: Your DEVASTATING comment with emojis (if should_comment is true)

Example format:
{{"type": "comment", "should_comment": true, "comment": "TERRIBLE pick! 😂 {player_picked} is OVERRATED!"}}

If they're your RIVAL, make it PERSONAL! If they made a BAD pick, ROAST THEM! 🔥
Use emojis to make your point UNFORGETTABLE! 😈"""
        
        # Retry logic for network issues
        max_retries = 2  # Fewer retries for comments to avoid delays
        
        for attempt in range(max_retries):
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
                return None
                    
            except Exception as e:
                if attempt < max_retries - 1 and "timeout" in str(e).lower():
                    await asyncio.sleep(1.0)  # Short retry for comments
                    continue
                else:
                    print(f"Error getting comment from Team {commenting_team}: {e}")
                    return None
        
        return None


# Cleanup function for session end
async def cleanup_session(manager: DynamicA2AAgentManager):
    """Clean up resources when a session ends."""
    try:
        await manager.stop_agents()
    except Exception as e:
        print(f"Error during cleanup for session {manager.session_id}: {e}") 