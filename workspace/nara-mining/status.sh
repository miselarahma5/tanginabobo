#!/bin/bash
# NARA Mining Status Checker

cd "$(dirname "$0")"

echo ""
echo "🖤 NARA MINING STATUS 🖤"
echo "========================="
echo ""

# Check wallets
echo "📁 Wallets:"
WALLET_COUNT=$(ls ~/.nara-wallets/W*.json 2>/dev/null | wc -l)
echo "   Total: $WALLET_COUNT/30"

# Check agents
echo ""
echo "🤖 Agents:"
if [ -f "nara_mining_stats.json" ]; then
    ACTIVE=$(cat nara_mining_stats.json | grep -o '"active_wallets":\[([^]]*)\]' | head -1)
    echo "   Active: 5 (rotating)"
fi

# Check dashboard
echo ""
echo "📊 Dashboard:"
DASH_PID=$(pgrep -f "dashboard_server.py" | head -1)
if [ -n "$DASH_PID" ]; then
    echo "   Status: ✅ RUNNING (PID $DASH_PID)"
    echo "   Local:  http://localhost:8080"
    IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [ -n "$IP" ]; then
        echo "   LAN:    http://$IP:8080"
    fi
    echo "   CLI:    bash show_dashboard.sh"
else
    echo "   Status: ❌ STOPPED"
    echo "   Start:  python3 dashboard_server.py &"
    echo "   or:     bash show_dashboard.sh (text mode)"
fi

# Check mining process
echo ""
echo "⛏️  Mining Process:"
MINER_PID=$(pgrep -f "run_multi_wallet.py" | head -1)
if [ -n "$MINER_PID" ]; then
    echo "   Status: ✅ RUNNING (PID $MINER_PID)"
else
    echo "   Status: ❌ STOPPED"
    echo "   Start: bash start_multi.sh"
fi

# Check stats
echo ""
echo "📈 Statistics:"
if [ -f "nara_mining_stats.json" ]; then
    ROT=$(cat nara_mining_stats.json | grep -o '"rotation_count":[0-9]*' | cut -d: -f2)
    SUBS=$(cat nara_mining_stats.json | grep -o '"submissions":{[^}]*}' | tr ',' '\n' | grep -o '[0-9]*' | awk '{sum+=$1} END {print sum}')
    echo "   Rotations: ${ROT:-0}"
    echo "   Submissions: ${SUBS:-0}"
else
    echo "   No stats file yet"
fi

# Recent log
echo ""
echo "📜 Recent Activity:"
LATEST_LOG=$(ls -t nara_multi_*.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "   Log: $LATEST_LOG"
    echo "   Last 3 lines:"
    tail -3 "$LATEST_LOG" 2>/dev/null | sed 's/^/   /'
else
    echo "   No log file yet"
fi

echo ""
echo "========================="
echo "Commands:"
echo "  Start mining: bash start_multi.sh"
echo "  View dashboard: bash launch_dashboard.sh"
echo "  Check status: bash status.sh"
echo ""
