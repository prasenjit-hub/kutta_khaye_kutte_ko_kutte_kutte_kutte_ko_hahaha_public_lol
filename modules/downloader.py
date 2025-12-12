"""
YouTube Video Downloader - HINDI ONLY VERSION
Downloads videos in 1080p with ONLY Hindi audio using yt-dlp
NO FALLBACK to English - if Hindi not available, skip the video
"""
import yt_dlp
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
    def check_hindi_audio_available(self, video_url: str) -> bool:
        """
        Check if Hindi audio track is available for the video
        Returns True if Hindi audio exists, False otherwise
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        # Add cookies if available
        if os.path.exists('youtube_cookies.txt'):
            ydl_opts['cookiefile'] = 'youtube_cookies.txt'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # Check for Hindi audio in formats
                formats = info.get('formats', [])
                for fmt in formats:
                    lang = fmt.get('language', '')
                    if lang == 'hi':
                        return True
                
                # Also check requested_formats
                requested = info.get('requested_formats', [])
                for fmt in requested:
                    lang = fmt.get('language', '')
                    if lang == 'hi':
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error checking Hindi audio: {e}")
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
            logger.info(f"Video already downloaded: {output_path}")
            return output_path
        
        # HINDI ONLY - No fallback to English!
        # First check if Hindi audio is available
        logger.info(f"🔍 Checking for Hindi audio availability...")
        
        # Format string for HINDI ONLY - will FAIL if Hindi not available
        # This is intentional - we don't want English fallback
        format_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[language=hi][ext=m4a]/bestvideo[height<=1080]+bestaudio[language=hi]'
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
            'logger': logger,
            'progress_hooks': [self._progress_hook],
            'postprocessor_args': ['-c:a', 'aac'],
        }
        
        try:
            logger.info(f"📥 Downloading video with HINDI audio only: {video_url}")
            
            # Check for cookies file (optional for public videos)
            if os.path.exists('youtube_cookies.txt'):
                logger.info("🍪 Using YouTube cookies for authentication")
                ydl_opts['cookiefile'] = 'youtube_cookies.txt'
            else:
                logger.info("ℹ️ No cookies file found, attempting without authentication")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Verify Hindi audio was actually downloaded
                if 'requested_formats' in info:
                    audio_format = info.get('requested_formats', [{}])[-1]
                    audio_lang = audio_format.get('language', 'unknown')
                    
                    if audio_lang == 'hi':
                        logger.info("✅ Successfully downloaded with HINDI audio!")
                    else:
                        # This shouldn't happen with our format string, but just in case
                        logger.error(f"❌ Expected Hindi audio but got: {audio_lang}")
                        # Delete the file since it's not Hindi
                        if os.path.exists(output_path):
                            os.remove(output_path)
                        return None
            
            if os.path.exists(output_path):
                logger.info(f"✅ Download complete (Hindi): {output_path}")
                return output_path
            else:
                logger.error("❌ Download failed - file not found")
                return None
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'language=hi' in error_msg or 'no suitable format' in error_msg.lower():
                logger.warning(f"⚠️ Hindi audio NOT AVAILABLE for this video. Skipping...")
                logger.warning(f"   Video: {video_url}")
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
    # Test downloader - Hindi only
    downloader = VideoDownloader()
    
    # Test with a MrBeast video (should have Hindi audio after March 2019)
    test_url = "https://www.youtube.com/watch?v=8bMh8azh3CY"
    result = downloader.download_video(test_url, "test_hindi_video")
    
    if result:
        print(f"\n✅ Downloaded successfully (Hindi audio) to: {result}")
    else:
        print("\n❌ Download failed - Hindi audio not available")
