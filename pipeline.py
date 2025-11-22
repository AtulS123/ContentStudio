import argparse
import os
import sys
from scripts.generate_image import generate_image
from scripts.animate_image import animate_image

def run_pipeline(prompt):
    """
    Run the full Text-to-Video pipeline.
    """
    print("="*50)
    print(f"Starting Content Generation Pipeline")
    print(f"Prompt: {prompt}")
    print("="*50)

    # Step 1: Text to Image
    print("\n[Stage 1] Generating Keyframe...")
    image_path = generate_image(prompt, steps=4) # 4 steps for better quality with SDXL Turbo
    
    if not image_path or not os.path.exists(image_path):
        print("Error: Image generation failed.")
        return

    # Step 2: Image to Video
    print("\n[Stage 2] Animating Keyframe...")
    video_path = animate_image(image_path)

    print("="*50)
    print(f"Pipeline Complete!")
    print(f"Generated Video: {video_path}")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Content Studio Pipeline")
    parser.add_argument("prompt", type=str, help="Text prompt for video generation")
    
    args = parser.parse_args()
    
    run_pipeline(args.prompt)
