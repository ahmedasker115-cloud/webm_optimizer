from pathlib import Path
from config import *
from ffmpeg_utils import run, get_duration_and_size
from utils import sanitize_filename
import os
import tempfile


def _parse_audio_bitrate(bitrate_str: str) -> int:
    try:
        s = bitrate_str.lower()
        if s.endswith('k'):
            return int(float(s[:-1]) * 1000)
        return int(s)
    except Exception:
        return 160000


def _compute_video_kbps(duration: float, audio_bps: int) -> int:
    total_bits = MAX_SIZE_MB * 8 * 1024 * 1024
    if duration <= 0:
        return 200
    target_video_bps = max(100000, int((total_bits - (audio_bps * duration)) / duration * 0.95))
    return max(50, int(target_video_bps / 1000))


def _encode_with_retry(cmd_base, output_path, initial_kbps):
    output_path = output_path.with_name(sanitize_filename(output_path.name))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    current_kbps = initial_kbps
    attempts = 0
    max_attempts = 4
    tmppath = None
    try:
        while True:
            tf = tempfile.NamedTemporaryFile(delete=False, dir=str(output_path.parent), suffix=output_path.suffix)
            tmppath = tf.name
            tf.close()

            cmd = list(cmd_base) + ["-b:v", f"{current_kbps}k", "-minrate", f"{current_kbps}k", "-maxrate", f"{current_kbps}k", tmppath]
            run(cmd)
            import shutil
            shutil.move(tmppath, str(output_path))

            final_bytes = os.path.getsize(output_path)
            allowed = int(MAX_SIZE_MB * 1024 * 1024)
            if final_bytes <= allowed or attempts >= max_attempts:
                break

            scale = (allowed / final_bytes) * 0.95
            current_kbps = max(50, int(current_kbps * scale))
            attempts += 1
            tmppath = None
    finally:
        if tmppath and os.path.exists(tmppath):
            try:
                os.remove(tmppath)
            except Exception:
                pass


def compress(input_path, output_path):
    # compute duration and audio bitrate
    try:
        duration, _ = get_duration_and_size(input_path)
    except Exception:
        duration = 0.0

    audio_bps = _parse_audio_bitrate(AUDIO_BITRATE)
    kbps = _compute_video_kbps(duration, audio_bps)

    cmd_base = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libvpx-vp9",
        "-deadline", VP9_DEADLINE,
        "-threads", str(VP9_THREADS),
        "-c:a", AUDIO_CODEC,
        "-b:a", AUDIO_BITRATE,
        "-ac", str(AUDIO_CHANNELS),
        "-ar", str(AUDIO_RATE),
    ]

    _encode_with_retry(cmd_base, output_path, kbps)


def trim(input_path, output_path):
    # simple container copy for trimming (fast and preserves quality)
    output_path = output_path.with_name(sanitize_filename(output_path.name))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tf = tempfile.NamedTemporaryFile(delete=False, dir=str(output_path.parent), suffix=output_path.suffix)
    tmppath = tf.name
    tf.close()
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-t", str(MAX_DURATION),
            "-c", "copy",
            tmppath
        ]
        run(cmd)
        import shutil
        shutil.move(tmppath, str(output_path))
    finally:
        if os.path.exists(tmppath):
            try:
                os.remove(tmppath)
            except Exception:
                pass


def trim_and_compress(input_path, output_path):
    try:
        duration, _ = get_duration_and_size(input_path)
    except Exception:
        duration = MAX_DURATION

    audio_bps = _parse_audio_bitrate(AUDIO_BITRATE)
    kbps = _compute_video_kbps(duration if duration <= MAX_DURATION else MAX_DURATION, audio_bps)

    cmd_base = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-t", str(MAX_DURATION),
        "-c:v", "libvpx-vp9",
        "-deadline", VP9_DEADLINE,
        "-threads", str(VP9_THREADS),
        "-c:a", AUDIO_CODEC,
        "-b:a", AUDIO_BITRATE,
        "-ac", str(AUDIO_CHANNELS),
        "-ar", str(AUDIO_RATE),
    ]

    _encode_with_retry(cmd_base, output_path, kbps)
