from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.word_video import build_ffmpeg_command, create_word_video  # noqa: E402


def test_build_ffmpeg_command_combines_static_image_and_audio_into_square_mp4():
    command = build_ffmpeg_command(
        image_path=Path("assets/images/word-agent.png"),
        audio_path=Path("assets/audio/word-agent.mp3"),
        output_path=Path("assets/videos/word-agent.mp4"),
    )

    assert command[:5] == [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
    ]
    assert command[5] == "assets/images/word-agent.png"
    assert command[6:8] == ["-i", "assets/audio/word-agent.mp3"]
    vf = command[command.index("-vf") + 1]
    assert "scale=1080:1080:force_original_aspect_ratio=decrease" in vf
    assert "pad=1080:1080:(ow-iw)/2:(oh-ih)/2" in vf
    assert command[-1] == "assets/videos/word-agent.mp4"


def test_create_word_video_creates_parent_dir_and_runs_ffmpeg(tmp_path, monkeypatch):
    image_path = tmp_path / "images" / "word-agent.png"
    audio_path = tmp_path / "audio" / "word-agent.mp3"
    output_path = tmp_path / "videos" / "word-agent.mp4"
    image_path.parent.mkdir()
    audio_path.parent.mkdir()
    image_path.write_bytes(b"fake png")
    audio_path.write_bytes(b"fake mp3")
    calls: list[list[str]] = []

    def fake_run(command, check, capture_output, text):
        calls.append(command)
        output_path.write_bytes(b"fake mp4")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = create_word_video(image_path, audio_path, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.parent.is_dir()
    assert calls == [build_ffmpeg_command(image_path, audio_path, output_path)]


def test_create_word_video_rejects_missing_inputs(tmp_path):
    image_path = tmp_path / "missing.png"
    audio_path = tmp_path / "missing.mp3"
    output_path = tmp_path / "word.mp4"

    with pytest.raises(FileNotFoundError, match="Image file not found"):
        create_word_video(image_path, audio_path, output_path)

    image_path.write_bytes(b"fake png")
    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        create_word_video(image_path, audio_path, output_path)
