#!/usr/bin/env python3
"""
Fantasy Draft Multi-Agent Demo
Showcases multi-agent and multi-turn capabilities
"""

import os
import time
import gradio as gr
from typing import List, Tuple
from dotenv import load_dotenv
from agent import FantasyDraftAgent
from data import TOP_PLAYERS
from multiagent_draft import MultiAgentMockDraft
from multiagent_scenarios import (
    run_interactive_mock_draft,
    create_quick_multiagent_demo,
    format_conversation_block
)

# Load environment variables from .env file
load_dotenv()


class FantasyDraftApp:
    def __init__(self):
        self.current_draft = None  # Store the current mock draft
        self.draft_output = ""  # Store the draft output so far
    
    def run_multiagent_demo(self, demo_type: str):
        """Run a multi-agent demonstration."""
        if demo_type == "Quick A2A Demo":
            # Run the quick communication demo
            for output in create_quick_multiagent_demo():
                yield output
        elif demo_type == "Mock Draft":
            # Run the interactive mock draft
            from multiagent_scenarios import run_interactive_mock_draft
            
            # Reset any previous draft
            self.current_draft = None
            self.draft_output = ""
            
            # Run the draft generator
            draft_generator = run_interactive_mock_draft()
            
            for output in draft_generator:
                # Check if this is a tuple (draft state, output)
                if isinstance(output, tuple):
                    # This means it's the user's turn
                    self.current_draft, self.draft_output = output
                    # Add a special marker for Gradio to detect
                    yield self.draft_output + "\n<!--USER_TURN-->"
                    return
                else:
                    # Regular output
                    self.draft_output = output
                    yield output
        else:
            yield "Please select a demo type."
    
    def continue_mock_draft(self, player_name: str):
        """Continue the mock draft after user makes a pick."""
        if not self.current_draft:
            yield "No active draft. Please start a new mock draft."
            return
        
        if not player_name:
            yield self.draft_output + "\n\n⚠️ Please enter a player name!"
            return
        
        # Make the user's pick
        messages = self.current_draft.make_user_pick(player_name)
        self.draft_output += format_conversation_block(messages)
        yield self.draft_output
        
        # Continue the draft from where we left off
        # We need to track where we were in the draft
        total_picks = len([p for picks in self.current_draft.draft_board.values() for p in picks])
        current_round = ((total_picks - 1) // 6) + 1  # 6 teams per round
        
        # Continue with the rest of the draft
        import time
        from multiagent_scenarios import format_agent_message, format_memory_indicator, create_mock_draft_visualization
        
        draft_memories = []
        
        # Continue the draft
        for round_num in range(current_round, 4):  # Continue from current round to round 3
            if round_num > current_round:
                self.draft_output += f"\n## 🔄 ROUND {round_num}\n\n"
                yield self.draft_output
            
            # Snake draft order - 6 teams total
            if round_num % 2 == 1:
                pick_order = list(range(1, 7))  # 1-6 for odd rounds
            else:
                pick_order = list(range(6, 0, -1))  # 6-1 for even rounds
            
            # Calculate where we are in the current round
            picks_in_round = total_picks % 6  # 6 teams per round
            start_idx = picks_in_round if round_num == current_round else 0
            
            for pick_in_round, team_num in enumerate(list(pick_order)[start_idx:], start_idx + 1):
                pick_num = (round_num - 1) * 6 + pick_in_round  # 6 teams per round
                
                # Show draft board at start of round
                if pick_in_round == 1:
                    self.draft_output += create_mock_draft_visualization(self.current_draft, round_num, pick_num)
                    self.draft_output += "\n"
                    yield self.draft_output
                
                # Process the pick
                messages, result = self.current_draft.simulate_draft_turn(round_num, pick_num, team_num)
                
                # Display messages
                self.draft_output += format_conversation_block(messages)
                yield self.draft_output
                
                if result is None:
                    # It's the user's turn again
                    self.draft_output += "\n**⏰ YOU'RE ON THE CLOCK! Type your pick below.**\n\n"
                    yield self.draft_output + "\n<!--USER_TURN-->"
                    return
                
                # Add memory indicators
                if round_num > 1 and pick_in_round % 2 == 0:
                    if team_num in self.current_draft.agents:
                        agent = self.current_draft.agents[team_num]
                        if len(agent.picks) > 1:
                            memory = f"{agent.team_name} has drafted: {', '.join(agent.picks)}"
                            draft_memories.append(memory)
                    
                    if draft_memories:
                        self.draft_output += format_memory_indicator(round_num, draft_memories[-2:])
                        yield self.draft_output
                
                time.sleep(0.5)
            
            # End of round
            self.draft_output += format_agent_message("commissioner", "ALL", 
                f"That's the end of Round {round_num}!")
            yield self.draft_output
        
        # Final summary
        self.draft_output += "\n## 📊 FINAL RESULTS\n\n"
        self.draft_output += self.current_draft.get_draft_summary()
        yield self.draft_output
        
        # Clear the draft state
        self.current_draft = None


def create_gradio_interface():
    """Create the main Gradio interface."""
    app = FantasyDraftApp()
    
    with gr.Blocks(title="Fantasy Draft Multi-Agent Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🏈 Fantasy Draft Multi-Agent Demo
        
        Experience AI agents with distinct strategies competing in a mock draft!
        Watch them debate, adapt, and remember as they build their teams.
        """)
        
        gr.Markdown("## 🤝 Multi-Agent Mock Draft")
        gr.Markdown("""
        ### Features Demonstrated:
        - **Agent-to-Agent (A2A) Communication**: Agents comment on each other's picks
        - **Multi-Turn Memory**: Agents remember previous interactions and strategies
        - **Interactive Drafting**: You draft at position 4 with AI advisor guidance
        - **Distinct Personalities**: Each agent follows a unique draft strategy
        
        ### 🎭 Agent Roster
        - 📘 **Team 1**: Zero RB Strategy - Prioritizes WRs early
        - 📗 **Team 2**: Best Player Available - Always takes highest-ranked
        - 📙 **Team 3**: Robust RB Strategy - Loads up on RBs
        - 👤 **YOU**: Draft at position 4 with advisor help
        - 📓 **Team 5**: Upside Hunter - Targets breakout candidates
        - 📜 **Commissioner**: Manages the draft flow
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                multiagent_demo_select = gr.Dropdown(
                    choices=["Quick A2A Demo", "Mock Draft"],
                    value="Quick A2A Demo",
                    label="Select Demo Type",
                    info="Quick demo shows agent communication, Mock Draft is interactive"
                )
                run_multiagent_btn = gr.Button("▶️ Run Multi-Agent Demo", variant="primary", size="lg")
                
            with gr.Column(scale=2):
                multiagent_output = gr.Markdown(elem_classes=["multiagent-output"])
                
                # Mock draft interaction
                with gr.Row(visible=False) as mock_draft_controls:
                    with gr.Column():
                        draft_pick_input = gr.Textbox(
                            label="Your Pick",
                            placeholder="Type player name and press Enter (e.g., 'Justin Jefferson')",
                            elem_id="draft-pick-input"
                        )
                        submit_pick_btn = gr.Button("Submit Pick", variant="primary")
                        
                        # Available players display
                        with gr.Accordion("📋 Available Players", visible=False) as available_accordion:
                            available_players_display = gr.Textbox(
                                label="Top 20 Available",
                                lines=15,
                                interactive=False
                            )
        
        # Function to check if it's user's turn and show/hide controls
        def check_user_turn(output_text):
            """Check if output indicates it's user's turn."""
            if "<!--USER_TURN-->" in output_text:
                # Remove the marker from display
                clean_output = output_text.replace("<!--USER_TURN-->", "")
                # Get available players
                if app.current_draft:
                    available = app.current_draft.get_available_players()
                    available_text = "Available Players:\n\n"
                    for player in sorted(available)[:20]:  # Show top 20
                        if player in TOP_PLAYERS:
                            info = TOP_PLAYERS[player]
                            available_text += f"• {player} ({info['pos']}, {info['team']})\n"
                else:
                    available_text = "No draft active"
                
                return (
                    clean_output,  # Clean output
                    gr.update(visible=True),  # Show draft controls
                    gr.update(visible=True, open=True),  # Show available players and open it
                    available_text,  # Available players list
                    ""  # Clear the input
                )
            else:
                return (
                    output_text,  # Regular output
                    gr.update(visible=False),  # Hide draft controls
                    gr.update(visible=False),  # Hide available players
                    "",  # Clear available list
                    ""  # Clear the input
                )
        
        # Run multi-agent demo with control visibility handling
        def run_and_check(demo_type):
            """Run demo and check for user turn."""
            for output in app.run_multiagent_demo(demo_type):
                result = check_user_turn(output)
                yield result
        
        run_multiagent_btn.click(
            run_and_check,
            multiagent_demo_select,
            [multiagent_output, mock_draft_controls, available_accordion, available_players_display, draft_pick_input],
            show_progress=True
        )
        
        # Continue draft after user pick
        def submit_and_continue(player_name):
            """Submit pick and continue draft."""
            for output in app.continue_mock_draft(player_name):
                result = check_user_turn(output)
                yield result
        
        submit_pick_btn.click(
            submit_and_continue,
            draft_pick_input,
            [multiagent_output, mock_draft_controls, available_accordion, available_players_display, draft_pick_input],
            show_progress=True
        )
        
        # Also submit on enter
        draft_pick_input.submit(
            submit_and_continue,
            draft_pick_input,
            [multiagent_output, mock_draft_controls, available_accordion, available_players_display, draft_pick_input],
            show_progress=True
        )
        
        # Add custom CSS for better styling
        demo.css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        
        /* Multi-agent demo specific styles - Force text colors */
        .markdown-text div[style*="background-color"] {
            color: #212121 !important;
        }
        
        /* Force text color in all agent-specific styled divs */
        div[style*="#E3F2FD"], div[style*="#e3f2fd"] {
            color: #1a237e !important;
        }
        
        div[style*="#E8F5E9"], div[style*="#e8f5e9"] {
            color: #1b5e20 !important;
        }
        
        div[style*="#FFF3E0"], div[style*="#fff3e0"] {
            color: #e65100 !important;
        }
        
        div[style*="#FFEBEE"], div[style*="#ffebee"] {
            color: #b71c1c !important;
        }
        
        div[style*="#F5E6FF"], div[style*="#f5e6ff"] {
            color: #4a148c !important;
        }
        
        div[style*="#ECEFF1"], div[style*="#eceff1"] {
            color: #263238 !important;
        }
        
        div[style*="#E8EAF6"], div[style*="#e8eaf6"] {
            color: #1a237e !important;
        }
        
        div[style*="#F5F5F5"], div[style*="#f5f5f5"] {
            color: #424242 !important;
        }
        
        /* Specific styling for multiagent output message boxes only */
        .multiagent-output div[style*="background-color"] {
            color: #212121 !important;
        }
        
        .multiagent-output div[style*="background-color"] p,
        .multiagent-output div[style*="background-color"] span,
        .multiagent-output div[style*="background-color"] strong,
        .multiagent-output div[style*="background-color"] em {
            color: inherit !important;
        }
        
        /* Memory boxes specifically */
        .multiagent-output div[style*="#F5F5F5"] {
            color: #424242 !important;
        }
        
        #draft-pick-input {
            font-size: 1.1em;
        }
        """
    
    return demo


def main():
    """Launch the Gradio app."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("The app will launch but agent responses will fail without an API key.")
        print("Set it using: export OPENAI_API_KEY='your-key-here'\n")
    
    print("🚀 Launching Fantasy Draft Multi-Agent Demo...")
    print("📡 The app will be available at http://localhost:7860")
    
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True to create a public link
        show_error=True
    )


if __name__ == "__main__":
    main() 