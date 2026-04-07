#!/usr/bin/python3
"""
X Auto Poster with AI Crypto Tweet Generator
1. Fetch trending crypto data from CoinGecko
2. Generate engaging tweet
3. Post to X using Playwright + cookies

Usage:
    cd ~/x-auto-post
    /usr/bin/python3 x_crypto_post.py
"""

import requests
import json
import random
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# ============ CRYPTO DATA FETCHER ============

def get_trending_coins():
    """Fetch trending coins from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return [
            {
                'name': item.get('item', {}).get('name', ''),
                'symbol': item.get('item', {}).get('symbol', '').upper(),
                'rank': item.get('item', {}).get('market_cap_rank', 'N/A')
            }
            for item in data.get('coins', [])[:5]
        ]
    except:
        return []

def get_top_gainers():
    """Fetch top gainers from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'price_change_percentage_24h_desc',
            'per_page': 5,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        resp = requests.get(url, params=params, timeout=10)
        return [
            {
                'name': c.get('name', ''),
                'symbol': c.get('symbol', '').upper(),
                'change': round(c.get('price_change_percentage_24h', 0), 2),
                'price': c.get('current_price', 0)
            }
            for c in resp.json()
        ]
    except:
        return []

def generate_crypto_tweet():
    """Generate engaging crypto tweet from live data"""
    trending = get_trending_coins()
    gainers = get_top_gainers()
    
    templates = []
    
    # Trending templates
    if trending:
        c = random.choice(trending)
        templates.extend([
            f"🔥 {c['symbol']} sedang trending! Rank #{c['rank']}. Sudah punya? #crypto #{c['symbol']}",
            f"👀 {c['name']} ({c['symbol']}) trending hari ini. DYOR sebelum FOMO! #{c['symbol']}",
            f"🚀 {c['symbol']} masuk top trending! Hype atau fundamental? #crypto #{c['symbol']}",
        ])
    
    # Gainers templates
    if gainers:
        c = random.choice(gainers)
        if c['change'] > 0:
            templates.extend([
                f"📈 {c['symbol']} +{c['change']}% dalam 24h! Harga ${c['price']:,.2f}. Moon? 🌙 #{c['symbol']}",
                f"💥 GAINER: {c['name']} ({c['symbol']}) +{c['change']}%! Bull run? #{c['symbol']} #crypto",
                f"🏃 {c['symbol']} naik {c['change']}%! Jangan ketinggalan! #crypto #{c['symbol']}",
            ])
    
    # Combined market update
    if trending and gainers:
        t, g = random.choice(trending), random.choice(gainers)
        templates.append(
            f"📊 Update:\n🔥 Trending: {t['symbol']}\n📈 Gainer: {g['symbol']} (+{g['change']}%)\n\nMarket seru! #crypto"
        )
    
    # Fallback generic tweets
    if not templates:
        templates = [
            "🧠 DYOR sebelum FOMO! Crypto market bergerak cepat. Risk management is key! #crypto",
            "⚡ Crypto never sleeps! Peluang di mana-mana, yang penting timing. #crypto #trading",
            "🎯 Another day in crypto. Stay alert, stay profitable! WAGMI 🚀🌙 #crypto",
        ]
    
    return random.choice(templates)

# ============ X POSTER ============

def load_cookies():
    """Load cookies from cookies.json"""
    with open('cookies.json', 'r') as f:
        return json.load(f)

async def post_to_x(content):
    """Post tweet using Playwright + cookies"""
    cookies = load_cookies()
    
    async with async_playwright() as p:
        # Launch with stealth settings to avoid bot detection
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        
        # Inject cookies
        await context.add_cookies([
            {'name': c['name'], 'value': c['value'], 'domain': c.get('domain', '.x.com'), 'path': '/'}
            for c in cookies
        ])
        
        page = await context.new_page()
        
        # Hide webdriver detection
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        # Go to home page (NOT intent URL - more reliable)
        await page.goto('https://x.com/home', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        if 'login' in page.url:
            print("ERROR: Not logged in - cookies may be expired")
            await browser.close()
            return False
        
        # Find tweet textarea
        textarea = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
        await textarea.click(force=True)
        await page.wait_for_timeout(1000)
        
        # Type content with realistic delay
        await page.keyboard.type(content, delay=50)
        await page.wait_for_timeout(2000)
        
        # CRITICAL: Remove overlays that block clicks
        await page.evaluate('''() => {
            document.getElementById('layers')?.remove();
            document.querySelectorAll('[style*="position: fixed"]').forEach(el => {
                if (getComputedStyle(el).zIndex > 100) el.remove();
            });
        }''')
        
        await page.wait_for_timeout(1000)
        
        # Click button via JavaScript (not .click() - overlay blocks it)
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
        
        await page.wait_for_timeout(3000)
        await browser.close()
        
        return result == "clicked"

async def main():
    print(f"\n{'='*50}")
    print(f"X CRYPTO AUTO POSTER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    # Generate tweet from crypto data
    print("\n📊 Fetching crypto data...")
    tweet = generate_crypto_tweet()
    
    print("\n📝 Generated Tweet:")
    print("-" * 40)
    print(tweet)
    print("-" * 40)
    print(f"Length: {len(tweet)} chars")
    
    # Save for reference
    with open('latest_tweet.txt', 'w') as f:
        f.write(tweet)
    
    # Post to X
    print("\n🚀 Posting to X...")
    success = await post_to_x(tweet)
    
    if success:
        print("\n✅ SUCCESS: Tweet posted!")
        return 0
    else:
        print("\n❌ FAILED: Could not post")
        return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))