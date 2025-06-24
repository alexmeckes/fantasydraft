"""
Fantasy Draft Agent - Gradio Web Interface
A visual frontend for the any-agent powered fantasy draft assistant.
"""

import gradio as gr
import os
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from agent import FantasyDraftAgent
from scenarios import ScenarioRunner, SCENARIOS
from visualizer import (
    create_player_card,
    create_comparison_card,
    create_roster_summary,
    create_draft_board_snapshot,
    create_decision_summary
)
from data import TOP_PLAYERS, get_best_available, get_players_by_position
from multiagent_draft import MultiAgentMockDraft
from multiagent_scenarios import (
    run_interactive_mock_draft,
    create_quick_multiagent_demo,
    format_agent_message,
    format_conversation_block,
    format_memory_indicator,
    create_mock_draft_visualization
)

# Load environment variables from .env file
load_dotenv()


class FantasyDraftApp:
    def __init__(self):
        self.agent = FantasyDraftAgent()
        self.scenario_runner = ScenarioRunner()
        self.conversation_history = []
        self.current_draft = None  # Store the current mock draft
        self.draft_output = ""  # Store the draft output so far
        
    def chat_response(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """Handle chat interactions with the agent."""
        if not message:
            return "", history
        
        # Process special commands
        if message.lower().startswith("pick "):
            player = message[5:].strip()
            self.agent.update_draft_state(player, is_my_pick=True)
            response = f"✅ **DRAFT CONFIRMATION**\n\nYou drafted {player}!\n\n{create_player_card(player)}"
        elif message.lower() == "reset":
            self.agent.reset_draft()
            self.conversation_history = []
            response = "🔄 **DRAFT RESET**\n\nDraft reset! Starting fresh."
        else:
            # Regular chat with agent
            agent_response = self.agent.run(message)
            # Add clear agent label
            response = f"**🤖 AGENT RESPONSE**\n\n{agent_response}"
        
        # Update history
        history.append([message, response])
        self.conversation_history = history
        
        return "", history
    
    def chat_response_streaming(self, message: str, history: List[List[str]]):
        """Handle chat interactions with streaming responses."""
        import time
        
        if not message:
            yield "", history
            return
        
        # Process special commands
        if message.lower().startswith("pick "):
            player = message[5:].strip()
            self.agent.update_draft_state(player, is_my_pick=True)
            response = f"✅ **DRAFT CONFIRMATION**\n\nYou drafted {player}!\n\n{create_player_card(player)}"
            history.append([message, response])
            yield "", history
        elif message.lower() == "reset":
            self.agent.reset_draft()
            self.conversation_history = []
            response = "🔄 **DRAFT RESET**\n\nDraft reset! Starting fresh."
            history.append([message, response])
            yield "", history
        else:
            # Show user message immediately
            history.append([message, ""])
            yield "", history
            
            # Show thinking indicator
            history[-1][1] = "🤔 *Agent is thinking...*"
            yield "", history
            time.sleep(0.5)
            
            # Get agent response
            response = self.agent.run(message)
            
            # Stream the response with clear label
            formatted_response = f"**🤖 AGENT RESPONSE**\n\n{response}"
            history[-1][1] = ""
            for i in range(0, len(formatted_response), 5):  # Stream 5 chars at a time
                history[-1][1] = formatted_response[:i+5]
                yield "", history
                time.sleep(0.01)
        
        self.conversation_history = history
    
    def get_roster_view(self) -> str:
        """Get current roster visualization."""
        return create_roster_summary(self.agent.draft_state["my_picks"])
    
    def get_draft_board(self) -> str:
        """Get draft board visualization."""
        all_picks = self.agent.draft_state["all_picks"]
        if not all_picks:
            return "No picks made yet. Start drafting!"
        return create_draft_board_snapshot(all_picks)
    
    def compare_players(self, player1: str, player2: str) -> str:
        """Compare two players side by side."""
        if not player1 or not player2:
            return "Please enter both player names to compare."
        return create_comparison_card(player1, player2)
    
    def analyze_position(self, position: str) -> str:
        """Analyze a specific position."""
        if position not in ["RB", "WR", "QB", "TE"]:
            return "Please select a valid position (RB, WR, QB, or TE)."
        
        analysis = self.agent._analyze_position_scarcity(position)
        
        # Add best available at position
        best = get_best_available(self.agent.draft_state["all_picks"], position)
        if best and best[0]:
            name, info = best
            analysis += f"\nBest available: {name} (ADP: {info['adp']}, Tier: {info['tier']})"
        
        return analysis
    
    def run_scenario(self, scenario_name: str, typewriter_enabled: bool = False):
        """Run a demo scenario and yield results progressively for real-time display."""
        import time
        
        scenario_map = {
            "The Opening Pick": "scenario_1",
            "The Position Run": "scenario_2", 
            "The Sleeper Question": "scenario_3",
            "The Stack Builder": "scenario_4"
        }
        
        scenario_id = scenario_map.get(scenario_name)
        if not scenario_id:
            yield "Please select a scenario from the dropdown."
            return
        
        # Reset agent for fresh scenario
        self.scenario_runner.setup_scenario(scenario_id)
        scenario = SCENARIOS[scenario_id]
        
        # Start with header
        output = f"# 🎬 {scenario_name}\n\n"
        output += f"**Scenario**: {scenario['description']}\n\n"
        output += "## 💬 Multi-Turn Conversation Timeline\n\n"
        output += "> **Watch how the agent remembers and builds on previous context!**\n\n"
        yield output
        
        time.sleep(1)  # Pause for effect
        
        # Process each turn in real-time
        conversation_log = []
        context_phrases = [
            "you mentioned", "you said", "earlier", "before",
            "as I mentioned", "like we discussed", "you asked about",
            "regarding your", "based on your", "given that you"
        ]
        
        for i, turn in enumerate(scenario["conversation"]):
            # Add turn separator
            output += f"---\n\n"
            yield output
            time.sleep(0.5)
            
            # Show turn header
            output += f"### 🔄 Turn {i + 1}: {turn['showcases']}\n\n"
            yield output
            time.sleep(0.5)
            
            # Show memory indicator for turns after the first
            if i > 0:
                output += f"💭 **Agent Memory Active** - Remembering {i} previous exchange{'s' if i > 1 else ''}\n\n"
                yield output
                time.sleep(0.5)
            
            # Show user message
            output += "\n<div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0; color: #0d47a1;'>\n\n"
            output += "**👤 USER**\n\n"
            yield output
            
            user_msg = turn['user']
            if typewriter_enabled:
                # Type out user message with typewriter effect
                user_output = ""
                for j in range(0, len(user_msg), 5):  # Show 5 chars at a time
                    user_output = user_msg[:j+5]
                    yield output + user_output + "\n\n</div>"
                    time.sleep(0.02)
            
            output += user_msg + "\n\n</div>\n\n"
            yield output
            time.sleep(0.5)
            
            # Show "Agent is thinking..." indicator
            output += "🤔 *Agent is thinking...*\n\n"
            yield output
            time.sleep(1)
            
            # Get agent response
            agent_response = self.scenario_runner.agent.run(turn['user'])
            
            # Remove thinking indicator and show response
            output = output.replace("🤔 *Agent is thinking...*\n\n", "")
            output += "<div style='background-color: #f3e5f5; padding: 15px; border-radius: 10px; margin: 10px 0; color: #4a148c;'>\n\n"
            output += "**🤖 AGENT**\n\n"
            yield output
            
            if typewriter_enabled:
                # Type out agent response with typewriter effect
                agent_output = ""
                for j in range(0, len(agent_response), 10):  # Show 10 chars at a time
                    agent_output = agent_response[:j+10]
                    yield output + agent_output + "\n\n</div>"
                    time.sleep(0.02)
            
            output += agent_response + "\n\n</div>\n\n"
            yield output
            
            # Check for context references
            response_lower = agent_response.lower()
            has_context = any(phrase in response_lower for phrase in context_phrases)
            
            if has_context:
                time.sleep(0.5)
                output += f"✨ **Context Retention**: The agent referenced the previous conversation!\n\n"
                yield output
                
                # Add specific memory indicators
                if "Bijan" in agent_response and i > 0 and any("Bijan" in c['user'] for c in conversation_log):
                    output += f"🔗 **Remembered**: User's concern about Bijan from earlier\n\n"
                    yield output
                elif "5th pick" in agent_response and i > 0:
                    output += f"🔗 **Remembered**: User's draft position from Turn 1\n\n"
                    yield output
            
            conversation_log.append({
                "user": turn['user'],
                "agent": agent_response
            })
            
            time.sleep(1)  # Pause between turns
        
        # Add summary at the end
        output += "---\n\n"
        output += "## 📊 Multi-Turn Summary\n\n"
        yield output
        time.sleep(0.5)
        
        context_count = sum(1 for turn in conversation_log if any(phrase in turn['agent'].lower() for phrase in context_phrases))
        
        output += f"- **Total Turns**: {len(conversation_log)}\n"
        yield output
        time.sleep(0.3)
        
        output += f"- **Context References**: {context_count}\n"
        yield output
        time.sleep(0.3)
        
        output += f"- **Key Demonstration**: The agent maintains conversation context across all {len(conversation_log)} turns\n"
        yield output
    
    def get_available_players(self, position: str = "ALL") -> str:
        """Get list of available players."""
        available = {name: info for name, info in TOP_PLAYERS.items() 
                    if name not in self.agent.draft_state["all_picks"]}
        
        if position != "ALL":
            available = {name: info for name, info in available.items() 
                        if info["pos"] == position}
        
        if not available:
            return f"No players available at {position}"
        
        # Sort by ADP
        sorted_players = sorted(available.items(), key=lambda x: x[1]["adp"])
        
        output = f"🏈 Available Players ({position})\n"
        output += "="*40 + "\n\n"
        
        for name, info in sorted_players[:15]:  # Show top 15
            output += f"{name} ({info['pos']}, {info['team']}) - ADP: {info['adp']}, Tier: {info['tier']}\n"
        
        if len(sorted_players) > 15:
            output += f"\n... and {len(sorted_players) - 15} more"
        
        return output
    
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
    
    with gr.Blocks(title="Fantasy Draft Agent", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🏈 Fantasy Draft Agent
            ### Powered by any-agent framework
            
            Your AI assistant for fantasy football drafts with multi-turn conversation support.
            """
        )
        
        with gr.Tabs():
            # Tab 1: Interactive Draft Chat
            with gr.TabItem("💬 Draft Assistant"):
                gr.Markdown("Chat with your AI draft assistant. It remembers context across conversations!")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            height=500,
                            show_label=False,
                            elem_id="chatbot"
                        )
                        
                        with gr.Row():
                            msg = gr.Textbox(
                                placeholder="Ask for draft advice or type 'pick PlayerName' to draft...",
                                show_label=False,
                                scale=4
                            )
                            submit = gr.Button("Send", scale=1, variant="primary")
                        
                        gr.Examples(
                            examples=[
                                "Who are the top 3 RBs available?",
                                "I have the 5th pick. Who should I target?",
                                "Should I go RB or WR in round 1?",
                                "pick Christian McCaffrey",
                                "What's the best value pick available?",
                                "reset"
                            ],
                            inputs=msg
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Your Roster")
                        roster_display = gr.Textbox(
                            value=app.get_roster_view(),
                            lines=20,
                            max_lines=25,
                            show_label=False,
                            interactive=False
                        )
                        refresh_roster = gr.Button("🔄 Refresh Roster")
            
            # Tab 2: Player Analysis
            with gr.TabItem("📊 Player Analysis"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Compare Players")
                        player1_input = gr.Textbox(
                            label="Player 1",
                            placeholder="e.g., Christian McCaffrey"
                        )
                        player2_input = gr.Textbox(
                            label="Player 2", 
                            placeholder="e.g., Austin Ekeler"
                        )
                        compare_btn = gr.Button("Compare", variant="primary")
                        comparison_output = gr.Textbox(
                            label="Comparison",
                            lines=10,
                            interactive=False
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Position Analysis")
                        position_select = gr.Dropdown(
                            choices=["RB", "WR", "QB", "TE"],
                            label="Select Position",
                            value="RB"
                        )
                        analyze_btn = gr.Button("Analyze Position", variant="primary")
                        position_output = gr.Textbox(
                            label="Analysis",
                            lines=10,
                            interactive=False
                        )
            
            # Tab 3: Available Players
            with gr.TabItem("🎯 Available Players"):
                gr.Markdown("### Browse Available Players")
                
                position_filter = gr.Radio(
                    choices=["ALL", "RB", "WR", "QB", "TE"],
                    value="ALL",
                    label="Filter by Position"
                )
                
                available_output = gr.Textbox(
                    value=app.get_available_players(),
                    lines=20,
                    interactive=False,
                    show_label=False
                )
                
                refresh_available = gr.Button("🔄 Refresh Available Players")
            
            # Tab 4: Demo Scenarios
            with gr.TabItem("🎬 Demo Scenarios"):
                gr.Markdown(
                    """
                    ### Pre-built Scenarios
                    
                    These scenarios demonstrate the agent's multi-turn conversation capabilities.
                    Each showcases different aspects of draft strategy and context retention.
                    """
                )
                
                scenario_select = gr.Dropdown(
                    choices=[
                        "The Opening Pick",
                        "The Position Run",
                        "The Sleeper Question", 
                        "The Stack Builder"
                    ],
                    label="Select Scenario",
                    value="The Opening Pick"
                )
                
                with gr.Row():
                    run_scenario_btn = gr.Button("▶️ Run Scenario", variant="primary")
                    typewriter_enabled = gr.Checkbox(
                        label="Enable typewriter effect",
                        value=False,  # Default to off to avoid issues
                        info="Uncheck for faster display without character-by-character animation"
                    )
                
                scenario_output = gr.Markdown()
            
            # Tab 5: Draft Board
            with gr.TabItem("📋 Draft Board"):
                gr.Markdown("### Current Draft Board")
                
                draft_board_output = gr.Textbox(
                    value=app.get_draft_board(),
                    lines=20,
                    interactive=False,
                    show_label=False
                )
                
                refresh_board = gr.Button("🔄 Refresh Draft Board")
            
            # Tab 6: Multi-Agent Demos
            with gr.TabItem("🤝 Multi-Agent Demos"):
                gr.Markdown(
                    """
                    ### Multi-Agent Mock Draft
                    
                    Experience multiple AI agents working together in a mock draft!
                    Each agent has its own strategy and personality. Watch them:
                    - 💬 Communicate directly with each other
                    - 🧠 Remember previous conversations
                    - 🎯 Adapt strategies based on the draft flow
                    - 🤖 Demonstrate any-agent's A2A capabilities
                    """
                )
                
                with gr.Row():
                    with gr.Column():
                        multiagent_demo_select = gr.Dropdown(
                            choices=[
                                "Quick A2A Demo",
                                "Mock Draft"
                            ],
                            label="Select Multi-Agent Demo",
                            value="Quick A2A Demo"
                        )
                        
                        run_multiagent_btn = gr.Button("▶️ Run Multi-Agent Demo", variant="primary")
                        
                        gr.Markdown(
                            """
                            ### 🎭 Agent Roster
                            - 📘 **Team 1**: Zero RB Strategy
                            - 📗 **Team 2**: Best Player Available
                            - 📙 **Team 3**: Robust RB Strategy
                            - 📕 **Your Advisor**: Helps you make picks
                            - 📓 **Team 5**: Upside Hunter
                            - 📜 **Commissioner**: Manages the draft
                            """
                        )
                    
                    with gr.Column(scale=2):
                        multiagent_output = gr.Markdown(elem_classes=["multiagent-output"])
                        
                        # Mock draft interaction
                        with gr.Row(visible=False) as mock_draft_controls:
                            draft_pick_input = gr.Textbox(
                                label="Your Pick",
                                placeholder="Enter player name (e.g., 'Justin Jefferson')...",
                                scale=3
                            )
                            submit_pick_btn = gr.Button("Submit Pick", variant="primary", scale=1)
                            
                        # Available players helper (visible during user turn)
                        with gr.Accordion("🏈 Available Players", open=False, visible=False) as available_helper:
                            available_list = gr.Textbox(
                                value="",
                                lines=10,
                                interactive=False,
                                show_label=False
                            )
        
        # Connect event handlers
        msg.submit(app.chat_response, [msg, chatbot], [msg, chatbot]).then(
            app.get_roster_view, None, roster_display
        )
        submit.click(app.chat_response, [msg, chatbot], [msg, chatbot]).then(
            app.get_roster_view, None, roster_display
        )
        
        refresh_roster.click(app.get_roster_view, None, roster_display)
        refresh_board.click(app.get_draft_board, None, draft_board_output)
        
        compare_btn.click(
            app.compare_players,
            [player1_input, player2_input],
            comparison_output
        )
        
        analyze_btn.click(
            app.analyze_position,
            position_select,
            position_output
        )
        
        position_filter.change(
            app.get_available_players,
            position_filter,
            available_output
        )
        
        refresh_available.click(
            app.get_available_players,
            position_filter,
            available_output
        )
        
        run_scenario_btn.click(
            app.run_scenario,
            [scenario_select, typewriter_enabled],
            scenario_output,
            show_progress=True  # Show progress while streaming
        )
        
        # Removed the change event - only run when button is clicked
        
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
            [multiagent_output, mock_draft_controls, available_helper, available_list, draft_pick_input],
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
            [multiagent_output, mock_draft_controls, available_helper, available_list, draft_pick_input],
            show_progress=True
        )
        
        # Also submit on enter
        draft_pick_input.submit(
            submit_and_continue,
            draft_pick_input,
            [multiagent_output, mock_draft_controls, available_helper, available_list, draft_pick_input],
            show_progress=True
        )
        
        # Add custom CSS for better styling
        demo.css = """
        #chatbot {
            border-radius: 10px;
        }
        .gradio-container {
            max-width: 1400px !important;
        }
        
        /* Style user messages */
        .message.user {
            background-color: #e3f2fd !important;
            border-left: 4px solid #1976d2 !important;
        }
        
        /* Style agent messages */
        .message.bot {
            background-color: #f3e5f5 !important;
            border-left: 4px solid #7b1fa2 !important;
        }
        
        /* Add padding to messages */
        .message {
            padding: 12px !important;
            margin: 8px 0 !important;
            border-radius: 8px !important;
        }
        
        /* Style the chat bubbles */
        .message.user .text {
            color: #0d47a1 !important;
        }
        
        .message.bot .text {
            color: #4a148c !important;
        }
        
        /* Add labels before messages */
        .message.user::before {
            content: "👤 USER";
            display: block;
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 8px;
            font-size: 0.9em;
        }
        
        .message.bot::before {
            content: "🤖 AGENT";
            display: block;
            font-weight: bold;
            color: #7b1fa2;
            margin-bottom: 8px;
            font-size: 0.9em;
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
        
        div[style*="#FFFDE7"], div[style*="#fffde7"] {
            color: #827717 !important;
        }
        
        div[style*="#FFF8E1"], div[style*="#fff8e1"] {
            color: #ff6f00 !important;
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
        """
    
    return demo


def main():
    """Launch the Gradio app."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("The app will launch but agent responses will fail without an API key.")
        print("Set it using: export OPENAI_API_KEY='your-key-here'\n")
    
    print("🚀 Launching Fantasy Draft Agent Web Interface...")
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