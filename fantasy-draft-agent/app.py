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
    format_conversation_block
)

# Load environment variables from .env file
load_dotenv()


class FantasyDraftApp:
    def __init__(self):
        self.current_draft = None  # Store the current mock draft
        self.draft_output = ""  # Store the draft output so far
    
    def run_multiagent_demo(self):
        """Run the mock draft demonstration."""
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
        with gr.Column(elem_id="main-container"):
            gr.Markdown("""
            # 🏈 Fantasy Draft Multi-Agent Demo
            
            **Experience a living draft room** where 6 AI agents with distinct strategies compete, communicate, and remember. 
            You'll draft at position 4 with your advisor's guidance. Watch agents comment on picks, debate strategies, and adapt their plans!
            """)
            
            with gr.Tabs():
                # Demo Tab
                with gr.TabItem("🎮 Demo"):
                    # Single centered button
                    with gr.Row():
                        with gr.Column():
                            run_multiagent_btn = gr.Button("🏈 Start Mock Draft", variant="primary", size="lg", elem_id="start-button")
                    
                    # Main output area
                    multiagent_output = gr.Markdown(elem_classes=["multiagent-output"])
                    
                    # Mock draft interaction (hidden until needed)
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
                
                # How It Works Tab
                with gr.TabItem("🔧 How It Works"):
                    gr.Markdown("""
                    ## Technical Implementation
                    
                    This demo showcases advanced multi-agent capabilities using the **any-agent framework**.
                    
                    ### 🤖 Framework: any-agent (TinyAgent)
                    
                    - **Lightweight**: < 100 lines of core agent code
                    - **Flexible**: Supports multiple LLM providers (OpenAI, Anthropic, etc.)
                    - **Multi-turn ready**: Built-in conversation history management
                    - **Model**: GPT-4 (configurable)
                    
                    ### 🧠 Multi-Turn Memory System
                    
                    Each agent maintains:
                    - **Conversation History**: Full context of all interactions
                    - **Draft State**: Current picks, available players, round info
                    - **Strategy Memory**: Remembers own strategy and others' approaches
                    - **Pick History**: Tracks all selections for informed decisions
                    
                    ### 💬 Agent-to-Agent (A2A) Communication
                    
                    Agents can:
                    - **Comment on picks**: React to other agents' selections
                    - **Respond to comments**: Defend their strategies
                    - **Remember debates**: Reference earlier conversations
                    - **Adapt strategies**: Adjust based on draft flow
                    
                    ### 📊 Architecture Flow
                    """)
                    
                    gr.Markdown("""
                    ```
                    ┌─────────────────┐
                    │ User Clicks     │
                    │ Start Button    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Initialize 6    │
                    │ Unique Agents   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
              ┌─────────┐      ┌─────────┐
              │ Round 1 │      │ Round 2 │ (Snake)
              └────┬────┘      └────┬────┘
                   │                 │
                   ▼                 ▼
            Teams 1,2,3 ──► YOU ◄── Team 5,6
                   │         │        │
                   ▼         ▼        ▼
            [A2A Comments] [Pick] [Reactions]
                   │         │        │
                   └─────────┴────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Memory Updates   │
                    │ & Next Round     │
                    └─────────────────┘
                    ```""")
                    
                    gr.Markdown("""
                    ### 🎯 Key Features Demonstrated
                    
                    1. **Persistent Context**: Each agent remembers all previous interactions
                    2. **Strategic Personalities**: 5 distinct draft strategies competing
                    3. **Dynamic Adaptation**: Agents adjust based on draft progression
                    4. **Natural Dialogue**: Human-like commentary and debates
                    5. **User Integration**: Seamless human participation with AI guidance
                    
                    ### 📝 Implementation Details
                    
                    - **Agent Classes**: Inheritance-based design with base `DraftAgent`
                    - **Message Formatting**: Custom HTML/CSS for visual distinction
                    - **State Management**: Draft board tracking and validation
                    - **Memory Indicators**: Visual cues showing context retention
                    
                    ### 🚀 Why This Matters
                    
                    This demo proves that sophisticated multi-agent systems can be built with minimal code,
                    showcasing the power of modern LLMs when properly orchestrated. The any-agent framework
                    makes it easy to create agents that truly communicate and remember, not just respond.
                    """)
        
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
        def run_and_check():
            """Run demo and check for user turn."""
            for output in app.run_multiagent_demo():
                result = check_user_turn(output)
                yield result
        
        run_multiagent_btn.click(
            run_and_check,
            None,
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
            max-width: 800px !important;
            margin: 0 auto !important;
        }
        
        #main-container {
            text-align: center;
        }
        
        #start-button {
            margin: 20px auto !important;
            max-width: 300px !important;
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