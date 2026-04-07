#!/usr/bin/env python3
"""
NARA Twitter Binder (Batch)
Bind Twitter untuk semua 30 wallet untuk dapat 20 NARA + stake-free mining.
⚠️  WARNING: Requires manual tweet posting for each wallet
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional

WALLET_DIR = Path.home() / ".nara-wallets"
MAX_WALLETS = 30

def run_cli(wallet_idx: int, cmd: list, capture_json: bool = False) -> tuple:
    """Run naracli command for specific wallet"""
    wallet_file = WALLET_DIR / f"W{wallet_idx:03d}.json"
    
    if not wallet_file.exists():
        return False, "Wallet not found"
    
    env = os.environ.copy()
    env["NARA_WALLET"] = str(wallet_file)
    
    full_cmd = ["npx", "naracli@latest"] + cmd
    
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def get_bind_instructions(wallet_idx: int) -> Optional[str]:
    """Get tweet content untuk di-post"""
    success, output = run_cli(wallet_idx, ["agent", "bind-twitter"])
    
    if success:
        # Extract tweet content dari output
        lines = output.split('\n')
        for line in lines:
            if "tweet" in line.lower() or "post" in line.lower():
                return line.strip()
        return output  # Return full output kalo ga ketemu
    return None

def bind_wallet(wallet_idx: int, tweet_url: str) -> bool:
    """Bind wallet dengan tweet URL"""
    success, output = run_cli(
        wallet_idx, 
        ["agent", "bind-twitter", tweet_url, "--relay"]
    )
    
    if success and ("success" in output.lower() or "verified" in output.lower()):
        return True
    return False

def main():
    print("="*60)
    print("🐦 NARA Twitter Batch Binder (30 Wallets)")
    print("="*60)
    print("\n⚠️  PROSEDUR:")
    print("1. Tool akan kasih tweet content per wallet")
    print("2. LU POST TWEET MANUAL di Twitter/X")
    print("3. Masukkan tweet URL")
    print("4. Tool akan auto-bind via relay")
    print("\n💰 REWARD: 20 NARA + stake-free mining per wallet")
    print("📊 TOTAL POTENSI: 600 NARA (30 wallets)")
    print("="*60)
    
    confirm = input("\nLanjut? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled")
        return
    
    success_count = 0
    
    for i in range(1, MAX_WALLETS + 1):
        wallet_id = f"W{i:03d}"
        print(f"\n{'='*60}")
        print(f"🔄 Wallet {wallet_id} ({i}/{MAX_WALLETS})")
        print(f"{'='*60}")
        
        # Get instructions
        print("\n📋 Tweet Instructions:")
        instructions = get_bind_instructions(i)
        
        if instructions:
            print(instructions)
        else:
            print("⚠️  Gagal ambil instructions. Skip wallet ini.")
            continue
        
        # Ask for tweet URL
        print("\n👉 Post tweet di Twitter, kemudian:")
        tweet_url = input(f"Masukkan tweet URL untuk {wallet_id}: ").strip()
        
        if not tweet_url:
            print("⏭️  Skip (no URL provided)")
            continue
        
        if not tweet_url.startswith("http"):
            print("❌ Invalid URL format. Skip.")
            continue
        
        # Bind
        print(f"🔗 Binding {wallet_id}...")
        if bind_wallet(i, tweet_url):
            print(f"✅ {wallet_id} berhasil bind!")
            print(f"   Reward: 20 NARA + stake-free mining credits")
            success_count += 1
        else:
            print(f"❌ {wallet_id} gagal bind. Cek manual:")
            print(f"   npx naracli -w ~/.nara-wallets/{wallet_id}.json agent bind-twitter")
        
        # Delay antar wallet
        if i < MAX_WALLETS:
            print("\n⏳ Pause 2 detik...")
            import time
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"🎉 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Berhasil bind: {success_count}/{MAX_WALLETS}")
    print(f"💰 Total reward: {success_count * 20} NARA")
    print(f"🚀 Stake-free mining: {success_count} wallets")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
