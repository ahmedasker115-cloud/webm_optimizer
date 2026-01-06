import os
import subprocess
from config import MAX_DURATION, MAX_SIZE_MB
from utils import ensure_folder, mb_to_bytes


def optimize_webm(file_path, output_dir=None):
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    output_dir = output_dir or os.path.dirname(file_path)
    ensure_folder(output_dir)
    output_file = os.path.join(output_dir, f"{name}_optimized.webm")
    
    # جلب مدة الفيديو
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    duration = float(result.stdout)
    
    # trim duration
    trim_duration = min(duration, MAX_DURATION)
    
    # حساب حجم البتريت للفيديو
    # حجم الملف النهائي = (Video_bitrate + Audio_bitrate) * duration
    # حجم البايت النهائي = MAX_SIZE_MB * 1024 * 1024
    # Audio bitrate ثابت 192 kbps
    audio_bitrate_kbps = 192
    max_total_bitrate = (MAX_SIZE_MB * 8192) / trim_duration  # kbps
    video_bitrate_kbps = max_total_bitrate - audio_bitrate_kbps
    if video_bitrate_kbps < 100:  # لا نخفض البتريت للفيديو بشكل مبالغ فيه
        video_bitrate_kbps = 100

    # أمر ffmpeg
    cmd = ["ffmpeg", "-y", "-i", file_path]
    
    if trim_duration < duration:
        cmd += ["-t", str(trim_duration)]
    
    cmd += [
        "-c:v", "libvpx-vp9",
        "-b:v", f"{int(video_bitrate_kbps)}k",
        "-c:a", "libopus",
        "-b:a", f"{audio_bitrate_kbps}k",
        output_file
    ]
    
    subprocess.run(cmd, stderr=subprocess.DEVNULL)
    return output_file
