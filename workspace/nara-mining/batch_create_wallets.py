#!/usr/bin/env python3
"""
Batch create NARA wallets W002-W030
Creates 3 wallets per run to avoid timeout
"""
import subprocess
import json
import os
import sys
from pathlib import Path

WALLET_DIR = Path("~/.nara-wallets").expanduser()
MNEMONIC_DIR = Path("~/.nara-mnemonics").expanduser()

def wallet_exists(wallet_num):
    return (WALLET_DIR / f"W{wallet_num:03d}.json").exists()

def create_wallet(wallet_num):
    wallet_file = WALLET_DIR / f"W{wallet_num:03d}.json"
    log_file = MNEMONIC_DIR / f"W{wallet_num:03d}-creation.log"
    
    print(f"Creating W{wallet_num:03d}...")
    
    # Run wallet create
    result = subprocess.run(
        ["npx", "naracli@latest", "wallet", "create", "-w", str(wallet_file)],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Save output
    with open(log_file, 'w') as f:
        f.write(result.stdout + "\n" + result.stderr)
    
    # Check if wallet created
    if wallet_file.exists():
        # Extract mnemonic from output
        for line in result.stdout.split('\n'):
            if 'mnemonic' in line.lower() or 'phrase' in line.lower():
                mnemonic = line.split(':')[-1].strip() if ':' in line else line.strip()
                mnemonic_file = MNEMONIC_DIR / f"W{wallet_num:03d}-mnemonic.txt"
                with open(mnemonic_file, 'w') as f:
                    f.write(f"W{wallet_num:03d}: {mnemonic}\n")
                print(f"  ✓ W{wallet_num:03d} created + mnemonic saved")
                return True
        
        # If mnemonic not found in stdout, try to extract from file
        print(f"  ✓ W{wallet_num:03d} created (mnemonic in log)")
        return True
    else:
        print(f"  ✗ W{wallet_num:03d} failed: {result.stderr[-200:]}")
        return False

def main():
    # Check args
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
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
    
    print("=" * 40)
    print(f"Created: {created}/{count}")
    if failed:
        print(f"Failed: {[f'W{i:03d}' for i in failed]}")
        print(f"\nRetry with: python3 batch_create_wallets.py {failed[0]} {len(failed)}")

if __name__ == "__main__":
    main()
