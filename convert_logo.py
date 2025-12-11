"""
Logo Saver
This script saves the generated logo to the project folder
"""
import os
import shutil
from PIL import Image

# NEW GENERATED LOGO PATH
SOURCE_PATH = r".gemini\antigravity\brain\434f95e2-5aa2-4043-b90e-c9d6d5bde74e\epic_shorts_hub_final_1765394939128.png"
DEST_DIR = "channel_assets"

print("=" * 60)
print("📦 Packing Logo...")
print("=" * 60)

if not os.path.exists(DEST_DIR):
    os.makedirs(DEST_DIR)

if os.path.exists(SOURCE_PATH):
    # 1. Save PNG
    shutil.copy2(SOURCE_PATH, f"{DEST_DIR}/logo.png")
    print(f"✅ Logo saved: {DEST_DIR}/logo.png")
    
    # 2. Convert JPG
    try:
        img = Image.open(f"{DEST_DIR}/logo.png")
        img.convert('RGB').save(f"{DEST_DIR}/logo.jpg")
        print(f"✅ JPG version created")
    except Exception as e:
        print(f"⚠️ JPG conversion error: {e}")
        
    print("\n✨ Logo secured! You can now move the project folder.")
else:
    print(f"❌ Logo file not found at: {SOURCE_PATH}")
