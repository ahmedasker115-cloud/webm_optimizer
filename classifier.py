from enum import Enum
from config import MAX_DURATION, MAX_SIZE_MB
from ffmpeg_utils import get_duration_and_size


class Category(Enum):
    PASS = "pass"
    COMPRESS_ONLY = "compress_only"
    TRIM_ONLY = "trim_only"
    TRIM_AND_COMPRESS = "trim_and_compress"


def classify(video_path):
    duration, size_mb = get_duration_and_size(video_path)

    if duration <= MAX_DURATION and size_mb <= MAX_SIZE_MB:
        return Category.PASS

    if duration <= MAX_DURATION and size_mb > MAX_SIZE_MB:
        return Category.COMPRESS_ONLY

    if duration > MAX_DURATION and size_mb <= MAX_SIZE_MB:
        return Category.TRIM_ONLY

    return Category.TRIM_AND_COMPRESS
