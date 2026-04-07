#!/usr/bin/env python3
"""
NARA PoMI Mining Bot
Auto-answer on-chain quests to earn NARA via Proof of Machine Intelligence (PoMI)
"""

import asyncio
import json
import time
import random
import subprocess
import logging
import re
import os
from datetime import datetime
from typing import Dict, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class NaraMiner:
    """
    NARA PoMI Mining Bot
    
    Flow:
    1. Check wallet exists
    2. Check agent registered
    3. Check balance
    4. Fetch quest
    5. Solve question
    6. Submit answer (relay or direct)
    7. Loop
    """
    
    def __init__(
        self,
        agent_id: str = "hermes-auto-miner",
        agent_type: str = "hermes",
        model: str = "k2.5",
        relay_threshold: float = 0.1,
        min_time_remaining: int = 10,
        wallet_path: str = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model = model
        self.relay_threshold = relay_threshold  # Use relay if balance < this
        self.min_time_remaining = min_time_remaining  # Skip if timeRemaining < this
        self.wallet_path = wallet_path or os.path.expanduser("~/.nara-wallets/W001.json")
        
        self.stats = {
            "total_quests": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "earned_nara": 0.0,
            "start_time": None
        }
        
        self.wallet_address = None
        self.agent_registered = False
        self.balance = 0.0
        
    def run_cli(self, cmd: list, capture_json: bool = True) -> Tuple[bool, any]:
        """Run npx naracli command with wallet"""
        try:
            # Add npx prefix and wallet flag
            full_cmd = ["npx", "naracli@latest", "-w", self.wallet_path] + cmd
            
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Check for specific errors
                if "6003" in result.stderr:
                    return False, {"error": "wrong_answer", "code": 6003}
                elif "6007" in result.stderr:
                    return False, {"error": "already_submitted", "code": 6007}
                else:
                    logger.error(f"CLI error: {result.stderr}")
                    return False, result.stderr
            
            if capture_json:
                try:
                    return True, json.loads(result.stdout)
                except json.JSONDecodeError:
                    return True, result.stdout
            else:
                return True, result.stdout
                
        except subprocess.TimeoutExpired:
            logger.error("Command timeout")
            return False, "timeout"
        except Exception as e:
            logger.error(f"CLI exception: {e}")
            return False, str(e)
    
    def check_wallet(self) -> bool:
        """Check if wallet exists"""
        success, result = self.run_cli(["address"], capture_json=False)
        if success and result and "Error" not in result:
            self.wallet_address = result.strip()
            logger.info(f"✓ Wallet: {self.wallet_address[:20]}...")
            return True
        else:
            logger.error("✗ No wallet found. Run: npx naracli wallet create")
            return False
    
    def check_agent(self) -> bool:
        """Check if agent is registered"""
        success, result = self.run_cli(["agent", "get", "--json"])
        if success and isinstance(result, dict) and "id" in result:
            self.agent_registered = True
            agent_id = result.get("id", "unknown")
            points = result.get("points", 0)
            logger.info(f"✓ Agent: {agent_id} | Points: {points}")
            return True
        else:
            logger.warning("✗ Agent not registered")
            logger.info("Register with: npx naracli agent register <id> --relay")
            return False
    
    def check_balance(self) -> float:
        """Check NARA balance"""
        success, result = self.run_cli(["balance", "--json"])
        if success and isinstance(result, dict):
            self.balance = float(result.get("balance", 0))
            logger.info(f"💰 Balance: {self.balance:.4f} NARA")
            return self.balance
        else:
            logger.warning("Could not check balance, assuming 0")
            self.balance = 0
            return 0
    
    def fetch_quest(self) -> Optional[Dict]:
        """Fetch current quest"""
        success, result = self.run_cli(["quest", "get", "--json"])
        if not success or not isinstance(result, dict):
            logger.warning("Failed to fetch quest")
            return None
        
        # Check if quest is active
        if result.get("expired") or not result.get("active", True):
            logger.info("No active quest, waiting...")
            return None
        
        return result
    
    def should_skip_quest(self, quest: Dict) -> tuple[bool, str]:
        """Determine if we should skip this quest"""
        time_remaining = quest.get("timeRemaining", 0)
        
        # Parse time string like "1m 45s" to seconds
        if isinstance(time_remaining, str):
            minutes = 0
            seconds = 0
            m_match = re.search(r'(\d+)m', time_remaining)
            s_match = re.search(r'(\d+)s', time_remaining)
            if m_match:
                minutes = int(m_match.group(1))
            if s_match:
                seconds = int(s_match.group(1))
            time_remaining = minutes * 60 + seconds
        
        if time_remaining <= self.min_time_remaining:
            return True, f"timeRemaining ({time_remaining}s) <= {self.min_time_remaining}s"
        
        # Parse stake requirement (may include " NARA" suffix)
        stake_str = str(quest.get("stakeRequirement", "0") or "0")
        stake_num = re.search(r'([\d.]+)', stake_str)
        stake_requirement = float(stake_num.group(1)) if stake_num else 0
        
        # Parse free credits
        free_str = str(quest.get("freeCredits", "0") or "0")
        free_num = re.search(r'([\d.]+)', free_str)
        free_credits = float(free_num.group(1)) if free_num else 0
        
        if stake_requirement > 0 and self.balance < stake_requirement and free_credits <= 0:
            return True, "insufficient stake and free credits"
        
        return False, ""
    
    def solve_question(self, question: str) -> str:
        """Solve quest using AI solver"""
        try:
            import ai_solver
            answer = ai_solver.solve(question)
            if answer == "SKIP_TRIVIA":
                return "SKIP_TRIVIA"
            return answer
        except Exception as e:
            logger.warning(f"AI solver failed: {e}")
            return "SKIP_TRIVIA"
    def submit_answer(
        self, 
        answer: str, 
        use_relay: bool = False,
        auto_stake: bool = False
    ) -> Tuple[bool, str]:
        """Submit quest answer"""
        cmd = [
            "quest", "answer",
            answer,
            "--agent", self.agent_type,
            "--model", self.model
        ]
        
        if use_relay or self.balance < self.relay_threshold:
            cmd.append("--relay")
            logger.info("Using relay (gasless)")
        
        if auto_stake:
            cmd.append("--stake")
            cmd.append("auto")
        
        success, result = self.run_cli(cmd, capture_json=False)
        
        if success:
            logger.info(f"✓ Answer submitted")
            return True, "success"
        elif isinstance(result, dict):
            error_code = result.get("code", 0)
            if error_code == 6003:
                return False, "wrong_answer_or_expired"
            elif error_code == 6007:
                return False, "already_submitted"
            else:
                return False, f"error_{error_code}"
        else:
            return False, str(result)
    
    async def mining_loop(self):
        """Main mining loop"""
        logger.info("🖤 Starting NARA PoMI Mining...")
        logger.info(f"Agent: {self.agent_id}")
        logger.info(f"Model: {self.model}")
        
        self.stats["start_time"] = datetime.now()
        
        while True:
            try:
                # 1. Check wallet
                if not self.wallet_address:
                    if not self.check_wallet():
                        logger.error("No wallet. Create one first!")
                        await asyncio.sleep(60)
                        continue
                
                # 2. Check agent
                if not self.agent_registered:
                    self.check_agent()  # Don't stop, just warn
                
                # 3. Check balance
                self.check_balance()
                
                # 4. Fetch quest
                quest = self.fetch_quest()
                if not quest:
                    await asyncio.sleep(5)
                    continue
                
                self.stats["total_quests"] += 1
                
                question = quest.get("question", "")
                time_remaining = quest.get("timeRemaining", 0)
                
                logger.info(f"🎯 Quest: {question[:60]}...")
                logger.info(f"⏱️  Time remaining: {time_remaining}s")
                
                # 5. Check if we should skip
                should_skip, reason = self.should_skip_quest(quest)
                if should_skip:
                    logger.info(f"⏭️  Skipping: {reason}")
                    self.stats["skipped"] += 1
                    await asyncio.sleep(5)
                    continue
                
                # 6. Solve question
                answer = self.solve_question(question)
                
                # Skip if trivia
                if answer == "SKIP_TRIVIA":
                    logger.info("⏭️  Skipping trivia question")
                    self.stats["skipped"] += 1
                    await asyncio.sleep(5)
                    continue
                
                logger.info(f"🎯 Answer: {answer}")
                
                # 7. Submit answer
                use_relay = self.balance < self.relay_threshold
                stake_req = quest.get("stakeRequirement", 0)
                auto_stake = stake_req > 0 and self.balance >= stake_req
                
                success, status = self.submit_answer(answer, use_relay, auto_stake)
                
                if success:
                    logger.info(f"✅ Submitted: {status}")
                    self.stats["successful"] += 1
                    # Assume we earned something (will be confirmed next balance check)
                else:
                    logger.warning(f"❌ Failed: {status}")
                    self.stats["failed"] += 1
                    
                    if status == "wrong_answer_or_expired":
                        logger.info("Wrong answer or expired - adjust timing/solver")
                    elif status == "already_submitted":
                        logger.info("Already submitted this round")
                
                # 8. Wait for round to end
                wait_time = max(1, time_remaining + 1)
                logger.info(f"⏳ Waiting {wait_time}s for next round...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Mining stopped by user")
                break
            except Exception as e:
                logger.error(f"Mining loop error: {e}")
                await asyncio.sleep(10)
    
    def print_dashboard(self):
        """Print mining stats"""
        if not self.stats["start_time"]:
            return
        
        runtime = datetime.now() - self.stats["start_time"]
        runtime_str = str(runtime).split('.')[0]
        
        print("\n" + "="*50)
        print(f"🖤 NARA PoMI MINER - {self.agent_id}")
        print("="*50)
        print(f"⏱️  Runtime: {runtime_str}")
        print(f"💰 Balance: {self.balance:.4f} NARA")
        print(f"📊 Total Quests: {self.stats['total_quests']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"⏭️  Skipped: {self.stats['skipped']}")
        print("="*50)
        print("🚀 Mining NARA 24/7 with ZK proofs!")
        print("="*50 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NARA PoMI Mining Bot")
    parser.add_argument("--agent-id", default="hermes-auto-miner", help="Agent ID")
    parser.add_argument("--agent-type", default="hermes", help="Agent type")
    parser.add_argument("--model", default="k2.5", help="Model name")
    parser.add_argument("--relay-threshold", type=float, default=0.1, help="Balance threshold for relay")
    
    args = parser.parse_args()
    
    miner = NaraMiner(
        agent_id=args.agent_id,
        agent_type=args.agent_type,
        model=args.model,
        relay_threshold=args.relay_threshold
    )
    
    try:
        asyncio.run(miner.mining_loop())
    except KeyboardInterrupt:
        miner.print_dashboard()
        print("\n🖤 Mining stopped. See you next time!")


if __name__ == "__main__":
    main()
