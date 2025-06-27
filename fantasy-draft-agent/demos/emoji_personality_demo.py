#!/usr/bin/env python3
"""
Enhanced Personality Demo - Shows agents with heightened personalities and emoji usage
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.app_enhanced import A2AAgentManager
from core.data import TOP_PLAYERS

async def showcase_personalities():
    """Demonstrate the enhanced agent personalities with emojis."""
    
    print("🎭 ENHANCED PERSONALITY DEMO - EMOJI EDITION! 🎭")
    print("=" * 60)
    print("Watch as our DRAMATIC agents battle it out with EXTREME personalities!")
    print("=" * 60)
    
    # Create manager
    manager = A2AAgentManager()
    
    # Start agents
    await manager.start_agents()
    
    if not manager.is_running:
        print("❌ Failed to start agents")
        return
    
    print("\n🔥 LET THE DRAFT DRAMA BEGIN! 🔥\n")
    
    # Available players
    all_players = list(TOP_PLAYERS.keys())
    
    # Round 1: Set up the rivalry
    print("📢 ROUND 1: THE BATTLE LINES ARE DRAWN!\n")
    
    # Zero RB (Team 1) vs Robust RB (Team 3) - Natural enemies!
    print("⚔️ ZERO RB vs ROBUST RB - THE ETERNAL CONFLICT! ⚔️\n")
    
    # Team 1 picks
    pick1 = await manager.get_pick(1, all_players[:10], [], round_num=1)
    if pick1:
        print(f"🎯 Team 1 (Zero RB) selects: {pick1.player_name}")
        print(f"📋 {pick1.reasoning}")
        if pick1.trash_talk:
            print(f"🗣️ TRASH TALK: {pick1.trash_talk}\n")
    
    await asyncio.sleep(0.5)
    
    # Team 3 must comment on their rival!
    comment1 = await manager.get_comment(3, 1, pick1.player_name, round_num=1)
    if comment1:
        print(f"💢 Team 3 (Robust RB) FIRES BACK:")
        print(f"   {comment1}\n")
    
    await asyncio.sleep(0.5)
    
    # Team 3 picks
    all_players = [p for p in all_players if p != pick1.player_name]
    pick2 = await manager.get_pick(3, all_players[:10], [], round_num=1)
    if pick2:
        print(f"\n🎯 Team 3 (Robust RB) selects: {pick2.player_name}")
        print(f"📋 {pick2.reasoning}")
        if pick2.trash_talk:
            print(f"🗣️ TRASH TALK: {pick2.trash_talk}\n")
    
    # Team 1 responds
    comment2 = await manager.get_comment(1, 3, pick2.player_name, round_num=1)
    if comment2:
        print(f"💥 Team 1 (Zero RB) CLAPS BACK:")
        print(f"   {comment2}\n")
    
    print("\n" + "=" * 60)
    
    # Show the upside hunter
    print("🎲 ENTER THE CHAOS AGENT: UPSIDE HUNTER! 🎲\n")
    
    all_players = [p for p in all_players if p != pick2.player_name]
    pick3 = await manager.get_pick(5, all_players[:10], [], round_num=1)
    if pick3:
        print(f"🎯 Team 5 (Upside Hunter) selects: {pick3.player_name}")
        print(f"📋 {pick3.reasoning}")
        if pick3.trash_talk:
            print(f"🗣️ TRASH TALK: {pick3.trash_talk}\n")
    
    # BPA agents comment
    for team in [2, 6]:
        comment = await manager.get_comment(team, 5, pick3.player_name, round_num=1)
        if comment:
            print(f"📊 Team {team} (BPA) analyzes:")
            print(f"   {comment}\n")
    
    print("\n" + "=" * 60)
    print("🏆 PERSONALITY SHOWCASE COMPLETE! 🏆")
    print("\nNotice how each agent:")
    print("  ✅ Uses emojis that match their strategy")
    print("  ✅ Takes their philosophy to the EXTREME")
    print("  ✅ Makes BOLD, dramatic statements")
    print("  ✅ Creates memorable interactions")
    
    # Clean up
    await manager.stop_agents()

if __name__ == "__main__":
    asyncio.run(showcase_personalities()) 