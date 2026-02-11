"""
Video encoder module for muxing video and audio with FFmpeg.
"""
import subprocess
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal


class VideoEncoder(QThread):
    """Video encoder that muxes video and audio."""
    
    progress_updated = pyqtSignal(str)
    encoding_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, video_path, audio_path, output_path):
        super().__init__()
        self.video_path = Path(video_path)
        self.audio_path = Path(audio_path)
        self.output_path = Path(output_path)
    
    def run(self):
        """Mux video and audio using FFmpeg."""
        try:
            # Check if files exist
            if not self.video_path.exists():
                self.encoding_finished.emit(
                    False,
                    f"Video file not found: {self.video_path}"
                )
                return
            
            # Check if audio exists
            has_audio = self.audio_path.exists()
            
            if has_audio:
                # Mux video and audio
                self.progress_updated.emit("Muxing video and audio...")
                cmd = [
                    "ffmpeg",
                    "-i", str(self.video_path),
                    "-i", str(self.audio_path),
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-y",  # Overwrite output file
                    str(self.output_path)
                ]
            else:
                # Only video, no audio
                self.progress_updated.emit("Encoding video...")
                cmd = [
                    "ffmpeg",
                    "-i", str(self.video_path),
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-y",
                    str(self.output_path)
                ]
            
            # Run FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Wait for completion
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.progress_updated.emit("Encoding complete!")
                self.encoding_finished.emit(
                    True,
                    f"Recording saved to: {self.output_path}"
                )
                
                # Clean up temporary files
                self._cleanup_temp_files()
            else:
                self.encoding_finished.emit(
                    False,
                    f"FFmpeg error: {stderr}"
                )
        
        except FileNotFoundError:
            self.encoding_finished.emit(
                False,
                "FFmpeg not found. Please install FFmpeg and add it to PATH."
            )
        except Exception as e:
            self.encoding_finished.emit(
                False,
                f"Encoding error: {str(e)}"
            )
    
    def _cleanup_temp_files(self):
        """Remove temporary video and audio files."""
        try:
            if self.video_path.exists():
                self.video_path.unlink()
            if self.audio_path.exists():
                self.audio_path.unlink()
        except Exception as e:
            print(f"Cleanup error: {e}")
