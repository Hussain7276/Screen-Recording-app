"""
Global hotkey handler for screen recorder.
"""
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import keyboard


class HotkeyHandler(QThread):
    """Handler for global hotkeys."""
    
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
    
    def __init__(self, start_key="ctrl+shift+r", stop_key="ctrl+shift+s"):
        super().__init__()
        self.start_key = start_key
        self.stop_key = stop_key
        self._is_running = True
        self._registered = False
    
    def run(self):
        """Register and listen for hotkeys."""
        try:
            # Register hotkeys
            keyboard.add_hotkey(self.start_key, self._on_start)
            keyboard.add_hotkey(self.stop_key, self._on_stop)
            self._registered = True
            
            # Keep the thread alive
            while self._is_running:
                QThread.msleep(100)
        
        except Exception as e:
            print(f"Hotkey error: {e}")
        finally:
            self._unregister()
    
    def _on_start(self):
        """Handle start recording hotkey."""
        if self._is_running:
            self.start_recording.emit()
    
    def _on_stop(self):
        """Handle stop recording hotkey."""
        if self._is_running:
            self.stop_recording.emit()
    
    def _unregister(self):
        """Unregister hotkeys."""
        if self._registered:
            try:
                keyboard.remove_hotkey(self.start_key)
                keyboard.remove_hotkey(self.stop_key)
                self._registered = False
            except:
                pass
    
    def stop(self):
        """Stop the hotkey handler."""
        self._is_running = False
        self._unregister()
        self.quit()
        self.wait()
