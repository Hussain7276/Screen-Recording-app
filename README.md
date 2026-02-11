# Screen Recorder Pro

A professional, feature-rich screen recording application built with Python, PyQt5, and FFmpeg.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🖥️ **Full Screen Recording** - Record your entire screen
- 📐 **Region Selection** - Select specific areas to record
- 🎤 **Audio Recording** - Optional microphone audio capture
- ⚙️ **Configurable FPS** - Choose from 10-60 FPS
- 📹 **MP4/AVI Output** - H.264 encoded video
- ⏱️ **Countdown Timer** - 3-second countdown before recording
- ⌨️ **Global Hotkeys** - Ctrl+Shift+R (Start) / Ctrl+Shift+S (Stop)
- 🔴 **Live Status** - Real-time recording timer
- 🧵 **Multi-threaded** - No GUI freezing
- 🛡️ **Error Handling** - Graceful handling of missing dependencies

## 📋 Requirements

### Python Dependencies
```
PyQt5==5.15.10
mss==9.0.1
opencv-python==4.8.1.78
numpy==1.24.3
sounddevice==0.4.6
scipy==1.11.4
keyboard==0.13.5
```

### System Dependencies
- **Python 3.10+**
- **FFmpeg** (required for video encoding)

## 🚀 Installation

### Step 1: Clone/Download this Repository
```bash
cd screen_recorder
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install FFmpeg

#### Windows:
**Option A: Direct Download**
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" variable → Add `C:\ffmpeg\bin`
4. Verify installation:
   ```cmd
   ffmpeg -version
   ```

**Option B: Using Chocolatey**
```bash
choco install ffmpeg
```

**Option C: Using Scoop**
```bash
scoop install ffmpeg
```

## 🎮 Usage

### Running the Application
```bash
python main.py
```

### Basic Workflow

1. **Configure Settings**
   - Select FPS (10-60)
   - Choose "Full Screen" or "Selected Region"
   - Enable/disable microphone recording

2. **Select Region** (Optional)
   - Click "Select Region" button
   - Click and drag on screen to select area
   - Press ESC to cancel selection

3. **Start Recording**
   - Click "Start Recording" button OR press `Ctrl+Shift+R`
   - Wait for 3-second countdown
   - Recording begins automatically

4. **Stop Recording**
   - Click "Stop Recording" button OR press `Ctrl+Shift+S`
   - Choose save location in file dialog
   - Wait for video processing

5. **Access Your Recording**
   - Default location: `screen_recorder/output/recordings/`
   - Or custom location you selected

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+R` | Start Recording |
| `Ctrl+Shift+S` | Stop Recording |
| `ESC` | Cancel region selection |

## 📦 Building Executable (EXE)

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create single executable
pyinstaller --onefile --windowed --name="ScreenRecorder" main.py

# With custom icon (optional)
pyinstaller --onefile --windowed --name="ScreenRecorder" --icon=icon.ico main.py
```

The executable will be created in `dist/ScreenRecorder.exe`

### Using Auto-py-to-exe (GUI Tool)

```bash
pip install auto-py-to-exe
auto-py-to-exe
```

Then configure through the GUI:
- Script: `main.py`
- Onefile: Yes
- Console: Window Based (hide console)
- Icon: Optional

## 📁 Project Structure

```
screen_recorder/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── ui/                          # User Interface
│   ├── __init__.py
│   ├── main_window.py          # Main GUI window
│   └── region_selector.py      # Region selection overlay
│
├── recorder/                    # Recording Logic
│   ├── __init__.py
│   ├── screen_recorder.py      # Screen capture (MSS + OpenCV)
│   ├── audio_recorder.py       # Audio capture (sounddevice)
│   └── encoder.py              # Video encoding (FFmpeg)
│
├── utils/                       # Utilities
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── timer.py                # Countdown & recording timer
│   └── hotkeys.py              # Global hotkey handler
│
└── output/                      # Output Directory
    └── recordings/              # Saved recordings
```

## ⚙️ Configuration

Edit `utils/config.py` to customize:

```python
# Recording settings
DEFAULT_FPS = 30
DEFAULT_CODEC = "mp4v"
DEFAULT_AUDIO_SAMPLE_RATE = 44100
DEFAULT_AUDIO_CHANNELS = 2

# Hotkey settings
HOTKEY_START = "ctrl+shift+r"
HOTKEY_STOP = "ctrl+shift+s"

# UI settings
COUNTDOWN_SECONDS = 3

# File settings
DEFAULT_OUTPUT_FORMAT = "mp4"
```

## 🔧 Troubleshooting

### FFmpeg Not Found
**Problem**: "FFmpeg not found" error  
**Solution**: Install FFmpeg and add to system PATH (see Installation step 3)

### No Microphone Detected
**Problem**: Audio checkbox is disabled  
**Solution**: 
- Ensure microphone is connected
- Check Windows Privacy Settings → Microphone → Allow apps to access
- Restart the application

### Recording is Laggy
**Problem**: Low FPS during recording  
**Solution**: 
- Lower FPS to 20 or 15
- Close other resource-intensive applications
- Record smaller regions instead of full screen

### Large File Sizes
**Problem**: Output files are too large  
**Solution**: Edit `recorder/encoder.py` and adjust CRF value:
```python
"-crf", "28",  # Higher = smaller file (23 is default, 18-28 recommended)
```

### Hotkeys Not Working
**Problem**: Global hotkeys don't respond  
**Solution**: Run the application as Administrator (required for global hotkeys on Windows)

### Permission Errors
**Problem**: Can't save recordings  
**Solution**: 
- Ensure you have write permissions in the output directory
- Try selecting a different save location

## 🎯 Advanced Features

### Custom Countdown Duration
Edit `utils/config.py`:
```python
COUNTDOWN_SECONDS = 5  # Change to desired seconds
```

### Change Video Codec
Edit `recorder/screen_recorder.py`:
```python
codec = "XVID"  # For AVI
codec = "mp4v"  # For MP4 (default)
```

### Adjust Audio Quality
Edit `recorder/encoder.py`:
```python
"-b:a", "320k",  # Higher = better quality (default: 192k)
```

### Custom Output Directory
Edit `utils/config.py`:
```python
OUTPUT_DIR = Path("C:/MyRecordings")  # Custom path
```

## 🐛 Known Issues

1. **Hotkeys require Administrator**: Global hotkeys on Windows need elevated privileges
2. **First recording delay**: Initial recording may have slight delay while initializing codecs
3. **No multi-monitor support yet**: Currently records primary monitor only

## 🔮 Future Enhancements

- [ ] Multi-monitor support
- [ ] Webcam overlay
- [ ] Drawing tools during recording
- [ ] Scheduled recordings
- [ ] Cloud upload integration
- [ ] Video editing features
- [ ] System audio recording
- [ ] Live streaming support

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📧 Support

If you encounter any issues or have questions:
1. Check the Troubleshooting section
2. Review closed issues on GitHub
3. Open a new issue with details

## 🙏 Acknowledgments

- **MSS** - Lightning-fast screen capture
- **PyQt5** - Professional GUI framework
- **FFmpeg** - Industry-standard video encoding
- **OpenCV** - Computer vision and video processing
- **sounddevice** - Audio capture

---

**Made with ❤️ by Python enthusiasts**

**Version**: 1.0.0  
**Last Updated**: 2025
