"""
Lightweight A2A Manager for HF Spaces - Real distributed agents using HTTP only.
Works without grpcio dependencies by using httpx and FastAPI directly.
"""

import asyncio
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import multiprocessing
import time
import socket
from contextlib import closing
from core.agent import FantasyDraftAgent
from core.constants import AGENT_CONFIGS


# Pydantic models for API
class PickRequest(BaseModel):
    available_players: List[str]
    previous_picks: List[str]
    round_num: int


class PickResponse(BaseModel):
    type: str = "pick"
    player_name: str
    reasoning: str
    trash_talk: Optional[str] = None


class CommentRequest(BaseModel):
    picking_team: int
    player: str
    round_num: int


class CommentResponse(BaseModel):
    comment: Optional[str]


class LightweightA2AAgent:
    """Single agent server that runs in its own process"""
    
    def __init__(self, team_num: int, port: int):
        self.team_num = team_num
        self.port = port
        self.app = FastAPI()
        self.agent = None
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.on_event("startup")
        async def startup():
            config = AGENT_CONFIGS[self.team_num]
            self.agent = FantasyDraftAgent(
                team_name=config["team_name"],
                strategy=config["strategy"],
                traits=config["traits"],
                rival_teams=config.get("rival_teams", [])
            )
            print(f"✅ Agent {self.team_num} initialized on port {self.port}")
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "team": self.team_num}
        
        @self.app.post("/pick", response_model=PickResponse)
        async def make_pick(request: PickRequest):
            if not self.agent:
                raise HTTPException(status_code=500, detail="Agent not initialized")
            
            # Update agent's picks
            self.agent.picks = request.previous_picks.copy()
            
            # Make pick
            player = self.agent.make_pick(request.available_players, request.round_num)
            reasoning = self.agent.explain_pick(player, request.round_num)
            
            # Optional trash talk
            trash_talk = None
            import random
            if random.random() < 0.3:
                trash_talk = random.choice([
                    f"Can't believe {player} was still available!",
                    f"{player} is going to be huge this year!",
                    "Building a championship team here.",
                    "Y'all sleeping on my picks!"
                ])
            
            return PickResponse(
                player_name=player,
                reasoning=reasoning,
                trash_talk=trash_talk
            )
        
        @self.app.post("/comment", response_model=CommentResponse)
        async def make_comment(request: CommentRequest):
            if not self.agent:
                raise HTTPException(status_code=500, detail="Agent not initialized")
            
            # Higher chance of comment for rivals
            import random
            if request.picking_team in self.agent.rival_teams:
                if random.random() < 0.8:
                    comment = self.agent.react_to_pick(
                        f"Team {request.picking_team}",
                        request.player,
                        request.round_num
                    )
                    return CommentResponse(comment=comment)
            else:
                if random.random() < 0.3:
                    comment = self.agent.react_to_pick(
                        f"Team {request.picking_team}",
                        request.player,
                        request.round_num
                    )
                    return CommentResponse(comment=comment)
            
            return CommentResponse(comment=None)
    
    def run(self):
        """Run the agent server"""
        uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="error")


def _run_agent_server(team_num: int, port: int):
    """Function to run in separate process"""
    agent = LightweightA2AAgent(team_num, port)
    agent.run()


class LightweightA2AAgentManager:
    """
    Manages lightweight A2A agents using only HTTP (no grpcio).
    Each agent runs as a FastAPI server in a separate process.
    """
    
    def __init__(self, session_id: str = "lightweight"):
        self.session_id = session_id
        self.processes: Dict[int, multiprocessing.Process] = {}
        self.allocated_ports: List[int] = []
        self.base_port = 5001
        self.running = False
        self.max_comments_per_pick = 2
        self.client = None
    
    def _find_free_port(self, start_port: int) -> int:
        """Find a free port starting from start_port"""
        for port in range(start_port, start_port + 100):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                try:
                    sock.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"No free ports found starting from {start_port}")
    
    async def start_agents(self):
        """Start all agent servers"""
        print(f"🚀 Starting lightweight A2A agents for session {self.session_id}...")
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(timeout=10.0)
        
        # Allocate ports and start processes
        for team_num in [1, 2, 3, 5, 6]:
            port = self._find_free_port(self.base_port + team_num - 1)
            self.allocated_ports.append(port)
            
            # Start agent process
            process = multiprocessing.Process(
                target=_run_agent_server,
                args=(team_num, port)
            )
            process.start()
            self.processes[team_num] = process
            
            print(f"⏳ Starting agent {team_num} on port {port}...")
        
        # Wait for all agents to be ready
        await self._wait_for_agents()
        
        self.running = True
        print(f"✅ All lightweight A2A agents ready!")
    
    async def _wait_for_agents(self):
        """Wait for all agents to respond to health checks"""
        max_retries = 30
        for team_num, port in zip([1, 2, 3, 5, 6], self.allocated_ports):
            url = f"http://127.0.0.1:{port}/health"
            for i in range(max_retries):
                try:
                    response = await self.client.get(url)
                    if response.status_code == 200:
                        print(f"✅ Agent {team_num} ready on port {port}")
                        break
                except:
                    pass
                await asyncio.sleep(0.5)
            else:
                raise RuntimeError(f"Agent {team_num} failed to start on port {port}")
    
    async def get_pick(self, team_num: int, available_players: List[str], 
                      previous_picks: List[str], round_num: int) -> Optional[PickResponse]:
        """Get pick from agent via HTTP"""
        if team_num not in self.processes:
            return None
        
        port_index = [1, 2, 3, 5, 6].index(team_num)
        port = self.allocated_ports[port_index]
        
        try:
            response = await self.client.post(
                f"http://127.0.0.1:{port}/pick",
                json={
                    "available_players": available_players,
                    "previous_picks": previous_picks,
                    "round_num": round_num
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return PickResponse(**data)
            else:
                print(f"Error from agent {team_num}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Failed to get pick from agent {team_num}: {e}")
            return None
    
    async def get_comment(self, commenting_team: int, picking_team: int, 
                         player: str, round_num: int) -> Optional[str]:
        """Get comment from agent via HTTP"""
        if commenting_team not in self.processes:
            return None
        
        port_index = [1, 2, 3, 5, 6].index(commenting_team)
        port = self.allocated_ports[port_index]
        
        try:
            response = await self.client.post(
                f"http://127.0.0.1:{port}/comment",
                json={
                    "picking_team": picking_team,
                    "player": player,
                    "round_num": round_num
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("comment")
            else:
                return None
        except Exception as e:
            print(f"Failed to get comment from agent {commenting_team}: {e}")
            return None
    
    async def cleanup(self):
        """Stop all agent servers"""
        if self.running:
            print(f"🛑 Stopping lightweight A2A agents for session {self.session_id}...")
            
            # Close HTTP client
            if self.client:
                await self.client.aclose()
            
            # Terminate all processes
            for team_num, process in self.processes.items():
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)
                    if process.is_alive():
                        process.kill()
                        process.join()
                print(f"✅ Agent {team_num} stopped")
            
            self.processes.clear()
            self.allocated_ports.clear()
            self.running = False
            print(f"✅ Lightweight A2A session {self.session_id} cleaned up")


# Provide same cleanup function interface
async def cleanup_session(manager: LightweightA2AAgentManager):
    """Clean up a lightweight A2A session"""
    if manager:
        await manager.cleanup() 