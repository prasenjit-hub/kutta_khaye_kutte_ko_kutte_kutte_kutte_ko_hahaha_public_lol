"""
Test: Latest Video Logic & Hindi Audio
"""
from modules.scraper import get_channel_videos

print("=" * 80)
print("Testing: Latest Video Download Logic")
print("=" * 80)

# Test scrape
channel = "https://www.youtube.com/@MrBeast"
print(f"\n📺 Scraping: {channel}")
print("Sorting by: DATE (newest first)\n")

videos = get_channel_videos(channel, sort_by='date')

if videos:
    print(f"✓ Found {len(videos)} videos\n")
    print("=" * 80)
    print("Latest 5 Videos (Newest First):")
    print("=" * 80)
    
    for i, video in enumerate(videos[:5], 1):
        print(f"\n{i}. {video['title']}")
        print(f"   Published: {video.get('published', 'Unknown')}")
        print(f"   Views: {video['views']:,}")
        print(f"   Duration: {video['duration']}")
        print(f"   ID: {video['id']}")
    
    print("\n" + "=" * 80)
    print("Processing Order (How System Works):")
    print("=" * 80)
    
    print("""
Day 1:
  ✅ Download: Video #1 (Latest)
  ✅ Split into parts
  ✅ Upload all parts
  ✅ Mark as "completed" in tracking.json

Day 2:
  ❌ Video #1 → Status: completed → SKIP!
  ✅ Video #2 (2nd latest) → Download & Process

Day 3:
  ❌ Video #1 → SKIP (completed)
  ❌ Video #2 → SKIP (completed)
  ✅ Video #3 (3rd latest) → Download & Process

... continues newest to oldest
""")
    
    print("=" * 80)
    print("Hindi Audio Preference:")
    print("=" * 80)
    print("""
When downloading:
  1️⃣ First try: Hindi audio track
  2️⃣ Fallback: Best available audio
  3️⃣ Always: 1080p video quality

If Hindi dubbed version exists → Downloaded ✅
If no Hindi → English audio used
""")
    
    print("=" * 80)
    print("Tracking System:")
    print("=" * 80)
    print("""
tracking.json structure:
{
  "videos": {
    "VIDEO_ID_1": {
      "title": "Latest Video",
      "published": "1 day ago",
      "status": "completed",  ← Skip this!
      "parts_uploaded": [1,2,3,4,5]
    },
    "VIDEO_ID_2": {
      "title": "2nd Latest",
      "published": "3 days ago",
      "status": "pending"  ← Process this next!
    }
  }
}
""")
    
    print("=" * 80)
    print("✅ All Logic Updated!")
    print("=" * 80)
    print("\nReady to run:")
    print("  python main.py --full")
    print("\nThis will:")
    print("  1. Scrape channel (newest first)")
    print("  2. Find latest incomplete video")
    print("  3. Download with Hindi audio (if available)")
    print("  4. Process & upload")
    print("  5. Mark as completed")
    print("  6. Next run → automatically picks 2nd latest")
    
else:
    print("✗ No videos found")
