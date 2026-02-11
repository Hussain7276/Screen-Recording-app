"""
Audio recording module using sounddevice.
"""
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from PyQt5.QtCore import QThread, pyqtSignal
import queue


class AudioRecorder(QThread):
    """Audio recorder that runs in a separate thread."""
    
    error_occurred = pyqtSignal(str)
    
    def __init__(self, output_path, sample_rate=44100, channels=2):
        super().__init__()
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.channels = channels
        self._is_recording = False
        self._audio_queue = queue.Queue()
        self._frames = []
    
    def run(self):
        """Start audio recording."""
        self._is_recording = True
        self._frames = []
        
        def callback(indata, frames, time_info, status):
            """Callback for audio stream."""
            if status:
                print(f"Audio status: {status}")
            if self._is_recording:
                self._audio_queue.put(indata.copy())
        
        try:
            # Start audio stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                dtype=np.int16
            ):
                # Collect audio data
                while self._is_recording:
                    try:
                        data = self._audio_queue.get(timeout=0.1)
                        self._frames.append(data)
                    except queue.Empty:
                        continue
            
            # Save audio file
            if self._frames:
                audio_data = np.concatenate(self._frames, axis=0)
                wavfile.write(
                    str(self.output_path),
                    self.sample_rate,
                    audio_data
                )
        
        except Exception as e:
            self.error_occurred.emit(f"Audio recording error: {str(e)}")
    
    def stop_recording(self):
        """Stop audio recording."""
        self._is_recording = False
    
    @staticmethod
    def check_microphone():
        """Check if microphone is available."""
        try:
            devices = sd.query_devices()
            for device in devices:
                if device['max_input_channels'] > 0:
                    return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_default_device():
        """Get default input device info."""
        try:
            return sd.query_devices(kind='input')
        except Exception:
            return None
