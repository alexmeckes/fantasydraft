#!/usr/bin/env python3
"""
Context Injection Demo - Alternative to Task IDs
Shows how to maintain conversation state by passing full context with each request.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from any_agent import AnyAgent, AgentConfig


# Response models
class PickResponse(BaseModel):
    player: str
    reasoning: str
    reference_to_past: Optional[str] = None


class CommentResponse(BaseModel):
    comment: str
    escalation_level: int  # 1-10, does it escalate based on history?


class ContextInjectionDemo:
    """Demo showing context injection approach to multi-turn conversations."""
    
    def __init__(self):
        self.agents = {}
        # Store EVERYTHING locally - no task IDs needed
        self.full_conversation_history = {}
        self.pick_history = {}
        self.rivalry_scores = {}
        
    async def create_agents(self):
        """Create stateless agents that rely on context injection."""
        
        # Zero RB Agent - No memory, relies on injected context
        self.agents['zero_rb'] = await AnyAgent.create_async(
            "openai",
            AgentConfig(
                model_id="gpt-4o-mini",
                instructions="""You are a Zero RB fantasy football strategist.
                
IMPORTANT: You have NO memory between calls. All context comes from the conversation history provided.
- Read the FULL CONTEXT carefully
- Reference specific past events when mentioned
- Escalate rivalries based on what was said before
- Your personality should be consistent with past interactions""",
                output_type=PickResponse | CommentResponse
            )
        )
        
        # Robust RB Agent - Also stateless
        self.agents['robust_rb'] = await AnyAgent.create_async(
            "openai",
            AgentConfig(
                model_id="gpt-4o-mini",
                instructions="""You are a Robust RB traditionalist.
                
IMPORTANT: You have NO memory between calls. All context comes from the conversation history provided.
- Study the conversation history for past interactions
- Remember and reference specific insults or claims
- Build on previous arguments
- Get more heated if the rivalry has history""",
                output_type=PickResponse | CommentResponse
            )
        )
        
        print("✅ Created stateless agents for context injection demo")
    
    def _add_to_history(self, agent_name: str, entry: Dict):
        """Add entry to conversation history."""
        if agent_name not in self.full_conversation_history:
            self.full_conversation_history[agent_name] = []
        
        entry['timestamp'] = datetime.now().isoformat()
        entry['sequence'] = len(self.full_conversation_history[agent_name])
        self.full_conversation_history[agent_name].append(entry)
    
    def _get_formatted_history(self, agent_name: str, include_rivals: bool = True) -> str:
        """Format the complete conversation history for injection."""
        history_parts = []
        
        # Add own history
        if agent_name in self.full_conversation_history:
            history_parts.append("YOUR PREVIOUS INTERACTIONS:")
            for entry in self.full_conversation_history[agent_name]:
                history_parts.append(
                    f"[{entry['sequence']}] {entry.get('type', 'unknown')}: {entry.get('content', '')}"
                )
        
        # Add rival interactions if requested
        if include_rivals:
            rival_name = 'robust_rb' if agent_name == 'zero_rb' else 'zero_rb'
            if rival_name in self.full_conversation_history:
                history_parts.append(f"\n{rival_name.upper()} HISTORY (YOUR RIVAL):")
                for entry in self.full_conversation_history[rival_name][-3:]:  # Last 3
                    history_parts.append(
                        f"[{entry['sequence']}] {entry.get('type', 'unknown')}: {entry.get('content', '')}"
                    )
        
        # Add rivalry score
        rivalry_key = "zero_rb_vs_robust_rb"
        if rivalry_key in self.rivalry_scores:
            history_parts.append(f"\nRIVALRY INTENSITY: {self.rivalry_scores[rivalry_key]}/10")
        
        return "\n".join(history_parts) if history_parts else "No previous interactions."
    
    async def simulate_draft_with_context(self):
        """Run a multi-round draft using context injection."""
        
        print("\n🏈 ROUND 1 - First Interactions")
        print("=" * 50)
        
        # Round 1: Zero RB picks with no history
        history = self._get_formatted_history('zero_rb')
        
        pick_prompt = f"""
FULL CONVERSATION HISTORY:
{history}

CURRENT PICK SITUATION:
Available players: Justin Jefferson (WR), Christian McCaffrey (RB), Tyreek Hill (WR)
This is Round 1, Pick 1.

Make your pick and explain your reasoning. Since this is your first pick, establish your philosophy strongly.
"""
        
        pick1 = await self.agents['zero_rb'].run_async(pick_prompt)
        print(f"\n📘 Zero RB picks: {pick1.player}")
        print(f"   Reasoning: {pick1.reasoning}")
        
        # Store the interaction
        self._add_to_history('zero_rb', {
            'type': 'pick',
            'round': 1,
            'content': f"Picked {pick1.player}: {pick1.reasoning}",
            'player': pick1.player
        })
        
        # Robust RB comments - with Zero RB's history injected
        rb_history = self._get_formatted_history('robust_rb', include_rivals=True)
        
        comment_prompt = f"""
FULL CONVERSATION HISTORY:
{rb_history}

CURRENT SITUATION:
Zero RB just picked {pick1.player} in Round 1.
They said: "{pick1.reasoning}"

Provide a comment criticizing their pick and philosophy.
"""
        
        comment1 = await self.agents['robust_rb'].run_async(comment_prompt)
        print(f"\n📙 Robust RB: {comment1.comment}")
        
        # Store the comment
        self._add_to_history('robust_rb', {
            'type': 'comment',
            'round': 1,
            'content': comment1.comment,
            'target': 'zero_rb',
            'about_player': pick1.player
        })
        
        # Update rivalry score
        self.rivalry_scores['zero_rb_vs_robust_rb'] = comment1.escalation_level
        
        print("\n🏈 ROUND 2 - Building on History")
        print("=" * 50)
        
        # Round 2: Robust RB picks - should reference Round 1
        rb_history = self._get_formatted_history('robust_rb')
        
        pick_prompt2 = f"""
FULL CONVERSATION HISTORY:
{rb_history}

CURRENT PICK SITUATION:
Available players: Christian McCaffrey (RB), Nick Chubb (RB), CeeDee Lamb (WR)
This is Round 2, Pick 3 (your turn).

Make your pick. Reference your previous criticism of Zero RB's strategy.
"""
        
        pick2 = await self.agents['robust_rb'].run_async(pick_prompt2)
        print(f"\n📙 Robust RB picks: {pick2.player}")
        print(f"   Reasoning: {pick2.reasoning}")
        if pick2.reference_to_past:
            print(f"   Past reference: {pick2.reference_to_past}")
        
        self._add_to_history('robust_rb', {
            'type': 'pick',
            'round': 2,
            'content': f"Picked {pick2.player}: {pick2.reasoning}",
            'player': pick2.player
        })
        
        # Zero RB responds - should remember the criticism
        zrb_history = self._get_formatted_history('zero_rb', include_rivals=True)
        
        response_prompt = f"""
FULL CONVERSATION HISTORY:
{zrb_history}

CURRENT SITUATION:
Robust RB just picked {pick2.player} in Round 2.
They said: "{pick2.reasoning}"

In Round 1, they criticized your pick of {pick1.player}.
Provide a snarky comment defending your strategy and mocking theirs.
Reference the specific criticism they made earlier.
"""
        
        response = await self.agents['zero_rb'].run_async(response_prompt)
        print(f"\n📘 Zero RB fires back: {response.comment}")
        print(f"   Escalation level: {response.escalation_level}/10")
        
        self._add_to_history('zero_rb', {
            'type': 'comment',
            'round': 2,
            'content': response.comment,
            'target': 'robust_rb',
            'about_player': pick2.player
        })
        
        # Update rivalry
        self.rivalry_scores['zero_rb_vs_robust_rb'] = max(
            self.rivalry_scores['zero_rb_vs_robust_rb'],
            response.escalation_level
        )
        
        print("\n🏈 ROUND 3 - Full History Context")
        print("=" * 50)
        
        # Show how the full context has grown
        print("\n📊 Context Size Check:")
        for agent in ['zero_rb', 'robust_rb']:
            history = self._get_formatted_history(agent, include_rivals=True)
            print(f"{agent}: {len(history)} characters, {len(history.split())} words")
        
        # One more pick to show deep context
        zrb_history = self._get_formatted_history('zero_rb', include_rivals=True)
        
        final_pick_prompt = f"""
FULL CONVERSATION HISTORY:
{zrb_history}

CURRENT PICK SITUATION:
Available players: Davante Adams (WR), Stefon Diggs (WR), Derrick Henry (RB)
This is Round 3, Pick 13 (your second pick).

Make your pick. Reference BOTH:
1. Your Round 1 philosophy
2. The escalating rivalry with Robust RB
3. Their specific criticisms and your responses
"""
        
        final_pick = await self.agents['zero_rb'].run_async(final_pick_prompt)
        print(f"\n📘 Zero RB's second pick: {final_pick.player}")
        print(f"   Reasoning: {final_pick.reasoning}")
        if final_pick.reference_to_past:
            print(f"   Callbacks: {final_pick.reference_to_past}")
    
    async def compare_with_task_ids(self):
        """Show the differences between context injection and task IDs."""
        
        print("\n\n📊 CONTEXT INJECTION VS TASK IDs")
        print("=" * 50)
        
        print("\n1. STATE MANAGEMENT:")
        print("   Context Injection: All state stored locally, injected each time")
        print("   Task IDs: State maintained on agent server")
        
        print("\n2. TOKEN USAGE:")
        print("   Context Injection: Grows with conversation length")
        print("   Task IDs: Consistent token usage")
        
        print("\n3. DEBUGGING:")
        print("   Context Injection: Full visibility into what agent sees")
        print("   Task IDs: Black box - can't see internal state")
        
        print("\n4. FLEXIBILITY:")
        print("   Context Injection: Can modify/filter history before sending")
        print("   Task IDs: Agent controls its own memory")
        
        print("\n5. PERFORMANCE:")
        total_tokens = sum(
            len(self._get_formatted_history(agent).split()) 
            for agent in self.full_conversation_history.keys()
        )
        print(f"   Total context words after 3 rounds: ~{total_tokens}")
        print("   With Task IDs: Would be constant per request")


async def main():
    """Run the context injection demonstration."""
    print("=== CONTEXT INJECTION DEMO ===")
    print("Alternative to Task IDs for Multi-turn Conversations")
    print()
    
    demo = ContextInjectionDemo()
    
    # Create agents
    await demo.create_agents()
    
    # Run the simulation
    await demo.simulate_draft_with_context()
    
    # Compare approaches
    await demo.compare_with_task_ids()
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main()) 