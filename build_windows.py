"""
Simple helper to build BN Optimizer on Windows using PyInstaller.
Place a static ffmpeg build into the repository at `ffmpeg/bin/ffmpeg.exe` and
`ffmpeg/bin/ffprobe.exe` before running.

Usage:
    python build_windows.py

This script calls PyInstaller with a one-file build and includes the ffmpeg
binaries (if present) into the packaged executable.
"""
import os
import shutil
import subprocess
import sys
from logging_setup import logger

HERE = os.path.dirname(__file__)
ICON = os.path.join(HERE, "assets", "icon.ico")
FFMPEG_BIN = os.path.join(HERE, "ffmpeg", "bin")

def main():
    if not shutil.which("pyinstaller"):
        logger.error("PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--name=BN Optimizer",
    ]

    if os.path.exists(ICON):
        cmd.append(f"--icon={ICON}")

    # include ffmpeg binaries if they exist
    if os.path.isdir(FFMPEG_BIN):
        for exe in ("ffmpeg.exe", "ffprobe.exe"):
            src = os.path.join(FFMPEG_BIN, exe)
            if os.path.exists(src):
                # format is SRC;DEST (on Windows use ;)
                cmd.append(f"--add-binary={src};ffmpeg\\bin")

    # entry script
    cmd.append("main.py")

    logger.info("Running: %s", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == '__main__':
    main()
