"""
YouTube Video Downloader with Gofile Cloud Storage
ALL AUTOMATIC ON GITHUB ACTIONS:
- No cloud_url: Download from YouTube → Upload to Gofile → Save URL
- cloud_url exists: Download from Gofile → Process
"""
import subprocess
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
        Download from YouTube with Hindi audio ONLY
        Uses cookies from secrets
        """
        logger.info(f"📥 Downloading from YouTube with HINDI audio...")
        
        if not os.path.exists('youtube_cookies.txt'):
            logger.error("❌ youtube_cookies.txt not found! Add YOUTUBE_COOKIES secret.")
            return False
        
        cmd = [
            'yt-dlp',
            '--cookies', 'youtube_cookies.txt',
            '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi]/bestvideo[height<=1080]+bestaudio[language=hi]',
            '--merge-output-format', 'mp4',
            '-o', output_path,
            video_url
        ]
        
        try:
            logger.info("🍪 Using cookies for authentication")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 1000000:
                    logger.info(f"✅ YouTube download complete: {output_path} ({file_size // 1024 // 1024} MB)")
                    return True
            
            # Check error
            if result.stderr:
                stderr = result.stderr.lower()
                if 'requested format' in stderr:
                    logger.warning("⚠️ Hindi audio not available for this video")
                elif 'sign in' in stderr:
                    logger.error("❌ Cookies expired! Please refresh YOUTUBE_COOKIES secret.")
                else:
                    logger.error(f"❌ Error: {result.stderr[-300:]}")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Download timed out (15 min)")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def upload_to_cloud(self, file_path: str) -> Optional[Dict]:
        """Upload to Gofile cloud storage"""
        logger.info(f"☁️ Uploading to Gofile cloud storage...")
        return self.cloud.upload_file(file_path)
    
    def download_from_cloud(self, gofile_url: str, output_path: str) -> bool:
        """Download from Gofile cloud storage"""
        logger.info(f"☁️ Downloading from Gofile: {gofile_url}")
        return self.cloud.download_file(gofile_url, output_path)
    
    def download_video(self, video_url: str, video_id: str, cloud_url: str = None) -> tuple:
        """
        Download video for processing
        Returns: (video_path, cloud_url) - cloud_url may be new if just uploaded
        
        Logic:
        1. If cloud_url exists → Download from Gofile
        2. If no cloud_url → Download from YouTube → Upload to Gofile → Return new URL
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        new_cloud_url = cloud_url  # Will be updated if we upload new
        
        # Check if already exists locally
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
            logger.info(f"✓ Video already exists locally: {output_path}")
            return output_path, new_cloud_url
        
        # If cloud_url exists, download from Gofile
        if cloud_url:
            logger.info(f"☁️ Cloud URL exists, downloading from Gofile...")
            if self.download_from_cloud(cloud_url, output_path):
                return output_path, cloud_url
            else:
                logger.error("❌ Failed to download from Gofile!")
                return None, cloud_url
        
        # No cloud_url - need to download from YouTube and upload to Gofile
        logger.info(f"📺 No cloud URL - downloading from YouTube first...")
        
        if not self.download_from_youtube(video_url, output_path):
            logger.error("❌ Failed to download from YouTube")
            return None, None
        
        # Upload to Gofile for future runs
        logger.info(f"☁️ Uploading to Gofile for future runs...")
        cloud_info = self.upload_to_cloud(output_path)
        
        if cloud_info:
            new_cloud_url = cloud_info.get('download_page')
            logger.info(f"✅ Uploaded to Gofile: {new_cloud_url}")
        else:
            logger.warning("⚠️ Failed to upload to Gofile, but local file exists")
        
        return output_path, new_cloud_url


if __name__ == "__main__":
    print("Testing connections...")
    downloader = VideoDownloader()
    
    # Test Gofile
    server = downloader.cloud.get_best_server()
    print(f"Gofile: {server}" if server else "Gofile: Failed")
    
    # Test cookies
    if os.path.exists('youtube_cookies.txt'):
        print("Cookies: Found")
    else:
        print("Cookies: Not found")
