import PyInstaller.__main__
import os
import platform

is_windows = platform.system() == "Windows"
ffmpeg_dir = os.path.abspath("ffmpeg")

# ffmpeg and ffprobe binary names
ffmpeg_bin = "ffmpeg.exe" if is_windows else "ffmpeg"
ffprobe_bin = "ffprobe.exe" if is_windows else "ffprobe"

PyInstaller.__main__.run([
    "downloader.py",
    "--name=ytdownload",
    "--onefile",
    "--add-data=" + os.path.join(ffmpeg_dir, ffmpeg_bin) + os.pathsep + "ffmpeg",
    "--add-data=" + os.path.join(ffmpeg_dir, ffprobe_bin) + os.pathsep + "ffmpeg",
    "--clean",
    "--noconfirm",
])


