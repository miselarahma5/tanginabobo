#!/bin/bash
# Create 30 NARA wallets with logging

WALLET_DIR="$HOME/.nara-wallets"
MNEMONIC_DIR="$HOME/.nara-mnemonics"

mkdir -p "$WALLET_DIR" "$MNEMONIC_DIR"
chmod 700 "$WALLET_DIR" "$MNEMONIC_DIR"

echo "🖤 Creating 30 NARA Wallets..."
echo "⚠️  IMPORTANT: Mnemonics will be shown ONCE"
echo "   Save them immediately!"
echo ""

for i in {1..30}; do
    wallet_id=$(printf "W%03d" $i)
    wallet_file="$WALLET_DIR/${wallet_id}.json"
    log_file="$MNEMONIC_DIR/${wallet_id}-creation.log"
    
    echo "[$i/30] Creating ${wallet_id}..."
    
    # Create wallet with output captured
    NARA_WALLET="$wallet_file" npx naracli@latest wallet create 2>&1 | tee "$log_file"
    
    # Extract address
    address=$(NARA_WALLET="$wallet_file" npx naracli@latest address 2>/dev/null)
    echo "  Address: ${address:0:20}..."
    
    # Small delay
    sleep 0.5
done

echo ""
echo "✅ 30 wallets created!"
echo ""
echo "🔒 NEXT - CRITICAL:"
echo "1. Extract mnemonics from logs:"
echo "   cat ~/.nara-mnemonics/*-creation.log"
echo ""
echo "2. Save mnemonics OFFLINE (write on paper):"
echo "   cat ~/.nara-mnemonics/*-creation.log > ~/nara-backup.txt"
echo "   # Then print and store in safe/lockbox"
echo ""
echo "3. Verify wallets:"
echo "   ls ~/.nara-wallets/"
