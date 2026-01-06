import subprocess
import json


def run(cmd: list):
    subprocess.run(cmd, check=True)


def probe(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path)
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def get_duration_and_size(path):
    data = probe(path)
    duration = float(data["format"]["duration"])
    size_mb = int(data["format"]["size"]) / (1024 * 1024)
    return duration, size_mb
