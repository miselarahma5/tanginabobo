#!/usr/bin/env python3
"""
NARA PoMI Mining Bot - Math-Only Solver
Auto-answer on-chain quests to earn NARA
Features:
- Regex-based math solving (no API needed)
- Auto-skip trivia questions
- Gasless relay submission
- Stake-free credit support
"""

import asyncio
import json
import re
import subprocess
import logging
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
    NARA PoMI Mining Bot with math-only solver
    """
    
    def __init__(
        self,
        agent_id: str = "auto-miner",
        agent_type: str = "hermes",
        model: str = "k2.5",
        relay_threshold: float = 0.1,
        min_time_remaining: int = 15,
        wallet_path: str = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model = model
        self.relay_threshold = relay_threshold
        self.min_time_remaining = min_time_remaining
        self.wallet_path = wallet_path
        
        self.stats = {
            "total_quests": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None
        }
        
        self.wallet_address = None
        self.agent_registered = False
        self.balance = 0.0
        
    def run_cli(self, cmd: list, capture_json: bool = True) -> Tuple[bool, any]:
        """Run naracli with wallet flag"""
        try:
            # CRITICAL: Use -w flag, not NARA_WALLET env var
            full_cmd = ["npx", "naracli@latest"]
            if self.wallet_path:
                full_cmd.extend(["-w", self.wallet_path])
            full_cmd.extend(cmd)
            
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                if "6003" in result.stderr:
                    return False, {"error": "wrong_answer", "code": 6003}
                elif "6007" in result.stderr:
                    return False, {"error": "already_submitted", "code": 6007}
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
    
    def check_wallet(self) -> bool:
        """Check wallet exists"""
        success, result = self.run_cli(["address"], capture_json=False)
        if success and result and "Error" not in result:
            self.wallet_address = result.strip()
            logger.info(f"✓ Wallet: {self.wallet_address[:20]}...")
            return True
        logger.error("✗ No wallet found")
        return False
    
    def check_agent(self) -> bool:
        """Check agent registration"""
        success, result = self.run_cli(["agent", "get"], capture_json=False)
        if success and "Agent ID" in str(result):
            self.agent_registered = True
            return True
        logger.warning("✗ Agent not registered")
        return False
    
    def fetch_quest(self) -> Optional[Dict]:
        """Fetch current quest"""
        success, result = self.run_cli(["quest", "get"], capture_json=False)
        if not success:
            return None
        
        # Parse text output into dict
        quest = {"raw": result}
        for line in str(result).split('\n'):
            if 'Question:' in line:
                quest['question'] = line.split('Question:')[1].strip()
            elif 'Time remaining:' in line:
                quest['timeRemaining'] = line.split(':')[1].strip()
            elif 'freeCredits:' in line or 'Stake-free credits:' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    quest['freeCredits'] = int(match.group(1))
            elif 'stakeRequirement:' in line or 'Stake requirement:' in line:
                match = re.search(r'([\d.]+)', line)
                if match:
                    quest['stakeRequirement'] = match.group(1)
        
        return quest
    
    def should_skip_quest(self, quest: Dict) -> Tuple[bool, str]:
        """Determine if quest should be skipped"""
        # Parse timeRemaining (format: "1m 45s")
        time_str = quest.get("timeRemaining", "0")
        minutes = 0
        seconds = 0
        m_match = re.search(r'(\d+)m', str(time_str))
        s_match = re.search(r'(\d+)s', str(time_str))
        if m_match:
            minutes = int(m_match.group(1))
        if s_match:
            seconds = int(s_match.group(1))
        time_remaining = minutes * 60 + seconds
        
        if time_remaining <= self.min_time_remaining:
            return True, f"timeRemaining ({time_remaining}s) <= {self.min_time_remaining}s"
        
        # Parse stake requirement (format: "1363.90 NARA")
        stake_str = str(quest.get("stakeRequirement", "0") or "0")
        stake_match = re.search(r'([\d.]+)', stake_str)
        stake_requirement = float(stake_match.group(1)) if stake_match else 0
        
        free_str = str(quest.get("freeCredits", "0") or "0")
        free_match = re.search(r'(\d+)', free_str)
        free_credits = int(free_match.group(1)) if free_match else 0
        
        if stake_requirement > 0 and self.balance < stake_requirement and free_credits <= 0:
            return True, "insufficient stake and free credits"
        
        return False, ""
    
    def solve_question(self, question: str) -> str:
        """Solve using ai_solver"""
        try:
            import ai_solver
            return ai_solver.solve(question)
        except Exception as e:
            logger.warning(f"Solver error: {e}")
            return "SKIP_TRIVIA"
    
    def submit_answer(self, answer: str, use_relay: bool = True) -> Tuple[bool, str]:
        """Submit answer"""
        cmd = [
            "quest", "answer", answer,
            "--agent", self.agent_type,
            "--model", self.model
        ]
        
        if use_relay:
            cmd.append("--relay")
        
        success, result = self.run_cli(cmd, capture_json=False)
        
        if success:
            return True, "success"
        
        if isinstance(result, dict):
            code = result.get("code", 0)
            if code == 6003:
                return False, "wrong_answer"
            elif code == 6007:
                return False, "already_submitted"
        
        return False, str(result)[:50]
    
    async def mining_loop(self):
        """Main mining loop"""
        logger.info("🖤 Starting NARA PoMI Mining...")
        self.stats["start_time"] = datetime.now()
        
        while True:
            try:
                # Check wallet
                if not self.wallet_address:
                    if not self.check_wallet():
                        await asyncio.sleep(60)
                        continue
                
                # Check agent
                self.check_agent()
                
                # Fetch quest
                quest = self.fetch_quest()
                if not quest:
                    await asyncio.sleep(5)
                    continue
                
                self.stats["total_quests"] += 1
                
                question = quest.get("question", "")
                logger.info(f"🎯 {question[:50]}...")
                
                # Check skip
                should_skip, reason = self.should_skip_quest(quest)
                if should_skip:
                    logger.info(f"⏭️ Skip: {reason}")
                    self.stats["skipped"] += 1
                    await asyncio.sleep(5)
                    continue
                
                # Solve
                answer = self.solve_question(question)
                
                if answer == "SKIP_TRIVIA":
                    logger.info("⏭️ Skipping trivia")
                    self.stats["skipped"] += 1
                    await asyncio.sleep(5)
                    continue
                
                logger.info(f"🎯 Answer: {answer}")
                
                # Submit
                success, status = self.submit_answer(answer, True)
                
                if success:
                    logger.info("✅ Submitted!")
                    self.stats["successful"] += 1
                else:
                    logger.warning(f"❌ Failed: {status}")
                    self.stats["failed"] += 1
                
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(10)
    
    def print_dashboard(self):
        """Print stats"""
        if not self.stats["start_time"]:
            return
        
        runtime = datetime.now() - self.stats["start_time"]
        print("\n" + "="*50)
        print(f"🖤 NARA MINER - {self.agent_id}")
        print(f"⏱️ Runtime: {str(runtime).split('.')[0]}")
        print(f"🎯 Quests: {self.stats['total_quests']}")
        print(f"✅ Success: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"⏭️ Skipped: {self.stats['skipped']}")
        print("="*50)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallet", default="~/.nara-wallets/W001.json")
    parser.add_argument("--agent-id", default="auto-miner")
    parser.add_argument("--min-time", type=int, default=15)
    args = parser.parse_args()
    
    import os
    wallet_path = os.path.expanduser(args.wallet)
    
    miner = NaraMiner(
        agent_id=args.agent_id,
        min_time_remaining=args.min_time,
        wallet_path=wallet_path
    )
    
    try:
        asyncio.run(miner.mining_loop())
    except KeyboardInterrupt:
        miner.print_dashboard()
