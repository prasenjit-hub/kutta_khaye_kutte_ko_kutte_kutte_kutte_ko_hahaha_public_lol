"""
YouTube to YouTube Shorts Automation
Main orchestration script - OPTIMIZED for incremental processing

Key Features:
- Cloud Sync Phase: Backups videos to HuggingFace (to avoid frequent YouTube downloads)
- Serial Processing: Processes one video at a time until completion
- Only processes segments that need to be uploaded
- Resumes from where it left off
- Tracks progress in tracking.json
"""
import argparse
import json
import os
import logging
import shutil
from datetime import datetime
from modules.scraper import get_channel_videos
from modules.downloader import VideoDownloader
from modules.splitter import VideoSplitter
from modules.editor import VideoEditor
from modules.youtube_uploader import YouTubeUploader
from modules.notifier import notify_cookies_needed, notify_all_videos_complete, notify_video_uploaded, notify_error

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YouTubeShortsAutomation:
    def __init__(self, config_path: str = 'config.json', tracking_path: str = 'tracking.json'):
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.tracking_path = tracking_path
        self.tracking = self._load_tracking()
        
        # Create directories
        for path in self.config['paths'].values():
            os.makedirs(path, exist_ok=True)
        
        # Initialize modules
        self.downloader = VideoDownloader(self.config['paths']['downloads'])
        self.splitter = VideoSplitter(self.config['paths']['processed'])
        self.editor = VideoEditor(self.config)
        
        # YouTube uploader (lazy init)
        self._uploader = None
        
        # Get limits from config
        self.max_uploads_per_run = self.config['video_settings'].get('max_uploads_per_run', 3)
        self.max_segments_per_video = self.config['video_settings'].get('max_segments_per_video', 10)
        self.segment_duration = self.config['video_settings'].get('segment_duration_seconds', 60)
    
    @property
    def uploader(self):
        """Lazy initialize uploader to avoid authentication on every run"""
        if self._uploader is None:
            credentials_file = self.config['youtube_upload']['credentials_file']
            self._uploader = YouTubeUploader(credentials_file)
        return self._uploader
    
    def _load_tracking(self) -> dict:
        """Load tracking database"""
        if os.path.exists(self.tracking_path):
            with open(self.tracking_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'channel_url': '', 'last_scrape': None, 'videos': {}}
    
    def _save_tracking(self):
        """Save tracking database"""
        with open(self.tracking_path, 'w', encoding='utf-8') as f:
            json.dump(self.tracking, f, indent=2, ensure_ascii=False)
    
    def scrape_channel(self, channel_url: str = None):
        """Scrape YouTube channel and update tracking (sorted by date - newest first)"""
        if channel_url is None:
            channel_url = self.config['youtube_channel']
        
        logger.info(f"Scraping channel: {channel_url}")
        videos = get_channel_videos(channel_url, sort_by='date')
        
        # Update tracking
        self.tracking['channel_url'] = channel_url
        self.tracking['last_scrape'] = datetime.now().isoformat()
        
        for video in videos:
            video_id = video['id']
            if video_id not in self.tracking['videos']:
                self.tracking['videos'][video_id] = {
                    'title': video['title'],
                    'views': video['views'],
                    'duration': video['duration'],
                    'published': video.get('published', 'Unknown'),
                    'url': video['url'],
                    'status': 'pending',
                    'parts_uploaded': [],
                    'total_parts': 0,
                    'youtube_video_ids': [],
                    'downloaded_at': None,
                    'last_upload': None,
                    'cloud_url': None  # HuggingFace cloud storage URL
                }
            else:
                # Update views and published date
                self.tracking['videos'][video_id]['views'] = video['views']
                self.tracking['videos'][video_id]['published'] = video.get('published', 'Unknown')
        
        self._save_tracking()
        logger.info(f"✓ Scraped {len(videos)} videos (sorted by date - newest first)")
        return videos
    
    def get_next_video_to_process(self) -> tuple:
        """
        Get the next video that needs processing.
        Priority: partial (resume) > pending (new)
        Returns: (video_id, video_data) or (None, None)
        """
        # First, look for partial videos (resume upload)
        for video_id, data in self.tracking['videos'].items():
            if data.get('status') == 'partial':
                logger.info(f"📌 Resuming partial video: {data['title']}")
                return video_id, data
        
        # Then, look for pending videos (new)
        for video_id, data in self.tracking['videos'].items():
            if data.get('status') == 'pending':
                logger.info(f"📌 Starting new video: {data['title']}")
                return video_id, data
        
        logger.info("✅ All videos completed!")
        return None, None
    
    def run_full_automation(self):
        """
        Run complete automation pipeline - DUAL PHASE
        
        Phase 1: Cloud Sync (Backup assets to HuggingFace)
        Phase 2: Serial Processing (Process 1 video)
        """
        logger.info("=" * 60)
        logger.info("=== Starting Full Automation (Cloud Sync + Processing) ===")
        logger.info("=" * 60)
        
        # 1. Scrape channel for latest videos
        self.scrape_channel()
        
        # --- PHASE 1: CLOUD SYNC ---
        logger.info("\n" + "=" * 40)
        logger.info("=== PHASE 1: CLOUD SYNC ===")
        logger.info("=" * 40)
        
        # Find videos needing sync (pending/partial but no cloud_url)
        videos_to_sync = []
        for vid_id, data in self.tracking['videos'].items():
            if data['status'] in ['pending', 'partial'] and not data.get('cloud_url'):
                videos_to_sync.append((vid_id, data))
        
        # Sync up to 5 per run to respect execution time limits
        MAX_SYNC_PER_RUN = 5
        
        if not videos_to_sync:
            logger.info("✅ All current videos are backed up to Cloud!")
        else:
            logger.info(f"🔍 Found {len(videos_to_sync)} videos needing sync. Syncing top {MAX_SYNC_PER_RUN}...")
            
            for i, (video_id, video_data) in enumerate(videos_to_sync[:MAX_SYNC_PER_RUN]):
                logger.info(f"\n☁️ Syncing {i+1}/{MAX_SYNC_PER_RUN}: {video_data['title'][:50]}...")
                
                # Fetch video: If no cloud_url, downloader will: YouTube -> Download -> Upload -> Return New URL
                # We force cloud_url=None to trigger the download/upload flow
                _, new_cloud_url = self.downloader.download_video(
                    video_data['url'],
                    video_id,
                    cloud_url=None 
                )
                
                if new_cloud_url:
                    self.tracking['videos'][video_id]['cloud_url'] = new_cloud_url
                    self._save_tracking()
                    
                    # Immediate cleanup of local file to save space
                    local_path = os.path.join(self.config['paths']['downloads'], f"{video_id}.mp4")
                    if os.path.exists(local_path):
                        try:
                            os.remove(local_path)
                            logger.info("🗑️ Cleared local temp file")
                        except:
                            pass
                else:
                     logger.warning(f"⚠️ Failed to sync {video_id}. Will retry next run.")

        logger.info("\n✅ Phase 1 Complete.")
        
        # --- PHASE 2: PROCESSING ---
        logger.info("\n" + "=" * 40)
        logger.info("=== PHASE 2: PROCESSING SHORTS ===")
        logger.info("=" * 40)
        
        # Find next video to process
        video_id, video_data = self.get_next_video_to_process()
        
        if not video_id:
            logger.info("🎉 All videos processed! No more videos to upload!")
            try:
                notify_all_videos_complete()
            except:
                pass
            return
        
        self.process_video_for_shorts(video_id, video_data)

    def process_video_for_shorts(self, video_id, video_data):
        """Process a single video: Download (Cloud) -> Split -> Edit -> Upload"""
        logger.info(f"\n📹 Processing Target: {video_data['title']}")
        logger.info(f"   Status: {video_data.get('status')}")
        logger.info(f"   Parts uploaded: {video_data.get('parts_uploaded', [])}")
        logger.info(f"   Cloud URL: {video_data.get('cloud_url', 'Not uploaded yet')}")
        
        # A. DOWNLOAD (Ideally from Cloud now)
        video_path = os.path.join(self.config['paths']['downloads'], f"{video_id}.mp4")
        cloud_url = video_data.get('cloud_url')
        
        if not os.path.exists(video_path) or os.path.getsize(video_path) < 1000000:
            logger.info(f"\n📥 Downloading video for processing...")
            
            video_path, new_cloud_url = self.downloader.download_video(
                video_data['url'],
                video_id,
                cloud_url=cloud_url
            )
            
            # If we got a new URL (fallback happened), save it
            if new_cloud_url and new_cloud_url != cloud_url:
                self.tracking['videos'][video_id]['cloud_url'] = new_cloud_url
                self._save_tracking()
            
            if not video_path or not os.path.exists(video_path):
                logger.warning("⚠️ Could not download video for processing!")
                logger.warning("   Stopping automation. Check logs.")
                
                try:
                    from modules.notifier import notify_download_failed
                    notify_download_failed(video_data['title'], "Download failed during processing phase")
                except:
                    pass
                
                self.tracking['videos'][video_id]['status'] = 'download_failed'
                self._save_tracking()
                return # Stop here
        else:
            logger.info(f"✓ Video already locally available: {video_path}")
        
        # B. ANALYZE & SPLIT
        parts_already_uploaded = video_data.get('parts_uploaded', [])
        next_part_to_upload = max(parts_already_uploaded) + 1 if parts_already_uploaded else 1
        
        from modules.splitter import get_video_duration
        try:
             total_duration = get_video_duration(video_path)
             # Calculate total parts
             total_possible_parts = int(total_duration / self.segment_duration)
             if total_duration % self.segment_duration >= 10:
                 total_possible_parts += 1
             
             total_parts = min(total_possible_parts, self.max_segments_per_video)
        except Exception as e:
             logger.error(f"❌ Error calculating duration: {e}")
             total_parts = self.max_segments_per_video # Fallback
        
        logger.info(f"\n📊 Video Analysis:")
        logger.info(f"   Total duration: {total_duration:.2f}s")
        logger.info(f"   Total parts: {total_parts}")
        logger.info(f"   Next part: {next_part_to_upload}")
        
        # Check Completion
        if next_part_to_upload > total_parts:
            logger.info(f"✅ Video complete! Cleaning up...")
            self.tracking['videos'][video_id]['status'] = 'completed'
            
            # Delete local
            if os.path.exists(video_path):
                os.remove(video_path)
            
            # Delete from cloud (HuggingFace) to free space - OPTIONAL since user has 100GB
            # User said "jabtam sare video part part me upload kerna khatam na hojaye"
            # It implies we delete AFTER processing is done.
            cloud_url = video_data.get('cloud_url')
            if cloud_url:
                logger.info(f"🗑️ Deleting from cloud storage (Video Complete)...")
                self.downloader.delete_from_cloud(cloud_url)
                self.tracking['videos'][video_id]['cloud_url'] = None
            
            self._save_tracking()
            
            # Recursively start next video?
            # User: "jab 1 video ke sare part upload hona khatam hojaye tab dusre video pe jayenge"
            # So yes, we should start the next one.
            logger.info("➡️ Moving to next video...")
            return self.run_full_automation()

        # C. PROCESS SEGMENTS
        parts_to_process = []
        for part_num in range(next_part_to_upload, total_parts + 1):
            if len(parts_to_process) >= self.max_uploads_per_run:
                break
            parts_to_process.append(part_num)
            
        logger.info(f"\n🎯 Processing parts: {parts_to_process}")
        
        processed_dir = self.config['paths']['processed']
        segments_to_upload = []
        
        for part_num in parts_to_process:
            start_time = (part_num - 1) * self.segment_duration
            end_time = min(start_time + self.segment_duration, total_duration)
            
            segment_filename = f"{video_id}_part{part_num}.mp4"
            segment_path = os.path.join(processed_dir, segment_filename)
            edited_filename = f"{video_id}_part{part_num}_edited.mp4"
            edited_path = os.path.join(processed_dir, edited_filename)
            
            # Create/Split
            if not os.path.exists(segment_path):
                logger.info(f"Creating part {part_num}...")
                from modules.splitter import split_video
                result_path = split_video(video_path, start_time, end_time, processed_dir, segment_filename)
                if not result_path:
                    logger.error(f"Failed to split part {part_num}")
                    continue
            
            # Edit
            logger.info(f"Editing part {part_num}...")
            edited_result = self.editor.add_overlays(
                segment_path, part_num, video_data['title'], edited_path
            )
            
            if edited_result:
                segments_to_upload.append((edited_path, part_num, video_data['title']))
                # Clean raw segment
                if os.path.exists(segment_path):
                    os.remove(segment_path)
            else:
                 logger.error(f"Failed to edit part {part_num}")

        # D. UPLOAD
        logger.info(f"\n🚀 Uploading {len(segments_to_upload)} segments...")
        
        upload_config = self.config['youtube_upload']
        uploaded_parts = list(parts_already_uploaded)
        uploaded_ids = list(video_data.get('youtube_video_ids', []))
        
        for edited_path, part_num, title in segments_to_upload:
            title_text = f"{title} - Part {part_num}"
            if len(title_text) > 95:
                title_text = title[:90] + f"... - Part {part_num}"
            
            final_title = f"{title_text} #shorts #mrbeast"
            
            description = upload_config['description_template'].format(
                title=title, part=part_num, total=total_parts, url=video_data['url']
            )
            
            # Check Daily Limit
            if self.uploader.is_daily_limit_reached():
                logger.warning("⚠️ Daily upload limit reached!")
                break
            
            try:
                # Assuming upload_short exists in uploader
                yt_id = self.uploader.upload_short(
                    edited_path, 
                    final_title, 
                    description,
                    upload_config['tags'],
                    upload_config['category_id'],
                    upload_config['privacy_status']
                )
                
                if yt_id:
                    logger.info(f"✅ Uploaded: https://youtube.com/shorts/{yt_id}")
                    uploaded_parts.append(part_num)
                    uploaded_ids.append(yt_id)
                    
                    self.tracking['videos'][video_id]['parts_uploaded'] = sorted(uploaded_parts)
                    self.tracking['videos'][video_id]['youtube_video_ids'] = uploaded_ids
                    
                    if part_num == 1:
                        self.tracking['videos'][video_id]['status'] = 'partial'
                    
                    self._save_tracking()
                    
                    try:
                        notify_video_uploaded(final_title, part_num, total_parts)
                    except:
                        pass
                else:
                    logger.error("Upload returned no ID (Quota?)")
            
            except Exception as e:
                logger.error(f"Upload Error: {e}")
            
            # Cleanup edited file
            if os.path.exists(edited_path):
                os.remove(edited_path)
        
        # Check completion after uploads
        if len(uploaded_parts) >= total_parts:
            self.tracking['videos'][video_id]['status'] = 'completed'
            logger.info("🎉 Video completed!")
            
            # Re-trigger cleanup logic (delete from cloud) by calling recursively or next run
            # For now, just save. Next run will catch it as 'completed' or we can handle it now.
            # Best to let next run 'move on' or just delete now:
            
            if os.path.exists(video_path):
                os.remove(video_path)
            
            if cloud_url:
                logger.info(f"🗑️ Deleting from cloud storage...")
                self.downloader.delete_from_cloud(cloud_url)
                self.tracking['videos'][video_id]['cloud_url'] = None
            
            self._save_tracking()

    def show_status(self):
        """Show current tracking status"""
        print("\n" + "=" * 60)
        print("=== Status Report ===")
        print("=" * 60)
        print(f"Channel: {self.tracking.get('channel_url', 'Not set')}")
        print(f"Last Scrape: {self.tracking.get('last_scrape', 'Never')}")
        print(f"\nTotal Videos: {len(self.tracking.get('videos', {}))}")
        
        # Count by status
        status_counts = {}
        for video_data in self.tracking.get('videos', {}).values():
            status = video_data.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\nStatus Breakdown:")
        for status, count in status_counts.items():
            emoji = {'completed': '✅', 'partial': '🔄', 'pending': '⏳'}.get(status, '❓')
            print(f"  {emoji} {status}: {count}")
        
        # Show partial videos (in progress)
        partial = [
            (vid, data) for vid, data in self.tracking.get('videos', {}).items()
            if data.get('status') == 'partial'
        ]
        if partial:
            print("\n🔄 In Progress:")
            for vid, data in partial:
                uploaded = len(data.get('parts_uploaded', []))
                total = data.get('total_parts', '?')
                print(f"  • {data['title']}")
                print(f"    Progress: {uploaded}/{total} parts")
        
        # Show next pending
        pending = [
            (vid, data) for vid, data in self.tracking.get('videos', {}).items()
            if data.get('status') == 'pending'
        ]
        if pending:
            print(f"\n⏳ Next Pending: {pending[0][1]['title']}")


def main():
    parser = argparse.ArgumentParser(description='YouTube to YouTube Shorts Automation')
    parser.add_argument('--channel', help='YouTube channel URL to scrape')
    parser.add_argument('--scrape', action='store_true', help='Only scrape channel')
    parser.add_argument('--status', action='store_true', help='Show tracking status')
    parser.add_argument('--full', action='store_true', help='Run full automation pipeline')
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = YouTubeShortsAutomation()
    
    # Execute requested action
    if args.status:
        automation.show_status()
    elif args.scrape:
        automation.scrape_channel(args.channel)
    elif args.full:
        automation.run_full_automation()
    else:
        # Default: show status
        automation.show_status()


if __name__ == "__main__":
    main()
