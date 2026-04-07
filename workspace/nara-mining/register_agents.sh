#!/bin/bash
# Register all 30 wallets as NARA agents

WALLET_DIR="$HOME/.nara-wallets"
LOG_DIR="$HOME/.nara-mnemonics"

for i in $(seq 1 30); do
    WALLET_NUM=$(printf "%03d" $i)
    WALLET_FILE="$WALLET_DIR/W$WALLET_NUM.json"
    AGENT_ID="hitagi-agent-$WALLET_NUM"
    LOG_FILE="$LOG_DIR/W$WALLET_NUM-register.log"
    
    if [ -f "$WALLET_FILE" ]; then
        echo "Registering W$WALLET_NUM..."
        
        # Check if already registered
        CHECK=$(npx naracli@latest -w "$WALLET_FILE" agent get 2>&1)
        if echo "$CHECK" | grep -q "Agent ID"; then
            echo "  ✓ W$WALLET_NUM already registered"
            continue
        fi
        
        # Register agent
        OUTPUT=$(npx naracli@latest -w "$WALLET_FILE" agent register "$AGENT_ID" --relay 2>&1)
        echo "$OUTPUT" > "$LOG_FILE"
        
        if echo "$OUTPUT" | grep -q "registered"; then
            echo "  ✓ W$WALLET_NUM registered as $AGENT_ID"
        else
            echo "  ✗ W$WALLET_NUM failed: $(echo "$OUTPUT" | tail -1)"
        fi
        
        sleep 2
    fi
done

echo ""
echo "Done! Check $LOG_DIR for details"
