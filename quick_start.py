"""
Quick Start Guide - YouTube Shorts Automation
"""
import json
import os

print("=" * 80)
print("YouTube to YouTube Shorts Automation - Quick Start")
print("=" * 80)

# Step 1: Check config
print("\n📝 Step 1: Checking Configuration...")
if not os.path.exists('config.json'):
    print("✗ config.json not found!")
    exit(1)

with open('config.json', 'r') as f:
    config = json.load(f)

youtube_channel = config['youtube_channel']
credentials_file = config['youtube_upload']['credentials_file']

if youtube_channel == "https://www.youtube.com/@CHANNEL_NAME":
    print("⚠️  Please update config.json with target YouTube channel!")
    print("\nEdit config.json and update:")
    print('  - "youtube_channel": "https://www.youtube.com/@ChannelName"')
    print("\nThen run this script again.")
    exit(1)

print(f"✓ YouTube Channel: {youtube_channel}")

# Step 2: Check YouTube credentials
print("\n🔑 Step 2: Checking YouTube Authentication...")
if not os.path.exists(credentials_file):
    print(f"✗ {credentials_file} not found!")
    print("\n⚠️  YouTube API Setup Required:")
    print("1. Read YOUTUBE_SETUP.md for complete guide")
    print("2. Create Google Cloud project")
    print("3. Enable YouTube Data API v3")
    print("4. Download credentials as youtube_credentials.json")
    print("5. Run this script again")
    exit(1)

print(f"✓ Credentials file found: {credentials_file}")

# Check if already authenticated
if os.path.exists('youtube_token.pickle'):
    print("✓ Already authenticated (token found)")
else:
    print("⚠️  First time authentication needed")
    print("\nRun: python modules\\youtube_uploader.py")
    print("Browser will open → Login → Grant permissions → Done!")
    exit(1)

# Step 3: Test YouTube API
print("\n🎬 Step 3: Testing YouTube API...")
try:
    from modules.youtube_uploader import YouTubeUploader
    
    uploader = YouTubeUploader(credentials_file)
    print("✓ YouTube API authenticated successfully!")
    
except Exception as e:
    print(f"✗ YouTube API authentication failed: {e}")
    print("\nTry:")
    print("1. Delete youtube_token.pickle")
    print("2. Run: python modules\\youtube_uploader.py")
    exit(1)

# Step 4: Test scraper
print("\n🔍 Step 4: Testing YouTube Scraper...")
try:
    from modules.scraper import get_channel_videos
    
    videos = get_channel_videos(youtube_channel)
    
    if videos:
        print(f"✓ Found {len(videos)} videos!")
        print(f"\nHighest viewed video:")
        top = videos[0]
        print(f"  Title: {top['title']}")
        print(f"  Views: {top['views']:,}")
        print(f"  Duration: {top['duration']}")
    else:
        print("✗ No videos found. Check the channel URL.")
        exit(1)
        
except Exception as e:
    print(f"✗ Scraper test failed: {e}")
    exit(1)

# Step 5: Check directories
print("\n📁 Step 5: Checking Directories...")
for dirname in ['downloads', 'processed', 'logs']:
    if os.path.exists(dirname):
        print(f"✓ {dirname}/ exists")
    else:
        os.makedirs(dirname)
        print(f"✓ Created {dirname}/")

# Step 6: Check FFmpeg
print("\n🎥 Step 6: Checking FFmpeg...")
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ FFmpeg installed")
    else:
        print("✗ FFmpeg not working properly")
except FileNotFoundError:
    print("✗ FFmpeg not found in PATH")
    print("\nPlease install FFmpeg:")
    print("https://ffmpeg.org/download.html")
    exit(1)

# All checks passed!
print("\n" + "=" * 80)
print("✅ SETUP COMPLETE! ALL SYSTEMS READY!")
print("=" * 80)

print(f"\n🎯 Target Channel: {youtube_channel}")
print(f"📊 Available Videos: {len(videos)}")
print(f"🏆 Top Video: {videos[0]['views']:,} views")

print("\n🚀 Ready to Start! Choose an option:\n")
print("Option 1: Full Automation (Recommended)")
print("  python main.py --full")
print("  → Downloads, processes, and uploads highest viewed video\n")

print("Option 2: Step by Step")
print("  python main.py --scrape     # Update video list")
print("  python main.py --status     # Check current status")
print("  python main.py --full       # Run full automation\n")

print("Option 3: Check Status First")
print("  python main.py --status     # See what's already been done\n")

print("=" * 80)
print("📈 YouTube API Quota:")
print("  Default: ~6 uploads/day")
print("  Request increase for 60+ uploads/day (free, 24-48hr)")
print("  See YOUTUBE_SETUP.md for quota increase guide")
print("=" * 80)

print("\n💡 Tips:")
print("  - First run will take time (downloading + processing)")
print("  - Videos are saved locally (won't re-download)")
print("  - Check logs/automation.log for detailed progress")
print("  - Already uploaded videos are automatically skipped")

print("\n✅ Safe & Legal:")
print("  - Uses official YouTube API")
print("  - No ban risk")
print("  - Monetization eligible")

print("\n" + "=" * 80)
