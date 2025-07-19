"""Extract conversations from DeepThoughts markdown files."""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any


def extract_conversation_from_markdown(
    filepath: str
) -> Dict[str, Any]:
    """Extract conversation transcript from DeepThoughts markdown file.

    Args:
        filepath: Path to the DeepThoughts markdown file

    Returns:
        Dictionary containing conversation data
    """
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract date from filename
    filename = os.path.basename(filepath)
    date_match = re.match(
        r'DeepThoughts_(\d{8})_(\d{4})\.md',
        filename
    )
    if date_match:
        date_str = date_match.group(1)
        time_str = date_match.group(2)
        timestamp = datetime.strptime(
            f"{date_str}_{time_str}",
            "%Y%m%d_%H%M"
        )
    else:
        timestamp = datetime.now()

    # Find conversation transcript section
    transcript_match = re.search(
        r'### Conversation Transcript\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )

    if not transcript_match:
        return None

    transcript = transcript_match.group(1).strip()

    # Parse conversation messages
    messages = []
    current_speaker = None
    current_content = []

    for line in transcript.split('\n'):
        # Check for speaker line
        speaker_match = re.match(r'\*\*(\w+):\*\*\s*(.*)', line)
        if speaker_match:
            # Save previous message if exists
            if current_speaker and current_content:
                messages.append({
                    "type": "user" if current_speaker == "Michael"
                    else "assistant",
                    "content": '\n'.join(current_content).strip(),
                    "timestamp": timestamp.isoformat()
                })

            # Start new message
            current_speaker = speaker_match.group(1)
            first_content = speaker_match.group(2)
            current_content = [first_content] if first_content else []
        elif line.strip() and current_speaker:
            # Continue current message
            current_content.append(line.strip())

    # Save last message
    if current_speaker and current_content:
        messages.append({
            "type": "user" if current_speaker == "Michael"
            else "assistant",
            "content": '\n'.join(current_content).strip(),
            "timestamp": timestamp.isoformat()
        })

    if not messages:
        return None

    # Create conversation data
    conversation_data = {
        "conversation_id": f"deep_thoughts_{timestamp.strftime('%Y%m%d_%H%M')}",
        "timestamp": timestamp.isoformat(),
        "messages": messages,
        "metadata": {
            "source": "deep_thoughts",
            "original_file": filename,
            "total_messages": len(messages)
        }
    }

    return conversation_data


def main():
    """Main function to extract all DeepThoughts conversations."""
    deep_thoughts_dir = "docs/prototype/DeepThoughts"
    output_dir = "data/conversations"

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Process all DeepThoughts files
    processed = 0
    skipped = 0

    for filename in sorted(os.listdir(deep_thoughts_dir)):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(deep_thoughts_dir, filename)
        print(f"Processing {filename}...")

        conversation_data = extract_conversation_from_markdown(filepath)

        if conversation_data:
            # Save to conversations directory
            output_filename = f"deep_thoughts_{filename.replace('.md', '.json')}"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, 'w') as f:
                json.dump(conversation_data, f, indent=2)

            processed += 1
            message_count = len(conversation_data['messages'])
            print(f"  ✓ Extracted {message_count} messages")
        else:
            skipped += 1
            print("  ✗ No conversation transcript found")

    print(f"\n✅ Processed {processed} files, skipped {skipped}")
    print(f"📁 Conversations saved to {output_dir}/")


if __name__ == "__main__":
    main()
