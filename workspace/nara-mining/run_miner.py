#!/usr/bin/env python3
"""
NARA Math-Only Mining Bot Runner
Auto-start mining with W001
"""
import asyncio
import sys
import os
sys.path.insert(0, '.')
from nara_miner import NaraMiner

async def main():
    # Use W001 wallet
    wallet_path = os.path.expanduser("~/.nara-wallets/W001.json")
    
    miner = NaraMiner(
        agent_id='hitagi-agent-001',
        relay_threshold=0.0,  # Use relay (gasless) always
        min_time_remaining=20,  # Skip if less than 20s
        wallet_path=wallet_path
    )
    
    print("🖤 NARA MATH-ONLY MINING BOT")
    print("=" * 50)
    print("Features:")
    print("  ✓ Auto-solve math problems")
    print("  ✓ Skip trivia questions")
    print("  ✓ Gasless relay submission")
    print("  ✓ Stake-free credits (from Twitter bind)")
    print("=" * 50)
    
    # Check wallet
    if not miner.check_wallet():
        print("\n❌ Wallet not found!")
        print(f"   Check: {wallet_path}")
        return
    
    # Check agent
    miner.check_agent()
    
    print("\n🚀 Starting mining loop...")
    print("Press Ctrl+C to stop\n")
    
    # Start mining
    try:
        await miner.mining_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        miner.print_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
