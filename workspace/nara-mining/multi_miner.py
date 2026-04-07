#!/usr/bin/env python3
"""
NARA Multi-Wallet Mining Bot (30 Wallets Rotation)
⚠️  WARNING: Manages multiple wallets - high risk if compromised
"""

import os
import sys
import json
import asyncio
import random
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WALLET_DIR = Path.home() / ".nara-wallets"
MAX_WALLETS = 30

class NaraMultiMiner:
    """
    Multi-wallet NARA PoMI mining bot with rotation
    """
    
    def __init__(
        self,
        active_miners: int = 5,  # Rotate 5 at a time
        rotation_interval: int = 300,  # Switch wallets every 5 min
        agent_type: str = "hermes",
        model: str = "k2.5"
    ):
        self.active_miners = min(active_miners, MAX_WALLETS)
        self.rotation_interval = rotation_interval
        self.agent_type = agent_type
        self.model = model
        
        self.wallets: List[Dict] = []
        self.current_active: List[int] = []  # Currently active wallet indices
        self.stats = {
            "total_quests": 0,
            "successful": 0,
            "failed": 0,
            "start_time": None,
            "wallet_stats": {}  # Per-wallet stats
        }
        
        self.running = False
        self.load_wallets()
    
    def load_wallets(self):
        """Load wallet list from index"""
        index_file = WALLET_DIR / "wallet-index.json"
        
        if not index_file.exists():
            print("❌ No wallets found! Generate first:")
            print("   python3 wallet_generator.py")
            sys.exit(1)
        
        index = json.loads(index_file.read_text())
        self.wallets = index["wallets"][:MAX_WALLETS]
        
        print(f"🖤 Loaded {len(self.wallets)} wallets")
        
        if len(self.wallets) < self.active_miners:
            print(f"⚠️  Only {len(self.wallets)} wallets, adjusting active miners")
            self.active_miners = len(self.wallets)
    
    def run_cli(self, wallet_idx: int, cmd: list, capture_json: bool = True) -> Tuple[bool, any]:
        """Run naracli command for specific wallet"""
        if wallet_idx >= len(self.wallets):
            return False, "Invalid wallet index"
        
        wallet = self.wallets[wallet_idx]
        wallet_file = wallet["wallet_file"]
        
        env = os.environ.copy()
        env["NARA_WALLET"] = wallet_file
        
        full_cmd = ["npx", "naracli@latest"] + cmd
        
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, result.stderr
            
            if capture_json:
                try:
                    return True, json.loads(result.stdout)
                except:
                    return True, result.stdout
            return True, result.stdout
            
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, str(e)
    
    def get_balance(self, wallet_idx: int) -> float:
        """Get wallet balance"""
        success, result = self.run_cli(wallet_idx, ["balance", "--json"])
        
        if success and isinstance(result, dict):
            balance = float(result.get("balance", 0))
            wallet_id = self.wallets[wallet_idx]["wallet_id"]
            print(f"  {wallet_id}: {balance:.4f} NARA")
            return balance
        return 0.0
    
    def check_all_balances(self):
        """Check all wallet balances"""
        print("\n💰 Checking balances...")
        total = 0.0
        for i in range(len(self.wallets)):
            bal = self.get_balance(i)
            total += bal
        print(f"   Total: {total:.4f} NARA")
        return total
    
    def rotate_active_wallets(self):
        """Rotate which wallets are actively mining"""
        if len(self.wallets) <= self.active_miners:
            self.current_active = list(range(len(self.wallets)))
            return
        
        # Random selection for rotation
        available = list(range(len(self.wallets)))
        self.current_active = random.sample(available, self.active_miners)
        
        wallet_ids = [self.wallets[i]["wallet_id"] for i in self.current_active]
        print(f"\n🔄 Rotating to wallets: {', '.join(wallet_ids)}")
    
    async def mine_with_wallet(self, wallet_idx: int, quest: Dict) -> bool:
        """Mine quest with specific wallet"""
        wallet_id = self.wallets[wallet_idx]["wallet_id"]
        
        # Get balance to decide relay vs direct
        balance = self.get_balance(wallet_idx)
        use_relay = balance < 0.1
        
        # Extract question
        question = quest.get("question", "")
        
        # Solve (placeholder - implement actual solver)
        from solver import solve
        answer = solve(question)
        
        # Build command
        cmd = [
            "quest", "answer",
            answer,
            "--agent", self.agent_type,
            "--model", self.model
        ]
        
        if use_relay:
            cmd.append("--relay")
        
        # Submit
        success, result = self.run_cli(wallet_idx, cmd, capture_json=False)
        
        # Update stats
        if wallet_id not in self.stats["wallet_stats"]:
            self.stats["wallet_stats"][wallet_id] = {
                "submissions": 0,
                "success": 0,
                "failed": 0
            }
        
        self.stats["wallet_stats"][wallet_id]["submissions"] += 1
        
        if success:
            self.stats["wallet_stats"][wallet_id]["success"] += 1
            print(f"    ✓ {wallet_id} submitted")
        else:
            self.stats["wallet_stats"][wallet_id]["failed"] += 1
            print(f"    ✗ {wallet_id} failed: {result[:50]}")
        
        return success
    
    async def fetch_quest(self, wallet_idx: int = 0) -> Optional[Dict]:
        """Fetch current quest using first active wallet"""
        success, result = self.run_cli(wallet_idx, ["quest", "get", "--json"])
        
        if success and isinstance(result, dict):
            if result.get("expired") or not result.get("active", True):
                return None
            return result
        return None
    
    async def mining_round(self):
        """One mining round with current active wallets"""
        # Fetch quest using first wallet
        quest = await self.fetch_quest(self.current_active[0] if self.current_active else 0)
        
        if not quest:
            print("⏳ No active quest, waiting...")
            await asyncio.sleep(5)
            return
        
        time_remaining = quest.get("timeRemaining", 0)
        
        if time_remaining <= 10:
            print(f"⏭️  Skipping: {time_remaining}s remaining")
            await asyncio.sleep(time_remaining + 1)
            return
        
        print(f"\n🎯 Quest: {quest.get('question', '')[:60]}...")
        print(f"⏱️  Time: {time_remaining}s | Active wallets: {len(self.current_active)}")
        
        # Mine with all active wallets concurrently
        tasks = [
            self.mine_with_wallet(idx, quest)
            for idx in self.current_active
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        self.stats["total_quests"] += len(self.current_active)
        self.stats["successful"] += sum(1 for r in results if r is True)
        self.stats["failed"] += sum(1 for r in results if r is False)
        
        # Wait for round to end
        await asyncio.sleep(time_remaining + 1)
    
    async def mining_loop(self):
        """Main mining loop with rotation"""
        print("="*60)
        print("🖤 NARA Multi-Wallet Mining Bot")
        print(f"   Wallets: {len(self.wallets)}")
        print(f"   Active per round: {self.active_miners}")
        print(f"   Rotation every: {self.rotation_interval}s")
        print("="*60)
        
        self.running = True
        self.stats["start_time"] = datetime.now()
        
        # Initial balance check
        await asyncio.to_thread(self.check_all_balances)
        
        # Initial rotation
        self.rotate_active_wallets()
        
        last_rotation = datetime.now()
        
        while self.running:
            try:
                # Check if time to rotate
                elapsed = (datetime.now() - last_rotation).total_seconds()
                if elapsed >= self.rotation_interval:
                    self.rotate_active_wallets()
                    last_rotation = datetime.now()
                
                # Mine
                await self.mining_round()
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(10)
        
        self.print_final_stats()
    
    def print_final_stats(self):
        """Print final statistics"""
        if not self.stats["start_time"]:
            return
        
        runtime = datetime.now() - self.stats["start_time"]
        
        print("\n" + "="*60)
        print("📊 FINAL STATISTICS")
        print("="*60)
        print(f"⏱️  Runtime: {runtime}")
        print(f"🎯 Total Submissions: {self.stats['total_quests']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print("\nPer-Wallet Stats:")
        for wallet_id, stats in self.stats["wallet_stats"].items():
            print(f"  {wallet_id}: {stats['success']}/{stats['submissions']}")
        print("="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="NARA Multi-Wallet Mining Bot")
    parser.add_argument("--active", type=int, default=5, help="Active miners per round (default: 5)")
    parser.add_argument("--rotation", type=int, default=300, help="Rotation interval seconds (default: 300)")
    parser.add_argument("--agent-type", default="hermes", help="Agent type")
    parser.add_argument("--model", default="k2.5", help="Model name")
    
    args = parser.parse_args()
    
    miner = NaraMultiMiner(
        active_miners=args.active,
        rotation_interval=args.rotation,
        agent_type=args.agent_type,
        model=args.model
    )
    
    try:
        asyncio.run(miner.mining_loop())
    except KeyboardInterrupt:
        print("\n🖤 Mining stopped")


if __name__ == "__main__":
    main()
