"""
HuggingFace Cloud Storage Module
Uses HuggingFace Hub for reliable video storage (10GB free)
"""
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get HuggingFace token from environment
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_REPO_ID = os.environ.get("HF_REPO_ID", "")  # e.g., "username/mrbeast-videos-storage"


class HuggingFaceStorage:
    """
    HuggingFace Hub storage for videos
    - Reliable, 10GB free
    - Quality maintained
    - Easy delete when done
    """
    
    def __init__(self):
        self.token = HF_TOKEN
        self.repo_id = HF_REPO_ID
        self._api = None
    
    @property
    def api(self):
        """Lazy load HuggingFace API"""
        if self._api is None:
            try:
                from huggingface_hub import HfApi
                self._api = HfApi(token=self.token)
            except ImportError:
                logger.error("❌ huggingface_hub not installed. Run: pip install huggingface_hub")
                return None
        return self._api
    
    def is_configured(self) -> bool:
        """Check if HuggingFace is properly configured"""
        if not self.token:
            logger.warning("⚠️ HF_TOKEN not set")
            return False
        if not self.repo_id:
            logger.warning("⚠️ HF_REPO_ID not set")
            return False
        if not self.api:
            return False
        return True
    
    def upload_file(self, file_path: str, video_id: str) -> Optional[str]:
        """
        Upload a video file to HuggingFace
        
        Args:
            file_path: Local path to the video
            video_id: Video ID for naming in HF
        
        Returns:
            HuggingFace file path (repo_id/filename) or None on failure
        """
        if not self.is_configured():
            logger.error("❌ HuggingFace not configured!")
            return None
        
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return None
        
        file_size = os.path.getsize(file_path)
        logger.info(f"📤 Uploading to HuggingFace: {file_path} ({file_size // 1024 // 1024} MB)")
        
        try:
            # Upload file to HuggingFace repo
            hf_path = f"videos/{video_id}.mp4"
            
            self.api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=hf_path,
                repo_id=self.repo_id,
                repo_type="dataset",
                token=self.token
            )
            
            # Return the HuggingFace path
            hf_url = f"hf://{self.repo_id}/{hf_path}"
            logger.info(f"✅ Uploaded to HuggingFace: {hf_url}")
            return hf_url
            
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return None
    
    def download_file(self, hf_path: str, output_path: str) -> bool:
        """
        Download a video file from HuggingFace
        
        Args:
            hf_path: HuggingFace path (hf://repo_id/path)
            output_path: Local path to save
        
        Returns:
            True if successful
        """
        if not self.is_configured():
            logger.error("❌ HuggingFace not configured!")
            return False
        
        logger.info(f"📥 Downloading from HuggingFace: {hf_path}")
        
        try:
            from huggingface_hub import hf_hub_download
            
            # Parse the path
            # Format: hf://repo_id/path/to/file (where repo_id is User/Repo)
            if hf_path.startswith("hf://"):
                clean_path = hf_path[5:]
                # We expect User/Repo/Path...
                parts = clean_path.split("/")
                if len(parts) >= 3:
                     repo_id = f"{parts[0]}/{parts[1]}"
                     file_path = "/".join(parts[2:])
                else:
                     # Fallback if weird format
                     repo_id = self.repo_id
                     file_path = clean_path
            else:
                # Assume it's just the file path in default repo
                repo_id = self.repo_id
                file_path = hf_path
            
            # Download
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=file_path,
                repo_type="dataset",
                token=self.token,
                local_dir=os.path.dirname(output_path)
            )
            
            # Move to expected location if different
            if downloaded_path != output_path:
                import shutil
                shutil.move(downloaded_path, output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
                logger.info(f"✅ Downloaded: {output_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return False
    
    def delete_file(self, hf_path: str) -> bool:
        """
        Delete a video file from HuggingFace
        
        Args:
            hf_path: HuggingFace path to delete
        
        Returns:
            True if successful
        """
        if not self.is_configured():
            return False
        
        logger.info(f"🗑️ Deleting from HuggingFace: {hf_path}")
        
        try:
            # Parse the path
            if hf_path.startswith("hf://"):
                clean_path = hf_path[5:]
                parts = clean_path.split("/")
                if len(parts) >= 3:
                     repo_id = f"{parts[0]}/{parts[1]}"
                     file_path = "/".join(parts[2:])
                else:
                     repo_id = self.repo_id
                     file_path = clean_path
            else:
                repo_id = self.repo_id
                file_path = hf_path
            
            self.api.delete_file(
                path_in_repo=file_path,
                repo_id=repo_id,
                repo_type="dataset",
                token=self.token
            )
            
            logger.info(f"✅ Deleted from HuggingFace")
            return True
            
        except Exception as e:
            logger.error(f"❌ Delete error: {e}")
            return False


if __name__ == "__main__":
    print("Testing HuggingFace connection...")
    storage = HuggingFaceStorage()
    
    if storage.is_configured():
        print("✅ HuggingFace configured")
    else:
        print("❌ HuggingFace not configured")
        print("   Set HF_TOKEN and HF_REPO_ID environment variables")
