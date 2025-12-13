"""
Gofile.io Cloud Storage Module
Free cloud storage for temporary video storage
No account required for basic uploads!
"""
import requests
import os
import logging
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GofileStorage:
    """
    Gofile.io cloud storage handler
    - Upload videos after downloading from YouTube
    - Download for processing
    - Delete when all parts are uploaded
    """
    
    def __init__(self):
        self.api_base = "https://api.gofile.io"
    
    def get_best_server(self) -> Optional[str]:
        """Get the best available server for upload"""
        try:
            response = requests.get(f"{self.api_base}/servers", timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                servers = data.get("data", {}).get("servers", [])
                if servers:
                    # Return first available server
                    server = servers[0].get("name")
                    logger.info(f"📡 Using Gofile server: {server}")
                    return server
            
            logger.error("❌ Could not get Gofile server")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Gofile server: {e}")
            return None
    
    def upload_file(self, file_path: str) -> Optional[Dict]:
        """
        Upload a file to Gofile.io
        
        Args:
            file_path: Path to the file to upload
        
        Returns:
            Dict with downloadPage, fileId, fileName, etc. or None on failure
        """
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return None
        
        # Get best server
        server = self.get_best_server()
        if not server:
            return None
        
        upload_url = f"https://{server}.gofile.io/contents/uploadfile"
        
        file_size = os.path.getsize(file_path)
        logger.info(f"📤 Uploading to Gofile: {file_path} ({file_size // 1024 // 1024} MB)")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(upload_url, files=files, timeout=600)
            
            data = response.json()
            
            if data.get("status") == "ok":
                file_data = data.get("data", {})
                download_page = file_data.get("downloadPage")
                file_id = file_data.get("fileId")
                direct_link = file_data.get("directLink") or file_data.get("link")
                
                logger.info(f"✅ Upload successful!")
                logger.info(f"   File ID: {file_id}")
                logger.info(f"   Download page: {download_page}")
                
                return {
                    "file_id": file_id,
                    "download_page": download_page,
                    "direct_link": direct_link,
                    "file_name": file_data.get("fileName"),
                    "parent_folder": file_data.get("parentFolder"),
                }
            else:
                logger.error(f"❌ Upload failed: {data}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return None
    
    def get_download_link(self, download_page: str) -> Optional[str]:
        """
        Get direct download link from Gofile download page
        Note: Gofile requires token for direct downloads, so we use content API
        """
        try:
            # Extract content ID from download page URL
            # URL format: https://gofile.io/d/CONTENT_ID
            content_id = download_page.split("/d/")[-1] if "/d/" in download_page else None
            
            if not content_id:
                logger.error(f"❌ Invalid download page URL: {download_page}")
                return None
            
            # Get content info
            response = requests.get(
                f"{self.api_base}/contents/{content_id}",
                params={"wt": "4fd6sg89d7s6"},  # Guest token
                timeout=30
            )
            
            data = response.json()
            
            if data.get("status") == "ok":
                contents = data.get("data", {}).get("children", {})
                if contents:
                    # Get first file's direct link
                    for file_id, file_info in contents.items():
                        link = file_info.get("link")
                        if link:
                            logger.info(f"✅ Got download link for {file_info.get('name')}")
                            return link
            
            logger.error(f"❌ Could not get download link: {data}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting download link: {e}")
            return None
    
    def download_file(self, download_page: str, output_path: str) -> bool:
        """
        Download a file from Gofile
        
        Args:
            download_page: Gofile download page URL
            output_path: Where to save the file
        
        Returns:
            True if successful, False otherwise
        """
        direct_link = self.get_download_link(download_page)
        
        if not direct_link:
            logger.error("❌ Could not get direct download link")
            return False
        
        logger.info(f"📥 Downloading from Gofile...")
        
        try:
            response = requests.get(
                direct_link,
                stream=True,
                timeout=600,
                headers={"Cookie": "accountToken=guest"}
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            last_log = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            if percent >= last_log + 10:
                                logger.info(f"   Progress: {percent}%")
                                last_log = percent
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
                logger.info(f"✅ Download complete: {output_path}")
                return True
            else:
                logger.error("❌ Downloaded file too small or missing")
                return False
                
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return False
    
    def delete_file(self, content_id: str) -> bool:
        """
        Delete a file/folder from Gofile
        Note: Requires account token for deletion
        For guest uploads, files auto-delete after inactivity
        """
        logger.info(f"🗑️ File {content_id} will be auto-deleted by Gofile after inactivity")
        return True


if __name__ == "__main__":
    # Test Gofile
    storage = GofileStorage()
    
    # Test get server
    server = storage.get_best_server()
    print(f"Best server: {server}")
