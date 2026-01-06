from pathlib import Path
from config import *
from ffmpeg_utils import run


def compress(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libvpx-vp9",
        "-crf", str(VP9_CRF),
        "-b:v", "0",
        "-deadline", VP9_DEADLINE,
        "-threads", str(VP9_THREADS),
        "-c:a", AUDIO_CODEC,
        "-b:a", AUDIO_BITRATE,
        "-ac", str(AUDIO_CHANNELS),
        "-ar", str(AUDIO_RATE),
        str(output_path)
    ]
    run(cmd)

def trim(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-t", str(MAX_DURATION),
        "-c", "copy",
        str(output_path)
    ]
    run(cmd)

def trim_and_compress(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-t", str(MAX_DURATION),
        "-c:v", "libvpx-vp9",
        "-crf", str(VP9_CRF),
        "-b:v", "0",
        "-deadline", VP9_DEADLINE,
        "-threads", str(VP9_THREADS),
        "-c:a", AUDIO_CODEC,
        "-b:a", AUDIO_BITRATE,
        "-ac", str(AUDIO_CHANNELS),
        "-ar", str(AUDIO_RATE),
        str(output_path)
    ]
    run(cmd)
