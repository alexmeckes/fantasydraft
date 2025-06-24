"""
Pre-crafted demo scenarios for Fantasy Draft Agent.
Each scenario showcases different multi-turn conversation capabilities.
"""

from agent import FantasyDraftAgent
from typing import List, Dict


# Define our demo scenarios
SCENARIOS = {
    "scenario_1": {
        "name": "The Opening Pick",
        "description": "User has 5th pick, top 4 RBs are gone. Shows strategy adaptation.",
        "setup": {
            "pick_number": 5,
            "drafted_players": ["Christian McCaffrey", "Justin Jefferson", "CeeDee Lamb", "Tyreek Hill"]
        },
        "conversation": [
            {
                "user": "I have the 5th pick and the top 4 guys are gone - McCaffrey, Jefferson, Lamb, and Hill. What should I do?",
                "showcases": "Initial situation assessment"
            },
            {
                "user": "I'm worried about Bijan being a rookie. What about Ekeler instead?",
                "showcases": "Addressing specific concerns"
            },
            {
                "user": "Good point about the Chargers offense. Who would you pair with him in round 2?",
                "showcases": "Building on previous context"
            }
        ]
    },
    
    "scenario_2": {
        "name": "The Position Run", 
        "description": "Round 3, all QBs being drafted. Shows patience and value finding.",
        "setup": {
            "pick_number": 8,
            "round": 3,
            "my_picks": ["Ja'Marr Chase", "Nick Chubb"],
            "recent_picks": ["Josh Allen", "Patrick Mahomes", "Jalen Hurts", "Lamar Jackson"]
        },
        "conversation": [
            {
                "user": "Everyone is taking QBs! Allen, Mahomes, Hurts, and Lamar just went. Should I panic and grab one?",
                "showcases": "Handling draft runs"
            },
            {
                "user": "You're right about value. Who's the best player available regardless of position?",
                "showcases": "Pivoting strategy based on advice"
            },
            {
                "user": "I took A.J. Brown. When should I actually target a QB then?",
                "showcases": "Long-term planning with context"
            },
            {
                "user": "Makes sense. What late-round QBs pair well with the Eagles offense?",
                "showcases": "Advanced strategy (stacking)"
            }
        ]
    },
    
    "scenario_3": {
        "name": "The Sleeper Question",
        "description": "Round 10, looking for upside. Shows deep knowledge + context.",
        "setup": {
            "pick_number": 3,
            "round": 10,
            "my_picks": ["Justin Jefferson", "Tony Pollard", "Mark Andrews", "Chris Olave", 
                         "Amari Cooper", "Dak Prescott", "Kenneth Walker", "Terry McLaurin", "George Kittle"]
        },
        "conversation": [
            {
                "user": "Round 10 now. I need some upside guys. Who are your favorite sleepers?",
                "showcases": "Late-round strategy shift"
            },
            {
                "user": "I like the Vikings connection with Jefferson. Tell me more about Addison.",
                "showcases": "Building on roster construction"
            },
            {
                "user": "Sold! I grabbed him. Now I need a backup RB with upside.",
                "showcases": "Continuing roster building"
            }
        ]
    },
    
    "scenario_4": {
        "name": "The Stack Builder",
        "description": "Has Mahomes, wants receivers. Shows correlation strategy.",
        "setup": {
            "pick_number": 10,
            "round": 5,
            "my_picks": ["Saquon Barkley", "Davante Adams", "Patrick Mahomes", "Breece Hall"]
        },
        "conversation": [
            {
                "user": "I've got Mahomes. Should I try to get Kelce or a Chiefs WR to stack?",
                "showcases": "Stack strategy introduction"
            },
            {
                "user": "Kelce went right before my pick! What Chiefs WRs are worth targeting?",
                "showcases": "Adapting to changing circumstances"
            },
            {
                "user": "When do you think I should target one of them? This pick or wait?",
                "showcases": "Timing decisions with context"
            }
        ]
    }
}


class ScenarioRunner:
    """Run and manage demo scenarios."""
    
    def __init__(self):
        self.agent = FantasyDraftAgent()
    
    def setup_scenario(self, scenario_id: str):
        """Set up the agent with scenario-specific state."""
        scenario = SCENARIOS[scenario_id]
        setup = scenario["setup"]
        
        # Reset agent
        self.agent.reset_draft()
        
        # Apply setup
        if "pick_number" in setup:
            self.agent.draft_state["pick_number"] = setup["pick_number"]
        
        if "round" in setup:
            self.agent.draft_state["round"] = setup["round"]
        
        if "drafted_players" in setup:
            for player in setup["drafted_players"]:
                self.agent.update_draft_state(player)
        
        if "my_picks" in setup:
            self.agent.draft_state["my_picks"] = setup["my_picks"]
            # Add to all picks
            for pick in setup["my_picks"]:
                if pick not in self.agent.draft_state["all_picks"]:
                    self.agent.draft_state["all_picks"].append(pick)
        
        if "recent_picks" in setup:
            for pick in setup["recent_picks"]:
                if pick not in self.agent.draft_state["all_picks"]:
                    self.agent.update_draft_state(pick)
    
    def run_scenario(self, scenario_id: str, verbose: bool = True) -> List[Dict]:
        """Run a complete scenario and return the conversation."""
        scenario = SCENARIOS[scenario_id]
        self.setup_scenario(scenario_id)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Scenario: {scenario['name']}")
            print(f"Description: {scenario['description']}")
            print(f"{'='*60}\n")
        
        conversation_log = []
        
        for i, turn in enumerate(scenario["conversation"], 1):
            if verbose:
                # Visual indicator for turn number
                print(f"\n{'━'*60}")
                print(f"🔄 TURN {i} - {turn['showcases']}")
                print(f"{'━'*60}")
                
                # Show conversation memory state
                if i > 1:
                    print(f"💭 AGENT MEMORY: Remembering {len(self.agent.draft_state['conversation_history'])} previous exchanges")
                    last_topic = self.agent.draft_state['conversation_history'][-1]['user'] if self.agent.draft_state['conversation_history'] else ""
                    if last_topic:
                        print(f"📌 Last discussed: '{last_topic[:50]}...'")
                
                print(f"\n👤 User: {turn['user']}")
            
            response = self.agent.run(turn["user"])
            
            if verbose:
                print(f"\n🤖 Agent: {response}")
                
                # Highlight context references
                context_indicators = [
                    "you mentioned", "you said", "earlier", "before", 
                    "as I mentioned", "like we discussed", "you asked about",
                    "regarding your", "based on your", "given that you"
                ]
                
                # Check if response references previous context
                response_lower = response.lower()
                context_found = any(indicator in response_lower for indicator in context_indicators)
                
                if context_found:
                    print(f"\n✨ CONTEXT RETENTION: Agent referenced previous conversation!")
                
                print(f"\n{'-'*40}")
            
            conversation_log.append({
                "turn": i,
                "showcases": turn["showcases"],
                "user": turn["user"],
                "agent": response,
                "context_retained": context_found if verbose else False
            })
        
        return conversation_log
    
    def run_all_scenarios(self) -> Dict[str, List[Dict]]:
        """Run all scenarios and return results."""
        results = {}
        
        for scenario_id in SCENARIOS:
            print(f"\nRunning {scenario_id}...")
            results[scenario_id] = self.run_scenario(scenario_id)
        
        return results
    
    def export_scenario_transcript(self, scenario_id: str, conversation_log: List[Dict]) -> str:
        """Export a scenario as a formatted transcript."""
        scenario = SCENARIOS[scenario_id]
        
        transcript = f"# {scenario['name']}\n\n"
        transcript += f"**Scenario**: {scenario['description']}\n\n"
        
        for turn in conversation_log:
            transcript += f"### Turn {turn['turn']}: {turn['showcases']}\n\n"
            transcript += f"**User**: {turn['user']}\n\n"
            transcript += f"**Agent**: {turn['agent']}\n\n"
            transcript += "---\n\n"
        
        return transcript


def demo_scenarios():
    """Run a demo of all scenarios."""
    runner = ScenarioRunner()
    
    # Run scenario 1 as a detailed example
    print("\n" + "="*60)
    print("FANTASY DRAFT AGENT - DEMO SCENARIOS")
    print("="*60)
    
    # Run just the first scenario in detail
    conversation = runner.run_scenario("scenario_1", verbose=True)
    
    # Show how to export
    transcript = runner.export_scenario_transcript("scenario_1", conversation)
    print("\nExported Transcript Preview:")
    print(transcript[:500] + "...")
    
    print("\n\nTo run all scenarios:")
    print(">>> runner.run_all_scenarios()")


if __name__ == "__main__":
    demo_scenarios()
