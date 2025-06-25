"""
Helper functions for A2A response parsing and formatting.
"""
import json
from typing import Any, Optional, Dict, List
from pydantic import BaseModel


def parse_a2a_response(result: Any, output_class: type[BaseModel]) -> Optional[BaseModel]:
    """
    Parse A2A response from various wrapper formats.
    
    Args:
        result: Raw response from A2A agent
        output_class: Expected output class (e.g., A2AOutput)
        
    Returns:
        Parsed output object or None if parsing fails
        
    Example:
        >>> result = {"type": "pick", "player_name": "Jefferson"}
        >>> output = parse_a2a_response(result, A2AOutput)
        >>> print(output.player_name)
        "Jefferson"
    """
    # Handle string responses
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except:
            return None
    
    # Handle direct output class instance
    if isinstance(result, output_class):
        return result
    
    # Handle dict with expected fields
    if isinstance(result, dict):
        # Try direct conversion first
        if 'type' in result:
            try:
                return output_class(**result)
            except:
                pass
        
        # Handle A2A wrapper format
        if 'status' in result and 'message' in result.get('status', {}):
            return _extract_from_wrapper(result, output_class)
    
    return None


def _extract_from_wrapper(wrapped_result: Dict, output_class: type[BaseModel]) -> Optional[BaseModel]:
    """Extract response from A2A wrapper format."""
    try:
        message = wrapped_result['status']['message']
        if 'parts' in message and len(message['parts']) > 0:
            text = message['parts'][0].get('text', '')
            agent_response = json.loads(text)
            return output_class(**agent_response)
    except Exception:
        pass
    return None


def extract_task_id(result: Any) -> Optional[str]:
    """Extract task_id from A2A response if present."""
    if isinstance(result, dict) and 'task_id' in result:
        return result['task_id']
    return None


def build_pick_prompt(
    team_num: int,
    available_players: List[str],
    previous_picks: List[str],
    round_num: int,
    context: str = ""
) -> str:
    """
    Build a prompt for an agent to make a pick.
    
    Args:
        team_num: Team number making the pick
        available_players: List of available player names with positions
        previous_picks: List of players already picked by this team
        round_num: Current round number
        context: Additional context from conversation history
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""🚨 IT'S YOUR TIME TO DOMINATE! 🚨 (Round {round_num})
        {context}
Available top players: {', '.join(available_players)}
Your roster so far: {', '.join(previous_picks) if previous_picks else 'None yet'}

Make your pick and DESTROY the competition! 💪
Output an A2AOutput with type="pick", player_name, reasoning (with emojis!), and SAVAGE trash_talk!
Remember your ENEMIES and CRUSH their dreams! Use emojis to emphasize your DOMINANCE! 🔥"""
    
    return prompt


def build_comment_prompt(
    commenting_team: int,
    picking_team: int,
    player_picked: str,
    round_num: int,
    context: str = ""
) -> str:
    """
    Build a prompt for an agent to comment on another team's pick.
    
    Args:
        commenting_team: Team number making the comment
        picking_team: Team number that made the pick
        player_picked: Name of player that was picked
        round_num: Current round number
        context: Additional context from conversation history
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""🎯 Team {picking_team} just picked {player_picked}! 
{context}
This is your chance to DESTROY them with your superior knowledge! 💥
Should you UNLEASH your wisdom? Output an A2AOutput with type="comment", should_comment (true/false), and a DEVASTATING comment with emojis!
If they're your RIVAL, make it PERSONAL! If they made a BAD pick, ROAST THEM! 🔥
Use emojis to make your point UNFORGETTABLE! 😈"""
    
    return prompt


def format_available_players(players: List[str], player_info: Dict[str, Dict]) -> List[str]:
    """
    Format available players with their positions.
    
    Args:
        players: List of player names
        player_info: Dictionary with player information
        
    Returns:
        List of formatted strings like "Jefferson (WR)"
    """
    formatted = []
    for player in players[:10]:  # Top 10 only
        info = player_info.get(player, {})
        formatted.append(f"{player} ({info.get('pos', '??')})")
    return formatted 