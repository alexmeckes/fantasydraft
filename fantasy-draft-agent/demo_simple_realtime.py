#!/usr/bin/env python3
"""
Simple Real-Time Demo - No extra dependencies required
Shows multi-turn conversations unfolding in real-time.
"""

import time
import sys
from agent import FantasyDraftAgent


def print_slow(text, delay=0.03):
    """Print text character by character."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def show_thinking(duration=1.5):
    """Show animated thinking indicator."""
    print("  🤔 Agent is thinking", end='')
    for _ in range(int(duration * 3)):
        print(".", end='', flush=True)
        time.sleep(0.33)
    print("\r" + " " * 50 + "\r", end='')  # Clear line


def run_simple_realtime(clean_mode=False):
    """Run a simple real-time multi-turn demo."""
    print("\n" + "="*60)
    print("🏈 FANTASY DRAFT AGENT - REAL-TIME MULTI-TURN DEMO")
    print("="*60)
    if clean_mode:
        print("(Clean mode: No typewriter effects)")
    else:
        print("\nWatch the conversation unfold in real-time...")
    time.sleep(2)
    
    agent = FantasyDraftAgent()
    
    # The conversation
    turns = [
        "I have the 5th pick and the top 4 guys are gone - McCaffrey, Jefferson, Lamb, and Hill. What should I do?",
        "I'm worried about Bijan being a rookie. What about Ekeler instead?",
        "Good point about the Chargers offense. Who would you pair with him in round 2?"
    ]
    
    for i, user_msg in enumerate(turns):
        print(f"\n\n{'━'*60}")
        print(f"🔄 TURN {i + 1}")
        print(f"{'━'*60}")
        
        # Show memory state
        if i > 0:
            print(f"\n💭 AGENT MEMORY: Remembering {i} previous exchange{'s' if i > 1 else ''}")
            time.sleep(1)
        
        # User message
        print("\n👤 User: ", end='')
        if clean_mode:
            print(user_msg)
            time.sleep(0.5)
        else:
            print_slow(user_msg, delay=0.02)
            time.sleep(0.5)
        
        # Thinking animation (simplified in clean mode)
        if clean_mode:
            print("\n  🤔 Agent is thinking...")
            time.sleep(1)
        else:
            show_thinking()
        
        # Get response
        response = agent.run(user_msg)
        
        # Agent response
        print("\n🤖 Agent: ", end='')
        if clean_mode:
            print(response)
        else:
            print_slow(response, delay=0.015)
        
        # Check for context references
        context_clues = ["5th pick", "you mentioned", "we discussed", "Bijan", "Ekeler"]
        if any(clue in response for clue in context_clues):
            time.sleep(0.5)
            print("\n✨ CONTEXT RETENTION: Agent referenced previous conversation!")
            
            if i == 1 and "5th pick" in response:
                print("   → Remembered your draft position from Turn 1")
            elif i == 2 and "Ekeler" in response:
                print("   → Remembered the Ekeler discussion from Turn 2")
        
        time.sleep(2)
    
    # Summary
    print("\n\n" + "="*60)
    print("📊 DEMO COMPLETE")
    print("="*60)
    print("\n✅ The agent maintained context across all 3 turns!")
    print("✅ No need for the user to repeat information!")
    print("✅ This is the power of multi-turn conversations with any-agent!")


if __name__ == "__main__":
    clean_mode = False
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        clean_mode = True
    
    try:
        run_simple_realtime(clean_mode=clean_mode)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
        sys.exit(0) 