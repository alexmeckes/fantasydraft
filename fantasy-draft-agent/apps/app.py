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
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import FantasyDraftAgent
from core.data import TOP_PLAYERS
from apps.multiagent_draft import MultiAgentMockDraft
from apps.multiagent_scenarios import (
    run_interactive_mock_draft,
    format_conversation_block,
    format_agent_message,
    format_memory_indicator,
    create_mock_draft_visualization
)

# Fix for litellm 1.72.4 OpenAI endpoint issue
# This ensures litellm uses the correct OpenAI API endpoint
os.environ['OPENAI_API_BASE'] = 'https://api.openai.com/v1'

# Load environment variables from .env file
load_dotenv()


class FantasyDraftApp:
    def __init__(self):
        self.current_draft = None  # Store the current mock draft
        self.draft_output = ""  # Store the draft output so far
    
    def run_multiagent_demo(self):
        """Run the mock draft demonstration."""
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
        
        # Display messages with inline typing effect
        for msg in messages:
            if len(msg) >= 3:
                agent, recipient, content = msg[:3]
                
                # Check if it's a typing indicator - skip it
                if isinstance(agent, str) and agent.startswith("typing_"):
                    continue  # Skip typing indicators, we'll handle inline
                else:
                    # Show "..." first for typing effect
                    typing_placeholder = format_agent_message(agent, recipient, "...")
                    self.draft_output += typing_placeholder
                    yield self.draft_output
                    time.sleep(0.5)  # Brief typing delay
                    
                    # Replace "..." with actual message
                    self.draft_output = self.draft_output.replace(typing_placeholder, "")
                    self.draft_output += format_agent_message(agent, recipient, content)
                    yield self.draft_output
                    time.sleep(1.0)  # Reading delay
        
        # Continue the draft from where we left off
        # We need to track where we were in the draft
        total_picks = len([p for picks in self.current_draft.draft_board.values() for p in picks])
        current_round = ((total_picks - 1) // 6) + 1  # 6 teams per round
        
        # Continue with the rest of the draft
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
                
                # Display messages with inline typing effect
                for msg in messages:
                    if len(msg) >= 3:
                        agent, recipient, content = msg[:3]
                        
                        # Check if it's a typing indicator - skip it
                        if isinstance(agent, str) and agent.startswith("typing_"):
                            continue  # Skip typing indicators, we'll handle inline
                        else:
                            # Show "..." first for typing effect
                            typing_placeholder = format_agent_message(agent, recipient, "...")
                            self.draft_output += typing_placeholder
                            yield self.draft_output
                            time.sleep(0.5)  # Brief typing delay
                            
                            # Replace "..." with actual message
                            self.draft_output = self.draft_output.replace(typing_placeholder, "")
                            self.draft_output += format_agent_message(agent, recipient, content)
                            yield self.draft_output
                            time.sleep(1.0)  # Reading delay
                
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
    
    with gr.Blocks(title="Fantasy Draft Multi-Agent Demo", theme=gr.themes.Glass()) as demo:
        with gr.Column(elem_id="main-container"):
            gr.Markdown("""
            # 🏈 Fantasy Draft Multi-Agent Demo
            
            **Experience the future of AI interaction:** Watch 6 intelligent agents compete in a fantasy football draft with distinct strategies, real-time trash talk, and persistent memory.
            """)
            
            with gr.Tabs():
                # Demo Tab
                with gr.TabItem("🎮 Demo"):
                    # Show agent cards first
                    gr.Markdown("""
                    ### 🏈 Meet Your Competition
                    
                    You'll be drafting at **Position 4** with these AI opponents:
                    """)
                    
                    # Agent cards in a grid - all in one row
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            <div style="background-color: #E3F2FD; border-left: 4px solid #1976D2; padding: 15px; border-radius: 8px;">
                            
                            <h4 style="color: #1a237e !important; margin: 0 0 10px 0;">📘🤓 Team 1 - Zero RB</h4>
                            
                            <p style="color: #1976D2 !important; font-style: italic; margin: 10px 0; font-size: 0.95em;">"RBs get injured. I'll build around elite WRs."</p>
                            
                            <ul style="color: #1a237e !important; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #1a237e !important;">Avoids RBs early</li>
                            <li style="color: #1a237e !important;">Loads up on WRs</li>
                            <li style="color: #1a237e !important;">Gets RB value late</li>
                            </ul>
                            </div>
                            """)
                        
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            <div style="background-color: #E8F5E9; border-left: 4px solid #388E3C; padding: 15px; border-radius: 8px;">
                            
                            <h4 style="color: #1b5e20 !important; margin: 0 0 10px 0;">📗🧑‍💼 Team 2 - BPA</h4>
                            
                            <p style="color: #2e7d32 !important; font-style: italic; margin: 10px 0; font-size: 0.95em;">"Value is value. I don't reach for needs."</p>
                            
                            <ul style="color: #1b5e20 !important; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #1b5e20 !important;">Pure value drafting</li>
                            <li style="color: #1b5e20 !important;">Ignores needs</li>
                            <li style="color: #1b5e20 !important;">Mocks reaching</li>
                            </ul>
                            </div>
                            """)
                        
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            <div style="background-color: #FFF3E0; border-left: 4px solid #F57C00; padding: 15px; border-radius: 8px;">
                            
                            <h4 style="color: #e65100 !important; margin: 0 0 10px 0;">📙🧔 Team 3 - Robust RB</h4>
                            
                            <p style="color: #ef6c00 !important; font-style: italic; margin: 10px 0; font-size: 0.95em;">"RBs win championships. Period."</p>
                            
                            <ul style="color: #e65100 !important; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #e65100 !important;">RBs in rounds 1-2</li>
                            <li style="color: #e65100 !important;">Old-school approach</li>
                            <li style="color: #e65100 !important;">Foundation first</li>
                            </ul>
                            </div>
                            """)
                        
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            <div style="background-color: #E8EAF6; border-left: 4px solid #3F51B5; padding: 15px; border-radius: 8px;">
                            
                            <h4 style="color: #1a237e !important; margin: 0 0 10px 0;">👤 Position 4 - YOU</h4>
                            
                            <p style="color: #3949ab !important; font-style: italic; margin: 10px 0; font-size: 0.95em;">Your draft position with AI guidance</p>
                            
                            <ul style="color: #1a237e !important; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #1a237e !important;">📕🧙 Strategic advisor</li>
                            <li style="color: #1a237e !important;">Real-time guidance</li>
                            <li style="color: #1a237e !important;">Roster analysis</li>
                            </ul>
                            </div>
                            """)
                        
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            <div style="background-color: #F5E6FF; border-left: 4px solid #7B1FA2; padding: 15px; border-radius: 8px;">
                            
                            <h4 style="color: #4a148c !important; margin: 0 0 10px 0;">📓🤠 Team 5 - Upside</h4>
                            
                            <p style="color: #6a1b9a !important; font-style: italic; margin: 10px 0; font-size: 0.95em;">"Safe picks are for losers!"</p>
                            
                            <ul style="color: #4a148c !important; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #4a148c !important;">Seeks breakouts</li>
                            <li style="color: #4a148c !important;">High risk/reward</li>
                            <li style="color: #4a148c !important;">Mocks safety</li>
                            </ul>
                            </div>
                            """)
                        
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            <div style="background-color: #E8F5E9; border-left: 4px solid #388E3C; padding: 15px; border-radius: 8px;">
                            
                            <h4 style="color: #1b5e20 !important; margin: 0 0 10px 0;">📗👨‍🏫 Team 6 - BPA</h4>
                            
                            <p style="color: #2e7d32 !important; font-style: italic; margin: 10px 0; font-size: 0.95em;">"Another value drafter to punish reaches."</p>
                            
                            <ul style="color: #1b5e20 !important; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #1b5e20 !important;">Takes obvious value</li>
                            <li style="color: #1b5e20 !important;">Disciplined approach</li>
                            <li style="color: #1b5e20 !important;">No sentiment</li>
                            </ul>
                            </div>
                            """)
                    
                    gr.Markdown("""
                    ### 🎮 Draft Format
                    - **3 Rounds** of snake draft (1→6, 6→1, 1→6)
                    - **Real-time trash talk** between picks
                    - **Strategic advisor** guides your selections
                    - **Memory system** - agents remember and reference earlier picks
                    
                    Ready to experience the most realistic AI draft room?
                    """)
                    
                    # Start button at the bottom
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
                    #### 1️⃣ INITIALIZATION
                    User clicks "Start Mock Draft" → System creates 6 agents
                    
                    #### 2️⃣ AGENT SETUP
                    - **Team 1**: Zero RB Strategy
                    - **Team 2**: Best Player Available  
                    - **Team 3**: Robust RB Strategy
                    - **YOU**: Position 4 (with Advisor)
                    - **Team 5**: Upside Hunter
                    - **Team 6**: Best Player Available
                    
                    #### 3️⃣ DRAFT FLOW (3 Rounds)
                    - **Round 1**: Pick Order 1→2→3→YOU→5→6
                    - **Round 2**: Pick Order 6→5→YOU→3→2→1 (Snake)
                    - **Round 3**: Pick Order 1→2→3→YOU→5→6
                    
                    #### 4️⃣ EACH PICK TRIGGERS
                    - Agent makes selection based on strategy
                    - Other agents comment (A2A communication)
                    - Original agent may respond
                    - All agents update their memory
                    
                    #### 5️⃣ USER'S TURN
                    - Advisor analyzes draft state
                    - User sees available players
                    - User makes pick
                    - All agents react to user's choice
                    
                    #### 6️⃣ MEMORY & CONTEXT
                    - Each agent remembers all picks
                    - Agents reference earlier conversations
                    - Strategies adapt based on draft flow
                    - Visual memory indicators show retention
                    """)
                    
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
        /* Force white text on dark background for all main content */
        .gradio-container {
            max-width: 800px !important;
            margin: 0 auto !important;
            color: white !important;
        }
        
        /* Ensure all text elements are white by default */
        .gradio-container p,
        .gradio-container h1,
        .gradio-container h2,
        .gradio-container h3,
        .gradio-container h4,
        .gradio-container h5,
        .gradio-container h6,
        .gradio-container span,
        .gradio-container div,
        .gradio-container label,
        .gradio-container .markdown,
        .gradio-container .prose {
            color: white !important;
        }
        
        /* Ensure markdown content is white */
        .markdown-text,
        .markdown-text p,
        .markdown-text li,
        .markdown-text ul,
        .markdown-text ol {
            color: white !important;
        }
        
        #main-container {
            text-align: center;
            color: white !important;
        }
        
        /* Left-align text in How It Works tab */
        .tabitem:nth-child(2) {
            text-align: left !important;
        }
        
        #start-button {
            margin: 20px auto !important;
            max-width: 300px !important;
        }
        
        /* Only force dark text inside colored message boxes */
        div[style*="background-color"][style*="border-left"] {
            color: #212121 !important;
        }
        
        div[style*="background-color"][style*="border-left"] p,
        div[style*="background-color"][style*="border-left"] strong,
        div[style*="background-color"][style*="border-left"] em,
        div[style*="background-color"][style*="border-left"] span,
        div[style*="background-color"][style*="border-left"] li,
        div[style*="background-color"][style*="border-left"] ul,
        div[style*="background-color"][style*="border-left"] h1,
        div[style*="background-color"][style*="border-left"] h2,
        div[style*="background-color"][style*="border-left"] h3,
        div[style*="background-color"][style*="border-left"] h4 {
            color: #212121 !important;
        }
        
        /* System messages with yellow background */
        div[style*="#FFF9C4"] {
            color: #F57C00 !important;
        }
        
        /* Memory boxes */
        div[style*="#F5F5F5"] {
            color: #424242 !important;
        }
        
        #draft-pick-input {
            font-size: 1.1em;
        }
        
        /* Ensure tab labels are visible */
        .tab-nav button {
            color: white !important;
        }
        
        /* Ensure multiagent output text is white */
        .multiagent-output {
            color: white !important;
        }
        
        .multiagent-output p,
        .multiagent-output h1,
        .multiagent-output h2,
        .multiagent-output h3,
        .multiagent-output h4,
        .multiagent-output h5,
        .multiagent-output h6,
        .multiagent-output span,
        .multiagent-output div {
            color: white !important;
        }
        
        /* Specific rules for dark mode - target Gradio's dark theme class */
        .dark .gradio-container,
        .dark .gradio-container *:not([style*="background-color"]) {
            color: white !important;
        }
        
        /* Ensure description text under title is white */
        .gradio-container > div > div > div > p {
            color: white !important;
        }
        
        /* Tab content text */
        .tabitem .markdown-text {
            color: white !important;
        }
        
        /* Input labels and text */
        .gradio-container label {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        
        /* Button text that's not in primary buttons */
        button:not(.primary) {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        
        /* Fix for bold player names - ensure they're visible */
        .multiagent-output strong,
        .multiagent-output b {
            color: inherit !important;
            font-weight: 700;
        }
        
        /* Ensure bold text in message backgrounds has proper color */
        div[style*="background-color"] strong,
        div[style*="background-color"] b {
            color: inherit !important;
        }
        
        /* Specific fix for bold text in different message backgrounds */
        div[style*="background-color: #E3F2FD"] strong,  /* Team messages */
        div[style*="background-color: #FFF8E1"] strong,  /* Commissioner */
        div[style*="background-color: #FFEBEE"] strong,  /* Advisor */
        div[style*="background-color: #F3E5F5"] strong { /* Memory */
            color: #1a1a1a !important;
        }
        
        /* Inline typing effect */
        .typing-dots {
            animation: pulse 1.0s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        """
    
    return demo


def main():
    """Launch the Gradio app."""
    import sys
    
    # Check for --share flag
    share_mode = "--share" in sys.argv or "-s" in sys.argv
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("The app will launch but agent responses will fail without an API key.")
        print("Set it using: export OPENAI_API_KEY='your-key-here'\n")
    
    print("🚀 Launching Fantasy Draft Multi-Agent Demo...")
    
    if share_mode:
        print("🌐 Creating public share link (expires in 72 hours)...")
        print("📡 Please wait for the public URL...\n")
    else:
        print("📡 The app will be available at http://localhost:7860")
        print("💡 Tip: Use 'python app.py --share' to create a public link\n")
    
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share_mode,  # Enable sharing if flag is present
        show_error=True
    )


if __name__ == "__main__":
    main() 