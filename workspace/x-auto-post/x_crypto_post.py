#!/usr/bin/python3
"""
X Auto Poster with AI-Generated Crypto Tweets
1. Fetch real crypto data from CoinGecko + CMC
2. AI generates unique, engaging tweet
3. Post to X
"""

import requests
import json
import random
import sys
import asyncio
import os
import fcntl
from datetime import datetime
from playwright.async_api import async_playwright

# ============ CONFIG ============

FIREWORKS_API_KEY = "fw_7yUaJeJBDFig2GWL8nFPDQ"
FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"
FIREWORKS_MODEL = "accounts/fireworks/models/llama-v3p3-70b-instruct"

# ============ CRYPTO DATA FETCHER ============

def get_trending_coingecko():
    """Fetch trending from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return [
            {
                'name': item.get('item', {}).get('name', ''),
                'symbol': item.get('item', {}).get('symbol', '').upper(),
                'rank': item.get('item', {}).get('market_cap_rank', 'N/A'),
                'price_btc': item.get('item', {}).get('price_btc', 0)
            }
            for item in data.get('coins', [])[:5]
        ]
    except Exception as e:
        print(f"CoinGecko trending error: {e}")
        return []

def get_top_gainers_coingecko():
    """Fetch top gainers from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'price_change_percentage_24h_desc',
            'per_page': 10,
            'sparkline': False,
            'price_change_percentage': '24h,7d'
        }
        resp = requests.get(url, params=params, timeout=10)
        coins = []
        for c in resp.json():
            coins.append({
                'name': c.get('name', ''),
                'symbol': c.get('symbol', '').upper(),
                'change_24h': round(c.get('price_change_percentage_24h', 0) or 0, 2),
                'change_7d': round(c.get('price_change_percentage_7d_in_currency', 0) or 0, 2),
                'price': c.get('current_price', 0),
                'volume': c.get('total_volume', 0),
                'market_cap': c.get('market_cap', 0),
                'ath': c.get('ath', 0),
                'ath_change': round(c.get('ath_change_percentage', 0) or 0, 2)
            })
        return coins
    except Exception as e:
        print(f"CoinGecko gainers error: {e}")
        return []

def get_top_losers_coingecko():
    """Fetch top losers"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'price_change_percentage_24h_asc',
            'per_page': 5,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        resp = requests.get(url, params=params, timeout=10)
        return [
            {
                'name': c.get('name', ''),
                'symbol': c.get('symbol', '').upper(),
                'change_24h': round(c.get('price_change_percentage_24h', 0) or 0, 2),
                'price': c.get('current_price', 0)
            }
            for c in resp.json()
        ]
    except Exception as e:
        print(f"CoinGecko losers error: {e}")
        return []

def get_market_global():
    """Get global market data"""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        resp = requests.get(url, timeout=10)
        data = resp.json().get('data', {})
        return {
            'market_cap': data.get('total_market_cap', {}).get('usd', 0),
            'change_24h': round(data.get('market_cap_change_percentage_24h_usd', 0), 2),
            'btc_dominance': round(data.get('market_cap_percentage', {}).get('btc', 0), 1),
            'eth_dominance': round(data.get('market_cap_percentage', {}).get('eth', 0), 1),
            'volume': data.get('total_volume', {}).get('usd', 0),
            'fear_greed': None  # Will try to get from alternative source
        }
    except Exception as e:
        print(f"Global market error: {e}")
        return {}

def get_fear_greed_index():
    """Get Fear & Greed Index"""
    try:
        url = "https://api.alternative.me/fng/"
        resp = requests.get(url, timeout=10)
        data = resp.json().get('data', [{}])[0]
        return {
            'value': int(data.get('value', 50)),
            'classification': data.get('value_classification', 'Neutral')
        }
    except:
        return {'value': 50, 'classification': 'Neutral'}

def get_cmc_trending():
    """Fetch trending from CMC (public endpoint)"""
    try:
        url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/trending"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return [
            {
                'name': c.get('name', ''),
                'symbol': c.get('symbol', ''),
                'rank': c.get('cmcRank', 'N/A')
            }
            for c in data.get('data', {}).get('cryptoCurrencyList', [])[:5]
        ]
    except Exception as e:
        print(f"CMC trending error: {e}")
        return []

def format_price(price):
    """Format price nicely"""
    if price >= 1:
        return f"${price:,.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.8f}"

def format_large_number(num):
    """Format billions/millions"""
    if num >= 1_000_000_000_000:
        return f"${num/1_000_000_000_000:.1f}T"
    elif num >= 1_000_000_000:
        return f"${num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.1f}M"
    return f"${num:,.0f}"

# ============ AI TWEET GENERATOR ============

def generate_ai_tweet():
    """Fetch data and let AI create unique tweet"""
    
    # Fetch all data
    print("📊 Fetching crypto data...")
    
    trending_gecko = get_trending_coingecko()
    gainers = get_top_gainers_coingecko()
    losers = get_top_losers_coingecko()
    market = get_market_global()
    fgi = get_fear_greed_index()
    trending_cmc = get_cmc_trending()
    
    # Build context for AI
    context = f"""
CURRENT CRYPTO MARKET DATA ({datetime.now().strftime('%Y-%m-%d %H:%M')} UTC)

=== GLOBAL MARKET ===
Total Market Cap: {format_large_number(market.get('market_cap', 0))}
24h Change: {market.get('change_24h', 0)}%
BTC Dominance: {market.get('btc_dominance', 0)}%
ETH Dominance: {market.get('eth_dominance', 0)}%
Fear & Greed Index: {fgi['value']} ({fgi['classification']})

=== TOP GAINERS (24h) ===
{chr(10).join([f"{i+1}. {c['symbol']} - {c['name']}: {c['change_24h']}% | Price: {format_price(c['price'])} | Vol: {format_large_number(c['volume'])}" for i, c in enumerate(gainers[:5])])}

=== TOP LOSERS (24h) ===
{chr(10).join([f"{i+1}. {c['symbol']} - {c['name']}: {c['change_24h']}% | Price: {format_price(c['price'])}" for i, c in enumerate(losers[:3])])}

=== TRENDING (CoinGecko) ===
{chr(10).join([f"{i+1}. {c['symbol']} - {c['name']} (Rank #{c['rank']})" for i, c in enumerate(trending_gecko)])}

=== TRENDING (CMC) ===
{chr(10).join([f"{i+1}. {c['symbol']} - {c['name']} (Rank #{c['rank']})" for i, c in enumerate(trending_cmc)])}
"""
    
    # AI prompt
    prompt = f"""You are a crypto Twitter influencer. Create ONE engaging tweet based on this real market data.

RULES:
1. Maximum 280 characters (Twitter limit)
2. Use emojis but don't overdo it
3. Be insightful, NOT generic
4. Pick the most INTERESTING story from the data
5. Include relevant hashtag(s)
6. Write in a mix of Indonesian casual style + English crypto terms
7. Don't use placeholder or template - write something SPECIFIC
8. Make it feel fresh and personal, like a real trader sharing insights
9. If there's a big move (+20% or more), highlight it
10. If Fear & Greed is extreme, mention it

DATA:
{context}

Write only the tweet text, nothing else. No quotes, no explanation."""

    # Call Fireworks API
    try:
        url = f"{FIREWORKS_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {FIREWORKS_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": FIREWORKS_MODEL,
            "messages": [
                {"role": "system", "content": "You are a crypto Twitter influencer who writes engaging, original tweets about cryptocurrency markets."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.9
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        tweet = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        # Clean up if needed
        tweet = tweet.strip('"\'')
        
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        return tweet
        
    except Exception as e:
        print(f"AI generation error: {e}")
        # Fallback to template
        return generate_fallback_tweet(gainers, trending_gecko, market, fgi)

def generate_fallback_tweet(gainers, trending, market, fgi):
    """Fallback if AI fails"""
    if gainers and gainers[0]['change_24h'] > 10:
        c = gainers[0]
        return f"🔥 {c['symbol']} meledak {c['change_24h']}%! Harga {format_price(c['price'])}. Volume mencapai {format_large_number(c['volume'])}. Moon atau trap? 🌙 #{c['symbol']} #crypto"
    
    if trending:
        t = trending[0]
        return f"👀 {t['symbol']} trending hari ini! Rank #{t['rank']}. Masih early atau udah kebablasan? DYOR! #{t['symbol']} #crypto"
    
    if fgi['value'] <= 25:
        return f"😰 Fear & Greed: {fgi['value']} ({fgi['classification']})! Market takut = opportunity? Warren Buffett mode: be greedy when others fearful. #crypto #HODL"
    elif fgi['value'] >= 75:
        return f"🚀 Greed level: {fgi['value']} ({fgi['classification']})! Euphoria tinggi. Waktu take profit atau FOMO masuk? Careful! #crypto"
    
    return f"📊 Market: {market.get('change_24h', 0)}% | MCap: {format_large_number(market.get('market_cap', 0))} | F&G: {fgi['value']}\n\nSideways season atau accumulation phase? Stay sharp! #crypto"

# ============ X POSTER ============

def load_cookies():
    with open('cookies.json', 'r') as f:
        return json.load(f)

async def post_to_x(content):
    cookies = load_cookies()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        
        await context.add_cookies([
            {'name': c['name'], 'value': c['value'], 'domain': c.get('domain', '.x.com'), 'path': '/'}
            for c in cookies
        ])
        
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        # Go to home
        await page.goto('https://x.com/home', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        if 'login' in page.url:
            print("ERROR: Not logged in")
            await browser.close()
            return False
        
        # Find textarea
        textarea = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
        await textarea.click(force=True)
        await page.wait_for_timeout(1000)
        
        # Type
        await page.keyboard.type(content, delay=50)
        await page.wait_for_timeout(2000)
        
        # Remove overlays
        await page.evaluate('''() => {
            document.getElementById('layers')?.remove();
            document.querySelectorAll('[style*="position: fixed"]').forEach(el => {
                if (getComputedStyle(el).zIndex > 100) el.remove();
            });
        }''')
        
        await page.wait_for_timeout(1000)
        
        # Click button
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
    # Lock mechanism - prevent duplicate runs
    lock_file = open('/tmp/x_auto_post.lock', 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("❌ Another instance is already running. Exiting.")
        return 1
    
    print(f"\n{'='*50}")
    print(f"X CRYPTO AUTO POSTER v3.0 (AI-POWERED)")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    # Generate tweet with AI
    tweet = generate_ai_tweet()
    
    print("\n🤖 AI-Generated Tweet:")
    print("-" * 40)
    print(tweet)
    print("-" * 40)
    print(f"Length: {len(tweet)} chars")
    
    # Save
    with open('latest_tweet.txt', 'w') as f:
        f.write(tweet)
    
    # Append to history
    with open('tweets_history.txt', 'a') as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n{tweet}\n")
    
    # Post
    print("\n🚀 Posting to X...")
    success = await post_to_x(tweet)
    
    # Release lock
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
    
    if success:
        print("\n✅ SUCCESS: Tweet posted!")
    else:
        print("\n❌ FAILED: Could not post")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))