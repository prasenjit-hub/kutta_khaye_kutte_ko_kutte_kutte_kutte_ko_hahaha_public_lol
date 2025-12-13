"""
Batch Download Script - Run LOCALLY with fresh cookies
Downloads all pending videos and uploads to Gofile cloud storage

Usage:
1. Export fresh YouTube cookies to youtube_cookies.txt
2. Run: python batch_download.py
3. Videos will be uploaded to Gofile
4. Cloud URLs saved to tracking.json
5. Push tracking.json to GitHub
"""
import json
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.downloader import VideoDownloader
from modules.scraper import get_channel_videos
from modules.notifier import notify_download_complete, send_telegram_message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tracking():
    if os.path.exists('tracking.json'):
        with open('tracking.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'videos': {}, 'channel_url': '', 'last_scrape': None}


def save_tracking(tracking):
    with open('tracking.json', 'w', encoding='utf-8') as f:
        json.dump(tracking, f, indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("=== BATCH DOWNLOAD TO GOFILE ===")
    print("=" * 60)
    
    # Check for cookies
    if not os.path.exists('youtube_cookies.txt'):
        print("\n❌ ERROR: youtube_cookies.txt not found!")
        print("Please export cookies from browser first.")
        return
    
    # Load config and tracking
    config = load_config()
    tracking = load_tracking()
    
    # Initialize downloader
    downloader = VideoDownloader(config['paths']['downloads'])
    
    # Scrape channel first
    print(f"\n📡 Scraping channel: {config['youtube_channel']}")
    videos = get_channel_videos(config['youtube_channel'], sort_by='date')
    
    # Update tracking with new videos
    tracking['channel_url'] = config['youtube_channel']
    tracking['last_scrape'] = datetime.now().isoformat()
    
    for video in videos:
        video_id = video['id']
        if video_id not in tracking['videos']:
            tracking['videos'][video_id] = {
                'title': video['title'],
                'views': video['views'],
                'duration': video['duration'],
                'published': video.get('published', 'Unknown'),
                'url': video['url'],
                'status': 'pending',
                'parts_uploaded': [],
                'total_parts': 0,
                'youtube_video_ids': [],
                'downloaded_at': None,
                'last_upload': None,
                'cloud_url': None
            }
    
    save_tracking(tracking)
    print(f"✓ Found {len(videos)} videos")
    
    # Find videos that need downloading (no cloud_url)
    videos_to_download = []
    for video_id, data in tracking['videos'].items():
        if data.get('status') in ['pending', 'partial'] and not data.get('cloud_url'):
            videos_to_download.append((video_id, data))
    
    if not videos_to_download:
        print("\n✅ All videos already have cloud URLs!")
        print("No downloads needed.")
        return
    
    print(f"\n📥 Videos to download: {len(videos_to_download)}")
    print("-" * 40)
    
    # Download each video and upload to Gofile
    successful_downloads = 0
    
    for i, (video_id, video_data) in enumerate(videos_to_download, 1):
        print(f"\n[{i}/{len(videos_to_download)}] {video_data['title'][:50]}...")
        
        # Download from YouTube and upload to Gofile
        cloud_info = downloader.download_and_upload_to_cloud(
            video_data['url'],
            video_id
        )
        
        if cloud_info:
            # Update tracking
            tracking['videos'][video_id]['cloud_url'] = cloud_info.get('download_page')
            tracking['videos'][video_id]['downloaded_at'] = datetime.now().isoformat()
            save_tracking(tracking)
            
            successful_downloads += 1
            print(f"   ✅ Uploaded to: {cloud_info.get('download_page')}")
        else:
            print(f"   ❌ Failed to download/upload")
            tracking['videos'][video_id]['status'] = 'skipped_download_failed'
            save_tracking(tracking)
    
    # Summary
    print("\n" + "=" * 60)
    print("=== BATCH DOWNLOAD COMPLETE ===")
    print("=" * 60)
    print(f"✅ Successfully downloaded: {successful_downloads}/{len(videos_to_download)}")
    print(f"☁️ Videos now in Gofile cloud storage")
    print(f"\n📋 Next steps:")
    print(f"   1. Push tracking.json to GitHub")
    print(f"   2. GitHub Actions will process parts from Gofile")
    print(f"   3. No more cookies needed until all parts done!")
    
    # Send notification
    try:
        notify_download_complete(successful_downloads)
    except:
        pass
    
    print("\n💡 Run: git add tracking.json && git commit -m 'Add cloud URLs' && git push")


if __name__ == "__main__":
    main()
