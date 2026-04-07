#!/bin/bash
# Start NARA Multi-Wallet Mining (5 active, rotate every 5min)

cd "$(dirname "$0")"

echo "🖤 NARA Multi-Wallet Mining"
echo "==========================="
echo "Wallets: 30 (W001-W030)"
echo "Active: 5 miners"
echo "Rotation: every 5 minutes"
echo "Mode: Math-Only (skip trivia)"
echo "==========================="
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with unbuffered output for real-time logging
python3 -u run_multi_wallet.py 2>&1 | tee nara_multi_$(date +%Y%m%d_%H%M).log
