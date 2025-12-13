"""
YouTube Video Downloader - HINDI ONLY VERSION with Cloud Storage
For LOCAL batch download: Uses cookies file
For GitHub Actions: Uses cloud storage (Gofile)
"""
import yt_dlp
import os
import logging
from typing import Optional, Dict
from modules.cloud_storage import GofileStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.cloud = GofileStorage()
    
    def download_from_youtube(self, video_url: str, output_path: str) -> bool:
        """
        Download video from YouTube with Hindi audio using yt-dlp
        Requires youtube_cookies.txt to be present
        """
        logger.info(f"📥 Downloading from YouTube with HINDI audio...")
        
        # Check for cookies
        if not os.path.exists('youtube_cookies.txt'):
            logger.error("❌ youtube_cookies.txt not found!")
            logger.error("   Please export cookies from browser and save as youtube_cookies.txt")
            return False
        
        ydl_opts = {
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi]/bestvideo[height<=1080]+bestaudio[language=hi]',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'cookiefile': 'youtube_cookies.txt',
            'quiet': False,
            'no_warnings': False,
        }
        
        logger.info("🍪 Using cookies for YouTube download")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
                logger.info(f"✅ YouTube download complete: {output_path}")
                return True
            return False
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'sign in' in error_msg or 'bot' in error_msg:
                logger.error("❌ Cookies expired or invalid!")
                logger.error("   Please refresh cookies from browser")
            elif 'requested format' in error_msg:
                logger.error("❌ Hindi audio not available for this video")
            else:
                logger.error(f"❌ YouTube download error: {e}")
            return False
    
    def upload_to_cloud(self, file_path: str) -> Optional[Dict]:
        """Upload downloaded video to Gofile for persistent storage"""
        logger.info(f"☁️ Uploading to Gofile cloud storage...")
        return self.cloud.upload_file(file_path)
    
    def download_from_cloud(self, gofile_url: str, output_path: str) -> bool:
        """Download video from Gofile cloud storage"""
        logger.info(f"☁️ Downloading from Gofile: {gofile_url}")
        return self.cloud.download_file(gofile_url, output_path)
    
    def download_video(self, video_url: str, video_id: str, 
                       cloud_url: str = None, prefer_hindi: bool = True) -> Optional[str]:
        """
        Download video - from cloud if available, otherwise from YouTube
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Check if already downloaded locally
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000000:  # > 1MB
                logger.info(f"✓ Video already exists locally: {output_path}")
                return output_path
            else:
                os.remove(output_path)
        
        # Try downloading from cloud first (for GitHub Actions)
        if cloud_url:
            logger.info(f"🌐 Downloading from Gofile cloud...")
            if self.download_from_cloud(cloud_url, output_path):
                return output_path
            else:
                logger.warning("⚠️ Cloud download failed")
                return None
        
        # No cloud URL - need to download from YouTube (local only)
        logger.warning("⚠️ No cloud URL available")
        logger.warning("   Run batch_download.py locally to upload videos to cloud")
        return None
    
    def download_and_upload_to_cloud(self, video_url: str, video_id: str) -> Optional[Dict]:
        """
        Download from YouTube and upload to cloud storage
        Used by batch_download.py for local processing
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Download from YouTube
        if not self.download_from_youtube(video_url, output_path):
            return None
        
        # Upload to cloud
        cloud_info = self.upload_to_cloud(output_path)
        
        if cloud_info:
            logger.info(f"✅ Video saved to cloud: {cloud_info.get('download_page')}")
            # Delete local file to save space
            # os.remove(output_path)
        
        return cloud_info


if __name__ == "__main__":
    # Test downloader
    downloader = VideoDownloader()
    
    print("Testing Gofile connection...")
    server = downloader.cloud.get_best_server()
    if server:
        print(f"✅ Connected to Gofile server: {server}")
    else:
        print("❌ Could not connect to Gofile")
