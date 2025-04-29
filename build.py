import PyInstaller.__main__
import os
#import shutil
import platform

def build(target_platform):
    name = "ytdownload.exe" if target_platform == "windows" else "ytdownload"

    print(f"[+] Building for {target_platform.title()}...")

    PyInstaller.__main__.run([
        "downloader.py",
        "--name=" + name,
        "--onefile",
        "--noconfirm",
        "--clean"
    ])

    dist_file = os.path.join("dist", name)
    if os.path.exists(dist_file):
        print(f"[✓] Built: {dist_file}")
    else:
        print(f"[✗] Build failed for {target_platform}")

if __name__ == "__main__":
    system = platform.system().lower()

    # Build for current system
    build(system)
