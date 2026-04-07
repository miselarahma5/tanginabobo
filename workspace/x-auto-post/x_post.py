#!/usr/bin/python3
"""
X/Twitter Auto Poster - Remove overlay version
"""

import json
import random
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

def load_cookies():
    with open('cookies.json', 'r') as f:
        return json.load(f)

def get_content():
    try:
        with open('tweets.txt', 'r') as f:
            tweets = [line.strip() for line in f if line.strip()]
        if tweets:
            return random.choice(tweets)
    except:
        pass
    return "Test dari bot 🤖"

async def post_tweet():
    print(f"X Auto Poster - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    cookies = load_cookies()
    content = get_content()
    print(f"Tweet: {content}")
    
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
        
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        print("Membuka X...")
        await page.goto('https://x.com/home', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        if 'login' in page.url:
            print("ERROR: Tidak login")
            await browser.close()
            return 1
        
        print("Mencari kolom tweet...")
        textarea = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
        
        # Click and type
        await textarea.click(force=True)
        await page.wait_for_timeout(1000)
        await page.keyboard.type(content, delay=50)
        await page.wait_for_timeout(2000)
        
        print("Tweet dimasukkan, menghapus overlay...")
        
        # Remove ALL overlays
        await page.evaluate('''() => {
            // Remove layers div
            const layers = document.getElementById('layers');
            if (layers) layers.remove();
            
            // Remove any fixed position overlays
            document.querySelectorAll('[style*="position: fixed"], [style*="position:fixed"]').forEach(el => {
                if (getComputedStyle(el).zIndex > 100) el.remove();
            });
            
            // Remove cookie consent
            document.querySelectorAll('[data-testid*="cc"], [class*="cookie"]').forEach(el => el.remove());
        }''')
        
        await page.wait_for_timeout(1000)
        await page.screenshot(path='after_remove_overlay.png')
        
        # Try multiple ways to click
        print("Mengirim tweet...")
        
        # Method 1: Direct JS click
        result = await page.evaluate('''() => {
            const btns = document.querySelectorAll('[data-testid="tweetButtonInline"], [data-testid="tweetButton"]');
            for (let btn of btns) {
                if (btn.offsetParent !== null) {  // visible
                    btn.click();
                    return "clicked via JS: " + btn.dataset.testid;
                }
            }
            return "no visible button";
        }''')
        print(f"Method 1: {result}")
        
        await page.wait_for_timeout(2000)
        
        # Method 2: Keyboard Enter
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(3000)
        
        # Method 3: Ctrl+Enter
        await page.keyboard.press('Control+Enter')
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path='final_result.png')
        
        print("Selesai! Cek final_result.png")
        await browser.close()
        return 0

def main():
    return asyncio.run(post_tweet())

if __name__ == '__main__':
    sys.exit(main())