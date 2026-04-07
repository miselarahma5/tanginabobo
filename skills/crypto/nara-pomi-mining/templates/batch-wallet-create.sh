#!/bin/bash
# NARA Batch Wallet Creator
# ⚠️ CRITICAL: Handles naracli id.json conflict for batch creation

WALLET_NUM=$1
WALLET_DIR="$HOME/.nara-wallets"
MNEMONIC_DIR="$HOME/.nara-mnemonics"
DEFAULT_WALLET="$HOME/.config/nara/id.json"

WALLET_FILE="$WALLET_DIR/W$(printf "%03d" $WALLET_NUM).json"
LOG_FILE="$MNEMONIC_DIR/W$(printf "%03d" $WALLET_NUM)-creation.log"
MNEMONIC_FILE="$MNEMONIC_DIR/W$(printf "%03d" $WALLET_NUM)-mnemonic.txt"

# MUST remove default wallet first - naracli always creates at ~/.config/nara/id.json
rm -f "$DEFAULT_WALLET" 2>/dev/null

# Create wallet (saves to default path)
OUTPUT=$(npx naracli@latest wallet create 2>&1)

# Save full output
mkdir -p "$WALLET_DIR" "$MNEMONIC_DIR"
echo "$OUTPUT" > "$LOG_FILE"

# Check if created successfully
if [ -f "$DEFAULT_WALLET" ]; then
    # Move to custom location
    mv "$DEFAULT_WALLET" "$WALLET_FILE"
    
    # Extract mnemonic (12 words after "Mnemonic phrase")
    MNEMONIC=$(echo "$OUTPUT" | grep -A 1 "Mnemonic phrase" | tail -1 | tr -d ' ')
    if [ -n "$MNEMONIC" ]; then
        echo "W$(printf "%03d" $WALLET_NUM): $MNEMONIC" > "$MNEMONIC_FILE"
    fi
    
    # Extract address
    ADDRESS=$(echo "$OUTPUT" | grep "Public Key:" | cut -d: -f2 | tr -d ' ')
    
    echo "✓ W$(printf "%03d" $WALLET_NUM) created - $ADDRESS"
    exit 0
else
    echo "✗ W$(printf "%03d" $WALLET_NUM) failed"
    exit 1
fi
