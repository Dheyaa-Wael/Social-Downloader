from yt_dlp import YoutubeDL
import os

URL = input("Enter video URL: ")
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'ffmpeg_location': os.path.dirname(os.path.abspath("ffmpeg.exe")),
}
with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)
    print(f"title: {info.get('title')}")
    print(f"uploader: {info.get('uploader')}")
    formats = info.get('formats', [])
    for f in formats:
        format_id = f.get('format_id')
        format_note = f.get('format_note', 'N/A')
        ext = f.get('ext')
        resolution = f.get('resolution', 'audio only')
        vcodec = f.get('vcodec') 
        acodec = f.get('acodec') 
        
        
        has_video = vcodec != 'none'
        has_audio = acodec != 'none'
        
        type_desc = []
        if has_video: type_desc.append("video")
        if has_audio: type_desc.append("audio")
        
        print(f"ID: {format_id} | resolution: {format_note} ({resolution}) | ext: {ext} | content: {' + '.join(type_desc)}")
chosen_format = input("enter format id: ")
ydl_opts['format'] = chosen_format
with YoutubeDL(ydl_opts) as ydl:
    ydl.download(URL)