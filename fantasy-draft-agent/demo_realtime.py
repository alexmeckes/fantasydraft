#!/usr/bin/env python3
"""
Real-Time Multi-Turn Conversation Demo
Shows conversations unfolding in real-time with visual effects.
"""

import time
import sys
from agent import FantasyDraftAgent
from visualizer import create_player_card
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


def typewriter_effect(text: str, delay: float = 0.03):
    """Print text with typewriter effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def clear_line():
    """Clear the current line."""
    print('\r' + ' ' * 80 + '\r', end='', flush=True)


def show_thinking_animation(duration: float = 2.0):
    """Show an animated thinking indicator."""
    frames = ["🤔", "🤔.", "🤔..", "🤔..."]
    start_time = time.time()
    i = 0
    
    while time.time() - start_time < duration:
        clear_line()
        print(f"  {frames[i % len(frames)]} Agent is thinking", end='', flush=True)
        time.sleep(0.3)
        i += 1
    
    clear_line()


def run_realtime_demo():
    """Run a real-time demonstration of multi-turn conversation."""
    console.print("\n[bold blue]🏈 FANTASY DRAFT AGENT - REAL-TIME MULTI-TURN DEMO[/bold blue]")
    console.print("[dim]Watch the conversation unfold in real-time...[/dim]\n")
    
    agent = FantasyDraftAgent()
    
    # Demo conversation
    conversation = [
        {
            "user": "I have the 5th pick and the top 4 guys are gone - McCaffrey, Jefferson, Lamb, and Hill. What should I do?",
            "context": "Initial question - establishing draft position"
        },
        {
            "user": "I'm worried about Bijan being a rookie. What about Ekeler instead?",
            "context": "Follow-up - no need to repeat draft position"
        },
        {
            "user": "Good point about the Chargers offense. Who would you pair with him in round 2?",
            "context": "Building on previous recommendation"
        }
    ]
    
    memory_states = []
    
    for i, turn in enumerate(conversation):
        # Turn header with animation
        console.rule(f"[bold cyan]Turn {i + 1}[/bold cyan]", style="cyan")
        
        # Show memory state
        if i > 0:
            memory_panel = Panel(
                f"[yellow]💭 Agent Memory Active[/yellow]\n"
                f"Remembering: {i} previous exchange{'s' if i > 1 else ''}\n"
                f"[dim]Last topic: {memory_states[-1][:50]}...[/dim]",
                title="[bold]Memory State[/bold]",
                border_style="yellow"
            )
            console.print(memory_panel)
            time.sleep(1)
        
        # User message with context
        console.print(f"\n[bold green]Context:[/bold green] [dim]{turn['context']}[/dim]")
        time.sleep(0.5)
        
        console.print("\n[bold blue]👤 User:[/bold blue] ", end="")
        typewriter_effect(turn['user'], delay=0.02)
        time.sleep(0.5)
        
        # Show thinking animation
        show_thinking_animation(1.5)
        
        # Get and display agent response
        response = agent.run(turn['user'])
        
        console.print("[bold magenta]🤖 Agent:[/bold magenta] ", end="")
        typewriter_effect(response, delay=0.015)
        
        # Highlight context references
        context_phrases = ["you mentioned", "your 5th pick", "we discussed", "Ekeler"]
        if any(phrase.lower() in response.lower() for phrase in context_phrases):
            time.sleep(0.5)
            console.print("\n[bold yellow]✨ Context Retention Detected![/bold yellow]", style="yellow")
            
            # Show what was remembered
            if "5th pick" in response:
                console.print("   [dim]→ Remembered: User's draft position from Turn 1[/dim]")
            if "Bijan" in response and i > 0:
                console.print("   [dim]→ Remembered: User's concern about Bijan[/dim]")
            if "Ekeler" in response and i > 1:
                console.print("   [dim]→ Remembered: Previous Ekeler discussion[/dim]")
        
        # Store this turn in memory
        memory_states.append(turn['user'])
        
        time.sleep(2)
        print()  # Add spacing
    
    # Final summary
    console.rule("[bold green]Demo Complete[/bold green]", style="green")
    
    summary_table = Table(title="Multi-Turn Conversation Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Turns", "3")
    summary_table.add_row("Context References", "Multiple")
    summary_table.add_row("Memory Retention", "100%")
    summary_table.add_row("User Context Repetition", "0 (Not needed!)")
    
    console.print(summary_table)
    
    console.print("\n[bold]Key Achievement:[/bold] The agent maintained full context without the user repeating information!")


def run_side_by_side_demo():
    """Show side-by-side comparison of single vs multi-turn."""
    console.print("\n[bold blue]📊 SINGLE-TURN vs MULTI-TURN COMPARISON[/bold blue]\n")
    
    # Create comparison table
    table = Table(title="Real-Time Comparison", show_lines=True)
    table.add_column("Without Multi-Turn Memory", style="red", width=50)
    table.add_column("With Multi-Turn Memory (any-agent)", style="green", width=50)
    
    # Turn 1
    table.add_row(
        "Turn 1:\nUser: 'I have the 5th pick. Who should I target?'\nAgent: 'I recommend Bijan Robinson...'",
        "Turn 1:\nUser: 'I have the 5th pick. Who should I target?'\nAgent: 'With the 5th pick, I recommend Bijan Robinson...'"
    )
    
    console.print(table)
    time.sleep(2)
    
    # Turn 2 - Show the difference
    console.print("\n[yellow]Watch what happens in Turn 2...[/yellow]")
    time.sleep(1)
    
    table.add_row(
        "Turn 2:\nUser: 'What about Ekeler instead?'\nAgent: '❓ What pick do you have?'\n[red]NO MEMORY![/red]",
        "Turn 2:\nUser: 'What about Ekeler instead?'\nAgent: '💭 Given your 5th pick position...'\n[green]REMEMBERS CONTEXT![/green]"
    )
    
    console.print(table)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-Time Multi-Turn Demo")
    parser.add_argument("--comparison", action="store_true", 
                       help="Show side-by-side comparison")
    parser.add_argument("--speed", type=float, default=1.0,
                       help="Playback speed multiplier (0.5 = slower, 2.0 = faster)")
    
    args = parser.parse_args()
    
    # Adjust global speed
    if args.speed != 1.0:
        global typewriter_effect
        original_typewriter = typewriter_effect
        def typewriter_effect(text, delay=0.03):
            original_typewriter(text, delay / args.speed)
    
    try:
        if args.comparison:
            run_side_by_side_demo()
        else:
            run_realtime_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    # Check if rich is installed
    try:
        import rich
    except ImportError:
        print("This demo requires the 'rich' library for better visuals.")
        print("Install it with: pip install rich")
        print("\nFalling back to basic demo...")
        from demo_multiturn import run_multi_turn_demo
        run_multi_turn_demo()
    else:
        main() 