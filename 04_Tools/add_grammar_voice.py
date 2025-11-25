import json
import os

# Script to add voice and rate metadata to grammar lesson JSON files

grammar_files = [
    r"C:\Users\atuls\Startup\ContentStudio\01_Scripts\English\Unit_1_Fables_and_Folk_Tales\Grammar_Present_Progressive_Tense.json",
    r"C:\Users\atuls\Startup\ContentStudio\01_Scripts\English\Unit_1_Fables_and_Folk_Tales\Grammar_Adverbs.json"
]

for file_path in grammar_files:
    print(f"Processing: {file_path}")
    
    # Read the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Add voice and rate to metadata
    data['metadata']['voice'] = 'en-US-JennyNeural'
    data['metadata']['rate'] = '-10%'
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print(f"✓ Updated: {file_path}")

print("\nAll files updated successfully!")
