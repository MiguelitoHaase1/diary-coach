#!/usr/bin/env python3
"""
Automatically convert the latest Deep Thoughts to audio after a coaching session.
Can be integrated into run_multi_agent.py or run as a standalone script.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from tts_deep_thoughts import TTSConverter, MarkdownProcessor


def find_latest_deep_thoughts(directory: Path = None) -> Path:
    """Find the most recent Deep Thoughts file."""
    if directory is None:
        # Check both possible locations
        locations = [
            Path('docs/prototype/DeepThoughts'),
            Path('data/reports')
        ]
    else:
        locations = [directory]
    
    all_files = []
    for loc in locations:
        if loc.exists():
            # Handle both naming patterns
            patterns = ['**/DeepThoughts_*.md', '**/deep_thoughts_*.md']
            for pattern in patterns:
                all_files.extend(loc.glob(pattern))
    
    if not all_files:
        return None
    
    # Sort by modification time, most recent first
    return max(all_files, key=lambda f: f.stat().st_mtime)


async def convert_latest_to_audio():
    """Convert the latest Deep Thoughts to audio."""
    # Find latest file
    latest_file = find_latest_deep_thoughts()
    
    if not latest_file:
        print("No Deep Thoughts files found.")
        return False
    
    print(f"Found latest Deep Thoughts: {latest_file}")
    
    # Check if it's recent (within last 5 minutes)
    file_age = datetime.now().timestamp() - latest_file.stat().st_mtime
    if file_age > 300:  # 5 minutes
        print(f"File is {file_age/60:.1f} minutes old. Skipping auto-conversion.")
        print("To convert manually, run:")
        print(f"python scripts/tts_deep_thoughts.py {latest_file}")
        return False
    
    # Get API credentials
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_id = os.getenv('ELEVENLABS_VOICE_ID')
    
    if not api_key or not voice_id:
        print("ElevenLabs credentials not found in environment.")
        return False
    
    # Initialize converter
    converter = TTSConverter(api_key, voice_id)
    processor = MarkdownProcessor()
    
    # Read and process content
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Clean for speech
    clean_text = processor.clean_for_speech(content)
    
    # Generate output path
    output_dir = Path('data/audio')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract timestamp from filename
    timestamp = latest_file.stem.split('_', 1)[1] if '_' in latest_file.stem else datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'deep_thoughts_audio_{timestamp}.mp3'
    
    print(f"Converting to audio...")
    print(f"   Characters: {len(clean_text):,}")
    
    # Convert to speech
    result = await converter.convert_text_async(
        clean_text,
        str(output_path),
        "eleven_monolingual_v1"
    )
    
    if result['success']:
        print(f"✅ Audio saved to: {result['output_path']}")
        print(f"   File size: {result['file_size']:,} bytes")
        print(f"   Generation time: {result['duration']:.1f}s")
        return True
    else:
        print(f"❌ Error: {result['error']}")
        return False


def integrate_with_multi_agent():
    """
    Call this function at the end of run_multi_agent.py to auto-convert.
    
    Example integration in run_multi_agent.py:
    
    # At the end of main():
    from scripts.auto_tts_after_session import integrate_with_multi_agent
    integrate_with_multi_agent()
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n🎙️ Converting Deep Thoughts to audio...")
    asyncio.run(convert_latest_to_audio())


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(convert_latest_to_audio())