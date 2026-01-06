import subprocess
import json
import shutil
import os


def _find_executable(name: str):
    # prefer bundled ffmpeg/ffprobe in ./ffmpeg/bin, then PATH
    local = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", name)
    if os.path.exists(local):
        return local
    which = shutil.which(name)
    if which:
        return which
    return name


def run(cmd: list):
    # replace command name with absolute path if possible
    if cmd:
        if os.path.basename(cmd[0]) in ("ffmpeg", "ffmpeg.exe"):
            cmd[0] = _find_executable("ffmpeg.exe" if os.name == "nt" else "ffmpeg")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        # surface stderr/stdout for debugging
        raise RuntimeError(f"ffmpeg failed: {e}") from e


def probe(path):
    ffprobe = _find_executable("ffprobe.exe" if os.name == "nt" else "ffprobe")
    cmd = [
        ffprobe, "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path)
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {p.stderr}")
    return json.loads(p.stdout)


def get_duration_and_size(path):
    data = probe(path)
    fmt = data.get("format", {})
    try:
        duration = float(fmt.get("duration", 0.0))
    except Exception:
        duration = 0.0
    try:
        size_mb = float(fmt.get("size", 0.0)) / (1024 * 1024)
    except Exception:
        size_mb = 0.0
    return duration, size_mb
