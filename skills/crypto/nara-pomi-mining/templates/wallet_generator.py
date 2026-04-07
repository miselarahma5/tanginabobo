#!/usr/bin/env python3
"""
NARA Multi-Wallet Generator (30 Wallets)
⚠️  WARNING: This handles sensitive private keys. Use with caution.
"""

import os
import sys
import json
import subprocess
import getpass
from datetime import datetime
from pathlib import Path

WALLET_COUNT = 30
WALLET_DIR = Path.home() / ".nara-wallets"
MNEMONIC_DIR = Path.home() / ".nara-mnemonics"

def setup_directories():
    """Create secure wallet directories"""
    WALLET_DIR.mkdir(mode=0o700, exist_ok=True)
    MNEMONIC_DIR.mkdir(mode=0o700, exist_ok=True)
    
    # Create .gitignore to prevent accidental commits
    gitignore = WALLET_DIR / ".gitignore"
    gitignore.write_text("*\n!.gitignore\n")
    
    print(f"🖤 Wallet directory: {WALLET_DIR}")
    print(f"🖤 Mnemonic directory: {MNEMONIC_DIR}")

def generate_wallet(wallet_num: int) -> dict:
    """Generate single NARA wallet using naracli"""
    wallet_id = f"W{wallet_num:03d}"
    wallet_file = WALLET_DIR / f"{wallet_id}.json"
    mnemonic_file = MNEMONIC_DIR / f"{wallet_id}-mnemonic.txt"
    
    print(f"\n🔑 Generating {wallet_id}...")
    
    # Set environment to use specific wallet file
    env = os.environ.copy()
    env["NARA_WALLET"] = str(wallet_file)
    
    # Create wallet using naracli
    cmd = ["npx", "naracli@latest", "wallet", "create"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to create {wallet_id}: {result.stderr}")
            return None
        
        # Extract mnemonic from output (should be shown once)
        output = result.stdout + result.stderr
        
        # Save output for manual mnemonic extraction
        log_file = MNEMONIC_DIR / f"{wallet_id}-creation.log"
        log_file.write_text(output)
        
        print(f"  ✓ {wallet_id} created")
        print(f"  ⚠️  IMPORTANT: Check {log_file} for mnemonic")
        
        return {
            "wallet_id": wallet_id,
            "wallet_file": str(wallet_file),
            "status": "created"
        }
        
    except Exception as e:
        print(f"❌ Error creating {wallet_id}: {e}")
        return None

def register_agent(wallet_num: int, agent_id: str, use_relay: bool = True) -> bool:
    """Register agent for wallet"""
    wallet_id = f"W{wallet_num:03d}"
    wallet_file = WALLET_DIR / f"{wallet_id}.json"
    
    print(f"\n🤖 Registering agent {agent_id}...")
    
    env = os.environ.copy()
    env["NARA_WALLET"] = str(wallet_file)
    
    cmd = [
        "npx", "naracli@latest",
        "agent", "register", agent_id,
        "--relay" if use_relay else ""
    ]
    cmd = [c for c in cmd if c]  # Remove empty strings
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"  ✓ Agent {agent_id} registered")
            return True
        else:
            # Check if already registered
            if "already exists" in result.stderr.lower():
                print(f"  ℹ️  Agent {agent_id} already registered")
                return True
            print(f"  ❌ Failed: {result.stderr[:100]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def generate_all_wallets():
    """Generate all 30 wallets"""
    print("="*60)
    print("🖤 NARA Multi-Wallet Generator (30 Wallets)")
    print("="*60)
    print("\n⚠️  SECURITY WARNINGS:")
    print("- 30 wallets will be created with separate key files")
    print("- Mnemonics are CRITICAL - lose them = lose funds")
    print(f"- Wallets saved to: {WALLET_DIR}")
    print(f"- Logs saved to: {MNEMONIC_DIR}")
    print("\n🔒 Directories have strict permissions (0700)")
    print("🚫 DO NOT upload these folders to GitHub/cloud")
    print("="*60)
    
    confirm = input("\nContinue with 30 wallet generation? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled")
        return
    
    # Setup
    setup_directories()
    
    # Check naracli installed
    print("\n📦 Checking naracli...")
    result = subprocess.run(
        ["npx", "naracli@latest", "--version"],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        print("❌ naracli not found. Install first: npm install -g naracli")
        return
    print("✓ naracli found")
    
    # Generate wallets
    wallets = []
    for i in range(1, WALLET_COUNT + 1):
        wallet = generate_wallet(i)
        if wallet:
            wallets.append(wallet)
        
        # Small delay to prevent rate limiting
        import time
        time.sleep(0.5)
    
    # Save wallet index
    index_file = WALLET_DIR / "wallet-index.json"
    index_file.write_text(json.dumps({
        "created_at": datetime.now().isoformat(),
        "count": len(wallets),
        "wallets": wallets
    }, indent=2))
    
    print(f"\n{'='*60}")
    print(f"✅ Generated {len(wallets)}/{WALLET_COUNT} wallets")
    print(f"📁 Location: {WALLET_DIR}")
    print(f"📝 Index: {index_file}")
    
    print("\n⚠️  NEXT STEPS - CRITICAL:")
    print("1. Extract mnemonics from log files in:", MNEMONIC_DIR)
    print("2. Write down mnemonics on PAPER (offline)")
    print("3. Store in secure location (safe, encrypted drive)")
    print("4. NEVER share mnemonics with anyone")
    print("\n🤖 To register agents, run:")
    print("   python3 wallet_generator.py --register")
    print("="*60)

def register_all_agents():
    """Register agents for all wallets"""
    index_file = WALLET_DIR / "wallet-index.json"
    
    if not index_file.exists():
        print("❌ No wallet index found. Generate wallets first!")
        return
    
    index = json.loads(index_file.read_text())
    
    print("="*60)
    print("🤖 Registering 30 Agents")
    print("="*60)
    
    # Ask for referral
    referral = input("Referral agent ID (optional, press Enter to skip): ").strip()
    
    success_count = 0
    for i in range(1, WALLET_COUNT + 1):
        agent_id = f"{index['wallets'][i-1]['wallet_id']}-miner"
        
        success = register_agent(i, agent_id, use_relay=True)
        if success:
            success_count += 1
        
        # Delay to prevent rate limiting
        import time
        time.sleep(1)
    
    print(f"\n✅ Registered {success_count}/{WALLET_COUNT} agents")

def show_status():
    """Show wallet and agent status"""
    index_file = WALLET_DIR / "wallet-index.json"
    
    if not index_file.exists():
        print("❌ No wallets found")
        return
    
    index = json.loads(index_file.read_text())
    
    print("="*60)
    print("📊 Wallet Status")
    print("="*60)
    
    for wallet in index["wallets"]:
        wallet_id = wallet["wallet_id"]
        wallet_file = Path(wallet["wallet_file"])
        
        status = "✓" if wallet_file.exists() else "✗"
        
        # Check agent
        env = os.environ.copy()
        env["NARA_WALLET"] = str(wallet_file)
        
        result = subprocess.run(
            ["npx", "naracli@latest", "agent", "get", "--json"],
            capture_output=True,
            text=True,
            env=env,
            timeout=10
        )
        
        agent_status = "❓"
        if result.returncode == 0 and "id" in result.stdout:
            agent_status = "✓"
        
        print(f"{wallet_id}: Wallet {status} | Agent {agent_status}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NARA 30-Wallet Generator")
    parser.add_argument("--generate", action="store_true", help="Generate 30 wallets")
    parser.add_argument("--register", action="store_true", help="Register 30 agents")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    if args.register:
        register_all_agents()
    elif args.status:
        show_status()
    else:
        generate_all_wallets()
