# 🖤 NARA Mining Dashboard - Access Guide

## Dashboard Access Methods

### 1. CLI Text Dashboard (Fastest)
```bash
cd /root/.hermes/workspace/nara-mining
bash show_dashboard.sh
```
Shows real-time stats, top wallets, and recent activity in terminal.

### 2. Web Dashboard (Local/LAN)
**Start server:**
```bash
cd /root/.hermes/workspace/nara-mining
python3 dashboard_server.py
```

**Access URLs:**
- Local: http://localhost:8080
- LAN: http://YOUR_SERVER_IP:8080
- Network: http://0.0.0.0:8080

**Or use launcher:**
```bash
bash launch_dashboard.sh
```

### 3. Web Dashboard + Public URL (Cloudflare Tunnel)
**Auto-start everything:**
```bash
cd /root/.hermes/workspace/nara-mining
bash launch_dashboard.sh
# Type 'y' when asked for public tunnel
```

**Or manual tunnel:**
```bash
# 1. Start local server
python3 dashboard_server.py &

# 2. Start tunnel
bash start_tunnel.sh

# 3. Public URL will appear (like https://xxx.trycloudflare.com)
```

## Dashboard Features

### Real-time Stats
- ⛏️  Active miners (5 rotating wallets)
- 📊 Total submissions count
- 🔄 Rotation counter
- 💰 Earnings tracking

### Visual Wallet Grid
- 30 wallet boxes (W001-W030)
- Active wallets highlighted in pink/purple
- Submission count per wallet

### Top Performers
- Bar chart of top 5 wallets
- Submission counts
- Visual progress bars

### Activity Log
- Last 20 mining events
- Color-coded: ✅ Success, ❌ Failed, ⏭️ Skipped

## Files
- `dashboard.html` - Main web interface
- `dashboard_server.py` - HTTP server (port 8080)
- `nara_mining_stats.json` - Stats data (auto-updated)
- `show_dashboard.sh` - CLI text view
- `launch_dashboard.sh` - Interactive launcher
- `start_tunnel.sh` - Cloudflare tunnel

## Auto-Refresh
- Web dashboard: Every 5 seconds
- Stats file: Updated by mining bot
- CLI view: Manual (run again to refresh)

## Troubleshooting

### Port 8080 blocked?
```bash
# Use different port
python3 -m http.server 9000
# Then access http://localhost:9000/dashboard.html
```

### Can't access from outside?
```bash
# Check firewall
sudo ufw allow 8080/tcp  # Ubuntu
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT  # Generic
```

### Stats not updating?
- Mining bot updates `nara_mining_stats.json`
- Web dashboard auto-refreshes every 5s
- Check: `cat nara_mining_stats.json`

## Security Notes

- Dashboard is read-only (no wallet control)
- No private keys or mnemonics exposed
- Safe to share public tunnel URL
- Default: No authentication (add if needed)

## Quick Commands

```bash
# View dashboard (text)
bash show_dashboard.sh

# Start web server
python3 dashboard_server.py &

# Start with tunnel (public URL)
bash launch_dashboard.sh

# Stop everything
pkill -f dashboard_server
pkill -f cloudflared

# Check status
bash status.sh
```

---
🖤 Dashboard refreshes automatically. Watch your mining stats grow!
