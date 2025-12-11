"""
Test YouTube Scraper
"""
from modules.scraper import get_channel_videos

# Test channel
test_channel = "https://www.youtube.com/@MrBeast"

print(f"Testing scraper with: {test_channel}")
print("Scraping channel...")

videos = get_channel_videos(test_channel)

if videos:
    print(f"\n✓ SUCCESS! Found {len(videos)} videos\n")
    print("Top 5 videos by views:")
    print("-" * 80)
    for i, video in enumerate(videos[:5], 1):
        print(f"{i}. {video['title']}")
        print(f"   Views: {video['views']:,} | Duration: {video['duration']}")
        print(f"   URL: {video['url']}\n")
else:
    print("\n✗ FAILED! No videos found")
