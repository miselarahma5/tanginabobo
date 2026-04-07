---
name: airdrop-auto-submit
description: Bot untuk auto-submit email ke landing page airdrop dengan web dashboard, Puppeteer automation, dan Telegram alerts
---

# Airdrop Auto-Submit Bot Dashboard

Bot untuk auto-submit email ke landing page airdrop (coming soon pages) dengan web dashboard.

## Project Structure
```
~/airdrop-bot/
├── server.js          # Express server + API endpoints
├── automation.js      # Puppeteer bot class
├── database.js        # SQLite setup
├── telegram.js       # Alert module
├── airdrop.db         # SQLite database
└── public/
    ├── index.html     # Dashboard UI
    └── screenshots/   # Submission screenshots
```

## Tech Stack
- Express.js (web server)
- Puppeteer + puppeteer-extra-plugin-stealth (automation)
- better-sqlite3 (database)
- node-telegram-bot-api (alerts)
- Tailwind CSS (UI)

## Key Features
1. **Email Management** - Add single or bulk emails
2. **Website Management** - Add single or bulk URLs
3. **Auto-Submit** - Puppeteer finds email input + submit button automatically
4. **Telegram Alerts** - Per-submission + batch summary
5. **Submission Log** - Track success/failed with screenshots
6. **SQLite Database** - Persistent storage

## Automation Logic
```javascript
// Email input selectors to try (in order)
const emailSelectors = [
  'input[type="email"]',
  'input[name="email"]',
  'input[placeholder*="email" i]',
  'input[placeholder*="Email" i]',
  'input[placeholder*="e-mail" i]',
  'input[id*="email" i]',
  'input[aria-label*="email" i]',
  'input.form-control[type="text"]',
  'input.lg\\:w-full[type="text"]',
  'input.input[type="text"]'
];

// Submit button detection - iterate all buttons and check innerText
const submitKeywords = ['submit', 'join', 'notify', 'subscribe', 'register', 'sign', 'get', 'start'];

// Success detection - check body text for keywords
const successKeywords = ['success', 'thank', 'thanks', 'subscribed', 'welcome', 'confirmed', 'check your email'];
const errorKeywords = ['error', 'invalid', 'already', 'failed', 'try again', 'bot verification'];
```

## Bot Detection Bypass Attempts
1. **puppeteer-extra-plugin-stealth** - Helps with basic fingerprinting
2. **Delay between actions** - Human-like timing (3-5s delay)
3. **Randomized typing** - `{ delay: 50 }` for natural feel
4. **Residential proxy** - REQUIRED for sites with bot protection (tested: privket.com still blocks without proxy)

## API Endpoints
- `GET /api/emails` - List emails
- `POST /api/emails` - Bulk add emails
- `POST /api/emails/single` - Add single email
- `DELETE /api/emails/:id` - Delete email
- `GET /api/websites` - List websites
- `POST /api/websites` - Bulk add websites
- `GET /api/submissions` - Submission log
- `POST /api/run` - Start bot
- `GET /api/status` - Check running status
- `POST /api/stop` - Stop bot

## Run
```bash
cd ~/airdrop-bot
node server.js
# Dashboard: http://localhost:3200
```

## Pitfalls
- **Bot Detection** - Many sites detect Puppeteer even with stealth plugin (tested: privket.com returns "Bot verification failed")
- **Residential Proxy Needed** - For sites with bot protection, need residential proxy (upgrade Browserbase plan or use similar service)
- **CAPTCHA** - Some sites have CAPTCHA requiring manual intervention
- **Cloudflare/HCaptcha** - Sites with strong protection will block automation
- **Email validation** - Patterns vary between sites
- **Email verification** - Some sites require clicking verification link in email

## CAPTCHA Types Encountered
1. **Cloudflare Turnstile** (privket.com)
   - Invisible CAPTCHA, sitekey: `0x4AAAAAACziYVeRu3DBE_PA`
   - API: POST `/api/notify` with `{ email, turnstileToken }`
   - Token required from JS challenge
   - **No free bypass** - need 2captcha/capsolver (~$1/1000)

2. **Tally.so Built-in CAPTCHA** (praxisnation.com)
   - Form embed: `tally.so/embed/mJLVZr`
   - CAPTCHA appears after form fill
   - Message: "Complete the Captcha before you can proceed"
   - **No free bypass**

3. **hCaptcha / reCAPTCHA** - Common on airdrop pages
   - Need captcha solver service

## Free Bypass Methods Tried (All Failed)
1. ❌ puppeteer-extra-plugin-stealth - Basic fingerprinting bypass
2. ❌ Playwright with human-like behavior - Mouse movement, slow typing
3. ❌ Firefox browser (different fingerprint) - Still blocked
4. ❌ Advanced stealth: `navigator.webdriver=undefined`, `window.chrome`
5. ❌ Human simulation: scroll, random delays, variable typing speed

## Tested Sites
- ❌ privket.com - Cloudflare Turnstile, requires captcha token
- ❌ praxisnation.com - Tally.so form with built-in CAPTCHA
- ⚠️ Sites without CAPTCHA should work with stealth plugin

## Improvements To Add
- Proxy rotation for multi-account
- Temp email API integration
- Discord webhook alerts
- CAPTCHA solver integration