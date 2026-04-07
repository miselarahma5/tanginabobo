/**
 * Vecteezy Upload Script (Puppeteer + Stealth)
 * 
 * Usage:
 *   cd ~/microstock-workflow
 *   node vecteezy_upload.js [image_path]
 * 
 * Requirements:
 *   npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

puppeteer.use(StealthPlugin());

const EMAIL = 'your_email@gmail.com';  // GANTI dengan email Vecteezy lu
const PASSWORD = 'your_password';       // GANTI dengan password Vecteezy lu
const COOKIES_FILE = './vecteezy_cookies_new.json';

async function login(page) {
    console.log('🔐 Logging in to Vecteezy...');
    await page.goto('https://contributors.vecteezy.com/sign_in', { waitUntil: 'networkidle2', timeout: 60000 });
    await new Promise(r => setTimeout(r, 5000));

    await page.type('#Email-input', EMAIL);
    await page.type('#Password-input', PASSWORD);
    
    await page.evaluate(() => {
        const btn = [...document.querySelectorAll('button')].find(b => b.innerText.includes('Log in'));
        if (btn) btn.click();
    });
    
    await new Promise(r => setTimeout(r, 10000));
    
    if (!page.url().includes('sign_in')) {
        console.log('✅ Login successful!');
        const cookies = await page.cookies();
        fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2));
        return true;
    } else {
        console.log('❌ Login failed');
        return false;
    }
}

async function upload(imagePath) {
    const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36');
    
    // Try to load existing cookies
    let loggedIn = false;
    if (fs.existsSync(COOKIES_FILE)) {
        const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf8'));
        await page.setCookie(...cookies);
        
        await page.goto('https://contributors.vecteezy.com/portfolio/upload', { waitUntil: 'networkidle2', timeout: 60000 });
        await new Promise(r => setTimeout(r, 5000));
        
        if (!page.url().includes('sign_in')) {
            console.log('✅ Session valid (using saved cookies)');
            loggedIn = true;
        }
    }
    
    // Login if needed
    if (!loggedIn) {
        const success = await login(page);
        if (!success) {
            await browser.close();
            return { success: false, error: 'Login failed' };
        }
    }
    
    // Navigate to upload page
    console.log('🌐 Navigating to upload page...');
    await page.goto('https://contributors.vecteezy.com/portfolio/upload', { waitUntil: 'networkidle2', timeout: 60000 });
    await new Promise(r => setTimeout(r, 3000));
    
    // Upload file
    if (imagePath) {
        console.log('📤 Uploading:', imagePath);
        const fileInput = await page.$('input[type="file"]');
        await fileInput.uploadFile(imagePath);
        
        console.log('⏳ Waiting 60s for upload...');
        await new Promise(r => setTimeout(r, 60000));
        
        const body = await page.evaluate(() => document.body.innerText);
        if (body.includes('Add Data')) {
            console.log('✅ Upload complete! Check Add Data tab to add metadata.');
        } else if (body.includes('Error')) {
            console.log('❌ Upload error detected');
        }
    }
    
    // Get upload status
    const status = await page.evaluate(() => {
        const tabs = [...document.querySelectorAll('a')].filter(a => 
            a.innerText.includes('Add Data') || 
            a.innerText.includes('Pending') ||
            a.innerText.includes('Approved')
        );
        return tabs.map(t => t.innerText);
    });
    console.log('📊 Status tabs:', status);
    
    await page.screenshot({ path: 'images-raw/vecteezy_upload_result.png', fullPage: true });
    console.log('📸 Screenshot saved');
    
    await browser.close();
    return { success: true };
}

// Run
const imagePath = process.argv[2] || null;
upload(imagePath)
    .then(r => console.log('\n📊 Result:', r))
    .catch(e => console.error('❌ Error:', e));