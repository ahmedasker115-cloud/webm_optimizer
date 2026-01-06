from pathlib import Path

MAX_DURATION = 20.0          # seconds
MAX_SIZE_MB = 3.99

VIDEO_EXTS = {".webm"}

OUTPUT_DIR_NAME = "output"

VP9_CRF = 32                 # quality-balanced
VP9_DEADLINE = "good"
VP9_THREADS = 4

AUDIO_CODEC = "libopus"
AUDIO_BITRATE = "160k"       # واضح ونظيف للمشاهد
AUDIO_CHANNELS = 2
AUDIO_RATE = 48000
