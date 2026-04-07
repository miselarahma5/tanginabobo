#!/bin/bash
# NARA Batch Agent Registration
# Register all 30 wallets as agents

WALLET_DIR="$HOME/.nara-wallets"
LOG_DIR="$HOME/.nara-mnemonics"

for i in $(seq 1 30); do
    WALLET_NUM=$(printf "%03d" $i)
    WALLET_FILE="$WALLET_DIR/W$WALLET_NUM.json"
    AGENT_ID="hitagi-agent-$WALLET_NUM"  # MUST BE LOWERCASE!
    LOG_FILE="$LOG_DIR/W$WALLET_NUM-register.log"
    
    if [ -f "$WALLET_FILE" ]; then
        echo -n "Registering W$WALLET_NUM... "
        
        # Check if already registered
        CHECK=$(npx naracli@latest -w "$WALLET_FILE" agent get 2>&1)
        if echo "$CHECK" | grep -q "Agent ID"; then
            echo "ALREADY REGISTERED"
            continue
        fi
        
        # Register agent with --relay (gasless for 0 balance wallets)
        OUTPUT=$(npx naracli@latest -w "$WALLET_FILE" agent register "$AGENT_ID" --relay 2>&1)
        echo "$OUTPUT" > "$LOG_FILE"
        
        if echo "$OUTPUT" | grep -q "registered"; then
            echo "✓ SUCCESS"
        else
            ERROR=$(echo "$OUTPUT" | grep -E "Error|error" | tail -1)
            echo "✗ FAILED: $ERROR"
        fi
        
        sleep 2  # Rate limiting protection
    fi
done

echo ""
echo "Done! Check $LOG_DIR for error details"
echo "Verify with: npx naracli -w ~/.nara-wallets/W001.json agent get"
