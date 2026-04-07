# X Auto Post Bot

Bot untuk auto posting ke X/Twitter 1x sehari pakai cookies browser.

## Setup

### 1. Export Cookies dari Browser

1. Install extension **"EditThisCookie"** atau **"Cookie Editor"** di browser
2. Login ke X/Twitter di browser
3. Buka halaman X.com
4. Klik extension, pilih **Export** cookies
5. Simpan file sebagai `cookies.json` di folder ini

### 2. Format cookies.json

Harus berupa array JSON:
```json
[
  {
    "name": "auth_token",
    "value": "xxx",
    "domain": ".twitter.com"
  },
  {
    "name": "ct0",
    "value": "xxx",
    "domain": ".twitter.com"
  },
  ...
]
```

### 3. Edit tweets.txt

Tambahkan tweet yang mau di-post (1 per baris). Bot akan pilih random setiap hari.

### 4. Test

```bash
python3 x_post.py
```

### 5. Setup Cronjob

Bot sudah auto-setup dengan cronjob harian jam 09:00 pagi.

## File Penting

- `cookies.json` - cookies dari browser (WAJIB)
- `tweets.txt` - daftar tweet untuk di-post
- `x_post.py` - script utama

## Notes

- Cookies bisa expired, kalau gagal login ulang dan export cookies baru
- Jangan spam, X bisa kena limit
- Posting 1x sehari aman