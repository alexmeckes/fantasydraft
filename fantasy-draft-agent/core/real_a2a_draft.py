#!/usr/bin/env python3
"""
Real A2A Implementation for Fantasy Draft Agents
This shows how to properly implement Agent-to-Agent communication
using the any-agent framework's A2A protocol.
"""

import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel
from any_agent import AgentConfig, AnyAgent
from any_agent.serving import A2AServingConfig
from any_agent.tools import a2a_tool_async
from any_agent.serving.config import default_history_formatter
import httpx
from a2a.client import A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from uuid import uuid4


# Define structured outputs for agents
class DraftPick(BaseModel):
    player_name: str
    position: str
    reasoning: str
    confidence: float


class DraftComment(BaseModel):
    is_commenting: bool
    comment: Optional[str] = None
    target_team: Optional[str] = None
    sentiment: Optional[str] = None  # "positive", "negative", "neutral"


class DraftResponse(BaseModel):
    should_respond: bool
    response: Optional[str] = None


# Base A2A Draft Agent
class A2ADraftAgent:
    """Base class for A2A-enabled draft agents."""
    
    def __init__(self, team_name: str, strategy: str, port: int):
        self.team_name = team_name
        self.strategy = strategy
        self.port = port
        self.picks = []
        self.agent = None
        self.serving_task = None
        
    async def initialize(self):
        """Initialize the agent with A2A capabilities."""
        self.agent = await AnyAgent.create_async(
            "openai",  # Using OpenAI for better structured outputs
            AgentConfig(
                name=f"{self.team_name.lower().replace(' ', '_')}_agent",
                model_id="gpt-4o-mini",
                instructions=self._get_instructions(),
                description=f"{self.team_name} - {self.strategy} draft strategy",
                output_type=DraftPick | DraftComment | DraftResponse,
                agent_args={"temperature": 0.8}  # More personality
            )
        )
    
    def _get_instructions(self) -> str:
        """Get agent-specific instructions."""
        return f"""You are {self.team_name}, a fantasy football team manager.
        
Your draft strategy: {self.strategy}
Your personality: Competitive, confident in your strategy, willing to trash talk.

When making picks:
- Output a DraftPick with your selection and reasoning
- Be confident about your strategy
- Show personality in your reasoning

When asked to comment on another team's pick:
- Output a DraftComment
- Set is_commenting=true if you want to comment (about 50% of the time)
- Be competitive - trash talk is encouraged!
- Target the team that made the pick
- Express strong opinions about their choice

When asked to respond to a comment:
- Output a DraftResponse
- Set should_respond=true if you want to respond (about 70% of the time)
- Defend your choices aggressively
- Fire back at critics

Remember: This is a competition. Show confidence and personality!"""
    
    async def serve(self):
        """Serve this agent via A2A protocol."""
        self.serving_task = asyncio.create_task(
            self.agent.serve_async(
                A2AServingConfig(
                    port=self.port,
                    task_timeout_minutes=60,  # 1 hour draft session
                    history_formatter=default_history_formatter,
                    endpoint=f"/{self.team_name.lower().replace(' ', '_')}"
                )
            )
        )
        print(f"🚀 {self.team_name} agent serving on port {self.port}")
    
    async def shutdown(self):
        """Shutdown the agent server."""
        if self.serving_task:
            self.serving_task.cancel()
            try:
                await self.serving_task
            except asyncio.CancelledError:
                pass


# Specific Strategy Implementations
class ZeroRBA2AAgent(A2ADraftAgent):
    """Zero RB strategy agent with A2A."""
    
    def __init__(self, port: int):
        super().__init__("Team 1", "Zero RB Strategy", port)
    
    def _get_instructions(self) -> str:
        base = super()._get_instructions()
        return base + """

Specific to your Zero RB strategy:
- ALWAYS prioritize WRs in early rounds
- Mock teams that take RBs early
- Talk about injury risk and RB volatility
- Get defensive when criticized about ignoring RBs
- Your catchphrase: "RBs get injured, WRs win championships!"
"""


class RobustRBA2AAgent(A2ADraftAgent):
    """Robust RB strategy agent with A2A."""
    
    def __init__(self, port: int):
        super().__init__("Team 3", "Robust RB Strategy", port)
    
    def _get_instructions(self) -> str:
        base = super()._get_instructions()
        return base + """

Specific to your Robust RB strategy:
- ALWAYS take RBs in rounds 1-2
- Mock "fancy" WR strategies as risky
- Emphasize the importance of a strong RB foundation
- Be old-school and traditional in your approach
- Your catchphrase: "Championships are won in the trenches with RBs!"
"""


# Multi-Agent Draft Coordinator
class A2ADraftCoordinator:
    """Coordinates a draft using real A2A communication."""
    
    def __init__(self):
        self.agents: Dict[int, A2ADraftAgent] = {}
        self.draft_board: Dict[int, List[str]] = {}
        self.available_players = []  # Would be populated from data
        self.task_ids: Dict[str, str] = {}  # Track task IDs for each agent
        
    async def setup_agents(self):
        """Initialize and serve all draft agents."""
        # Create agents with different strategies
        self.agents[1] = ZeroRBA2AAgent(port=5001)
        self.agents[2] = A2ADraftAgent("Team 2", "Best Player Available", port=5002)
        self.agents[3] = RobustRBA2AAgent(port=5003)
        self.agents[5] = A2ADraftAgent("Team 5", "Upside Hunter", port=5005)
        
        # Initialize and serve all agents
        for agent in self.agents.values():
            await agent.initialize()
            await agent.serve()
        
        # Wait for servers to start
        await asyncio.sleep(2)
        
        print("✅ All agents initialized and serving via A2A")
    
    async def execute_draft_turn(self, team_num: int, round_num: int) -> Dict:
        """Execute a draft turn using A2A communication."""
        if team_num not in self.agents:
            return {"error": "Team not found"}
        
        agent = self.agents[team_num]
        results = {"pick": None, "comments": [], "responses": []}
        
        async with httpx.AsyncClient() as client:
            # 1. Get the agent's pick via A2A
            try:
                # Create A2A client for this agent
                a2a_client = await A2AClient.get_client_from_agent_card_url(
                    client, f"http://localhost:{agent.port}"
                )
                
                # Build pick request
                pick_prompt = f"""Round {round_num} - Make your pick!
                
Available top players: {', '.join(self.available_players[:10])}
Your previous picks: {', '.join(agent.picks)}

Output a DraftPick with your selection."""
                
                # Send pick request
                pick_request = SendMessageRequest(
                    id=str(uuid4()),
                    params=MessageSendParams(
                        message={
                            "role": "user",
                            "parts": [{"kind": "text", "text": pick_prompt}],
                            "messageId": str(uuid4()),
                            "contextId": f"draft_session_{team_num}"
                        }
                    )
                )
                
                # Get pick response
                pick_response = await a2a_client.send_message(pick_request)
                
                # Extract task ID for this agent if first interaction
                if team_num not in self.task_ids:
                    self.task_ids[team_num] = pick_response.root.result.id
                
                results["pick"] = pick_response.root.result
                
                # 2. Get comments from other agents
                for other_team, other_agent in self.agents.items():
                    if other_team == team_num:
                        continue
                    
                    # Create client for other agent
                    other_client = await A2AClient.get_client_from_agent_card_url(
                        client, f"http://localhost:{other_agent.port}"
                    )
                    
                    # Ask for comment
                    comment_prompt = f"""{agent.team_name} just picked {results['pick']['player_name']} in round {round_num}.

Should you comment on this pick? Output a DraftComment."""
                    
                    comment_request = SendMessageRequest(
                        id=str(uuid4()),
                        params=MessageSendParams(
                            message={
                                "role": "user",
                                "parts": [{"kind": "text", "text": comment_prompt}],
                                "messageId": str(uuid4()),
                                "contextId": f"draft_session_{other_team}",
                                "taskId": self.task_ids.get(other_team)  # Continue conversation
                            }
                        }
                    )
                    
                    comment_response = await other_client.send_message(comment_request)
                    
                    # Update task ID
                    if other_team not in self.task_ids:
                        self.task_ids[other_team] = comment_response.root.result.id
                    
                    # Add comment if agent chose to comment
                    if comment_response.root.result.get("is_commenting"):
                        results["comments"].append({
                            "from": other_agent.team_name,
                            "comment": comment_response.root.result.get("comment")
                        })
                
                # 3. Get responses to comments
                for comment in results["comments"]:
                    response_prompt = f"""{comment['from']} said about your pick: "{comment['comment']}"

Do you want to respond? Output a DraftResponse."""
                    
                    response_request = SendMessageRequest(
                        id=str(uuid4()),
                        params=MessageSendParams(
                            message={
                                "role": "user",
                                "parts": [{"kind": "text", "text": response_prompt}],
                                "messageId": str(uuid4()),
                                "contextId": f"draft_session_{team_num}",
                                "taskId": self.task_ids[team_num]  # Continue conversation
                            }
                        )
                    )
                    
                    response_response = await a2a_client.send_message(response_request)
                    
                    if response_response.root.result.get("should_respond"):
                        results["responses"].append({
                            "to": comment['from'],
                            "response": response_response.root.result.get("response")
                        })
                
            except Exception as e:
                results["error"] = str(e)
        
        return results
    
    async def run_mock_draft(self):
        """Run a complete mock draft with A2A communication."""
        await self.setup_agents()
        
        # Simulate 3 rounds
        for round_num in range(1, 4):
            print(f"\n🏈 ROUND {round_num}")
            
            # Snake draft order
            if round_num % 2 == 1:
                order = [1, 2, 3, 4, 5, 6]  # 4 is human, 6 is another AI
            else:
                order = [6, 5, 4, 3, 2, 1]
            
            for team in order:
                if team == 4:
                    print("👤 Your turn! (simulated)")
                    continue
                
                if team in self.agents:
                    results = await self.execute_draft_turn(team, round_num)
                    
                    # Display results
                    if "pick" in results and results["pick"]:
                        pick = results["pick"]
                        print(f"\n📋 {self.agents[team].team_name} selects: {pick.get('player_name')}")
                        print(f"   Reasoning: {pick.get('reasoning')}")
                    
                    # Show comments
                    for comment in results.get("comments", []):
                        print(f"\n💬 {comment['from']}: {comment['comment']}")
                    
                    # Show responses
                    for response in results.get("responses", []):
                        print(f"   ↩️  {self.agents[team].team_name}: {response['response']}")
        
        # Shutdown all agents
        for agent in self.agents.values():
            await agent.shutdown()
        
        print("\n✅ Draft complete! All agents shut down.")


# Example usage
async def main():
    """Run the A2A draft demo."""
    coordinator = A2ADraftCoordinator()
    
    # In a real implementation, populate available players
    coordinator.available_players = [
        "Christian McCaffrey", "Tyreek Hill", "Justin Jefferson",
        "CeeDee Lamb", "Austin Ekeler", "Bijan Robinson",
        "Ja'Marr Chase", "Cooper Kupp", "Stefon Diggs"
    ]
    
    await coordinator.run_mock_draft()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 