"""
Static player data for Fantasy Draft Agent MVP.
Hardcoded top 50 fantasy football players with basic stats.
"""

# Top players by position with their Average Draft Position (ADP) and 2023 stats
TOP_PLAYERS = {
    # Top Running Backs
    "Christian McCaffrey": {"pos": "RB", "adp": 1.2, "tier": 1, "ppg_2023": 22.1, "team": "SF"},
    "Austin Ekeler": {"pos": "RB", "adp": 4.5, "tier": 1, "ppg_2023": 18.7, "team": "LAC"},
    "Bijan Robinson": {"pos": "RB", "adp": 3.8, "tier": 1, "ppg_2023": 15.2, "team": "ATL"},
    "Saquon Barkley": {"pos": "RB", "adp": 5.2, "tier": 1, "ppg_2023": 17.3, "team": "NYG"},
    "Tony Pollard": {"pos": "RB", "adp": 8.1, "tier": 2, "ppg_2023": 14.8, "team": "DAL"},
    "Jonathan Taylor": {"pos": "RB", "adp": 6.7, "tier": 2, "ppg_2023": 13.5, "team": "IND"},
    "Derrick Henry": {"pos": "RB", "adp": 11.3, "tier": 2, "ppg_2023": 13.9, "team": "TEN"},
    "Nick Chubb": {"pos": "RB", "adp": 9.5, "tier": 2, "ppg_2023": 16.8, "team": "CLE"},
    "Josh Jacobs": {"pos": "RB", "adp": 10.2, "tier": 2, "ppg_2023": 15.7, "team": "LV"},
    "Breece Hall": {"pos": "RB", "adp": 7.8, "tier": 2, "ppg_2023": 14.2, "team": "NYJ"},
    
    # Top Wide Receivers
    "Tyreek Hill": {"pos": "WR", "adp": 3.1, "tier": 1, "ppg_2023": 20.2, "team": "MIA"},
    "CeeDee Lamb": {"pos": "WR", "adp": 2.5, "tier": 1, "ppg_2023": 19.8, "team": "DAL"},
    "Justin Jefferson": {"pos": "WR", "adp": 1.8, "tier": 1, "ppg_2023": 21.5, "team": "MIN"},
    "Ja'Marr Chase": {"pos": "WR", "adp": 4.2, "tier": 1, "ppg_2023": 18.9, "team": "CIN"},
    "A.J. Brown": {"pos": "WR", "adp": 6.3, "tier": 1, "ppg_2023": 17.6, "team": "PHI"},
    "Stefon Diggs": {"pos": "WR", "adp": 7.1, "tier": 1, "ppg_2023": 17.2, "team": "BUF"},
    "Amon-Ra St. Brown": {"pos": "WR", "adp": 9.8, "tier": 2, "ppg_2023": 16.4, "team": "DET"},
    "Davante Adams": {"pos": "WR", "adp": 8.9, "tier": 2, "ppg_2023": 16.8, "team": "LV"},
    "Chris Olave": {"pos": "WR", "adp": 14.3, "tier": 2, "ppg_2023": 14.1, "team": "NO"},
    "DK Metcalf": {"pos": "WR", "adp": 15.7, "tier": 2, "ppg_2023": 13.8, "team": "SEA"},
    "Mike Evans": {"pos": "WR", "adp": 16.2, "tier": 2, "ppg_2023": 15.3, "team": "TB"},
    "Calvin Ridley": {"pos": "WR", "adp": 18.5, "tier": 3, "ppg_2023": 12.1, "team": "JAX"},
    
    # Top Quarterbacks
    "Josh Allen": {"pos": "QB", "adp": 24.3, "tier": 1, "ppg_2023": 24.6, "team": "BUF"},
    "Patrick Mahomes": {"pos": "QB", "adp": 22.1, "tier": 1, "ppg_2023": 25.8, "team": "KC"},
    "Jalen Hurts": {"pos": "QB", "adp": 19.8, "tier": 1, "ppg_2023": 26.4, "team": "PHI"},
    "Lamar Jackson": {"pos": "QB", "adp": 31.5, "tier": 2, "ppg_2023": 21.3, "team": "BAL"},
    "Dak Prescott": {"pos": "QB", "adp": 45.7, "tier": 2, "ppg_2023": 20.1, "team": "DAL"},
    "Joe Burrow": {"pos": "QB", "adp": 38.2, "tier": 2, "ppg_2023": 19.8, "team": "CIN"},
    "Justin Herbert": {"pos": "QB", "adp": 42.3, "tier": 2, "ppg_2023": 19.2, "team": "LAC"},
    
    # Top Tight Ends
    "Travis Kelce": {"pos": "TE", "adp": 12.4, "tier": 1, "ppg_2023": 16.4, "team": "KC"},
    "Mark Andrews": {"pos": "TE", "adp": 25.6, "tier": 1, "ppg_2023": 13.2, "team": "BAL"},
    "T.J. Hockenson": {"pos": "TE", "adp": 34.8, "tier": 2, "ppg_2023": 11.8, "team": "MIN"},
    "George Kittle": {"pos": "TE", "adp": 41.2, "tier": 2, "ppg_2023": 10.9, "team": "SF"},
    "Darren Waller": {"pos": "TE", "adp": 48.5, "tier": 2, "ppg_2023": 9.7, "team": "NYG"},
    
    # Additional depth players for rounds 5-10
    "Jahmyr Gibbs": {"pos": "RB", "adp": 21.3, "tier": 3, "ppg_2023": 11.2, "team": "DET"},
    "Rhamondre Stevenson": {"pos": "RB", "adp": 23.7, "tier": 3, "ppg_2023": 12.1, "team": "NE"},
    "Kenneth Walker": {"pos": "RB", "adp": 28.4, "tier": 3, "ppg_2023": 11.8, "team": "SEA"},
    "DeAndre Hopkins": {"pos": "WR", "adp": 52.1, "tier": 3, "ppg_2023": 10.2, "team": "TEN"},
    "Keenan Allen": {"pos": "WR", "adp": 29.8, "tier": 3, "ppg_2023": 13.1, "team": "LAC"},
    "Amari Cooper": {"pos": "WR", "adp": 37.2, "tier": 3, "ppg_2023": 12.7, "team": "CLE"},
    "Terry McLaurin": {"pos": "WR", "adp": 44.6, "tier": 3, "ppg_2023": 11.9, "team": "WAS"},
    "DJ Moore": {"pos": "WR", "adp": 35.9, "tier": 3, "ppg_2023": 11.4, "team": "CHI"},
    "Deshaun Watson": {"pos": "QB", "adp": 68.3, "tier": 3, "ppg_2023": 16.7, "team": "CLE"},
    "Trevor Lawrence": {"pos": "QB", "adp": 71.2, "tier": 3, "ppg_2023": 17.2, "team": "JAX"},
    
    # Sleepers and late-round targets
    "Jordan Addison": {"pos": "WR", "adp": 85.3, "tier": 4, "ppg_2023": 8.2, "team": "MIN"},
    "Jahan Dotson": {"pos": "WR", "adp": 92.7, "tier": 4, "ppg_2023": 7.8, "team": "WAS"},
    "Khalil Herbert": {"pos": "RB", "adp": 89.1, "tier": 4, "ppg_2023": 8.9, "team": "CHI"},
    "Zay Flowers": {"pos": "WR", "adp": 76.4, "tier": 4, "ppg_2023": 9.1, "team": "BAL"},
}


def get_player_info(player_name: str) -> dict:
    """Get player information by name."""
    return TOP_PLAYERS.get(player_name, {})


def get_players_by_position(position: str) -> dict:
    """Get all players at a specific position."""
    return {name: info for name, info in TOP_PLAYERS.items() if info["pos"] == position}


def get_players_by_tier(tier: int) -> dict:
    """Get all players in a specific tier."""
    return {name: info for name, info in TOP_PLAYERS.items() if info["tier"] == tier}


def get_available_players(drafted_players: list) -> dict:
    """Get all players not yet drafted."""
    return {name: info for name, info in TOP_PLAYERS.items() if name not in drafted_players}


def get_best_available(drafted_players: list, position: str = None) -> tuple:
    """Get the best available player overall or by position."""
    available = get_available_players(drafted_players)
    
    if position:
        available = {name: info for name, info in available.items() if info["pos"] == position}
    
    if not available:
        return None, None
    
    # Sort by ADP (lower is better)
    best = min(available.items(), key=lambda x: x[1]["adp"])
    return best
