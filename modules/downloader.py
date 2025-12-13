"""
YouTube Video Downloader - HINDI ONLY VERSION using Cobalt API
Downloads videos with Hindi dubbed audio using Cobalt (FREE, no cookies needed!)
"""
import requests
import os
import logging
import time
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cobalt API endpoints (try multiple in case one is down)
COBALT_APIS = [
    "https://api.cobalt.tools",
    "https://cobalt-api.kwiatekmiki.com",
    "https://cobalt.canine.tools",
]


class VideoDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.working_api = None
    
    def find_working_api(self) -> Optional[str]:
        """Find a working Cobalt API endpoint"""
        if self.working_api:
            return self.working_api
            
        for api in COBALT_APIS:
            try:
                # Test the API
                response = requests.get(api, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Found working Cobalt API: {api}")
                    self.working_api = api
                    return api
            except:
                continue
        
        logger.error("❌ No working Cobalt API found")
        return None
    
    def download_with_cobalt(self, video_url: str, output_path: str) -> bool:
        """
        Download video using Cobalt API with Hindi audio
        """
        api_base = self.find_working_api()
        if not api_base:
            return False
        
        api_url = f"{api_base}/"
        
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
            logger.info(f"📡 Requesting from Cobalt API...")
            response = requests.post(api_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                logger.error(f"❌ Cobalt API error: {response.status_code}")
                logger.error(f"   Response: {response.text[:500]}")
                return False
            
            data = response.json()
            
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
                    return self.download_file(download_url, output_path)
            
            if status == "picker":
                # Multiple options available, pick the video
                picker = data.get("picker", [])
                for item in picker:
                    if item.get("type") == "video":
                        download_url = item.get("url")
                        if download_url:
                            return self.download_file(download_url, output_path)
            
            if status == "stream":
                download_url = data.get("url")
                if download_url:
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
            logger.info(f"📥 Downloading video...")
            
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
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:  # > 1MB
                logger.info(f"✅ Download complete: {output_path}")
                return True
            else:
                logger.error("❌ Downloaded file too small or missing")
                return False
                
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
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
