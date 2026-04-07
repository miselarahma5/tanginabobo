#!/usr/bin/python3
"""
X/Twitter Auto Poster using Playwright
Uses home page approach (more reliable than intent URL)
"""

import json
import random
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

def load_cookies():
    """Load cookies from cookies.json"""
    with open('cookies.json', 'r') as f:
        return json.load(f)

def get_content():
    """Get random content from tweets.txt"""
    try:
        with open('tweets.txt', 'r') as f:
            tweets = [line.strip() for line in f if line.strip()]
        if tweets:
            return random.choice(tweets)
    except:
        pass
    return "Testing auto post bot 🤖"

async def post_tweet():
    print(f"X Auto Poster - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    cookies = load_cookies()
    content = get_content()
    print(f"Posting: {content}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
        
        # Add cookies
        await context.add_cookies([
            {
                'name': c['name'],
                'value': c['value'],
                'domain': c.get('domain', '.x.com'),
                'path': c.get('path', '/'),
            }
            for c in cookies
        ])
        
        page = await context.new_page()
        
        # Hide webdriver detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        # Go to HOME page (not intent URL - intent URL often redirects to login)
        print("Opening X home...")
        await page.goto('https://x.com/home', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        # Check if logged in
        if 'login' in page.url:
            print("Error: Not logged in. Cookies may have expired.")
            await page.screenshot(path='error_login.png')
            await browser.close()
            return 1
        
        # Find tweet textarea
        print("Finding tweet composer...")
        try:
            textarea = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
            
            # Click and type
            await textarea.click(force=True)
            await page.wait_for_timeout(1000)
            await page.keyboard.type(content, delay=50)
            await page.wait_for_timeout(2000)
            
            # Remove overlay that blocks clicks
            await page.evaluate('''() => {
                const layers = document.getElementById('layers');
                if (layers) layers.remove();
                document.querySelectorAll('[style*="position: fixed"]').forEach(el => {
                    if (getComputedStyle(el).zIndex > 100) el.remove();
                });
            }''')
            
            await page.wait_for_timeout(1000)
            
            # Click tweet button via JavaScript (more reliable than .click())
            print("Submitting tweet...")
            result = await page.evaluate('''() => {
                const btns = document.querySelectorAll('[data-testid="tweetButtonInline"], [data-testid="tweetButton"]');
                for (let btn of btns) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return "clicked";
                    }
                }
                return "not found";
            }''')
            
            await page.wait_for_timeout(5000)
            
            print(f"Tweet submitted! ({result})")
            await browser.close()
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path='error.png')
            await browser.close()
            return 1

def main():
    return asyncio.run(post_tweet())

if __name__ == '__main__':
    sys.exit(main())