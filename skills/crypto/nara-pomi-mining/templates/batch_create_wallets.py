#!/usr/bin/env python3
"""
Batch create NARA wallets W002-W030
Creates wallets sequentially to avoid conflicts
"""
import subprocess
import json
import os
import sys
from pathlib import Path

WALLET_DIR = Path("~/.nara-wallets").expanduser()
MNEMONIC_DIR = Path("~/.nara-mnemonics").expanduser()
DEFAULT_WALLET = Path("~/.config/nara/id.json").expanduser()

def wallet_exists(wallet_num):
    return (WALLET_DIR / f"W{wallet_num:03d}.json").exists()

def create_wallet(wallet_num):
    """Create single wallet and move to numbered location"""
    wallet_file = WALLET_DIR / f"W{wallet_num:03d}.json"
    log_file = MNEMONIC_DIR / f"W{wallet_num:03d}-creation.log"
    mnemonic_file = MNEMONIC_DIR / f"W{wallet_num:03d}-mnemonic.txt"
    
    print(f"Creating W{wallet_num:03d}...", end=' ')
    
    # Remove any existing default wallet (prevents conflict)
    if DEFAULT_WALLET.exists():
        DEFAULT_WALLET.unlink()
    
    # Create wallet
    result = subprocess.run(
        ["npx", "naracli@latest", "wallet", "create"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Save log
    with open(log_file, 'w') as f:
        f.write(result.stdout + "\n" + result.stderr)
    
    # Move wallet to numbered location
    if DEFAULT_WALLET.exists():
        os.rename(DEFAULT_WALLET, wallet_file)
        
        # Extract mnemonic
        mnemonic = None
        for line in result.stdout.split('\n'):
            if 'mnemonic' in line.lower() or 'phrase' in line.lower():
                mnemonic = line.split(':')[-1].strip() if ':' in line else line.strip()
        
        if mnemonic:
            with open(mnemonic_file, 'w') as f:
                f.write(f"W{wallet_num:03d}: {mnemonic}\n")
        
        print("✓")
        return True
    else:
        print(f"✗ ({result.stderr[-50:]}...)")
        return False

def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    print(f"Creating wallets W{start:03d} - W{start+count-1:03d}")
    print("=" * 40)
    
    created = 0
    failed = []
    
    for i in range(start, start + count):
        if wallet_exists(i):
            print(f"W{i:03d} already exists, skipping")
            created += 1
            continue
        
        if create_wallet(i):
            created += 1
        else:
            failed.append(i)
        
        # Small delay to prevent rate limiting
        import time
        time.sleep(1)
    
    print("=" * 40)
    print(f"Created: {created}/{count}")
    if failed:
        print(f"Failed: {[f'W{i:03d}' for i in failed]}")
        print(f"\nRetry: python3 batch_create_wallets.py {failed[0]} {len(failed)}")

if __name__ == "__main__":
    main()
