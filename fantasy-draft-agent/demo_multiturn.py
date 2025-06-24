#!/usr/bin/env python3
"""
Multi-Turn Conversation Demo
Shows the visual enhancements for demonstrating context retention.
"""

import time
from scenarios import ScenarioRunner
from visualizer import (
    create_multi_turn_diagram, 
    create_context_highlight_example,
    create_multi_turn_flow
)
from agent import FantasyDraftAgent


def animated_print(text: str, delay: float = 0.03):
    """Print text with a typing animation effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def run_multi_turn_demo():
    """Run a visual demonstration of multi-turn conversations."""
    print("\n" + "="*60)
    print("🏈 FANTASY DRAFT AGENT - MULTI-TURN CONVERSATION DEMO")
    print("="*60)
    
    # Show the concept diagram
    print("\n📊 Concept Overview:")
    print(create_multi_turn_diagram("The Opening Pick"))
    
    input("\nPress Enter to see a real example...")
    
    # Show example with annotations
    print("\n📝 Example with Annotations:")
    print(create_context_highlight_example())
    
    input("\nPress Enter to run a live demo...")
    
    # Run actual scenario with enhanced visuals
    print("\n🎬 Live Demo: Running 'The Opening Pick' Scenario\n")
    
    runner = ScenarioRunner()
    conversation = runner.run_scenario("scenario_1", verbose=True)
    
    # Show the visual flow
    print("\n" + "="*60)
    print("📊 Conversation Flow Visualization:")
    print("="*60)
    print(create_multi_turn_flow(conversation))
    
    # Highlight key achievements
    print("\n🎯 Key Achievements Demonstrated:")
    print("  ✅ Agent remembered the 5th pick position across all turns")
    print("  ✅ Agent referenced previous player discussions")
    print("  ✅ Agent built recommendations on earlier advice")
    print("  ✅ No need for user to repeat context")
    print("\n💡 This is powered by any-agent's conversation management!")


def run_comparison_demo():
    """Show the difference between single-turn and multi-turn."""
    print("\n" + "="*60)
    print("📊 SINGLE-TURN vs MULTI-TURN COMPARISON")
    print("="*60)
    
    print("\n❌ WITHOUT Multi-Turn Memory:")
    print("─" * 40)
    print("Turn 1: User: 'I have the 5th pick. Who should I target?'")
    print("        Agent: 'I recommend Bijan Robinson...'")
    print("\nTurn 2: User: 'What about Ekeler instead?'")
    print("        Agent: '❓ What pick do you have?' (No memory!)")
    
    print("\n\n✅ WITH Multi-Turn Memory (any-agent):")
    print("─" * 40)
    print("Turn 1: User: 'I have the 5th pick. Who should I target?'")
    print("        Agent: 'With the 5th pick, I recommend Bijan Robinson...'")
    print("\nTurn 2: User: 'What about Ekeler instead?'")
    print("        Agent: '💭 Given your 5th pick position, Ekeler is also great...'")
    print("               └── Remembers context without being told again!")


def main():
    """Main entry point for multi-turn demo."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Turn Conversation Demo")
    parser.add_argument("--concept", action="store_true", 
                       help="Show concept diagram only")
    parser.add_argument("--example", action="store_true", 
                       help="Show annotated example")
    parser.add_argument("--comparison", action="store_true", 
                       help="Show single vs multi-turn comparison")
    parser.add_argument("--live", action="store_true", 
                       help="Run live scenario demo")
    
    args = parser.parse_args()
    
    if args.concept:
        print(create_multi_turn_diagram("Demo Scenario"))
    elif args.example:
        print(create_context_highlight_example())
    elif args.comparison:
        run_comparison_demo()
    elif args.live:
        runner = ScenarioRunner()
        runner.run_scenario("scenario_1", verbose=True)
    else:
        # Run full demo
        run_multi_turn_demo()


if __name__ == "__main__":
    main() 