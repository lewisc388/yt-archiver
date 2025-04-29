@echo off
set PYINSTALLER=pyinstaller
set SCRIPT=downloader.py
set FFMPEG=ffmpeg.exe

REM Ensure ffmpeg.exe is in the same folder as this script
if not exist %FFMPEG% (
    echo ERROR: ffmpeg.exe not found in current directory.
    exit /b 1
)

%PYINSTALLER% --onefile --add-binary "%FFMPEG%;." %SCRIPT%

echo.
echo Build complete. Your executable is in the dist\ folder.
pause
