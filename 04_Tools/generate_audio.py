import argparse
import json
import os
import asyncio
import edge_tts
from pydub import AudioSegment
import re
import tempfile
import shutil
import imageio_ffmpeg

# Configure pydub to use imageio-ffmpeg binary
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()
AudioSegment.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
AudioSegment.ffprobe = imageio_ffmpeg.get_ffmpeg_exe()

# Define workspace paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, "02_Assets")

# Voice Options
# Narrator: Deep, calm, baritone-like.
NARRATOR_VOICE = "en-US-ChristopherNeural"
# Character (Generic Male): Friendly, conversational.
CHARACTER_VOICE = "en-IN-PrabhatNeural"

async def generate_segment(text, voice, output_path, rate="+0%"):
    """Generate audio for a text segment."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

async def generate_audio_for_poem(scene, output_path, default_voice, default_rate):
    """
    Generate audio for a poem scene.
    Uses the specified voice and rate, treating the entire text as a single block
    to maintain poetic flow.
    """
    narration = scene.get("narration_text", "")
    if not narration:
        return False
        
    print(f"Generating Poem Audio: {output_path}")
    await generate_segment(narration, default_voice, output_path, rate=default_rate)
    return True

async def generate_audio_for_story(scene, output_path, default_voice, default_rate):
    """
    Generate audio for a story scene.
    Currently uses the same logic as poem (single block), but separated for future
    enhancements like multi-voice dialogue.
    """
    narration = scene.get("narration_text", "")
    if not narration:
        return False

    print(f"Generating Story Audio: {output_path}")
    # Future: Add dialogue parsing here
    await generate_segment(narration, default_voice, output_path, rate=default_rate)
    return True

async def process_json_script(json_path, force=False):
    """
    Process a JSON script and generate audio for all scenes.
    """
    print(f"Processing JSON script: {json_path}")
    print(f"Force Overwrite: {force}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    story_title = data.get("metadata", {}).get("title", "Untitled")
    subject = data.get("metadata", {}).get("subject", "General")
    unit = data.get("metadata", {}).get("unit", "Unit_0")
    
    # Check content type (poem vs story)
    content_type = data.get("metadata", {}).get("type", "story").lower()
    print(f"Content Type: {content_type}")
    
    # Normalize folder names
    safe_subject = subject.replace(" ", "_")
    safe_unit = unit.replace(":", "").replace(" ", "_")
    safe_title = story_title.replace(" ", "_")
    
    # Construct output directory: 02_Assets/Audio/Subject/Unit/Story/
    story_audio_dir = os.path.join(ASSETS_DIR, "Audio", safe_subject, safe_unit, safe_title)
    os.makedirs(story_audio_dir, exist_ok=True)
    
    scenes = data.get("scenes", [])
    print(f"Story: {story_title}")
    print(f"Output Directory: {story_audio_dir}")
    
    tasks = []
    
    # Check for custom voice and rate in metadata
    custom_voice = data.get("metadata", {}).get("voice")
    narrator_voice = custom_voice if custom_voice else NARRATOR_VOICE
    
    custom_rate = data.get("metadata", {}).get("rate")
    rate = custom_rate if custom_rate else "+0%"
    
    print(f"Using Voice: {narrator_voice}")
    print(f"Using Rate: {rate}")
    
    for scene in scenes:
        scene_id = scene.get("id")
        
        filename = f"scene_{scene_id:02d}.mp3"
        output_path = os.path.join(story_audio_dir, filename)
        
        if os.path.exists(output_path) and not force:
            print(f"Scene {scene_id} audio already exists. Skipping.")
            continue
            
        # Dispatch based on type
        if content_type == "poem":
            task = generate_audio_for_poem(scene, output_path, narrator_voice, rate)
        else:
            task = generate_audio_for_story(scene, output_path, narrator_voice, rate)
            
        tasks.append(task)
        
    if tasks:
        await asyncio.gather(*tasks)
        print("Audio generation complete!")
    else:
        print("No new audio files generated.")

if __name__ == "__main__":
    # Fix for Windows Event Loop Policy
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    parser = argparse.ArgumentParser(description="Generate audio narration with edge-tts")
    parser.add_argument("json_path", type=str, help="Path to JSON script file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    args = parser.parse_args()
    
    asyncio.run(process_json_script(args.json_path, args.force))
