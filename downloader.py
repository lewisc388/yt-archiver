# Standard library imports
import os
import sys
import subprocess
import platform
import argparse
import re

# Third-party imports
from pytubefix import YouTube   # YouTube downloader (patched for better support)
from pytubefix.cli import on_progress   # Used for progress callbacks
from pydub.utils import which   # Finds the path to FFmpeg/ffprobe
from pydub import AudioSegment  # Audio processing (conversion to MP3)
import eyed3    # MP3 metadata tagging

# URL regex for validation
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# OS-specific default output folder
default_output = os.path.join('.\\downloads' if os.name == 'nt' else './downloads')


def ensure_ffmpeg_installed():
    # Ensures that both ffmpeg and ffprobe are installed.
    # On Linux, it attempts to install them via apt.
    # On Windows, prompts the user to install manually.
    
    def is_installed(binary):
        return which(binary) is not None

    if is_installed("ffmpeg") and is_installed("ffprobe"):
        return  # All good

    print("[*] FFmpeg or ffprobe not found. Attempting installation...")

    system = platform.system()

    try:
        if system == "Linux":
            subprocess.check_call(["sudo", "apt", "update"])
            subprocess.check_call(["sudo", "apt", "install", "-y", "ffmpeg"])
        elif system == "Windows":
            print("Please install FFmpeg manually from https://ffmpeg.org/download.html and ensure it's in your PATH.")
            input("Press Enter after installing FFmpeg to continue...")
        else:
            print(f"Unsupported OS: {system}")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Failed to install FFmpeg: {e}")
        sys.exit(1)

    if not (is_installed("ffmpeg") and is_installed("ffprobe")):
        print("[!] FFmpeg or ffprobe still not found after attempted install.")
        sys.exit(1)

    # Update ffmpeg path for pydub explicitly
    AudioSegment.converter = which("ffmpeg")
    AudioSegment.ffprobe = which("ffprobe")


def download_mp3(youtube_url, output_path=default_output):
    # Downloads the audio from a YouTube video and saves it as an MP3 file.
    # Also embeds title and author as metadata.

    try:
        yt = YouTube(youtube_url, on_progress_callback = on_progress)
        title = yt.title
        author = yt.author

        print(f"[*] MP3 Downloading: {title}")
        audio_stream = yt.streams.filter(only_audio=True).first()
        downloaded_file = audio_stream.download(output_path=output_path)

        base, _ = os.path.splitext(downloaded_file)
        mp3_file = base + '.mp3'

        audio = AudioSegment.from_file(downloaded_file)
        audio.export(mp3_file, format="mp3")
        os.remove(downloaded_file) # Remove original .webm/.m4a file

        audiofile = eyed3.load(mp3_file)
        if audiofile.tag is None:
            audiofile.initTag()
        audiofile.tag.title = title
        audiofile.tag.artist = author
        audiofile.tag.save()

        print(f"[*] MP3 Saved: {mp3_file}")
    except Exception as e:
        print(f"[!] MP3 Error: {e}")


def download_mp4(youtube_url, output_path=default_output):
    # Downloads the highest-resolution progressive MP4 video.

    try:
        yt = YouTube(youtube_url, on_progress_callback = on_progress)
        print(f"[*] MP4 Downloading: {yt.title}")
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video_stream.download(output_path=output_path)
        print(f"[*] MP4 Saved to {output_path}")
    except Exception as e:
        print(f"[!] MP4 Error: {e}")


def process_links(urls, download_types, output_folder):
    # Processes one or more YouTube URLs, downloading them as specified types (mp3/mp4).

    for url in urls:
        if 'mp3' in download_types:
            download_mp3(url, output_folder)
        if 'mp4' in download_types:
            download_mp4(url, output_folder)
        

def interactive_mode(download_types, output_folder):
    # Interactive mode to repeatedly prompt the user for YouTube URLs.

    print("Enter YouTube URLs one at a time (type 'quit' to exit):")
    while True:
        url = input("URL: ").strip()
        if url.lower() == "quit":
            break
        if url and re.match(regex, url) is not None:
            process_links([url], download_types, output_folder)
        else:
            print("[*] Error: Invalid URL")


def ensure_output_folder(path, is_default):
    
    # Ensures the output folder exists.
    # - If default path: create it if it doesn't exist.
    # - If user-specified: throw an error if it doesn't exist.
    
    if os.path.exists(path):
        return

    if is_default:
        print(f"[*] Default output folder '{path}' not found. Creating...")
        os.makedirs(path)
    else:
        print(f"[!] Error: Specified output folder '{path}' does not exist.")
        sys.exit(1)


def main():
    # Entry point: Parses arguments and runs the appropriate download method.
    # Supports:
    #   - Single URL
    #   - Batch from file
    #   - Interactive input

    ensure_ffmpeg_installed()

    parser = argparse.ArgumentParser(description="Download YouTube videos as MP3 or MP4")
    parser.add_argument("-t", "--type", choices=["mp3", "mp4"], default=["mp3", "mp4"], nargs="+", help="Download type(s) (mp3, mp4, or both)")
    parser.add_argument("-l", "--link", help="Single URL to the Youtube video")
    parser.add_argument("-f", "--file", help="Path to a .txt file containing a list of YouTube URLs")
    parser.add_argument("-o", "--output", default=default_output, help="Output folder for Downloads")

    args = parser.parse_args()

    # Check whether the output path was provided explicitly
    is_default_output = args.output == default_output
    ensure_output_folder(args.output, is_default_output)

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