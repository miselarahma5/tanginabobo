#!/bin/bash
# Create 30 NARA wallets - FIXED version

WALLET_DIR="$HOME/.nara-wallets"
MNEMONIC_DIR="$HOME/.nara-mnemonics"

mkdir -p "$WALLET_DIR" "$MNEMONIC_DIR"
chmod 700 "$WALLET_DIR" "$MNEMONIC_DIR"

echo "🖤 Creating 30 NARA Wallets..."
echo "⚠️  CRITICAL: Save each mnemonic immediately!"
echo ""

# Move first wallet if exists
if [ -f "$HOME/.config/nara/id.json" ]; then
    mv "$HOME/.config/nara/id.json" "$WALLET_DIR/W001.json"
    echo "✓ Moved existing wallet to W001"
fi

for i in {1..30}; do
    wallet_id=$(printf "W%03d" $i)
    wallet_file="$WALLET_DIR/${wallet_id}.json"
    
    # Skip if already exists
    if [ -f "$wallet_file" ] && [ $i -eq 1 ]; then
        echo "[$i/30] ${wallet_id} already exists (moved)"
        continue
    elif [ -f "$wallet_file" ]; then
        echo "[$i/30] ${wallet_id} already exists, skipping"
        continue
    fi
    
    echo "[$i/30] Creating ${wallet_id}..."
    echo "========================================" >> "$MNEMONIC_DIR/${wallet_id}.log"
    echo "Wallet: ${wallet_id}" >> "$MNEMONIC_DIR/${wallet_id}.log"
    echo "Created: $(date)" >> "$MNEMONIC_DIR/${wallet_id}.log"
    echo "========================================" >> "$MNEMONIC_DIR/${wallet_id}.log"
    
    # Create wallet with -w flag
    npx naracli@latest wallet create -w "$wallet_file" 2>&1 | tee -a "$MNEMONIC_DIR/${wallet_id}.log"
    
    # Check success
    if [ -f "$wallet_file" ]; then
        address=$(npx naracli@latest address -w "$wallet_file" 2>/dev/null)
        echo "  ✅ Created: ${address:0:25}..."
        
        # Extract mnemonic from log
        echo "" >> "$MNEMONIC_DIR/${wallet_id}.log"
        echo "🔒 MNEMONIC (SAVE OFFLINE):" >> "$MNEMONIC_DIR/${wallet_id}.log"
        grep -A 12 "Mnemonic phrase" "$MNEMONIC_DIR/${wallet_id}.log" | tail -13 >> "$MNEMONIC_DIR/${wallet_id}-mnemonic.txt"
    else
        echo "  ❌ Failed to create ${wallet_id}"
    fi
    
    sleep 0.5
done

echo ""
echo "========================================"
echo "✅ Wallet creation complete!"
echo "========================================"
echo ""
echo "🔒 CRITICAL - BACKUP MNEMONICS NOW:"
echo ""
echo "1. View all mnemonics:"
echo "   cat ~/.nara-mnemonics/*-mnemonic.txt"
echo ""
echo "2. Save OFFLINE (paper/encrypted drive):"
echo "   cat ~/.nara-mnemonics/*-mnemonic.txt > ~/nara-mnemonics-backup.txt"
echo "   # Print dan simpan di tempat fisik aman!"
echo ""
echo "3. Verify wallets:"
echo "   ls -la ~/.nara-wallets/"
echo ""
echo "⚠️  WARNINGS:"
echo "   - Mnemonics = MASTER KEY (lose = lose funds)"
echo "   - JANGAN share dengan SIAPAPUN"
echo "   - JANGAN upload ke cloud/GitHub"
echo "========================================"
