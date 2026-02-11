"""
Timer utility for countdown and recording duration.
"""
from PyQt5.QtCore import QThread, pyqtSignal
import time


class CountdownTimer(QThread):
    """Countdown timer that runs in a separate thread."""
    
    tick = pyqtSignal(int)  # Emits remaining seconds
    finished = pyqtSignal()  # Emits when countdown finishes
    
    def __init__(self, seconds=3):
        super().__init__()
        self.seconds = seconds
        self._is_running = True
    
    def run(self):
        """Run the countdown."""
        for i in range(self.seconds, 0, -1):
            if not self._is_running:
                return
            self.tick.emit(i)
            time.sleep(1)
        
        if self._is_running:
            self.finished.emit()
    
    def stop(self):
        """Stop the countdown."""
        self._is_running = False


class RecordingTimer(QThread):
    """Timer to track recording duration."""
    
    time_updated = pyqtSignal(str)  # Emits formatted time string
    
    def __init__(self):
        super().__init__()
        self._is_running = True
        self.start_time = None
    
    def run(self):
        """Run the recording timer."""
        self.start_time = time.time()
        
        while self._is_running:
            elapsed = time.time() - self.start_time
            time_str = self._format_time(elapsed)
            self.time_updated.emit(time_str)
            time.sleep(0.1)
    
    def stop(self):
        """Stop the timer."""
        self._is_running = False
    
    @staticmethod
    def _format_time(seconds):
        """Format seconds into HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
