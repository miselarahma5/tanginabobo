#!/usr/bin/env python3
"""
NARA Multi-Wallet Mining Runner
5 active miners, rotate every 5 minutes
Math-only solver, no API key required
"""

import asyncio
import json
import random
import time
from pathlib import Path
from nara_miner import NaraMiner

WALLET_DIR = Path.home() / ".nara-wallets"
STATS_FILE = Path("nara_mining_stats.json")
ACTIVE_MINERS = 5
ROTATION_INTERVAL = 300  # 5 minutes

class MultiWalletMiner:
    def __init__(self):
        self.wallets = []
        self.active_indices = []
        self.stats = {
            "total_wallets": 30,
            "active_wallets": [],
            "rotation_count": 0,
            "start_time": time.time(),
            "submissions": {}
        }
        self.load_wallets()
        
    def load_wallets(self):
        """Load W001-W030"""
        for i in range(1, 31):
            wallet_file = WALLET_DIR / f"W{i:03d}.json"
            if wallet_file.exists():
                self.wallets.append({
                    "number": i,
                    "id": f"W{i:03d}",
                    "wallet_file": str(wallet_file),
                    "agent_id": f"hitagi-agent-{i:03d}"
                })
        print(f"🖤 Loaded {len(self.wallets)} wallets")
    
    def select_active(self):
        """Select 5 random wallets"""
        self.active_indices = random.sample(range(len(self.wallets)), ACTIVE_MINERS)
        self.stats["active_wallets"] = [self.wallets[i]["id"] for i in self.active_indices]
        self.stats["rotation_count"] += 1
        print(f"\n🔄 Rotation #{self.stats['rotation_count']}: " + ", ".join(self.stats["active_wallets"]))
    
    async def run_miner(self, wallet_idx):
        """Run single wallet mining cycle"""
        w = self.wallets[wallet_idx]
        
        miner = NaraMiner(
            agent_id=w["agent_id"],
            relay_threshold=0.0,
            min_time_remaining=15,  # Skip if < 15s
            wallet_path=w["wallet_file"]
        )
        
        # Check wallet
        if not miner.check_wallet():
            print(f"❌ {w['id']}: Wallet error")
            return False
        
        # Fetch quest
        quest = miner.fetch_quest()
        if not quest:
            print(f"⏳ {w['id']}: No quest")
            return False
        
        question = quest.get("question", "")
        time_remaining = quest.get("timeRemaining", 0)
        
        # Skip check (time/stake)
        should_skip, reason = miner.should_skip_quest(quest)
        if should_skip:
            print(f"⏭️  {w['id']}: Skip ({reason[:30]})")
            return False
        
        # Solve
        answer = miner.solve_question(question)
        if answer == "SKIP_TRIVIA":
            print(f"⏭️  {w['id']}: Skip trivia")
            return False
        
        print(f"🎯 {w['id']}: {question[:40]}... -> {answer}")
        
        # Submit
        success, status = miner.submit_answer(answer, use_relay=True, auto_stake=False)
        
        if success:
            print(f"✅ {w['id']}: Submitted!")
            self.stats["submissions"][w["id"]] = self.stats["submissions"].get(w["id"], 0) + 1
            self.save_stats()
            return True
        else:
            print(f"❌ {w['id']}: {status[:40]}")
            return False
    
    async def mining_round(self):
        """Run all active miners concurrently"""
        tasks = [asyncio.create_task(self.run_miner(i)) for i in self.active_indices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if r is True)
        print(f"📊 Round: {success}/{len(tasks)} submitted")
    
    def save_stats(self):
        """Save to JSON for dashboard"""
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    async def run(self):
        """Main loop"""
        print("🖤 NARA Multi-Wallet Mining")
        print("Mode: Math-Only | 5 active | 5min rotation\n")
        
        try:
            while True:
                self.select_active()
                end_time = time.time() + ROTATION_INTERVAL
                
                while time.time() < end_time:
                    await self.mining_round()
                    print("⏳ Waiting 10s...\n")
                    await asyncio.sleep(10)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            self.save_stats()

if __name__ == "__main__":
    miner = MultiWalletMiner()
    asyncio.run(miner.run())
