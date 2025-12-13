"""
YouTube Video Downloader - HINDI ONLY VERSION
Downloads videos in 1080p with ONLY Hindi audio using yt-dlp
Automatically generates cookies using Playwright if needed
"""
import yt_dlp
import os
import logging
import subprocess
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.cookies_generated = False
    
    def ensure_cookies(self):
        """Generate cookies if not present or if they might be stale"""
        cookie_file = "youtube_cookies.txt"
        
        # Check if cookies file exists and is recent (less than 6 hours old)
        if os.path.exists(cookie_file):
            import time
            file_age = time.time() - os.path.getmtime(cookie_file)
            if file_age < 6 * 3600:  # 6 hours
                logger.info("🍪 Using existing cookies (less than 6 hours old)")
                return True
        
        # Generate new cookies
        logger.info("🔄 Generating fresh cookies...")
        try:
            from modules.cookie_generator import run_cookie_generator
            success = run_cookie_generator()
            if success:
                logger.info("✅ Fresh cookies generated!")
                self.cookies_generated = True
                return True
            else:
                logger.error("❌ Cookie generation failed")
                return False
        except Exception as e:
            logger.error(f"❌ Cookie generator error: {e}")
            return False
    
    def download_video(self, video_url: str, video_id: str, prefer_hindi: bool = True) -> Optional[str]:
        """
        Download video in 1080p with ONLY Hindi audio
        
        Args:
            video_url: YouTube video URL
            video_id: Video ID for filename
            prefer_hindi: Must be True for this Hindi-only version
        
        Returns:
            Path to downloaded file or None if Hindi audio not available
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Check if already downloaded
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000000:  # > 1MB
                logger.info(f"Video already downloaded: {output_path}")
                return output_path
            else:
                os.remove(output_path)  # Remove incomplete file
        
        # Ensure we have valid cookies
        if not self.ensure_cookies():
            logger.error("❌ Cannot proceed without valid cookies")
            return None
        
        logger.info(f"🔍 Checking for Hindi audio availability...")
        logger.info(f"📥 Downloading video with HINDI audio only: {video_url}")
        
        # yt-dlp options for Hindi audio
        ydl_opts = {
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi]/bestvideo[height<=1080]+bestaudio[language=hi]',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'cookiefile': 'youtube_cookies.txt',
            'quiet': False,
            'no_warnings': False,
            'logger': logger,
            'progress_hooks': [self._progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists(output_path):
                logger.info(f"✅ Successfully downloaded with HINDI audio!")
                logger.info(f"✅ Download complete (Hindi): {output_path}")
                return output_path
            else:
                logger.error("❌ Download failed - file not found")
                return None
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            
            if 'requested format is not available' in error_msg:
                logger.warning(f"⚠️ Hindi audio NOT AVAILABLE for this video. Skipping...")
            elif 'sign in to confirm' in error_msg or 'cookies' in error_msg:
                logger.error("❌ Authentication failed - cookies may be invalid")
                # Try regenerating cookies
                if not self.cookies_generated:
                    logger.info("🔄 Attempting to regenerate cookies...")
                    if self.ensure_cookies():
                        # Retry download
                        return self.download_video(video_url, video_id, prefer_hindi)
            else:
                logger.error(f"❌ Download error: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error downloading video: {e}")
            return None
    
    def _progress_hook(self, d):
        """Progress callback for download status"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            logger.info(f"Downloading: {percent} at {speed} ETA: {eta}")
        elif d['status'] == 'finished':
            logger.info("Download finished, now merging...")


if __name__ == "__main__":
    # Test downloader
    downloader = VideoDownloader()
    
    # Test with a MrBeast video
    test_url = "https://www.youtube.com/watch?v=8bMh8azh3CY"
    result = downloader.download_video(test_url, "test_hindi_video")
    
    if result:
        print(f"\n✅ Downloaded successfully (Hindi audio) to: {result}")
    else:
        print("\n❌ Download failed - Hindi audio not available")
