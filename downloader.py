import os
import sys
import argparse
import time
import re
from pytubefix import YouTube
from pytubefix.cli import on_progress
import pydub
from pydub import AudioSegment
import eyed3
#from pytube import YouTube
#import moviepy
#from moviepy.config import change_settings
#import moviepy.config as mpy_config
#from moviepy import VideoFileClip

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# Set Default download folder path based on OS
default_output = os.path.join('.\\downloads' if os.name == 'nt' else './downloads')

# # Set the path to the local ffmpeg binary
# ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg' if os.name != 'nt' else 'ffmpeg.exe')
# mpy_config.FFMPEG_BINARY = ffmpeg_path


def ensure_ffmpeg_path():
    from pydub.utils import which

    base_path = os.path.join(os.path.dirname(__file__), 'ffmpeg')
    ffmpeg_bin = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
    ffprobe_bin = 'ffprobe.exe' if os.name == 'nt' else 'ffprobe'

    ffmpeg_path = os.path.join(base_path, ffmpeg_bin)
    ffprobe_path = os.path.join(base_path, ffprobe_bin)

    if os.path.isfile(ffmpeg_path) and os.path.isfile(ffprobe_path):
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffprobe = ffprobe_path
    else:
        # Fallback to system PATH
        ffmpeg_found = which("ffmpeg")
        ffprobe_found = which("ffprobe")
        if ffmpeg_found and ffprobe_found:
            AudioSegment.converter = ffmpeg_found
            AudioSegment.ffprobe = ffprobe_found
        else:
            print("Error: ffmpeg and/or ffprobe not found.")
            sys.exit(1)


def download_mp3(youtube_url, output_path=default_output):
    try:
        yt = YouTube(youtube_url)
        title = yt.title
        author = yt.author

        print(f"[MP3] Downloading: {title}")
        audio_stream = yt.streams.filter(only_audio=True).first()
        downloaded_file = audio_stream.download(output_path=output_path)

        base, _ = os.path.splitext(downloaded_file)
        mp3_file = base + '.mp3'

        audio = AudioSegment.from_file(downloaded_file)
        audio.export(mp3_file, format="mp3")
        os.remove(downloaded_file)

        audiofile = eyed3.load(mp3_file)
        if audiofile.tag is None:
            audiofile.initTag()
        audiofile.tag.title = title
        audiofile.tag.artist = author
        audiofile.tag.save()

        print(f"[MP3] Saved: {mp3_file}")
    except Exception as e:
        print(f"[MP3] Error: {e}")


def download_mp4(youtube_url, output_path=default_output):
    try:
        yt = YouTube(youtube_url)
        print(f"[MP4] Downloading: {yt.title}")
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video_stream.download(output_path=output_path)
        print(f"[MP4] Saved to {output_path}")
    except Exception as e:
        print(f"[MP4] Error: {e}")


def process_links(urls, download_types, output_folder):
    for url in urls:
        if 'mp3' in download_types:
            download_mp3(url, output_folder)
        if 'mp4' in download_types:
            download_mp4(url, output_folder)
        

def interactive_mode(download_types, output_folder):
    print("Enter YouTube URLs one at a time (type 'quit' to exit):")
    while True:
        url = input("URL: ").strip()
        if url.lower() == "quit":
            break
        if url and re.match(regex, url) is not None:
            process_links([url], download_types, output_folder)
        else:
            print("[*] Error: Invalid URL")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos as MP3 or MP4")
    parser.add_argument("-t", "--type", choices=["mp3", "mp4"], default=["mp3", "mp4"], nargs="+", help="Download type(s) (mp3, mp4, or both)")
    parser.add_argument("-l", "--link", help="Single URL to the Youtube video")
    parser.add_argument("-f", "--file", help="Path to a .txt file containing a list of YouTube URLs")
    parser.add_argument("-o", "--output", default=default_output, help="Output folder for Downloads")

    args = parser.parse_args()

    if args.file:
        if os.path.isfile(args.file):
            try:
                with open(args.file, "r") as f:
                    urls = [line.strip() for line in f.readlines() if line.strip()]
                process_links(urls, args.type, args.output)

            except Exception as e:
                print(f"[*] Error: {e}")
                quit()
        
    elif args.link:
        urls = [args.link.strip()]
        process_links(urls, args.type, args.output)

    else:
        interactive_mode(args.type, args.output)


if __name__ == "__main__":
    main()