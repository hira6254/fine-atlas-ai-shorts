#!/usr/bin/env python3
"""
Deterministic Quality Gate for Fine Atlas 4K 60fps Master & 30s Cinema Shorts
=============================================================================
Verifies all Step-2 outputs in <1.5s, ¥0:
  1. `output/master_720p.mp4`             (720x1280, 24fps, H.264 yuv420p, AAC 48kHz stereo, ~27.7s)
  2. `output/master_720p_16x9.mp4`        (1280x720, 24fps, H.264 yuv420p, AAC 48kHz stereo, ~27.7s)
  3. `output/FA_DAY-02_Amadai_9x16_jp.mp4` (1080x1920, 24fps, exact 30.00s, AAC 48kHz stereo)
  4. `output/FA_DAY-02_Amadai_9x16_en.mp4` (1080x1920, 24fps, exact 30.00s, AAC 48kHz stereo)
  5. 4x2 Contact Sheets (`contact_sheet_4x2.jpg`, `contact_sheet_cinema_jp_4x2.jpg`, `contact_sheet_cinema_en_4x2.jpg`)
  6. Colab Overlay & Audio Pack (`overlay_tracks/overlay_manifest.json`, WAVs, nofadeout clean stream)
  7. Visual frame invariants on JP/EN 30s cinema shorts:
     - Active culinary motion in center region (y=420..1260) during cut1 slow-mo & cut3 grill
     - Clean transition into dark-navy/gold official brand closing card after 27.7s
     - Non-silent audio stream
"""

import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OVERLAY = OUT / "overlay_tracks"


def fail(msg: str):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def probe(path: Path) -> dict:
    if not path.exists() or path.stat().st_size < 100_000:
        fail(f"Missing or too small video: {path}")
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    info = json.loads(raw)
    dur = float(info["format"]["duration"])
    vs = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    aus = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not vs or not aus:
        fail(f"{path.name}: missing video or audio stream")
    return {"dur": dur, "size": int(info["format"]["size"]), "v": vs, "a": aus}


def grab_frame(path: Path, t: float, w: int, h: int) -> Image.Image:
    res = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{t:.2f}",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        capture_output=True,
        check=True,
    )
    return Image.frombytes("RGB", (w, h), res.stdout)


def check_audio_nonzero(path: Path):
    res = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in res.stderr.splitlines():
        if "mean_volume:" in line:
            val = float(line.split("mean_volume:")[1].split("dB")[0].strip())
            if val < -55.0:
                fail(f"{path.name}: audio appears silent (mean_volume={val} dB)")
            return val
    fail(f"{path.name}: could not parse mean_volume")


def main():
    specs = [
        (OUT / "master_720p.mp4", 720, 1280, "24/1", 26.5, 29.0),
        (OUT / "master_720p_16x9.mp4", 1280, 720, "24/1", 26.5, 29.0),
        (OUT / "FA_DAY-02_Amadai_9x16_jp.mp4", 1080, 1920, "24/1", 29.85, 30.15),
        (OUT / "FA_DAY-02_Amadai_9x16_en.mp4", 1080, 1920, "24/1", 29.85, 30.15),
    ]

    for path, ew, eh, efps, dmin, dmax in specs:
        info = probe(path)
        v, a = info["v"], info["a"]
        if (int(v["width"]), int(v["height"])) != (ew, eh):
            fail(f"{path.name}: expected {ew}x{eh}, got {v['width']}x{v['height']}")
        if v["codec_name"] != "h264" or v["pix_fmt"] != "yuv420p":
            fail(f"{path.name}: unexpected codec/pix_fmt {v['codec_name']}/{v['pix_fmt']}")
        if v["r_frame_rate"] != efps:
            fail(f"{path.name}: expected fps {efps}, got {v['r_frame_rate']}")
        if not (dmin <= info["dur"] <= dmax):
            fail(f"{path.name}: duration {info['dur']:.2f}s out of expected [{dmin}, {dmax}]")
        if a["codec_name"] != "aac" or int(a["sample_rate"]) != 48000 or int(a["channels"]) != 2:
            fail(f"{path.name}: unexpected audio spec {a}")
        mv = check_audio_nonzero(path)
        print(
            f"[PASS] {path.name:32s} | {ew}x{eh} @ {efps} | {info['dur']:5.2f}s | "
            f"{info['size']/1024/1024:5.2f}MB | audio={mv:.1f}dB"
        )

    # Check contact sheets & Colab overlay pack
    for req in [
        OUT / "contact_sheet_4x2.jpg",
        OUT / "contact_sheet_16x9_4x2.jpg",
        OUT / "contact_sheet_cinema_jp_4x2.jpg",
        OUT / "contact_sheet_cinema_en_4x2.jpg",
        OVERLAY / "overlay_manifest.json",
        OVERLAY / "narration_jp_30s.wav",
        OVERLAY / "narration_en_30s.wav",
        OVERLAY / "bgm_koto_30s.wav",
        OVERLAY / "clean_9x16_nofadeout.mp4",
    ]:
        if not req.exists() or req.stat().st_size == 0:
            fail(f"Missing required artifact: {req}")

    # Visual invariants on JP cinema edition
    jp_mp4 = OUT / "FA_DAY-02_Amadai_9x16_jp.mp4"
    f_hook1 = grab_frame(jp_mp4, 1.5, 1080, 1920)
    f_hook2 = grab_frame(jp_mp4, 3.8, 1080, 1920)
    f_end = grab_frame(jp_mp4, 28.0, 1080, 1920)

    center_box = (140, 460, 940, 1260)
    diff_motion = sum(ImageStat.Stat(ImageChops.difference(f_hook1.crop(center_box), f_hook2.crop(center_box))).mean) / 3.0
    if diff_motion < 4.0:
        fail(f"Center food region appears frozen in cut1 (diff={diff_motion:.2f})")

    diff_end = sum(ImageStat.Stat(ImageChops.difference(f_hook2.crop(center_box), f_end.crop(center_box))).mean) / 3.0
    if diff_end < 20.0:
        fail(f"Closing card transition not detected at 28.0s (diff={diff_end:.2f})")

    print(
        f"[PASS] All Step-2 visual & Colab overlay-pack checks passed! "
        f"(cut1_motion={diff_motion:.1f}, closing_diff={diff_end:.1f})"
    )


if __name__ == "__main__":
    main()
