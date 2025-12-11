"""
Test YouTube Upload
Simple script to test YouTube upload without downloading/editing
"""
import os
import sys
import json
from modules.youtube_uploader import YouTubeUploader

def test_upload():
    print("=" * 80)
    print("🧪 YOUTUBE UPLOAD TEST")
    print("=" * 80)
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Get your test video path
    print("\n📹 Enter the path to your test video:")
    print("   (Example: test_output/test_video_part1_edited.mp4)")
    print("   (Or drag-and-drop the file here)")
    video_path = input("\nVideo Path: ").strip().strip('"')
    
    if not os.path.exists(video_path):
        print(f"\n❌ Video file not found: {video_path}")
        return
    
    # Get video title
    print("\n✏️ Enter a test title (or press Enter for default):")
    title = input("Title: ").strip()
    if not title:
        title = "Test Upload - YouTube Shorts"
    
    print("\n" + "=" * 80)
    print("📤 UPLOADING...")
    print("=" * 80)
    print(f"📁 File: {video_path}")
    print(f"📝 Title: {title}")
    print(f"🏷️ Tags: {len(config['youtube_upload']['tags'])} tags")
    print(f"🔒 Privacy: {config['youtube_upload']['privacy_status']}")
    print("")
    
    # Initialize uploader
    try:
        uploader = YouTubeUploader(
            credentials_file=config['youtube_upload']['credentials_file']
        )
        print("✅ YouTube API authenticated!")
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\n💡 Solution:")
        print("   1. Make sure youtube_credentials.json exists")
        print("   2. First time: Browser will open for login")
        print("   3. Click 'Allow' to grant permissions")
        return
    
    # Upload
    try:
        description = config['youtube_upload']['description_template'].format(
            title=title,
            part=1,
            total=1,
            url="https://youtube.com/test"
        )
        
        video_id = uploader.upload_short(
            video_path=video_path,
            title=title,
            description=description,
            tags=config['youtube_upload']['tags'],
            category_id=config['youtube_upload']['category_id'],
            privacy_status=config['youtube_upload']['privacy_status']
        )
        
        if video_id:
            print("\n" + "=" * 80)
            print("🎉 UPLOAD SUCCESSFUL!")
            print("=" * 80)
            print(f"✅ Video ID: {video_id}")
            print(f"🔗 Watch: https://youtube.com/watch?v={video_id}")
            print(f"📊 Check YouTube Studio: https://studio.youtube.com/")
            print("\n💡 It may take a few minutes to process on YouTube")
        else:
            print("\n❌ Upload failed!")
            
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload()
    input("\nPress Enter to exit...")
