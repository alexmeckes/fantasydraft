"""
Fantasy Draft Agent Demo - Main entry point.
Run demonstrations of the any-agent powered fantasy draft assistant.
"""

import os
import sys
from typing import Dict, List
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import FantasyDraftAgent
from core.scenarios import ScenarioRunner, SCENARIOS
from core.visualizer import (
    create_player_card, 
    create_comparison_card,
    create_roster_summary,
    create_multi_turn_flow,
    create_scenario_result
)

# Load environment variables from .env file
load_dotenv()


class FantasyDraftDemo:
    """Main demo class for Fantasy Draft Agent."""
    
    def __init__(self):
        self.agent = FantasyDraftAgent()
        self.scenario_runner = ScenarioRunner()
    
    def interactive_demo(self):
        """Run an interactive demo where users can ask questions."""
        print("\n" + "="*60)
        print("🏈 FANTASY DRAFT AGENT - INTERACTIVE MODE")
        print("="*60)
        print("\nI'm your AI fantasy draft assistant powered by any-agent!")
        print("Ask me anything about your draft strategy.\n")
        print("Commands:")
        print("  - Type your question to get draft advice")
        print("  - Type 'pick <player>' to make a pick")
        print("  - Type 'roster' to see your current roster")
        print("  - Type 'reset' to start a new draft")
        print("  - Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("\nGood luck with your draft! 🏆")
                    break
                
                elif user_input.lower() == 'reset':
                    self.agent.reset_draft()
                    print("\nDraft reset! Starting fresh.\n")
                
                elif user_input.lower() == 'roster':
                    print(create_roster_summary(self.agent.draft_state["my_picks"]))
                
                elif user_input.lower().startswith('pick '):
                    player = user_input[5:].strip()
                    self.agent.update_draft_state(player, is_my_pick=True)
                    print(f"\n✅ You drafted {player}!")
                    print(create_player_card(player))
                
                else:
                    response = self.agent.run(user_input)
                    print(f"\nAgent: {response}\n")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
    
    def scenario_demo(self, scenario_id: str = None):
        """Run a specific scenario or all scenarios."""
        if scenario_id:
            if scenario_id not in SCENARIOS:
                print(f"Unknown scenario: {scenario_id}")
                print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
                return
            
            print(f"\nRunning scenario: {scenario_id}")
            conversation = self.scenario_runner.run_scenario(scenario_id, verbose=True)
            
            # Show conversation flow visualization
            print("\n" + create_multi_turn_flow(conversation))
            
            # Export transcript
            transcript = self.scenario_runner.export_scenario_transcript(scenario_id, conversation)
            filename = f"scenario_{scenario_id}_transcript.md"
            with open(filename, 'w') as f:
                f.write(transcript)
            print(f"Transcript saved to: {filename}")
        
        else:
            # Run all scenarios
            print("\n🎬 Running all demo scenarios...\n")
            results = self.scenario_runner.run_all_scenarios()
            
            # Save all transcripts
            for scenario_id, conversation in results.items():
                transcript = self.scenario_runner.export_scenario_transcript(scenario_id, conversation)
                filename = f"scenario_{scenario_id}_transcript.md"
                with open(filename, 'w') as f:
                    f.write(transcript)
            
            print(f"\nAll {len(results)} scenarios completed!")
            print("Transcripts saved to scenario_*_transcript.md files")
    
    def quick_demo(self):
        """Run a quick demonstration of key features."""
        print("\n" + "="*60)
        print("🏈 FANTASY DRAFT AGENT - QUICK DEMO")
        print("="*60)
        
        # Demo 1: Basic question
        print("\n1️⃣ Basic Draft Question:")
        print("User: What are the top 3 RBs available?")
        response = self.agent.run("What are the top 3 RBs available?")
        print(f"Agent: {response}")
        
        # Demo 2: Contextual advice
        print("\n\n2️⃣ Contextual Draft Advice:")
        print("User: I have the 5th pick. McCaffrey, Jefferson, Lamb, and Hill are gone. Help!")
        response = self.agent.run("I have the 5th pick. McCaffrey, Jefferson, Lamb, and Hill are gone. Help!")
        print(f"Agent: {response}")
        
        # Demo 3: Multi-turn conversation
        print("\n\n3️⃣ Multi-turn Conversation (Context Retention):")
        print("User: What about taking Ekeler instead?")
        response = self.agent.run("What about taking Ekeler instead?")
        print(f"Agent: {response}")
        
        # Demo 4: Player comparison
        print("\n\n4️⃣ Player Comparison Visual:")
        print(create_comparison_card("Bijan Robinson", "Austin Ekeler"))
        
        print("\n✅ Quick demo complete!")
        print("Try 'python demo.py --interactive' for interactive mode")
        print("Or 'python demo.py --scenario 1' to run specific scenarios")
    
    def test_installation(self):
        """Test that everything is installed correctly."""
        print("\n🔧 Testing Fantasy Draft Agent Installation...")
        
        try:
            # Test imports
            print("✓ Core modules imported successfully")
            
            # Test agent creation
            test_agent = FantasyDraftAgent()
            print("✓ Agent created successfully")
            
            # Test basic query
            response = test_agent.run("Test query", maintain_context=False)
            print("✓ Agent responds to queries")
            
            # Test data access
            from core.data import TOP_PLAYERS
            print(f"✓ Player database loaded ({len(TOP_PLAYERS)} players)")
            
            # Test visualization
            card = create_player_card("Christian McCaffrey")
            print("✓ Visualization components working")
            
            print("\n✅ All tests passed! The agent is ready to use.")
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nPlease make sure you've installed dependencies:")
            print("  pip install -r requirements.txt")
            return False


def main():
    """Main entry point for the demo."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fantasy Draft Agent Demo")
    parser.add_argument("--test", action="store_true", help="Test installation")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    parser.add_argument("--scenario", type=str, help="Run specific scenario (1-4)")
    parser.add_argument("--all-scenarios", action="store_true", help="Run all scenarios")
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set it using: export OPENAI_API_KEY='your-key-here'")
        print("Or create a .env file with: OPENAI_API_KEY=your-key-here\n")
    
    demo = FantasyDraftDemo()
    
    if args.test:
        demo.test_installation()
    elif args.interactive:
        demo.interactive_demo()
    elif args.scenario:
        demo.scenario_demo(f"scenario_{args.scenario}")
    elif args.all_scenarios:
        demo.scenario_demo()
    elif args.quick:
        demo.quick_demo()
    else:
        # Default: show options
        print("\n🏈 Fantasy Draft Agent powered by any-agent")
        print("\nUsage:")
        print("  python demo.py --test          # Test installation")
        print("  python demo.py --quick         # Quick demonstration")
        print("  python demo.py --interactive   # Interactive draft mode")
        print("  python demo.py --scenario 1    # Run scenario 1")
        print("  python demo.py --all-scenarios # Run all scenarios")
        print("\nRunning quick demo by default...\n")
        demo.quick_demo()


if __name__ == "__main__":
    main()
