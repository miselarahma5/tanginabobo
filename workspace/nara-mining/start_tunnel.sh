#!/bin/bash
# Start Cloudflare tunnel for dashboard access

cd "$(dirname "$0")"

echo "🖤 NARA Dashboard Tunnel"
echo "======================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️  cloudflared not found. Installing..."
    
    # Install cloudflared
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -sLO https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
        chmod +x cloudflared-linux-amd64
        sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared 2>/dev/null || mv cloudflared-linux-amd64 cloudflared
        echo "✓ cloudflared installed"
    else
        echo "❌ Please install cloudflared manually:"
        echo "   https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
        exit 1
    fi
fi

echo "🚀 Starting tunnel..."
echo "   Local server: http://localhost:8080"
echo ""
echo "🌐 Public URL will appear below (wait 10-15 seconds):"
echo "═══════════════════════════════════════════════════════"

# Start tunnel
cloudflared tunnel --url http://localhost:8080 2>&1 | while read line; do
    if echo "$line" | grep -q "https://.*trycloudflare.com"; then
        URL=$(echo "$line" | grep -o "https://[^ ]*trycloudflare.com[^ ]*")
        echo ""
        echo "✅ PUBLIC DASHBOARD URL:"
        echo "   $URL"
        echo ""
        echo "   Share this URL to access dashboard from anywhere!"
        echo "═══════════════════════════════════════════════════════"
    fi
done
