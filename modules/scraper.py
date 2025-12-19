"""
YouTube Channel Scraper - HINDI VERSION
Scrapes all videos from a YouTube channel without using API
Filters videos to only include those after March 15, 2019 (Hindi audio available)
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Minimum date for Hindi audio availability on MrBeast channel
MIN_VIDEO_DATE = datetime(2019, 3, 15)


def parse_relative_date(relative_str: str) -> datetime:
    """
    Parse relative date strings like "2 days ago", "1 month ago", "1 year ago"
    Returns approximate datetime
    """
    now = datetime.now()
    relative_str = relative_str.lower().strip()
    
    # Extract number and unit
    match = re.search(r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s*ago', relative_str)
    
    if not match:
        # If can't parse, assume it's recent (within date range)
        return now
    
    number = int(match.group(1))
    unit = match.group(2)
    
    # Calculate the date
    if unit == 'second':
        return now - timedelta(seconds=number)
    elif unit == 'minute':
        return now - timedelta(minutes=number)
    elif unit == 'hour':
        return now - timedelta(hours=number)
    elif unit == 'day':
        return now - timedelta(days=number)
    elif unit == 'week':
        return now - timedelta(weeks=number)
    elif unit == 'month':
        return now - timedelta(days=number * 30)  # Approximate
    elif unit == 'year':
        return now - timedelta(days=number * 365)  # Approximate
    
    return now


def is_video_after_min_date(published_str: str, min_date: datetime = MIN_VIDEO_DATE) -> bool:
    """
    Check if video was published after the minimum date
    """
    video_date = parse_relative_date(published_str)
    return video_date >= min_date



def get_channel_videos(channel_url: str, sort_by: str = 'date', filter_by_date: bool = True) -> List[Dict]:
    """
    Scrape all videos from a YouTube channel using yt-dlp for reliability.
    """
    logger.info(f"Scraping channel: {channel_url}")
    
    # Ensure URL ends with /videos to target long-form content
    if not channel_url.endswith('/videos'):
        channel_url = channel_url.rstrip('/') + '/videos'
    
    videos = []
    import subprocess
    import shutil
    
    # Check if yt-dlp is available
    if not shutil.which('yt-dlp'):
        logger.error("yt-dlp not found! Please install it.")
        return []
        
    try:
        # Use yt-dlp to get video list (flat playlist, no download fast)
        # Limit to 50 videos since we prioritize new ones (and for speed)
        # We can increase this later if needed, but 50 is enough for automation.
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--dump-single-json',
            '--playlist-end', '50',
            channel_url
        ]
        
        logger.info("Fetching video list via yt-dlp...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            logger.error(f"yt-dlp scraping failed: {result.stderr}")
            return []
            
        data = json.loads(result.stdout)
        entries = data.get('entries', [])
        
        logger.info(f"Found {len(entries)} videos (limited to latest 50)")
        
        for entry in entries:
            pub_date = "Unknown"
            # yt-dlp often gives upload_date in YYYYMMDD format
            if entry.get('upload_date'):
                d = entry.get('upload_date')
                try:
                    dt = datetime.strptime(d, '%Y%m%d')
                    pub_date = dt.strftime('%Y-%m-%d')
                except:
                    pass
            
            videos.append({
                'id': entry.get('id'),
                'title': entry.get('title'),
                'views': entry.get('view_count', 0) or 0,
                'duration': entry.get('duration', 0), # in seconds
                'published': pub_date,
                'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
            })

        # Filter by date (Hindi audio availability)
        if filter_by_date:
            filtered_videos = []
            for v in videos:
                # If date is known, check it
                if v['published'] != 'Unknown':
                    try:
                        v_date = datetime.strptime(v['published'], '%Y-%m-%d')
                        if v_date >= MIN_VIDEO_DATE:
                            filtered_videos.append(v)
                    except:
                        # Keep if date parsing fails (safe side)
                        filtered_videos.append(v)
                else:
                    # Keep unknowns
                    filtered_videos.append(v)
            
            diff = len(videos) - len(filtered_videos)
            logger.info(f"🇮🇳 Filtered out {diff} old videos")
            videos = filtered_videos
            
        logger.info(f"✓ {len(videos)} videos ready for processing")
        return videos
        
    except Exception as e:
        logger.error(f"Error extracting videos: {e}")
        return []


def extract_videos_from_page(html_content: str) -> List[Dict]:
    """Deprecated: Manual extraction logic (kept for fallback reference)"""
    return []



def parse_view_count(view_text: str) -> int:
    """
    Parse view count text like "1.2M views" to integer
    """
    try:
        # Remove "views" and clean
        view_text = view_text.lower().replace('views', '').replace('view', '').strip()
        
        # Handle K, M, B suffixes
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in view_text:
                number = float(view_text.replace(suffix, '').strip())
                return int(number * multiplier)
        
        # No suffix, just a number
        return int(view_text.replace(',', ''))
        
    except:
        return 0


if __name__ == "__main__":
    # Test the scraper
    test_url = "https://www.youtube.com/@MrBeast"
    videos = get_channel_videos(test_url, filter_by_date=True)
    
    print(f"\n🇮🇳 Videos with Hindi audio (after March 2019):")
    print(f"Total: {len(videos)} videos\n")
    
    print("Top 5 videos:")
    for i, video in enumerate(videos[:5], 1):
        print(f"{i}. {video['title']}")
        print(f"   Views: {video['views']:,} | Duration: {video['duration']}")
        print(f"   Published: {video['published']}")
        print(f"   URL: {video['url']}\n")
