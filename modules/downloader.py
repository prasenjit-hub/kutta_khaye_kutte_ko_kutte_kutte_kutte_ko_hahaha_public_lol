"""
YouTube Video Downloader - HINDI ONLY VERSION with Cloud Storage
Downloads videos with Hindi audio, uploads to Gofile for persistent storage
Subsequent runs download from Gofile (no YouTube auth needed!)
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
        """
        logger.info(f"📥 Downloading from YouTube with HINDI audio...")
        
        ydl_opts = {
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi]/bestvideo[height<=1080]+bestaudio[language=hi]',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
        }
        
        # Add cookies if available
        if os.path.exists('youtube_cookies.txt'):
            ydl_opts['cookiefile'] = 'youtube_cookies.txt'
            logger.info("🍪 Using cookies for YouTube download")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
                logger.info(f"✅ YouTube download complete: {output_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ YouTube download error: {e}")
            return False
    
    def upload_to_cloud(self, file_path: str) -> Optional[Dict]:
        """
        Upload downloaded video to Gofile for persistent storage
        """
        logger.info(f"☁️ Uploading to cloud storage...")
        return self.cloud.upload_file(file_path)
    
    def download_from_cloud(self, gofile_url: str, output_path: str) -> bool:
        """
        Download video from Gofile cloud storage
        """
        logger.info(f"☁️ Downloading from cloud storage...")
        return self.cloud.download_file(gofile_url, output_path)
    
    def download_video(self, video_url: str, video_id: str, 
                       cloud_url: str = None, prefer_hindi: bool = True) -> Optional[str]:
        """
        Download video - from cloud if available, otherwise from YouTube
        
        Args:
            video_url: YouTube video URL
            video_id: Video ID for filename
            cloud_url: Gofile URL if already uploaded to cloud
            prefer_hindi: Always True for Hindi version
        
        Returns:
            Path to downloaded file or None if failed
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Check if already downloaded locally
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000000:  # > 1MB
                logger.info(f"✓ Video already exists locally: {output_path}")
                return output_path
            else:
                os.remove(output_path)  # Remove incomplete file
        
        # Try downloading from cloud first (if URL available)
        if cloud_url:
            logger.info(f"🌐 Cloud URL available, downloading from Gofile...")
            if self.download_from_cloud(cloud_url, output_path):
                return output_path
            else:
                logger.warning("⚠️ Cloud download failed, will try YouTube...")
        
        # Download from YouTube
        logger.info(f"📺 Downloading from YouTube: {video_url}")
        if self.download_from_youtube(video_url, output_path):
            return output_path
        
        logger.error(f"❌ Could not download video")
        return None
    
    def download_and_upload_to_cloud(self, video_url: str, video_id: str) -> Optional[Dict]:
        """
        Download from YouTube and upload to cloud storage
        Returns cloud storage info (URL, file_id, etc.)
        
        Args:
            video_url: YouTube video URL
            video_id: Video ID for filename
        
        Returns:
            Dict with cloud storage info or None if failed
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Download from YouTube
        if not self.download_from_youtube(video_url, output_path):
            return None
        
        # Upload to cloud
        cloud_info = self.upload_to_cloud(output_path)
        
        if cloud_info:
            # Optionally delete local file to save space
            # os.remove(output_path)
            logger.info(f"✅ Video saved to cloud: {cloud_info.get('download_page')}")
        
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
