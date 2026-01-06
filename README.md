BN Optimizer
- Validates WebM videos
- Max 20s / 3.99MB
- Preserves quality and audio clarity
- Safe output folder, same filenames

Build (Windows) - one-file executable

1. Install dependencies in your venv:

```powershell
python -m pip install -r requirements.txt
```

2. Place a static Windows ffmpeg build under `ffmpeg/bin/ffmpeg.exe` and `ffmpeg/bin/ffprobe.exe`.

3. Run the build helper:

```powershell
python build_windows.py
```

This calls `pyinstaller` to create a single-file Windows executable. The script will include
ffmpeg binaries if they are present under `ffmpeg/bin`.

Notes
- App name: BN Optimizer
- Icon placeholder: `assets/icon.ico` (replace with a real ICO before building)

GUI
- Small theme toggle (black/red) is available in the top bar.

ffmpeg handling
- The app will look for local `ffmpeg`/`ffprobe` under `./ffmpeg/bin` first, then the system PATH.
- If ffmpeg is missing, operations that require probing/encoding will raise informative errors.
