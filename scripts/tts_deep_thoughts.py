#!/usr/bin/env python3
"""
ElevenLabs Text-to-Speech converter for Deep Thoughts.

This script converts Deep Thoughts markdown files to natural-sounding audio
using the ElevenLabs API. It handles markdown formatting, rate limiting,
and provides a simple CLI interface for testing.
"""

import argparse
import asyncio
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs, AsyncElevenLabs

# Load environment variables
load_dotenv()


class MarkdownProcessor:
    """Process markdown text for natural speech synthesis."""

    @staticmethod
    def clean_for_speech(text: str) -> str:
        """
        Convert markdown to clean text suitable for TTS.

        Args:
            text: Raw markdown text

        Returns:
            Cleaned text optimized for speech synthesis
        """
        # Remove markdown headers but keep the text
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Convert bold/italic to plain text
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'__([^_]+)__', r'\1', text)      # Bold alt
        text = re.sub(r'_([^_]+)_', r'\1', text)        # Italic alt

        # Remove code blocks but keep content
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Inline code

        # Convert lists to natural speech
        text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

        # Remove horizontal rules
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

        # Clean up evaluation scores (A: 1/1 → A: pass)
        text = re.sub(r'([A-E]):\s*1/1', r'\1: pass', text)
        text = re.sub(r'([A-E]):\s*0/1', r'\1: fail', text)

        # Remove multiple blank lines
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # Add pauses for better speech rhythm
        text = text.replace('🎯', '... ')
        text = text.replace('💪', '... ')
        text = text.replace('🌟', '... ')

        return text.strip()


class TTSConverter:
    """Convert text to speech using ElevenLabs API."""

    def __init__(self, api_key: str, voice_id: str):
        """
        Initialize the TTS converter.

        Args:
            api_key: ElevenLabs API key
            voice_id: Selected voice ID
        """
        self.client = ElevenLabs(api_key=api_key)
        self.async_client = AsyncElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.rate_limit_delay = 0.5  # Delay between API calls

    def get_voice_settings(self,
                           stability: float = 0.75,
                           similarity_boost: float = 0.85,
                           style: float = 0.5,
                           use_speaker_boost: bool = True) -> VoiceSettings:
        """
        Get voice settings for natural speech.

        Args:
            stability: Voice consistency (0-1)
            similarity_boost: Voice similarity to original (0-1)
            style: Style exaggeration (0-1)
            use_speaker_boost: Enable speaker boost

        Returns:
            VoiceSettings object
        """
        return VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost
        )

    async def convert_text_async(self,
                                 text: str,
                                 output_path: str,
                                 model: str = "eleven_monolingual_v1"
                                 ) -> Dict[str, Any]:
        """
        Convert text to speech asynchronously.

        Args:
            text: Text to convert
            output_path: Output file path
            model: ElevenLabs model to use

        Returns:
            Dict with conversion results
        """
        start_time = time.time()

        try:
            # Generate audio
            # Note: ElevenLabs doesn't have async version for convert
            # We'll use sync version in async context
            audio_chunks = []
            for chunk in self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                voice_settings=self.get_voice_settings(),
                model_id=model
            ):
                audio_chunks.append(chunk)

            # Save to file
            with open(output_path, 'wb') as f:
                for chunk in audio_chunks:
                    f.write(chunk)

            # Get file size
            file_size = os.path.getsize(output_path)
            duration = time.time() - start_time

            return {
                'success': True,
                'output_path': output_path,
                'file_size': file_size,
                'duration': duration,
                'characters': len(text)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }

    def convert_text(self,
                     text: str,
                     output_path: str,
                     model: str = "eleven_monolingual_v1") -> Dict[str, Any]:
        """
        Convert text to speech synchronously.

        Args:
            text: Text to convert
            output_path: Output file path
            model: ElevenLabs model to use

        Returns:
            Dict with conversion results
        """
        start_time = time.time()

        try:
            # Generate audio
            audio = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                voice_settings=self.get_voice_settings(),
                model_id=model
            )

            # Save to file
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)

            # Get file size
            file_size = os.path.getsize(output_path)
            duration = time.time() - start_time

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return {
                'success': True,
                'output_path': output_path,
                'file_size': file_size,
                'duration': duration,
                'characters': len(text)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }


def find_deep_thoughts_files(directory: Path) -> list[Path]:
    """
    Find all Deep Thoughts markdown files in a directory.

    Args:
        directory: Directory to search

    Returns:
        List of Deep Thoughts file paths
    """
    # Support both naming patterns
    patterns = ['**/deep_thoughts_*.md', '**/DeepThoughts_*.md']
    files = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))
    return sorted(files, reverse=True)  # Most recent first


def generate_output_filename(input_path: Path, output_dir: Path) -> Path:
    """
    Generate output filename for audio file.

    Args:
        input_path: Input markdown file path
        output_dir: Output directory

    Returns:
        Output file path
    """
    # Extract date from filename if present
    match = re.search(r'(\d{8}_\d{6})', input_path.stem)
    if match:
        timestamp = match.group(1)
        filename = f'deep_thoughts_audio_{timestamp}.mp3'
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'deep_thoughts_audio_{timestamp}.mp3'

    return output_dir / filename


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert Deep Thoughts markdown to audio'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Input markdown file or directory (default: data/reports)'
    )
    parser.add_argument(
        '--output-dir',
        default='data/audio',
        help='Output directory for audio files'
    )
    parser.add_argument(
        '--voice-id',
        help='Override voice ID from environment'
    )
    parser.add_argument(
        '--model',
        default='eleven_monolingual_v1',
        help='ElevenLabs model to use'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Convert only the latest Deep Thoughts file'
    )
    parser.add_argument(
        '--text',
        help='Convert text directly instead of file'
    )

    args = parser.parse_args()

    # Get API credentials
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_id = args.voice_id or os.getenv('ELEVENLABS_VOICE_ID')

    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment")
        sys.exit(1)

    if not voice_id:
        print("Error: ELEVENLABS_VOICE_ID not found in environment or arguments")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize converter
    converter = TTSConverter(api_key, voice_id)
    processor = MarkdownProcessor()

    # Handle direct text input
    if args.text:
        print("Converting text to speech...")
        clean_text = processor.clean_for_speech(args.text)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f'tts_output_{timestamp}.mp3'

        result = await converter.convert_text_async(
            clean_text,
            str(output_path),
            args.model
        )

        if result['success']:
            print(f"✅ Audio saved to: {result['output_path']}")
            print(f"   File size: {result['file_size']:,} bytes")
            print(f"   Duration: {result['duration']:.1f}s")
            print(f"   Characters: {result['characters']:,}")
        else:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        return

    # Find input files
    if args.input:
        input_path = Path(args.input)
    else:
        # Check both locations
        locations = [Path('docs/prototype/DeepThoughts'), Path('data/reports')]
        files = []
        for loc in locations:
            if loc.exists():
                files.extend(find_deep_thoughts_files(loc))
        files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        if args.latest and files:
            files = files[:1]
        if files:
            input_path = files[0].parent
        else:
            input_path = Path('data/reports')

    if args.input and Path(args.input).is_file():
        files = [Path(args.input)]
    elif not args.input and files:
        pass  # Already found files above
    else:
        files = find_deep_thoughts_files(input_path)
        if args.latest and files:
            files = files[:1]

    if not files:
        print(f"No Deep Thoughts files found in {input_path}")
        sys.exit(1)

    # Convert each file
    for i, file_path in enumerate(files):
        print(f"\nProcessing {i+1}/{len(files)}: {file_path.name}")

        # Read and process markdown
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            continue

        # Clean for speech
        clean_text = processor.clean_for_speech(content)
        orig_len = len(content)
        clean_len = len(clean_text)
        print(f"   Original: {orig_len:,} chars → Cleaned: {clean_len:,} chars")

        # Generate output filename
        output_path = generate_output_filename(file_path, output_dir)

        # Convert to speech
        result = await converter.convert_text_async(
            clean_text,
            str(output_path),
            args.model
        )

        if result['success']:
            print(f"   ✅ Audio saved to: {result['output_path']}")
            print(f"   File size: {result['file_size']:,} bytes")
            print(f"   Generation time: {result['duration']:.1f}s")

            # Mobile-friendly format check
            if result['file_size'] > 10 * 1024 * 1024:  # 10MB
                print("   ⚠️  Warning: File > 10MB may be slow on mobile")
        else:
            print(f"   ❌ Error: {result['error']}")

    print(f"\n✅ Conversion complete! Audio files saved to {output_dir}")


if __name__ == '__main__':
    asyncio.run(main())
