# Grammar Lesson Scripts - Index

## Overview
This directory contains kid-friendly educational video scripts for crucial grammar topics from Grade 6 English curriculum.

## Organization by Unit

### Unit 1: Fables and Folk Tales
1. **Grammar_Homophones.json** - Words that sound the same but have different meanings
   - Topics: I/eye, son/sun, see/sea, ate/eight
   - Duration: ~6 scenes, ~79 seconds

2. **Grammar_Present_Progressive_Tense.json** - Actions happening right now
   - Topics: am/is/are + verb-ing formula
   - Duration: ~6 scenes, ~86 seconds

### Unit 2: Friendship
3. **Grammar_Past_Tense_Three_Forms.json** - Three ways to talk about the past
   - Topics: Simple Past, Past Progressive, Past Perfect
   - Duration: ~6 scenes, ~87 seconds

### Unit 3: Nurturing Nature
4. **Grammar_Modal_Verbs.json** - Helping verbs with special powers
   - Topics: may, should, can, must, need to, used to
   - Duration: ~6 scenes, ~83 seconds

## Script Format
All scripts follow the standard ContentStudio JSON format:
- **metadata**: ID, title, subject, class, unit, version
- **scenes**: Array of scene objects with:
  - id, title, narration_text
  - visual_prompt (for AI image generation)
  - assets (image and audio file names)
  - effect (visual effect type and parameters)
  - duration (in seconds)

## Usage
These scripts can be used with the ContentStudio pipeline:
```bash
python 04_Tools/pipeline.py 01_Scripts/English/Unit_X/Grammar_[Topic].json
```

## Future Scripts (To Be Created)
Based on crucial grammar topics:

### Unit 1 (Additional)
- Grammar_Adverbs.json
- Grammar_Contractions.json

### Unit 2 (Additional)
- Grammar_Adjectives.json
- Grammar_Prefixes_Suffixes.json

### Unit 4
- Grammar_Past_Perfect_Tense.json

### Unit 5
- Grammar_Present_Tense.json
- Grammar_Words_of_Quantity.json

## Design Principles
1. **Kid-Friendly**: Simple language, relatable examples
2. **Visual**: Clear visual prompts for each concept
3. **Engaging**: Fun characters, colorful scenes
4. **Progressive**: Builds from simple to complex
5. **Practical**: Real-life examples children can relate to

## Notes
- Each script is ~12-16 seconds per scene
- Total video length: ~75-90 seconds
- Designed for 6th grade comprehension level
- Follows CBSE curriculum alignment
