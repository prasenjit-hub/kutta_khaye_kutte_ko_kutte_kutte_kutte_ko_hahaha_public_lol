"""
YouTube Video Downloader - HINDI ONLY VERSION using Cobalt API
Downloads videos with Hindi dubbed audio using self-hosted Cobalt (FREE, no cookies needed!)
"""
import requests
import os
import logging
import time
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Cobalt API URL from environment variable
COBALT_API_URL = os.environ.get("COBALT_API_URL", "")


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
    def download_with_cobalt(self, video_url: str, output_path: str) -> bool:
        """
        Download video using self-hosted Cobalt API with Hindi audio
        """
        if not COBALT_API_URL:
            logger.error("❌ COBALT_API_URL environment variable not set!")
            return False
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # Request body with Hindi audio preference
        payload = {
            "url": video_url,
            "videoQuality": "1080",
            "youtubeDubLang": "hi",  # Hindi dubbed audio!
            "youtubeVideoCodec": "h264",
            "filenameStyle": "basic",
        }
        
        try:
            logger.info(f"📡 Requesting from Cobalt API: {COBALT_API_URL}")
            response = requests.post(COBALT_API_URL, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"❌ Cobalt API error: {response.status_code}")
                logger.error(f"   Response: {response.text[:500]}")
                return False
            
            data = response.json()
            logger.info(f"📥 Cobalt response status: {data.get('status')}")
            
            # Check response status
            status = data.get("status")
            
            if status == "error":
                error_code = data.get("error", {}).get("code", "unknown")
                logger.error(f"❌ Cobalt error: {error_code}")
                return False
            
            if status == "redirect" or status == "tunnel":
                # Direct download URL
                download_url = data.get("url")
                if download_url:
                    logger.info(f"📥 Got download URL, downloading...")
                    return self.download_file(download_url, output_path)
            
            if status == "picker":
                # Multiple options available, pick the video
                picker = data.get("picker", [])
                for item in picker:
                    if item.get("type") == "video":
                        download_url = item.get("url")
                        if download_url:
                            logger.info(f"📥 Got video from picker, downloading...")
                            return self.download_file(download_url, output_path)
            
            if status == "stream":
                download_url = data.get("url")
                if download_url:
                    logger.info(f"📥 Got stream URL, downloading...")
                    return self.download_file(download_url, output_path)
            
            logger.error(f"❌ Unexpected Cobalt response: {data}")
            return False
            
        except requests.exceptions.Timeout:
            logger.error("❌ Cobalt API timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Cobalt API error: {e}")
            return False
    
    def download_file(self, url: str, output_path: str) -> bool:
        """Download file from URL with progress"""
        try:
            logger.info(f"📥 Downloading video file...")
            
            response = requests.get(url, stream=True, timeout=600)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            last_log = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress every 10%
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            if percent >= last_log + 10:
                                logger.info(f"   Progress: {percent}%")
                                last_log = percent
            
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            if file_size > 1000000:  # > 1MB means valid video
                logger.info(f"✅ Download complete: {output_path} ({file_size // 1024 // 1024} MB)")
                return True
            else:
                logger.error(f"❌ Downloaded file too small: {file_size} bytes")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return False
                
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return False
    
    def download_video(self, video_url: str, video_id: str, prefer_hindi: bool = True) -> Optional[str]:
        """
        Download video with Hindi audio using Cobalt API
        
        Args:
            video_url: YouTube video URL
            video_id: Video ID for filename
            prefer_hindi: Always True for this version
        
        Returns:
            Path to downloaded file or None if failed
        """
        output_path = os.path.join(self.download_dir, f"{video_id}.mp4")
        
        # Check if already downloaded
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000000:  # > 1MB means valid
                logger.info(f"✓ Video already downloaded: {output_path}")
                return output_path
            else:
                # Incomplete download, remove and retry
                os.remove(output_path)
        
        logger.info(f"🔍 Downloading with Hindi audio...")
        logger.info(f"📹 Video: {video_url}")
        
        # Try Cobalt API
        success = self.download_with_cobalt(video_url, output_path)
        
        if success and os.path.exists(output_path):
            return output_path
        else:
            logger.warning(f"⚠️ Could not download video with Hindi audio")
            return None


if __name__ == "__main__":
    # Test downloader
    downloader = VideoDownloader()
    
    # Test with a MrBeast video
    test_url = "https://www.youtube.com/watch?v=8bMh8azh3CY"
    result = downloader.download_video(test_url, "test_hindi_video")
    
    if result:
        print(f"\n✅ Downloaded successfully to: {result}")
    else:
        print("\n❌ Download failed")
