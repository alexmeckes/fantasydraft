#!/usr/bin/env python3
"""
Fantasy Draft Multi-Agent Demo
Multi-agent system using the any-agent framework for fantasy football drafts
"""

import os
import time
import gradio as gr
import asyncio
import nest_asyncio
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import FantasyDraftAgent
from core.data import TOP_PLAYERS
from core.constants import (
    TYPING_DELAY_SECONDS,
    MESSAGE_DELAY_SECONDS,
)

from apps.multiagent_draft import MultiAgentMockDraft
from apps.multiagent_scenarios import (
    run_interactive_mock_draft,
    format_conversation_block,
    format_agent_message,
    format_memory_indicator,
    create_mock_draft_visualization
)

# Apply nest_asyncio for async in Gradio
nest_asyncio.apply()

# Fix for litellm 1.72.4 OpenAI endpoint issue
os.environ['OPENAI_API_BASE'] = 'https://api.openai.com/v1'

# Load environment variables
load_dotenv()


class FantasyDraftApp:
    def __init__(self):
        self.current_draft = None  # Store the current mock draft
        self.draft_output = ""  # Store the draft output so far
        self.custom_prompts = {}  # Store custom agent prompts
    
    def run_multiagent_demo(self):
        """Run the mock draft demonstration."""
        # Reset any previous draft
        self.current_draft = None
        self.draft_output = ""
        
        # Debug: Log custom prompts
        print(f"DEBUG: Starting draft with custom_prompts: {len(self.custom_prompts)} teams customized")
        for team_num, prompt in self.custom_prompts.items():
            print(f"DEBUG: Team {team_num} has custom prompt ({len(prompt)} chars)")
        
        # Use basic multiagent draft with custom prompts
        draft_generator = run_interactive_mock_draft(custom_prompts=self.custom_prompts)
        
        for output in draft_generator:
            if isinstance(output, tuple):
                # This means it's the user's turn
                self.current_draft, self.draft_output = output
                yield self.draft_output + "\n<!--USER_TURN-->"
                return
            else:
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
                    continue
                else:
                    # Show "..." first for typing effect
                    typing_placeholder = format_agent_message(agent, recipient, "...")
                    self.draft_output += typing_placeholder
                    yield self.draft_output
                    time.sleep(TYPING_DELAY_SECONDS)
                    
                    # Replace "..." with actual message
                    self.draft_output = self.draft_output.replace(typing_placeholder, "")
                    self.draft_output += format_agent_message(agent, recipient, content)
                    yield self.draft_output
                    time.sleep(MESSAGE_DELAY_SECONDS)
        
        # Continue with the rest of the draft
        yield from self.continue_basic_multiagent_draft()
    
    def continue_basic_multiagent_draft(self):
        """Continue basic multiagent draft after user pick."""
        # Calculate where we are
        total_picks = len([p for picks in self.current_draft.draft_board.values() for p in picks])
        current_round = ((total_picks - 1) // 6) + 1
        
        # Continue from where we left off
        for round_num in range(current_round, 4):  # Continue through round 3
            if round_num > current_round:
                self.draft_output += f"\n## 🔄 ROUND {round_num}\n\n"
                yield self.draft_output
            
            # Snake draft order
            if round_num % 2 == 1:
                pick_order = list(range(1, 7))
            else:
                pick_order = list(range(6, 0, -1))
            
            # Calculate where we are in this round
            picks_in_round = total_picks % 6
            if round_num == current_round:
                # Skip picks already made
                start_idx = picks_in_round
            else:
                start_idx = 0
            
            for pick_in_round, team_num in enumerate(pick_order[start_idx:], start_idx + 1):
                pick_num = (round_num - 1) * 6 + pick_in_round
                
                # Show draft board at start of round
                if pick_in_round == 1:
                    self.draft_output += create_mock_draft_visualization(self.current_draft, round_num, pick_num)
                    self.draft_output += "\n"
                    yield self.draft_output
                
                if team_num == 4:  # User's turn
                    # Get advisor recommendation
                    advisor = self.current_draft.user_advisor
                    
                    # Get available players
                    all_picked = [p for picks in self.current_draft.draft_board.values() for p in picks]
                    available = [p for p in TOP_PLAYERS.keys() if p not in all_picked]
                    
                    # Get other agent strategies for advisor context
                    strategies = {f"Team {i}": agent.strategy for i, agent in self.current_draft.agents.items()}
                    
                    # Get advisor recommendation
                    advice = advisor.advise_user(available, self.current_draft.draft_board, strategies)
                    
                    # Show advisor message
                    self.draft_output += format_agent_message(advisor, "USER", advice)
                    yield self.draft_output
                    
                    self.draft_output += "\n**⏰ YOU'RE ON THE CLOCK! Type your pick below.**\n\n"
                    yield self.draft_output + "\n<!--USER_TURN-->"
                    return
                else:
                    # AI agent pick
                    messages, _ = self.current_draft.simulate_draft_turn(round_num, pick_num, team_num)
                    
                    # Display messages with typing effect
                    for msg in messages:
                        if len(msg) >= 3:
                            agent, recipient, content = msg[:3]
                            
                            # Show "..." first for typing effect
                            typing_placeholder = format_agent_message(agent, recipient, "...")
                            self.draft_output += typing_placeholder
                            yield self.draft_output
                            time.sleep(TYPING_DELAY_SECONDS)
                            
                            # Replace with actual message
                            self.draft_output = self.draft_output.replace(typing_placeholder, "")
                            self.draft_output += format_agent_message(agent, recipient, content)
                            yield self.draft_output
                            time.sleep(MESSAGE_DELAY_SECONDS)
                    
                    time.sleep(TYPING_DELAY_SECONDS)
            
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
    
    with gr.Blocks(title="Fantasy Draft Multi-Agent Demo", theme=gr.themes.Soft()) as demo:
        # Create state for each user session
        app_state = gr.State(None)
        
        with gr.Column(elem_id="main-container"):
            gr.Markdown("""
            # 🏈 Fantasy Draft Multi-Agent Demo
            
            **Multi-agent system demo using the any-agent framework:** Watch 6 AI agents draft fantasy football teams while maintaining conversation history, reacting to each other's picks, and following distinct strategies.
            """)
            
            with gr.Tabs():
                # Demo Tab
                with gr.TabItem("🎮 Demo"):
                    # Show agent cards
                    gr.Markdown("""
                    ### 🏈 Meet Your Competition
                    
                    You'll be drafting at **Position 4** with these AI opponents:
                    """)
                    
                    # Store agent prompts in state
                    agent_prompts = gr.State({})
                    
                    # Agent cards with settings buttons
                    # First row of agents
                    with gr.Row():
                        # Team 1 - Zero RB
                        with gr.Column(scale=1):
                            with gr.Group():
                                gr.HTML("""
                                <div style="background-color: #E3F2FD; border-left: 4px solid #1976D2; padding: 15px; border-radius: 8px;">
                                <h4 style="color: #0d47a1; margin: 0 0 10px 0;">📘🤓 Team 1 - Zero RB</h4>
                                <p style="color: #424242; font-style: italic; margin: 10px 0; font-size: 0.95em;">"RBs get injured. I'll build around elite WRs."</p>
                                <ul style="color: #424242; font-size: 0.9em; margin: 0; padding-left: 20px;">
                                <li style="color: #424242;">Avoids RBs early</li>
                                <li style="color: #424242;">Loads up on WRs</li>
                                <li style="color: #424242;">Gets RB value late</li>
                                </ul>
                                </div>
                                """)
                                team1_settings_btn = gr.Button("⚙️ Customize", size="sm", variant="secondary")
                                with gr.Column(visible=False) as team1_prompt_col:
                                    team1_prompt = gr.Textbox(
                                        label="Team 1 Personality & Strategy",
                                        value="""You are Team 1, a fantasy football manager with Zero RB strategy.

PERSONALITY & STRATEGY:
- Use LOTS of emojis that match your strategy! 🔥
- Be EXTREMELY dramatic and over-the-top! 
- Take your philosophy to the EXTREME!
- MOCK other strategies viciously!
- Use CAPS for emphasis!
- Make BOLD predictions!
- Reference previous interactions with SPITE!
- Build INTENSE rivalries!
- Your responses should be ENTERTAINING and MEMORABLE!

Your EXTREME philosophy: RUNNING BACKS ARE DEAD TO ME! 💀 While others waste early picks on injury-prone RBs who'll disappoint them by Week 4, I'm building an AIR RAID OFFENSE with elite WRs! 🚀 My receivers will be FEASTING while your precious RBs are in the medical tent! 🏥

BE LOUD! BE PROUD! BE UNFORGETTABLE! 🎯""",
                                        lines=15,
                                        interactive=True,
                                        info="Customize personality and strategy."
                                    )
                                    team1_save_btn = gr.Button("💾 Save", size="sm", variant="primary")
                        
                        # Team 2 - BPA
                        with gr.Column(scale=1):
                            with gr.Group():
                                gr.HTML("""
                                <div style="background-color: #E8F5E9; border-left: 4px solid #388E3C; padding: 15px; border-radius: 8px;">
                                <h4 style="color: #1b5e20; margin: 0 0 10px 0;">📗🧑‍💼 Team 2 - BPA</h4>
                                <p style="color: #424242; font-style: italic; margin: 10px 0; font-size: 0.95em;">"Value is value. I don't reach for needs."</p>
                                <ul style="color: #424242; font-size: 0.9em; margin: 0; padding-left: 20px;">
                                <li style="color: #424242;">Pure value drafting</li>
                                <li style="color: #424242;">Ignores needs</li>
                                <li style="color: #424242;">Mocks reaching</li>
                                </ul>
                                </div>
                                """)
                                team2_settings_btn = gr.Button("⚙️ Customize", size="sm", variant="secondary")
                                with gr.Column(visible=False) as team2_prompt_col:
                                    team2_prompt = gr.Textbox(
                                        label="Team 2 Personality & Strategy",
                                        value="""You are Team 2, a fantasy football manager with BPA (Best Player Available) strategy.

PERSONALITY & STRATEGY:
- Use LOTS of emojis that match your strategy! 💎
- Be EXTREMELY condescending about others' reaches!
- Act like the SMARTEST person in the room!
- MOCK positional bias with FURY!
- Use CAPS for emphasis!
- Quote "value" constantly!
- Shame others for their TERRIBLE process!
- Your responses should be ARROGANT and CUTTING!

Your EXTREME philosophy: PROCESS OVER EVERYTHING! 📊 I don't care about your "needs" or "strategies" - I take the BEST PLAYER on my board, PERIOD! 💯 While you CLOWNS reach for positions, I'm accumulating VALUE that will BURY you! 📈 Your emotional drafting DISGUSTS me!

BE RUTHLESS! BE RIGHT! BE THE VALUE VULTURE! 🦅""",
                                        lines=15,
                                        interactive=True,
                                        info="Customize personality and strategy."
                                    )
                                    team2_save_btn = gr.Button("💾 Save", size="sm", variant="primary")
                        
                        # Team 3 - Robust RB
                        with gr.Column(scale=1):
                            with gr.Group():
                                gr.HTML("""
                                <div style="background-color: #FFF3E0; border-left: 4px solid #F57C00; padding: 15px; border-radius: 8px;">
                                <h4 style="color: #e65100; margin: 0 0 10px 0;">📙🧔 Team 3 - Robust RB</h4>
                                <p style="color: #424242; font-style: italic; margin: 10px 0; font-size: 0.95em;">"RBs win championships. Period."</p>
                                <ul style="color: #424242; font-size: 0.9em; margin: 0; padding-left: 20px;">
                                <li style="color: #424242;">RBs in rounds 1-2</li>
                                <li style="color: #424242;">Old-school approach</li>
                                <li style="color: #424242;">Foundation first</li>
                                </ul>
                                </div>
                                """)
                                team3_settings_btn = gr.Button("⚙️ Customize", size="sm", variant="secondary")
                                with gr.Column(visible=False) as team3_prompt_col:
                                    team3_prompt = gr.Textbox(
                                        label="Team 3 Personality & Strategy",
                                        value="""You are Team 3, a fantasy football manager with Robust RB strategy.

PERSONALITY & STRATEGY:
- Use LOTS of emojis that match your strategy! 💪
- Be EXTREMELY old-school and stubborn!
- HATE the modern passing game!
- DESPISE Zero RB with PASSION!
- Use CAPS for emphasis!
- Talk about "FOUNDATION" and "BEDROCK"!
- Act like it's still 2005!
- Your responses should be GRUMPY and TRADITIONAL!

Your EXTREME philosophy: GROUND AND POUND FOREVER! 🏃‍♂️ These young punks with their "pass-catching backs" and "satellite players" make me SICK! 🤮 Give me WORKHORSE RBs who get 25+ touches! That's REAL FOOTBALL! While you're playing fantasy, I'm building a FORTRESS! 🏰

BE STUBBORN! BE TRADITIONAL! ESTABLISH THE RUN! 🏈""",
                                        lines=15,
                                        interactive=True,
                                        info="Customize personality and strategy."
                                    )
                                    team3_save_btn = gr.Button("💾 Save", size="sm", variant="primary")
                    
                    # Second row of agents
                    with gr.Row():
                        # Team 4 - User
                        with gr.Column(scale=1):
                            gr.HTML("""
                            <div style="background-color: #E8EAF6; border-left: 4px solid #3F51B5; padding: 15px; border-radius: 8px;">
                            <h4 style="color: #1a237e; margin: 0 0 10px 0;">👤 Position 4 - YOU</h4>
                            <p style="color: #424242; font-style: italic; margin: 10px 0; font-size: 0.95em;">Your draft position with AI guidance</p>
                            <ul style="color: #424242; font-size: 0.9em; margin: 0; padding-left: 20px;">
                            <li style="color: #424242;">📕🧙 Strategic advisor</li>
                            <li style="color: #424242;">Real-time guidance</li>
                            <li style="color: #424242;">Roster analysis</li>
                            </ul>
                            </div>
                            """)
                        
                        # Team 5 - Upside
                        with gr.Column(scale=1):
                            with gr.Group():
                                gr.HTML("""
                                <div style="background-color: #F5E6FF; border-left: 4px solid #7B1FA2; padding: 15px; border-radius: 8px;">
                                <h4 style="color: #4a148c; margin: 0 0 10px 0;">📓🤠 Team 5 - Upside</h4>
                                <p style="color: #424242; font-style: italic; margin: 10px 0; font-size: 0.95em;">"Safe picks are for losers!"</p>
                                <ul style="color: #424242; font-size: 0.9em; margin: 0; padding-left: 20px;">
                                <li style="color: #424242;">Seeks breakouts</li>
                                <li style="color: #424242;">High risk/reward</li>
                                <li style="color: #424242;">Mocks safety</li>
                                </ul>
                                </div>
                                """)
                                team5_settings_btn = gr.Button("⚙️ Customize", size="sm", variant="secondary")
                                with gr.Column(visible=False) as team5_prompt_col:
                                    team5_prompt = gr.Textbox(
                                        label="Team 5 Personality & Strategy",
                                        value="""You are Team 5, a fantasy football manager with Upside Hunter strategy.

PERSONALITY & STRATEGY:
- Use LOTS of emojis that match your strategy! 🚀
- Be EXTREMELY risk-seeking and wild!
- HATE safe, boring picks!
- Talk about CEILING and EXPLOSIVENESS!
- Use CAPS for emphasis!
- Mock "floor" players constantly!
- Be a GAMBLER at heart!
- Your responses should be CHAOTIC and EXCITING!

Your EXTREME philosophy: BOOM OR BUST, BABY! 💥 Why settle for consistent mediocrity when you can have LEAGUE-WINNING UPSIDE?! 🏆 I'd rather finish LAST than FOURTH! Your "safe" picks make me YAWN! 🥱 I'm here to DESTROY leagues, not participate in them!

BE BOLD! BE RECKLESS! SWING FOR THE FENCES! ⚡""",
                                        lines=15,
                                        interactive=True,
                                        info="Customize personality and strategy."
                                    )
                                    team5_save_btn = gr.Button("💾 Save", size="sm", variant="primary")
                        
                        # Team 6 - BPA
                        with gr.Column(scale=1):
                            with gr.Group():
                                gr.HTML("""
                                <div style="background-color: #E8F5E9; border-left: 4px solid #388E3C; padding: 15px; border-radius: 8px;">
                                <h4 style="color: #1b5e20; margin: 0 0 10px 0;">📗👨‍🏫 Team 6 - BPA</h4>
                                <p style="color: #424242; font-style: italic; margin: 10px 0; font-size: 0.95em;">"Another value drafter to punish reaches."</p>
                                <ul style="color: #424242; font-size: 0.9em; margin: 0; padding-left: 20px;">
                                <li style="color: #424242;">Takes obvious value</li>
                                <li style="color: #424242;">Disciplined approach</li>
                                <li style="color: #424242;">No sentiment</li>
                                </ul>
                                </div>
                                """)
                                team6_settings_btn = gr.Button("⚙️ Customize", size="sm", variant="secondary")
                                with gr.Column(visible=False) as team6_prompt_col:
                                    team6_prompt = gr.Textbox(
                                        label="Team 6 Personality & Strategy",
                                        value="""You are Team 6, a fantasy football manager with BPA (Best Player Available) strategy.

PERSONALITY & STRATEGY:
- Use LOTS of emojis that match your strategy! 📊
- Be EXTREMELY analytical and cold!
- Act like a PROFESSOR lecturing idiots!
- Quote analytics and math constantly!
- Use CAPS for emphasis!
- Be DISGUSTED by emotional drafting!
- Mock "gut feelings" ruthlessly!
- Your responses should be PEDANTIC and SUPERIOR!

Your EXTREME philosophy: THE SPREADSHEET NEVER LIES! 📈 I have SEVENTEEN models that all agree - you're drafting like CHILDREN! 🧮 Your "hunches" and "feelings" are WORTHLESS compared to my ALGORITHMS! While you follow your heart, I follow the DATA!

BE ANALYTICAL! BE MERCILESS! TRUST THE PROCESS! 🤖""",
                                        lines=15,
                                        interactive=True,
                                        info="Customize personality and strategy."
                                    )
                                    team6_save_btn = gr.Button("💾 Save", size="sm", variant="primary")
                    
                    gr.Markdown("""
                    ### 🎮 Draft Format
                    * **3 Rounds** of snake draft (1→6, 6→1, 1→6)
                    * **Real-time trash talk** between picks
                    * **Strategic advisor** guides your selections
                    * **Memory system** - agents remember and reference earlier picks
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
                    
                    ### 💬 Single-Process Multi-Agent Communication
                    
                    - **In-Memory Communication**: Agents interact directly via method calls
                    - **Shared Draft State**: All agents see the same draft board
                    - **Fast Execution**: No network overhead
                    - **Conversation Memory**: Each agent remembers interactions
                    
                    ### 📊 Architecture Flow
                    
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
                    - Other agents comment based on rivalries
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
        
        # Function to check if it's user's turn and show/hide controls
        def check_user_turn(output_text, app):
            """Check if output indicates it's user's turn."""
            if "<!--USER_TURN-->" in output_text:
                # Remove the marker from display
                clean_output = output_text.replace("<!--USER_TURN-->", "")
                # Get available players
                if app and app.current_draft:
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
        
        # Toggle prompt visibility
        def toggle_prompt_visibility():
            return gr.update(visible=True)
        
        # Save prompt
        def save_prompt(team_num, prompt_text, app, prompts_dict):
            """Save a custom prompt for a team."""
            if app is None:
                app = FantasyDraftApp()
            prompts_dict[team_num] = prompt_text
            app.custom_prompts = prompts_dict
            return app, prompts_dict, gr.update(visible=False)
        
        # Run and check function - with streaming support
        def run_and_check(app, prompts_dict, team1_val, team2_val, team3_val, team5_val, team6_val):
            """Run the draft and check for user turns."""
            try:
                if app is None:
                    app = FantasyDraftApp()
                
                # Collect all current textbox values (whether saved or not)
                current_prompts = {}
                if team1_val and team1_val.strip():
                    current_prompts[1] = team1_val
                if team2_val and team2_val.strip():
                    current_prompts[2] = team2_val
                if team3_val and team3_val.strip():
                    current_prompts[3] = team3_val
                if team5_val and team5_val.strip():
                    current_prompts[5] = team5_val
                if team6_val and team6_val.strip():
                    current_prompts[6] = team6_val
                
                # ALWAYS update custom prompts before running draft
                app.custom_prompts = current_prompts
                
                generator = app.run_multiagent_demo()
                output = ""
                
                # Stream updates while draft is running
                for chunk in generator:
                    output = chunk
                    # For streaming, we need to yield all 6 values
                    # Keep controls hidden during streaming
                    yield output, app, gr.update(visible=False), gr.update(visible=False), gr.update(value=""), ""
                    
                    # Check if it's user's turn
                    if "<!--USER_TURN-->" in output:
                        break
                
                # Final yield with turn check and proper UI updates
                clean_output, controls_update, accordion_update, available_text, input_clear = check_user_turn(output, app)
                yield clean_output, app, controls_update, accordion_update, available_text, input_clear
                
            except Exception as e:
                import traceback
                error_msg = f"## ❌ Error Starting Draft\n\n"
                error_msg += f"**Error Type:** {type(e).__name__}\n"
                error_msg += f"**Error Message:** {str(e)}\n\n"
                
                # Get the full traceback
                tb_str = traceback.format_exc()
                print(f"Full error traceback:\n{tb_str}")  # Log to console
                
                # Check for common issues
                if "OPENAI_API_KEY" in str(e) or "api_key" in str(e).lower():
                    error_msg += "**Solution:** Please set your OpenAI API key in Hugging Face Space Settings:\n"
                    error_msg += "1. Go to Settings → Repository secrets\n"
                    error_msg += "2. Add a new secret named `OPENAI_API_KEY`\n"
                    error_msg += "3. Paste your OpenAI API key as the value\n"
                    error_msg += "4. Restart the Space\n"
                elif "NoneType" in str(e):
                    error_msg += "**Details:** A required value is None. This might be a configuration issue.\n"
                    error_msg += "Please check the console logs for the full error trace.\n"
                else:
                    error_msg += "**Full error:** " + str(e)[:500] + "...\n" if len(str(e)) > 500 else str(e) + "\n"
                    error_msg += "\nPlease check the console logs for more details.\n"
                
                yield error_msg, app, gr.update(), gr.update(), gr.update(), ""
        
        # Submit and continue function - with streaming support
        def submit_and_continue(player_name, app):
            """Submit user's pick and continue the draft."""
            if app is None:
                yield "No active draft. Please start a new mock draft.", app, gr.update(), gr.update(), gr.update(), ""
                return
            
            generator = app.continue_mock_draft(player_name)
            output = ""
            
            # Stream updates while draft continues
            for chunk in generator:
                output = chunk
                # For streaming, we need to yield all 6 values
                # Keep controls hidden during streaming
                yield output, app, gr.update(visible=False), gr.update(visible=False), gr.update(value=""), ""
                
                # Check if it's user's turn again
                if "<!--USER_TURN-->" in output:
                    break
            
            # Final yield with turn check and proper UI updates
            clean_output, controls_update, accordion_update, available_text, input_clear = check_user_turn(output, app)
            yield clean_output, app, controls_update, accordion_update, available_text, input_clear
        
        # Set up event handlers
        # Team prompt toggles
        team1_settings_btn.click(
            toggle_prompt_visibility,
            outputs=team1_prompt_col
        )
        team2_settings_btn.click(
            toggle_prompt_visibility,
            outputs=team2_prompt_col
        )
        team3_settings_btn.click(
            toggle_prompt_visibility,
            outputs=team3_prompt_col
        )
        team5_settings_btn.click(
            toggle_prompt_visibility,
            outputs=team5_prompt_col
        )
        team6_settings_btn.click(
            toggle_prompt_visibility,
            outputs=team6_prompt_col
        )
        
        # Save prompts
        team1_save_btn.click(
            lambda prompt, app, prompts: save_prompt(1, prompt, app, prompts),
            inputs=[team1_prompt, app_state, agent_prompts],
            outputs=[app_state, agent_prompts, team1_prompt_col]
        )
        team2_save_btn.click(
            lambda prompt, app, prompts: save_prompt(2, prompt, app, prompts),
            inputs=[team2_prompt, app_state, agent_prompts],
            outputs=[app_state, agent_prompts, team2_prompt_col]
        )
        team3_save_btn.click(
            lambda prompt, app, prompts: save_prompt(3, prompt, app, prompts),
            inputs=[team3_prompt, app_state, agent_prompts],
            outputs=[app_state, agent_prompts, team3_prompt_col]
        )
        team5_save_btn.click(
            lambda prompt, app, prompts: save_prompt(5, prompt, app, prompts),
            inputs=[team5_prompt, app_state, agent_prompts],
            outputs=[app_state, agent_prompts, team5_prompt_col]
        )
        team6_save_btn.click(
            lambda prompt, app, prompts: save_prompt(6, prompt, app, prompts),
            inputs=[team6_prompt, app_state, agent_prompts],
            outputs=[app_state, agent_prompts, team6_prompt_col]
        )
        
        # Start mock draft with streaming
        run_multiagent_btn.click(
            fn=run_and_check,
            inputs=[app_state, agent_prompts, team1_prompt, team2_prompt, team3_prompt, team5_prompt, team6_prompt],
            outputs=[multiagent_output, app_state, mock_draft_controls, available_accordion, available_players_display, draft_pick_input],
            api_name="start_draft",
            queue=True
        )
        
        # Submit pick button with streaming
        submit_pick_btn.click(
            fn=submit_and_continue,
            inputs=[draft_pick_input, app_state],
            outputs=[multiagent_output, app_state, mock_draft_controls, available_accordion, available_players_display, draft_pick_input],
            api_name="submit_pick",
            queue=True
        )
        
        # Submit pick on Enter with streaming
        draft_pick_input.submit(
            fn=submit_and_continue,
            inputs=[draft_pick_input, app_state],
            outputs=[multiagent_output, app_state, mock_draft_controls, available_accordion, available_players_display, draft_pick_input],
            api_name="submit_pick_enter",
            queue=True
        )
        
        # Custom CSS for styling
        demo.css = """
        #main-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .multiagent-output {
            max-height: 600px;
            overflow-y: auto;
            padding: 20px;
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 8px;
            color: #f7fafc;
            font-size: 16px;
            line-height: 1.6;
        }
        
        /* Simple rule: all text in message boxes should be dark */
        .multiagent-output div[style*="background-color"] {
            color: #1a202c;
        }
        
        .multiagent-output div[style*="background-color"] * {
            color: #1a202c;
        }
        
        /* Tables should be white in dark background */
        .multiagent-output table {
            color: #f7fafc;
            border-color: #4a5568;
        }
        
        .multiagent-output th, .multiagent-output td {
            color: #f7fafc;
            border-color: #4a5568;
        }
        
        #draft-pick-input {
            font-size: 1.2em;
            padding: 10px;
        }
        
        #start-button {
            font-size: 1.2em;
            padding: 15px 30px;
        }
        
        .monospace {
            font-family: 'Courier New', monospace;
        }
        
        /* Dark theme support */
        .dark .multiagent-output {
            background: #1f2937;
            border-color: #374151;
            color: #f9fafb;
        }
        
        .dark .multiagent-output div[style*="background-color"] {
            color: #1a202c;
        }
        
        .dark .multiagent-output div[style*="background-color"] * {
            color: #1a202c;
        }
        """
    
    return demo


def main():
    """Launch the Gradio app."""
    # Set environment variables for cloud deployment
    if os.getenv("SPACE_ID"):  # Running on Hugging Face Spaces
        print("🤗 Running on Hugging Face Spaces")
        os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
        os.environ["GRADIO_SERVER_PORT"] = "7860"
        
        # Check for API key but don't fail - just warn
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY not found in environment")
            print("   Please set it in Space Settings → Repository secrets")
    
    # Create and launch the interface
    demo = create_gradio_interface()
    
    # Enable queue for streaming with proper configuration
    demo.queue(max_size=20)
    
    # Launch with appropriate settings
    demo.launch(
        share=False,
        server_name="0.0.0.0" if os.getenv("SPACE_ID") else None,
        server_port=7860 if os.getenv("SPACE_ID") else None,
        max_threads=20
    )


if __name__ == "__main__":
    main() 