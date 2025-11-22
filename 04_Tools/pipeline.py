import argparse
import json
import os
import sys
from generate_image import generate_image
from animate_image import animate_image

# Define paths relative to the workspace root (assuming script is run from 04_Tools or root)
# We will normalize paths to be absolute based on the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, "02_Assets")
OUTPUT_VIDEO_DIR = os.path.join(WORKSPACE_ROOT, "03_Output_Video")

def run_pipeline(json_path):
    """
    Run the full Text-to-Video pipeline based on a JSON configuration file.
    """
    print("="*50)
    print(f"Starting Content Generation Pipeline")
    print(f"Config File: {json_path}")
    print("="*50)

    with open(json_path, 'r') as f:
        config = json.load(f)

    story_title = config.get("story_title", "Untitled_Story")
    scenes = config.get("scenes", [])

    print(f"Story: {story_title}")
    print(f"Found {len(scenes)} scenes.")

    # Create story-specific directories
    story_safe_title = story_title.replace(" ", "_")
    story_images_dir = os.path.join(ASSETS_DIR, "Images", story_safe_title)
    story_video_dir = os.path.join(OUTPUT_VIDEO_DIR, story_safe_title)
    
    os.makedirs(story_images_dir, exist_ok=True)
    os.makedirs(story_video_dir, exist_ok=True)

    for scene in scenes:
        scene_id = scene.get("scene_id")
        title = scene.get("title", f"Scene_{scene_id}")
        visual_prompt = scene.get("visual")
        
        print(f"\n--- Processing Scene {scene_id}: {title} ---")
        print(f"Visual Prompt: {visual_prompt}")

        # Step 1: Text to Image
        image_filename = f"{story_safe_title}_scene_{scene_id:02d}.png"
        image_path = os.path.join(story_images_dir, image_filename)
        
        if os.path.exists(image_path):
             print(f"[Stage 1] Image already exists: {image_path}. Skipping generation.")
        else:
            print("\n[Stage 1] Generating Keyframe...")
            # We call the imported function. Note: generate_image might print its own output.
            generated_path = generate_image(visual_prompt, output_path=image_path, steps=25)
            if not generated_path:
                print("Error: Image generation failed. Skipping scene.")
                continue

        # Step 2: Image to Video
        video_filename = f"{story_safe_title}_scene_{scene_id:02d}.mp4"
        video_path = os.path.join(story_video_dir, video_filename)

        if os.path.exists(video_path):
            print(f"[Stage 2] Video already exists: {video_path}. Skipping animation.")
        else:
            print("\n[Stage 2] Animating Keyframe...")
            animate_image(image_path, output_path=video_path)

    print("="*50)
    print(f"Pipeline Complete for {story_title}!")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Content Studio Pipeline")
    parser.add_argument("json_config", type=str, help="Path to JSON configuration file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_config):
        print(f"Error: Config file not found at {args.json_config}")
        sys.exit(1)
        
    run_pipeline(args.json_config)
