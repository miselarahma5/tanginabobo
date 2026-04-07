#!/bin/bash
# Quick dashboard view via CLI

cd "$(dirname "$0")"

echo ""
echo "🖤 NARA MINING DASHBOARD (Text Mode)"
echo "════════════════════════════════════"
echo ""

# Check server status
DASH_PID=$(pgrep -f "dashboard_server.py" | head -1)
if [ -n "$DASH_PID" ]; then
    echo "✅ Dashboard Server: RUNNING (PID $DASH_PID)"
else
    echo "❌ Dashboard Server: STOPPED"
    echo "   Run: python3 dashboard_server.py &"
    echo ""
fi

# Show access URLs
echo "📊 Access URLs:"
echo "   Local:  http://localhost:8080"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -n "$IP" ]; then
    echo "   LAN:    http://$IP:8080"
fi
echo ""

# Load stats
if [ -f "nara_mining_stats.json" ]; then
    echo "📈 Current Stats:"
    echo "─────────────────"
    
    # Parse JSON with Python
    python3 << 'PYEOF'
import json
try:
    with open('nara_mining_stats.json') as f:
        data = json.load(f)
    
    total = data.get('total_wallets', 0)
    active = len(data.get('active_wallets', []))
    rot = data.get('rotation_count', 0)
    subs = data.get('submissions', {})
    total_subs = sum(subs.values())
    balance = data.get('total_balance', 0)
    
    print(f"   Total Wallets: {total}")
    print(f"   Active Now:    {active}")
    print(f"   Rotations:     {rot}")
    print(f"   Submissions:   {total_subs}")
    print(f"   Total Balance: \033[1;33m{balance:.4f} NARA\033[0m")
    print(f"   Est. Earnings: \033[1;36m{total_subs * 0.33:.2f} NARA\033[0m")
    print("")
    
    # Show top balances
    balances = data.get('wallet_balances', {})
    if balances:
        print("💰 Top Balances:")
        print("─────────────────")
        sorted_bal = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:3]
        for wallet, bal in sorted_bal:
            if bal > 0:
                print(f"   {wallet}: \033[33m{bal:.4f} NARA\033[0m")
        print("")
    
    print("🖤 Top Wallets:")
    print("─────────────────")
    
    sorted_wallets = sorted(subs.items(), key=lambda x: x[1], reverse=True)[:5]
    max_count = max(subs.values()) if subs else 1
    
    for wallet, count in sorted_wallets:
        bar_len = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "█" * bar_len
        bal = balances.get(wallet, 0)
        bal_str = f"({bal:.2f}N)" if bal > 0 else ""
        print(f"   {wallet:8} {count:3} {bar} \033[33m{bal_str}\033[0m")
        
    print("")
except Exception as e:
    print(f"   Error reading stats: {e}")
PYEOF
    
    echo ""
fi

# Recent activity
LATEST_LOG=$(ls -t nara_multi_*.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "📜 Recent Activity ($LATEST_LOG):"
    echo "──────────────────────────────────"
    tail -8 "$LATEST_LOG" 2>/dev/null | while read line; do
        # Colorize output
        if echo "$line" | grep -q "✅\|Submitted"; then
            echo "   ✓ $line"
        elif echo "$line" | grep -q "❌\|Failed\|Error"; then
            echo "   ✗ $line"
        elif echo "$line" | grep -q "⏭️\|Skip"; then
            echo "   ⊘ $line"
        else
            echo "   $line"
        fi
    done
else
    echo "📜 No mining log yet (mining not started)"
fi

echo ""
echo "════════════════════════════════════"
echo "Commands:"
echo "  start_multi.sh       - Start mining"
echo "  launch_dashboard.sh  - Open dashboard"
echo "  start_tunnel.sh      - Public URL"
echo ""
