"""
Core Fantasy Draft Agent using any-agent framework.
Supports multi-turn conversations and maintains draft state.
"""

import os
from typing import List, Dict, Optional, Annotated
from dotenv import load_dotenv
from any_agent import AnyAgent, AgentConfig
from .data import TOP_PLAYERS, get_player_info, get_best_available, get_players_by_position

# Load environment variables from .env file
load_dotenv()


class FantasyDraftAgent:
    def __init__(self, framework: str = "tinyagent", model_id: str = "gpt-4o-mini"):
        """Initialize the Fantasy Draft Agent."""
        self.framework = framework
        self.model_id = model_id
        
        # Draft state management
        self.draft_state = {
            "my_picks": [],
            "all_picks": [],
            "round": 1,
            "pick_number": 5,  # Default to 5th pick
            "league_size": 12,
            "roster_needs": {
                "QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1
            },
            "conversation_history": []
        }
        
        # Initialize the agent with tools
        self.agent = AnyAgent.create(
            framework,
            AgentConfig(
                model_id=model_id,
                instructions=self._get_instructions(),
                tools=[
                    self._get_player_stats,
                    self._check_best_available,
                    self._analyze_position_scarcity,
                    self._get_team_stack_options,
                ],
                model_args={"temperature": 0.7}
            )
        )
    
    def _get_instructions(self) -> str:
        """Get the agent's system instructions."""
        return """You are an expert fantasy football draft assistant with deep knowledge of:
        - Player values, tiers, and ADP (Average Draft Position)
        - Draft strategy (Zero RB, Hero RB, Robust RB, etc.)
        - Position scarcity and value-based drafting
        - Team stacking strategies
        - Injury concerns and player situations
        
        Your role is to:
        1. Provide draft advice based on the current situation
        2. Remember previous picks and conversations in the draft
        3. Adapt strategy based on how the draft unfolds
        4. Explain your reasoning clearly
        5. Consider both floor and ceiling when recommending players
        
        Always maintain context from previous turns in our conversation.
        Reference specific players and situations we've discussed.
        Be conversational but authoritative in your recommendations."""
    
    def _get_player_stats(
        self,
        player_name: Annotated[str, "The name of the player to look up"]
    ) -> str:
        """Get detailed stats for a specific player."""
        info = get_player_info(player_name)
        if not info:
            return f"No data found for {player_name}"
        
        return (f"{player_name} ({info['pos']}, {info['team']}) - "
                f"ADP: {info['adp']}, Tier: {info['tier']}, "
                f"2023 PPG: {info['ppg_2023']}")
    
    def _check_best_available(
        self,
        position: Annotated[Optional[str], "Position to filter by (RB, WR, QB, TE)"] = None
    ) -> str:
        """Check the best available player overall or by position."""
        best = get_best_available(self.draft_state["all_picks"], position)
        if not best or not best[0]:
            pos_str = f" at {position}" if position else ""
            return f"No players available{pos_str}"
        
        name, info = best
        return (f"Best available{' ' + position if position else ''}: "
                f"{name} ({info['pos']}, {info['team']}) - "
                f"ADP: {info['adp']}, Tier: {info['tier']}, "
                f"2023 PPG: {info['ppg_2023']}")
    
    def _analyze_position_scarcity(
        self,
        position: Annotated[str, "Position to analyze (RB, WR, QB, TE)"]
    ) -> str:
        """Analyze scarcity at a position based on remaining players."""
        available = get_players_by_position(position)
        drafted = [p for p in self.draft_state["all_picks"] if p in available]
        remaining = len(available) - len(drafted)
        
        # Count by tier
        tier_counts = {}
        for name, info in available.items():
            if name not in drafted:
                tier = info['tier']
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        analysis = f"Position analysis for {position}:\n"
        analysis += f"Total remaining: {remaining}\n"
        for tier in sorted(tier_counts.keys()):
            analysis += f"Tier {tier}: {tier_counts[tier]} players\n"
        
        return analysis
    
    def _get_team_stack_options(
        self,
        team: Annotated[str, "Team abbreviation (e.g., KC, BUF, MIA)"]
    ) -> str:
        """Get stacking options for a specific team."""
        team_players = {name: info for name, info in TOP_PLAYERS.items() 
                       if info.get('team') == team and name not in self.draft_state["all_picks"]}
        
        if not team_players:
            return f"No available players from {team}"
        
        result = f"Available {team} players for stacking:\n"
        for name, info in sorted(team_players.items(), key=lambda x: x[1]['adp']):
            result += f"- {name} ({info['pos']}) - ADP: {info['adp']}\n"
        
        return result
    
    def update_draft_state(self, pick: str, is_my_pick: bool = False):
        """Update the draft state with a new pick."""
        self.draft_state["all_picks"].append(pick)
        if is_my_pick:
            self.draft_state["my_picks"].append(pick)
        
        # Update round
        total_picks = len(self.draft_state["all_picks"])
        self.draft_state["round"] = (total_picks // self.draft_state["league_size"]) + 1
    
    def run(self, prompt: str, maintain_context: bool = True) -> str:
        """Run the agent with a prompt, maintaining conversation context."""
        # Build context from previous conversation if needed
        if maintain_context and self.draft_state["conversation_history"]:
            context = self._build_conversation_context()
            full_prompt = f"{context}\n\nCurrent message: {prompt}"
        else:
            full_prompt = prompt
        
        # Add current draft state to prompt
        draft_context = self._build_draft_context()
        full_prompt = f"{draft_context}\n\n{full_prompt}"
        
        # Run the agent
        trace = self.agent.run(full_prompt)
        
        # Store conversation turn
        self.draft_state["conversation_history"].append({
            "user": prompt,
            "agent": trace.final_output
        })
        
        return trace.final_output
    
    def _build_conversation_context(self) -> str:
        """Build context from conversation history."""
        if not self.draft_state["conversation_history"]:
            return ""
        
        context = "Previous conversation:\n"
        # Include last 3 exchanges for context
        recent_history = self.draft_state["conversation_history"][-3:]
        for turn in recent_history:
            context += f"User: {turn['user']}\n"
            context += f"Assistant: {turn['agent']}\n\n"
        
        return context
    
    def _build_draft_context(self) -> str:
        """Build context about current draft state."""
        context = f"Current draft state:\n"
        context += f"Round: {self.draft_state['round']}\n"
        context += f"Your pick number: {self.draft_state['pick_number']}\n"
        
        if self.draft_state["my_picks"]:
            context += f"Your picks: {', '.join(self.draft_state['my_picks'])}\n"
        
        if self.draft_state["all_picks"]:
            recent_picks = self.draft_state["all_picks"][-5:]
            context += f"Recent picks: {', '.join(recent_picks)}\n"
        
        return context
    
    def reset_draft(self):
        """Reset the draft state for a new draft."""
        self.draft_state = {
            "my_picks": [],
            "all_picks": [],
            "round": 1,
            "pick_number": 5,
            "league_size": 12,
            "roster_needs": {
                "QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1
            },
            "conversation_history": []
        }


# Simple test function
def test_agent():
    """Test the fantasy draft agent."""
    agent = FantasyDraftAgent()
    
    # Test basic question
    response = agent.run("What are the top 3 RBs available?")
    print("Agent:", response)
    print("\n" + "="*50 + "\n")
    
    # Test multi-turn conversation
    response = agent.run("I have the 5th pick. The first 4 picks were McCaffrey, Jefferson, Lamb, and Hill. What should I do?")
    print("Agent:", response)
    print("\n" + "="*50 + "\n")
    
    # Follow-up that should remember context
    response = agent.run("What about taking a WR instead?")
    print("Agent:", response)


if __name__ == "__main__":
    test_agent()
