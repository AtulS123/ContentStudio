import argparse
import torch
from diffusers import FluxPipeline
import os
from datetime import datetime

def generate_image(prompt, output_path=None, steps=25, guidance_scale=3.5):
    """
    Generate an image using Flux.1-dev.
    """
    print(f"Initializing Flux.1-dev...")
    print(f"Prompt: {prompt}")
    print("Note: This model is large (12B). Expect slow generation on 8GB VRAM.")

    # Load pipeline
    # bfloat16 is recommended for Flux
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev", 
        torch_dtype=torch.bfloat16
    )
    
    # Aggressive memory optimization
    # enable_sequential_cpu_offload() is slower but saves more memory than enable_model_cpu_offload()
    print("Enabling sequential CPU offload...")
    pipe.enable_sequential_cpu_offload()
    
    # Optional: VAE slicing/tiling to save VRAM during decoding
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()

    # Generate
    print(f"Generating image ({steps} steps)...")
    image = pipe(
        prompt=prompt, 
        height=768, # Reduced from 1024 to save VRAM
        width=1024,
        num_inference_steps=steps, 
        guidance_scale=guidance_scale,
        max_sequence_length=512 # Reduced from 4096 to save VRAM
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images with Flux.1-dev")
    parser.add_argument("prompt", type=str, help="Text prompt for generation")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--steps", type=int, default=25, help="Number of inference steps (default: 25)")
    
    args = parser.parse_args()
    
    generate_image(args.prompt, args.output, args.steps)
