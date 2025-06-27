#!/usr/bin/env python3
"""
Demo comparing Task ID only vs Dual Approach
Shows why Task ID only is cleaner and more effective
"""

import asyncio
from typing import Optional
from pydantic import BaseModel
from any_agent import AnyAgent, AgentConfig


class DraftResponse(BaseModel):
    action: str
    content: str
    memory_reference: Optional[str] = None


async def demo_dual_approach():
    """Demonstrate the current dual approach (Task ID + Context Injection)."""
    print("\n=== DUAL APPROACH (Current Implementation) ===")
    print("Using BOTH Task IDs and Context Injection\n")
    
    # Simulate what app_enhanced.py does
    conversation_history = {}
    task_ids = {}
    
    # Create agent
    agent = await AnyAgent.create_async(
        "openai",
        AgentConfig(
            model_id="gpt-4o-mini",
            instructions="You are a fantasy football team manager. Follow the context provided.",
            output_type=DraftResponse
        )
    )
    
    # Round 1 - First interaction
    print("ROUND 1:")
    
    # Build context (empty for first round)
    context = ""  # No history yet
    
    # Complex prompt with injected context
    prompt = f"""CONVERSATION HISTORY:
{context}

CURRENT SITUATION:
Round 1 - Pick from: Jefferson, McCaffrey, Hill
Your roster: None

Make a pick and explain."""
    
    response1 = await agent.run_async(prompt, task_id=task_ids.get('team1'))
    print(f"Pick: {response1.content}")
    
    # Store in BOTH places (redundant!)
    task_ids['team1'] = "abc123"  # Simulated task ID
    conversation_history['team1'] = ["Round 1: Picked Jefferson"]
    
    print("\n" + "="*50 + "\n")
    
    # Round 2 - Show the complexity
    print("ROUND 2:")
    
    # Build context from our tracking
    context = "\n".join(conversation_history['team1'])
    
    # Another complex prompt
    prompt = f"""CONVERSATION HISTORY:
{context}

CURRENT SITUATION:
Round 2 - Team 3 just picked McCaffrey and said "RBs win championships!"
Should you respond?"""
    
    response2 = await agent.run_async(prompt, task_id=task_ids['team1'])
    print(f"Response: {response2.content}")
    
    # More dual tracking...
    conversation_history['team1'].append("Round 2: Mocked Team 3's RB pick")
    
    print("\nPROBLEMS:")
    print("- Managing two state systems")
    print("- Prompt includes partial context + agent has its own memory")
    print("- Complex code to maintain both")
    print(f"- Token usage: ~{len(prompt.split())} words in prompt")


async def demo_taskid_only():
    """Demonstrate the cleaner Task ID only approach."""
    print("\n\n=== TASK ID ONLY APPROACH (Proposed) ===")
    print("Using ONLY Task IDs for all state management\n")
    
    # Only track task IDs
    task_ids = {}
    
    # Create agent with memory emphasis
    agent = await AnyAgent.create_async(
        "openai",
        AgentConfig(
            model_id="gpt-4o-mini",
            instructions="""You are a fantasy football team manager.
            
IMPORTANT: You have FULL MEMORY of all interactions.
- Remember every pick and comment
- Build on previous conversations
- Reference past events naturally""",
            output_type=DraftResponse
        )
    )
    
    # Round 1 - Simple!
    print("ROUND 1:")
    
    # Simple prompt - no context injection
    prompt = """Round 1 - Pick from: Jefferson, McCaffrey, Hill
Your roster: None

Make a pick and explain."""
    
    response1 = await agent.run_async(prompt, task_id=task_ids.get('team1'))
    print(f"Pick: {response1.content}")
    
    # Only store task ID
    task_ids['team1'] = "def456"  # Simulated
    
    print("\n" + "="*50 + "\n")
    
    # Round 2 - Still simple!
    print("ROUND 2:")
    
    # Another simple prompt - agent remembers Round 1
    prompt = """Round 2 - Team 3 just picked McCaffrey and said "RBs win championships!"
Should you respond? Remember your previous picks."""
    
    response2 = await agent.run_async(prompt, task_id=task_ids['team1'])
    print(f"Response: {response2.content}")
    if response2.memory_reference:
        print(f"Memory reference: {response2.memory_reference}")
    
    print("\nBENEFITS:")
    print("- Single state system (just task IDs)")
    print("- Agent manages its own memory completely")
    print("- Much simpler code")
    print(f"- Token usage: ~{len(prompt.split())} words (much less!)")
    
    # Round 3 - Show memory building
    print("\n" + "="*50 + "\n")
    print("ROUND 3 - Testing Deep Memory:")
    
    prompt = """Round 3 - Your turn again.
Available: Lamb, Diggs, Chase

Make a pick that fits with your previous selections."""
    
    response3 = await agent.run_async(prompt, task_id=task_ids['team1'])
    print(f"Pick: {response3.content}")
    if response3.memory_reference:
        print(f"Remembered: {response3.memory_reference}")


async def main():
    """Run both demos to show the difference."""
    print("=== TASK ID COMPARISON DEMO ===")
    print("Showing why Task ID only is cleaner than dual approach")
    
    # Show dual approach problems
    await demo_dual_approach()
    
    # Show Task ID only benefits  
    await demo_taskid_only()
    
    print("\n\n=== SUMMARY ===")
    print("""
Dual Approach (Current):
- Complex: Manages task_ids AND conversation_history
- Redundant: Same information in two places
- Confusing: Agent sees partial context + has own memory
- More tokens: Larger prompts with injected context

Task ID Only (Proposed):
- Simple: Just task_ids
- Clean: Single source of truth
- Natural: Agent manages all memory
- Efficient: Smaller prompts, less tokens

Recommendation: Refactor to use Task ID only!
""")


if __name__ == "__main__":
    asyncio.run(main()) 