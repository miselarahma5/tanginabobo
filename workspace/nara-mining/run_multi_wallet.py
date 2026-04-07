#!/usr/bin/env python3
"""
NARA Multi-Wallet Mining Bot
Rotate 5 active miners from 30 wallets every 5 minutes
"""
import asyncio
import json
import random
import subprocess
import time
import re
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '.')
from nara_miner import NaraMiner

WALLET_DIR = Path.home() / ".nara-wallets"
ACTIVE_MINERS = 5
ROTATION_INTERVAL = 300  # 5 minutes
STATS_FILE = Path("nara_mining_stats.json")
LOG_FILE = None

class MultiWalletMiner:
    def __init__(self, active_count=5, rotation_interval=300):
        self.active_count = active_count
        self.rotation_interval = rotation_interval
        self.wallets = []
        self.active_indices = []
        self.stats = {
            "total_wallets": 0,
            "active_wallets": [],
            "rotation_count": 0,
            "start_time": None,
            "earnings": {},
            "submissions": {}
        }
        self.load_wallets()
        
    def load_wallets(self):
        """Load all 30 wallets"""
        for i in range(1, 31):
            wallet_file = WALLET_DIR / f"W{i:03d}.json"
            if wallet_file.exists():
                self.wallets.append({
                    "number": i,
                    "id": f"W{i:03d}",
                    "wallet_file": str(wallet_file),
                    "agent_id": f"hitagi-agent-{i:03d}"
                })
        
        self.stats["total_wallets"] = len(self.wallets)
        print(f"🖤 Loaded {len(self.wallets)} wallets")
        
    def select_active(self):
        """Select random active miners"""
        if len(self.wallets) <= self.active_count:
            self.active_indices = list(range(len(self.wallets)))
        else:
            self.active_indices = random.sample(range(len(self.wallets)), self.active_count)
        
        active_ids = [self.wallets[i]["id"] for i in self.active_indices]
        self.stats["active_wallets"] = active_ids
        self.stats["rotation_count"] += 1
        
        print(f"\n{'='*50}")
        print(f"🔄 Rotation #{self.stats['rotation_count']}")
        print(f"⏱️  {datetime.now().strftime('%H:%M:%S')}")
        print(f"🖤 Active miners: {', '.join(active_ids)}")
        print(f"{'='*50}\n")
        
    async def run_miner(self, wallet_idx):
        """Run single miner for one quest cycle"""
        wallet = self.wallets[wallet_idx]
        wallet_id = wallet["id"]
        
        miner = NaraMiner(
            agent_id=wallet["agent_id"],
            relay_threshold=0.0,
            min_time_remaining=20,
            wallet_path=wallet["wallet_file"]
        )
        
        # Check wallet
        if not miner.check_wallet():
            print(f"❌ {wallet_id}: Wallet error")
            return False
        
        # Fetch quest
        quest = miner.fetch_quest()
        if not quest:
            print(f"⏳ {wallet_id}: No active quest")
            return False
        
        question = quest.get("question", "")
        time_remaining = quest.get("timeRemaining", 0)
        
        # Skip check
        should_skip, reason = miner.should_skip_quest(quest)
        if should_skip:
            print(f"⏭️  {wallet_id}: Skip ({reason[:30]})")
            return False
        
        # Solve
        answer = miner.solve_question(question)
        
        if answer == "SKIP_TRIVIA":
            print(f"⏭️  {wallet_id}: Skip trivia")
            return False
        
        print(f"🎯 {wallet_id}: {question[:40]}... -> {answer}")
        
        # Submit
        success, status = miner.submit_answer(answer, True, False)
        
        if success:
            print(f"✅ {wallet_id}: Submitted!")
            self.stats["submissions"][wallet_id] = self.stats["submissions"].get(wallet_id, 0) + 1
            return True
        else:
            print(f"❌ {wallet_id}: {status[:40]}")
            return False
    
    async def mining_round(self):
        """Run one round with active miners (concurrent)"""
        tasks = []
        for idx in self.active_indices:
            task = asyncio.create_task(self.run_miner(idx))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        print(f"\n📊 Round result: {success_count}/{len(tasks)} submitted")
        
    def save_stats(self):
        """Save stats to file"""
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    async def check_balances(self):
        """Check all wallet balances"""
        print("🖤 Checking wallet balances...")
        total_balance = 0.0
        
        for wallet in self.wallets:
            try:
                # Run balance check
                cmd = ["npx", "naracli@latest", "-w", wallet["wallet_file"], "balance"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                # Parse balance from output
                balance_match = re.search(r'(\d+\.?\d*)\s*NARA', result.stdout)
                if balance_match:
                    balance = float(balance_match.group(1))
                    wallet["balance"] = balance
                    total_balance += balance
                else:
                    wallet["balance"] = 0.0
                    
            except Exception as e:
                wallet["balance"] = 0.0
        
        self.stats["total_balance"] = total_balance
        self.stats["wallet_balances"] = {w["id"]: w.get("balance", 0) for w in self.wallets}
        print(f"💰 Total Balance: {total_balance:.4f} NARA")
        return total_balance
    
    async def run(self):
        """Main loop with rotation"""
        print("🖤 NARA MULTI-WALLET MINING BOT")
        print("=" * 50)
        print(f"Total wallets: {self.stats['total_wallets']}")
        print(f"Active miners: {self.active_count}")
        print(f"Rotation: every {self.rotation_interval}s ({self.rotation_interval//60}m)")
        print("=" * 50)
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Initial balance check
        await self.check_balances()
        
        try:
            while True:
                # Check balances every 10 rotations
                if self.stats["rotation_count"] % 10 == 0:
                    await self.check_balances()
                
                # Select new active miners
                self.select_active()
                
                # Run multiple rounds until rotation
                end_time = time.time() + self.rotation_interval
                
                while time.time() < end_time:
                    await self.mining_round()
                    self.save_stats()
                    
                    # Wait before next round
                    wait = 10
                    print(f"\n⏳ Waiting {wait}s...\n")
                    await asyncio.sleep(wait)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
            self.save_stats()
            self.print_final_stats()
    
    def print_final_stats(self):
        """Print final statistics"""
        print("\n" + "=" * 50)
        print("🖤 FINAL STATS")
        print("=" * 50)
        print(f"Rotations: {self.stats['rotation_count']}")
        print(f"Submissions per wallet:")
        for wid, count in sorted(self.stats["submissions"].items()):
            print(f"  {wid}: {count}")
        print("=" * 50)

if __name__ == "__main__":
    miner = MultiWalletMiner(active_count=5, rotation_interval=300)
    asyncio.run(miner.run())
