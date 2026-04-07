#!/bin/bash
# NARA Multi-Wallet Mining Bot Runner

cd "$(dirname "$0")"

echo "🖤 NARA Multi-Wallet Mining Bot"
echo "================================"
echo ""

# Check dependencies
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Check wallets exist
WALLET_DIR="$HOME/.nara-wallets"
if [ ! -f "$WALLET_DIR/wallet-index.json" ]; then
    echo "❌ No wallets found!"
    echo "   Generate first: python3 wallet_generator.py"
    exit 1
fi

WALLET_COUNT=$(python3 -c "import json; print(len(json.load(open('$WALLET_DIR/wallet-index.json'))['wallets']))")
echo "✓ Found $WALLET_COUNT wallets"

# Default settings
ACTIVE_MINERS=5
ROTATION=300

echo ""
echo "Settings:"
echo "  Active miners per round: $ACTIVE_MINERS"
echo "  Rotation interval: ${ROTATION}s (5 min)"
echo "  Agent type: hermes"
echo "  Model: k2.5"
echo ""

echo "Starting multi-wallet miner..."
echo "Press Ctrl+C to stop"
echo ""

python3 multi_miner.py \
    --active $ACTIVE_MINERS \
    --rotation $ROTATION \
    --agent-type hermes \
    --model k2.5
