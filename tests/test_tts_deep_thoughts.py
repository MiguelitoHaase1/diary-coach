"""Tests for the TTS Deep Thoughts converter."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from tts_deep_thoughts import (  # noqa: E402
    MarkdownProcessor, TTSConverter,
    find_deep_thoughts_files, generate_output_filename
)


class TestMarkdownProcessor:
    """Test markdown processing for speech."""

    def test_removes_headers(self):
        """Should remove markdown headers but keep text."""
        processor = MarkdownProcessor()
        text = "# Header 1\n## Header 2\nContent"
        result = processor.clean_for_speech(text)
        assert "Header 1" in result
        assert "Header 2" in result
        assert "#" not in result

    def test_removes_formatting(self):
        """Should remove bold/italic formatting."""
        processor = MarkdownProcessor()
        text = "This is **bold** and *italic* text"
        result = processor.clean_for_speech(text)
        assert result == "This is bold and italic text"

    def test_converts_lists(self):
        """Should convert markdown lists to bullet points."""
        processor = MarkdownProcessor()
        text = "- Item 1\n- Item 2\n1. Numbered item"
        result = processor.clean_for_speech(text)
        assert "• Item 1" in result
        assert "• Item 2" in result
        assert "Numbered item" in result
        assert "1." not in result

    def test_removes_links(self):
        """Should remove link syntax but keep text."""
        processor = MarkdownProcessor()
        text = "This is a [link](https://example.com) in text"
        result = processor.clean_for_speech(text)
        assert result == "This is a link in text"

    def test_cleans_evaluation_scores(self):
        """Should convert evaluation scores to readable format."""
        processor = MarkdownProcessor()
        text = "A: 1/1 - Success\nB: 0/1 - Failed"
        result = processor.clean_for_speech(text)
        assert "A: pass" in result
        assert "B: fail" in result

    def test_adds_pauses_for_emojis(self):
        """Should replace emojis with pauses."""
        processor = MarkdownProcessor()
        text = "Achievement 🎯 Complete"
        result = processor.clean_for_speech(text)
        assert "Achievement ...  Complete" in result


class TestTTSConverter:
    """Test TTS conversion functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock ElevenLabs client."""
        with patch('tts_deep_thoughts.ElevenLabs') as mock:
            yield mock

    @pytest.fixture
    def mock_async_client(self):
        """Mock async ElevenLabs client."""
        with patch('tts_deep_thoughts.AsyncElevenLabs') as mock:
            yield mock

    def test_voice_settings(self, mock_client, mock_async_client):
        """Should create proper voice settings."""
        converter = TTSConverter("test_key", "test_voice")
        settings = converter.get_voice_settings()

        assert settings.stability == 0.75
        assert settings.similarity_boost == 0.85
        assert settings.style == 0.5
        assert settings.use_speaker_boost is True

    def test_custom_voice_settings(self, mock_client, mock_async_client):
        """Should allow custom voice settings."""
        converter = TTSConverter("test_key", "test_voice")
        settings = converter.get_voice_settings(
            stability=0.5,
            similarity_boost=0.9,
            style=0.7,
            use_speaker_boost=False
        )

        assert settings.stability == 0.5
        assert settings.similarity_boost == 0.9
        assert settings.style == 0.7
        assert settings.use_speaker_boost is False

    @pytest.mark.asyncio
    async def test_convert_text_async_success(self, mock_client, mock_async_client):
        """Should convert text successfully."""
        # Setup mock
        mock_instance = AsyncMock()
        mock_async_client.return_value = mock_instance

        # Mock audio generation
        async def mock_audio_generator():
            yield b'audio_chunk_1'
            yield b'audio_chunk_2'

        mock_instance.generate.return_value = mock_audio_generator()

        # Test conversion
        converter = TTSConverter("test_key", "test_voice")
        result = await converter.convert_text_async(
            "Test text",
            "/tmp/test_output.mp3"
        )

        assert result['success'] is True
        assert result['characters'] == 9
        assert 'duration' in result

    @pytest.mark.asyncio
    async def test_convert_text_async_error(self, mock_client, mock_async_client):
        """Should handle conversion errors."""
        # Setup mock to raise error on the sync client (since async uses sync internally)
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.text_to_speech.convert.side_effect = Exception("API Error")

        # Test conversion
        converter = TTSConverter("test_key", "test_voice")
        result = await converter.convert_text_async(
            "Test text",
            "/tmp/test_output.mp3"
        )

        assert result['success'] is False
        assert "API Error" in result['error']
        assert 'duration' in result

    def test_convert_text_sync(self, mock_client, mock_async_client):
        """Should convert text synchronously."""
        # Setup mock
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock audio generation
        mock_instance.generate.return_value = [b'audio_chunk_1', b'audio_chunk_2']

        # Mock file operations
        with patch('builtins.open', create=True):
            with patch('os.path.getsize', return_value=1024):
                with patch('time.sleep'):  # Skip rate limiting
                    # Test conversion
                    converter = TTSConverter("test_key", "test_voice")
                    result = converter.convert_text(
                        "Test text",
                        "/tmp/test_output.mp3"
                    )

        assert result['success'] is True
        assert result['file_size'] == 1024
        assert result['characters'] == 9


class TestFileOperations:
    """Test file discovery and naming."""

    def test_find_deep_thoughts_files(self):
        """Should find Deep Thoughts files."""
        # Mock both glob patterns
        with patch('pathlib.Path.glob') as mock_glob:
            # Return empty for first pattern, files for second
            mock_glob.side_effect = [
                [],  # DeepThoughts_* pattern
                [    # deep_thoughts_* pattern
                    Path('data/reports/deep_thoughts_20250128_120000.md'),
                    Path('data/reports/deep_thoughts_20250127_120000.md')
                ]
            ]

            files = find_deep_thoughts_files(Path('data/reports'))

            assert len(files) == 2
            # Should be sorted most recent first
            assert '20250128' in str(files[0])
            assert '20250127' in str(files[1])

    def test_generate_output_filename_with_timestamp(self):
        """Should extract timestamp from input filename."""
        input_path = Path('deep_thoughts_20250128_120000.md')
        output_dir = Path('/tmp')

        result = generate_output_filename(input_path, output_dir)

        assert result.name == 'deep_thoughts_audio_20250128_120000.mp3'
        assert result.parent == output_dir

    def test_generate_output_filename_without_timestamp(self):
        """Should generate timestamp if not in filename."""
        input_path = Path('deep_thoughts.md')
        output_dir = Path('/tmp')

        with patch('tts_deep_thoughts.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20250128_150000'
            result = generate_output_filename(input_path, output_dir)

        assert result.name == 'deep_thoughts_audio_20250128_150000.mp3'


class TestCLIIntegration:
    """Test CLI functionality."""

    @pytest.mark.asyncio
    async def test_main_with_text_input(self):
        """Should convert direct text input."""
        test_args = [
            'tts_deep_thoughts.py',
            '--text', 'Hello world',
            '--voice-id', 'test_voice'
        ]

        with patch('sys.argv', test_args):
            with patch.dict(os.environ, {'ELEVENLABS_API_KEY': 'test_key'}):
                with patch('tts_deep_thoughts.TTSConverter') as mock_converter:
                    mock_instance = Mock()
                    mock_converter.return_value = mock_instance

                    # Mock async conversion
                    mock_instance.convert_text_async = AsyncMock(return_value={
                        'success': True,
                        'output_path': '/tmp/output.mp3',
                        'file_size': 1024,
                        'duration': 1.5,
                        'characters': 11
                    })

                    # Import and run main
                    from tts_deep_thoughts import main
                    await main()

                    # Verify conversion was called
                    mock_instance.convert_text_async.assert_called_once()
                    call_args = mock_instance.convert_text_async.call_args[0]
                    assert "Hello world" in call_args[0]
