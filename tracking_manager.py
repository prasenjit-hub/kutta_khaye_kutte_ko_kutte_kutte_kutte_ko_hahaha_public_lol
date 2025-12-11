"""
Advanced Tracking Manager
View and manage uploaded videos
"""
import json
from datetime import datetime
from typing import Dict, List


class TrackingManager:
    def __init__(self, tracking_file='tracking.json'):
        self.tracking_file = tracking_file
        self.tracking = self._load()
    
    def _load(self) -> dict:
        try:
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'channel_url': '', 'last_scrape': None, 'videos': {}}
    
    def _save(self):
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracking, f, indent=2, ensure_ascii=False)
    
    def get_stats(self) -> dict:
        """Get overall statistics"""
        videos = self.tracking.get('videos', {})
        
        stats = {
            'total': len(videos),
            'pending': 0,
            'downloaded': 0,
            'processed': 0,
            'completed': 0,
            'partial': 0
        }
        
        for video_data in videos.values():
            status = video_data.get('status', 'pending')
            stats[status] = stats.get(status, 0) + 1
        
        return stats
    
    def get_pending_videos(self) -> List[tuple]:
        """Get all pending videos sorted by views"""
        videos = self.tracking.get('videos', {})
        
        pending = [
            (vid, data) for vid, data in videos.items()
            if data.get('status') == 'pending'
        ]
        
        # Sort by views (highest first)
        pending.sort(key=lambda x: x[1].get('views', 0), reverse=True)
        
        return pending
    
    def get_completed_videos(self) -> List[tuple]:
        """Get all completed videos"""
        videos = self.tracking.get('videos', {})
        
        completed = [
            (vid, data) for vid, data in videos.items()
            if data.get('status') == 'completed'
        ]
        
        return completed
    
    def is_already_uploaded(self, video_id: str) -> bool:
        """Check if video is already uploaded"""
        video = self.tracking.get('videos', {}).get(video_id, {})
        return video.get('status') == 'completed'
    
    def mark_as_uploaded(self, video_id: str, parts: List[int]):
        """Mark video as uploaded"""
        if video_id in self.tracking.get('videos', {}):
            self.tracking['videos'][video_id]['status'] = 'completed'
            self.tracking['videos'][video_id]['parts_uploaded'] = parts
            self.tracking['videos'][video_id]['last_upload'] = datetime.now().isoformat()
            self._save()
    
    def reset_video_status(self, video_id: str):
        """Reset video to pending (to re-upload)"""
        if video_id in self.tracking.get('videos', {}):
            self.tracking['videos'][video_id]['status'] = 'pending'
            self.tracking['videos'][video_id]['parts_uploaded'] = []
            self._save()
    
    def export_uploaded_list(self, filename='uploaded_videos.txt'):
        """Export list of uploaded videos to text file"""
        completed = self.get_completed_videos()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("UPLOADED VIDEOS LIST\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, (vid, data) in enumerate(completed, 1):
                f.write(f"{i}. {data['title']}\n")
                f.write(f"   Video ID: {vid}\n")
                f.write(f"   Views: {data.get('views', 0):,}\n")
                f.write(f"   Parts Uploaded: {data.get('parts_uploaded', [])}\n")
                f.write(f"   Upload Date: {data.get('last_upload', 'N/A')}\n")
                f.write(f"   URL: {data.get('url', 'N/A')}\n")
                f.write("\n")
        
        print(f"✓ Exported {len(completed)} uploaded videos to {filename}")
    
    def show_report(self):
        """Display detailed tracking report"""
        print("\n" + "=" * 80)
        print("TRACKING REPORT")
        print("=" * 80)
        
        print(f"\nChannel: {self.tracking.get('channel_url', 'Not set')}")
        print(f"Last Scrape: {self.tracking.get('last_scrape', 'Never')}")
        
        stats = self.get_stats()
        print(f"\n📊 Statistics:")
        print(f"  Total Videos: {stats['total']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  Downloaded: {stats['downloaded']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Partial: {stats.get('partial', 0)}")
        
        # Show pending videos
        pending = self.get_pending_videos()
        if pending:
            print(f"\n📝 Top 5 Pending Videos (Highest Views):")
            for i, (vid, data) in enumerate(pending[:5], 1):
                print(f"  {i}. {data['title']}")
                print(f"     Views: {data.get('views', 0):,} | ID: {vid}")
        
        # Show recently uploaded
        completed = self.get_completed_videos()
        if completed:
            # Sort by upload date
            completed.sort(key=lambda x: x[1].get('last_upload', ''), reverse=True)
            print(f"\n✅ Recently Uploaded (Last 5):")
            for i, (vid, data) in enumerate(completed[:5], 1):
                print(f"  {i}. {data['title']}")
                print(f"     Parts: {data.get('parts_uploaded', [])} | Uploaded: {data.get('last_upload', 'N/A')}")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    
    manager = TrackingManager()
    
    # Parse command
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'stats':
            stats = manager.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif command == 'pending':
            pending = manager.get_pending_videos()
            print(f"Found {len(pending)} pending videos")
            for vid, data in pending[:10]:
                print(f"- {data['title']} ({data.get('views', 0):,} views)")
        
        elif command == 'completed':
            completed = manager.get_completed_videos()
            print(f"Found {len(completed)} completed videos")
            for vid, data in completed:
                print(f"- {data['title']} (Parts: {data.get('parts_uploaded', [])})")
        
        elif command == 'export':
            manager.export_uploaded_list()
        
        elif command == 'check' and len(sys.argv) > 2:
            video_id = sys.argv[2]
            is_uploaded = manager.is_already_uploaded(video_id)
            print(f"Video {video_id}: {'UPLOADED' if is_uploaded else 'NOT UPLOADED'}")
        
        else:
            manager.show_report()
    else:
        manager.show_report()
