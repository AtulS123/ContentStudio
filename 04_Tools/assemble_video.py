import json
import os
import subprocess
from pathlib import Path
import imageio_ffmpeg
import shutil

# Get FFmpeg binary path
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
FFPROBE_BIN = FFMPEG_BIN.replace('ffmpeg', 'ffprobe')

# Define workspace paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, "02_Assets")
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "03_Output")

def get_audio_duration(audio_path):
    """Get duration of audio file using ffprobe."""
    try:
        cmd = [
            FFPROBE_BIN,
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Warning: Could not get duration for {audio_path}: {e}")
        return 5.0

def create_video_from_image_audio(image_path, audio_path, output_path, subtitle_text=None, duration=None):
    """
    Create a video clip from a single image and audio using FFmpeg.
    """
    if duration is None:
        duration = get_audio_duration(audio_path)
    
    # Base FFmpeg command
    cmd = [
        FFMPEG_BIN,
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-t', str(duration),
        '-vf', f'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
        '-y',
        output_path
    ]
    
    # Add subtitle filter if provided
    if subtitle_text:
        # Escape special characters for FFmpeg
        subtitle_text = subtitle_text.replace("'", "'\\\\\\''").replace(":", "\\:").replace("%", "\\%")
        
        # Wrap text to max 60 characters per line
        words = subtitle_text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > 60:  # +1 for space
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Join lines with newline
        wrapped_text = '\\n'.join(lines[:3])  # Max 3 lines
        
        # Add subtitle filter with better positioning
        subtitle_filter = (
            f"drawtext=text='{wrapped_text}':"
            f"fontfile=/Windows/Fonts/arial.ttf:"
            f"fontsize=22:"
            f"fontcolor=white:"
            f"borderw=2:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h-120:"
            f"box=1:"
            f"boxcolor=black@0.5:"
            f"boxborderw=10"
        )
        
        # Update video filter
        for i, arg in enumerate(cmd):
            if arg == '-vf':
                cmd[i+1] = cmd[i+1] + ',' + subtitle_filter
                break
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating video clip: {e}")
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False

def concatenate_videos(video_files, output_path):
    """
    Concatenate multiple video files using FFmpeg.
    """
    # Create a temporary file list for FFmpeg concat
    concat_file = os.path.join(os.path.dirname(output_path), 'concat_list.txt')
    
    with open(concat_file, 'w') as f:
        for video_file in video_files:
            # Use absolute paths and escape them
            abs_path = os.path.abspath(video_file).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    
    cmd = [
        FFMPEG_BIN,
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        '-y',
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        os.remove(concat_file)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating videos: {e}")
        print(f"FFmpeg error: {e.stderr.decode()}")
        if os.path.exists(concat_file):
            os.remove(concat_file)
        return False

def assemble_video_ffmpeg(json_path, output_path=None, burn_subtitles=False):
    """
    Assemble video using FFmpeg from JSON script, images, and audio.
    """
    print(f"Processing JSON script: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.get('metadata', {})
    story_title = metadata.get('title', 'Untitled')
    scenes = data.get('scenes', [])
    
    print(f"Story: {story_title}")
    print(f"Scenes: {len(scenes)}")
    
    # Determine asset directories based on JSON path
    safe_title = story_title.replace(" ", "_")
    
    # This mirrors the structure: 01_Scripts/... -> 02_Assets/Images/...
    image_dir = None
    try:
        script_rel_path = os.path.relpath(json_path, os.path.join(WORKSPACE_ROOT, "01_Scripts"))
        script_dir = os.path.dirname(script_rel_path)
        story_name = os.path.splitext(os.path.basename(json_path))[0]
        
        image_dir = os.path.join(ASSETS_DIR, "Images", script_dir, story_name)
    except ValueError:
        # Fallback if script is not in 01_Scripts
        safe_title = story_title.replace(" ", "_")
        image_dir = os.path.join(ASSETS_DIR, "Images", safe_title)
    
    print(f"DEBUG: image_dir = {image_dir}")
    
    if not os.path.exists(image_dir):
        # Try finding it by name (fallback)
        safe_title = story_title.replace(" ", "_")
        images_base = os.path.join(ASSETS_DIR, "Images")
        found = False
        for root, dirs, files in os.walk(images_base):
            for d in dirs:
                if safe_title.lower() in d.lower() or d.lower() in safe_title.lower():
                    image_dir = os.path.join(root, d)
                    found = True
                    break
            if found:
                break
    
    if not os.path.exists(image_dir):
        print(f"Error: Could not find image directory for {story_title}")
        print(f"Expected: {image_dir}")
        return None
    
    # Find audio directory
    audio_base = os.path.join(ASSETS_DIR, "Audio", "English")
    audio_dir = None
    for unit_dir in os.listdir(audio_base):
        unit_path = os.path.join(audio_base, unit_dir)
        if os.path.isdir(unit_path):
            for story_dir in os.listdir(unit_path):
                story_path = os.path.join(unit_path, story_dir)
                if os.path.isdir(story_path) and (safe_title.lower() in story_dir.lower() or story_dir.lower() in safe_title.lower()):
                    audio_dir = story_path
                    break
        if audio_dir:
            break
    
    if not audio_dir:
        print(f"Error: Could not find audio directory for {safe_title}")
        return None
    
    print(f"Image directory: {image_dir}")
    print(f"Audio directory: {audio_dir}")
    
    # Generate SRT subtitle file
    from generate_subtitles import generate_srt_from_json
    srt_path = os.path.join(OUTPUT_DIR, f"{safe_title}_temp.srt")
    generate_srt_from_json(json_path, srt_path)
    
    # Create temporary directory for scene clips
    temp_dir = os.path.join(OUTPUT_DIR, "_temp_clips")
    os.makedirs(temp_dir, exist_ok=True)
    
    scene_videos = []
    
    # Process each scene
    for scene in scenes:
        scene_id = scene.get('id')
        narration = scene.get('narration_text', '')
        assets = scene.get('assets', {})
        
        # Get file paths
        image_file = assets.get('image_file', f'scene_{scene_id:02d}.png')
        audio_file = assets.get('audio_file', f'scene_{scene_id:02d}.mp3')
        
        image_path = os.path.join(image_dir, image_file)
        audio_path = os.path.join(audio_dir, audio_file)
        
        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            continue
        
        if not os.path.exists(audio_path):
            print(f"Warning: Audio not found: {audio_path}")
            continue
        
        print(f"\nProcessing Scene {scene_id}...")
        
        # Get duration from JSON (if available) or use default
        duration = scene.get('duration', 10.0)
        
        # Create temporary video for this scene (without subtitles)
        scene_video_path = os.path.join(temp_dir, f'scene_{scene_id:02d}.mp4')
        
        if create_video_from_image_audio(image_path, audio_path, scene_video_path, None, duration):
            scene_videos.append(scene_video_path)
            print(f"Scene {scene_id} processed [OK] - Duration: {duration}s")
        else:
            print(f"Scene {scene_id} failed [ERROR]")
    
    if not scene_videos:
        print("Error: No scene videos were created.")
        return None
    
    # Set output path
    if output_path is None:
        # Mirror structure: 01_Scripts/... -> 03_Output/...
        try:
            script_rel_path = os.path.relpath(json_path, os.path.join(WORKSPACE_ROOT, "01_Scripts"))
            script_dir = os.path.dirname(script_rel_path)
            output_dir = os.path.join(OUTPUT_DIR, script_dir)
        except ValueError:
            # Fallback
            output_dir = OUTPUT_DIR
            
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{safe_title}.mp4")
    
    # Concatenate all scene videos
    print(f"\nConcatenating {len(scene_videos)} scenes...")
    temp_concat_path = os.path.join(temp_dir, "concat_no_subs.mp4")
    
    if not concatenate_videos(scene_videos, temp_concat_path):
        print("Error: Failed to concatenate videos.")
        return None
    
    # Burn in subtitles if requested and SRT file exists
    if burn_subtitles and srt_path and os.path.exists(srt_path):
        print("\nBurning subtitles into video...")
        
        # Escape the SRT path for Windows
        srt_path_escaped = srt_path.replace('\\', '/').replace(':', '\\:')
        
        subtitle_cmd = [
            FFMPEG_BIN,
            '-i', temp_concat_path,
            '-vf', f"subtitles='{srt_path_escaped}':force_style='FontName=Arial,FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=0,MarginV=50'",
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(subtitle_cmd, check=True, capture_output=True)
            print(f"[SUCCESS] Video created with subtitles!")
            
            # Cleanup temp concat file
            if os.path.exists(temp_concat_path):
                os.remove(temp_concat_path)
                
        except subprocess.CalledProcessError as e:
            print(f"Error burning subtitles: {e}")
            print(f"FFmpeg error: {e.stderr.decode()}")
            # Fall back to video without subtitles
            import shutil
            shutil.copy(temp_concat_path, output_path)
            print("Saved video without subtitles as fallback")
    else:
        # No subtitles burning, just use the concatenated video
        import shutil
        shutil.copy(temp_concat_path, output_path)
        print(f"[SUCCESS] Video created (no subtitles burned).")
        
        # Copy SRT to output directory if it exists
        if srt_path and os.path.exists(srt_path):
            output_srt_path = output_path.replace(".mp4", ".srt")
            shutil.copy2(srt_path, output_srt_path)
            print(f"Copied SRT to: {output_srt_path}")

    # Cleanup SRT temp file
    if srt_path and os.path.exists(srt_path):
        os.remove(srt_path)
    
    print(f"Output: {output_path}")
    
    # Get file size
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f"File size: {file_size:.2f} MB")
    
    # Cleanup temp files
    for video in scene_videos:
        if os.path.exists(video):
            os.remove(video)
    if os.path.exists(temp_dir):
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    return output_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Assemble video using FFmpeg")
    parser.add_argument("json_path", type=str, help="Path to JSON script file")
    parser.add_argument("--output", type=str, default=None, help="Output video path")
    parser.add_argument("--burn-subtitles", action="store_true", help="Burn subtitles into video")
    
    args = parser.parse_args()
    
    assemble_video_ffmpeg(args.json_path, args.output, args.burn_subtitles)
