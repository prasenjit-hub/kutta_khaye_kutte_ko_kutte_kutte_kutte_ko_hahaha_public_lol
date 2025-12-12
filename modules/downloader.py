"""
YouTube Video Downloader - HINDI ONLY VERSION
Downloads videos in 1080p with ONLY Hindi audio using yt-dlp
Uses --remote-components for proper YouTube extraction on servers
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
    
    def download_video(self, video_url: str, video_id: str, prefer_hindi: bool = True) -> Optional[str]:
        """
        Download video in 1080p with ONLY Hindi audio
        Uses yt-dlp command line with --remote-components for proper extraction
        
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
            logger.info(f"Video already downloaded: {output_path}")
            return output_path
        
        logger.info(f"🔍 Checking for Hindi audio availability...")
        logger.info(f"📥 Downloading video with HINDI audio only: {video_url}")
        
        # Build yt-dlp command
        # Using command line instead of Python API for better --remote-components support
        cmd = [
            'yt-dlp',
            '--remote-components', 'ejs:github',  # Enable JS challenge solving
            '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi]/bestvideo[height<=1080]+bestaudio[language=hi]',
            '--merge-output-format', 'mp4',
            '-o', output_path,
            '--no-warnings',
        ]
        
        # Add cookies if available
        if os.path.exists('youtube_cookies.txt'):
            logger.info("🍪 Using YouTube cookies for authentication")
            cmd.extend(['--cookies', 'youtube_cookies.txt'])
        else:
            logger.info("ℹ️ No cookies file found")
        
        cmd.append(video_url)
        
        try:
            logger.info(f"Running: {' '.join(cmd[:5])}...")  # Log partial command
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    logger.info(f"✅ Download complete (Hindi): {output_path}")
                    return output_path
                else:
                    logger.error("❌ Download seemed successful but file not found")
                    return None
            else:
                stderr = result.stderr.lower()
                
                # Check if it's a "format not available" error (no Hindi)
                if 'requested format is not available' in stderr or 'no video formats found' in stderr:
                    logger.warning(f"⚠️ Hindi audio NOT AVAILABLE for this video. Skipping...")
                    return None
                elif 'sign in to confirm' in stderr:
                    logger.error("❌ Cookies invalid or expired. Please refresh cookies.")
                    return None
                else:
                    logger.error(f"❌ Download failed: {result.stderr[:500]}")
                    return None
                    
        except subprocess.TimeoutExpired:
            logger.error("❌ Download timed out (10 minutes)")
            return None
        except Exception as e:
            logger.error(f"❌ Error downloading video: {e}")
            return None


if __name__ == "__main__":
    # Test downloader - Hindi only
    downloader = VideoDownloader()
    
    # Test with a MrBeast video
    test_url = "https://www.youtube.com/watch?v=8bMh8azh3CY"
    result = downloader.download_video(test_url, "test_hindi_video")
    
    if result:
        print(f"\n✅ Downloaded successfully (Hindi audio) to: {result}")
    else:
        print("\n❌ Download failed - Hindi audio not available or error occurred")
