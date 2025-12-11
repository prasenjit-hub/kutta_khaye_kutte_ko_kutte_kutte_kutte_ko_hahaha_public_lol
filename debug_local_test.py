"""
Local Debug & Test Script
Tests the complete pipeline: Splitter + Editor
Run this to verify everything works on your local machine before deploying.
"""
import os
import sys
import json
import shutil
import argparse
from pathlib import Path


def test_imports():
    """Test if all modules can be imported correctly"""
    print("=" * 60)
    print("TEST 1: Import Verification")
    print("=" * 60)
    
    success = True
    modules_to_test = [
        ("modules.splitter", "VideoSplitter"),
        ("modules.editor", "VideoEditor"),
        ("modules.downloader", "VideoDownloader"),
        ("modules.scraper", "get_channel_videos"),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}.{class_name} - Import Error: {e}")
            success = False
        except AttributeError as e:
            print(f"  ❌ {module_name}.{class_name} - Not Found: {e}")
            success = False
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name} - Error: {e}")
            success = False
    
    if success:
        print("\n✅ All modules imported successfully!")
    else:
        print("\n❌ Some imports failed. Fix these before proceeding.")
    
    return success


def test_config():
    """Test if config.json is valid"""
    print("\n" + "=" * 60)
    print("TEST 2: Config Validation")
    print("=" * 60)
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['video_settings', 'overlay_settings', 'paths']
        missing = [k for k in required_keys if k not in config]
        
        if missing:
            print(f"  ❌ Missing required config keys: {missing}")
            return False, None
        
        print(f"  ✅ Config loaded successfully")
        print(f"     - Video segment duration: {config['video_settings'].get('segment_duration_seconds', 60)}s")
        print(f"     - Max segments: {config['video_settings'].get('max_segments_per_video', 10)}")
        print(f"     - Target resolution: {config['video_settings'].get('target_resolution', [1080, 1920])}")
        
        return True, config
        
    except FileNotFoundError:
        print("  ❌ config.json not found!")
        return False, None
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in config.json: {e}")
        return False, None


def find_test_video():
    """Find a video file to test with"""
    print("\n" + "=" * 60)
    print("TEST 3: Finding Test Video")
    print("=" * 60)
    
    # Search locations
    search_dirs = ['downloads', 'test_output', '.']
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for file in os.listdir(search_dir):
                if file.endswith('.mp4') and not file.endswith('_edited.mp4'):
                    video_path = os.path.join(search_dir, file)
                    size_mb = os.path.getsize(video_path) / (1024 * 1024)
                    if size_mb > 1:  # At least 1MB (not corrupted/empty)
                        print(f"  ✅ Found: {video_path} ({size_mb:.2f} MB)")
                        return video_path
    
    print("  ❌ No suitable test video found!")
    print("     Place a .mp4 file in 'downloads' folder to test.")
    print("     Or run: python main.py --download <video_id>")
    return None


def test_splitter(video_path: str, output_dir: str = "test_output"):
    """Test the video splitter module"""
    print("\n" + "=" * 60)
    print("TEST 4: Video Splitter")
    print("=" * 60)
    
    from modules.splitter import VideoSplitter
    
    # Clean output directory
    if os.path.exists(output_dir):
        print(f"  🗑️ Cleaning {output_dir}...")
        shutil.rmtree(output_dir)
    
    try:
        splitter = VideoSplitter(output_dir=output_dir)
        
        # Get video info first
        print(f"  📊 Getting video info...")
        info = splitter.get_segment_info(video_path, segment_duration=60)
        
        if info:
            print(f"     - Total duration: {info['total_duration']:.2f}s")
            print(f"     - Expected segments: {info['num_segments']}")
        
        # Split the video (only first segment for quick test)
        print(f"  ✂️ Splitting video (60s segments)...")
        
        # Use short segment for testing (30s)
        segments = splitter.split_video(video_path, "debug_test", segment_duration=30)
        
        # Limit to first segment only for quick testing
        if len(segments) > 1:
            print(f"  ℹ️ Created {len(segments)} segments, keeping only first for quick test")
            # Keep only first segment file, delete others
            for seg in segments[1:]:
                if os.path.exists(seg):
                    os.remove(seg)
            segments = segments[:1]
        
        if segments:
            print(f"  ✅ Created {len(segments)} segment(s):")
            for seg in segments:
                if os.path.exists(seg):
                    size_kb = os.path.getsize(seg) / 1024
                    print(f"     - {seg} ({size_kb:.2f} KB)")
            return True, segments
        else:
            print("  ❌ No segments created!")
            return False, []
            
    except Exception as e:
        print(f"  ❌ Splitter failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_editor(segment_path: str, config: dict):
    """Test the video editor module"""
    print("\n" + "=" * 60)
    print("TEST 5: Video Editor")
    print("=" * 60)
    
    from modules.editor import VideoEditor
    
    try:
        editor = VideoEditor(config)
        
        output_path = segment_path.replace('.mp4', '_edited.mp4')
        
        print(f"  🎬 Adding overlays...")
        print(f"     - Input: {segment_path}")
        print(f"     - Output: {output_path}")
        
        result = editor.add_overlays(
            video_path=segment_path,
            part_number=1,
            title="Debug Test Video",
            output_path=output_path
        )
        
        if result and os.path.exists(result):
            size_kb = os.path.getsize(result) / 1024
            print(f"  ✅ Editor successful!")
            print(f"     - Output: {result} ({size_kb:.2f} KB)")
            return True, result
        else:
            print("  ❌ Editor failed - no output file created!")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Editor failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def run_full_test():
    """Run complete test pipeline"""
    print("\n")
    print("🔧 " + "=" * 56 + " 🔧")
    print("   LOCAL DEBUG TEST - Instagram Auto Video Upload")
    print("🔧 " + "=" * 56 + " 🔧")
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ FAILED: Fix import errors first!")
        return False
    
    # Test 2: Config
    config_ok, config = test_config()
    if not config_ok:
        print("\n❌ FAILED: Fix config.json!")
        return False
    
    # Test 3: Find video
    video_path = find_test_video()
    if not video_path:
        print("\n⚠️ SKIPPED: No test video available.")
        print("   The imports and config are fine!")
        print("   Add a video to 'downloads' folder to test full pipeline.")
        return True
    
    # Test 4: Splitter
    splitter_ok, segments = test_splitter(video_path)
    if not splitter_ok or not segments:
        print("\n❌ FAILED: Splitter not working!")
        return False
    
    # Test 5: Editor
    editor_ok, edited_path = test_editor(segments[0], config)
    if not editor_ok:
        print("\n❌ FAILED: Editor not working!")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("  ✅ All modules imported correctly")
    print("  ✅ Config is valid")
    print("  ✅ Splitter working")
    print("  ✅ Editor working")
    print("\n🎉 ALL TESTS PASSED! Ready for GitHub Actions deployment.")
    
    return True


def quick_import_test():
    """Quick test - just check imports"""
    print("Quick Import Test...")
    return test_imports()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug and test the video pipeline")
    parser.add_argument('--quick', action='store_true', help='Quick test - only check imports')
    parser.add_argument('--video', help='Specific video path to test with')
    
    args = parser.parse_args()
    
    if args.quick:
        success = quick_import_test()
    else:
        # If specific video provided, use it
        if args.video and os.path.exists(args.video):
            # Override find_test_video
            original_find = find_test_video
            def find_test_video():
                print(f"  ✅ Using provided video: {args.video}")
                return args.video
            globals()['find_test_video'] = find_test_video
        
        success = run_full_test()
    
    sys.exit(0 if success else 1)
