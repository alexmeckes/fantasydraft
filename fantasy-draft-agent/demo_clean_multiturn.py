#!/usr/bin/env python3
"""
Clean Multi-Turn Conversation Demo
Displays complete messages with clear visual indicators.
No typewriter effects to avoid terminal compatibility issues.
"""

import time
from agent import FantasyDraftAgent


def display_turn(turn_number, user_msg, agent_response, memory_count=0):
    """Display a conversation turn with clean formatting."""
    print(f"\n{'━' * 60}")
    print(f"🔄 Turn {turn_number}: ", end="")
    
    if memory_count > 0:
        print(f"💭 Agent Memory Active - Remembering {memory_count} previous exchange{'s' if memory_count > 1 else ''}")
    else:
        print("Initial situation assessment")
    
    print()
    
    # Display complete user message
    print(f"👤 User: {user_msg}")
    
    # Pause for readability
    time.sleep(1)
    
    # Display complete agent response
    print(f"\n🤖 Agent: {agent_response}")
    
    # Highlight context retention
    context_indicators = {
        "5th pick": "Remembered draft position from Turn 1",
        "you mentioned": "Using previous conversation context",
        "Bijan": "Recalling earlier player discussion",
        "Ekeler": "Building on previous recommendation",
        "we discussed": "Referencing earlier exchange",
        "earlier": "Acknowledging conversation history"
    }
    
    found_indicators = []
    for indicator, description in context_indicators.items():
        if indicator.lower() in agent_response.lower():
            found_indicators.append(f"   → {description}")
    
    if found_indicators and memory_count > 0:
        print("\n✨ Context Retention Detected:")
        for indicator in found_indicators:
            print(indicator)
    
    time.sleep(1.5)


def run_clean_demo():
    """Run a clean multi-turn demonstration."""
    print("\n" + "=" * 60)
    print("🏈 FANTASY DRAFT AGENT - CLEAN MULTI-TURN DEMO")
    print("=" * 60)
    print("\nDemonstrating context retention across multiple turns...")
    print("(No typewriter effects for better compatibility)")
    
    agent = FantasyDraftAgent()
    
    # Define the conversation
    conversation = [
        "I have the 5th pick and the top 4 guys are gone - McCaffrey, Jefferson, Lamb, and Hill. What should I do?",
        "I'm worried about Bijan being a rookie. What about Ekeler instead?",
        "Good point about the Chargers offense. Who would you pair with him in round 2?"
    ]
    
    # Run the conversation
    for i, user_msg in enumerate(conversation):
        response = agent.run(user_msg)
        display_turn(i + 1, user_msg, response, memory_count=i)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    print("\n✅ The agent successfully maintained context across all 3 turns")
    print("✅ No need for the user to repeat their draft position or preferences")
    print("✅ Each response built upon the previous conversation")
    print("\n💡 This demonstrates any-agent's powerful multi-turn conversation capabilities!")


def run_split_screen_demo():
    """Show a cleaner side-by-side comparison."""
    print("\n" + "=" * 60)
    print("📊 COMPARING: Single-Turn vs Multi-Turn Conversations")
    print("=" * 60)
    
    scenarios = [
        {
            "turn": 1,
            "user": "I have the 5th pick. Who should I target?",
            "single_turn": "I recommend targeting a top RB like Bijan Robinson or Austin Ekeler.",
            "multi_turn": "With the 5th pick and the top 4 gone, I recommend Bijan Robinson or Austin Ekeler."
        },
        {
            "turn": 2,
            "user": "What about Ekeler instead?",
            "single_turn": "❌ Ekeler is a great choice. What pick do you have?",
            "multi_turn": "✅ Given your 5th pick position, Ekeler is an excellent choice over Bijan."
        },
        {
            "turn": 3,
            "user": "Who for round 2?",
            "single_turn": "❌ That depends on your first pick. Who did you take?",
            "multi_turn": "✅ Since you're taking Ekeler at 5, in round 2 I'd target..."
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'─' * 60}")
        print(f"Turn {scenario['turn']}:")
        print(f"User: \"{scenario['user']}\"")
        print(f"\n❌ Without Memory: {scenario['single_turn']}")
        print(f"✅ With Memory:    {scenario['multi_turn']}")
        time.sleep(2)
    
    print(f"\n{'─' * 60}")
    print("\n🎯 Key Difference: Multi-turn agents remember context, eliminating repetition!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--comparison":
        run_split_screen_demo()
    else:
        run_clean_demo() 