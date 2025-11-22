import json
import os
import re

def split_into_chunks(text, max_words=10):
    """
    Split text into sentences, and then split long sentences into chunks.
    Used for stories.
    """
    # First split into sentences
    # Split on . ! ? followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    final_chunks = []
    
    for sentence in sentences:
        words = sentence.split()
        if len(words) <= max_words:
            final_chunks.append(sentence)
        else:
            # Split long sentence into smaller chunks
            current_chunk = []
            current_length = 0
            
            for word in words:
                current_chunk.append(word)
                current_length += 1
                
                if current_length >= max_words:
                    final_chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
            
            if current_chunk:
                final_chunks.append(" ".join(current_chunk))
                
    return final_chunks

def format_timestamp(seconds):
    """Format seconds into h, m, s, ms tuple"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return h, m, s, ms

def create_srt_entries(chunks, duration, start_time):
    """
    Create SRT entries from text chunks, distributing duration proportionally.
    """
    srt_entries = []
    current_time = start_time
    
    # Calculate total characters to distribute duration proportionally
    total_chars = sum(len(chunk.replace(" ", "")) for chunk in chunks)
    
    for i, chunk in enumerate(chunks, 1):
        # Calculate duration proportional to length
        chunk_chars = len(chunk.replace(" ", ""))
        if total_chars > 0:
            chunk_duration = duration * (chunk_chars / total_chars)
        else:
            chunk_duration = duration / len(chunks)
            
        end_time = current_time + chunk_duration
        
        # Format timestamps
        start_h, start_m, start_s, start_ms = format_timestamp(current_time)
        end_h, end_m, end_s, end_ms = format_timestamp(end_time)
        
        entry = {
            "start": f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d}",
            "end": f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}",
            "text": chunk
        }
        
        srt_entries.append(entry)
        current_time = end_time
        
    return srt_entries

def generate_srt_for_poem(narration_text, duration, start_time):
    """
    Generate SRT entries for a poem scene.
    Splits by newlines to preserve poetic structure.
    """
    # Split by newlines, remove empty lines
    chunks = [line.strip() for line in narration_text.split('\n') if line.strip()]
    return create_srt_entries(chunks, duration, start_time)

def generate_srt_for_story(narration_text, duration, start_time):
    """
    Generate SRT entries for a story scene.
    Uses sentence/word chunking logic.
    """
    chunks = split_into_chunks(narration_text, max_words=10)
    return create_srt_entries(chunks, duration, start_time)

def generate_srt_from_json(json_path, output_srt_path):
    """
    Generate SRT subtitle file from JSON script.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    scenes = data.get('scenes', [])
    metadata = data.get('metadata', {})
    content_type = metadata.get('type', 'story').lower()
    
    print(f"Generating subtitles for: {metadata.get('title', 'Unknown')}")
    print(f"Type: {content_type}")
    
    all_entries = []
    srt_index = 1
    current_time = 0.0
    
    for scene in scenes:
        narration = scene.get('narration_text', '')
        duration = scene.get('duration', 10.0)
        
        if narration:
            if content_type == 'poem':
                entries = generate_srt_for_poem(narration, duration, current_time)
            else:
                entries = generate_srt_for_story(narration, duration, current_time)
            
            for entry in entries:
                srt_block = f"{srt_index}\n"
                srt_block += f"{entry['start']} --> {entry['end']}\n"
                srt_block += f"{entry['text']}\n"
                all_entries.append(srt_block)
                srt_index += 1
            
            # Advance global time by full scene duration
            current_time += duration
            
    # Write SRT file
    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_entries))
    
    print(f"SRT file created: {output_srt_path}")
    return output_srt_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SRT subtitles from JSON")
    parser.add_argument("json_path", type=str, help="Path to JSON script file")
    parser.add_argument("--output", type=str, default=None, help="Output SRT file path")
    
    args = parser.parse_args()
    
    if args.output is None:
        # Generate output path based on JSON path
        base = os.path.splitext(args.json_path)[0]
        args.output = base + ".srt"
    
    generate_srt_from_json(args.json_path, args.output)
