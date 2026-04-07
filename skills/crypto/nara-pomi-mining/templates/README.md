# 🖤 NARA PoMI Mining Bot - Multi-Wallet (30 Wallets)

Auto-mining bot untuk **NARA chain** dengan **30 wallet rotation** - menggunakan Proof of Machine Intelligence (PoMI) untuk earn NARA gratis.

## 🚀 What is PoMI?

**Proof of Machine Intelligence (PoMI)** - AI agents solve on-chain quests dengan ZK proofs dan earn NARA rewards.

- ✅ **Free mining** - No gas dengan relay
- ✅ **30 wallets** - Rotate tiap 5 menit
- ✅ **5 active miners** - Mine paralel tiap round
- ✅ **First-come-first-served** - Speed matters!

## ⚠️ SECURITY WARNING - CRITICAL

**30 wallets = 30x private keys**

```
🔴 RISIKO TINGGI:
- 30 private keys tersimpan di 1 mesin
- Kalo file bocor, 30 wallet hilang semua
- Mnemonic adalah MASTER KEY

🟡 MITIGASI:
- Folder: ~/.nara-wallets (permission 0700)
- Mnemonics: ~/.nara-mnemonics (terpisah)
- .gitignore: Auto-prevent upload ke GitHub
- Backup: LAKUKAN MANUAL ke offline storage
```

**🚫 JANGAN PERNAH:**
- Upload wallet folder ke cloud/GitHub
- Share mnemonic/private key siapapun
- Simpan mnemonic di device online tanpa encrypt

## 📦 Prerequisites

```bash
# Node.js >= 18
node --version

# Python 3
python3 --version

# Install NARA CLI
npm install -g naracli
```

## 🛠️ Setup (30 Wallets)

### Step 1: Generate 30 Wallets
```bash
python3 wallet_generator.py
```

Ini akan:
- Generate 30 wallet (W001-W030)
- Simpan di `~/.nara-wallets/`
- Log mnemonic di `~/.nara-mnemonics/`
- Set permission strict (0700)

**⚠️ BACA LOG FILES** dan catet mnemonic di **KERTAS** (offline)!

### Step 2: Register 30 Agents
```bash
python3 wallet_generator.py --register
```

Ini akan register 30 agent ID (W001-miner, W002-miner, dst).

**Optional:** Masukkan referral ID saat prompt untuk dapat diskon.

### Step 3: Bind Twitter (Untuk semua wallet - OPSIONAL tapi RECOMMENDED)

Untuk stake-free mining + 20 NARA bonus per wallet:

```bash
# Manual per wallet (30x)
export NARA_WALLET=~/.nara-wallets/W001.json
npx naracli agent bind-twitter
tweet_url="https://x.com/username/status/1234567890"
npx naracli agent bind-twitter $tweet_url --relay

# Ulangi untuk W002-W030...
```

**Atau** gunakan script helper (buat sendiri untuk batch):
```bash
# Buat script bind_all.sh
for i in {1..30}; do
    wallet=$(printf "~/.nara-wallets/W%03d.json" $i)
    export NARA_WALLET=$wallet
    # ... bind logic
done
```

### Step 4: Check Status
```bash
python3 wallet_generator.py --status
```

## 🎮 Start Mining

### Single Wallet Mode (Testing)
```bash
# Default 1 wallet
python3 nara_miner.py

# Atau spesifik
python3 nara_miner.py --agent-id hermes-miner-001
```

### Multi-Wallet Mode (30 Wallets Rotation) ⭐
```bash
bash run_multi.sh
```

**Atau dengan custom settings:**
```bash
python3 multi_miner.py \
    --active 10 \           # 10 wallet mine paralel
    --rotation 300 \        # Rotate tiap 5 menit
    --agent-type hermes \
    --model k2.5
```

## ⚙️ Configuration

### `miner_config.json`
```json
{
  "agent_type": "hermes",
  "model": "k2.5",
  "active_miners": 5,
  "rotation_interval": 300,
  "relay_threshold": 0.1,
  "min_time_remaining": 10
}
```

### Environment Variables
```bash
export NARA_WALLET=~/.nara-wallets/W001.json  # Pilih wallet
export NARA_RPC_URL=https://mainnet-api.nara.build/
```

## 🎯 Mining Strategy

### Rotation Logic
- **5 active miners** dari 30 wallets
- **Rotate tiap 5 menit** (random selection)
- **Balance check** sebelum submit

### When to Use Relay vs Direct

| Balance | Method | Speed | Gas |
|---------|--------|-------|-----|
| 0 NARA | **MUST --relay** | Slower | Free |
| 0.01-0.1 | `--relay` | Slower | Free |
| >= 0.1 | Direct RPC | **Faster** | Bayar |

### Quest Timing (CRITICAL!)

- ZK proof generation: **2-4 detik**
- **Skip** kalo `timeRemaining <= 10s`
- **Speed matters** - First correct answers get rewards
- 30 wallets = 30 submissions per round = **30x peluang!**

### Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| 6003 | Wrong answer / expired | Next round submit lebih cepat |
| 6007 | Already submitted | Wallet lain di round ini sudah submit |
| 5xx | Relay failure | Retry dengan backup relay |

## 📊 Stats & Monitoring

### Real-time Dashboard
```
==================================================
🖤 NARA PoMI MULTI-MINER (30 Wallets)
==================================================
⏱️  Runtime: 02:34:18
💰 Total Balance: 45.23 NARA (30 wallets)
🎯 Total Submissions: 1,234
✅ Successful: 1,180
❌ Failed: 54
--------------------------------------------------
Active Wallets: W007, W015, W003, W022, W011
Rotation in: 124s
==================================================
```

### Per-Wallet Stats
Tersimpan di memory, bisa export ke file:
```bash
# Tambahkan di multi_miner.py untuk save stats ke JSON
```

## 💎 Earning Calculation (Estimasi)

**Asumsi:**
- 30 wallets
- 5 active per round
- Rotate tiap 5 menit = 6 set/jam = all 30 wallets mine tiap jam
- 24 jam = 24 cycles untuk semua wallet
- Success rate: 80%
- Average reward: 0.5 NARA per correct answer

**Estimasi per wallet:**
- 24 submissions/hari
- 80% success = 19.2 successful
- 19.2 × 0.5 = **~9.6 NARA/hari per wallet**

**Total 30 wallets:**
- 30 × 9.6 = **~288 NARA/hari** (estimasi)

**Plus:**
- Points (bonus multiplier)
- Referral rewards (kalo ada downline)

## 🔒 Backup & Security

### Mnemonic Backup (CRITICAL!)
```bash
# Backup all mnemonics
cp ~/.nara-mnemonics/* ~/secure-backup/

# Print to paper (recommended)
cat ~/.nara-mnemonics/W001-mnemonic.txt
# ... print and store in safe ...
```

### Wallet Files Backup
```bash
# Encrypt sebelum backup
tar -czf - ~/.nara-wallets | gpg -c > wallets-backup.tar.gz.gpg

# Store di offline USB/external drive
```

### Recovery
Kalo mesin rusak/hilang:
```bash
# Restore dari mnemonic
npx naracli wallet import -m "twelve words mnemonic phrase here..."
```

## 🛒 Spending NARA

Buy LLM API credits dengan NARA:
- 1 NARA = 10 CU (Compute Units)
- Claude, GPT-4o, DeepSeek, Gemini
- https://model-api.nara.build/402

## 🤖 AgentX Social Platform (Optional)

```bash
npx naracli skills add agentx
```

Social platform untuk agents - post, comment, discover services.

## 📚 File Structure

```
nara-mining/
├── README.md              # Ini
├── NARA_SKILL.md          # Full NARA documentation
├── wallet_generator.py    # Generate 30 wallets + register agents
├── multi_miner.py         # Multi-wallet mining bot ⭐
├── bind_twitter.py        # Batch Twitter binding
├── nara_miner.py          # Single wallet bot
├── solver.py              # Quest solver examples
├── config/
│   └── miner_config.json  # Settings
└── scripts/
    ├── run.sh            # Single wallet runner
    ├── run_multi.sh      # Multi-wallet runner ⭐
    ├── setup.sh          # Initial setup
    └── check_security.sh # Verify permissions
```

## 🔗 Resources

- Homepage: https://nara.build
- CLI Source: https://github.com/nara-chain/nara-cli
- NPM Package: https://www.npmjs.com/package/naracli
- Explorer: https://explorer.nara.build/
- Telegram: https://t.me/narabuild
- Discord: https://discord.gg/aeNMBjkWsh

## ⚠️ Troubleshooting

### "No wallets found"
```bash
# Generate dulu
python3 wallet_generator.py
```

### "Agent not registered"
```bash
# Register semua
python3 wallet_generator.py --register
```

### "Relay error 6003"
Salah jawaban atau expired. Quest berbeda tiap round, jadi solver harus adaptif.

### "Balance 0 for all wallets"
Normal untuk wallet baru. Mine pakai relay dulu sampai dapet reward.

### "Too many requests"
NARA ada rate limit. Multi-miner udah include delay antar wallet.

## 🎓 Advanced: Custom Solver

Edit `solver.py` untuk implement logic solve quest:

```python
def solve(question: str) -> str:
    # Contoh: Math solver
    if "+" in question or "*" in question:
        return str(eval(question))
    
    # Contoh: Trivia solver (pake API)
    if "capital" in question.lower():
        return query_knowledge_base(question)
    
    # ... implement more solvers
    
    return "placeholder_answer"  # Will fail
```

## 📜 License

MIT - Use at your own risk. Not responsible for lost funds.

---

🚀 **Mine NARA 24/7 with 30 wallets!** 🖤

Keep grinding, stay safe! ✧
