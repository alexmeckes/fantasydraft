#!/usr/bin/env python3
"""
Fantasy Draft Multi-Agent Demo - Enhanced with A2A Support
Combines the superior UI from the main app with real A2A capabilities
"""

import os
import time
import gradio as gr
import asyncio
import nest_asyncio
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import FantasyDraftAgent
from core.data import TOP_PLAYERS
from core.constants import (
    TYPING_DELAY_SECONDS,
    MESSAGE_DELAY_SECONDS,
    AGENT_START_DELAY,
    AGENT_STARTUP_WAIT,
    DEFAULT_TIMEOUT,
    MAX_COMMENTS_PER_PICK,
    RIVAL_PAIRS,
    AGENT_CONFIGS
)
from core.a2a_helpers import (
    parse_a2a_response,
    extract_task_id,
    format_available_players
)
# Lazy import A2A components to avoid import errors on HF Spaces
DynamicA2AAgentManager = None
cleanup_session = None

from apps.multiagent_draft import MultiAgentMockDraft
from apps.multiagent_scenarios import (
    run_interactive_mock_draft,
    format_conversation_block,
    format_agent_message,
    format_memory_indicator,
    create_mock_draft_visualization
)

# A2A components will be imported lazily when needed
# to avoid import errors on Hugging Face Spaces

# Apply nest_asyncio for async in Gradio
nest_asyncio.apply()

# Fix for litellm 1.72.4 OpenAI endpoint issue
os.environ['OPENAI_API_BASE'] = 'https://api.openai.com/v1'

# Load environment variables
load_dotenv()


class EnhancedFantasyDraftApp:
    def __init__(self):
        self.current_draft = None  # Store the current mock draft
        self.draft_output = ""  # Store the draft output so far
        self.a2a_manager = None  # Will be created dynamically with session ID
        self.use_real_a2a = False
        self.a2a_status = "Not initialized"
        self.session_id = None
        self.custom_prompts = {}  # Store custom agent prompts
    
    async def toggle_a2a_mode(self, use_a2a: bool):
        """Toggle between basic multiagent and A2A modes."""
        self.use_real_a2a = use_a2a
        
        if use_a2a:
            # Lazy import A2A components only when needed
            try:
                global DynamicA2AAgentManager, cleanup_session
                from core.dynamic_a2a_manager import DynamicA2AAgentManager, cleanup_session
                self.real_a2a = True
                self.a2a_type = "full"
            except ImportError as e:
                # Fall back to simulated A2A
                try:
                    from core.simulated_a2a_manager import SimulatedA2AAgentManager, cleanup_session
                    DynamicA2AAgentManager = SimulatedA2AAgentManager
                    self.real_a2a = False
                    self.a2a_type = "simulated"
                    print("Using simulated A2A mode (real A2A not available)")
                except ImportError as e2:
                    self.a2a_status = f"❌ A2A mode not available: {str(e)}. Please use Basic Multiagent mode."
                    self.use_real_a2a = False
                    return self.a2a_status
            
            # Generate unique session ID if needed
            if not self.session_id:
                import uuid
                self.session_id = str(uuid.uuid4())[:8]
            
            # Create new dynamic manager for this session with custom prompts
            self.a2a_manager = DynamicA2AAgentManager(
                self.session_id,
                custom_prompts=self.custom_prompts
            )
            
            try:
                await self.a2a_manager.start_agents()
                ports = self.a2a_manager.allocated_ports
                if hasattr(self, 'a2a_type'):
                    if self.a2a_type == "full":
                        self.a2a_status = f"✅ Full A2A Mode Active (Session: {self.session_id}, Ports: {ports[0]}-{ports[-1]})"
                    elif self.a2a_type == "lightweight":
                        self.a2a_status = f"✅ Lightweight A2A Mode Active (Session: {self.session_id}, HTTP Ports: {ports[0]}-{ports[-1]})"
                    else:  # simulated
                        self.a2a_status = f"✅ Simulated A2A Mode Active (Session: {self.session_id}, Mock Ports: {ports[0]}-{ports[-1]})"
                else:
                    self.a2a_status = f"✅ A2A Mode Active (Session: {self.session_id}, Ports: {ports[0]}-{ports[-1]})"
            except RuntimeError as e:
                # Failed to allocate ports or start agents
                self.a2a_status = f"❌ Failed to start A2A: {str(e)}"
                self.use_real_a2a = False
                self.a2a_manager = None
        else:
            if self.a2a_manager and cleanup_session:
                await cleanup_session(self.a2a_manager)
                self.a2a_manager = None
            self.a2a_status = "✅ Basic Multiagent Mode Active (Using built-in communication)"
        
        return self.a2a_status
    
    def run_multiagent_demo(self, use_a2a: bool = False):
        """Run the mock draft demonstration with optional A2A support."""
        # Reset any previous draft
        self.current_draft = None
        self.draft_output = ""
        
        # First, set the mode (like in the working version)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        status = loop.run_until_complete(self.toggle_a2a_mode(use_a2a))
        yield f"**Mode:** {status}\n\n"
        
        # Initialize draft
        self.current_draft = MultiAgentMockDraft(user_pick_position=4)
        
        # Run the appropriate draft
        if use_a2a and self.a2a_manager:
            yield from self.run_a2a_draft()
        else:
            # Use basic multiagent draft
            draft_generator = run_interactive_mock_draft()
            
            for output in draft_generator:
                if isinstance(output, tuple):
                    # This means it's the user's turn
                    self.current_draft, self.draft_output = output
                    yield self.draft_output + "\n<!--USER_TURN-->"
                    return
                else:
                    self.draft_output = output
                    yield output
    
    def run_a2a_draft(self):
        """Run draft with A2A communication."""
        # Initialize draft
        self.current_draft = MultiAgentMockDraft(user_pick_position=4)
        self.draft_output = "# 🏈 Mock Draft with A2A Communication\n\n"
        
        # Welcome message
        if hasattr(self, 'a2a_type'):
            if self.a2a_type == "full":
                welcome_msg = "Welcome to the A2A-powered draft! Each agent is running on its own server with full A2A protocol."
            elif self.a2a_type == "lightweight":
                welcome_msg = "Welcome to the lightweight A2A draft! Each agent runs on its own HTTP server (no grpcio needed)."
            else:  # simulated
                welcome_msg = "Welcome to the simulated A2A draft! Agents communicate using mock HTTP calls."
        else:
            welcome_msg = "Welcome to the A2A-powered draft! Each agent is running on its own server."
        self.draft_output += format_agent_message(
            "commissioner", "ALL",
            welcome_msg
        )
        yield self.draft_output
        
        # Run draft rounds
        loop = asyncio.get_event_loop()
        
        for round_num in range(1, 4):  # 3 rounds
            self.draft_output += f"\n## 🔄 ROUND {round_num}\n\n"
            yield self.draft_output
            
            # Snake draft order
            if round_num % 2 == 1:
                pick_order = list(range(1, 7))
            else:
                pick_order = list(range(6, 0, -1))
            
            for pick_in_round, team_num in enumerate(pick_order, 1):
                pick_num = (round_num - 1) * 6 + pick_in_round
                
                # Show draft board at start of round
                if pick_in_round == 1:
                    self.draft_output += create_mock_draft_visualization(self.current_draft, round_num, pick_num)
                    self.draft_output += "\n"
                    yield self.draft_output
                
                if team_num == 4:  # User's turn
                    # Get advisor recommendation - use user_advisor directly
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
                    # A2A agent pick
                    messages = loop.run_until_complete(
                        self.run_a2a_draft_turn(team_num, round_num, pick_num)
                    )
                    
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
    
    async def run_a2a_draft_turn(self, team_num: int, round_num: int, pick_num: int):
        """Run a draft turn using A2A."""
        messages = []
        
        # Commissioner announcement
        messages.append((
            self.current_draft.commissioner,
            "ALL",
            f"Team {team_num} is on the clock!"
        ))
        
        # Get available players
        all_picked = [p for picks in self.current_draft.draft_board.values() for p in picks]
        available = [p for p in TOP_PLAYERS.keys() if p not in all_picked]
        
        # Get pick from A2A agent
        previous_picks = self.current_draft.draft_board.get(team_num, [])
        pick_result = await self.a2a_manager.get_pick(team_num, available, previous_picks, round_num)
        
        if not pick_result or pick_result.type != "pick":
            # Fallback to simulation
            if team_num == 5:
                # Special handling for Team 5 to reduce user wait time
                messages.append((
                    self.current_draft.commissioner,
                    "ALL",
                    f"⚡ Team 5 is taking their time - using quick simulation"
                ))
            else:
                messages.append((
                    self.current_draft.commissioner,
                    "ALL",
                    f"⚠️ Team {team_num} A2A agent not responding - using simulation"
                ))
            
            sim_messages, _ = self.current_draft.simulate_draft_turn(round_num, pick_num, team_num)
            messages.extend(sim_messages)
            return messages
        
        # Make the pick
        player = pick_result.player_name
        self.current_draft.draft_board[team_num].append(player)
        
        # Update agent's picks if it exists
        agent = self.current_draft.agents.get(team_num)
        if agent:
            agent.picks.append(player)
        
        # Commissioner announcement of pick
        pick_num = len([p for picks in self.current_draft.draft_board.values() for p in picks])
        confirm_msg = self.current_draft.commissioner.confirm_pick(
            agent.team_name if agent else f"Team {team_num}", 
            player, 
            pick_num
        )
        messages.append((self.current_draft.commissioner, "ALL", confirm_msg))
        
        # Agent explains reasoning
        messages.append((
            agent if agent else "system",
            "ALL",
            f"{pick_result.reasoning}"
        ))
        
        if pick_result.trash_talk:
            messages.append((
                agent if agent else "system",
                "ALL",
                pick_result.trash_talk
            ))
        
        # Get comments from other A2A agents
        potential_commenters = [t for t in [1, 2, 3, 5, 6] if t != team_num and t != 4]
        
        # For Team 5, skip comments to avoid timeouts cascading
        if team_num == 5:
            potential_commenters = []  # No comments when Team 5 picks
        
        # Sort commenters to prioritize rivals
        if team_num in RIVAL_PAIRS and potential_commenters:
            rivals = RIVAL_PAIRS[team_num]
            if isinstance(rivals, int):
                rivals = [rivals]
            # Put rivals first in the list
            prioritized_commenters = [t for t in rivals if t in potential_commenters]
            prioritized_commenters.extend([t for t in potential_commenters if t not in prioritized_commenters])
            potential_commenters = prioritized_commenters
        
        # Collect comments up to the configured limit
        comment_count = 0
        max_comments = self.a2a_manager.max_comments_per_pick
        
        # Reduce comments if we're getting late in the draft
        if pick_num >= 4:  # After pick 4, reduce comments
            max_comments = min(max_comments, 1)
        
        for other_team in potential_commenters:
            if comment_count >= max_comments:
                break
            
            # Skip Team 5 commenting to avoid more timeouts
            if other_team == 5:
                continue
                
            comment = await self.a2a_manager.get_comment(other_team, team_num, player, round_num)
            if comment:
                other_agent = self.current_draft.agents.get(other_team)
                if other_agent:
                    # Use the same pattern as earlier for the picking agent's name
                    picking_agent_name = agent.team_name if agent else f"Team {team_num}"
                    messages.append((
                        other_agent,
                        picking_agent_name,
                        comment
                    ))
                    comment_count += 1
        
        return messages
    
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
        if self.use_real_a2a and self.a2a_manager:
            yield from self.continue_a2a_draft()
        else:
            yield from self.continue_basic_multiagent_draft()
    
    def continue_a2a_draft(self):
        """Continue A2A draft after user pick."""
        # Calculate where we are
        total_picks = len([p for picks in self.current_draft.draft_board.values() for p in picks])
        current_round = ((total_picks - 1) // 6) + 1
        
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Continue from current position
        for round_num in range(current_round, 4):
            if round_num > current_round:
                self.draft_output += f"\n## 🔄 ROUND {round_num}\n\n"
                yield self.draft_output
            
            # Snake draft order
            if round_num % 2 == 1:
                pick_order = list(range(1, 7))
            else:
                pick_order = list(range(6, 0, -1))
            
            # Calculate where we are in the current round
            picks_in_round = total_picks % 6
            start_idx = picks_in_round if round_num == current_round else 0
            
            for pick_in_round, team_num in enumerate(list(pick_order)[start_idx:], start_idx + 1):
                pick_num = (round_num - 1) * 6 + pick_in_round
                
                # Show draft board at start of round
                if pick_in_round == 1:
                    self.draft_output += create_mock_draft_visualization(self.current_draft, round_num, pick_num)
                    self.draft_output += "\n"
                    yield self.draft_output
                
                if team_num == 4:  # User's turn again
                    # Get advisor recommendation - use user_advisor directly
                    advisor = self.current_draft.user_advisor
                    
                    all_picked = [p for picks in self.current_draft.draft_board.values() for p in picks]
                    available = [p for p in TOP_PLAYERS.keys() if p not in all_picked]
                    
                    # Get other agent strategies for advisor context
                    strategies = {f"Team {i}": agent.strategy for i, agent in self.current_draft.agents.items()}
                    
                    advice = advisor.advise_user(available, self.current_draft.draft_board, strategies)
                    self.draft_output += format_agent_message(advisor, "USER", advice)
                    yield self.draft_output
                    
                    self.draft_output += "\n**⏰ YOU'RE ON THE CLOCK! Type your pick below.**\n\n"
                    yield self.draft_output + "\n<!--USER_TURN-->"
                    return
                else:
                    # A2A agent pick
                    messages = loop.run_until_complete(
                        self.run_a2a_draft_turn(team_num, round_num, pick_num)
                    )
                    
                    for msg in messages:
                        if len(msg) >= 3:
                            agent, recipient, content = msg[:3]
                            typing_placeholder = format_agent_message(agent, recipient, "...")
                            self.draft_output += typing_placeholder
                            yield self.draft_output
                            time.sleep(TYPING_DELAY_SECONDS)
                            
                            self.draft_output = self.draft_output.replace(typing_placeholder, "")
                            self.draft_output += format_agent_message(agent, recipient, content)
                            yield self.draft_output
                            time.sleep(MESSAGE_DELAY_SECONDS)
                    
                    time.sleep(TYPING_DELAY_SECONDS)
            
            self.draft_output += format_agent_message("commissioner", "ALL", 
                f"That's the end of Round {round_num}!")
            yield self.draft_output
        
        # Final summary
        self.draft_output += "\n## 📊 FINAL RESULTS\n\n"
        self.draft_output += self.current_draft.get_draft_summary()
        yield self.draft_output
        
        self.current_draft = None
    
    def continue_basic_multiagent_draft(self):
        """Continue basic multiagent draft after user pick."""
        # This is the original logic from app.py
        total_picks = len([p for picks in self.current_draft.draft_board.values() for p in picks])
        current_round = ((total_picks - 1) // 6) + 1
        
        draft_memories = []
        
        for round_num in range(current_round, 4):
            if round_num > current_round:
                self.draft_output += f"\n## 🔄 ROUND {round_num}\n\n"
                yield self.draft_output
            
            if round_num % 2 == 1:
                pick_order = list(range(1, 7))
            else:
                pick_order = list(range(6, 0, -1))
            
            picks_in_round = total_picks % 6
            start_idx = picks_in_round if round_num == current_round else 0
            
            for pick_in_round, team_num in enumerate(list(pick_order)[start_idx:], start_idx + 1):
                pick_num = (round_num - 1) * 6 + pick_in_round
                
                if pick_in_round == 1:
                    self.draft_output += create_mock_draft_visualization(self.current_draft, round_num, pick_num)
                    self.draft_output += "\n"
                    yield self.draft_output
                
                messages, result = self.current_draft.simulate_draft_turn(round_num, pick_num, team_num)
                
                for msg in messages:
                    if len(msg) >= 3:
                        agent, recipient, content = msg[:3]
                        
                        if isinstance(agent, str) and agent.startswith("typing_"):
                            continue
                        else:
                            typing_placeholder = format_agent_message(agent, recipient, "...")
                            self.draft_output += typing_placeholder
                            yield self.draft_output
                            time.sleep(TYPING_DELAY_SECONDS)
                            
                            self.draft_output = self.draft_output.replace(typing_placeholder, "")
                            self.draft_output += format_agent_message(agent, recipient, content)
                            yield self.draft_output
                            time.sleep(MESSAGE_DELAY_SECONDS)
                
                if result is None:
                    self.draft_output += "\n**⏰ YOU'RE ON THE CLOCK! Type your pick below.**\n\n"
                    yield self.draft_output + "\n<!--USER_TURN-->"
                    return
                
                if round_num > 1 and pick_in_round % 2 == 0:
                    if team_num in self.current_draft.agents:
                        agent = self.current_draft.agents[team_num]
                        if len(agent.picks) > 1:
                            memory = f"{agent.team_name} has drafted: {', '.join(agent.picks)}"
                            draft_memories.append(memory)
                    
                    if draft_memories:
                        self.draft_output += format_memory_indicator(round_num, draft_memories[-2:])
                        yield self.draft_output
                
                time.sleep(TYPING_DELAY_SECONDS)
            
            self.draft_output += format_agent_message("commissioner", "ALL", 
                f"That's the end of Round {round_num}!")
            yield self.draft_output
        
        self.draft_output += "\n## 📊 FINAL RESULTS\n\n"
        self.draft_output += self.current_draft.get_draft_summary()
        yield self.draft_output
        
        self.current_draft = None


def create_gradio_interface():
    """Create the main Gradio interface with A2A support."""
    
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
                    # Add A2A Mode Toggle
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 🔧 Communication Mode")
                            communication_mode = gr.Radio(
                                ["Basic Multiagent", "A2A (Experimental)"],
                                value="Basic Multiagent",
                                label="Select how agents communicate",
                                info="Basic Multiagent: Reliable single-process execution (Recommended) | A2A: Distributed but may timeout on cloud"
                            )
                            mode_info = gr.Markdown(
                                """
                                **Basic Multiagent** (Recommended): Fast, reliable execution with full agent personalities
                                **A2A (Experimental)**: Distributed architecture with separate HTTP servers per agent
                                
                                *Note: A2A mode may experience timeouts on cloud deployments. Use Basic Multiagent for best experience.*
                                """
                            )
                    
                    # Show agent cards
                    gr.Markdown("""
                    ### 🏈 Meet Your Competition
                    
                    You'll be drafting at **Position 4** with these AI opponents:
                    """)
                    
                    # Store agent prompts in state
                    agent_prompts = gr.State({})
                    
                    # Agent cards with settings buttons
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
                                        label="Team 1 Personality & Strategy (Output format is fixed)",
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
                                        info="Customize personality and strategy. Output format instructions are automatically included."
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
                                        label="Team 2 Personality & Strategy (Output format is fixed)",
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
                                        info="Customize personality and strategy. Output format instructions are automatically included."
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
                                        label="Team 3 Personality & Strategy (Output format is fixed)",
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
                                        info="Customize personality and strategy. Output format instructions are automatically included."
                                    )
                                    team3_save_btn = gr.Button("💾 Save", size="sm", variant="primary")
                        
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
                                        label="Team 5 Personality & Strategy (Output format is fixed)",
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
                                        info="Customize personality and strategy. Output format instructions are automatically included."
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
                                        label="Team 6 Personality & Strategy (Output format is fixed)",
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
                                        info="Customize personality and strategy. Output format instructions are automatically included."
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
                
                # Debug Tab
                with gr.TabItem("🔍 Debug"):
                    gr.Markdown("""
                    ## A2A Debugging Tools
                    
                    Use these tools to test A2A functionality and diagnose any issues.
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            test_a2a_btn = gr.Button("🧪 Test A2A Dependencies & Ports", variant="primary", size="lg")
                            test_network_btn = gr.Button("🌐 Test Network Connectivity", variant="secondary", size="lg")
                            
                    a2a_test_output = gr.Textbox(
                        label="Test Results", 
                        lines=20, 
                        interactive=False,
                        elem_classes=["monospace"]
                    )
                    
                    gr.Markdown("""
                    ### What this test checks:
                    - ✓ Python environment and version
                    - ✓ a2a-sdk package installation
                    - ✓ Module imports (a2a, any_agent)
                    - ✓ Port availability for agents
                    - ✓ A2A agent startup capability
                    
                    ### Common issues:
                    - **Import errors**: Check if a2a-sdk is properly installed
                    - **Port conflicts**: Other services might be using ports 5000-9000
                    - **Timeout errors**: Network latency on cloud deployments
                    """)
                
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
                    
                    **Two Modes Available:**
                    
                    #### 1. A2A Mode (Default) ✨
                    - **Distributed Architecture**: Each agent runs on its own HTTP server
                    - **Dynamic Ports**: Each session gets unique ports automatically (5000-9000 range)
                    - **True Isolation**: No shared memory, HTTP communication only
                    - **Production Ready**: Scalable to multiple machines
                    - **Real HTTP Calls**: Agents communicate via actual network requests
                    - **Task Continuity**: Conversation context maintained across turns
                    
                    #### 2. Basic Multiagent Mode
                    - Single process, direct method calls
                    - Shared memory between agents
                    - Fast execution, simple debugging
                    - Fallback option if A2A requirements aren't met
                    
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
        
        # Test A2A functionality
        def test_a2a_functionality():
            """Test A2A dependencies and port availability."""
            import socket
            import subprocess
            import importlib.util
            import site
            
            test_results = []
            
            # 1. Python Environment
            test_results.append("=== Python Environment ===")
            test_results.append(f"Python: {sys.version.split()[0]}")
            test_results.append(f"Platform: {sys.platform}")
            test_results.append(f"SPACE_ID: {os.getenv('SPACE_ID', 'Not on HF Spaces')}")
            
            # 2. Check a2a-sdk installation
            test_results.append("\n=== Package Installation ===")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "show", "a2a-sdk"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
                    location_line = [line for line in result.stdout.split('\n') if line.startswith('Location:')]
                    test_results.append(f"✅ a2a-sdk installed: {version_line[0] if version_line else 'Unknown version'}")
                    if location_line:
                        test_results.append(f"   {location_line[0]}")
                else:
                    test_results.append("❌ a2a-sdk NOT installed according to pip")
            except Exception as e:
                test_results.append(f"❌ Error checking pip: {e}")
            
            # 3. Module search
            test_results.append("\n=== Module Search ===")
            a2a_spec = importlib.util.find_spec("a2a")
            if a2a_spec:
                test_results.append(f"✅ a2a module found at: {a2a_spec.origin}")
            else:
                test_results.append("❌ a2a module NOT found by importlib")
                # Manual search
                for path in site.getsitepackages():
                    if os.path.exists(path):
                        a2a_path = os.path.join(path, "a2a")
                        if os.path.exists(a2a_path):
                            test_results.append(f"   Found a2a directory at: {a2a_path}")
            
            # 4. Import tests
            test_results.append("\n=== Import Tests ===")
            
            # Basic a2a import
            try:
                import a2a
                test_results.append(f"✅ import a2a: Success")
                try:
                    import a2a.types
                    test_results.append("✅ import a2a.types: Success")
                    try:
                        from a2a.types import AgentSkill
                        test_results.append("✅ from a2a.types import AgentSkill: Success")
                    except ImportError as e:
                        test_results.append(f"❌ AgentSkill import: {e}")
                except ImportError as e:
                    test_results.append(f"❌ a2a.types import: {e}")
            except ImportError as e:
                test_results.append(f"❌ a2a import failed: {e}")
            
            # any_agent A2A imports
            try:
                from any_agent.serving import A2AServingConfig
                from any_agent.tools import a2a_tool_async
                test_results.append("✅ any_agent A2A components: Success!")
            except ImportError as e:
                test_results.append(f"❌ any_agent A2A import: {e}")
            
            # 5. Port availability
            test_results.append("\n=== Port Availability ===")
            test_ports = [5001, 5002, 5003, 5004, 5005, 5006]
            available_count = 0
            
            for port in test_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('127.0.0.1', port))
                    test_results.append(f"✅ Port {port} available")
                    available_count += 1
                    sock.close()
                except Exception:
                    test_results.append(f"❌ Port {port} not available")
            
            test_results.append(f"\n📊 Summary: {available_count}/{len(test_ports)} ports available")
            
            # 6. Check any-agent version if imports failed
            if "❌ any_agent A2A import" in "\n".join(test_results):
                test_results.append("\n=== Version Check ===")
                try:
                    result = subprocess.run([sys.executable, "-m", "pip", "show", "any-agent"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
                        if version_line:
                            test_results.append(f"any-agent version: {version_line[0]}")
                            # Check if version is < 0.22
                            import re
                            version_match = re.search(r'Version: (\d+)\.(\d+)', version_line[0])
                            if version_match:
                                major, minor = int(version_match.group(1)), int(version_match.group(2))
                                if major == 0 and minor < 22:
                                    test_results.append("⚠️ any-agent version < 0.22.0 - A2A components not available")
                                    test_results.append("💡 Solution: Update requirements.txt to any-agent[a2a,openai]>=0.22.0")
                except Exception as e:
                    test_results.append(f"Could not check any-agent version: {e}")
            
            # Final verdict
            if available_count >= 6 and "✅ any_agent A2A components: Success!" in "\n".join(test_results):
                test_results.append("\n✅ A2A should work! Try selecting A2A mode.")
            else:
                test_results.append("\n❌ A2A requirements not met. Use Basic Multiagent mode.")
            
            return "\n".join(test_results)
        
        # Test network connectivity for A2A
        async def test_network_connectivity():
            """Test network connectivity for A2A servers."""
            import httpx
            
            results = []
            results.append("=== A2A Network Connectivity Test ===")
            results.append(f"Running on HF Spaces: {bool(os.getenv('SPACE_ID'))}\n")
            
            # Test different host configurations
            configs = [
                ("localhost", 8000, "Local loopback"),
                ("127.0.0.1", 8000, "IP loopback"),
                ("0.0.0.0", 8000, "All interfaces"),
            ]
            
            for host, port, desc in configs:
                results.append(f"Testing {host}:{port} ({desc})...")
                
                timeout = httpx.Timeout(timeout=5.0, connect=2.0, read=5.0)
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    # Test basic connectivity
                    try:
                        response = await client.get(f"http://{host}:{port}/")
                        results.append(f"  ✅ Connected: HTTP {response.status_code}")
                    except httpx.ConnectError:
                        results.append(f"  ❌ Connection refused (no server)")
                    except httpx.ReadTimeout:
                        results.append(f"  ❌ Read timeout (server not responding)")
                    except Exception as e:
                        results.append(f"  ❌ Error: {type(e).__name__}")
                
                results.append("")
            
            results.append("=== Recommendations ===")
            if os.getenv("SPACE_ID"):
                results.append("On HF Spaces:")
                results.append("• A2A servers bind to 0.0.0.0 for external access")
                results.append("• Clients connect via 127.0.0.1 internally")
                results.append("• Network timeouts are common - retries help")
                results.append("• Consider Basic Multiagent mode for reliability")
            else:
                results.append("Local development:")
                results.append("• Both localhost and 127.0.0.1 should work")
                results.append("• Check firewall if connections fail")
            
            return "\n".join(results)
        
        # No need for separate mode change handler - it happens when draft starts
        
        # Functions to handle prompt editing
        def toggle_prompt_visibility():
            """Toggle prompt editor visibility."""
            return gr.update(visible=True)
        
        def save_prompt(team_num, prompt_text, app, prompts_dict):
            """Save custom prompt for a team."""
            if app is None:
                app = EnhancedFantasyDraftApp()
            if prompts_dict is None:
                prompts_dict = {}
            
            prompts_dict[team_num] = prompt_text
            app.custom_prompts[team_num] = prompt_text
            return app, prompts_dict, gr.update(visible=False)
        
        # Run multi-agent demo with control visibility handling
        def run_and_check(mode, app, prompts_dict):
            """Run demo and check for user turn."""
            # Create a new app instance for this user if needed
            if app is None:
                app = EnhancedFantasyDraftApp()
            
            # Apply custom prompts if any
            if prompts_dict:
                app.custom_prompts = prompts_dict
            
            use_a2a = (mode == "A2A (Experimental)")
            for output in app.run_multiagent_demo(use_a2a):
                result = check_user_turn(output, app)
                yield result + (app,)  # Return the app state as the last element
        
        # Wire up settings buttons for each team
        team1_settings_btn.click(toggle_prompt_visibility, [], [team1_prompt_col])
        team2_settings_btn.click(toggle_prompt_visibility, [], [team2_prompt_col])
        team3_settings_btn.click(toggle_prompt_visibility, [], [team3_prompt_col])
        team5_settings_btn.click(toggle_prompt_visibility, [], [team5_prompt_col])
        team6_settings_btn.click(toggle_prompt_visibility, [], [team6_prompt_col])
        
        # Wire up save buttons
        team1_save_btn.click(
            lambda p, a, d: save_prompt(1, p, a, d),
            [team1_prompt, app_state, agent_prompts],
            [app_state, agent_prompts, team1_prompt_col]
        )
        team2_save_btn.click(
            lambda p, a, d: save_prompt(2, p, a, d),
            [team2_prompt, app_state, agent_prompts],
            [app_state, agent_prompts, team2_prompt_col]
        )
        team3_save_btn.click(
            lambda p, a, d: save_prompt(3, p, a, d),
            [team3_prompt, app_state, agent_prompts],
            [app_state, agent_prompts, team3_prompt_col]
        )
        team5_save_btn.click(
            lambda p, a, d: save_prompt(5, p, a, d),
            [team5_prompt, app_state, agent_prompts],
            [app_state, agent_prompts, team5_prompt_col]
        )
        team6_save_btn.click(
            lambda p, a, d: save_prompt(6, p, a, d),
            [team6_prompt, app_state, agent_prompts],
            [app_state, agent_prompts, team6_prompt_col]
        )
        
        run_multiagent_btn.click(
            run_and_check,
            [communication_mode, app_state, agent_prompts],
            [multiagent_output, mock_draft_controls, available_accordion, available_players_display, draft_pick_input, app_state],
            show_progress=True
        )
        
        # Wrapper for async network test
        def run_network_test():
            """Run the async network test."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(test_network_connectivity())
        
        # Wire up test buttons
        test_a2a_btn.click(
            test_a2a_functionality,
            [],
            [a2a_test_output]
        )
        
        test_network_btn.click(
            run_network_test,
            [],
            [a2a_test_output]
        )
        
        # Continue draft after user pick
        def submit_and_continue(player_name, app):
            """Submit pick and continue draft."""
            if app is None:
                yield ("No active draft. Please start a new mock draft.", 
                       gr.update(visible=False), gr.update(visible=False), "", "", None)
                return
                
            for output in app.continue_mock_draft(player_name):
                result = check_user_turn(output, app)
                yield result + (app,)  # Return the app state as the last element
        
        submit_pick_btn.click(
            submit_and_continue,
            [draft_pick_input, app_state],
            [multiagent_output, mock_draft_controls, available_accordion, available_players_display, draft_pick_input, app_state],
            show_progress=True
        )
        
        # Also submit on enter
        draft_pick_input.submit(
            submit_and_continue,
            [draft_pick_input, app_state],
            [multiagent_output, mock_draft_controls, available_accordion, available_players_display, draft_pick_input, app_state],
            show_progress=True
        )
        
        # Minimal CSS for layout only
        demo.css = """
        #main-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .multiagent-output {
            max-height: 800px;
            overflow-y: auto;
        }
        
        /* Force dark text in message cards */
        .multiagent-output div[style*="background-color"] {
            color: #212121 !important;
        }
        
        .multiagent-output div[style*="background-color"] * {
            color: #212121 !important;
        }
        
        #start-button {
            margin-top: 20px;
        }
        
        /* Monospace font for debug output */
        .monospace textarea {
            font-family: 'Courier New', Courier, monospace;
            font-size: 12px;
        }
        
        /* Settings button styling */
        button[variant="secondary"] {
            margin-top: 8px;
            width: 100%;
        }
        
        /* Prompt editor styling */
        .prompt-editor {
            margin-top: 10px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 4px;
        }
        """
        
        # Note: Gradio's unload() doesn't support inputs, so automatic cleanup
        # happens when the Python process ends or when new sessions override old ones
    
    return demo


def main():
    """Main entry point."""
    # Check for API key - but don't exit on Hugging Face Spaces
    if not os.getenv("OPENAI_API_KEY"):
        if os.getenv("SPACE_ID"):  # Running on Hugging Face Spaces
            print("⚠️  OPENAI_API_KEY not found - please set it in Space Settings > Repository secrets")
        else:
            print("Error: OPENAI_API_KEY not found in environment")
            print("Please set it using: export OPENAI_API_KEY='your-key-here'")
            exit(1)
    
    # Create and launch the interface
    demo = create_gradio_interface()
    
    print("🚀 Launching Enhanced Fantasy Draft App with A2A Support...")
    
    # Check if running on Hugging Face Spaces
    if os.getenv("SPACE_ID"):
        demo.launch()  # Hugging Face handles server config
    else:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=True,
            show_error=True
        )


if __name__ == "__main__":
    main() 