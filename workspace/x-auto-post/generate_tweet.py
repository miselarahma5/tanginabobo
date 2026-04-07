#!/usr/bin/python3
"""
Crypto Tweet Generator
Fetch trending crypto dan generate tweet menarik
"""

import requests
import json
import random
from datetime import datetime

def get_trending_coins():
    """Fetch trending coins from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        coins = []
        for item in data.get('coins', [])[:5]:
            coin = item.get('item', {})
            coins.append({
                'name': coin.get('name', ''),
                'symbol': coin.get('symbol', '').upper(),
                'market_cap_rank': coin.get('market_cap_rank', 'N/A'),
                'price_btc': coin.get('price_btc', 0)
            })
        return coins
    except Exception as e:
        print(f"Error fetching trending: {e}")
        return []

def get_top_gainers():
    """Fetch top gainers from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'price_change_percentage_24h_desc',
            'per_page': 5,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        gainers = []
        for coin in data:
            gainers.append({
                'name': coin.get('name', ''),
                'symbol': coin.get('symbol', '').upper(),
                'change_24h': round(coin.get('price_change_percentage_24h', 0), 2),
                'price': coin.get('current_price', 0)
            })
        return gainers
    except Exception as e:
        print(f"Error fetching gainers: {e}")
        return []

def get_crypto_news():
    """Fetch latest crypto news"""
    try:
        # Using CryptoCompare API (free)
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&limit=5"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        news = []
        for item in data.get('Data', []):
            news.append({
                'title': item.get('title', ''),
                'source': item.get('source', ''),
                'categories': item.get('categories', '')
            })
        return news
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def generate_tweet(trending, gainers, news):
    """Generate engaging crypto tweet"""
    
    templates = []
    
    # Template untuk trending coins
    if trending:
        coin = random.choice(trending)
        templates.extend([
            f"🔥 {coin['symbol']} sedang trending! Market cap rank #{coin['market_cap_rank']}. Apa kalian sudah punya? #crypto #{coin['symbol']}",
            f"👀 Semua orang bicara tentang {coin['name']} ({coin['symbol']}) hari ini. Masih belum terlambat untuk DYOR! #crypto",
            f"🚀 {coin['symbol']} masuk top trending di CoinGecko! Hype atau fundamental? Kalian gimana? #{coin['symbol']} #crypto",
        ])
    
    # Template untuk top gainers
    if gainers:
        coin = random.choice(gainers)
        if coin['change_24h'] > 0:
            templates.extend([
                f"📈 {coin['symbol']} naik {coin['change_24h']}% dalam 24 jam! Harga sekarang ${coin['price']:,.4f}. Moon incoming? 🌙 #{coin['symbol']}",
                f"💥 GAINER ALERT: {coin['name']} ({coin['symbol']}) +{coin['change_24h']}% hari ini! Apakah ini awal bull run? #crypto #{coin['symbol']}",
                f"🏃 {coin['symbol']} lagi lari keras! +{coin['change_24h']}% dalam 24jam. Jangan sampai ketinggalan! #{coin['symbol']}",
            ])
    
    # Template untuk news
    if news:
        item = random.choice(news)
        templates.extend([
            f"📰 Breaking: {item['title'][:80]}... Stay updated fam! #crypto #news",
            f"🔔 News alert: {item['title'][:70]}... Apa dampaknya untuk market? #{item['categories'].split('|')[0] if item['categories'] else 'crypto'}",
        ])
    
    # Template kombinasi
    if trending and gainers:
        t = random.choice(trending)
        g = random.choice(gainers)
        templates.append(
            f"📊 Market Update:\n🔥 Trending: {t['symbol']}\n📈 Top gainer: {g['symbol']} (+{g['change_24h']}%)\n\nMarket lagi seru hari ini! #crypto"
        )
    
    # Template generik jika ada data
    if trending or gainers:
        templates.extend([
            f"🧠 DYOR sebelum FOMO! Hari ini crypto market lagi bergerak cepat. Trending coins bisa jadi peluang atau jebakan. #crypto #trading",
            f"⚡ Crypto never sleeps! Market 24/7,机会 everywhere. Yang penting risk management tetap jaga. #crypto #DYOR",
            f"🎯 Another day, another opportunity di crypto space. Stay alert, stay profitable! WAGMI 🚀🌙 #crypto",
        ])
    
    if not templates:
        return "Crypto market senin-senang saja hari ini. Stay tuned untuk update selanjutnya! #crypto"
    
    return random.choice(templates)

def main():
    print(f"Crypto Tweet Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    print("Fetching trending coins...")
    trending = get_trending_coins()
    print(f"Found {len(trending)} trending coins")
    
    print("Fetching top gainers...")
    gainers = get_top_gainers()
    print(f"Found {len(gainers)} top gainers")
    
    print("Fetching crypto news...")
    news = get_crypto_news()
    print(f"Found {len(news)} news items")
    
    print("\nGenerating tweet...")
    tweet = generate_tweet(trending, gainers, news)
    
    print("\n" + "=" * 50)
    print("GENERATED TWEET:")
    print("=" * 50)
    print(tweet)
    print("=" * 50)
    print(f"Length: {len(tweet)} characters")
    
    # Save to file
    with open('latest_tweet.txt', 'w') as f:
        f.write(tweet)
    
    print("\nTweet saved to latest_tweet.txt")
    
    # Also show data used
    if trending:
        print("\n--- Trending Coins ---")
        for c in trending:
            print(f"  {c['symbol']} - {c['name']} (Rank #{c['market_cap_rank']})")
    
    if gainers:
        print("\n--- Top Gainers ---")
        for c in gainers:
            print(f"  {c['symbol']} - {c['name']} +{c['change_24h']}% (${c['price']:,.4f})")
    
    return tweet

if __name__ == '__main__':
    main()