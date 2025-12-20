
import requests
import time
import logging
import os

logger = logging.getLogger(__name__)

class InstagramGraphUploader:
    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def upload_reel(self, video_url: str, caption: str) -> str:
        """
        Uploads a Reel to Instagram using the Graph API.
        
        Args:
            video_url (str): Publicly accessible URL of the video (e.g. HuggingFace link)
            caption (str): Caption for the Reel
            
        Returns:
            str: Media ID if successful, None otherwise
        """
        if not self.access_token or not self.account_id:
            logger.error("❌ Instagram credentials missing")
            return None
            
        # 1. Create Media Container
        logger.info("📸 Creating Instagram Media Container...")
        container_url = f"{self.base_url}/{self.account_id}/media"
        
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
            # Instagram takes time to download the video from the URL
            logger.info("⏳ Waiting for Instagram to process video...")
            status = "IN_PROGRESS"
            attempts = 0
            
            while status != "FINISHED" and attempts < 20:
                time.sleep(5)  # CHECK EVERY 5 SECONDS
                status_url = f"{self.base_url}/{container_id}"
                status_resp = requests.get(status_url, params={
                    "fields": "status_code",
                    "access_token": self.access_token
                })
                
                status_data = status_resp.json()
                status = status_data.get("status_code", "ERROR")
                
                if status == "ERROR":
                    logger.error("❌ Media processing failed on Instagram side")
                    return None
                    
                attempts += 1
                if attempts % 2 == 0:
                    logger.info(f"   Processing status: {status}...")
            
            if status != "FINISHED":
                logger.error("❌ Timeout waiting for media processing")
                return None
                
            # Step C: Publish Media
            logger.info("🚀 Publishing Reel...")
            publish_url = f"{self.base_url}/{self.account_id}/media_publish"
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
                logger.error(f"❌ Publish Error: {pub_resp.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Instagram API Exception: {e}")
            return None
