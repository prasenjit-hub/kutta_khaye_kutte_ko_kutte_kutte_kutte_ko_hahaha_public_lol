"""
YouTube Video Downloader - HINDI ONLY VERSION
Uses yt-dlp with --remote-components for proper Hindi audio detection
Cookies from youtube_cookies.txt (decoded from secrets)
"""
import subprocess
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
    def download_video(self, video_url: str, video_id: str, prefer_hindi: bool = True) -> Optional[str]:
        """
        Download video with HINDI audio only using yt-dlp CLI
        Uses --remote-components ejs:github for proper YouTube extraction
        
        Args:
            video_url: YouTube video URL
            video_id: Video ID for filename
            prefer_hindi: Must be True for Hindi-only version
        
        Returns:
            Path to downloaded file or None if Hindi audio not available
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Check if already downloaded
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000000:  # > 1MB
                logger.info(f"✓ Video already downloaded: {output_path}")
                return output_path
            else:
                os.remove(output_path)  # Remove incomplete file
        
        logger.info(f"📥 Downloading video with HINDI audio: {video_url}")
        
        # Build yt-dlp command
        cmd = [
            'yt-dlp',
            '--remote-components', 'ejs:github',  # Enable JS challenge solving
            '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi]/bestvideo[height<=1080]+bestaudio[language=hi]',
            '--merge-output-format', 'mp4',
            '-o', output_path,
        ]
        
        # Add cookies if available
        if os.path.exists('youtube_cookies.txt'):
            logger.info("🍪 Using cookies for authentication")
            cmd.extend(['--cookies', 'youtube_cookies.txt'])
        else:
            logger.warning("⚠️ No cookies file found - may fail without authentication")
        
        cmd.append(video_url)
        
        try:
            logger.info(f"Running yt-dlp with remote-components...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900  # 15 minute timeout
            )
            
            # Log output for debugging
            if result.stdout:
                for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                    if line.strip():
                        logger.info(f"  {line}")
            
            if result.returncode == 0:
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
                    logger.info(f"✅ Download complete (Hindi audio): {output_path}")
                    return output_path
                else:
                    logger.error("❌ Download seemed successful but file not found or too small")
                    return None
            else:
                stderr = result.stderr.lower() if result.stderr else ""
                
                # Check error type
                if 'requested format is not available' in stderr:
                    logger.warning(f"⚠️ Hindi audio NOT AVAILABLE for this video. Skipping...")
                elif 'sign in to confirm' in stderr:
                    logger.error("❌ Cookies expired or invalid. Please refresh cookies!")
                elif 'no video formats' in stderr:
                    logger.warning(f"⚠️ Could not extract video formats. Skipping...")
                else:
                    # Log the actual error
                    logger.error(f"❌ Download failed:")
                    for line in (result.stderr or "").split('\n')[-5:]:
                        if line.strip():
                            logger.error(f"  {line}")
                
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Download timed out (15 minutes)")
            return None
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None


if __name__ == "__main__":
    # Test downloader
    downloader = VideoDownloader()
    
    print("Testing yt-dlp availability...")
    result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ yt-dlp version: {result.stdout.strip()}")
    else:
        print("❌ yt-dlp not found")
