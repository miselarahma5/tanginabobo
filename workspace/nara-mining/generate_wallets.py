#!/usr/bin/env python3
"""
Generate wallet keys for NARA mining
"""

import json
import os
import secrets
import time
from typing import Dict, List

def generate_wallet(wallet_id: str) -> Dict:
    """Generate single wallet data"""
    # Generate random private key (32 bytes hex)
    private_key = secrets.token_hex(32)
    
    # Derive public address (simplified - real implementation would use proper crypto)
    address = f"NARA_{wallet_id}_{secrets.token_hex(8).upper()}"
    
    return {
        "wallet_id": wallet_id,
        "address": address,
        "private_key": private_key,  # ⚠️ KEEP SECRET
        "created_at": str(int(time.time()))
    }

def generate_wallets(count: int = 20, filename: str = "wallets.json"):
    """Generate multiple wallets W001-W{count}"""
    wallets = []
    
    print(f"🖤 Generating {count} NARA wallets...")
    
    for i in range(1, count + 1):
        wallet_id = f"W{i:03d}"
        wallet = generate_wallet(wallet_id)
        wallets.append(wallet)
        print(f"  ✓ {wallet_id}: {wallet['address'][:20]}...")
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(wallets, f, indent=2)
    
    print(f"\n⚠️  WALLETS SAVED TO: {filename}")
    print("⚠️  KEEP THIS FILE SECURE - IT CONTAINS PRIVATE KEYS!")
    print(f"\n✅ Generated {count} wallets ready for mining")
    
    return wallets

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate NARA wallets")
    parser.add_argument("-c", "--count", type=int, default=20, help="Number of wallets")
    parser.add_argument("-o", "--output", default="wallets.json", help="Output file")
    
    args = parser.parse_args()
    
    generate_wallets(args.count, args.output)
