import argparse
import torch
from diffusers import FluxPipeline
import os
import json
from datetime import datetime

# Define workspace paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, "02_Assets")

model_id = "black-forest-labs/FLUX.1-dev"

def generate_image(prompt, output_path=None, steps=25, guidance_scale=3.5):
    """
    Generate an image using Flux.1-dev.
    """
    print(f"Initializing Flux.1-dev...")
    print(f"Prompt: {prompt}")
    print("Note: This model is large (12B). Expect slow generation on 8GB VRAM.")

    try:
        # Load pipeline
        print(f"Loading model: {model_id}")
        pipe = FluxPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.bfloat16
        )
        
        # Enable CPU offload to save VRAM
        pipe.enable_model_cpu_offload()
        
        print(f"Generating image for prompt: '{prompt}'")
        image = pipe(
            prompt=prompt, 
            height=720,   # HD Ready (optimized for tablets)
            width=1280,   # 16:9 aspect ratio
            num_inference_steps=steps, 
            guidance_scale=guidance_scale,
            max_sequence_length=512
        ).images[0]

        # Save
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join("output", "images", f"gen_{timestamp}.png")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        image.save(output_path)
        print(f"Image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"\nError during generation: {e}")
        if "401" in str(e) or "403" in str(e) or "gated" in str(e).lower():
            print("\n" + "="*60)
            print("AUTHENTICATION ERROR: Flux.1-dev requires Hugging Face login")
            print("="*60)
            print("\nFollow these steps:")
            print("1. Go to: https://huggingface.co/black-forest-labs/FLUX.1-dev")
            print("2. Click 'Agree and access repository' to accept the terms")
            print("3. Create an access token: https://huggingface.co/settings/tokens")
            print("   - Click 'New token'")
            print("   - Name it (e.g., 'flux-dev')")
            print("   - Select 'Read' permission")
            print("   - Click 'Generate token' and copy it")
            print("4. Run in terminal: huggingface-cli login")
            print("   - Paste your token when prompted")
            print("="*60)
        return None

def generate_from_json(json_path, steps=25):
    """
    Generate images for all scenes in a JSON script.
    """
    print(f"Processing JSON script: {json_path}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    story_id = data.get("metadata", {}).get("id", "Unknown_Story")
    story_title = data.get("metadata", {}).get("title", "Untitled")
    scenes = data.get("scenes", [])
    
    print(f"Story: {story_title} ({story_id})")
    print(f"Found {len(scenes)} scenes.")
    
    # Create output directory for this story based on script path
    # This mirrors the structure: 01_Scripts/... -> 02_Assets/Images/...
    script_rel_path = os.path.relpath(json_path, os.path.join(WORKSPACE_ROOT, "01_Scripts"))
    script_dir = os.path.dirname(script_rel_path)
    story_name = os.path.splitext(os.path.basename(json_path))[0]
    
    story_images_dir = os.path.join(ASSETS_DIR, "Images", script_dir, story_name)
    os.makedirs(story_images_dir, exist_ok=True)
    
    # Initialize pipeline once
    try:
        print(f"Initializing Flux.1-dev...")
        pipe = FluxPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.bfloat16
        )
        pipe.enable_sequential_cpu_offload()
        pipe.vae.enable_slicing()
        pipe.vae.enable_tiling()
    except Exception as e:
        print(f"\nError loading model: {e}")
        if "401" in str(e) or "403" in str(e) or "gated" in str(e).lower():
            print("\n" + "="*60)
            print("AUTHENTICATION ERROR: Flux.1-dev requires Hugging Face login")
            print("="*60)
            print("\nFollow these steps:")
            print("1. Go to: https://huggingface.co/black-forest-labs/FLUX.1-dev")
            print("2. Click 'Agree and access repository' to accept the terms")
            print("3. Create an access token: https://huggingface.co/settings/tokens")
            print("   - Click 'New token'")
            print("   - Name it (e.g., 'flux-dev')")
            print("   - Select 'Read' permission")
            print("   - Click 'Generate token' and copy it")
            print("4. Run in terminal: huggingface-cli login")
            print("   - Paste your token when prompted")
            print("="*60)
        return
    
    for scene in scenes:
        scene_id = scene.get("id")
        visual_prompt = scene.get("visual_prompt")
        
        if not visual_prompt:
            print(f"Skipping Scene {scene_id}: No visual prompt.")
            continue
            
        # Define output filename
        image_filename = f"scene_{scene_id:02d}.png"
        output_path = os.path.join(story_images_dir, image_filename)
        
        if os.path.exists(output_path):
            print(f"Scene {scene_id} image already exists: {output_path}. Skipping.")
            continue
            
        print(f"\nGenerating Scene {scene_id}...")
        print(f"Prompt: {visual_prompt}")
        
        # Generate
        image = pipe(
            prompt=visual_prompt, 
            height=720,   # HD Ready (optimized for tablets)
            width=1280,   # 16:9 aspect ratio
            num_inference_steps=steps, 
            guidance_scale=3.5,
            max_sequence_length=512
        ).images[0]
        
        image.save(output_path)
        print(f"Saved to: {output_path}")
        
    print("\nBatch generation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images with Flux.1-dev")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", type=str, help="Single text prompt for generation")
    group.add_argument("--json", type=str, help="Path to JSON script file for batch generation")
    
    parser.add_argument("--output", type=str, default=None, help="Output file path (for single prompt)")
    parser.add_argument("--steps", type=int, default=25, help="Number of inference steps (default: 25)")
    
    args = parser.parse_args()
    
    if args.json:
        generate_from_json(args.json, args.steps)
    else:
        generate_image(args.prompt, args.output, args.steps)
