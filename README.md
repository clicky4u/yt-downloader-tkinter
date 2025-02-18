# 🎥 yt-downloader-tkinter
A Python-based YouTube video downloader with a Tkinter GUI. Supports video/audio downloads, multiple resolutions, and additional features like thumbnails and video info.

## 📌 Features
✅ Download videos or audio from YouTube  
✅ Save videos in various formats and qualities  
✅ Option to download thumbnails and video info  

## 📦 Requirements
- Python 3.x
- `yt-dlp` library
- `Pillow` (for image processing like QR codes, thumbnails)
- **FFmpeg** (Required for certain formats)

### ⚠️ Installing FFmpeg
1. Download `ffmpeg.exe` from [this link](https://www.gyan.dev/ffmpeg/builds/) (or any trusted source).
2. Move `ffmpeg.exe` to the `_internal` folder inside this project.
3. Run the script as usual.

## 🚀 Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/clicky4u/yt-downloader-tkinter.git
cd yt-downloader-tkinter
pip install -r requirements.txt
Then run: youtube_downloader.py
