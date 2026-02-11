"""
Main window for screen recorder application.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QGroupBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor

from recorder.screen_recorder import ScreenRecorder
from recorder.audio_recorder import AudioRecorder
from recorder.encoder import VideoEncoder
from utils.timer import CountdownTimer, RecordingTimer
from utils.hotkeys import HotkeyHandler
from utils.config import (
    APP_NAME, DEFAULT_FPS, get_temp_video_path,
    get_temp_audio_path, get_output_path, check_ffmpeg,
    COUNTDOWN_SECONDS, HOTKEY_START, HOTKEY_STOP
)
from ui.region_selector import RegionSelector


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(500, 400)
        
        # Recording state
        self.is_recording = False
        self.selected_region = None
        
        # Recorder instances
        self.screen_recorder = None
        self.audio_recorder = None
        self.encoder = None
        self.countdown_timer = None
        self.recording_timer = None
        self.hotkey_handler = None
        
        # Check FFmpeg
        if not check_ffmpeg():
            QMessageBox.warning(
                self,
                "FFmpeg Not Found",
                "FFmpeg is not installed or not in PATH.\n"
                "Audio and video will not be merged properly.\n"
                "Please install FFmpeg for full functionality."
            )
        
        # Initialize UI
        self._init_ui()
        
        # Start hotkey handler
        self._init_hotkeys()
    
    def _init_ui(self):
        """Initialize user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Settings group
        settings_group = QGroupBox("Recording Settings")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)
        
        # FPS selector
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(10, 60)
        self.fps_spinbox.setValue(DEFAULT_FPS)
        fps_layout.addWidget(self.fps_spinbox)
        fps_layout.addStretch()
        settings_layout.addLayout(fps_layout)
        
        # Screen mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Screen Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Full Screen", "Selected Region"])
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        settings_layout.addLayout(mode_layout)
        
        # Select region button
        self.select_region_btn = QPushButton("Select Region")
        self.select_region_btn.clicked.connect(self._select_region)
        self.select_region_btn.setEnabled(False)
        settings_layout.addWidget(self.select_region_btn)
        
        # Enable region selection when mode changes
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        
        # Audio recording checkbox
        self.audio_checkbox = QCheckBox("Record Microphone Audio")
        self.audio_checkbox.setChecked(True)
        
        # Check if microphone is available
        if not AudioRecorder.check_microphone():
            self.audio_checkbox.setEnabled(False)
            self.audio_checkbox.setChecked(False)
            self.audio_checkbox.setText("Record Microphone Audio (No microphone detected)")
        
        settings_layout.addWidget(self.audio_checkbox)
        
        main_layout.addWidget(settings_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        # Recording status indicator
        self.status_label = QLabel("⚫ Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(14)
        self.status_label.setFont(status_font)
        status_layout.addWidget(self.status_label)
        
        # Timer label
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_font = QFont()
        timer_font.setPointSize(24)
        timer_font.setBold(True)
        self.timer_label.setFont(timer_font)
        status_layout.addWidget(self.timer_label)
        
        main_layout.addWidget(status_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🔴 Start Recording")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self._start_recording)
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #218838; }"
        )
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⬛ Stop Recording")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.clicked.connect(self._stop_recording)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #dc3545; color: white; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #c82333; }"
        )
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        # Hotkey info
        hotkey_info = QLabel(
            f"Hotkeys: {HOTKEY_START.upper()} (Start) | {HOTKEY_STOP.upper()} (Stop)"
        )
        hotkey_info.setAlignment(Qt.AlignCenter)
        hotkey_info.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(hotkey_info)
        
        main_layout.addStretch()
    
    def _init_hotkeys(self):
        """Initialize global hotkeys."""
        self.hotkey_handler = HotkeyHandler(HOTKEY_START, HOTKEY_STOP)
        self.hotkey_handler.start_recording.connect(self._start_recording)
        self.hotkey_handler.stop_recording.connect(self._stop_recording)
        self.hotkey_handler.start()
    
    def _on_mode_changed(self, mode):
        """Handle screen mode change."""
        if mode == "Selected Region":
            self.select_region_btn.setEnabled(True)
        else:
            self.select_region_btn.setEnabled(False)
            self.selected_region = None
    
    def _select_region(self):
        """Open region selector."""
        selector = RegionSelector()
        selector.region_selected.connect(self._on_region_selected)
        selector.show()
        selector.activateWindow()
    
    @pyqtSlot(tuple)
    def _on_region_selected(self, region):
        """Handle region selection."""
        self.selected_region = region
        QMessageBox.information(
            self,
            "Region Selected",
            f"Selected region: {region[2]}x{region[3]} at ({region[0]}, {region[1]})"
        )
    
    @pyqtSlot()
    def _start_recording(self):
        """Start recording with countdown."""
        if self.is_recording:
            return
        
        # Validate region selection
        if self.mode_combo.currentText() == "Selected Region" and not self.selected_region:
            QMessageBox.warning(
                self,
                "No Region Selected",
                "Please select a screen region first."
            )
            return
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.mode_combo.setEnabled(False)
        self.select_region_btn.setEnabled(False)
        self.audio_checkbox.setEnabled(False)
        self.fps_spinbox.setEnabled(False)
        
        # Start countdown
        self.countdown_timer = CountdownTimer(COUNTDOWN_SECONDS)
        self.countdown_timer.tick.connect(self._on_countdown_tick)
        self.countdown_timer.finished.connect(self._start_actual_recording)
        self.countdown_timer.start()
    
    @pyqtSlot(int)
    def _on_countdown_tick(self, remaining):
        """Handle countdown tick."""
        self.status_label.setText(f"⏱️ Starting in {remaining}...")
    
    @pyqtSlot()
    def _start_actual_recording(self):
        """Start actual recording after countdown."""
        self.is_recording = True
        
        # Update UI
        self.status_label.setText("🔴 Recording")
        self.status_label.setStyleSheet("color: red;")
        self.stop_btn.setEnabled(True)
        
        # Get FPS
        fps = self.fps_spinbox.value()
        
        # Determine region
        region = None
        if self.mode_combo.currentText() == "Selected Region":
            region = self.selected_region
        
        # Start screen recorder
        video_path = get_temp_video_path()
        self.screen_recorder = ScreenRecorder(video_path, fps, region)
        self.screen_recorder.error_occurred.connect(self._on_error)
        self.screen_recorder.start()
        
        # Start audio recorder if enabled
        if self.audio_checkbox.isChecked():
            audio_path = get_temp_audio_path()
            self.audio_recorder = AudioRecorder(audio_path)
            self.audio_recorder.error_occurred.connect(self._on_error)
            self.audio_recorder.start()
        
        # Start recording timer
        self.recording_timer = RecordingTimer()
        self.recording_timer.time_updated.connect(self._on_timer_update)
        self.recording_timer.start()
    
    @pyqtSlot(str)
    def _on_timer_update(self, time_str):
        """Update timer display."""
        self.timer_label.setText(time_str)
    
    @pyqtSlot()
    def _stop_recording(self):
        """Stop recording."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Update UI
        self.status_label.setText("⏹️ Processing...")
        self.status_label.setStyleSheet("color: orange;")
        self.stop_btn.setEnabled(False)
        
        # Stop timers
        if self.recording_timer:
            self.recording_timer.stop()
            self.recording_timer.wait()
        
        # Stop recorders
        if self.screen_recorder:
            self.screen_recorder.stop_recording()
            self.screen_recorder.wait()
        
        if self.audio_recorder:
            self.audio_recorder.stop_recording()
            self.audio_recorder.wait()
        
        # Choose output location
        default_path = str(get_output_path())
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recording",
            default_path,
            "MP4 Video (*.mp4);;AVI Video (*.avi)"
        )
        
        if output_path:
            # Start encoding
            video_path = get_temp_video_path()
            audio_path = get_temp_audio_path() if self.audio_checkbox.isChecked() else None
            
            self.encoder = VideoEncoder(video_path, audio_path, output_path)
            self.encoder.progress_updated.connect(self._on_encoding_progress)
            self.encoder.encoding_finished.connect(self._on_encoding_finished)
            self.encoder.start()
        else:
            # Cancelled, reset UI
            self._reset_ui()
    
    @pyqtSlot(str)
    def _on_encoding_progress(self, message):
        """Handle encoding progress."""
        self.status_label.setText(f"⚙️ {message}")
    
    @pyqtSlot(bool, str)
    def _on_encoding_finished(self, success, message):
        """Handle encoding completion."""
        if success:
            QMessageBox.information(self, "Success", message)
            self.status_label.setText("✅ Ready")
            self.status_label.setStyleSheet("color: green;")
        else:
            QMessageBox.critical(self, "Error", message)
            self.status_label.setText("❌ Error")
            self.status_label.setStyleSheet("color: red;")
        
        self._reset_ui()
    
    @pyqtSlot(str)
    def _on_error(self, error_message):
        """Handle recording error."""
        QMessageBox.critical(self, "Recording Error", error_message)
        self.is_recording = False
        self._reset_ui()
    
    def _reset_ui(self):
        """Reset UI to ready state."""
        self.timer_label.setText("00:00:00")
        self.status_label.setText("⚫ Ready")
        self.status_label.setStyleSheet("")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.mode_combo.setEnabled(True)
        self.fps_spinbox.setEnabled(True)
        
        if AudioRecorder.check_microphone():
            self.audio_checkbox.setEnabled(True)
        
        if self.mode_combo.currentText() == "Selected Region":
            self.select_region_btn.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle window close."""
        # Stop hotkeys
        if self.hotkey_handler:
            self.hotkey_handler.stop()
        
        # Stop recording if active
        if self.is_recording:
            reply = QMessageBox.question(
                self,
                "Recording in Progress",
                "Recording is in progress. Stop and exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.screen_recorder:
                    self.screen_recorder.stop_recording()
                if self.audio_recorder:
                    self.audio_recorder.stop_recording()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
