#!/usr/bin/python3
"""
Microstock Automation Workflow
===============================
1. Generate AI image prompts (using Fireworks API)
2. Generate images via browser/API
3. Upscale images
4. Inject metadata
5. Upload to Vecteezy via FTP
"""

import os
import json
import random
import requests
import time
import subprocess
from datetime import datetime
from pathlib import Path

# ============ CONFIG ============

# Get API key from environment or config
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "")
FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"
FIREWORKS_MODEL = "accounts/fireworks/models/llama-v3p3-70b-instruct"

# Directories
BASE_DIR = Path.home() / "microstock-workflow"
PROMPTS_DIR = BASE_DIR / "prompts"
RAW_DIR = BASE_DIR / "images-raw"
UPSCALED_DIR = BASE_DIR / "images-upscaled"
UPLOADED_DIR = BASE_DIR / "uploaded"
LOGS_DIR = BASE_DIR / "logs"

# Vecteezy FTP
VECTEEZY_FTP_HOST = os.getenv("VECTEEZY_FTP_HOST", "ftp.vecteezy.com")
VECTEEZY_FTP_USER = os.getenv("VECTEEZY_FTP_USER", "")
VECTEEZY_FTP_PASS = os.getenv("VECTEEZY_FTP_PASS", "")

# ============ PROMPT GENERATOR ============

CATEGORIES = [
    "abstract background", "business concept", "technology", "nature landscape",
    "minimalist design", "geometric pattern", "corporate team", "food photography",
    "fitness lifestyle", "education concept", "medical healthcare", "holiday celebration",
    "animal wildlife", "architecture building", "fashion style", "outdoor adventure",
    "urban city life", "eco green environment", "social media icons", "3D render object"
]

STYLES = [
    "photorealistic", "cinematic lighting", "soft natural light", "dramatic shadows",
    "minimalist clean", "vibrant colorful", "moody atmosphere", "bright airy",
    "professional studio", "golden hour", "blue hour", "high key lighting",
    "low key lighting", "editorial style", "commercial advertising", "fine art"
]

def generate_prompts_batch(count=100):
    """Generate batch of AI image prompts"""
    
    # Due to token limits, generate in batches
    BATCH_SIZE = 50  # 50 prompts per batch
    all_prompts = []
    batches_needed = (count + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_num in range(batches_needed):
        remaining = count - len(all_prompts)
        batch_count = min(BATCH_SIZE, remaining)
        
        prompt = f"""You are a professional stock image prompt engineer. Generate {batch_count} unique, high-quality image prompts for microstock websites (Shutterstock, Vecteezy, Adobe Stock).

REQUIREMENTS FOR EACH PROMPT:
1. Write ONE prompt per line
2. Each prompt must be descriptive and detailed (50-80 words)
3. Include: subject, action/pose, setting, lighting, mood, style, camera angle
4. Focus on commercial-sellable content (no copyrighted characters, no brands)
5. Vary subjects: people, nature, abstract, objects, backgrounds, technology
6. Use professional photography terminology
7. Avoid: violence, politics, religion, controversial topics
8. Make each prompt UNIQUE and different from others

CATEGORIES TO COVER (mix them):
{', '.join(random.sample(CATEGORIES, min(10, len(CATEGORIES))))}

STYLES TO USE (mix them):
{', '.join(random.sample(STYLES, min(8, len(STYLES))))}

EXAMPLE FORMAT:
"A professional diverse business team collaborating in a modern glass office building, natural sunlight streaming through floor-to-ceiling windows, candid authentic expressions, soft bokeh background, corporate atmosphere, shot on Canon EOS R5 with 85mm lens, professional commercial photography style"

Now generate {batch_count} unique prompts. Number each one (1., 2., 3., etc). Each prompt on its own line. NO blank lines between prompts."""

        try:
            url = f"{FIREWORKS_BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {FIREWORKS_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": FIREWORKS_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a professional stock image prompt engineer with expertise in commercial photography and AI image generation."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4096,
                "temperature": 0.8
            }
            
            print(f"🤖 Generating batch {batch_num + 1}/{batches_needed} ({batch_count} prompts)...")
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            result = resp.json()
            
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Parse prompts - split by lines and filter
            prompts = []
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove common prefixes (numbering, bullets)
                if line[0].isdigit():
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        clean = parts[1].strip()
                    else:
                        clean = line
                elif line.startswith('-') or line.startswith('*'):
                    clean = line.lstrip('- *').strip()
                else:
                    clean = line
                
                # Only add if it's a substantial prompt
                if len(clean) > 30:
                    prompts.append(clean)
            
            print(f"📊 Parsed {len(prompts)} prompts from this batch")
            all_prompts.extend(prompts)
            
            # Small delay between batches
            if batch_num < batches_needed - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Error in batch {batch_num + 1}: {e}")
            continue
    
    return all_prompts[:count]

def save_prompts(prompts, batch_name=None):
    """Save prompts to file"""
    if not batch_name:
        batch_name = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    filepath = PROMPTS_DIR / f"prompts_{batch_name}.txt"
    
    with open(filepath, 'w') as f:
        f.write(f"# Microstock Prompts Batch: {batch_name}\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Count: {len(prompts)}\n\n")
        for i, p in enumerate(prompts, 1):
            f.write(f"{i}. {p}\n\n")
    
    print(f"💾 Saved {len(prompts)} prompts to {filepath}")
    return filepath

def generate_prompts_daily(count=150):
    """Daily prompt generation task"""
    print(f"\n{'='*50}")
    print(f"MICROSTOCK PROMPT GENERATOR")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    prompts = generate_prompts_batch(count)
    
    if prompts:
        filepath = save_prompts(prompts)
        return {
            'success': True,
            'count': len(prompts),
            'file': str(filepath),
            'prompts': prompts
        }
    
    return {'success': False, 'count': 0, 'error': 'No prompts generated'}

# ============ METADATA INJECTOR ============

def inject_metadata(image_path, title, description, keywords):
    """Inject metadata into image file"""
    try:
        from PIL import Image
        import piexif
        
        img = Image.open(image_path)
        
        # Prepare EXIF data
        exif_dict = {
            "0th": {
                piexif.ImageIFD.ImageDescription: description.encode('utf-8'),
                piexif.ImageIFD.XPTitle: title.encode('utf-16-le'),
                piexif.ImageIFD.XPComment: description.encode('utf-16-le'),
                piexif.ImageIFD.XPKeywords: ','.join(keywords).encode('utf-16-le'),
            },
            "Exif": {
                piexif.ExifIFD.UserComment: description.encode('utf-8'),
            }
        }
        
        exif_bytes = piexif.dump(exif_dict)
        
        # Save with metadata
        output_path = UPSCALED_DIR / Path(image_path).name
        img.save(output_path, "JPEG", exif=exif_bytes, quality=95)
        
        print(f"✅ Metadata injected: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Metadata error: {e}")
        return None

# ============ FTP UPLOADER ============

def upload_to_vecteezy(image_paths):
    """Upload images to Vecteezy via FTP"""
    if not VECTEEZY_FTP_USER or not VECTEEZY_FTP_PASS:
        print("❌ Vecteezy FTP credentials not set")
        print("Set VECTEEZY_FTP_USER and VECTEEZY_FTP_PASS environment variables")
        return False
    
    try:
        # Build lftp command
        files_str = ' '.join([f'"{p}"' for p in image_paths])
        
        cmd = f'''lftp -c "
set ftp:ssl-allow no
open -u {VECTEEZY_FTP_USER},{VECTEEZY_FTP_PASS} {VECTEEZY_FTP_HOST}
mput {files_str}
bye
"'''
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Uploaded {len(image_paths)} images to Vecteezy")
            return True
        else:
            print(f"❌ FTP error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

# ============ MAIN WORKFLOW ============

def run_daily_workflow(prompt_count=150):
    """Run the complete daily workflow"""
    
    print("\n" + "="*60)
    print("MICROSTOCK DAILY WORKFLOW")
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*60)
    
    results = {
        'date': datetime.now().isoformat(),
        'steps': {}
    }
    
    # Step 1: Generate Prompts
    print("\n📝 STEP 1: Generating prompts...")
    prompts_result = generate_prompts_daily(prompt_count)
    results['steps']['prompts'] = prompts_result
    
    if prompts_result['success']:
        print(f"   ✅ {prompts_result['count']} prompts generated")
    else:
        print("   ❌ Prompt generation failed")
        return results
    
    # Step 2: Generate Images (placeholder - implement based on your method)
    print("\n🎨 STEP 2: Image generation...")
    print("   ⏳ This step requires your image generation setup")
    print("   Run image generation separately, then continue to step 3")
    results['steps']['images'] = {'status': 'pending', 'note': 'Manual or separate automation'}
    
    # Step 3: Upscale (placeholder - implement based on your tool)
    print("\n🔍 STEP 3: Upscaling...")
    print("   ⏳ Requires upscaler setup (Real-ESRGAN, etc)")
    results['steps']['upscale'] = {'status': 'pending'}
    
    # Step 4: Metadata injection (ready)
    print("\n🏷️ STEP 4: Metadata injection...")
    print("   ✅ Tool ready - run on upscaled images")
    results['steps']['metadata'] = {'status': 'ready', 'function': 'inject_metadata()'}
    
    # Step 5: Upload (ready if credentials set)
    print("\n📤 STEP 5: Upload to Vecteezy...")
    if VECTEEZY_FTP_USER:
        print("   ✅ FTP configured and ready")
    else:
        print("   ⚠️ Set VECTEEZY_FTP_USER and VECTEEZY_FTP_PASS")
    results['steps']['upload'] = {'status': 'ready' if VECTEEZY_FTP_USER else 'pending'}
    
    return results

# ============ CLI ============

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'prompts':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 150
            result = generate_prompts_daily(count)
            print(json.dumps(result, indent=2))
        
        elif command == 'metadata':
            if len(sys.argv) < 5:
                print("Usage: metadata <image_path> <title> <description> <keyword1,keyword2,...>")
            else:
                inject_metadata(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(','))
        
        elif command == 'upload':
            images = sys.argv[2:]
            upload_to_vecteezy(images)
        
        elif command == 'workflow':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 150
            run_daily_workflow(count)
        
        else:
            print("Commands: prompts, metadata, upload, workflow")
    
    else:
        # Default: generate prompts
        generate_prompts_daily(150)