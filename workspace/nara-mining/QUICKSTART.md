# NARA Multi-Wallet Mining - Quick Start

## Setup Complete ✅
- 30 Wallets: W001-W030 created
- 30 Agents: registered
- W001: Twitter bound (20 NARA + 100 credits)

## Start Mining

### 1. Single Wallet (W001 only)
```bash
cd /root/.hermes/workspace/nara-mining
python3 run_miner.py
```

### 2. Multi-Wallet (5 active, rotate every 5min)
```bash
cd /root/.hermes/workspace/nara-mining
bash start_multi.sh
```

## Mining Behavior

**SOLVE (Auto):**
- Math: 5+3, 10-4, 6×7, etc
- Square root patterns
- Money calculations ($X per dozen)
- Multiple choice with numbers (A/B/C/D)

**SKIP (Trivia):**
- History: "Who invented..."
- Science: "What is proton..."
- Sports: "Which award..."
- Arts: "Who composed..."

## Files
- `~/.nara-wallets/` - 30 wallet files
- `~/.nara-mnemonics/` - Backup phrases (IMPORTANT!)
- `nara_multi_*.log` - Mining logs

## Monitor
Watch logs in real-time:
```bash
tail -f nara_multi_*.log
```

## Stats
Check submissions:
```bash
cat ~/.nara-mining-stats.json
```

## Stop
Press `Ctrl+C` to stop gracefully
