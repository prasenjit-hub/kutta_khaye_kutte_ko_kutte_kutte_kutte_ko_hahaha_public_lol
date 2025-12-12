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
    Scrape all videos from a YouTube channel and sort
    
    Args:
        channel_url: YouTube channel URL (e.g., https://www.youtube.com/@ChannelName)
        sort_by: 'date' for newest first, 'views' for highest views first
        filter_by_date: If True, only include videos after March 15, 2019
    
    Returns:
        List of video dictionaries with id, title, views, duration, upload_date
    """
    logger.info(f"Scraping channel: {channel_url}")
    
    # Ensure URL ends with /videos
    if not channel_url.endswith('/videos'):
        channel_url = channel_url.rstrip('/') + '/videos'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
        
        # Extract initial data from page
        videos = extract_videos_from_page(response.text)
        
        logger.info(f"Found {len(videos)} total videos")
        
        # Filter videos by date (only after March 15, 2019 for Hindi audio)
        if filter_by_date:
            original_count = len(videos)
            videos = [v for v in videos if is_video_after_min_date(v.get('published', 'Unknown'))]
            filtered_count = original_count - len(videos)
            logger.info(f"🇮🇳 Filtered out {filtered_count} videos (before March 2019, no Hindi audio)")
            logger.info(f"✓ {len(videos)} videos with Hindi audio available")
        
        # Sort by date (newest first) or views (highest first)
        if sort_by == 'date':
            # Videos are already in chronological order (newest first) from YouTube
            logger.info("Sorted by upload date (newest first)")
        else:
            # Sort by views (highest first)
            videos.sort(key=lambda x: x.get('views', 0), reverse=True)
            logger.info("Sorted by views (highest first)")
        
        return videos
        
    except Exception as e:
        logger.error(f"Error scraping channel: {e}")
        return []


def extract_videos_from_page(html_content: str) -> List[Dict]:
    """
    Extract video information from YouTube page HTML
    """
    videos = []
    
    # Look for ytInitialData JSON in the page
    match = re.search(r'var ytInitialData = ({.*?});', html_content)
    if not match:
        logger.warning("Could not find ytInitialData in page")
        return videos
    
    try:
        data = json.loads(match.group(1))
        
        # Navigate through the nested JSON structure
        tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
        
        for tab in tabs:
            tab_renderer = tab.get('tabRenderer', {})
            if tab_renderer.get('selected'):
                contents = tab_renderer.get('content', {}).get('richGridRenderer', {}).get('contents', [])
                
                for item in contents:
                    video_renderer = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                    
                    if video_renderer:
                        video_id = video_renderer.get('videoId')
                        title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', '')
                        
                        # Extract view count
                        view_text = video_renderer.get('viewCountText', {}).get('simpleText', '0')
                        views = parse_view_count(view_text)
                        
                        # Extract duration
                        duration_text = video_renderer.get('lengthText', {}).get('simpleText', '')
                        
                        # Extract upload time (e.g., "2 days ago", "1 week ago")
                        publish_time = video_renderer.get('publishedTimeText', {}).get('simpleText', 'Unknown')
                        
                        if video_id and title:
                            videos.append({
                                'id': video_id,
                                'title': title,
                                'views': views,
                                'duration': duration_text,
                                'published': publish_time,
                                'url': f'https://www.youtube.com/watch?v={video_id}'
                            })
        
    except Exception as e:
        logger.error(f"Error parsing video data: {e}")
    
    return videos


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
