import os
import sys
import shutil
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
from yt_dlp.utils import DownloadError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

class youtube_video:
    URL: str
    has_2160: bool
    has_1440: bool
    has_1080: bool
    has_720: bool
    has_480: bool
    has_360: bool
    has_240: bool
    has_144: bool

    def display(self):
        print(f"2160p: {self.has_2160}")
        print(f"1440p: {self.has_1440}")
        print(f"1080p: {self.has_1080}")
        print(f"720p: {self.has_720}")
        print(f"480p: {self.has_480}")
        print(f"360p: {self.has_360}")
        print(f"240p: {self.has_240}")
        print(f"144p: {self.has_144}")

    def __init__(self,URL):
        self.URL = URL
        self.has_2160 = False
        self.has_1440 = False
        self.has_1080 = False
        self.has_720 = False
        self.has_480 = False
        self.has_360 = False
        self.has_240 = False
        self.has_144 = False

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
                        self.has_2160 = True
                    elif format_note == "1440p" or format_note == "1440p60":
                        self.has_1440 = True
                    elif format_note == "1080p" or format_note == "1080p60":
                        self.has_1080 = True
                    elif format_note == "720p" or format_note == "720p60":
                        self.has_720 = True
                    elif format_note == "480p":
                        self.has_480 = True
                    elif format_note == "360p":
                        self.has_360 = True
                    elif format_note == "240p":
                        self.has_240 = True
                    elif format_note == "144p":
                        self.has_144 = True
                    else:
                        pass
        else:
            print("Valid URL, but no video could be found or the site isn't supported.")
    
    def download_video(self,resolution):
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'merge_output_format': 'mp4',
            'ffmpeg_location': get_ffmpeg_location(),
        }
        if is_supported_url(self.URL):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download(self.URL)
            except Exception as e:
                print(f"Error occurred while downloading video: {e}")

    def download_audio(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': get_ffmpeg_location(),
        }
        if is_supported_url(self.URL):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download(self.URL)
            except Exception as e:
                print(f"Error occurred while downloading audio: {e}")

def main():
    while True:
        URL = input("Enter video URL: ").strip()
        if not is_valid_url(URL):
            print("That doesn't look like a valid URL.")
            continue
        if not is_supported_url(URL):
            print("Valid URL, but no video could be found or the site isn't supported.")
            continue
        break

    video = youtube_video(URL)
    while True:
        try:
            choice = int(input("[1] download video [2] download audio: "))
        except ValueError:
            print("Please enter a valid number.")
            continue
        if choice == 1:
            video.check_resolution()
            video.display()
            while True:
                try:
                    resolution = int(input("enter resolution without (p): "))
                except ValueError:
                    print("Please enter a valid number.")
                    continue
                if resolution >= 144:
                    video.download_video(resolution)
                    break
                else:
                    print("Enter valid resolution")
                    continue
            break
        elif choice == 2:
            video.download_audio()
            break
        else:
            print("enter valid number")
            continue

if __name__ == "__main__":
    main()