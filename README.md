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

## Run

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open: http://127.0.0.1:8000/docs

## Usage

Set a URL first, then download:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/content/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DVIDEO_ID"
curl.exe "http://127.0.0.1:8000/content/video/formats"
curl.exe -X POST "http://127.0.0.1:8000/content/video/download?resolution=720"
curl.exe -OJ "http://127.0.0.1:8000/content/downloaded/file"
```

Download MP3:

```powershell
curl.exe "http://127.0.0.1:8000/content/audio/download"
curl.exe -OJ "http://127.0.0.1:8000/content/downloaded/file"
```

## Notes

- Files are saved in `downloads/`
- The app keeps one active URL/download at a time
- Only URLs supported by yt-dlp work
