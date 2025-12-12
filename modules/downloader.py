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
    
    def get_ydl_opts(self):
        """Get base yt-dlp options with cookies if available"""
        opts = {
            'quiet': False,
            'no_warnings': False,
        }
        
        if os.path.exists('youtube_cookies.txt'):
            logger.info("🍪 Using YouTube cookies for authentication")
            opts['cookiefile'] = 'youtube_cookies.txt'
        else:
            logger.info("ℹ️ No cookies file found, attempting without authentication")
        
        return opts
    
    def find_hindi_audio_format(self, video_url: str) -> Optional[str]:
        """
        Check available formats and find Hindi audio format ID
        Returns format ID string or None if not available
        """
        ydl_opts = self.get_ydl_opts()
        ydl_opts['quiet'] = True
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                formats = info.get('formats', [])
                
                # Find Hindi audio formats
                hindi_audio_ids = []
                best_video_id = None
                best_video_height = 0
                
                for fmt in formats:
                    format_id = fmt.get('format_id', '')
                    language = fmt.get('language', '')
                    height = fmt.get('height', 0) or 0
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    
                    # Find Hindi audio
                    if language == 'hi' and acodec != 'none':
                        hindi_audio_ids.append(format_id)
                        logger.info(f"  Found Hindi audio: {format_id}")
                    
                    # Find best video (up to 1080p)
                    if vcodec != 'none' and height <= 1080 and height > best_video_height:
                        best_video_id = format_id
                        best_video_height = height
                
                if hindi_audio_ids and best_video_id:
                    # Return format: best_video + best_hindi_audio
                    format_str = f"{best_video_id}+{hindi_audio_ids[0]}"
                    logger.info(f"✅ Hindi audio available! Format: {format_str}")
                    return format_str
                elif hindi_audio_ids:
                    # Only audio, no suitable video found
                    logger.info(f"Found Hindi audio but no suitable video format")
                    return None
                else:
                    logger.warning("❌ No Hindi audio track found for this video")
                    return None
                    
        except Exception as e:
            logger.error(f"Error checking formats: {e}")
            return None
    
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
        
        logger.info(f"🔍 Checking for Hindi audio availability...")
        
        # First, find Hindi audio format
        format_str = self.find_hindi_audio_format(video_url)
        
        if not format_str:
            logger.warning(f"⚠️ Hindi audio NOT AVAILABLE for this video. Skipping...")
            return None
        
        # Download with the specific format
        ydl_opts = self.get_ydl_opts()
        ydl_opts.update({
            'format': format_str,
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'logger': logger,
            'progress_hooks': [self._progress_hook],
        })
        
        try:
            logger.info(f"📥 Downloading video with HINDI audio: {video_url}")
            logger.info(f"   Format: {format_str}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists(output_path):
                logger.info(f"✅ Download complete (Hindi): {output_path}")
                return output_path
            else:
                logger.error("❌ Download failed - file not found")
                return None
                
        except yt_dlp.utils.DownloadError as e:
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
