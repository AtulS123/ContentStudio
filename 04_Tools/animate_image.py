import argparse
import torch
from diffusers import AutoPipelineForImage2Video
from diffusers.utils import load_image, export_to_video
import os
from datetime import datetime

def animate_image(image_path, output_path=None):
    """
    Animate an image using Wan 2.1-I2V-14B.
    """
    print(f"Initializing Wan 2.1 (I2V)...")
    print(f"Input Image: {image_path}")
    print("Note: This model is massive (14B). Expect very slow generation.")

    # Load pipeline
    # Using AutoPipeline to handle the specific class loading
    model_id = "Wan-AI/Wan2.1-I2V-14B-480P" 
    
    pipe = AutoPipelineForImage2Video.from_pretrained(
        model_id, 
        torch_dtype=torch.bfloat16
    )
    
    # Aggressive memory optimization
    print("Enabling sequential CPU offload...")
    pipe.enable_sequential_cpu_offload()
    # pipe.enable_model_cpu_offload() # Alternative if sequential is too slow, but sequential is safer for 8GB

    # Load image
    image = load_image(image_path)
    # Wan 2.1 480P expects specific resolutions, resizing to be safe
    image = image.resize((832, 480)) 

    # Generate
    print("Generating video frames...")
    frames = pipe(
        image=image, 
        num_inference_steps=25,
        frames=81, # Wan generates 81 frames by default (approx 5s at 16fps)
    ).frames[0]

    # Save
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("output", "videos", f"vid_{timestamp}.mp4")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    export_to_video(frames, output_path, fps=16)
    print(f"Video saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Animate images with Wan 2.1")
    parser.add_argument("image_path", type=str, help="Path to input image")
    parser.add_argument("--output", type=str, default=None, help="Output video path")
    
    args = parser.parse_args()
    
    animate_image(args.image_path, args.output)
