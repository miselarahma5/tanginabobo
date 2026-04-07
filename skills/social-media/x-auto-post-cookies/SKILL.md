---
name: x-auto-post-cookies
description: Auto posting ke X/Twitter menggunakan browser cookies dengan Playwright automation. Schedule posting harian dengan konten dari file.
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [python3]
  packages: [playwright]
  files: [cookies.json, tweets.txt]
---

# X Auto Post dengan Cookies (Playwright)

Posting otomatis ke X/Twitter tanpa API credentials. Pakai cookies dari browser login + Playwright browser automation.

## Kapan Pakai Skill Ini

- User mau auto-post ke X tapi ga mau bayar API
- User mau schedule posting harian
- User punya akses browser untuk export cookies

## Setup

### 1. Install Playwright dan Chromium

```bash
pip3 install playwright
/usr/bin/python3 -m playwright install chromium
```

### 2. Buat Project Folder

```bash
mkdir -p ~/x-auto-post && cd ~/x-auto-post
```

### 3. Export Cookies dari Browser

User harus:
1. Install extension "EditThisCookie" atau "Cookie Editor" di browser
2. Login ke X.com di browser
3. Klik extension → Export cookies
4. Simpan sebagai `cookies.json` di folder project

Format cookies.json (dari Cookie Editor):
```json
[
  {
    "name": "auth_token",
    "value": "xxx",
    "domain": ".x.com",
    "path": "/"
  },
  {
    "name": "ct0",
    "value": "xxx",
    "domain": ".x.com"
  },
  ...
]
```

Cookies penting yang harus ada:
- `auth_token` (PALING PENTING)
- `ct0` (CSRF token)
- `kdt`
- `twid`

### 4. Buat File tweets.txt

Satu tweet per baris. Bot akan pilih random:

```
Hari baru, semangat baru! 🚀
Stay grinding, success will follow 💪
Crypto never sleeps 📈
WAGMI 🚀🌙
```

### 5. Buat Script x_post.py

Lihat file `scripts/x_post.py` untuk script lengkap.

### 6. Test Manual

```bash
cd ~/x-auto-post
/usr/bin/python3 x_post.py
```

### 7. Setup Cronjob dengan Hermes

**Untuk tweet crypto auto-generated (RECOMMENDED):**
```python
cronjob(
    action='create',
    name='x-auto-post-daily',
    schedule='0 9,18 * * *',  # 2x sehari: jam 9 dan 18
    prompt='Jalankan script X crypto auto post: cd ~/x-auto-post && /usr/bin/python3 x_crypto_post.py. Script akan fetch trending crypto, generate tweet, dan post ke X. Kirim hasil ke Telegram.',
    deliver='telegram'
)
```

**Untuk tweet manual dari file:**
```python
cronjob(
    action='create',
    name='x-auto-post-daily',
    schedule='0 9 * * *',  # 1x sehari
    prompt='Jalankan script X auto post: cd ~/x-auto-post && /usr/bin/python3 x_post.py. Kirim hasil ke Telegram.',
    deliver='telegram'
)
```

## File yang Dibutuhkan

| File | Deskripsi |
|------|-----------|
| `cookies.json` | Cookies dari browser (WAJIB) |
| `tweets.txt` | Daftar konten tweet (untuk x_post.py) |
| `x_post.py` | Script untuk tweet manual dari file |
| `x_crypto_post.py` | Script untuk auto-generate tweet crypto (RECOMMENDED) |

## Pilihan Script

**1. x_post.py** - Tweet dari file
- Baca konten dari `tweets.txt`
- Pilih random satu tweet
- Cocok untuk konten manual

**2. x_crypto_post.py** - Tweet crypto auto-generated (RECOMMENDED)
- Fetch trending coins & top gainers dari CoinGecko API
- Generate tweet menarik dengan hashtag
- Contoh output: "📈 ETH +1.21% dalam 24h! Harga $2,128.03. Moon? 🌙 #ETH"

## Cara Kerja

1. Load cookies dari `cookies.json`
2. Launch Playwright browser (Chromium headless) dengan stealth settings
3. Inject cookies ke browser context
4. Navigate ke `https://x.com/home` (HOME PAGE - lebih reliable dari intent URL)
5. Cari textarea `[data-testid="tweetTextarea_0"]`, isi dengan konten
6. Remove overlay via JavaScript (layer blocking clicks)
7. Click tombol tweet via JavaScript (`.click()` biasa sering gagal)
8. Return status sukses/gagal

**PENTING:** 
- Gunakan HOME PAGE (`/home`) BUKAN intent URL atau compose page
- Intent URL kadang redirect ke login walau cookies valid
- Compose page punya overlay yang susah di-handle
- Click tombol HARUS via JavaScript (`page.evaluate()`) bukan `.click()`

## Troubleshooting

### Cookies Expired
- Login ulang ke X di browser
- Export cookies baru
- Timpa file `cookies.json`

### "Not logged in" Error
- Cookies expired atau invalid
- Pastikan login di browser dengan akun yang benar
- Re-export cookies

### Playwright Chromium Not Found
```bash
/usr/bin/python3 -m playwright install chromium
```

### ModuleNotFoundError: No module named 'playwright'
- Pastikan pakai `/usr/bin/python3` bukan venv python
- Install dengan: `pip3 install playwright`

### Rate Limit / Akun Kena Limit
- Jangan posting terlalu sering
- 2x sehari aman
- Spread waktu minimal 6 jam

## Pitfalls

- **API approach tidak bekerja**: X API internal sudah berubah, harus pakai browser automation
- **Python venv vs system**: Hermes pakai venv python yang terpisah, harus pakai `/usr/bin/python3`
- **Domain .x.com vs .twitter.com**: X sekarang pakai domain `.x.com`, pastikan cookies domain benar
- **Headless mode**: Chromium headless butuh dependency sistem, jika error install dengan `playwright install-deps chromium`
- **Overlay blocking clicks**: X punya layer div (`#layers`) yang nge-block semua click. Solusi: remove via `page.evaluate()` atau click langsung via JavaScript
- **Intent URL tidak reliable**: Intent URL (`/intent/post`) kadang redirect ke login walau cookies valid. Gunakan home page (`/home`) + isi textarea manual
- **Click via .click() gagal**: Overlay nge-block pointer events. Solusi: click via `page.evaluate('() => btn.click()')`

## Notes

- Cookies bisa expired sewaktu-waktu (biasanya bertahan berbulan-bulan)
- Jangan spam, X bisa suspend akun
- Untuk fitur lebih lengkap (reply, quote, dll), pertimbangkan pakai API resmi
- Skill `xitter` pakai API resmi jika user punya developer access