---
name: auto-github-backup
description: Setup automated daily COMPLETE backup ke GitHub repo dengan cronjob - include memories, SOUL.md, skills, cron-output, workspace, config
tags: [backup, github, cronjob, automation, hermes, complete-backup]
---

# Auto GitHub Backup - COMPLETE Edition

Setup automated daily backup lengkap ke GitHub repo dengan cronjob. **Versi ini include SEMUA data penting** termasuk memories (user data) dan SOUL.md (personality).

## Perbedaan dari Backup Biasa

| Data | Backup Biasa | Complete Backup |
|------|--------------|-----------------|
| skills/ | ✓ | ✓ (with rsync --delete) |
| cron-output/ | ✓ | ✓ |
| workspace/ | ✓ | ✓ |
| **memories/** (user profile) | ✗ | **✓** |
| **SOUL.md** (personality) | ✗ | **✓** |
| **config.yaml** | ✗ | **✓** |
| **channel_directory.json** | ✗ | **✓** |

## Langkah-langkah

### 1. Siapkan folder backup
```bash
mkdir -p ~/backup-hermes && cd ~/backup-hermes
git init
git branch -m main
```

### 2. Buat file .token (WAJIB - jangan hardcode!)
```bash
echo "ghp_XXXXXXXXXXXXXXXXXXXXXXXX" > ~/backup-hermes/.token
```
Token harus punya scope `repo`. Jangan pernah commit token ke GitHub!

### 3. Buat .gitignore lengkap
```
# Jangan backup file ini ke GitHub
.token
.env
*.log
backup.log
last_backup.txt

# Jangan backup sensitive data
memories/*.lock
sessions/
auth.json
checkpoints/
state.db*
```

### 4. Buat backup-complete.sh

```bash
#!/bin/bash

# Complete Hermes Backup Bot
# Backup SEMUA data penting: memories, SOUL, skills, cron, workspace, config

BACKUP_DIR=~/backup-hermes
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="$BACKUP_DIR/backup.log"

# Token dari file terpisah (jangan hardcode!)
if [ -f "$BACKUP_DIR/.token" ]; then
    TOKEN=$(cat "$BACKUP_DIR/.token" 2>/dev/null | tr -d '\n')
else
    echo "[ERROR] Token file tidak ditemukan: $BACKUP_DIR/.token"
    exit 1
fi

cd "$BACKUP_DIR" || exit 1

echo "========================================" >> "$LOG_FILE"
echo "Backup dimulai: $DATE" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. BACKUP MEMORY (penting! ada data user)
echo "[+] Backup memories/..." | tee -a "$LOG_FILE"
mkdir -p memories
cp -r ~/.hermes/memories/* memories/ 2>/dev/null && echo "  ✓ memories OK" | tee -a "$LOG_FILE"

# 2. BACKUP SOUL.md (personality agent)
echo "[+] Backup SOUL.md..." | tee -a "$LOG_FILE"
cp ~/.hermes/SOUL.md . 2>/dev/null && echo "  ✓ SOUL.md OK" | tee -a "$LOG_FILE"

# 3. BACKUP SKILLS (gunakan rsync untuk handle deletions)
echo "[+] Backup skills/..." | tee -a "$LOG_FILE"
mkdir -p skills
rsync -av --delete ~/.hermes/skills/ skills/ 2>/dev/null && echo "  ✓ skills OK" | tee -a "$LOG_FILE"

# 4. BACKUP CRON OUTPUT
echo "[+] Backup cron-output/..." | tee -a "$LOG_FILE"
mkdir -p cron-output
cp -r ~/.hermes/cron/output/* cron-output/ 2>/dev/null && echo "  ✓ cron-output OK" | tee -a "$LOG_FILE"

# 5. BACKUP WORKSPACE
echo "[+] Backup workspace/..." | tee -a "$LOG_FILE"
mkdir -p workspace
cp -r ~/.hermes/workspace/* workspace/ 2>/dev/null && echo "  ✓ workspace OK" | tee -a "$LOG_FILE"

# 6. BACKUP CONFIG
echo "[+] Backup config.yaml..." | tee -a "$LOG_FILE"
cp ~/.hermes/config.yaml . 2>/dev/null && echo "  ✓ config.yaml OK" | tee -a "$LOG_FILE"

# 7. BACKUP CHANNEL DIRECTORY (gateway info)
echo "[+] Backup channel_directory.json..." | tee -a "$LOG_FILE"
cp ~/.hermes/channel_directory.json . 2>/dev/null && echo "  ✓ channel_directory OK" | tee -a "$LOG_FILE"

# Git operations
echo "[+] Git add all..." | tee -a "$LOG_FILE"
git add -A

echo "[+] Git commit..." | tee -a "$LOG_FILE"
git commit -m "Complete backup: $DATE

Backup includes:
- memories/ (user data)
- SOUL.md (personality)
- skills/ (all skills)
- cron-output/ (scheduled tasks)
- workspace/ (project files)
- config.yaml (settings)
- channel_directory.json (platform config)" --allow-empty 2>&1 | tee -a "$LOG_FILE"

echo "[+] Git push..." | tee -a "$LOG_FILE"
git push https://${TOKEN}@github.com/USERNAME/REPO.git main --force 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup BERHASIL: $DATE" | tee -a "$LOG_FILE"
    echo "Backup completed: $DATE" > last_backup.txt
else
    echo "❌ Backup GAGAL: $DATE" | tee -a "$LOG_FILE"
    exit 1
fi

echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
```

Ganti `USERNAME/REPO` dengan repo GitHub lu.

### 5. Setup git identity
```bash
git config --global user.email "backup-bot@local"
git config --global user.name "Hermes Backup Bot"
```

### 6. Push pertama kali
```bash
cd ~/backup-hermes
chmod +x backup-complete.sh
bash backup-complete.sh
```

### 7. Buat cronjob harian
Gunakan tool `cronjob` dengan:
- schedule: `0 0 * * *` (jam 00:00 UTC)
- prompt: `Jalankan /root/backup-hermes/backup-complete.sh`
- deliver: telegram (untuk notif sukses/gagal)

## Pitfalls & Solutions

1. **Token Security** - Jangan pernah hardcode token di script! Simpan di file `.token` terpisah dan add ke .gitignore

2. **Missing memories/** - Backup biasa sering lupa backup `memories/` (isi user profile). Data ini penting buat agent inget preferensi user!

3. **Missing SOUL.md** - Personality/persona agent tersimpan di SOUL.md. Kalau ga di-backup, agent kehilangan identitasnya setelah restore

4. **Git identity** - Perlu set user.email dan user.name sebelum commit

5. **Token scope** - Token harus punya scope `repo`

6. **rsync untuk skills** - Skills folder bisa besar dan ada file yang dihapus. Gunakan `rsync --delete` biar backup mirror exact state

## Restore dari Backup

```bash
# Clone backup repo
git clone https://github.com/USERNAME/REPO.git backup-restore
cd backup-restore

# Restore ke hermes
mkdir -p ~/.hermes/memories && cp -r memories/* ~/.hermes/memories/
cp SOUL.md ~/.hermes/
cp -r skills/* ~/.hermes/skills/
cp -r cron-output/* ~/.hermes/cron/output/ 2>/dev/null
mkdir -p ~/.hermes/workspace && cp -r workspace/* ~/.hermes/workspace/
cp config.yaml ~/.hermes/ 2>/dev/null
cp channel_directory.json ~/.hermes/ 2>/dev/null

echo "Restore complete!"
```

## Hasil

- Backup otomatis tiap hari jam 00:00 UTC
- Notifikasi sukses/gagal ke Telegram (atau platform lain)
- Include SEMUA data penting: user profile, personality, skills, cron, workspace, config
- Log lengkap di `backup.log`
- Timestamp terakhir backup di `last_backup.txt`