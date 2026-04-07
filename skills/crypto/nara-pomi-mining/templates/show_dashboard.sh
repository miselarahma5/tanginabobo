#!/bin/bash
# NARA Mining Dashboard - CLI Text Mode (No browser/server needed)

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
    echo "⏸️  Dashboard Server: NOT RUNNING"
fi

# Show access URLs
echo "📊 Access URLs:"
echo "   Local:  http://localhost:8080"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -n "$IP" ]; then
    echo "   LAN:    http://$IP:8080"
fi
echo ""

# Load and display stats
if [ -f "nara_mining_stats.json" ]; then
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
    
    print("📈 Current Stats:")
    print("─────────────────")
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
        sorted_bal = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:5]
        for wallet, bal in sorted_bal:
            if bal > 0:
                print(f"   {wallet}: \033[33m{bal:.4f} NARA\033[0m")
        print("")
    
    # Show top performers
    print("🖤 Top Wallets (Submissions):")
    print("─────────────────")
    
    sorted_wallets = sorted(subs.items(), key=lambda x: x[1], reverse=True)[:8]
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

# Show recent activity
LATEST_LOG=$(ls -t nara_multi_*.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "📜 Recent Activity ($LATEST_LOG):"
    echo "──────────────────────────────────"
    tail -10 "$LATEST_LOG" 2>/dev/null | while read line; do
        if echo "$line" | grep -q "✅\|Submitted"; then
            echo "   \033[32m✓ $line\033[0m"
        elif echo "$line" | grep -q "❌\|Failed\|Error"; then
            echo "   \033[31m✗ $line\033[0m"
        elif echo "$line" | grep -q "⏭️\|Skip"; then
            echo "   \033[33m⊘ $line\033[0m"
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
echo "  launch_dashboard.sh  - Web dashboard"
echo "  status.sh            - System status"
echo ""
