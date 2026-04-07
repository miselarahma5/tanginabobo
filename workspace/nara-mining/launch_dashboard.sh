#!/bin/bash
# Launch NARA Dashboard - Local + Public Access

cd "$(dirname "$0")"

echo "🖤 NARA Mining Dashboard Launcher"
echo "================================"
echo ""

# Kill old servers
pkill -f "dashboard_server.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null
sleep 1

echo "1️⃣  Starting local dashboard server..."
echo "   Port: 8080 (all interfaces)"
echo ""

# Start dashboard server in background
python3 dashboard_server.py > dashboard_server.log 2>&1 &
SERVER_PID=$!
sleep 2

# Check if running
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Local server running (PID: $SERVER_PID)"
    echo ""
    echo "📊 LOCAL ACCESS:"
    echo "   http://localhost:8080"
    echo "   http://127.0.0.1:8080"
    
    # Get IP
    IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [ -n "$IP" ]; then
        echo "   http://$IP:8080"
    fi
    echo ""
else
    echo "❌ Server failed to start"
    exit 1
fi

# Create/update stats file if not exists
if [ ! -f "nara_mining_stats.json" ]; then
    cat > nara_mining_stats.json << 'EOF'
{
  "total_wallets": 30,
  "active_wallets": ["W001", "W002", "W003", "W004", "W005"],
  "rotation_count": 0,
  "start_time": "2026-04-07T10:30:00",
  "submissions": {},
  "status": "Ready to mine"
}
EOF
fi

# Create symlink for logs
if ls nara_multi_*.log 1> /dev/null 2>&1; then
    LATEST=$(ls -t nara_multi_*.log | head -1)
    ln -sf "$LATEST" nara_multi_latest.log 2>/dev/null
fi

echo "═══════════════════════════════════════════════════════"
echo ""
read -p "🌐 Start public tunnel too? (y/n): " start_tunnel

if [ "$start_tunnel" = "y" ] || [ "$start_tunnel" = "Y" ]; then
    echo ""
    echo "2️⃣  Starting Cloudflare tunnel..."
    bash start_tunnel.sh
else
    echo ""
    echo "✅ Dashboard running locally on port 8080"
    echo ""
    echo "To stop: pkill -f dashboard_server.py"
    echo ""
    # Keep script running
    echo "Press Ctrl+C to stop..."
    wait $SERVER_PID
fi
