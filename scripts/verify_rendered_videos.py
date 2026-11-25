#!/usr/bin/env python3
"""
Deterministic Video Quality & Motion Gate (`scripts/verify_rendered_videos.py`)
===============================================================================
Verifies rendered Fine Atlas short videos (`videos/FA_DAY-*.mp4`) in <1.5s, ¥0:
  1. Exact 1080x1920 (9:16), H.264 yuv420p, 30fps, 30.0s duration, stereo 44.1kHz AAC audio
  2. Two-layer stability invariant: top header bar stays rock-steady inside a section,
     while the central culinary gallery window (24..1056, 372..1292) has continuous camera motion
  3. Wide -> Close-up sub-cut progression & delayed verified data plaque appearance
"""

import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT_DIR = Path(__file__).resolve().parent.parent
VIDEOS_DIR = ROOT_DIR / "videos"

EXPECTED_FILES = [
    "FA_DAY-01_jp.mp4",
    "FA_DAY-01_jp_nobgm.mp4",
    "FA_DAY-01_en.mp4",
    "FA_DAY-01_en_nobgm.mp4",
    "FA_DAY-06_jp.mp4",
    "FA_DAY-06_jp_nobgm.mp4",
    "FA_DAY-06_en.mp4",
    "FA_DAY-06_en_nobgm.mp4",
]


def fail(msg: str):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def extract_frame_rgb(mp4_path: Path, t_sec: float) -> Image.Image:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{t_sec:.3f}",
        "-i",
        str(mp4_path),
        "-frames:v",
        "1",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    return Image.frombytes("RGB", (1080, 1920), res.stdout)


def mean_abs_diff(img_a: Image.Image, img_b: Image.Image, box: tuple) -> float:
    diff = ImageChops.difference(img_a.crop(box), img_b.crop(box))
    stat = ImageStat.Stat(diff)
    return sum(stat.mean) / len(stat.mean)


def check_stream_specs(mp4_path: Path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,sample_rate,channels:format=duration",
        "-of",
        "json",
        str(mp4_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    dur = float(info["format"]["duration"])
    if not (29.85 <= dur <= 30.15):
        fail(f"{mp4_path.name}: expected 30.0s duration, got {dur:.3f}s")

    streams = {s["codec_type"]: s for s in info["streams"]}
    if "video" not in streams or "audio" not in streams:
        fail(f"{mp4_path.name}: missing video or audio stream")

    vs = streams["video"]
    if vs["codec_name"] != "h264" or vs["width"] != 1080 or vs["height"] != 1920 or vs["pix_fmt"] != "yuv420p":
        fail(f"{mp4_path.name}: unexpected video stream spec {vs}")
    if vs["r_frame_rate"] != "30/1":
        fail(f"{mp4_path.name}: expected 30/1 fps, got {vs['r_frame_rate']}")

    aus = streams["audio"]
    if aus["codec_name"] != "aac" or int(aus["sample_rate"]) != 44100 or int(aus["channels"]) != 2:
        fail(f"{mp4_path.name}: unexpected audio stream spec {aus}")


def main():
    for fname in EXPECTED_FILES:
        fpath = VIDEOS_DIR / fname
        if not fpath.exists() or fpath.stat().st_size < 100_000:
            fail(f"Missing or empty rendered video: {fpath}")
        check_stream_specs(fpath)

    # Pixel-level motion & stability check on 100% still-photo episode (FA_DAY-01_jp.mp4)
    day1 = VIDEOS_DIR / "FA_DAY-01_jp.mp4"
    f_3_6 = extract_frame_rgb(day1, 3.60)   # Before delayed plaque (3.0 + 0.6s), Shot 2A (Wide)
    f_5_5 = extract_frame_rgb(day1, 5.50)   # After delayed plaque (3.0 + 2.5s), Shot 2A (Wide)
    f_9_2 = extract_frame_rgb(day1, 9.20)   # Shot 2B (Close-up Toumin rapid freezer)
    f_21_0 = extract_frame_rgb(day1, 21.00) # Shot 4A (Climax Wide)
    f_25_2 = extract_frame_rgb(day1, 25.20) # Shot 4B (Climax Close-up glistening sashimi)

    header_box = (40, 40, 1040, 340)
    window_upper_box = (60, 400, 1020, 1120)
    plaque_region_box = (388, 1168, 1038, 1276)

    # 1. Stationary header invariant within Section 2
    hdr_diff = mean_abs_diff(f_3_6, f_5_5, header_box)
    if hdr_diff > 1.2:
        fail(f"Header wobbled unexpectedly inside section (mean diff={hdr_diff:.2f})")

    # 2. Continuous smooth photo motion inside gallery window (3.6s -> 5.5s)
    win_motion = mean_abs_diff(f_3_6, f_5_5, window_upper_box)
    if win_motion < 2.0:
        fail(f"Photo inside gallery window appears frozen between 3.6s and 5.5s (diff={win_motion:.2f})")

    # 3. Wide -> Close-up sub-cut progression inside 8.5s explanation & 7.0s climax slots
    subcut_body_diff = mean_abs_diff(f_5_5, f_9_2, window_upper_box)
    subcut_climax_diff = mean_abs_diff(f_21_0, f_25_2, window_upper_box)
    if subcut_body_diff < 12.0 or subcut_climax_diff < 10.0:
        fail(
            f"Wide -> Close-up sub-cut did not trigger cleanly (body={subcut_body_diff:.2f}, climax={subcut_climax_diff:.2f})"
        )

    # 4. Delayed verified data plaque appearance (absent at 3.6s, present at 5.5s)
    plaque_diff = mean_abs_diff(f_3_6, f_5_5, plaque_region_box)
    if plaque_diff < 8.0:
        fail(f"Delayed data plaque fade-in not detected between 3.6s and 5.5s (diff={plaque_diff:.2f})")

    print("[PASS] All 8 MP4 videos passed deterministic stream & documentary-motion checks!")
    print(f"  - Header stability diff (3.6s vs 5.5s): {hdr_diff:.2f} (stationary)")
    print(f"  - Gallery window camera motion diff (3.6s vs 5.5s): {win_motion:.2f} (smooth motion)")
    print(f"  - Wide -> Close-up sub-cut diff: body={subcut_body_diff:.2f}, climax={subcut_climax_diff:.2f}")
    print(f"  - Delayed verified plaque fade-in diff: {plaque_diff:.2f}")


if __name__ == "__main__":
    main()
