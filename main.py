from yt_dlp import YoutubeDL
import os

class youtube_video:
    URL = str
    has_2160 = bool
    has_1440 = bool
    has_1080 = bool
    has_720 = bool
    has_480 = bool
    has_360 = bool
    has_240 = bool
    has_144 = bool

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
    
    def download_video(self,resolution):
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'merge_output_format': 'mp4',
            'ffmpeg_location': os.path.dirname(os.path.abspath("tools/ffmpeg.exe")),
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.URL)

    def download_audio(self):
        ydl_opts = {
            'format': 'bestaudio',
            'ffmpeg_location': os.path.dirname(os.path.abspath("tools/ffmpeg.exe")),
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.URL)


URL = input("Enter video URL: ")
video = youtube_video(URL)
video.check_resolution()
video.display()
resolution = int(input("enter resolution without (p): "))
video.download_video(resolution)