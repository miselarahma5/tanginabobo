---
name: deploy-nodejs-bot
description: Deploy Node.js bots/services with external web access via cloudflared tunnel
triggers:
  - deploy bot
  - run trading bot
  - expose localhost
  - cloudflared tunnel
---

# Deploy Node.js Bot with External Access

Pattern for deploying Node.js bots/services with external web access via cloudflared tunnel.

## Steps

### 1. Clone Repository
```bash
git clone https://x-access-token:${TOKEN}@github.com/user/repo.git
```

### 2. Install Dependencies
```bash
cd repo-directory && npm install
```

### 3. Setup Environment
```bash
cp .env.example .env
# Edit .env with required values (API keys, private keys, wallet addresses, mode)
```

### 4. Run as Background Process
Use `background=true` for long-running services.

### 5. Create External Tunnel (cloudflared)
```bash
# Install:
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared && mv cloudflared /usr/local/bin/

# Create tunnel:
nohup cloudflared tunnel --url http://localhost:PORT > /tmp/tunnel.log 2>&1 &
sleep 5 && cat /tmp/tunnel.log | grep "trycloudflare"
```

### 6. Verify Bot Running
```bash
curl -s http://localhost:PORT/api/health
```

## Pitfalls

- Tunnel URLs are temporary - changes on restart
- Check wallet balances match trade size before LIVE mode
- Use background=true for long-running services
- Private keys in .env are sensitive - never commit to git

## Quick Reference

| Task | Method |
|------|--------|
| Start bot | terminal with `background=true` |
| Create tunnel | `cloudflared tunnel --url http://localhost:PORT` |
| Health check | `curl http://localhost:PORT/api/health` |
| Kill process | `process(action='kill', session_id='...')` |