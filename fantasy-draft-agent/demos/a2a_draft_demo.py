#!/usr/bin/env python3
"""
Working A2A Draft Demo
This demonstrates real Agent-to-Agent communication for the fantasy draft.
"""

import asyncio
import nest_asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from pydantic import BaseModel
from any_agent import AgentConfig, AnyAgent
from any_agent.serving import A2AServingConfig
from any_agent.tools import a2a_tool_async
from core.data import TOP_PLAYERS

# Apply nest_asyncio to allow running in Jupyter/existing event loops
nest_asyncio.apply()


# Define structured outputs
class DraftPick(BaseModel):
    player_name: str
    position: str
    reasoning: str
    trash_talk: Optional[str] = None


class AgentComment(BaseModel):
    should_comment: bool
    comment: Optional[str] = None
    target_team: Optional[str] = None


# Create specialized draft agents
async def create_draft_agent(
    name: str,
    strategy: str,
    port: int,
    personality: str
) -> AnyAgent:
    """Create and serve a draft agent with specific strategy."""
    
    agent = await AnyAgent.create_async(
        "tinyagent",  # Using tinyagent for simplicity
        AgentConfig(
            name=name.lower().replace(" ", "_"),
            model_id="gpt-4o-mini",
            instructions=f"""You are {name}, a fantasy football team manager.
            
Strategy: {strategy}
Personality: {personality}

When making picks:
- Output a DraftPick with your selection
- Include trash talk that fits your personality
- Be confident about your strategy

When asked to comment:
- Output an AgentComment
- Comment about 50% of the time (should_comment=true)
- Be competitive and show personality
- Target the team that made the pick

Available players will be provided. Pick based on your strategy.""",
            description=f"{name} - {strategy}",
            output_type=DraftPick | AgentComment,
        )
    )
    
    print(f"📡 Serving {name} on port {port}...")
    
    # Serve the agent asynchronously
    serve_task = asyncio.create_task(
        agent.serve_async(
            A2AServingConfig(
                port=port,
                task_timeout_minutes=30,
            )
        )
    )
    
    # Give it a moment to start
    await asyncio.sleep(1)
    
    return agent, serve_task


class A2ADraftDemo:
    """Simple A2A draft demonstration."""
    
    def __init__(self):
        self.agents = {}
        self.agent_tools = {}
        self.serve_tasks = []
        self.picks = {i: [] for i in range(1, 5)}  # 4 teams
        
    async def setup(self):
        """Setup all agents and their A2A tools."""
        print("\n🚀 Starting A2A Draft Demo...\n")
        
        # Define our agents
        agent_configs = [
            ("Team 1 - Zero RB", "Zero RB Strategy", 5001, 
             "Analytical, dismissive of RBs, loves WRs"),
            ("Team 2 - BPA", "Best Player Available", 5002,
             "Logical, value-focused, mocks reaches"),
            ("Team 3 - Robust RB", "Robust RB Strategy", 5003,
             "Traditional, RB-focused, old-school"),
            ("Team 4 - Upside", "Upside Hunter", 5004,
             "Risk-taker, seeks breakouts, mocks safe picks")
        ]
        
        # Create and serve each agent
        for name, strategy, port, personality in agent_configs:
            agent, serve_task = await create_draft_agent(
                name, strategy, port, personality
            )
            
            team_num = int(name.split()[1])
            self.agents[team_num] = agent
            self.serve_tasks.append(serve_task)
            
            # Create A2A tool for this agent
            agent_id = name.lower().replace(" ", "_").replace("-", "")
            self.agent_tools[team_num] = await a2a_tool_async(
                f"http://localhost:{port}/{agent_id}"
            )
        
        print("\n✅ All agents ready! Starting draft...\n")
        await asyncio.sleep(1)
    
    def get_available_players(self) -> List[str]:
        """Get list of available players."""
        all_picked = []
        for picks in self.picks.values():
            all_picked.extend(picks)
        
        available = [p for p in TOP_PLAYERS.keys() if p not in all_picked]
        return available[:20]  # Top 20 available
    
    async def execute_pick(self, team_num: int, round_num: int):
        """Execute a pick for a team using A2A."""
        available = self.get_available_players()
        
        # Format available players with positions
        available_str = []
        for player in available[:10]:
            info = TOP_PLAYERS[player]
            available_str.append(f"{player} ({info['pos']})")
        
        pick_prompt = f"""Round {round_num} - Your turn to pick!
        
Top available players: {', '.join(available_str)}
Your previous picks: {', '.join(self.picks[team_num]) if self.picks[team_num] else 'None'}

Make your pick and explain why. Include some trash talk!
Output a DraftPick."""
        
        print(f"\n🎯 Team {team_num} is on the clock...")
        
        # Get pick via A2A
        try:
            pick_result = await self.agent_tools[team_num](pick_prompt)
            
            # Store the pick
            self.picks[team_num].append(pick_result.player_name)
            
            # Display the pick
            print(f"\n📋 Team {team_num} selects: **{pick_result.player_name}** ({pick_result.position})")
            print(f"   💭 \"{pick_result.reasoning}\"")
            if pick_result.trash_talk:
                print(f"   🗣️  \"{pick_result.trash_talk}\"")
            
            return pick_result
            
        except Exception as e:
            print(f"❌ Error getting pick from Team {team_num}: {e}")
            return None
    
    async def get_comments(self, picking_team: int, pick: DraftPick):
        """Get comments from other teams about a pick."""
        comments = []
        
        for team_num, tool in self.agent_tools.items():
            if team_num == picking_team:
                continue
            
            comment_prompt = f"""Team {picking_team} just picked {pick.player_name} ({pick.position}).
They said: "{pick.trash_talk if pick.trash_talk else pick.reasoning}"

Should you comment on this pick? Remember your strategy and personality.
Output an AgentComment."""
            
            try:
                comment_result = await tool(comment_prompt)
                
                if comment_result.should_comment and comment_result.comment:
                    comments.append((team_num, comment_result.comment))
                    print(f"\n   💬 Team {team_num}: \"{comment_result.comment}\"")
                    
            except Exception as e:
                print(f"   ⚠️  Team {team_num} couldn't comment: {e}")
        
        return comments
    
    async def run_draft(self, rounds: int = 2):
        """Run a mock draft for specified rounds."""
        
        for round_num in range(1, rounds + 1):
            print(f"\n{'='*50}")
            print(f"📍 ROUND {round_num}")
            print(f"{'='*50}")
            
            # Simple sequential draft (not snake)
            for team_num in range(1, 5):
                # Make pick
                pick = await self.execute_pick(team_num, round_num)
                
                if pick:
                    # Get comments from other teams
                    await asyncio.sleep(0.5)  # Brief pause
                    await self.get_comments(team_num, pick)
                
                await asyncio.sleep(1)  # Pause between picks
        
        print(f"\n{'='*50}")
        print("📊 DRAFT RESULTS")
        print(f"{'='*50}\n")
        
        for team_num in range(1, 5):
            print(f"Team {team_num}: {', '.join(self.picks[team_num])}")
    
    async def cleanup(self):
        """Shutdown all agent servers."""
        print("\n🛑 Shutting down agent servers...")
        
        # Cancel all serve tasks
        for task in self.serve_tasks:
            task.cancel()
        
        # Wait for cancellation
        await asyncio.gather(*self.serve_tasks, return_exceptions=True)
        
        print("✅ All servers shut down.")


async def main():
    """Run the A2A draft demo."""
    demo = A2ADraftDemo()
    
    try:
        # Setup agents
        await demo.setup()
        
        # Run draft
        await demo.run_draft(rounds=2)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Draft interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always cleanup
        await demo.cleanup()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║        A2A Fantasy Draft Demo                ║
║                                              ║
║  This demonstrates real Agent-to-Agent       ║
║  communication using the any-agent framework ║
╚══════════════════════════════════════════════╝
""")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    # Run the async main
    asyncio.run(main()) 