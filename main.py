import os
import sys
import shutil
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from starlette.background import BackgroundTask
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
from yt_dlp.utils import DownloadError

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()


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

class MediaContent:
    URL: str
    progress: float
    filename: str
    folder: Path
    channel: str
    title: str
    duration_str: str
    viewers: int
    like_count: int
    thumbnail: str
    formats_list:dict = {
        "2160": False,
        "1440": False,
        "1080": False,
        "720": False,
        "480": False,
        "360": False,
        "240": False,
        "144": False
    }
    size_list:dict[str,float] = {
        "2160_size": 0,
        "1440_size": 0,
        "1080_size": 0,
        "720_size": 0,
        "480_size": 0,
        "360_size": 0,
        "240_size": 0,
        "144_size": 0
    }

    def progress_hook(self,d):
        if d['status'] == 'downloading':
            self.progress = (float(d['downloaded_bytes'])/float(d['total_bytes']))
        elif d['status'] == 'finished':
            print('finished')

    def __init__(self,URL, folder):
        self.URL = URL
        self.progress = 0
        self.folder = folder
        self.filename = None
        self.channel = "unknown"
        self.title = "unknown"
        self.duration_str = "00:00"
        self.viewers = 0
        self.like_count = 0
        self.thumbnail = None
        self.formats_list = {
            "2160": False,
            "1440": False,
            "1080": False,
            "720": False,
            "480": False,
            "360": False,
            "240": False,
            "144": False
        }

    def get_video_info(self):
        ydl_opts = {
        }
        if is_supported_url(self.URL):
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.URL, download=False)
                self.channel = info.get("channel")
                self.title = info.get("title")
                self.duration_str = info.get("duration_string")
                self.viewers = info.get("view_count")
                self.like_count = info.get("like_count")
                self.thumbnail = info.get("thumbnail")
                formats = info.get('formats', [])
                for f in formats:
                    format_size = f.get("filesize")
                    format_note = f.get("format_note")
                    if format_note == "2160p" or format_note == "2160p60":
                        self.formats_list["2160"] = True
                        self.size_list["2160_size"] = format_size / 1000000
                    if format_note == "1440p" or format_note == "1440p60":
                        self.formats_list["1440"] = True
                        self.size_list["1440_size"] = format_size / 1000000
                    if format_note == "1080p" or format_note == "1080p60":
                        self.formats_list["1080"] = True
                        self.size_list["1080_size"] = format_size / 1000000
                    if format_note == "720p" or format_note == "720p60":
                        self.formats_list["720"] = True
                        self.size_list["720_size"] = format_size / 1000000
                    if format_note == "480p":
                        self.formats_list["480"] = True
                        self.size_list["480_size"] = format_size / 1000000
                    if format_note == "360p":
                        self.formats_list["360"] = True
                        self.size_list["360_size"] = format_size / 1000000
                    if format_note == "240p":
                        self.formats_list["240"] = True
                        self.size_list["240_size"] = format_size / 1000000
                    if format_note == "144p":
                        self.formats_list["144"] = True
                        self.size_list["144_size"] = format_size / 1000000
        else:
            print("Valid URL, but no video could be found or the site isn't supported.")
    
    def download_video(self,resolution):
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'merge_output_format': 'mp4',
            'ffmpeg_location': get_ffmpeg_location(),
            'outtmpl': str(self.folder / '%(title)s.%(ext)s'),
            'progress_hooks' : [self.progress_hook],
        }
        if is_supported_url(self.URL):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info =ydl.extract_info(self.URL, download=True)
                    self.filename = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
            except Exception as e:
                print(f"Error occurred while downloading video: {e}")
        else:
            print("Valid URL, but no video could be found or the site isn't supported.")
            raise ValueError("URL not supported or no video found")

    def download_audio(self):
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'ffmpeg_location': get_ffmpeg_location(),
            'outtmpl': str(self.folder / '%(title)s.%(ext)s'),
            'progress_hooks' : [self.progress_hook],
        }
        if is_supported_url(self.URL):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info =ydl.extract_info(self.URL, download=True)
                    self.filename = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
            except Exception as e:
                print(f"Error occurred while downloading audio: {e}")
        else:
            print("Valid URL, but no audio could be found or the site isn't supported.")
            raise ValueError("URL not supported or no audio found")

jobs: dict[str, dict] = {}

def new_status():
    return {"downloaded": False, "state": "idle", "message": "No download in progress."}

def get_job(job_id: str) -> dict:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job

def cleanup_job(job_id: str):
    job = jobs.pop(job_id, None)
    if job:
        shutil.rmtree(job["content"].folder, ignore_errors=True)

@app.get("/")
def root():
    return {"message": "Welcome to the YouTube Downloader API. Use /docs for API documentation."}

@app.post("/content/url")
def post_video_url(url: str):
    if not is_valid_url(url):
        raise HTTPException(400, "Invalid URL")
    if not is_supported_url(url):
        raise HTTPException(400, "Unsupported URL")
    job_id = uuid.uuid4().hex
    folder = DOWNLOAD_DIR / job_id
    folder.mkdir()
    jobs[job_id] = {"content": MediaContent(url, folder), "status": new_status()}
    return {"job_id": job_id, "video_url": url}

@app.get("/content/{job_id}/info")
def get_video_info(job_id: str):
    content = get_job(job_id)["content"]
    content.get_video_info()
    return {
        "channel" : content.channel,
        "title" : content.title,
        "duration_string" : content.duration_str,
        "views" : content.viewers,
        "likes" : content.like_count,
        "thumbnail" : content.thumbnail,
        "formats" : content.formats_list,
        "sizes" : content.size_list,
    }

@app.post("/content/{job_id}/video/download")
def download_video(resolution: int, job_id: str):
    job = get_job(job_id)
    download_status = job["status"]
    content = job["content"]
    if resolution < 144:
        download_status["downloaded"] = False
        download_status["state"] = "error"
        download_status["message"] = "Resolution must be at least 144p"
        raise HTTPException(400, "Resolution must be at least 144p")
    if not content.URL:
        download_status["downloaded"] = False
        download_status["state"] = "error"
        download_status["message"] = "Set a URL first."
        raise HTTPException(400, "Set a URL first.")
    try:
        download_status["downloaded"] = False
        download_status["state"] = "preparing"
        download_status["message"] = f"Preparing to download video at {resolution}p"
        content.download_video(resolution)
        download_status["downloaded"] = True
        download_status["state"] = "completed"
        download_status["message"] = f"Video downloaded at {resolution}p"
        return {"download" : "Video downloaded at {resolution}p as mp4"}
    except FileNotFoundError as e:
        raise HTTPException(500, str(e))
    except (ValueError, DownloadError) as e:
        raise HTTPException(422, f"Could not download: {e}")

@app.get("/content/{job_id}/progress")
def get_progress(job_id: str):
    job = get_job(job_id)
    return {"progress" : job["content"].progress , "status" : job["status"]}

@app.get("/content/{job_id}/audio/download")
def download_audio(job_id: str):
    content = get_job(job_id)["content"]
    download_status = get_job(job_id)["status"]
    if not content.URL:
        raise HTTPException(400, "Set a URL first.")
    try:
        download_status["downloaded"] = False
        download_status["state"] = "preparing"
        download_status["message"] = f"Preparing to download audio"
        content.download_audio()
        download_status["downloaded"] = True
        download_status["state"] = "completed"
        download_status["message"] = f"Audio downloaded as mp3"
        return {"download": "Audio downloaded as mp3"}
    except FileNotFoundError as e:
        raise HTTPException(500, str(e))
    except (ValueError, DownloadError) as e:
        raise HTTPException(422, f"Could not download: {e}")

@app.get("/content/{job_id}/downloaded/file")
def get_downloaded_file(job_id: str):
    job = get_job(job_id)
    content = job["content"]
    download_status = job["status"]

    path = content.filename
    if not content.filename:
        raise HTTPException(404, "No file has been downloaded yet.")

    media = "video/mp4" if content.filename.suffix == ".mp4" else "audio/mpeg"
    content.filename = None
    download_status["downloaded"] = False
    download_status["state"] = "idle"
    download_status["message"] = "No download in progress."
    return FileResponse(path, media_type=media, filename=path.name)

@app.get("/content/{job_id}/downloaded/file/delete")
def delete_job(job_id: str):
    cleanup_job(job_id)
    return {"massage" : "job has been deleted"}