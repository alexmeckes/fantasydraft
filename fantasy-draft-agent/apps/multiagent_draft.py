#!/usr/bin/env python3
"""
Multi-Agent Mock Draft Implementation
Demonstrates A2A communication and multi-turn memory
"""

import time
from typing import Dict, List, Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import FantasyDraftAgent
from core.data import TOP_PLAYERS, get_best_available, get_players_by_position
import random

# Enhanced agents not available in the reorganized structure
USE_ENHANCED = False
print("📝 Using standard agents")


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
        # Convert ADP to a more understandable format
        adp_int = int(player_info['adp'])
        if adp_int == 0:
            adp_int = 1
        adp_description = f"ranked #{adp_int} overall" if adp_int <= 10 else f"typically drafted around pick #{adp_int}"
        
        context = f"""You are {self.team_name}, a fantasy football team manager following a {self.strategy}.
Your picks so far: {', '.join(self.picks) if self.picks else 'None yet'}

{team} just picked {player} ({player_info['pos']}, {adp_description}, Tier: {player_info['tier']}).

Based on your strategy and the current draft situation, provide a short, natural comment on this pick. 
Be competitive and show some personality - you can be critical, sarcastic, or dismissive if the pick doesn't align with your philosophy.
Don't be overly nice. This is a competitive draft and you want to win. Show confidence in your strategy.
Keep it under 2 sentences and make it feel like real draft room banter - trash talk is encouraged!
IMPORTANT: Don't mention raw ADP numbers like "1.5" - use natural language like "top pick", "#1 overall", "first round talent", etc."""

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
        self.person_emoji = "🤓"  # Analytical nerd
    
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
                # Convert ADP to readable format
                adp_int = int(player_info['adp'])
                if adp_int <= 12:
                    adp_desc = f"a top-{adp_int} player"
                elif adp_int <= 24:
                    adp_desc = "an early second-round talent"
                else:
                    adp_desc = f"ranked around #{adp_int}"
                
                context = f"""You are {self.team_name} following a Zero RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}

You're selecting {player} (WR, {player_info['team']}, {adp_desc}).

Explain your pick in 1-2 sentences, emphasizing why this fits your Zero RB strategy. 
Be confident and maybe a bit cocky about avoiding RBs. Take subtle shots at teams loading up on injury-prone RBs.
Show personality - you KNOW your strategy is superior.
Don't use raw numbers like "1.5" or "ADP 12" - use natural language."""
                
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
            
            # Convert ADP to readable format
            adp_int = int(player_info['adp'])
            if pos == 'RB':
                adp_desc = "a value RB" if adp_int > 24 else "a solid back"
            else:
                adp_desc = f"ranked #{adp_int}" if adp_int > 30 else f"a round {(adp_int-1)//12 + 1} talent"
            
            context = f"""You are {self.team_name} following a Zero RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks)}

You're selecting {player} ({pos}, {player_info['team']}, {adp_desc}).

Explain why you're taking this player now, given your Zero RB approach.
If it's a RB, explain why NOW is the right time (while others reached early). 
Be smug about getting value while others panicked. Keep it to 1-2 sentences with attitude.
Use terms like "value", "steal", "while others reached" - not raw numbers."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Hmm, slim pickings here..."
    



class BPAAgent(DraftAgent):
    """Agent that follows Best Player Available strategy."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Best Player Available", "#E8F5E9", "📗")
        self.person_emoji = "🧑‍💼"  # Business-like, calculated
    
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
            # Convert ADP to readable format
            adp_int = int(player_info['adp'])
            if adp_int <= 12:
                adp_desc = f"the #{adp_int} overall player"
            elif adp_int <= 24:
                adp_desc = "a late first/early second round value"
            else:
                adp_desc = f"ranked #{adp_int} overall"
            
            context = f"""You are {self.team_name} following a Best Player Available strategy.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}
Round: {len(self.picks) + 1}

You're selecting {player} ({pos}, {player_info['team']}, {adp_desc}).

Explain why this is the best value pick available. Focus on their value and ranking.
Be condescending about other teams reaching for needs or following rigid strategies.
You're the smart one taking the obvious value - let them know it. Keep it to 1-2 sentences.
Don't use raw ADP numbers - use terms like "best available", "top-ranked", "obvious value", etc."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Taking the best available..."
    



class RobustRBAgent(DraftAgent):
    """Agent that follows Robust RB strategy."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Robust RB Strategy", "#FFF3E0", "📙")
        self.person_emoji = "🧔"  # Old-school, traditional
    
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
                
                # Convert ADP to readable format
                adp_int = int(player_info['adp'])
                if adp_int <= 5:
                    adp_desc = "an elite, top-5 back"
                elif adp_int <= 12:
                    adp_desc = f"a premier RB1"
                else:
                    adp_desc = "a solid running back"
                
                context = f"""You are {self.team_name} following a Robust RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}

You're selecting {player} (RB, {player_info['team']}, {adp_desc}).

Explain why this RB is crucial for your Robust RB strategy. Be aggressive about RBs winning championships.
Mock teams that are going WR-heavy. You're building a REAL team with a strong foundation.
Be old-school and dismissive of "fancy" WR strategies. Keep it to 1-2 sentences with authority.
Use terms like "workhorse", "bell cow", "foundation" - not raw numbers."""
                
                reasoning = self.agent.run(context).strip()
                return player, reasoning
        
        # Best available after that
        best_available = [(p, info) for p, info in TOP_PLAYERS.items() 
                         if p in available_players]
        best_available.sort(key=lambda x: x[1]['adp'])
        
        if best_available:
            player = best_available[0][0]
            player_info = best_available[0][1]
            
            # Convert ADP to readable format
            adp_int = int(player_info['adp'])
            pos = player_info['pos']
            if pos == 'WR':
                adp_desc = "a quality receiver" if adp_int <= 24 else "a decent WR option"
            elif pos == 'TE':
                adp_desc = "a reliable tight end"
            else:
                adp_desc = f"ranked #{adp_int}"
            
            context = f"""You are {self.team_name} following a Robust RB strategy in round {round_num}.
Your previous picks: {', '.join(self.picks)}

You're selecting {player} ({player_info['pos']}, {player_info['team']}, {adp_desc}).

Explain how this pick fits with your RB-heavy build. If it's not a RB, grudgingly admit you need other positions too.
But emphasize your RB foundation is what matters. Be dismissive of WR-first teams. Keep it to 1-2 sentences.
Focus on your "foundation" and "championship formula" - avoid raw rankings."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Building around my RBs..."


class UpsideAgent(DraftAgent):
    """Agent that hunts for upside/breakout players."""
    
    def __init__(self, team_name: str):
        super().__init__(team_name, "Upside Hunter", "#FFFDE7", "📓")
        self.person_emoji = "🤠"  # Risk-taking cowboy
    
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
            
            # Convert ADP to readable format
            adp_int = int(player_info['adp'])
            adp_desc = "a sleeper pick" if adp_int > 36 else "someone with untapped potential"
            
            context = f"""You are {self.team_name}, an Upside Hunter who looks for breakout potential.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}
Round: {len(self.picks) + 1}

You're reaching slightly for {player} ({player_info['pos']}, {player_info['team']}, {adp_desc}).

Explain why you see breakout/league-winning potential in this player. Be enthusiastic about their upside.
Mock the "safe" picks others are making. You're here to WIN, not finish 4th! 
Championships require RISK! Keep it to 1-2 sentences with swagger.
Talk about "upside", "ceiling", "league-winner" - not specific rankings."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
            
        elif best_available:
            player = best_available[0][0]
            player_info = best_available[0][1]
            
            # Convert ADP to readable format
            adp_int = int(player_info['adp'])
            if adp_int <= 12:
                adp_desc = "a high-ceiling star"
            elif adp_int <= 36:
                adp_desc = "someone with serious upside"
            else:
                adp_desc = "a potential breakout"
            
            context = f"""You are {self.team_name}, an Upside Hunter who looks for league-winners.
Your previous picks: {', '.join(self.picks) if self.picks else 'None'}
Round: {len(self.picks) + 1}

You're selecting {player} ({player_info['pos']}, {player_info['team']}, {adp_desc}).

Explain what upside or potential you see in this player. Focus on ceiling over floor.
Be dismissive of "safe" boring picks. You're building a championship roster, not a participation trophy team!
Keep it to 1-2 sentences with confidence.
Use exciting terms like "breakout", "league-winner", "explosive" - not rankings."""
            
            reasoning = self.agent.run(context).strip()
            return player, reasoning
        
        return "Unknown Player", "Going for the home run pick..."


class UserAdvisorAgent(DraftAgent):
    """Agent that advises the user during their picks."""
    
    def __init__(self):
        super().__init__("Your Advisor", "Strategic Advisor", "#FFEBEE", "📕")
        self.person_emoji = "🧙"  # Wise advisor
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
- Best RB: {best_by_pos.get('RB', [None])[0]} {f"(ranked #{int(best_by_pos.get('RB', [None, {'adp': 999}])[1]['adp'])})" if best_by_pos.get('RB') else ""}
- Best WR: {best_by_pos.get('WR', [None])[0]} {f"(ranked #{int(best_by_pos.get('WR', [None, {'adp': 999}])[1]['adp'])})" if best_by_pos.get('WR') else ""}
- Best QB: {best_by_pos.get('QB', [None])[0]} {f"(ranked #{int(best_by_pos.get('QB', [None, {'adp': 999}])[1]['adp'])})" if best_by_pos.get('QB') else ""}
- Best TE: {best_by_pos.get('TE', [None])[0]} {f"(ranked #{int(best_by_pos.get('TE', [None, {'adp': 999}])[1]['adp'])})" if best_by_pos.get('TE') else ""}

Recent picks by other teams:
{chr(10).join(other_picks_summary[-3:]) if other_picks_summary else 'None yet'}

Other team strategies: {', '.join([f"{t}: {s}" for t, s in other_agents_strategies.items()])}

Provide strategic advice for the user's pick. Consider:
1. Their roster needs
2. Best available value
3. What other teams are doing
4. Position scarcity

Format as: 🎯 **Round {round_num} Advice** followed by 2-3 bullet points with specific player recommendations and reasoning.
Keep it concise but insightful.
When discussing player rankings, use natural language like "top-5 RB", "first-round talent", "mid-round value" instead of raw numbers like "ADP 12.5"."""
        
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
        
        # Add Team 6 as BPA if it's not the user position
        if 6 != user_pick_position:
            self.agents[6] = BPAAgent("Team 6")
            self.agents[6].person_emoji = "👨‍🏫"  # Professor, methodical
        
        self.user_position = user_pick_position
        self.user_advisor = UserAdvisorAgent()
        self.commissioner = CommissionerAgent()
        
        # Draft state
        self.draft_board = {i: [] for i in range(1, 7)}  # All 6 teams
        
        # Give all agents access to the draft board
        for agent in self.agents.values():
            agent.draft_board = self.draft_board
        
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
            # Include person emoji if available
            emojis = agent.icon
            if hasattr(agent, 'person_emoji'):
                emojis = f"{agent.icon}{agent.person_emoji}"
            
            if recipient == "ALL":
                return f"{emojis} **{agent.team_name}**: {message}"
            else:
                return f"{emojis} **{agent.team_name}** → {recipient}: {message}"
        else:
            # Commissioner
            return f"{agent.icon} **COMMISSIONER**: {message}"
    
    def is_pick_controversial(self, player: str, pick_num: int) -> bool:
        """Determine if a pick is controversial (reach, surprise, etc)."""
        if player not in TOP_PLAYERS:
            return False
        
        player_info = TOP_PLAYERS[player]
        expected_pick = pick_num * 1.5  # Rough estimate of expected ADP
        
        # Check if it's a reach (picked way above ADP)
        if player_info['adp'] > expected_pick + 5:
            return True
        
        # Check if it's a position run (3rd player at same position in a row)
        recent_picks = self.all_picks[-3:]
        recent_positions = [TOP_PLAYERS.get(p[1], {}).get('pos', '') for p in recent_picks]
        if recent_positions.count(player_info['pos']) >= 2:
            return True
        
        return False
    
    def select_commenters(self, picking_team: int, picked_player: str) -> List[int]:
        """Select 1-2 agents who should comment on this pick."""
        if picked_player not in TOP_PLAYERS:
            return []
        
        player_info = TOP_PLAYERS[picked_player]
        pick_num = len(self.all_picks) + 1
        available_commenters = [num for num in self.agents.keys() if num != picking_team]
        
        selected = []
        
        # For obvious early picks (CMC at 1, CeeDee at 2, etc), maybe skip comments
        # But always comment on user picks
        if pick_num <= 3 and player_info['adp'] <= pick_num + 1 and picking_team != self.user_position:
            # 50% chance to skip comments on obvious picks
            if random.random() < 0.5:
                return []
        
        # Priority 1: Next drafter (if not user)
        snake_order = self.get_draft_order(((pick_num - 1) // 6) + 1)
        current_pos = snake_order.index(picking_team)
        if current_pos < len(snake_order) - 1:
            next_drafter = snake_order[current_pos + 1]
            if next_drafter in available_commenters:
                selected.append(next_drafter)
                available_commenters.remove(next_drafter)
        
        # Priority 2: Agent with opposing strategy
        if picked_player in TOP_PLAYERS and len(selected) < 3:
            pos = player_info['pos']
            
            # Zero RB vs Robust RB conflict
            if pos == 'RB' and 1 in available_commenters:  # Zero RB agent
                selected.append(1)
                available_commenters.remove(1)
            elif pos == 'WR' and 3 in available_commenters:  # Robust RB agent
                selected.append(3)
                available_commenters.remove(3)
        
        # Priority 3: Random agent if pick is controversial
        if self.is_pick_controversial(picked_player, pick_num) and len(selected) < 2 and available_commenters:
            random_commenter = random.choice(available_commenters)
            selected.append(random_commenter)
        
        # For non-controversial picks, only 50% chance of any comment if none selected yet
        if not selected and available_commenters:
            # User picks always get at least 1 comment
            if picking_team == self.user_position:
                selected.append(random.choice(available_commenters))
            elif self.is_pick_controversial(picked_player, pick_num) or random.random() > 0.5:
                selected.append(random.choice(available_commenters))
        
        return selected[:2]  # Max 2 commenters
    
    def get_draft_order(self, round_num: int) -> List[int]:
        """Get the draft order for a given round (snake draft)."""
        if round_num % 2 == 1:
            return list(range(1, 7))  # 1-6 for odd rounds
        else:
            return list(range(6, 0, -1))  # 6-1 for even rounds
    
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
            
            # Enhanced features: sometimes add emoji storms and meta commentary
            if USE_ENHANCED and hasattr(agent, 'generate_emoji_storm'):
                # Controversial picks get emoji reactions
                if self.is_pick_controversial(player, pick_num) and random.random() > 0.6:
                    # Random agent drops emoji bomb
                    reactor = random.choice(list(self.agents.values()))
                    if reactor != agent:  # Don't react to yourself
                        player_adp = TOP_PLAYERS.get(player, {}).get('adp', 100)
                        emoji_storm = reactor.generate_emoji_storm("bad_pick" if pick_num < player_adp else "great_pick")
                        messages.append((reactor, "ALL", emoji_storm))
                
                # Meta commentary occasionally
                if pick_num % 10 == 0 and random.random() > 0.7:
                    meta_agent = random.choice(list(self.agents.values()))
                    meta_comments = [
                        "Is anyone else's algorithm telling them to be meaner? 🤖",
                        "Why do I always end up in the most toxic draft rooms? 😅",
                        "USER, PLEASE don't take my sleeper at pick 4 🙏",
                        "This draft chat gonna end up on r/fantasyfootball 📸",
                        "The disrespect in this room is ASTRONOMICAL 💀",
                        "I can't wait to screenshot this for the group chat later 📱"
                    ]
                    messages.append((meta_agent, "ALL", random.choice(meta_comments)))
            
            # Select 2-3 agents to comment
            if player in TOP_PLAYERS:
                player_info = TOP_PLAYERS[player]
                selected_commenters = self.select_commenters(team_num, player)
                
                # Generate comments from selected agents
                for commenter_num in selected_commenters:
                    other_agent = self.agents.get(commenter_num)
                    if other_agent:
                        # Add typing indicator
                        typing_msg = (f"typing_{other_agent.team_name}", agent.team_name, 
                                    f"{other_agent.team_name} is typing...")
                        messages.append(typing_msg)
                        
                        # Generate comment
                        comment = other_agent.comment_on_pick(agent.team_name, player, player_info)
                        if comment:
                            messages.append((other_agent, agent.team_name, comment))
                            
                            # Store in conversation memory
                            agent.remember_conversation(other_agent.team_name, comment)
                            other_agent.remember_conversation(agent.team_name, f"Picked {player}")
                            
                            # Enhanced agents respond more often (30% vs 15%)
                            response_chance = 0.70 if USE_ENHANCED else 0.85
                            if random.random() > response_chance:
                                # Typing indicator for response
                                response_typing = (f"typing_{agent.team_name}", other_agent.team_name,
                                                 f"{agent.team_name} is typing...")
                                messages.append(response_typing)
                                
                                response = agent.respond_to_comment(other_agent.team_name, comment)
                                if response:
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
        
        # Select agents to comment on user's pick
        if player_name in TOP_PLAYERS:
            player_info = TOP_PLAYERS[player_name]
            selected_commenters = self.select_commenters(self.user_position, player_name)
            
            # User picks get attention - allow up to 2 comments
            for commenter_num in selected_commenters[:2]:
                agent = self.agents.get(commenter_num)
                if agent:
                    # Add typing indicator
                    typing_msg = (f"typing_{agent.team_name}", "YOUR TEAM", 
                                f"{agent.team_name} is typing...")
                    messages.append(typing_msg)
                    
                    comment = agent.comment_on_pick("Your team", player_name, player_info)
                    if comment:
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