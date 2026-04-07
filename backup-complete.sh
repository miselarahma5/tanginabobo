#!/bin/bash

# Complete Hermes Backup Bot by Hitagi
# Backup SEMUA data penting: memories, SOUL, skills, cron, workspace, config

BACKUP_DIR=~/backup-hermes
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="$BACKUP_DIR/backup.log"

# Token dari file terpisah (jangan hardcode!)
if [ -f "$BACKUP_DIR/.token" ]; then
    TOKEN=$(cat "$BACKUP_DIR/.token" 2>/dev/null | tr -d '\n')
else
    echo "[ERROR] Token file tidak ditemukan: $BACKUP_DIR/.token"
    echo "Buat file .token dulu dengan isi: YOUR_GITHUB_TOKEN"
    exit 1
fi

cd "$BACKUP_DIR" || exit 1

echo "========================================" >> "$LOG_FILE"
echo "Backup dimulai: $DATE" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. BACKUP MEMORY (penting! ada data pek)
echo "[+] Backup memories/..." | tee -a "$LOG_FILE"
mkdir -p memories
cp -r ~/.hermes/memories/* memories/ 2>/dev/null && echo "  ✓ memories OK" | tee -a "$LOG_FILE" || echo "  ✗ memories failed" | tee -a "$LOG_FILE"

# 2. BACKUP SOUL.md (personality Hitagi)
echo "[+] Backup SOUL.md..." | tee -a "$LOG_FILE"
cp ~/.hermes/SOUL.md . 2>/dev/null && echo "  ✓ SOUL.md OK" | tee -a "$LOG_FILE" || echo "  ✗ SOUL.md failed" | tee -a "$LOG_FILE"

# 3. BACKUP SKILLS (27 skill)
echo "[+] Backup skills/..." | tee -a "$LOG_FILE"
mkdir -p skills
rsync -av --delete ~/.hermes/skills/ skills/ 2>/dev/null && echo "  ✓ skills OK" | tee -a "$LOG_FILE" || echo "  ✗ skills failed" | tee -a "$LOG_FILE"

# 4. BACKUP CRON OUTPUT
echo "[+] Backup cron-output/..." | tee -a "$LOG_FILE"
mkdir -p cron-output
cp -r ~/.hermes/cron/output/* cron-output/ 2>/dev/null && echo "  ✓ cron-output OK" | tee -a "$LOG_FILE" || echo "  ✗ cron-output failed" | tee -a "$LOG_FILE"

# 5. BACKUP WORKSPACE
echo "[+] Backup workspace/..." | tee -a "$LOG_FILE"
mkdir -p workspace
cp -r ~/.hermes/workspace/* workspace/ 2>/dev/null && echo "  ✓ workspace OK" | tee -a "$LOG_FILE" || echo "  ✗ workspace failed" | tee -a "$LOG_FILE"

# 6. BACKUP CONFIG (tapi exclude API keys)
echo "[+] Backup config.yaml..." | tee -a "$LOG_FILE"
cp ~/.hermes/config.yaml . 2>/dev/null && echo "  ✓ config.yaml OK" | tee -a "$LOG_FILE" || echo "  ✗ config.yaml failed" | tee -a "$LOG_FILE"

# 7. BACKUP CHANNEL DIRECTORY (gateway info)
echo "[+] Backup channel_directory.json..." | tee -a "$LOG_FILE"
cp ~/.hermes/channel_directory.json . 2>/dev/null && echo "  ✓ channel_directory OK" | tee -a "$LOG_FILE" || echo "  ✗ channel_directory failed" | tee -a "$LOG_FILE"

# Git operations
echo "[+] Git add all..." | tee -a "$LOG_FILE"
git add -A

echo "[+] Git commit..." | tee -a "$LOG_FILE"
git commit -m "🖤 Complete backup by Hitagi: $DATE

Backup includes:
- memories/ (user data)
- SOUL.md (personality)
- skills/ (27 skills)
- cron-output/ (scheduled tasks)
- workspace/ (project files)
- config.yaml (settings)
- channel_directory.json (platform config)" --allow-empty 2>&1 | tee -a "$LOG_FILE"

echo "[+] Git push..." | tee -a "$LOG_FILE"
git push https://${TOKEN}@github.com/miselarahma5/tanginabobo.git main --force 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup BERHASIL: $DATE" | tee -a "$LOG_FILE"
    echo "Backup completed: $DATE" > last_backup.txt
else
    echo "❌ Backup GAGAL: $DATE" | tee -a "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
