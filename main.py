import importlib.util
import os
import subprocess
import sys
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from starlette.background import BackgroundTask

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()

def ensure_yt_dlp():
    if importlib.util.find_spec("yt_dlp") is not None:
        print("yt-dlp is already installed.")
        return

    print("yt-dlp is not installed.")
    answer = input("Install it now? [y/n]: ").strip().lower()
    if answer != "y":
        print("Install it manually with:  pip install -r requirements.txt")
        sys.exit(1)

    print("Installing yt-dlp...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    except subprocess.CalledProcessError:
        print("Installation failed. Try:  pip install yt-dlp")
        sys.exit(1)
ensure_yt_dlp()
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
from yt_dlp.utils import DownloadError

def get_ffmpeg_location():
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)

    name = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"
    bundled = os.path.join(BASE_DIR, "tools", name)
    if os.path.isfile(bundled):
        return os.path.dirname(bundled)

    raise FileNotFoundError(
        "ffmpeg not found. Install it"
    )

def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except ValueError:
        print("this url is invalid")
        return False

def is_supported_url(url: str) -> bool:
    opts = {"quiet": True, "skip_download": True, "noplaylist": True}
    try:
        with YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=False)
        return True
    except DownloadError:
        return False

class YoutubeContent:
    URL: str
    filename: str
    formats_list:dict = {
        "2160p": False,
        "1440p": False,
        "1080p": False,
        "720p": False,
        "480p": False,
        "360p": False,
        "240p": False,
        "144p": False
    }

    def display(self):
        for resolution, available in self.formats_list.items():
            print(f"{resolution}: {available}")

    def __init__(self,URL):
        self.URL = URL
        self.filename = None
        self.formats_list = {
            "2160p": False,
            "1440p": False,
            "1080p": False,
            "720p": False,
            "480p": False,
            "360p": False,
            "240p": False,
            "144p": False
        }

    def check_resolution(self):
        ydl_opts = {
        }
        if is_supported_url(self.URL):
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.URL, download=False)
                formats = info.get('formats', [])
                for f in formats:
                    format_note = f.get("format_note")
                    if format_note == "2160p" or format_note == "2160p60":
                        self.formats_list["2160p"] = True
                    if format_note == "1440p" or format_note == "1440p60":
                        self.formats_list["1440p"] = True
                    if format_note == "1080p" or format_note == "1080p60":
                        self.formats_list["1080p"] = True
                    if format_note == "720p" or format_note == "720p60":
                        self.formats_list["720p"] = True
                    if format_note == "480p":
                        self.formats_list["480p"] = True
                    if format_note == "360p":
                        self.formats_list["360p"] = True
                    if format_note == "240p":
                        self.formats_list["240p"] = True
                    if format_note == "144p":
                        self.formats_list["144p"] = True
                    else:
                        pass
        else:
            print("Valid URL, but no video could be found or the site isn't supported.")
    
    def download_video(self,resolution):
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'merge_output_format': 'mp4',
            'ffmpeg_location': get_ffmpeg_location(),
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        }
        if is_supported_url(self.URL):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info =ydl.extract_info(self.URL, download=True)
                    self.filename = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
            except Exception as e:
                print(f"Error occurred while downloading video: {e}")

    def download_audio(self):
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'ffmpeg_location': get_ffmpeg_location(),
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        }
        if is_supported_url(self.URL):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info =ydl.extract_info(self.URL, download=True)
                    self.filename = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
            except Exception as e:
                print(f"Error occurred while downloading audio: {e}")

v1 = YoutubeContent("")

@app.post("/content/url")
def post_video_url(url: str):
    if not is_valid_url(url):
        raise HTTPException(400, "Invalid URL")
    v1.URL = url
    return {"video_url": url}

@app.get("/content/video/formats")
def check_formats():
    v1.check_resolution()
    return {"formats": v1.formats_list}

@app.post("/content/video/download")
def download_video(resolution: int):
    if resolution < 144:
        raise HTTPException(400, "Resolution must be at least 144p")
    if not v1.URL:
        raise HTTPException(400, "Set a URL first.")
    v1.download_video(resolution)
    return {"downloaded": f"Video downloaded at {resolution}p"}

@app.post("/content/audio/download")
def download_audio():
    if not v1.URL:
        raise HTTPException(400, "Set a URL first.")
    v1.download_audio()
    return {"downloaded": "Audio downloaded as mp3"}

def cleanup_file(path: Path):
    try:
        path.unlink(missing_ok=True)
    except OSError as e:
        print(f"Could not delete {path}: {e}")

@app.get("/content/downloaded/file")
def get_downloaded_file():
    path = v1.filename
    if not v1.filename:
        raise HTTPException(404, "No file has been downloaded yet.")

    media = "video/mp4" if v1.filename.suffix == ".mp4" else "audio/mpeg"
    v1.filename = None
    return FileResponse(path, media_type=media, filename=path.name, background=BackgroundTask(cleanup_file, path))