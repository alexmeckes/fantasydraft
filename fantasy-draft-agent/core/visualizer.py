"""
Visual components for Fantasy Draft Agent demos.
Creates ASCII and simple text visualizations for player cards and draft boards.
"""

from typing import List, Dict
from .data import TOP_PLAYERS, get_player_info


def create_player_card(player_name: str) -> str:
    """Generate ASCII player card for visualization."""
    player = get_player_info(player_name)
    if not player:
        return f"Player '{player_name}' not found"
    
    # Create a nice ASCII card
    card = f"""
    ╔═══════════════════════════════╗
    ║ {player_name:<27} ║
    ╠═══════════════════════════════╣
    ║ Position: {player['pos']:<18} ║
    ║ Team:     {player['team']:<18} ║
    ║ ADP:      {player['adp']:<18} ║
    ║ Tier:     {player['tier']:<18} ║
    ║ 2023 PPG: {player['ppg_2023']:<18} ║
    ╚═══════════════════════════════╝
    """
    return card


def create_comparison_card(player1: str, player2: str) -> str:
    """Create a side-by-side comparison of two players."""
    p1 = get_player_info(player1)
    p2 = get_player_info(player2)
    
    if not p1 or not p2:
        return "One or both players not found"
    
    comparison = f"""
    ╔════════════════╦════════════════╗
    ║ {player1[:14]:<14} ║ {player2[:14]:<14} ║
    ╠════════════════╬════════════════╣
    ║ {p1['pos']} - {p1['team']:<10} ║ {p2['pos']} - {p2['team']:<10} ║
    ║ ADP: {p1['adp']:<10} ║ ADP: {p2['adp']:<10} ║
    ║ Tier: {p1['tier']:<9} ║ Tier: {p2['tier']:<9} ║
    ║ PPG: {p1['ppg_2023']:<10} ║ PPG: {p2['ppg_2023']:<10} ║
    ╚════════════════╩════════════════╝
    """
    return comparison


def create_draft_board_snapshot(picks: List[Dict[str, any]], rounds_to_show: int = 3) -> str:
    """Create a simple draft board visualization."""
    board = "📋 DRAFT BOARD\n"
    board += "="*50 + "\n\n"
    
    # Group picks by round (assuming 12-team league)
    rounds = {}
    for i, pick in enumerate(picks):
        round_num = (i // 12) + 1
        if round_num <= rounds_to_show:
            if round_num not in rounds:
                rounds[round_num] = []
            
            pick_num = (i % 12) + 1
            player_name = pick if isinstance(pick, str) else pick.get("player", "Unknown")
            rounds[round_num].append(f"{pick_num}. {player_name}")
    
    # Display rounds
    for round_num in sorted(rounds.keys()):
        board += f"Round {round_num}:\n"
        for pick in rounds[round_num]:
            board += f"  {pick}\n"
        board += "\n"
    
    return board


def create_roster_summary(my_picks: List[str]) -> str:
    """Create a summary of the user's roster."""
    if not my_picks:
        return "No picks yet!"
    
    roster = "📝 YOUR ROSTER\n"
    roster += "="*30 + "\n\n"
    
    # Group by position
    by_position = {"QB": [], "RB": [], "WR": [], "TE": []}
    
    for player_name in my_picks:
        player = get_player_info(player_name)
        if player:
            pos = player['pos']
            if pos in by_position:
                by_position[pos].append(player_name)
    
    # Display by position
    for pos, players in by_position.items():
        if players:
            roster += f"{pos}:\n"
            for player in players:
                info = get_player_info(player)
                roster += f"  • {player} ({info['team']}) - {info['ppg_2023']} PPG\n"
            roster += "\n"
    
    # Calculate projected points
    total_projected = sum(get_player_info(p)['ppg_2023'] for p in my_picks if get_player_info(p))
    roster += f"Projected Weekly Points: {total_projected:.1f}\n"
    
    return roster


def create_decision_summary(options: List[str], recommendation: str, reason: str) -> str:
    """Create a visual summary of a draft decision."""
    summary = "🤔 DRAFT DECISION\n"
    summary += "="*40 + "\n\n"
    
    summary += "Options considered:\n"
    for i, option in enumerate(options, 1):
        player = get_player_info(option)
        if player:
            summary += f"{i}. {option} ({player['pos']}) - ADP: {player['adp']}\n"
    
    summary += f"\n✅ Recommendation: {recommendation}\n"
    summary += f"📊 Reason: {reason}\n"
    
    return summary


def create_scenario_result(scenario_name: str, picks: List[str], outcome: str) -> str:
    """Create a result summary for a scenario."""
    result = f"🏆 SCENARIO RESULT: {scenario_name}\n"
    result += "="*50 + "\n\n"
    
    result += "Picks made:\n"
    for i, pick in enumerate(picks, 1):
        player = get_player_info(pick)
        if player:
            result += f"{i}. {pick} ({player['pos']}) - {player['ppg_2023']} PPG\n"
    
    result += f"\n📈 Outcome: {outcome}\n"
    
    # Calculate total projected points
    total_ppg = sum(get_player_info(p)['ppg_2023'] for p in picks if get_player_info(p))
    result += f"Total Projected PPG: {total_ppg:.1f}\n"
    
    return result


def create_multi_turn_flow(conversation_turns: List[Dict]) -> str:
    """Visualize a multi-turn conversation flow with context indicators."""
    flow = "💬 MULTI-TURN CONVERSATION FLOW\n"
    flow += "="*50 + "\n\n"
    
    # Add legend
    flow += "📖 Legend:\n"
    flow += "  🔄 = New Turn\n"
    flow += "  💭 = Using Previous Context\n"
    flow += "  ✨ = Explicit Context Reference\n"
    flow += "  🔗 = Building on Previous Answer\n\n"
    
    flow += "Conversation Timeline:\n"
    flow += "│\n"
    
    for i, turn in enumerate(conversation_turns):
        # Turn header
        flow += f"├─ 🔄 TURN {turn['turn']}: {turn['showcases']}\n"
        flow += "│\n"
        
        # User message
        user_preview = turn['user'][:60] + "..." if len(turn['user']) > 60 else turn['user']
        flow += f"│  👤 User: \"{user_preview}\"\n"
        
        # Show if this builds on previous context
        if i > 0:
            flow += "│  └─ 💭 (References previous conversation)\n"
        
        # Agent response preview
        agent_preview = turn['agent'][:60] + "..." if len(turn['agent']) > 60 else turn['agent']
        flow += f"│  🤖 Agent: \"{agent_preview}\"\n"
        
        # Context retention indicator
        if turn.get('context_retained', False):
            flow += "│  └─ ✨ CONTEXT USED: Agent explicitly referenced earlier conversation\n"
        
        # Check for specific context clues
        agent_lower = turn['agent'].lower()
        if any(word in agent_lower for word in ['you mentioned', 'you said', 'earlier']):
            flow += "│  └─ 🔗 Directly references user's previous input\n"
        elif any(word in agent_lower for word in ['we discussed', 'as i mentioned']):
            flow += "│  └─ 🔗 Builds on previous recommendations\n"
        
        flow += "│\n"
    
    flow += "└─ 🏁 Conversation Complete\n\n"
    
    # Add summary
    flow += f"📊 Summary:\n"
    flow += f"  • Total turns: {len(conversation_turns)}\n"
    flow += f"  • Context references: {sum(1 for t in conversation_turns if t.get('context_retained', False))}\n"
    flow += f"  • Demonstrates: Multi-turn memory and context awareness\n"
    
    return flow


def create_multi_turn_diagram(scenario_name: str, turns: int = 3) -> str:
    """Create a visual diagram showing multi-turn conversation flow."""
    diagram = f"""
╔═══════════════════════════════════════════════════════╗
║          🏈 MULTI-TURN CONVERSATION DEMO              ║
║               {scenario_name:<35}    ║
╚═══════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────┐
│ 💡 KEY FEATURE: Context Retention Across Turns      │
└─────────────────────────────────────────────────────┘

    Turn 1                Turn 2                Turn 3
      │                     │                     │
      ▼                     ▼                     ▼
┌──────────┐         ┌──────────┐         ┌──────────┐
│ 👤 USER  │         │ 👤 USER  │         │ 👤 USER  │
│          │         │          │         │          │
│ Initial  │────────▶│ Follow   │────────▶│ Build    │
│ Question │ MEMORY  │ Up       │ MEMORY  │ On       │
└──────────┘         └──────────┘         └──────────┘
      │                     │                     │
      ▼                     ▼                     ▼
┌──────────┐         ┌──────────┐         ┌──────────┐
│ 🤖 AGENT │         │ 🤖 AGENT │         │ 🤖 AGENT │
│          │         │    💭    │         │    💭    │
│ Answer   │         │ Remembers│         │ Full     │
│          │         │ Turn 1   │         │ Context  │
└──────────┘         └──────────┘         └──────────┘

Legend:
  💭 = Agent accessing conversation memory
  ──▶ = Context flows forward to next turn
  👤 = User input
  🤖 = Agent response with memory
"""
    return diagram


def create_context_highlight_example() -> str:
    """Show an example of how context is retained across turns."""
    example = """
🎯 MULTI-TURN CONTEXT RETENTION EXAMPLE
═══════════════════════════════════════

TURN 1:
👤 User: "I have the 5th pick. Who should I target?"
🤖 Agent: "With the 5th pick, I recommend targeting Bijan Robinson..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TURN 2:
👤 User: "What about Ekeler instead?"
         ↑
         └─── 🔍 No need to repeat context (5th pick)

🤖 Agent: "Given your 5th pick position that we discussed..."
           ↑
           └─── ✨ AGENT REMEMBERS: Pick position from Turn 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TURN 3:
👤 User: "Who pairs well with him?"
         ↑
         └─── 🔍 Pronoun "him" refers to previous player

🤖 Agent: "To pair with Ekeler from your 5th pick..."
           ↑               ↑
           │               └─── ✨ REMEMBERS: Pick position
           └─────────────────── ✨ REMEMBERS: Player choice

📊 Context Retained: 100% across all turns!
"""
    return example


# Demo function
def demo_visuals():
    """Demonstrate all visualization functions."""
    print("FANTASY DRAFT AGENT - VISUAL COMPONENTS DEMO")
    print("="*50 + "\n")
    
    # Player card
    print("1. Player Card:")
    print(create_player_card("Christian McCaffrey"))
    
    # Comparison
    print("\n2. Player Comparison:")
    print(create_comparison_card("Tyreek Hill", "CeeDee Lamb"))
    
    # Draft board
    print("\n3. Draft Board:")
    picks = ["Christian McCaffrey", "Justin Jefferson", "CeeDee Lamb", "Tyreek Hill",
             "Bijan Robinson", "Ja'Marr Chase", "Austin Ekeler", "Saquon Barkley",
             "A.J. Brown", "Nick Chubb", "Stefon Diggs", "Breece Hall"]
    print(create_draft_board_snapshot(picks))
    
    # Roster summary
    print("\n4. Roster Summary:")
    my_picks = ["Bijan Robinson", "A.J. Brown", "Mark Andrews", "Chris Olave"]
    print(create_roster_summary(my_picks))
    
    # Decision summary
    print("\n5. Decision Summary:")
    print(create_decision_summary(
        options=["Bijan Robinson", "Austin Ekeler", "Ja'Marr Chase"],
        recommendation="Bijan Robinson",
        reason="Elite talent with RB1 upside in a high-powered offense"
    ))


if __name__ == "__main__":
    demo_visuals()
