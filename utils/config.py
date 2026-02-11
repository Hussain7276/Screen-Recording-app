"""
Configuration module for screen recorder.
Contains default settings and paths.
"""
import os
from pathlib import Path

# Application settings
APP_NAME = "Screen Recorder Pro"
APP_VERSION = "1.0.0"

# Recording settings
DEFAULT_FPS = 30
DEFAULT_CODEC = "mp4v"
DEFAULT_AUDIO_SAMPLE_RATE = 44100
DEFAULT_AUDIO_CHANNELS = 2

# File settings
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "recordings"
TEMP_VIDEO_NAME = "temp_video.avi"
TEMP_AUDIO_NAME = "temp_audio.wav"
DEFAULT_OUTPUT_FORMAT = "mp4"

# UI settings
COUNTDOWN_SECONDS = 3
TIMER_UPDATE_INTERVAL = 100  # milliseconds

# Hotkey settings
HOTKEY_START = "ctrl+shift+r"
HOTKEY_STOP = "ctrl+shift+s"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_temp_video_path():
    """Get temporary video file path."""
    return OUTPUT_DIR / TEMP_VIDEO_NAME


def get_temp_audio_path():
    """Get temporary audio file path."""
    return OUTPUT_DIR / TEMP_AUDIO_NAME


def get_output_path(filename=None):
    """Get output file path with timestamp if no filename provided."""
    if filename:
        return OUTPUT_DIR / filename
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUT_DIR / f"recording_{timestamp}.{DEFAULT_OUTPUT_FORMAT}"


def check_ffmpeg():
    """Check if FFmpeg is available in system PATH."""
    import subprocess
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
