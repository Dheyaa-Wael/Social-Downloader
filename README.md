# Social Downloader

Small FastAPI app for downloading videos or MP3 audio from supported URLs using [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Features

- Download video as MP4
- Download audio as MP3
- Check available video resolutions
- Download through a simple HTTP API
- Swagger docs at `/docs`

## Requirements

- Python 3
- pip
- FFmpeg

Install dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install fastapi uvicorn
```

FFmpeg setup:

- Windows: put `ffmpeg.exe` in `tools\ffmpeg.exe` or install FFmpeg and add it to `PATH`
- Linux/macOS: install FFmpeg with your package manager
- Termux: `pkg install ffmpeg`

## Notes

- Files are saved in `downloads/`
- The app keeps one active URL/download at a time
- Only URLs supported by yt-dlp work
