from pathlib import Path
from queue import Queue
from workers import EncodeWorker
from classifier import classify, Category
from config import VIDEO_EXTS, MAX_DURATION, MAX_SIZE_MB
from ffmpeg_utils import probe
import shutil
import os
from logging_setup import logger

TEST_DIR = Path("test_videos")
OUT_DIR = TEST_DIR / "output_smoke"


def ensure_out():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def scan_and_classify():
    groups = {c: [] for c in Category}
    for f in TEST_DIR.iterdir():
        if f.suffix.lower() in VIDEO_EXTS:
            try:
                cat = classify(f)
            except Exception as e:
                logger.exception(f"ERROR classify raised for {f}: {e}")
                raise
            groups[cat].append(f)
    return groups


def create_bad_file():
    bad = TEST_DIR / "bad.webm"
    with open(bad, "wb") as fh:
        fh.write(b"")
    return bad


def run_processing(groups):
    q = Queue()
    worker = EncodeWorker(q)
    worker.start()

    # enqueue tasks
    for cat in (Category.TRIM_ONLY, Category.COMPRESS_ONLY, Category.TRIM_AND_COMPRESS):
        for f in groups[cat]:
            out = OUT_DIR / f.name
            q.put((cat, f, out))

    # sentinel
    q.put(None)
    q.join()


def verify_outputs(groups):
    failures = []
    # only verify files that should be processed (not PASS)
    processed_cats = {Category.TRIM_ONLY, Category.COMPRESS_ONLY, Category.TRIM_AND_COMPRESS}
    for cat in processed_cats:
        for f in groups[cat]:
            out = OUT_DIR / f.name
            if not out.exists():
                failures.append(f"Missing output for {f} (expected {out})")
                continue
            # verify filename preserved
            if out.name != f.name:
                failures.append(f"Filename mismatch: {f} -> {out}")
                continue
            # probe
            try:
                info = probe(out)
            except Exception as e:
                failures.append(f"ffprobe failed for {out}: {e}")
                continue

            fmt = info.get("format", {})
            dur = float(fmt.get("duration", 0.0)) if fmt.get("duration") else 0.0
            size_mb = float(fmt.get("size", 0.0)) / (1024 * 1024) if fmt.get("size") else 0.0

            if cat in (Category.TRIM_ONLY, Category.TRIM_AND_COMPRESS):
                if dur > MAX_DURATION + 0.1:
                    failures.append(f"Duration too long for {out}: {dur}s (line should be <= {MAX_DURATION})")

            if cat in (Category.COMPRESS_ONLY, Category.TRIM_AND_COMPRESS):
                if size_mb > MAX_SIZE_MB + 0.1:
                    failures.append(f"Size too big for {out}: {size_mb:.2f} MB (limit {MAX_SIZE_MB})")

            # audio check: ensure an audio stream exists and sample rate reasonable
            streams = info.get("streams", [])
            audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
            if not audio_streams:
                failures.append(f"No audio stream in {out}")
            else:
                s = audio_streams[0]
                rate = int(s.get("sample_rate", 0)) if s.get("sample_rate") else 0
                ch = int(s.get("channels", 0)) if s.get("channels") else 0
                if rate < 22050 or ch < 1:
                    failures.append(f"Audio seems low quality in {out}: {rate}Hz {ch}ch")

    return failures


def main():
    if not TEST_DIR.exists():
        logger.error("test_videos folder missing; aborting smoke test")
        return

    ensure_out()

    # scan
    groups = scan_and_classify()
    logger.info("Groups summary:")
    for c in groups:
        logger.info("%s: %d", c.name, len(groups[c]))

    # create bad file and verify classifier tolerates it
    bad = create_bad_file()
    try:
        cat = classify(bad)
        logger.info("Bad file classified as: %s", cat)
    except Exception as e:
        logger.exception("Classifier crashed on bad file: %s", e)

    # run processing (headless simulation of GUI)
    run_processing(groups)

    failures = verify_outputs(groups)
    if failures:
        logger.error("SMOKE TEST FAILURES:")
        for f in failures:
            logger.error(" - %s", f)
    else:
        logger.info("SMOKE TEST PASSED")


if __name__ == '__main__':
    main()
