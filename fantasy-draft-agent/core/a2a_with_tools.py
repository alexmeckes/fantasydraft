#!/usr/bin/env python3
"""
Simpler A2A Implementation using a2a_tool_async
This shows how to use the a2a_tool pattern for easier agent communication.
"""

import asyncio
from typing import Dict, List
from pydantic import BaseModel
from any_agent import AgentConfig, AnyAgent
from any_agent.serving import A2AServingConfig
from any_agent.tools import a2a_tool_async


# Define output types
class PickDecision(BaseModel):
    player: str
    reasoning: str
    trash_talk: str


class CommentDecision(BaseModel):
    should_comment: bool
    comment: str = ""
    is_salty: bool = False


# Create specialized draft agents
async def create_zero_rb_agent():
    """Create and serve a Zero RB strategy agent."""
    agent = await AnyAgent.create_async(
        "openai",
        AgentConfig(
            name="zero_rb_agent",
            model_id="gpt-4o-mini",
            instructions="""You are Team 1, a Zero RB fanatic.
            
Your beliefs:
- WRs > RBs always
- RBs get injured too much
- Mock anyone who takes RBs early
- Your motto: "Zero RB or Zero Championships!"

Be aggressive and confident in your strategy.""",
            description="Zero RB strategy agent - avoids RBs early",
            output_type=PickDecision | CommentDecision,
        )
    )
    
    # Serve the agent
    await agent.serve_async(
        A2AServingConfig(
            port=5001,
            task_timeout_minutes=30,
        )
    )
    
    return agent


async def create_robust_rb_agent():
    """Create and serve a Robust RB strategy agent."""
    agent = await AnyAgent.create_async(
        "openai",
        AgentConfig(
            name="robust_rb_agent",
            model_id="gpt-4o-mini",
            instructions="""You are Team 3, a Robust RB traditionalist.
            
Your beliefs:
- RBs win championships
- WR-heavy teams are soft
- You need a strong RB foundation
- Your motto: "Establish the run game!"

Be old-school and dismissive of modern strategies.""",
            description="Robust RB strategy agent - prioritizes RBs",
            output_type=PickDecision | CommentDecision,
        )
    )
    
    await agent.serve_async(
        A2AServingConfig(
            port=5003,
            task_timeout_minutes=30,
        )
    )
    
    return agent


# Draft Coordinator using a2a_tools
class SimpleA2ADraftCoordinator:
    """Simpler coordinator using a2a_tool_async."""
    
    def __init__(self):
        self.agents = {}
        self.agent_tools = {}
        self.task_ids = {}
        
    async def setup(self):
        """Setup agents and create a2a tools."""
        print("🚀 Starting agent servers...")
        
        # Create and serve agents
        self.agents['zero_rb'] = await create_zero_rb_agent()
        self.agents['robust_rb'] = await create_robust_rb_agent()
        
        # Wait for servers to start
        await asyncio.sleep(2)
        
        # Create a2a tools for each agent
        self.agent_tools['zero_rb'] = await a2a_tool_async(
            "http://localhost:5001/zero_rb_agent"
        )
        self.agent_tools['robust_rb'] = await a2a_tool_async(
            "http://localhost:5003/robust_rb_agent"
        )
        
        print("✅ All agents ready for A2A communication!")
    
    async def simulate_pick_and_comment(self):
        """Simulate a pick and comment exchange."""
        
        # 1. Zero RB makes a pick
        print("\n📋 Team 1 (Zero RB) is making their pick...")
        
        pick_prompt = """It's your turn to pick!
        
Available: Justin Jefferson, Christian McCaffrey, CeeDee Lamb
Previous picks: None

Make your pick and explain why. Output a PickDecision."""
        
        # Get pick from Zero RB agent
        zero_rb_pick = await self.agent_tools['zero_rb'](
            pick_prompt,
            task_id=self.task_ids.get('zero_rb')  # Continue conversation if exists
        )
        
        # Store task ID for multi-turn
        if 'zero_rb' not in self.task_ids and hasattr(zero_rb_pick, 'id'):
            self.task_ids['zero_rb'] = zero_rb_pick.id
        
        print(f"\n📘 Team 1 selects: {zero_rb_pick.player}")
        print(f"   Reasoning: {zero_rb_pick.reasoning}")
        print(f"   💬 {zero_rb_pick.trash_talk}")
        
        # 2. Ask Robust RB to comment
        print("\n🤔 Team 3 (Robust RB) considering a comment...")
        
        comment_prompt = f"""Team 1 (Zero RB) just picked {zero_rb_pick.player}.
They said: "{zero_rb_pick.trash_talk}"

Should you comment on this pick? Remember you believe in RBs.
Output a CommentDecision."""
        
        # Get comment decision
        robust_comment = await self.agent_tools['robust_rb'](
            comment_prompt,
            task_id=self.task_ids.get('robust_rb')
        )
        
        if 'robust_rb' not in self.task_ids and hasattr(robust_comment, 'id'):
            self.task_ids['robust_rb'] = robust_comment.id
        
        if robust_comment.should_comment:
            print(f"\n📙 Team 3 → Team 1: {robust_comment.comment}")
            if robust_comment.is_salty:
                print("   (😤 They seem upset!)")
        
        # 3. Continue the conversation
        if robust_comment.should_comment:
            print("\n💭 Team 1 processing the comment...")
            
            response_prompt = f"""Team 3 (Robust RB) just said to you: "{robust_comment.comment}"

They're criticizing your Zero RB approach. How do you respond?
Remember to defend your strategy! Output a CommentDecision."""
            
            zero_response = await self.agent_tools['zero_rb'](
                response_prompt,
                task_id=self.task_ids['zero_rb']  # Continue the conversation!
            )
            
            if zero_response.should_comment:
                print(f"\n📘 Team 1 → Team 3: {zero_response.comment}")
    
    async def cleanup(self):
        """Shutdown all agents."""
        print("\n🛑 Shutting down agents...")
        # In a real implementation, you'd properly shutdown the servers
        # For now, the servers will stop when the program exits


# Using a coordinator agent with a2a tools
async def create_coordinator_agent():
    """Create a coordinator agent that uses other agents via a2a tools."""
    
    # First, start the draft agents
    print("🚀 Starting draft agents...")
    zero_rb = await create_zero_rb_agent()
    robust_rb = await create_robust_rb_agent()
    
    await asyncio.sleep(2)
    
    # Create a2a tools
    zero_rb_tool = await a2a_tool_async("http://localhost:5001/zero_rb_agent")
    robust_rb_tool = await a2a_tool_async("http://localhost:5003/robust_rb_agent")
    
    # Create coordinator with a2a tools
    coordinator = await AnyAgent.create_async(
        "openai",
        AgentConfig(
            model_id="gpt-4o",
            instructions="""You are the draft coordinator.
            
Use the Zero RB and Robust RB agents to simulate a draft.
1. Ask each agent to make picks
2. Get them to comment on each other's picks
3. Facilitate their debate
4. Keep the draft moving

The agents will maintain their own conversation history via task IDs.""",
            tools=[zero_rb_tool, robust_rb_tool],
        )
    )
    
    # Run a draft simulation
    result = await coordinator.run_async("""
    Simulate a mini draft:
    1. Ask Zero RB agent to pick from: Jefferson, McCaffrey, Lamb
    2. Get Robust RB to comment on the pick
    3. Let them debate briefly
    4. Summarize their interaction
    """)
    
    print("\n📊 Coordinator Summary:")
    print(result.final_output)


# Main execution
async def main():
    """Run the A2A draft demonstration."""
    
    print("=== A2A Draft Demo with any-agent ===\n")
    
    print("Option 1: Simple A2A Communication")
    coordinator = SimpleA2ADraftCoordinator()
    await coordinator.setup()
    await coordinator.simulate_pick_and_comment()
    await coordinator.cleanup()
    
    print("\n" + "="*50 + "\n")
    
    print("Option 2: Coordinator Agent with A2A Tools")
    # Uncomment to run this version
    # await create_coordinator_agent()


if __name__ == "__main__":
    asyncio.run(main()) 