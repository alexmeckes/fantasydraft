#!/usr/bin/env python3
"""
Multi-Agent Scenarios and Visualization
Provides formatted output for multi-agent interactions
"""

from .multiagent_draft import MultiAgentMockDraft, DraftAgent, CommissionerAgent
import time


def format_agent_message(agent, recipient: str, message: str, 
                        show_arrow: bool = True) -> str:
    """Format an agent message with proper styling."""
    
    # Check if this is a typing indicator
    if isinstance(agent, str) and agent.startswith("typing_"):
        # Extract the team name from typing_Team X
        team_name = agent.replace("typing_", "")
        return f'<div style="color: #666; font-style: italic; margin: 5px 0;">💭 *{team_name} is typing...*</div>\n\n'
    
    # Agent colors and styles
    agent_styles = {
        "📘": ("Team 1", "#E3F2FD", "#1976D2"),  # Blue
        "📘🤓": ("Team 1", "#E3F2FD", "#1976D2"),  # Blue with nerd emoji
        "📗": ("Team 2", "#E8F5E9", "#388E3C"),  # Green
        "📗🧑‍💼": ("Team 2", "#E8F5E9", "#388E3C"),  # Green with business person
        "📗👨‍🏫": ("Team 6", "#E8F5E9", "#388E3C"),  # Green with professor
        "📙": ("Team 3", "#FFF3E0", "#F57C00"),  # Orange
        "📙🧔": ("Team 3", "#FFF3E0", "#F57C00"),  # Orange with beard
        "📕": ("Your Advisor", "#FFEBEE", "#D32F2F"),  # Red
        "📕🧙": ("Your Advisor", "#FFEBEE", "#D32F2F"),  # Red with wizard
        "📓": ("Team 5", "#F5E6FF", "#7B1FA2"),  # Purple
        "📓🤠": ("Team 5", "#F5E6FF", "#7B1FA2"),  # Purple with cowboy
        "📜": ("COMMISSIONER", "#ECEFF1", "#455A64"),  # Blue-gray
        "👤": ("YOUR TEAM", "#E8EAF6", "#3F51B5"),  # Indigo for user
        "💭": ("System", "#FFF9C4", "#FBC02D"),  # Light yellow for loading/system messages
    }
    
    if hasattr(agent, 'icon'):
        icon = agent.icon
        # Include person emoji if available
        if hasattr(agent, 'person_emoji'):
            icon = f"{agent.icon}{agent.person_emoji}"
        if hasattr(agent, 'team_name'):
            name = agent.team_name
        else:
            name = "COMMISSIONER"
    else:
        # String agent (for simplified calls)
        if agent == "commissioner":
            icon = "📜"
            name = "COMMISSIONER"
        elif agent == "advisor":
            icon = "📕"
            name = "Your Advisor"
        elif agent == "user":
            icon = "👤"
            name = "YOUR TEAM"
        elif agent == "system":
            icon = "💭"
            name = "System"
        else:
            return message
    
    style = agent_styles.get(icon, ("Unknown", "#FFFFFF", "#000000"))
    bg_color, border_color = style[1], style[2]
    
    # Build the message box with more specific color
    html = f'<div style="background-color: {bg_color}; '
    html += f'border-left: 4px solid {border_color}; '
    html += f'padding: 15px; border-radius: 8px; margin: 10px 0; '
    html += f'color: #212121 !important;">\n\n'
    
    # Header with sender/recipient
    if agent == "system" or icon == "💭":
        # System messages are centered and italicized
        html = f'<div style="text-align: center; margin: 10px 0;">\n\n'
        html += f'*{message}*\n\n'
        html += '</div>\n\n'
        return html
    elif recipient == "ALL":
        html += f'**{icon} {name}**\n\n'
    elif recipient == "USER":
        html += f'**{icon} {name} → You**\n\n'
    elif show_arrow:
        html += f'**{icon} {name} → {recipient}**\n\n'
    else:
        html += f'**{icon} {name}**\n\n'
    
    # Message content
    html += f'{message}\n\n'
    html += '</div>\n\n'
    
    return html


def format_conversation_block(messages: list) -> str:
    """Format a block of messages for display."""
    output = ""
    for msg in messages:
        if len(msg) >= 3:
            agent, recipient, content = msg[:3]
            output += format_agent_message(agent, recipient, content)
    return output


def format_memory_indicator(round_num: int, memories: list) -> str:
    """Format a memory indicator showing what agents remember."""
    if not memories:
        return ""
    
    output = '<div style="background-color: #F5F5F5; '
    output += 'border: 2px dashed #9E9E9E; '
    output += 'padding: 12px; border-radius: 8px; margin: 15px 0; '
    output += 'color: #424242;">\n\n'
    output += f'**💭 DRAFT MEMORY (Round {round_num})**\n\n'
    
    for memory in memories:
        output += f'• {memory}\n'
    
    output += '\n</div>\n\n'
    return output


def create_mock_draft_visualization(draft: MultiAgentMockDraft, 
                                  round_num: int, pick_num: int) -> str:
    """Create a visual representation of the current draft state."""
    output = f"### 📋 Draft Board - Round {round_num}, Pick {pick_num}\n\n"
    
    # Create a simple draft board
    output += "| Team | Round 1 | Round 2 | Round 3 |\n"
    output += "|------|---------|---------|----------|\n"
    
    for team_num in range(1, 7):  # Show all 6 teams
        if team_num == draft.user_position:
            team_name = "**YOU**"
        else:
            agent = draft.agents.get(team_num)
            team_name = agent.team_name if agent else f"Team {team_num}"
        
        picks = draft.draft_board.get(team_num, [])
        row = f"| {team_name} "
        
        for round_idx in range(3):
            if round_idx < len(picks):
                row += f"| {picks[round_idx]} "
            else:
                row += "| - "
        
        row += "|\n"
        output += row
    
    return output


def run_interactive_mock_draft():
    """Run an interactive mock draft demo that yields formatted output."""
    
    # Initialize the draft
    draft = MultiAgentMockDraft(user_pick_position=4)
    
    # Skip introductions and go straight to commissioner welcome
    output = format_agent_message("commissioner", "ALL", 
        "Welcome to the draft! 6 teams, 3 rounds, snake format. Let's get started!")
    
    yield output
    
    # Track memories for demonstration
    draft_memories = []
    
    # Run the draft
    for round_num in range(1, 4):  # 3 rounds
        output += f"\n## 🔄 ROUND {round_num}\n\n"
        yield output
        
        # Snake draft order - 6 teams total
        if round_num % 2 == 1:
            pick_order = list(range(1, 7))  # 1-6 for odd rounds
        else:
            pick_order = list(range(6, 0, -1))  # 6-1 for even rounds
        
        for pick_in_round, team_num in enumerate(pick_order, 1):
            pick_num = (round_num - 1) * 6 + pick_in_round  # 6 teams per round
            
            # Show draft board at start of round
            if pick_in_round == 1:
                yield create_mock_draft_visualization(draft, round_num, pick_num)
                yield "\n"
            
            # Process the pick
            messages, waiting_for_user = draft.simulate_draft_turn(round_num, pick_num, team_num)
            
            # Show loading animation for AI agents
            if team_num != draft.user_position and team_num in draft.agents:
                agent = draft.agents[team_num]
                loading_msg = f"💭 *{agent.team_name} is contemplating their pick...*"
                output += format_agent_message("system", "ALL", loading_msg)
                yield output
                time.sleep(0.3)  # Brief pause for loading effect
            
            # Display messages with delays
            for msg in messages:
                if len(msg) >= 3:
                    agent, recipient, content = msg[:3]
                    output += format_agent_message(agent, recipient, content)
                    yield output
                    
                    # Add delays based on message type
                    if isinstance(agent, str) and agent.startswith("typing_"):
                        time.sleep(0.5)  # Short delay for typing indicators
                    else:
                        time.sleep(0.8)  # Slightly longer delay for actual messages
            
            if waiting_for_user is None:
                # Wait for user input (None means it's the user's turn)
                output += "\n**⏰ YOU'RE ON THE CLOCK! Type your pick below.**\n\n"
                yield (draft, output)  # Yield tuple to trigger UI update
                return  # Stop the generator here
            
            # Add memory indicators for multi-turn demonstration
            if round_num > 1 and pick_in_round % 2 == 0:
                # Show that agents remember previous picks
                if team_num in draft.agents:
                    agent = draft.agents[team_num]
                    if len(agent.picks) > 1:
                        memory = f"{agent.team_name} has drafted: {', '.join(agent.picks)}"
                        draft_memories.append(memory)
                
                if draft_memories:
                    output += format_memory_indicator(round_num, draft_memories[-2:])
                    yield output
            
            time.sleep(0.5)  # Brief pause between picks
        
        # End of round summary
        output += format_agent_message("commissioner", "ALL", 
            f"That's the end of Round {round_num}!")
        yield output
    
    # Final summary
    output += "\n## 📊 FINAL RESULTS\n\n"
    output += draft.get_draft_summary()
    yield output


def create_quick_multiagent_demo():
    """Create a quick demonstration of multi-agent communication."""
    
    output = "# 🤝 Multi-Agent Communication Demo\n\n"
    output += "> **Watch how agents discuss, debate, and remember!**\n\n"
    
    # Simulate a conversation about a pick
    messages = [
        ("📘", "ALL", "I'm taking **Justin Jefferson** with the first pick. Zero RB all the way!"),
        ("📙", "📘", "Leaving McCaffrey on the board? That's a mistake!"),
        ("📘", "📙", "RBs get injured. I'll take my chances with elite WRs."),
        ("📗", "ALL", "Interesting debate! I'll take whoever falls to me - best player available."),
    ]
    
    output += "## Turn 1: The First Pick Debate\n\n"
    
    for icon, recipient, message in messages:
        # Create a mock agent for formatting
        class MockAgent:
            def __init__(self, icon):
                self.icon = icon
                if icon == "📘":
                    self.team_name = "Team 1"
                elif icon == "📙":
                    self.team_name = "Team 3"
                elif icon == "📗":
                    self.team_name = "Team 2"
        
        agent = MockAgent(icon)
        output += format_agent_message(agent, recipient, message)
        yield output
        time.sleep(0.5)
    
    # Show memory
    output += format_memory_indicator(1, [
        "Team 1 committed to Zero RB strategy",
        "Team 3 prefers RB-heavy approach",
        "Teams are aware of each other's strategies"
    ])
    yield output
    
    # Continue conversation
    output += "\n## Turn 2: Reacting to Strategies\n\n"
    
    messages2 = [
        ("📙", "ALL", "With pick #3, I select **Christian McCaffrey**. Thanks for passing!"),
        ("📘", "📙", "Like I said, enjoy the injury risk. I'm happy with Jefferson."),
        ("📗", "ALL", "The top 2 players are gone. **CeeDee Lamb** gives me great value at #2."),
        ("📓", "ALL", "These conservative picks... I'm hunting for league-winners!")
    ]
    
    for icon, recipient, message in messages2:
        agent = MockAgent(icon)
        if icon == "📓":
            agent.team_name = "Team 5"
        output += format_agent_message(agent, recipient, message)
        yield output
        time.sleep(0.5)
    
    output += "\n## 🎯 Key Multi-Agent Features Demonstrated\n\n"
    output += "✅ **Agent-to-Agent Communication**: Direct responses between agents\n"
    output += "✅ **Strategy Awareness**: Agents know and react to others' strategies\n"
    output += "✅ **Memory Persistence**: Agents reference earlier statements\n"
    output += "✅ **Dynamic Adaptation**: Strategies influence the draft flow\n"
    
    yield output 