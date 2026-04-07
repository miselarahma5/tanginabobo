---
name: auto-github-backup
description: Setup automated daily backup ke GitHub repo dengan cronjob
tags: [backup, github, cronjob, automation]
---

# Auto GitHub Backup

Setup automated daily backup ke GitHub repo dengan cronjob.

## Langkah-langkah

### 1. Siapkan folder backup
```bash
mkdir -p ~/backup-hermes && cd ~/backup-hermes
git init
git branch -m main
```

### 2. Buat file .token (pisahkan dari script)
```bash
echo "YOUR_GITHUB_TOKEN" > ~/backup-hermes/.token
```

### 3. Buat .gitignore
```
.token
*.log
```

### 4. Buat backup.sh
```bash
#!/bin/bash

BACKUP_DIR=~/backup-hermes
DATE=$(date +%Y-%m-%d_%H-%M-%S)
TOKEN=$(cat ~/backup-hermes/.token 2>/dev/null)

cd $BACKUP_DIR

echo "Copying files..."

# Copy data yang mau di-backup
mkdir -p memory && cp -r ~/.hermes/memory/* memory/ 2>/dev/null
mkdir -p skills && cp -r ~/.hermes/skills/* skills/ 2>/dev/null
mkdir -p cron-output && cp -r ~/.hermes/cron/output/* cron-output/ 2>/dev/null
mkdir -p workspace && cp -r ~/killim workspace/ 2>/dev/null

git add -A
git commit -m "Backup $DATE" --allow-empty
git push https://${TOKEN}@github.com/USERNAME/REPO.git main --force

echo "Backup completed: $DATE"
```

### 5. Setup git identity
```bash
git config --global user.email "backup-bot@local"
git config --global user.name "Backup Bot"
```

### 6. Push pertama kali
```bash
cd ~/backup-hermes
git add -A
git commit -m "Initial backup setup"
git remote add origin https://github.com/USERNAME/REPO.git
git push -f https://TOKEN@github.com/USERNAME/REPO.git main
```

### 7. Buat cronjob harian
Gunakan tool `cronjob` dengan:
- schedule: `0 0 * * *` (jam 00:00)
- prompt: instruksi untuk jalankan backup.sh
- deliver: telegram (untuk notif sukses/gagal)

## Pitfalls

1. **GitHub Push Protection** - GitHub akan menolak push kalau ada token di file. Solusi: simpan token di file terpisah (.token) dan tambahkan ke .gitignore

2. **Git identity** - Perlu set user.email dan user.name sebelum commit

3. **Embedded git repos** - Kalau backup folder yang ada .git, akan jadi submodule. Tidak masalah tapi perlu di-note.

4. **Token scope** - Token harus punya scope `repo`

## Hasil

Backup akan jalan otomatis tiap hari jam 00:00 dan push ke GitHub. Notifikasi dikirim ke platform yang dikonfigurasi.