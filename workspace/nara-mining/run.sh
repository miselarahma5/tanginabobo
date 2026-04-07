#!/bin/bash
# NARA PoMI Mining Bot Runner

cd "$(dirname "$0")"

echo "🖤 NARA PoMI Mining Bot"
echo "======================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install from https://nodejs.org/"
    exit 1
fi

# Check naracli
if ! command -v naracli &> /dev/null; then
    echo "❌ naracli not found. Run: npm install -g naracli"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Check wallet
WALLET=$(npx naracli address 2>&1)
if echo "$WALLET" | grep -q "Error\|No such file"; then
    echo "❌ No wallet found!"
    echo "   Create one: npx naracli wallet create"
    exit 1
fi

echo "✓ Wallet: ${WALLET:0:20}..."

# Check agent
AGENT=$(npx naracli agent get --json 2>&1)
if echo "$AGENT" | grep -q "Error\|null"; then
    echo "⚠️  No agent registered"
    echo "   Register: npx naracli agent register <id> --relay"
fi

# Check balance
BALANCE=$(npx naracli balance --json 2>&1 | grep -o '"balance":[0-9.]*' | cut -d: -f2)
echo "✓ Balance: ${BALANCE:-0} NARA"

if (( $(echo "${BALANCE:-0} < 0.1" | bc -l) )); then
    echo "   Will use relay (gasless) mining"
fi

echo ""
echo "Starting miner..."
echo "Press Ctrl+C to stop"
echo ""

# Run Python miner
python3 nara_miner.py "$@"
