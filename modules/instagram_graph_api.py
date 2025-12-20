
import requests
import time
import logging
import os

logger = logging.getLogger(__name__)

class MetaGraphUploader:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.video_base_url = "https://graph-video.facebook.com/v18.0"
        
    def upload_instagram_reel(self, account_id: str, video_url: str, caption: str) -> str:
        """
        Uploads a Reel to Instagram
        """
        if not self.access_token or not account_id:
            logger.error("❌ Instagram credentials missing")
            return None
            
        # 1. Create Media Container
        logger.info("📸 Creating Instagram Media Container...")
        container_url = f"{self.base_url}/{account_id}/media"
        
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        try:
            # Step A: Initialize Upload
            resp = requests.post(container_url, data=payload)
            if resp.status_code != 200:
                logger.error(f"❌ Instagram Container Error: {resp.text}")
                return None
                
            container_id = resp.json().get("id")
            logger.info(f"   Container ID: {container_id}")
            
            # Step B: Wait for Status = FINISHED
            if not self._wait_for_processing(container_id):
                return None
                
            # Step C: Publish Media
            logger.info("🚀 Publishing Instagram Reel...")
            publish_url = f"{self.base_url}/{account_id}/media_publish"
            publish_payload = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            pub_resp = requests.post(publish_url, data=publish_payload)
            if pub_resp.status_code == 200:
                media_id = pub_resp.json().get("id")
                logger.info(f"✅ Instagram Reel Published! ID: {media_id}")
                return media_id
            else:
                logger.error(f"❌ Instagram Publish Error: {pub_resp.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Instagram API Exception: {e}")
            return None

    def upload_facebook_reel(self, page_id: str, video_url: str, description: str) -> str:
        """
        Uploads a Reel to Facebook Page
        """
        if not self.access_token or not page_id:
            logger.error("❌ Facebook credentials missing")
            return None
            
        logger.info(f"📘 Starting Facebook Reel Upload to Page {page_id}...")
        
        # Facebook Video API Endpoint
        url = f"{self.video_base_url}/{page_id}/videos"
        
        payload = {
            "file_url": video_url,
            "description": description,
            "access_token": self.access_token
        }
        
        try:
            resp = requests.post(url, data=payload)
            if resp.status_code == 200:
                video_id = resp.json().get("id")
                logger.info(f"✅ Facebook Reel Published! ID: {video_id}")
                return video_id
            else:
                logger.error(f"❌ Facebook Upload Error: {resp.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Facebook API Exception: {e}")
            return None

    def _wait_for_processing(self, container_id: str) -> bool:
        """Helper to wait for media processing"""
        logger.info("⏳ Waiting for media processing...")
        status = "IN_PROGRESS"
        attempts = 0
        
        while status != "FINISHED" and attempts < 20:
            time.sleep(5)
            status_url = f"{self.base_url}/{container_id}"
            status_resp = requests.get(status_url, params={
                "fields": "status_code",
                "access_token": self.access_token
            })
            
            status_data = status_resp.json()
            status = status_data.get("status_code", "ERROR")
            
            if status == "ERROR":
                logger.error("❌ Media processing failed")
                return False
                
            attempts += 1
            if attempts % 2 == 0:
                logger.info(f"   Processing status: {status}...")
        
        if status != "FINISHED":
            logger.error("❌ Timeout waiting for media processing")
            return False
        return True
