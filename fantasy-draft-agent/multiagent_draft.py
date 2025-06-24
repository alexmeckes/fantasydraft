#!/usr/bin/env python3
"""
Multi-Agent Mock Draft Implementation
Demonstrates A2A communication and multi-turn memory
"""

import time
from typing import Dict, List, Tuple, Optional
from agent import FantasyDraftAgent
from data import TOP_PLAYERS, get_best_available, get_players_by_position
import random


class DraftAgent:
    """Base class for draft agents with specific strategies."""
    
    def __init__(self, team_name: str, strategy: str, color: str, icon: str):
        self.team_name = team_name
        self.strategy = strategy
        self.color = color
        self.icon = icon
        self.agent = FantasyDraftAgent()
        self.picks = []
        self.conversation_memory = []
        
    def remember_conversation(self, speaker: str, message: str):
        """Store conversation in memory."""
        self.conversation_memory.append({
            "speaker": speaker,
            "message": message,
            "timestamp": time.time()
        })
    
    def make_pick(self, available_players: List[str], draft_board: Dict) -> Tuple[str, str]:
        """Make a pick based on strategy. Returns (player, reasoning)."""
        # This will be overridden by specific agent types
        pass
    
    def comment_on_pick(self, team: str, player: str, player_info: Dict) -> Optional[str]:
        """Generate commentary on another team's pick using LLM."""
        # Build context for the LLM
        context = f"""You are {self.team_name}, a fantasy football team manager following a {self.strategy}.
Your picks so far: {', '.join(self.picks) if self.picks else 'None yet'}

{team} just picked {player} ({player_info['pos']}, ADP: {player_info['adp']}, Tier: {player_info['tier']}).

Based on your strategy and the current draft situation, provide a short, natural comment on this pick. 
Be competitive and show some personality - you can be critical, sarcastic, or dismissive if the pick doesn't align with your philosophy.
Don't be overly nice. This is a competitive draft and you want to win. Show confidence in your strategy.
Keep it under 2 sentences and make it feel like real draft room banter - trash talk is encouraged!"""

        response = self.agent.run(context)
        return response.strip()
    
    def respond_to_comment(self, commenter: str, comment: str) -> Optional[str]:
        """Respond to another agent's comment using LLM."""
        # Build conversation context
        recent_memory = self.conversation_memory[-5:] if len(self.conversation_memory) > 5 else self.conversation_memory
        
        context = f"""You are {self.team_name}, following a {self.strategy} in a fantasy draft.
Your picks: {', '.join(self.picks) if self.picks else 'None yet'}

{commenter} just said to you: "{comment}"

Recent conversation history:
{chr(10).join([f"- {m['speaker']}: {m['message']}" for m in recent_memory])}

Respond naturally and briefly (1-2 sentences). Be competitive and defend your strategy aggressively.
You can be sarcastic, dismissive, or fire back with your own trash talk. This is a competition!
Don't be polite - show confidence and give as good as you get."""

        response = self.agent.run(context)
        return response.strip()


class ZeroRBAgent(DraftAgent):
    """Agent that follows Zero RB strategy."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Zero RB Strategy", "#E3F2FD", "📘")
    
    def make_pick(self, available_players: List[str], draft_board: Dict) -> Tuple[str, str]:
        # Prioritize WRs in early rounds
        round_num = len(self.picks) + 1
        
        if round_num <= 3:
            # Get best available WR
            best_wrs = [(p, info) for p, info in TOP_PLAYERS.items() 
                       if p in available_players and info['pos'] == 'WR']
            if best_wrs:
                best_wrs.sort(key=lambda x: x[1]['adp'])
                player = best_wrs[0][0]
                player_info = best_wrs[0][1]
                
                # Generate dynamic reasoning using LLM
                context = f"""You are {self.team_name} following a Zero RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}

You're selecting {player} (WR, {player_info['team']}, ADP: {player_info['adp']}).

Explain your pick in 1-2 sentences, emphasizing why this fits your Zero RB strategy. 
Be confident and maybe a bit cocky about avoiding RBs. Take subtle shots at teams loading up on injury-prone RBs.
Show personality - you KNOW your strategy is superior."""
                
                reasoning = self.agent.run(context).strip()
                return player, reasoning
        
        # Later rounds, grab RBs
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        if best_available:
            player = best_available[0][0]
            player_info = best_available[0][1]
            pos = player_info['pos']
            
            context = f"""You are {self.team_name} following a Zero RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks)}

You're selecting {player} ({pos}, {player_info['team']}, ADP: {player_info['adp']}).

Explain why you're taking this player now, given your Zero RB approach.
If it's a RB, explain why NOW is the right time (while others reached early). 
Be smug about getting value while others panicked. Keep it to 1-2 sentences with attitude."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Hmm, slim pickings here..."
    



class BPAAgent(DraftAgent):
    """Agent that follows Best Player Available strategy."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Best Player Available", "#E8F5E9", "📗")
    
    def make_pick(self, available_players: List[str], draft_board: Dict) -> Tuple[str, str]:
        # Simply take the best available by ADP
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        if best_available:
            player = best_available[0][0]
            player_info = best_available[0][1]
            pos = player_info['pos']
            
            # Generate dynamic reasoning using LLM
            context = f"""You are {self.team_name} following a Best Player Available strategy.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}
Round: {len(self.picks) + 1}

You're selecting {player} ({pos}, {player_info['team']}, ADP: {player_info['adp']}).

Explain why this is the best value pick available. Focus on their ranking/ADP value.
Be condescending about other teams reaching for needs or following rigid strategies.
You're the smart one taking the obvious value - let them know it. Keep it to 1-2 sentences."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Taking the best available..."
    



class RobustRBAgent(DraftAgent):
    """Agent that follows Robust RB strategy."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Robust RB Strategy", "#FFF3E0", "📙")
    
    def make_pick(self, available_players: List[str], draft_board: Dict) -> Tuple[str, str]:
        # Prioritize RBs early
        round_num = len(self.picks) + 1
        
        if round_num <= 2:
            # Get best available RB
            best_rbs = [(p, info) for p, info in TOP_PLAYERS.items() 
                       if p in available_players and info['pos'] == 'RB']
            if best_rbs:
                best_rbs.sort(key=lambda x: x[1]['adp'])
                player = best_rbs[0][0]
                player_info = best_rbs[0][1]
                
                context = f"""You are {self.team_name} following a Robust RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}

You're selecting {player} (RB, {player_info['team']}, ADP: {player_info['adp']}).

Explain why this RB is crucial for your Robust RB strategy. Be aggressive about RBs winning championships.
Mock teams that are going WR-heavy. You're building a REAL team with a strong foundation.
Be old-school and dismissive of "fancy" WR strategies. Keep it to 1-2 sentences with authority."""
                
                reasoning = self.agent.run(context).strip()
                return player, reasoning
        
        # Best available after that
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        if best_available:
            player = best_available[0][0]
            player_info = best_available[0][1]
            
            context = f"""You are {self.team_name} following a Robust RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks)}

You're selecting {player} ({player_info['pos']}, {player_info['team']}, ADP: {player_info['adp']}).

Explain how this pick fits with your RB-heavy build. If it's not a RB, grudgingly admit you need other positions too.
But emphasize your RB foundation is what matters. Be dismissive of WR-first teams. Keep it to 1-2 sentences."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Building around my RBs..."


class UpsideAgent(DraftAgent):
    """Agent that hunts for upside/breakout players."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Upside Hunter", "#FFFDE7", "📓")
    
    def make_pick(self, available_players: List[str], draft_board: Dict) -> Tuple[str, str]:
        # Look for high upside players
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        # Sometimes reach for upside
        if len(best_available) > 3 and random.random() > 0.5:
            # Take someone a bit later for "upside"
            player = best_available[2][0]  # Skip top 2, take 3rd
            player_info = best_available[2][1]
            
            context = f"""You are {self.team_name}, an Upside Hunter who looks for breakout potential.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}
Round: {len(self.picks) + 1}

You're reaching slightly for {player} ({player_info['pos']}, {player_info['team']}, ADP: {player_info['adp']}).

Explain why you see breakout/league-winning potential in this player. Be enthusiastic about their upside.
Mock the "safe" picks others are making. You're here to WIN, not finish 4th! 
Championships require RISK! Keep it to 1-2 sentences with swagger."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
            
        elif best_available:
            player = best_available[0][0]
            player_info = best_available[0][1]
            
            context = f"""You are {self.team_name}, an Upside Hunter who looks for league-winners.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}
Round: {len(self.picks) + 1}

You're selecting {player} ({player_info['pos']}, {player_info['team']}, ADP: {player_info['adp']}).

Explain what upside or potential you see in this player. Focus on ceiling over floor.
Be dismissive of "safe" boring picks. You're building a championship roster, not a participation trophy team!
Keep it to 1-2 sentences with confidence."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Going for the home run pick..."


class UserAdvisorAgent(DraftAgent):
    """Agent that advises the user during their picks."""
    
    def __init__(self):
        super().__init__("Your Advisor", "Strategic Advisor", "#FFEBEE", "📕")
        self.user_picks = []
    
    def advise_user(self, available_players: List[str], draft_board: Dict, 
                    other_agents_strategies: Dict[str, str]) -> str:
        """Provide advice to the user based on the draft flow."""
        # Count the actual round based on total picks made
        total_picks = sum(len(picks) for picks in draft_board.values())
        round_num = (total_picks // 6) + 1  # 6 teams per round
        
        # Get best available by position
        best_by_pos = {}
        for pos in ['RB', 'WR', 'QB', 'TE']:
            candidates = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players and info['pos'] == pos]
            if candidates:
                candidates.sort(key=lambda x: x[1]['adp'])
                best_by_pos[pos] = candidates[0]
        
        # Get user's current roster
        user_picks = self.user_picks
        user_rbs = [p for p in user_picks if TOP_PLAYERS.get(p, {}).get('pos') == 'RB']
        user_wrs = [p for p in user_picks if TOP_PLAYERS.get(p, {}).get('pos') == 'WR']
        
        # Analyze what other teams have been doing
        other_picks_summary = []
        for team, picks in draft_board.items():
            if picks and team != 4:  # Not the user
                recent_pick = picks[-1] if picks else None
                if recent_pick and recent_pick in TOP_PLAYERS:
                    other_picks_summary.append(f"Team {team} ({other_agents_strategies.get(f'Team {team}', 'Unknown')}): {recent_pick}")
        
        # Build context for LLM
        context = f"""You are an expert fantasy football advisor helping the user in round {round_num} of their draft.

User's current roster:
- RBs: {', '.join(user_rbs) if user_rbs else 'None'}
- WRs: {', '.join(user_wrs) if user_wrs else 'None'}

Top available players:
- Best RB: {best_by_pos.get('RB', [None])[0]} (ADP: {best_by_pos.get('RB', [None, {'adp': 'N/A'}])[1]['adp']})
- Best WR: {best_by_pos.get('WR', [None])[0]} (ADP: {best_by_pos.get('WR', [None, {'adp': 'N/A'}])[1]['adp']})
- Best QB: {best_by_pos.get('QB', [None])[0]} (ADP: {best_by_pos.get('QB', [None, {'adp': 'N/A'}])[1]['adp']})
- Best TE: {best_by_pos.get('TE', [None])[0]} (ADP: {best_by_pos.get('TE', [None, {'adp': 'N/A'}])[1]['adp']})

Recent picks by other teams:
{chr(10).join(other_picks_summary[-3:]) if other_picks_summary else 'None yet'}

Other team strategies: {', '.join([f"{t}: {s}" for t, s in other_agents_strategies.items()])}

Provide strategic advice for the user's pick. Consider:
1. Their roster needs
2. Best available value
3. What other teams are doing
4. Position scarcity

Format as: 🎯 **Round {round_num} Advice** followed by 2-3 bullet points with specific player recommendations and reasoning.
Keep it concise but insightful."""
        
        advice = self.agent.run(context).strip()
        return advice


class CommissionerAgent:
    """Agent that manages the draft flow and announcements."""
    
    def __init__(self):
        self.icon = "📜"
        self.color = "#FFF8E1"
        self.draft_log = []
    
    def announce_pick(self, round_num: int, pick_num: int, team: str) -> str:
        """Announce who's on the clock."""
        return f"**Round {round_num}, Pick {pick_num}** - {team} is on the clock!"
    
    def confirm_pick(self, team: str, player: str, pick_num: int) -> str:
        """Confirm a pick was made."""
        self.draft_log.append({
            "pick_num": pick_num,
            "team": team,
            "player": player
        })
        return f"With pick #{pick_num}, {team} selects **{player}**!"
    
    def announce_round_end(self, round_num: int) -> str:
        """Announce end of round."""
        return f"🏁 **End of Round {round_num}**"


class MultiAgentMockDraft:
    """Orchestrates the multi-agent mock draft."""
    
    def __init__(self, user_pick_position: int = 4):
        # Initialize agents
        self.agents = {
            1: ZeroRBAgent("Team 1"),
            2: BPAAgent("Team 2"), 
            3: RobustRBAgent("Team 3"),
            5: UpsideAgent("Team 5")
        }
        
        self.user_position = user_pick_position
        self.user_advisor = UserAdvisorAgent()
        self.commissioner = CommissionerAgent()
        
        # Draft state
        self.draft_board = {i: [] for i in range(1, 7) if i != user_pick_position}
        self.draft_board[user_pick_position] = []  # User's picks
        
        # Add Team 6 as an AI agent since user is at position 4
        if 6 not in self.agents and user_pick_position != 6:
            self.agents[6] = BPAAgent("Team 6")
        
        self.all_picks = []
        
        # Conversation log for visualization
        self.conversation_log = []
    
    def add_to_conversation(self, speaker: str, recipient: str, message: str, 
                          message_type: str = "comment"):
        """Add a message to the conversation log."""
        self.conversation_log.append({
            "speaker": speaker,
            "recipient": recipient,
            "message": message,
            "type": message_type,
            "timestamp": time.time()
        })
    
    def get_available_players(self) -> List[str]:
        """Get list of available players."""
        all_picked = [p for picks in self.draft_board.values() for p in picks]
        return [p for p in TOP_PLAYERS.keys() if p not in all_picked]
    
    def format_message(self, agent, recipient: str, message: str) -> str:
        """Format a message with agent styling."""
        if hasattr(agent, 'icon'):
            if recipient == "ALL":
                return f"{agent.icon} **{agent.team_name}**: {message}"
            else:
                return f"{agent.icon} **{agent.team_name}** → {recipient}: {message}"
        else:
            # Commissioner
            return f"{agent.icon} **COMMISSIONER**: {message}"
    
    def simulate_draft_turn(self, round_num: int, pick_num: int, team_num: int) -> List[str]:
        """Simulate one pick in the draft. Returns formatted messages."""
        messages = []
        
        # Commissioner announces pick
        announce_msg = self.commissioner.announce_pick(round_num, pick_num, f"Team {team_num}")
        messages.append(("commissioner", "ALL", announce_msg))
        
        if team_num == self.user_position:
            # User's turn - get advice
            available = self.get_available_players()
            strategies = {f"Team {i}": agent.strategy for i, agent in self.agents.items()}
            
            advice = self.user_advisor.advise_user(available, self.draft_board, strategies)
            messages.append(("advisor", "USER", advice))
            
            # Return messages and wait for user input
            return messages, None  # None indicates waiting for user
        
        else:
            # AI agent's turn
            agent = self.agents.get(team_num)
            if not agent:
                # Create a temporary BPA agent for this team
                agent = BPAAgent(f"Team {team_num}")
                self.agents[team_num] = agent
            
            available = self.get_available_players()
            
            # Agent makes pick
            player, reasoning = agent.make_pick(available, self.draft_board)
            
            # Update draft board
            self.draft_board[team_num].append(player)
            agent.picks.append(player)
            self.all_picks.append((team_num, player))
            
            # Announce pick
            confirm_msg = self.commissioner.confirm_pick(agent.team_name, player, pick_num)
            messages.append(("commissioner", "ALL", confirm_msg))
            
            # Agent explains pick
            messages.append((agent, "ALL", reasoning))
            
            # Other agents might comment
            if player in TOP_PLAYERS:
                player_info = TOP_PLAYERS[player]
                
                for other_num, other_agent in self.agents.items():
                    if other_num != team_num:
                        comment = other_agent.comment_on_pick(agent.team_name, player, player_info)
                        if comment and random.random() > 0.5:  # 50% chance to comment
                            messages.append((other_agent, agent.team_name, comment))
                            
                            # Store in conversation memory
                            agent.remember_conversation(other_agent.team_name, comment)
                            other_agent.remember_conversation(agent.team_name, f"Picked {player}")
                            
                            # Original agent might respond
                            response = agent.respond_to_comment(other_agent.team_name, comment)
                            if response and random.random() > 0.5:
                                messages.append((agent, other_agent.team_name, response))
                                other_agent.remember_conversation(agent.team_name, response)
            
            return messages, player
    
    def make_user_pick(self, player_name: str) -> List[str]:
        """Process the user's pick."""
        messages = []
        
        # Validate pick
        available = self.get_available_players()
        if player_name not in available:
            return [("advisor", "USER", f"❌ {player_name} is not available!")]
        
        # Make the pick
        self.draft_board[self.user_position].append(player_name)
        self.user_advisor.user_picks.append(player_name)
        self.all_picks.append((self.user_position, player_name))
        
        pick_num = len(self.all_picks)
        
        # Announce pick
        confirm_msg = self.commissioner.confirm_pick("YOUR TEAM", player_name, pick_num)
        messages.append(("commissioner", "ALL", confirm_msg))
        
        # Other agents comment on user's pick
        if player_name in TOP_PLAYERS:
            player_info = TOP_PLAYERS[player_name]
            
            for team_num, agent in self.agents.items():
                comment = agent.comment_on_pick("Your team", player_name, player_info)
                if comment and random.random() > 0.7:  # 70% chance to comment on user pick
                    messages.append((agent, "YOUR TEAM", comment))
        
        return messages
    
    def get_draft_summary(self) -> str:
        """Get a summary of the draft results."""
        summary = "📊 **DRAFT SUMMARY**\n\n"
        
        for team_num in sorted(self.draft_board.keys()):
            if team_num == self.user_position:
                summary += f"**YOUR TEAM**:\n"
            else:
                agent = self.agents.get(team_num)
                if agent:
                    summary += f"**{agent.team_name}** ({agent.strategy}):\n"
                else:
                    summary += f"**Team {team_num}**:\n"
            
            for i, player in enumerate(self.draft_board[team_num], 1):
                if player in TOP_PLAYERS:
                    info = TOP_PLAYERS[player]
                    summary += f"  R{i}: {player} ({info['pos']}, {info['team']})\n"
                else:
                    summary += f"  R{i}: {player}\n"
            summary += "\n"
        
        return summary 