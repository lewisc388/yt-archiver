#!/bin/bash

SCRIPT="downloader.py"
FFMPEG="ffmpeg"

# Check for ffmpeg binary
if [ ! -f "$FFMPEG" ]; then
    echo "ERROR: ffmpeg not found in current directory."
    exit 1
fi

# Make ffmpeg executable just in case
chmod +x ffmpeg

pyinstaller --onefile --add-binary "$FFMPEG:." "$SCRIPT"

echo ""
echo "Build complete. Your executable is in the dist/ directory."
