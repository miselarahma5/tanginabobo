#!/usr/bin/python3
"""
X/Twitter Auto Poster - Local Browser Version
Jalankan di komputer sendiri dengan browser visible

Setup:
1. Install: pip install playwright
2. Install browser: playwright install chromium
3. Jalankan: python x_post_local.py

Pertama kali jalankan akan:
- Buka browser untuk login manual
- Simpan cookies setelah lo login
- Posting tweet

Setelah itu cookies disimpan, jadi ga perlu login lagi
"""

import json
import random
import sys
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

COOKIES_FILE = 'cookies_saved.json'
TWEETS_FILE = 'tweets.txt'

def get_content():
    """Get random tweet from file"""
    try:
        with open(TWEETS_FILE, 'r') as f:
            tweets = [line.strip() for line in f if line.strip()]
        if tweets:
            return random.choice(tweets)
    except:
        pass
    return "Auto post dari bot 🤖"

async def login_and_save_cookies(page):
    """Open X for manual login, then save cookies"""
    print("\n" + "=" * 50)
    print("LOGIN MANUAL DIPERLUKAN")
    print("=" * 50)
    print("1. Browser akan terbuka")
    print("2. Login ke akun X lo")
    print("3. Setelah login berhasil, tekan ENTER di terminal ini")
    print("=" * 50 + "\n")
    
    await page.goto('https://x.com/login')
    
    # Wait for user to press Enter
    input("Tekan ENTER setelah selesai login... ")
    
    # Save cookies
    cookies = await page.context.cookies()
    with open(COOKIES_FILE, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print("Cookies disimpan!")
    return cookies

async def load_cookies(context):
    """Load saved cookies"""
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        return cookies
    return None

async def post_tweet():
    print(f"\nX Auto Poster - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    content = get_content()
    print(f"Tweet: {content}\n")
    
    async with async_playwright() as p:
        # Launch browser VISIBLE (headless=False)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Try to load saved cookies
        cookies = await load_cookies(context)
        
        if not cookies:
            # Need to login first
            await login_and_save_cookies(page)
        
        # Go to home
        print("Membuka X...")
        await page.goto('https://x.com/home', wait_until='networkidle')
        await page.wait_for_timeout(3000)
        
        # Check if still logged in
        if 'login' in page.url:
            print("Session expired, silakan login ulang...")
            await login_and_save_cookies(page)
            await page.goto('https://x.com/home', wait_until='networkidle')
            await page.wait_for_timeout(3000)
        
        print(f"URL: {page.url}")
        
        # Find tweet composer
        print("Mencari kolom tweet...")
        try:
            textarea = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
            
            # Click and type
            await textarea.click()
            await page.wait_for_timeout(500)
            
            # Type character by character (more realistic)
            for char in content:
                await page.keyboard.type(char)
                await asyncio.sleep(0.05)
            
            await page.wait_for_timeout(2000)
            print("Teks dimasukkan")
            
            # Find and click tweet button
            tweet_btn = await page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=5000)
            await tweet_btn.click()
            
            await page.wait_for_timeout(5000)
            
            print("\n" + "=" * 50)
            print("TWEET TERKIRIM!")
            print("=" * 50)
            
            # Keep browser open for a moment
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()
        return 0

def main():
    print("""
╔════════════════════════════════════════════╗
║     X AUTO POSTER - LOCAL BROWSER          ║
╠════════════════════════════════════════════╣
║  Jalankan di komputer lo sendiri           ║
║  Browser akan terbuka visible               ║
╚════════════════════════════════════════════╝
    """)
    
    return asyncio.run(post_tweet())

if __name__ == '__main__':
    sys.exit(main())