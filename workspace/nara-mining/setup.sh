#!/bin/bash
# NARA PoMI Mining Bot Setup

echo "🖤 NARA PoMI Mining Bot Setup"
echo "=============================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js >= 18"
    echo "   https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version too old: $(node --version)"
    echo "   Please upgrade to Node.js >= 18"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi

echo "✓ npm version: $(npm --version)"

# Install naracli
echo ""
echo "📦 Installing NARA CLI..."
echo "   npm install -g naracli"
echo ""
echo "⚠️  SECURITY NOTICE:"
echo "   This installs code from npm registry."
echo "   Package: https://www.npmjs.com/package/naracli"
echo "   Source:  https://github.com/nara-chain/nara-cli"
echo ""
read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 1
fi

npm install -g naracli

if [ $? -ne 0 ]; then
    echo "❌ Failed to install naracli"
    exit 1
fi

echo "✓ naracli installed"

# Check wallet
echo ""
echo "🔑 Checking wallet..."
WALLET=$(npx naracli address 2>&1)

if echo "$WALLET" | grep -q "Error\|No such file"; then
    echo "⚠️  No wallet found"
    echo "   Create one with: npx naracli wallet create"
    echo ""
    read -p "Create wallet now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npx naracli wallet create
    else
        echo "Please create wallet manually before mining"
    fi
else
    echo "✓ Wallet found: ${WALLET:0:20}..."
fi

# Check agent
echo ""
echo "🤖 Checking agent registration..."
AGENT_INFO=$(npx naracli agent get --json 2>&1)

if echo "$AGENT_INFO" | grep -q "Error\|null\|Not found"; then
    echo "⚠️  No agent registered"
    echo ""
    echo "   To register (FREE with 8+ char ID):"
    echo "   npx naracli agent register <your-agent-id> --relay"
    echo ""
    echo "   Example: npx naracli agent register hermes-miner-001 --relay"
else
    echo "✓ Agent registered"
    echo "$AGENT_INFO" | head -20
fi

# Check balance
echo ""
echo "💰 Checking balance..."
BALANCE=$(npx naracli balance --json 2>&1 | grep -o '"balance":[0-9.]*' | cut -d: -f2)

if [ -n "$BALANCE" ]; then
    echo "✓ Balance: $BALANCE NARA"
    
    if (( $(echo "$BALANCE < 0.1" | bc -l) )); then
        echo "   Balance low - will use relay for gasless mining"
    fi
else
    echo "⚠️  Could not check balance"
fi

echo ""
echo "=============================="
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Register agent: npx naracli agent register <id> --relay"
echo "2. Bind Twitter: npx naracli agent bind-twitter --relay"
echo "3. Start mining: python3 nara_miner.py"
echo ""
echo "🖤 Happy mining!"
