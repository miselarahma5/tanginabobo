---
name: x-crypto-auto-post
description: Auto-post AI-generated crypto tweets to X/Twitter using Playwright with cookies. Fetches real-time data from CoinGecko, CMC, and Fear & Greed Index, then uses AI (Llama 3.3 70B via Fireworks) to create unique, engaging tweets in Indonesian casual + English crypto style.
version: 3.0.0
author: Hitagi
tags: [twitter, x, crypto, auto-post, playwright, coingecko, ai, llama, fireworks]
---

# X Crypto Auto Poster v3.0 (AI-Powered)

Auto-generate dan post tweet crypto ke X/Twitter dengan AI-generated content.

## Fitur v3.0

- **AI-Generated Tweets**: Llama 3.3 70B via Fireworks API
- **Rich Data Sources**: CoinGecko, CMC, Fear & Greed Index
- **Original Content**: Bukan template, AI create fresh tiap post
- **Mixed Language**: Indonesian casual + English crypto terms
- **Contextual**: AI highlights the most interesting story from data
- **Tweet History**: Auto-save ke `tweets_history.txt`

## Perbandingan v2.0 vs v3.0

| v2.0 (Template) | v3.0 (AI-Generated) |
|-----------------|---------------------|
| Template statis | AI generate orisinal |
| Kalimat monoton | Narasi dinamis |
| Ga paham konteks | AI highlight story terbaik |
| Style manual pilih | AI adapt to market condition |

## Prerequisites

- Cookies X/Twitter yang valid (export dari browser)
- Python + Playwright installed
- Fireworks API key (untuk AI)

## Setup

### 1. Export Cookies X

1. Install extension "EditThisCookie" atau "Cookie Editor"
2. Login ke x.com di browser
3. Klik extension → Export cookies
4. Simpan sebagai `cookies.json`

### 2. Install Dependencies

```bash
pip install playwright requests
playwright install chromium
```

### 3. API Keys

Script menggunakan Fireworks API dari config Hermes:
```python
FIREWORKS_API_KEY = "fw_..."  # Atau dari config.yaml
FIREWORKS_MODEL = "accounts/fireworks/models/llama-v3p3-70b-instruct"
```

### 4. File Structure

```
x-auto-post/
├── x_crypto_post.py    # Main script v3.0 (AI-powered)
├── cookies.json        # X cookies
├── tweets_history.txt  # Auto-generated history
└── latest_tweet.txt    # Last generated tweet
```

## Cronjob Setup

```bash
# Jam 09:00 dan 18:00 UTC
(crontab -l 2>/dev/null; echo "0 9,18 * * * cd /root/x-auto-post && /usr/bin/python3 x_crypto_post.py >> /root/x-auto-post/cron.log 2>&1") | crontab -
```

**PENTING:** Pastikan cron service running:
```bash
systemctl status cron
```

## AI Tweet Generation

### Data Sources

```python
# CoinGecko APIs
"https://api.coingecko.com/api/v3/search/trending"      # Trending coins
"https://api.coingecko.com/api/v3/coins/markets"        # Gainers/Losers
"https://api.coingecko.com/api/v3/global"               # Market overview

# Fear & Greed Index
"https://api.alternative.me/fng/"                       # Sentiment index

# CMC (optional, might need API key)
"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/trending"
```

### AI Prompt Strategy

AI diberi data real-time dan diminta:
1. Pick the most INTERESTING story from the data
2. Maximum 280 characters
3. Use emojis but don't overdo it
4. Indonesian casual + English crypto terms
5. Be insightful, NOT generic
6. Highlight big moves (+20% or more)
7. Mention extreme Fear & Greed conditions

### AI Response Examples

```
# Market Fear Condition
"Extreme Fear mode on! 🚨 Fear & Greed Index at 12, 
BTC & ETH dumped -2.83% & -3.27% in 24h. 
Time to buy the dip, bro? 🤔 #cryptocurrency #bitcoin"

# Trending Coin
"Wah, Fear & Greed Index di 12, Extreme Fear nih! 🚨 
BTC dan ETH turun, tapi STO dan SIREN sedang naik di CoinGecko. 
Mungkin saatnya untuk buy the dip? #cryptocurrency #buythedip"
```

### Fallback jika AI Fail

```python
def generate_fallback_tweet(gainers, trending, market, fgi):
    # Simple template jika API error
    if fgi['value'] <= 25:
        return f"😰 Fear & Greed: {fgi['value']} ({fgi['classification']})! Market takut = opportunity?"
    # ... more fallbacks
```

## Key Issues & Solutions

### Problem 1: Cronjob Tidak Jalan

**Symptom:** Tweet tidak terkirim padahal script manual OK.

**Root Cause:** Crontab kosong atau cron service tidak running.

**Solution:**
1. Cek crontab: `crontab -l`
2. Cek cron service: `systemctl status cron`
3. Setup cronjob dengan command di atas

### Problem 2: Overlay Blocking Button

X.com punya overlay (`#layers`, cookie consent) yang nge-block klik tombol Post.

**Solution:**
```python
await page.evaluate('''() => {
    document.getElementById('layers')?.remove();
    document.querySelectorAll('[style*="position: fixed"]').forEach(el => {
        if (getComputedStyle(el).zIndex > 100) el.remove();
    });
}''')
```

### Problem 3: Click Intercepted

Normal click gagal karena overlay.

**Solution:**
```python
result = await page.evaluate('''() => {
    const btns = document.querySelectorAll('[data-testid="tweetButtonInline"], [data-testid="tweetButton"]');
    for (let btn of btns) {
        if (btn.offsetParent !== null) {
            btn.click();
            return "clicked";
        }
    }
    return "fail";
}''')
```

### Problem 4: Bot Detection

Headless browser detected sebagai bot.

**Solution:**
```python
browser = await p.chromium.launch(
    headless=True,
    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
)

await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
""")
```

### Problem 5: CoinGecko Rate Limit

**Symptom:** API returns 429 error

**Solution:** Tunggu reset (biasanya per menit). Cronjob 2x sehari aman.

### Problem 6: AI API Error

**Symptom:** Fireworks API timeout/error

**Solution:** Fallback ke template sederhana dengan `generate_fallback_tweet()`

## Testing

```bash
cd ~/x-auto-post
/usr/bin/python3 x_crypto_post.py

# Test multiple runs untuk lihat variasi AI
for i in 1 2 3; do /usr/bin/python3 x_crypto_post.py; sleep 2; done
```

## Limitations

- Cookies bisa expired (perlu refresh manual)
- Rate limit X jika posting terlalu sering
- CoinGecko API rate limit (gratis: 10-50 calls/menit)
- AI kadang generate mirip (tapi ga identik)

## Troubleshooting

| Issue | Check | Solution |
|-------|-------|----------|
| Tweet ga terkirim | `crontab -l` | Setup cronjob |
| Cron ga jalan | `systemctl status cron` | Start cron service |
| Playwright error | `playwright install chromium` | Install browser |
| Login failed | Check cookies.json | Re-export cookies |
| AI error | Check Fireworks API key | Check config.yaml |
| Rate limit CoinGecko | Tunggu 1 menit | Kurangi frequency |

## Upgrade Notes (v2.0 → v3.0)

1. Script baru menggunakan AI via Fireworks
2. Data fetch tambahan: Fear & Greed Index, CMC trending
3. Ga ada lagi template style, AI yang generate
4. Fallback tetap ada jika AI fail
5. Tweet lebih fresh dan varied