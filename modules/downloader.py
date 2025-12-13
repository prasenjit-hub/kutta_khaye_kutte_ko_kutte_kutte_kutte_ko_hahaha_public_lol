"""
YouTube Video Downloader with HuggingFace Cloud Storage
- Downloads from YouTube with Hindi audio
- Uploads to HuggingFace (10GB free, reliable)
- Downloads from HuggingFace for processing
- Deletes from HuggingFace when video complete
"""
import subprocess
import os
import logging
import json
from typing import Optional, Tuple
from modules.cloud_storage import HuggingFaceStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.cloud = HuggingFaceStorage()
    
    def get_hindi_audio_format(self, video_url: str) -> Optional[str]:
        """
        Find Hindi audio format ID from video
        Returns format ID like '251-7' for Hindi audio
        """
        logger.info("🔍 Checking for Hindi audio track...")
        
        cmd = [
            'yt-dlp',
            '--cookies', 'youtube_cookies.txt',
            '-J',  # JSON output
            '--no-download',
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Could not get video info: {result.stderr[-200:]}")
                return None
            
            data = json.loads(result.stdout)
            formats = data.get('formats', [])
            
            # Find Hindi audio format
            hindi_audio_id = None
            for fmt in formats:
                lang = fmt.get('language') or ''
                if lang.lower() in ['hi', 'hin', 'hindi']:
                    if fmt.get('acodec') != 'none':  # Is audio
                        hindi_audio_id = fmt.get('format_id')
                        logger.info(f"✅ Found Hindi audio: format_id={hindi_audio_id}")
                        break
            
            if not hindi_audio_id:
                logger.warning("⚠️ No Hindi audio track found in this video")
                return None
            
            return hindi_audio_id
            
        except json.JSONDecodeError:
            logger.error("❌ Failed to parse video info")
            return None
        except Exception as e:
            logger.error(f"❌ Error checking formats: {e}")
            return None
    
    def download_from_youtube(self, video_url: str, output_path: str) -> bool:
        """
        Download from YouTube with Hindi audio ONLY
        First checks if Hindi audio exists, then downloads
        """
        logger.info(f"📥 Downloading from YouTube with HINDI audio...")
        
        if not os.path.exists('youtube_cookies.txt'):
            logger.error("❌ youtube_cookies.txt not found! Add YOUTUBE_COOKIES secret.")
            return False
        
        logger.info("🍪 Using cookies for authentication")
        
        # First, find Hindi audio format
        hindi_format = self.get_hindi_audio_format(video_url)
        
        if not hindi_format:
            logger.warning("⚠️ Hindi audio not available - skipping this video")
            return False
        
        # Build format string with specific Hindi audio
        format_str = f'bestvideo[height<=1080][ext=mp4]+{hindi_format}/bestvideo[height<=1080]+{hindi_format}'
        
        cmd = [
            'yt-dlp',
            '--cookies', 'youtube_cookies.txt',
            '-f', format_str,
            '--merge-output-format', 'mp4',
            '-o', output_path,
            video_url
        ]
        
        try:
            logger.info(f"📥 Downloading with Hindi audio (format: {hindi_format})...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 1000000:
                    logger.info(f"✅ Download complete: {output_path} ({file_size // 1024 // 1024} MB)")
                    return True
            
            # Check error
            if result.stderr:
                stderr = result.stderr.lower()
                if 'sign in' in stderr:
                    logger.error("❌ Cookies expired! Please refresh YOUTUBE_COOKIES secret.")
                else:
                    logger.error(f"❌ Download error: {result.stderr[-300:]}")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Download timed out (15 min)")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def upload_to_cloud(self, file_path: str, video_id: str) -> Optional[str]:
        """Upload to HuggingFace cloud storage"""
        if not self.cloud.is_configured():
            logger.warning("⚠️ HuggingFace not configured, skipping cloud upload")
            return None
        return self.cloud.upload_file(file_path, video_id)
    
    def download_from_cloud(self, cloud_url: str, output_path: str) -> bool:
        """Download from HuggingFace cloud storage"""
        if not self.cloud.is_configured():
            logger.warning("⚠️ HuggingFace not configured")
            return False
        return self.cloud.download_file(cloud_url, output_path)
    
    def delete_from_cloud(self, cloud_url: str) -> bool:
        """Delete from HuggingFace when video is complete"""
        if not self.cloud.is_configured():
            return False
        return self.cloud.delete_file(cloud_url)
    
    def download_video(self, video_url: str, video_id: str, cloud_url: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Download video for processing
        Returns: (video_path, cloud_url) - cloud_url may be new if just uploaded
        
        Logic:
        1. If cloud_url exists → Download from HuggingFace
        2. If no cloud_url → Download from YouTube → Upload to HuggingFace → Return new URL
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        new_cloud_url = cloud_url
        
        # Check if already exists locally
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
            logger.info(f"✓ Video already exists locally: {output_path}")
            return output_path, new_cloud_url
        
        # If cloud_url exists, download from HuggingFace
        if cloud_url:
            logger.info(f"☁️ Cloud URL exists, downloading from HuggingFace...")
            if self.download_from_cloud(cloud_url, output_path):
                return output_path, cloud_url
            else:
                logger.warning("⚠️ Failed to download from HuggingFace, trying YouTube...")
        
        # Download from YouTube
        logger.info(f"📺 Downloading from YouTube...")
        if not self.download_from_youtube(video_url, output_path):
            logger.error("❌ Failed to download from YouTube")
            return None, None
        
        # Upload to HuggingFace for future runs
        if self.cloud.is_configured():
            logger.info(f"☁️ Uploading to HuggingFace for future runs...")
            new_cloud_url = self.upload_to_cloud(output_path, video_id)
            if new_cloud_url:
                logger.info(f"✅ Uploaded to HuggingFace: {new_cloud_url}")
        else:
            logger.info("ℹ️ HuggingFace not configured, video will be re-downloaded next run")
        
        return output_path, new_cloud_url


if __name__ == "__main__":
    print("Testing connections...")
    downloader = VideoDownloader()
    
    # Test HuggingFace
    if downloader.cloud.is_configured():
        print("✅ HuggingFace configured")
    else:
        print("⚠️ HuggingFace not configured (optional)")
    
    # Test cookies
    if os.path.exists('youtube_cookies.txt'):
        print("✅ Cookies file found")
    else:
        print("⚠️ Cookies file not found")
