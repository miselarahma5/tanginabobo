#!/bin/bash
# Create NARA wallet and save to custom location

WALLET_NUM=$1
WALLET_DIR="$HOME/.nara-wallets"
MNEMONIC_DIR="$HOME/.nara-mnemonics"
DEFAULT_WALLET="$HOME/.config/nara/id.json"

WALLET_FILE="$WALLET_DIR/W$(printf "%03d" $WALLET_NUM).json"
LOG_FILE="$MNEMONIC_DIR/W$(printf "%03d" $WALLET_NUM)-creation.log"
MNEMONIC_FILE="$MNEMONIC_DIR/W$(printf "%03d" $WALLET_NUM)-mnemonic.txt"

# Remove default wallet if exists (prevents conflicts)
rm -f "$DEFAULT_WALLET" 2>/dev/null

# Create wallet
OUTPUT=$(npx naracli@latest wallet create 2>&1)

# Save log
echo "$OUTPUT" > "$LOG_FILE"

# Check if created successfully
if [ -f "$DEFAULT_WALLET" ]; then
    # Move to custom location
    mv "$DEFAULT_WALLET" "$WALLET_FILE"
    
    # Extract mnemonic (critical for backup!)
    MNEMONIC=$(echo "$OUTPUT" | grep -A 1 "Mnemonic phrase" | tail -1 | tr -d ' ')
    if [ -n "$MNEMONIC" ]; then
        echo "W$(printf "%03d" $WALLET_NUM): $MNEMONIC" > "$MNEMONIC_FILE"
    fi
    
    echo "✓ W$(printf "%03d" $WALLET_NUM) created"
    exit 0
else
    echo "✗ W$(printf "%03d" $WALLET_NUM) failed"
    exit 1
fi
