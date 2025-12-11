"""
Test Mode - Process 1 Video Clip WITHOUT Upload
Download → Split → Edit → Save (No Upload)
"""
import json
import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.scraper import get_channel_videos
from modules.downloader import VideoDownloader
from modules.splitter import VideoSplitter
from modules.editor import VideoEditor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("TEST MODE - Process 1 Clip Only (No Upload)")
print("=" * 80)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

channel_url = config['youtube_channel']

if channel_url == "https://www.youtube.com/@CHANNEL_NAME":
    print("\n❌ Please update config.json with a real YouTube channel URL first!")
    exit(1)

print(f"\n🎯 Target Channel: {channel_url}")
print("This will:")
print("  1. Scrape channel")
print("  2. Download latest video (small portion only)")
print("  3. Create 1 segment (60 seconds)")
print("  4. Add overlay (Part 1)")
print("  5. Apply zoom (1.25x)")
print("  6. Save to test_output/")
print("  7. STOP (no upload)\n")

confirm = input("Continue? (y/n): ")
if confirm.lower() != 'y':
    print("Cancelled.")
    exit(0)

# Create test output directory
os.makedirs('test_output', exist_ok=True)

print("\n" + "=" * 80)
print("Step 1: Scraping Channel")
print("=" * 80)

videos = get_channel_videos(channel_url, sort_by='date')

if not videos:
    print("❌ No videos found!")
    exit(1)

latest = videos[0]
print(f"\n✅ Latest video found:")
print(f"   Title: {latest['title']}")
print(f"   Published: {latest.get('published', 'Unknown')}")
print(f"   Views: {latest['views']:,}")
print(f"   Duration: {latest['duration']}")
print(f"   URL: {latest['url']}")

print("\n" + "=" * 80)
print("Step 2: Downloading Video")
print("=" * 80)
print("⚠️  This will download the full video (may take time)")
print("   Testing with full video to get accurate 60-second clip\n")

downloader = VideoDownloader('test_output')
video_path = downloader.download_video(latest['url'], 'test_video', prefer_hindi=True)

if not video_path:
    print("❌ Download failed!")
    exit(1)

print(f"\n✅ Downloaded: {video_path}")

print("\n" + "=" * 80)
print("Step 3: Creating 60-Second Segment (First Segment Only)")
print("=" * 80)

# Check if segment already exists
first_segment_path = 'test_output/test_video_part1.mp4'

if os.path.exists(first_segment_path):
    print(f"\n✅ Segment already exists: {first_segment_path}")
    print("   Skipping to editing step...")
    first_segment = first_segment_path
else:
    splitter = VideoSplitter('test_output')
    
    # Only create first segment
    from moviepy.editor import VideoFileClip
    
    print("Creating first 60-second clip...")
    video = VideoFileClip(video_path)
    
    # Take first 60 seconds
    segment = video.subclip(0, min(60, video.duration))
    
    segment.write_videofile(
        first_segment_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        verbose=False
    )
    
    segment.close()
    video.close()
    
    first_segment = first_segment_path
    print(f"\n✅ Created segment: {first_segment}")

if not os.path.exists(first_segment):
    print("❌ Segment creation failed!")
    exit(1)

print("\n" + "=" * 80)
print("Step 4: Adding Overlays & Zoom")
print("=" * 80)
print(f"   Zoom level: {config['video_settings'].get('zoom_level', 1.25)}x")
print(f"   Part text: 'Part 1' (top, 80px)")
print(f"   Target resolution: 1080x1920 (9:16)")
print()

editor = VideoEditor(config)
edited_path = editor.add_overlays(
    first_segment,
    part_number=1,
    title=latest['title'],
    output_path='test_output/FINAL_TEST_VIDEO.mp4'
)

if not edited_path:
    print("❌ Editing failed!")
    exit(1)

print("\n" + "=" * 80)
print("✅ SUCCESS! Test Video Created")
print("=" * 80)

print(f"\n📁 Location: {os.path.abspath(edited_path)}")
print(f"📊 File size: {os.path.getsize(edited_path) / (1024*1024):.2f} MB")

print("\n" + "=" * 80)
print("What to Check in Video:")
print("=" * 80)
print("""
✓ Resolution: Should be 1080x1920 (vertical/portrait)
✓ Zoom: Landscape video should be zoomed in (1.25x)
✓ Part overlay: "Part 1" at top (white text, black shadow)
✓ No title overlay: Only Part number, no title text
✓ Duration: Exactly 60 seconds
✓ Quality: Clear 1080p video
✓ Audio: Check if Hindi (if video has Hindi dub)
""")

print("\n" + "=" * 80)
print("Next Steps:")
print("=" * 80)
print("""
1. Open and watch the test video:
   test_output/FINAL_TEST_VIDEO.mp4

2. Verify everything looks good

3. If satisfied, proceed with full automation:
   python main.py --full

4. To test again with different video:
   Delete test_output/ folder and run this script again
""")

print("\n📹 Opening video location...")
import subprocess
try:
    # Open folder in file explorer
    subprocess.Popen(f'explorer /select,"{os.path.abspath(edited_path)}"')
except:
    pass

print("\n✅ Test complete! Check the video.")
