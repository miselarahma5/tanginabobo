#!/bin/bash
# Batch transfer 0.2 NARA to wallets W003-W030

WALLET_DIR="$HOME/.nara-wallets"
FROM_WALLET="$WALLET_DIR/W001.json"
AMOUNT=0.2

echo "🖤 Batch Transfer: 0.2 NARA to W003-W030"
echo "======================================="
echo "From: W001"
echo "Amount: $AMOUNT NARA per wallet"
echo "Total: 28 wallets = 5.6 NARA"
echo "======================================="
echo ""

# Get W001 address for confirmation
FROM_ADDR=$(npx naracli@latest -w "$FROM_WALLET" address 2>&1 | tail -1 | tr -d ' ')
echo "From address: $FROM_ADDR"
echo ""

SUCCESS=0
FAILED=0

for i in $(seq 3 30); do
    WALLET_NUM=$(printf "%03d" $i)
    TO_WALLET="$WALLET_DIR/W$WALLET_NUM.json"
    
    if [ ! -f "$TO_WALLET" ]; then
        echo "⚠️  W$WALLET_NUM: Wallet not found, skipping"
        continue
    fi
    
    # Get recipient address
    TO_ADDR=$(npx naracli@latest -w "$TO_WALLET" address 2>&1 | tail -1 | tr -d ' ')
    
    echo -n "Transfer to W$WALLET_NUM ($TO_ADDR): "
    
    # Transfer
    RESULT=$(npx naracli@latest -w "$FROM_WALLET" transfer "$TO_ADDR" "$AMOUNT" 2>&1)
    
    if echo "$RESULT" | grep -q "successful"; then
        echo "✅ SUCCESS"
        ((SUCCESS++))
    else
        echo "❌ FAILED"
        echo "   Error: $(echo "$RESULT" | grep -E "Error|error" | head -1)"
        ((FAILED++))
    fi
    
    # Small delay to avoid rate limiting
    sleep 2
done

echo ""
echo "======================================="
echo "Transfer Complete!"
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
echo "======================================="

# Check W001 remaining balance
echo ""
echo "Checking W001 remaining balance:"
npx naracli@latest -w "$FROM_WALLET" balance 2>&1 | grep "Balance:"
