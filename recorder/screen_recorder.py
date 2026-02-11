"""
Screen recording module using mss and OpenCV.
"""
import mss
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class ScreenRecorder(QThread):
    """Screen recorder that runs in a separate thread."""
    
    error_occurred = pyqtSignal(str)
    frame_captured = pyqtSignal(object)  # For live preview
    
    def __init__(self, output_path, fps=30, region=None, codec="mp4v"):
        super().__init__()
        self.output_path = output_path
        self.fps = fps
        self.region = region  # (x, y, width, height) or None for full screen
        self.codec = codec
        self._is_recording = False
        self._writer = None
    
    def run(self):
        """Start screen recording."""
        self._is_recording = True
        
        try:
            with mss.mss() as sct:
                # Determine capture region
                if self.region:
                    monitor = {
                        "left": self.region[0],
                        "top": self.region[1],
                        "width": self.region[2],
                        "height": self.region[3]
                    }
                else:
                    monitor = sct.monitors[1]  # Primary monitor
                
                # Get dimensions
                width = monitor["width"]
                height = monitor["height"]
                
                # Initialize video writer
                fourcc = cv2.VideoWriter_fourcc(*self.codec)
                self._writer = cv2.VideoWriter(
                    str(self.output_path),
                    fourcc,
                    self.fps,
                    (width, height)
                )
                
                if not self._writer.isOpened():
                    self.error_occurred.emit("Failed to open video writer")
                    return
                
                # Calculate frame delay
                frame_delay = 1.0 / self.fps
                
                import time
                last_time = time.time()
                
                # Capture loop
                while self._is_recording:
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    
                    # Convert to numpy array
                    frame = np.array(screenshot)
                    
                    # Convert BGRA to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Write frame
                    self._writer.write(frame)
                    
                    # Emit frame for preview (optional)
                    self.frame_captured.emit(frame)
                    
                    # FPS control
                    current_time = time.time()
                    elapsed = current_time - last_time
                    sleep_time = max(0, frame_delay - elapsed)
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    last_time = time.time()
        
        except Exception as e:
            self.error_occurred.emit(f"Screen recording error: {str(e)}")
        
        finally:
            self._cleanup()
    
    def stop_recording(self):
        """Stop screen recording."""
        self._is_recording = False
    
    def _cleanup(self):
        """Clean up resources."""
        if self._writer:
            self._writer.release()
            self._writer = None
