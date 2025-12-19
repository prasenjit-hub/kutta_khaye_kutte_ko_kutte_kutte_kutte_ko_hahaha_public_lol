"""
Video Editor
Adds text overlays (part numbers) and converts to YouTube Shorts format (9:16)
Uses FFmpeg for reliable video processing with blur background for landscape videos
"""
import subprocess
import os
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



import random

def get_video_info(video_path: str) -> dict:
    """Get video dimensions and duration using ffprobe"""
    try:
        # Get video stream info
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0:s=x',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        dimensions = result.stdout.strip().split('x')
        
        width = int(dimensions[0]) if dimensions[0] else 1920
        height = int(dimensions[1]) if len(dimensions) > 1 and dimensions[1] else 1080
        
        # Get duration
        cmd_dur = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result_dur = subprocess.run(cmd_dur, capture_output=True, text=True)
        duration = float(result_dur.stdout.strip()) if result_dur.stdout.strip() else 60
        
        return {'width': width, 'height': height, 'duration': duration}
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {'width': 1920, 'height': 1080, 'duration': 60}


class VideoEditor:
    def __init__(self, config: dict):
        self.config = config
        self.overlay_settings = config.get('overlay_settings', {})
        self.video_settings = config.get('video_settings', {})
        self.reaction_dir = os.path.join(os.getcwd(), 'assets', 'reactions')

    def _create_reaction_track(self, target_duration: float) -> str:
        """
        Create a reaction video track by concatenating random clips
        from assets/reactions to match target_duration.
        Returns path to created temp file or None.
        """
        if not os.path.exists(self.reaction_dir):
            return None
            
        clips = [
            os.path.join(self.reaction_dir, f) 
            for f in os.listdir(self.reaction_dir) 
            if f.lower().endswith(('.mp4', '.mov', '.webm'))
        ]
        
        if not clips:
            return None
            
        # Select random clips to fill duration
        selected_clips = []
        current_duration = 0
        
        # Loop until we have enough footage (plus a bit extra buffer)
        while current_duration < target_duration + 5:
            clip = random.choice(clips)
            selected_clips.append(clip)
            # Estimate clip duration (assume ~7s as user said, or check real)
            # Check real duration for accuracy
            info = get_video_info(clip)
            current_duration += info['duration']
            
        # Create concat list file
        concat_list_path = 'temp_concat_list.txt'
        with open(concat_list_path, 'w', encoding='utf-8') as f:
            for clip in selected_clips:
                # Escape paths for FFmpeg
                formatted_path = clip.replace('\\', '/').replace("'", "'\\''")
                f.write(f"file '{formatted_path}'\n")
        
        output_path = 'temp_reaction_track.mp4'
        
        try:
            # Concatenate
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-t', str(target_duration),
                '-c:v', 'libx264',
                '-an', # No audio from reaction
                '-preset', 'ultrafast',
                output_path
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            os.remove(concat_list_path)
            
            if os.path.exists(output_path):
                return output_path
            return None
            
        except Exception as e:
            logger.error(f"Error creating reaction track: {e}")
            return None

    
    def _create_text_overlay(self, text: str, width: int, height: int = 200) -> str:
        """Create a text overlay image using PIL"""
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font
        font_size = self.overlay_settings.get('part_text_size', 80)
        font = None
        
        font_paths = [
            "arialbd.ttf",
            "arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Center text
        x = (width - text_width) // 2
        y = 50
        
        # Draw shadow
        shadow_offset = 3
        for ox in [-shadow_offset, 0, shadow_offset]:
            for oy in [-shadow_offset, 0, shadow_offset]:
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        # Save to temp file
        overlay_path = 'temp_overlay.png'
        img.save(overlay_path)
        
        return overlay_path
    
    def add_overlays(self, video_path: str, part_number: int, title: str, output_path: str = None) -> str:
        """
        Add text overlays + REACTION VIDEO and convert to YouTube Shorts format (9:16)
        """
        if output_path is None:
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_edited{ext}"
        
        reaction_track = None
        
        try:
            logger.info(f"Adding overlays to: {video_path}")
            
            # Verify input exists
            if not os.path.exists(video_path):
                logger.error(f"Input file not found: {video_path}")
                return None
            
            # Get video info
            video_info = get_video_info(video_path)
            input_width = video_info['width']
            input_height = video_info['height']
            duration = video_info['duration']
            
            # Generate Reaction Track
            reaction_track = self._create_reaction_track(duration)
            has_reaction = reaction_track is not None
            if has_reaction:
                logger.info("✓ Reaction track generated for overlay")
            
            logger.info(f"Input video: {input_width}x{input_height}")
            
            # Target resolution (9:16 for YouTube Shorts)
            target_width, target_height = self.video_settings.get('target_resolution', [1080, 1920])
            
            # Create text overlay
            part_text = self.overlay_settings.get('part_text_format', 'Part {n}').format(n=part_number)
            overlay_path = self._create_text_overlay(part_text, target_width)
            
            # Build FFmpeg filter
            filter_complex = self._build_filter_with_blur_background(
                input_width, input_height,
                target_width, target_height,
                has_reaction
            )
            
            # FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,  # [0:v] Input video
                '-i', overlay_path       # [1:v] Text Overlay
            ]
            
            if has_reaction:
                cmd.extend(['-i', reaction_track]) # [2:v] Reaction Video
                
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '0:a?',  # Keep audio if exists
                '-c:v', 'libx264',
                '-preset', 'slow',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '256k',
                '-r', '30',
                '-movflags', '+faststart',
                '-loglevel', 'error',
                output_path
            ])
            
            logger.info(f"Writing edited video to: {output_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup
            if os.path.exists(overlay_path):
                os.remove(overlay_path)
            if reaction_track and os.path.exists(reaction_track):
                os.remove(reaction_track)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
            
            # Verify output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                logger.info(f"✓ Overlay added successfully")
                return output_path
            else:
                logger.error("Output file missing or too small")
                return None
                
        except Exception as e:
            logger.error(f"Error adding overlays: {e}")
            # Ensure cleanup on crash
            if reaction_track and os.path.exists(reaction_track):
                try: 
                    os.remove(reaction_track) 
                except: 
                    pass
            import traceback
            traceback.print_exc()
            return None
    
    def _build_filter_with_blur_background(self, in_w: int, in_h: int, out_w: int, out_h: int, has_reaction: bool = False) -> str:
        """
        Build FFmpeg filter complex for 9:16 conversion with BLUR BACKGROUND
        Optional: Adds Reaction Video at Bottom Left
        """
        target_aspect = out_w / out_h
        current_aspect = in_w / in_h
        
        # 1. Prepare Main Video (Background + Foreground)
        if current_aspect > target_aspect:
            # LANDSCAPE video - needs blur background padding
            main_filter = (
                "[0:v]split=2[bg_in][fg_in];"
                f"[bg_in]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,crop={out_w}:{out_h},gblur=sigma=18,eq=brightness=-0.3:saturation=0.5[bg];"
                f"[fg_in]scale={out_w}:-2[fg_scaled];"
                "[bg][fg_scaled]overlay=(W-w)/2:(H-h)/2[main_out]"
            )
        else:
            # PORTRAIT/SQUARE
            if current_aspect < target_aspect:
                main_filter = f"[0:v]scale={out_w}:-2,crop={out_w}:{out_h}[main_out]"
            else:
                main_filter = f"[0:v]scale={out_w}:{out_h}[main_out]"
        
        # 2. Add Reaction (if present)
        if has_reaction:
            # Reaction size: 15% of width (roughly)
            react_w = int(out_w * 0.15)
            padding = 20
            
            # Process Reaction: [2:v] -> Crop Square -> Scale
            reaction_filter = (
                f";[2:v]crop='min(iw,ih)':'min(iw,ih)',scale={react_w}:{react_w}[react_out];"
                f"[main_out][react_out]overlay={padding}:H-h-{padding}[video_with_react]"
            )
            final_overlay_input = "[video_with_react]"
        else:
            reaction_filter = ""
            final_overlay_input = "[main_out]"
            
        # 3. Add Text Overlay
        final_filter = (
            f"{main_filter}{reaction_filter};"
            f"{final_overlay_input}[1:v]overlay=(W-w)/2:0[outv]"
        )
        
        return final_filter

    
    def _truncate_title(self, title: str, max_length: int = 40) -> str:
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + '...'


if __name__ == "__main__":
    import json
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    editor = VideoEditor(config)
    
    # Test with a video if exists
    test_dir = "test_output"
    if os.path.exists(test_dir):
        for f in os.listdir(test_dir):
            if f.endswith('.mp4') and not f.endswith('_edited.mp4'):
                input_path = os.path.join(test_dir, f)
                output_path = os.path.join(test_dir, f.replace('.mp4', '_edited.mp4'))
                
                print(f"Testing editor with: {input_path}")
                result = editor.add_overlays(input_path, 1, "Test Title", output_path)
                
                if result:
                    print(f"✓ Success: {result}")
                else:
                    print("✗ Failed")
                break
    else:
        print("No test_output directory found. Run splitter first.")
