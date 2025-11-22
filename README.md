# ContentStudio

ContentStudio is a local AI-powered pipeline for creating educational videos from text scripts. It transforms structured JSON content into engaging slideshow-style videos with narration, visual effects, and background music.

## Directory Structure

*   **`01_Scripts/`**: JSON configuration files defining the story, scenes, narration, and effects. This is the source of truth for video generation.
*   **`02_Assets/`**: Generated raw assets.
    *   `Audio/`: TTS audio files for narration.
    *   `Images/`: AI-generated keyframes (Flux.1-dev).
*   **`03_Output_Video/`**: Final rendered MP4 videos.
*   **`04_Tools/`**: Python scripts for the generation pipeline.
*   **`content/`**: Raw extracted text from source books and initial markdown drafts.

## Workflow

1.  **Scripting**: Create a JSON file in `01_Scripts/` (e.g., `ENG_U1_S1.json`) defining the scenes, narration, and visual prompts.
2.  **Asset Generation**: Run the pipeline to generate images and audio based on the JSON.
3.  **Video Assembly**: The pipeline assembles the assets into a video, applying specified effects (zoom, pan, etc.).

## Requirements

*   Python 3.10+
*   `torch`, `diffusers`, `transformers`, `accelerate`
*   `moviepy` (for video assembly)
*   NVIDIA GPU (recommended for faster generation)

## Usage

```bash
python 04_Tools/pipeline.py 01_Scripts/Your_Script.json
```
