#!/usr/bin/env python3
"""Create a word-card video from an English Coach image + audio pair.

The video is a static flashcard image synced with the pronunciation audio.
It uses ffmpeg so Hermes can send a single MP4 after `word:` creates both media files.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


DEFAULT_SIZE = 1080
DEFAULT_AUDIO_BITRATE = "192k"


def build_ffmpeg_command(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    *,
    size: int = DEFAULT_SIZE,
    audio_bitrate: str = DEFAULT_AUDIO_BITRATE,
) -> list[str]:
    """Build an ffmpeg command that turns one image and one audio file into MP4."""
    video_filter = (
        f"scale={size}:{size}:force_original_aspect_ratio=decrease,"
        f"pad={size}:{size}:(ow-iw)/2:(oh-ih)/2,"
        "format=yuv420p"
    )
    return [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-i",
        str(audio_path),
        "-vf",
        video_filter,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        audio_bitrate,
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def create_word_video(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    *,
    size: int = DEFAULT_SIZE,
    audio_bitrate: str = DEFAULT_AUDIO_BITRATE,
) -> Path:
    """Create an MP4 word-card video from an image and audio file."""
    image_path = Path(image_path)
    audio_path = Path(audio_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_ffmpeg_command(
        image_path,
        audio_path,
        output_path,
        size=size,
        audio_bitrate=audio_bitrate,
    )
    subprocess.run(command, check=True, capture_output=True, text=True)
    return output_path


def default_output_path(image_path: Path) -> Path:
    """Map assets/images/word-agent.png to assets/videos/word-agent.mp4."""
    if image_path.parent.name == "images":
        return image_path.parent.parent / "videos" / f"{image_path.stem}.mp4"
    return image_path.with_suffix(".mp4")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an English Coach word-card MP4 from image + audio."
    )
    parser.add_argument("--image", required=True, type=Path, help="Flashcard image path")
    parser.add_argument("--audio", required=True, type=Path, help="TTS audio path")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output MP4 path; defaults beside assets/videos when input is under assets/images",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=DEFAULT_SIZE,
        help="Square video size in pixels, default: 1080",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or default_output_path(args.image)
    result = create_word_video(args.image, args.audio, output_path, size=args.size)
    print(f"Video saved: {result}")
    print(f"MEDIA:{result}")


if __name__ == "__main__":
    main()
