#!/usr/bin/python3
"""
X/Twitter Auto Poster - Debug version with full logging
"""

import json
import random
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import urllib.parse

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
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
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
        
        # Use intent URL
        encoded_text = urllib.parse.quote(content)
        intent_url = f"https://x.com/intent/post?text={encoded_text}"
        
        print(f"Opening: {intent_url}")
        await page.goto(intent_url, wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        print(f"Current URL: {page.url}")
        
        # Screenshot
        await page.screenshot(path='debug_1_initial.png', full_page=True)
        
        # Check if logged in
        if 'login' in page.url.lower():
            print("ERROR: Not logged in!")
            await browser.close()
            return 1
        
        # Wait for textarea and verify content
        print("Checking textarea...")
        try:
            textarea = await page.wait_for_selector('textarea', timeout=10000)
            textarea_content = await textarea.input_value()
            print(f"Textarea content: {textarea_content}")
        except Exception as e:
            print(f"Textarea error: {e}")
        
        # Find tweet button
        print("Looking for post button...")
        
        # Try different button selectors
        selectors = [
            '[data-testid="tweetButton"]',
            '[data-testid="tweetButtonInline"]',
            'button[type="submit"]',
            'button:has-text("Post")',
            'button:has-text("Tweet")',
        ]
        
        btn = None
        for sel in selectors:
            try:
                btn = await page.wait_for_selector(sel, timeout=3000)
                if btn:
                    print(f"Found button: {sel}")
                    break
            except:
                continue
        
        if not btn:
            print("ERROR: No button found!")
            await page.screenshot(path='debug_2_no_button.png', full_page=True)
            await browser.close()
            return 1
        
        # Click button
        print("Clicking button...")
        await btn.click(force=True)
        await page.wait_for_timeout(8000)
        
        # Check result
        print(f"After click URL: {page.url}")
        await page.screenshot(path='debug_3_after_click.png', full_page=True)
        
        # Check for success indicators
        page_content = await page.content()
        
        if 'success' in page_content.lower() or page.url == 'https://x.com/':
            print("SUCCESS: Tweet posted!")
            await browser.close()
            return 0
        elif 'error' in page_content.lower():
            print("ERROR: Something went wrong")
            await browser.close()
            return 1
        else:
            print("Unknown status - check screenshots")
            await browser.close()
            return 1

def main():
    return asyncio.run(post_tweet())

if __name__ == '__main__':
    sys.exit(main())