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
        """Generate commentary on another team's pick."""
        # This will be overridden by specific agent types
        pass
    
    def respond_to_comment(self, commenter: str, comment: str) -> Optional[str]:
        """Respond to another agent's comment."""
        # Check if we have context about this commenter
        relevant_memory = [m for m in self.conversation_memory if m['speaker'] == commenter]
        if relevant_memory:
            return f"Like I mentioned earlier, {self.strategy.lower()} is my approach."
        return None


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
                return player, f"Sticking to my Zero RB build. Elite WRs are the foundation!"
        
        # Later rounds, grab RBs
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        if best_available:
            player = best_available[0][0]
            pos = TOP_PLAYERS[player]['pos']
            if round_num > 3 and pos == 'RB':
                return player, "Time to grab some RB value in the middle rounds."
            return player, f"Best player available at {pos}."
        
        return "Unknown Player", "Hmm, slim pickings here..."
    
    def comment_on_pick(self, team: str, player: str, player_info: Dict) -> Optional[str]:
        if player_info['pos'] == 'RB' and player_info['tier'] == 1:
            return "Interesting choice! I'm letting others chase RBs while I build my WR corps."
        elif player_info['pos'] == 'WR' and player_info['tier'] <= 2:
            return "Great minds think alike! WRs are so much safer."
        return None


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
            pos = TOP_PLAYERS[player]['pos']
            return player, f"Can't pass up the value here. {player} is the best on the board!"
        
        return "Unknown Player", "Taking the best available..."
    
    def comment_on_pick(self, team: str, player: str, player_info: Dict) -> Optional[str]:
        # Check if it was a reach based on ADP
        # Since we can't access the exact pick number, use the number of our own picks as estimate
        estimated_pick = len(self.picks) * 6  # 6 teams in the draft
        
        if player_info['adp'] > estimated_pick + 10:
            return f"That's a reach! {player} usually goes later."
        elif player_info['adp'] < estimated_pick - 10:
            return f"Great value! Can't believe {player} fell this far."
        return None


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
                return player, "RBs win championships! Locking up my backfield early."
        
        # Best available after that
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        if best_available:
            player = best_available[0][0]
            return player, f"Adding {player} to my RB-heavy build."
        
        return "Unknown Player", "Building around my RBs..."
    
    def comment_on_pick(self, team: str, player: str, player_info: Dict) -> Optional[str]:
        if player_info['pos'] == 'WR' and len(self.picks) < 3:
            return "Passing on RBs early? Bold move! More for me."
        elif player_info['pos'] == 'RB':
            return "Smart pick. RBs are getting scarce fast!"
        return None


class UpsideAgent(DraftAgent):
    """Agent that hunts for upside/breakout players."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Upside Hunter", "#FFFDE7", "📓")
    
    def make_pick(self, available_players: List[str], draft_board: Dict) -> Tuple[str, str]:
        # Look for high upside players (simulate by taking slightly lower ADP)
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        # Sometimes reach for upside
        if len(best_available) > 3 and random.random() > 0.5:
            # Take someone a bit later for "upside"
            player = best_available[2][0]  # Skip top 2, take 3rd
            return player, f"I'm betting on {player}'s breakout potential!"
        elif best_available:
            player = best_available[0][0]
            return player, f"{player} has league-winning upside!"
        
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
        
        # Analyze what others have been doing
        rb_heavy_teams = [team for team, strat in other_agents_strategies.items() 
                         if 'RB' in strat]
        
        # Get best available by position
        best_by_pos = {}
        for pos in ['RB', 'WR', 'QB', 'TE']:
            candidates = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players and info['pos'] == pos]
            if candidates:
                candidates.sort(key=lambda x: x[1]['adp'])
                best_by_pos[pos] = candidates[0]
        
        advice = f"🎯 **Round {round_num} Advice**\n\n"
        
        # Contextual advice based on what's happened
        if round_num == 1:
            advice += "For your first pick, I recommend:\n"
            if best_by_pos.get('RB'):
                advice += f"• **{best_by_pos['RB'][0]}** - Elite RB to anchor your team\n"
            if best_by_pos.get('WR'):
                advice += f"• **{best_by_pos['WR'][0]}** - Top WR for consistency\n"
        else:
            # Reference previous picks and strategies
            if len(rb_heavy_teams) >= 2:
                advice += "⚠️ Multiple teams are going RB-heavy. WRs might be better value!\n\n"
            
            # Check user's roster needs
            user_rbs = [p for p in self.user_picks if TOP_PLAYERS.get(p, {}).get('pos') == 'RB']
            user_wrs = [p for p in self.user_picks if TOP_PLAYERS.get(p, {}).get('pos') == 'WR']
            
            if len(user_rbs) == 0:
                advice += "📌 You need a RB! Consider:\n"
                if best_by_pos.get('RB'):
                    advice += f"• **{best_by_pos['RB'][0]}**\n"
            elif len(user_wrs) == 0:
                advice += "📌 You need a WR! Consider:\n"
                if best_by_pos.get('WR'):
                    advice += f"• **{best_by_pos['WR'][0]}**\n"
        
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
                            
                            # Original agent might respond
                            response = agent.respond_to_comment(other_agent.team_name, comment)
                            if response and random.random() > 0.5:
                                messages.append((agent, other_agent.team_name, response))
            
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