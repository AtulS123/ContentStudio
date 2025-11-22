import json
import os
import subprocess
import re
import imageio_ffmpeg

# Get FFmpeg binary
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

# Define workspace paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, "02_Assets")

def get_audio_duration(audio_path):
    """Get duration of audio file in seconds using FFmpeg."""
    try:
        cmd = [FFMPEG_BIN, '-i', audio_path]
        # ffmpeg prints info to stderr
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Look for "Duration: 00:00:05.12,"
        match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)", result.stderr)
        if match:
            h, m, s = map(float, match.groups())
            duration = h * 3600 + m * 60 + s
            return duration
        return None
    except Exception as e:
        print(f"Error getting duration for {audio_path}: {e}")
        return None

def add_durations_to_json(json_path):
    """
    Add duration field to each scene in JSON based on actual audio file duration.
    """
    print(f"Processing: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.get('metadata', {})
    story_title = metadata.get('title', 'Untitled')
    scenes = data.get('scenes', [])
    
    # Find audio directory
    safe_title = story_title.replace(" ", "_")
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
        return
    
    print(f"Audio directory: {audio_dir}")
    
    # Update each scene with duration
    updated = False
    for scene in scenes:
        scene_id = scene.get('id')
        audio_file = scene.get('assets', {}).get('audio_file', f'scene_{scene_id:02d}.mp3')
        audio_path = os.path.join(audio_dir, audio_file)
        
        if os.path.exists(audio_path):
            duration = get_audio_duration(audio_path)
            if duration:
                scene['duration'] = round(duration, 2)
                print(f"Scene {scene_id}: {duration:.2f}s")
                updated = True
        else:
            print(f"Warning: Audio file not found: {audio_path}")
    
    if updated:
        # Save updated JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Updated {json_path}")
    else:
        print("\n⚠️ No durations were added")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add audio durations to JSON script")
    parser.add_argument("json_path", type=str, help="Path to JSON script file")
    
    args = parser.parse_args()
    add_durations_to_json(args.json_path)
