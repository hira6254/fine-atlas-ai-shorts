#!/usr/bin/env python3
"""
FINE ATLAS — Cinema-Grade 4K 60fps Master Preparation & Bilingual 30s Short Studio
==================================================================================
Built for President Imada's 13-Chapter AI Short Video Plan & Fine Atlas Quality Standards.

What this pipeline produces in a single deterministic run:
  1. Clean Master Video for Google Colab 4K/60fps Upscaling (Real-ESRGAN + Practical-RIFE):
     - `output/master_720p.mp4`      (Default 9:16 vertical 720x1280 @ 24fps, ambient audio)
     - `output/master_720p_16x9.mp4` (Optional 16:9 horizontal 1280x720 @ 24fps)
     Specs:
       * Slow-motion selected cuts at 0.75x with FFmpeg optical flow (`minterpolate` MCI/AOBMC)
         and pitch-preserved audio tempo matching (`atempo=0.75`)
       * 0.70s crossfades at every cut boundary (`xfade` video + `acrossfade` audio)
       * 0.60s fade-in at head, 1.50s fade-out at tail
       * Subtle culinary cinema color grading & natural sharpening
  2. Contact Sheets (4x2 thumbnails) for instant visual inspection:
     - `output/contact_sheet_4x2.jpg`          (Clean master 4x2)
     - `output/contact_sheet_cinema_jp_4x2.jpg` (Finished 30s JP cinema edition 4x2)
  3. Ready-to-Share 30.00s Bilingual Full-Bleed Cinema Editions (1080x1920 @ 24fps):
     - `output/FA_DAY-02_Amadai_9x16_jp.mp4`
     - `output/FA_DAY-02_Amadai_9x16_en.mp4`
     Features:
       * Full-bleed 9:16 culinary framing (zero bulky black letterbox bars)
       * Translucent cinema gradient vignettes + Serif/Sans broadcast typography
       * Narration-synced subtitles (phrase-by-phrase fade transitions in SNS safe zone)
       * Verified Fine Atlas culinary data plaques (95% yield, ¥501 dish cost, 27.1% FL)
       * 3-layer mastered audio: authentic sizzle ambient sound + JP/EN neural narration + soft koto ambient BGM
       * Mandatory 27.0-30.0s Fine Atlas brand closing card:
           JP: 「日本の旬と品質を、一箱に。世界の厨房へ。」
           EN: "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."
  4. Colab Overlay & Audio Pack (`output/overlay_tracks/`):
     - Synced JP/EN narration tracks, BGM track, and `overlay_manifest.json` so the Google Colab
       4K 60fps notebook can composite razor-sharp native 4K (2160x3840) subtitles & closing card
       *after* Real-ESRGAN + Practical-RIFE without any AI text distortion.
"""

import argparse
import asyncio
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import textwrap
import wave
from pathlib import Path
import numpy as np
import edge_tts
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
CLIPS_DIR = ROOT_DIR / "clips"
OUTPUT_DIR = ROOT_DIR / "output"
OVERLAY_DIR = OUTPUT_DIR / "overlay_tracks"

FONT_SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

CATCHPHRASE_JP = "日本の旬と品質を、一箱に。世界の厨房へ。"
CATCHPHRASE_EN = "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."

FPS = 24
XFADE_DUR = 0.70
FADE_IN_DUR = 0.60
FADE_OUT_DUR = 1.50
SLOW_FACTOR = 0.75
TOTAL_FINAL_SEC = 30.00
ENDCARD_START_SEC = 27.00  # 27.00s - 30.00s official brand closing card (3.00s)

# Episode DAY-02 (Red Amadai / Guji) script broken into crisp cinema subtitle beats
EPISODE_PRESETS = {
    "DAY-02": {
        "code": "FA_DAY-02_Amadai",
        "fish_jp": "赤甘鯛（ぐじ）",
        "fish_en": "Red Tilefish (Amadai)",
        "category_jp": "FINE ATLAS ｜ 高級魚の極意",
        "category_en": "FINE ATLAS | LUXURY FISH CRAFT",
        "headline_jp": "高級魚「赤甘鯛」",
        "subhead_jp": "なぜウロコを残して焼くのか？",
        "headline_en": "Red Tilefish \"Amadai\"",
        "subhead_en": "Why Chefs Keep the Scales On",
        "plaques_jp": [
            (3.2, 13.0, "検証済み規格｜鱗付三枚おろしフィレ", "可食歩留まり 95%・下処理ロスゼロ"),
            (13.3, 26.4, "飲食店 1皿シミュレーション", "1皿原価 ¥501（原価率 27.1%）"),
        ],
        "plaques_en": [
            (3.2, 13.0, "VERIFIED SPEC | SCALE-ON FILLET", "95% Usable Yield • Zero Prep Damage"),
            (13.3, 26.4, "KITCHEN COST SIMULATION", "Dish Cost ¥501 • 27.1% Food Cost"),
        ],
        "beats_jp": [
            (
                "hook",
                0.20,
                5.45,
                "京都で「ぐじ」と呼ばれる高級魚、赤甘鯛。なぜプロは、ウロコを残して焼くのでしょうか？",
                ["京都で「ぐじ」と呼ばれる高級魚、赤甘鯛。", "なぜプロはウロコを残して焼くのか？"],
            ),
            (
                "body1",
                5.70,
                13.15,
                "薄いウロコに高温の油をかけると、花のように逆立ちサクサクに。繊細な白身を蒸気でふっくら閉じ込めます。",
                ["高温の油でウロコが花のように逆立ち", "サクサク食感＆白身をふっくら閉じ込める"],
            ),
            (
                "body2",
                13.40,
                20.10,
                "身が柔らかいため、産地で鱗付きフィレに急速冷凍。歩留まり95パーセントで下処理ロスはゼロ。",
                ["産地で鱗付きフィレに加工・急速冷凍", "可食歩留まり95%で仕込みの手間ゼロ"],
            ),
            (
                "climax",
                20.30,
                26.45,
                "和食の松笠焼きにも、フレンチのポワレにも。1皿原価率27パーセントで、主役の一皿に仕上がります。",
                ["和食の松笠焼き・フレンチのポワレに", "下処理ゼロ・原価率27.1%で主役の一皿へ"],
            ),
            (
                "closing",
                26.65,
                29.70,
                "日本の旬と品質を、一箱に。世界の厨房へ。",
                ["日本の旬と品質を、一箱に。", "世界の厨房へ。"],
            ),
        ],
        "beats_en": [
            (
                "hook",
                0.20,
                5.45,
                "Prized as Guji in Kyoto. Why do master chefs keep the scales on Red Tilefish?",
                ["Prized as \"Guji\" in Kyoto:", "Why do chefs leave the scales on?"],
            ),
            (
                "body1",
                5.70,
                13.15,
                "Paper-thin scales bloom crisp in hot oil, sealing the delicate white flesh in natural steam.",
                ["Hot oil blooms paper-thin scales crisp,", "sealing delicate white flesh in steam."],
            ),
            (
                "body2",
                13.40,
                20.10,
                "Rapid-frozen at the port as scale-on fillets, delivering a ninety-five percent yield with zero prep loss.",
                ["Rapid-frozen scale-on fillets deliver", "95% usable yield with zero prep loss."],
            ),
            (
                "climax",
                20.30,
                25.85,
                "Ready for Matsukasa-yaki or French poele, at an ideal twenty-seven percent food cost.",
                ["Ready for Matsukasa-yaki or French poele", "with zero scaling and 27.1% dish cost."],
            ),
            (
                "closing",
                26.05,
                29.75,
                "Japan's seasonal catch and peak quality, in one box. To kitchens worldwide.",
                ["Japan's seasonal catch & peak quality,", "in one box. To kitchens worldwide."],
            ),
        ],
    }
}

_FONT_CACHE = {}


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, int(size))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, int(size))
    return _FONT_CACHE[key]


def fit_font(draw: ImageDraw.ImageDraw, text: str, path: str, max_sz: int, min_sz: int, max_w: int):
    for sz in range(max_sz, min_sz - 1, -1):
        f = get_font(path, sz)
        if draw.textlength(text, font=f) <= max_w:
            return f
    return get_font(path, min_sz)


def probe_media(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels",
        "-of",
        "json",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    dur = float(info["format"]["duration"])
    size_bytes = int(info["format"]["size"])
    vs = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    aus = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    return {
        "path": str(path),
        "duration": dur,
        "size_bytes": size_bytes,
        "size_mb": round(size_bytes / (1024 * 1024), 2),
        "video": vs,
        "audio": aus,
        "has_audio": aus is not None,
    }


def preprocess_clip(
    src: Path,
    dst: Path,
    target_w: int,
    target_h: int,
    is_slow: bool,
    crop_x_ratio: float,
    grade: bool = True,
):
    """
    Normalizes a clip to exact target dimensions, 24fps, 48kHz stereo AAC,
    applying optical-flow slow motion (`minterpolate` + `atempo`) if selected.
    """
    info = probe_media(src)
    vs = info["video"]
    sw, sh = int(vs["width"]), int(vs["height"])
    target_ar = target_w / target_h
    src_ar = sw / sh

    vf_parts = []
    # Smart framing crop before optical-flow & scaling so subject stays dead-center
    if src_ar > target_ar + 0.01:
        # Source is wider than target (e.g., 16:9 -> 9:16: 608x1080 native pixels)
        crop_h = sh
        crop_w = int(round(sh * target_ar))
        crop_w -= crop_w % 2
        cx = int(max(0, min(sw - crop_w, round(sw * crop_x_ratio - crop_w / 2.0))))
        cx -= cx % 2
        vf_parts.append(f"crop={crop_w}:{crop_h}:{cx}:0")
    elif src_ar < target_ar - 0.01:
        crop_w = sw
        crop_h = int(round(sw / target_ar))
        crop_h -= crop_h % 2
        cy = (sh - crop_h) // 2
        cy -= cy % 2
        vf_parts.append(f"crop={crop_w}:{crop_h}:0:{cy}")

    if is_slow:
        # Downscale first ONLY if native crop exceeds target (e.g., 1920x1080 -> 1280x720)
        # Keep native 608x1080 for 9:16 so optical flow runs on true source pixels (~3.5x faster & sharper!)
        if src_ar <= target_ar + 0.01 and sw > target_w:
            vf_parts.append(f"scale={target_w}:{target_h}:flags=lanczos")
        vf_parts.append(f"setpts=PTS/{SLOW_FACTOR:.4f}")
        vf_parts.append(
            f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:search_param=16"
        )
        vf_parts.append(f"scale={target_w}:{target_h}:flags=lanczos")
    else:
        vf_parts.append(f"scale={target_w}:{target_h}:flags=lanczos")
        vf_parts.append(f"fps={FPS}")

    if grade:
        # Culinary cinema color grading: warm rich contrast + crisp texture detail
        vf_parts.append("eq=contrast=1.06:saturation=1.10:brightness=0.01:gamma=0.98")
        vf_parts.append("unsharp=5:5:0.42:5:5:0.0")

    vf_parts.append("format=yuv420p")
    vf_parts.append("setsar=1")
    vf_str = ",".join(vf_parts)

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    if info["has_audio"]:
        af_parts = []
        if is_slow:
            af_parts.append(f"atempo={SLOW_FACTOR:.4f}")
        af_parts.append("aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo")
        af_str = ",".join(af_parts)
        cmd += ["-vf", vf_str, "-af", af_str]
    else:
        dur_out = info["duration"] / (SLOW_FACTOR if is_slow else 1.0)
        cmd += [
            "-f",
            "lavfi",
            "-t",
            f"{dur_out:.3f}",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            vf_str,
        ]

    cmd += [
        "-c:v",
        "libx264",
        "-crf",
        "16",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(dst),
    ]
    subprocess.run(cmd, check=True)
    return probe_media(dst)


def concat_with_crossfades(
    norm_clips: list,
    out_mp4: Path,
    xfade_sec: float = XFADE_DUR,
    fade_in_sec: float = FADE_IN_DUR,
    fade_out_sec: float = FADE_OUT_DUR,
    apply_end_fade: bool = True,
):
    """
    Chains N normalized clips with exact `xfade` (video) and `acrossfade` (audio),
    plus head fade-in and optional tail fade-out.
    """
    n = len(norm_clips)
    assert n >= 2, "Need at least 2 clips to crossfade"

    durations = [probe_media(c)["duration"] for c in norm_clips]
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for c in norm_clips:
        cmd += ["-i", str(c)]

    filter_parts = []
    # Reset timestamps per stream to guarantee zero drift
    for i in range(n):
        filter_parts.append(f"[{i}:v]setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[v{i}]")
        filter_parts.append(f"[{i}:a]asetpts=PTS-STARTPTS,aresample=48000[a{i}]")

    cur_v = "v0"
    cur_a = "a0"
    cur_dur = durations[0]

    for i in range(1, n):
        offset = max(0.05, cur_dur - xfade_sec)
        nxt_v = f"xv{i}"
        nxt_a = f"xa{i}"
        filter_parts.append(
            f"[{cur_v}][v{i}]xfade=transition=fade:duration={xfade_sec:.3f}:offset={offset:.3f}[{nxt_v}]"
        )
        filter_parts.append(
            f"[{cur_a}][a{i}]acrossfade=d={xfade_sec:.3f}:c1=tri:c2=tri[{nxt_a}]"
        )
        cur_v = nxt_v
        cur_a = nxt_a
        cur_dur = offset + durations[i]

    # Head fade-in & tail fade-out
    v_fades = [f"fade=t=in:st=0:d={fade_in_sec:.3f}"]
    a_fades = [f"afade=t=in:st=0:d={fade_in_sec:.3f}"]
    if apply_end_fade and fade_out_sec > 0:
        fo_st = max(0.0, cur_dur - fade_out_sec)
        v_fades.append(f"fade=t=out:st={fo_st:.3f}:d={fade_out_sec:.3f}")
        a_fades.append(f"afade=t=out:st={fo_st:.3f}:d={fade_out_sec:.3f}")

    filter_parts.append(f"[{cur_v}]{','.join(v_fades)},format=yuv420p[vout]")
    filter_parts.append(f"[{cur_a}]{','.join(a_fades)}[aout]")

    cmd += [
        "-filter_complex",
        ";".join(filter_parts),
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-c:v",
        "libx264",
        "-crf",
        "16",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True)
    return probe_media(out_mp4)


def make_contact_sheet_4x2(video_path: Path, out_jpg: Path, title_text: str):
    """Creates a clean 4x2 contact sheet with timestamps & technical summary header."""
    info = probe_media(video_path)
    dur = info["duration"]
    vs = info["video"]
    w, h = int(vs["width"]), int(vs["height"])
    is_portrait = h > w
    tw, th = (320, 568) if is_portrait else (440, 248)
    gap = 14
    margin = 24
    hdr_h = 68

    canvas_w = margin * 2 + tw * 4 + gap * 3
    canvas_h = hdr_h + margin + th * 2 + gap
    canvas = Image.new("RGB", (canvas_w, canvas_h), (10, 22, 36))
    draw = ImageDraw.Draw(canvas)

    f_hdr = get_font(FONT_SANS, 22)
    f_sub = get_font(FONT_SANS, 16)
    f_ts = get_font(FONT_SANS, 16)

    draw.text((margin, 14), title_text, font=f_hdr, fill=(253, 224, 71))
    spec_line = (
        f"{video_path.name}  |  {w}x{h}  |  fps={vs['r_frame_rate']}  |  "
        f"{dur:.2f}s  |  {info['size_mb']:.2f} MB  |  Audio={'YES' if info['has_audio'] else 'NO'}"
    )
    draw.text((margin, 44), spec_line, font=f_sub, fill=(203, 213, 225))

    # Sample 8 visually informative moments across the video
    fracs = [0.04, 0.14, 0.28, 0.42, 0.56, 0.70, 0.84, 0.94]
    for idx, fr in enumerate(fracs):
        t = min(max(0.2, dur * fr), max(0.2, dur - 0.35))
        r, c = divmod(idx, 4)
        x0 = margin + c * (tw + gap)
        y0 = hdr_h + r * (th + gap)
        p = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                f"{t:.2f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-vf",
                f"scale={tw}:{th}:flags=lanczos",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ],
            capture_output=True,
            check=True,
        )
        im = Image.frombytes("RGB", (tw, th), p.stdout)
        canvas.paste(im, (x0, y0))
        draw.rectangle([x0, y0, x0 + tw - 1, y0 + th - 1], outline=(217, 119, 6), width=2)
        draw.rounded_rectangle([x0 + 8, y0 + 8, x0 + 92, y0 + 34], radius=6, fill=(10, 22, 36))
        draw.text((x0 + 50, y0 + 21), f"{t:05.2f}s", font=f_ts, fill=(253, 224, 71), anchor="mm")

    canvas.save(out_jpg, quality=92)


async def synth_tts_segment(text: str, voice: str, rate: str, pitch: str, out_mp3: Path, fallback_voice: str):
    last_err = None
    candidates = [voice, voice, fallback_voice, fallback_voice]
    for attempt, v in enumerate(candidates, start=1):
        try:
            comm = edge_tts.Communicate(text=text, voice=v, rate=rate, pitch=pitch)
            await comm.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 1000:
                return v
        except Exception as e:
            last_err = e
            await asyncio.sleep(0.8 * attempt)
    raise RuntimeError(f"TTS failed after retries for voice={voice}: {last_err}")


def build_synced_narration(beats: list, is_en: bool, out_wav: Path, tmp_dir: Path) -> list:
    """
    Synthesizes each beat in a single neural TTS call (with resilient retry),
    trims dead silence, aligns seamlessly to its timecode window with gentle FFmpeg atempo if needed,
    and mixes all beats onto a 30.00s 48kHz stereo WAV track.
    """
    voice = "en-US-AndrewMultilingualNeural" if is_en else "ja-JP-KeitaNeural"
    fallback_voice = "en-US-GuyNeural" if is_en else "ja-JP-NanamiNeural"
    pitch = "+0Hz" if is_en else "-2Hz"
    base_rate = "+5%" if is_en else "+10%"

    seg_records = []
    for bid, t_start, t_end, text, sub_lines in beats:
        window = t_end - t_start
        mp3_path = tmp_dir / f"tts_{'en' if is_en else 'jp'}_{bid}.mp3"
        wav_path = tmp_dir / f"tts_{'en' if is_en else 'jp'}_{bid}.wav"

        used_voice = asyncio.run(synth_tts_segment(text, voice, base_rate, pitch, mp3_path, fallback_voice))
        # Trim leading/trailing silence so timing is super crisp
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(mp3_path),
                "-af", "silenceremove=start_periods=1:start_threshold=-45dB:detection=peak,areverse,silenceremove=start_periods=1:start_threshold=-45dB:detection=peak,areverse,aresample=48000",
                "-ac", "2", "-ar", "48000",
                str(wav_path),
            ],
            check=True,
        )
        dur = probe_media(wav_path)["duration"]

        # Gently fit inside the timecode window with pitch-preserving atempo if slightly over
        tempo_used = 1.0
        if dur > window:
            tempo_used = min(1.40, dur / (window - 0.05))
            wav_fixed = tmp_dir / f"tts_{'en' if is_en else 'jp'}_{bid}_fit.wav"
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(wav_path),
                    "-af", f"atempo={tempo_used:.4f},aresample=48000",
                    "-ac", "2", "-ar", "48000",
                    str(wav_fixed),
                ],
                check=True,
            )
            wav_path = wav_fixed
            dur = probe_media(wav_path)["duration"]

        actual_start = t_start
        if bid == "closing" and dur < window:
            actual_start = t_start + (window - dur) * 0.35
        actual_end = actual_start + dur
        assert actual_end <= TOTAL_FINAL_SEC - 0.05, f"Beat {bid} overflows 30.00s ({actual_end:.2f}s)"
        print(
            f"  [TTS {'EN' if is_en else 'JP'}] {bid:7s}: voice={used_voice.split('-')[-1]} "
            f"rate={base_rate} atempo={tempo_used:.2f}x dur={dur:.2f}s ({actual_start:.2f}..{actual_end:.2f}s)"
        )
        seg_records.append((bid, actual_start, actual_end, wav_path, sub_lines))

    # Mix all speech segments onto a clean 30.00s stereo WAV
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-t", f"{TOTAL_FINAL_SEC:.2f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
    f_parts = []
    mix_inputs = ["[0:a]"]
    for idx, (bid, st, en, wp, _) in enumerate(seg_records, start=1):
        cmd += ["-i", str(wp)]
        delay_ms = int(round(st * 1000))
        f_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume=1.0[s{idx}]")
        mix_inputs.append(f"[s{idx}]")

    f_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:normalize=0:duration=first,highpass=f=85,compand=attacks=0.02:decays=0.15:points=-80/-80|-24/-24|-12/-10|0/-2[out]")
    cmd += ["-filter_complex", ";".join(f_parts), "-map", "[out]", "-ar", "48000", "-ac", "2", str(out_wav)]
    subprocess.run(cmd, check=True)

    # Return subtitle display intervals (slightly padded for graceful reading)
    sub_schedule = []
    for i, (bid, st, en, _, sub_lines) in enumerate(seg_records):
        if bid == "closing":
            continue  # Closing card displays its own dedicated full-screen brand typography
        nxt_st = seg_records[i + 1][1] if i + 1 < len(seg_records) else ENDCARD_START_SEC
        disp_end = min(ENDCARD_START_SEC - 0.25, max(en + 0.30, min(en + 0.65, nxt_st - 0.15)))
        sub_schedule.append({"id": bid, "start": round(st, 3), "end": round(disp_end, 3), "lines": sub_lines})
    return sub_schedule


def generate_koto_cinema_bgm(wav_path: Path, duration: float = TOTAL_FINAL_SEC, sr: int = 48000):
    """
    Synthesizes a warm, stately Japanese culinary documentary ambient BGM (D-minor pentatonic koto + subtle low pad)
    in 48kHz stereo using fast vectorized numpy math.
    """
    n = int(round(duration * sr))
    t = np.arange(n, dtype=np.float64) / sr

    # Subtle breathing stereo pad (D3 146.83Hz + A3 220Hz + D4 293.66Hz)
    env = np.minimum(1.0, t / 1.5) * np.minimum(1.0, np.maximum(0.0, (duration - t) / 2.0))
    pad_l = (0.095 * np.sin(2 * math.pi * 146.83 * t) + 0.060 * np.sin(2 * math.pi * 220.0 * t + 0.3)) * env
    pad_r = (0.095 * np.sin(2 * math.pi * 146.83 * t + 0.12) + 0.060 * np.sin(2 * math.pi * 220.0 * t)) * env

    left = pad_l.copy()
    right = pad_r.copy()

    # Elegant Miyako/Yo Japanese koto plucks
    notes = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46, 880.00]
    pattern = [0, 3, 2, 4, 3, 1, 0, 2, 5, 4, 3, 2, 0, 3, 4, 5]
    interval = 0.85
    k = 0
    while k * interval < duration - 1.5:
        st = k * interval
        freq = notes[pattern[k % len(pattern)]]
        idx0 = int(st * sr)
        length = min(int(2.4 * sr), n - idx0)
        if length <= 0:
            break
        dt = np.arange(length, dtype=np.float64) / sr
        p_env = np.minimum(1.0, dt / 0.015) * np.exp(-2.4 * dt)
        sig = (
            0.16 * np.sin(2 * math.pi * freq * dt)
            + 0.065 * np.sin(2 * math.pi * freq * 2.0 * dt) * np.exp(-4.2 * dt)
            + 0.025 * np.sin(2 * math.pi * freq * 3.0 * dt) * np.exp(-6.5 * dt)
        ) * p_env
        pan = 0.5 + 0.18 * math.sin(k * 1.1)
        left[idx0 : idx0 + length] += sig * (1.0 - pan * 0.4)
        right[idx0 : idx0 + length] += sig * (0.6 + pan * 0.4)
        k += 1

    # Soft harmonic fifth swell at narrative landmarks (0.05s, 6.0s, 13.0s, 20.3s, 27.0s)
    for ct in (0.05, 6.00, 13.00, 20.30, 27.00):
        idx0 = int(ct * sr)
        length = min(int(2.8 * sr), n - idx0)
        if length <= 0:
            continue
        dt = np.arange(length, dtype=np.float64) / sr
        c_env = np.minimum(1.0, dt / 0.05) * np.exp(-1.55 * dt)
        chord = (
            0.08 * np.sin(2 * math.pi * 293.66 * dt)
            + 0.065 * np.sin(2 * math.pi * 440.00 * dt)
            + 0.045 * np.sin(2 * math.pi * 587.33 * dt)
        ) * c_env
        left[idx0 : idx0 + length] += chord
        right[idx0 : idx0 + length] += chord

    # Normalize & export 16-bit stereo WAV
    peak = max(float(np.max(np.abs(left))), float(np.max(np.abs(right))), 1e-6)
    scale = 0.72 / peak
    interleaved = np.empty(n * 2, dtype=np.int16)
    interleaved[0::2] = np.clip(left * scale * 32767.0, -32767, 32767).astype(np.int16)
    interleaved[1::2] = np.clip(right * scale * 32767.0, -32767, 32767).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(interleaved.tobytes())


def build_cinema_vignette(w: int, h: int) -> Image.Image:
    """Builds a sleek top + bottom translucent navy-black vignette that leaves the middle 62% crystal clear."""
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    # Top gradient: y = 0 .. 0.24*h (alpha 195 -> 0)
    top_h = int(h * 0.24)
    y_top = np.linspace(1.0, 0.0, top_h) ** 1.55
    arr[:top_h, :, 0] = 8
    arr[:top_h, :, 1] = 18
    arr[:top_h, :, 2] = 32
    arr[:top_h, :, 3] = (y_top[:, None] * 198).astype(np.uint8)

    # Bottom gradient: y = 0.66*h .. h (alpha 0 -> 224)
    bot_y0 = int(h * 0.66)
    bot_h = h - bot_y0
    y_bot = np.linspace(0.0, 1.0, bot_h) ** 1.45
    arr[bot_y0:, :, 0] = 7
    arr[bot_y0:, :, 1] = 16
    arr[bot_y0:, :, 2] = 28
    arr[bot_y0:, :, 3] = (y_bot[:, None] * 224).astype(np.uint8)

    return Image.fromarray(arr, mode="RGBA")


def draw_text_with_shadow(draw: ImageDraw.ImageDraw, pos, text: str, font, fill, anchor="mm", shadow_offset=3):
    x, y = pos
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 185), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def build_top_header_layer(w: int, h: int, ep: dict, is_en: bool) -> Image.Image:
    """Renders refined Netflix/TV-CM style top badge & Serif headline strictly inside SNS top safe zone."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = w / 1080.0

    cat = ep["category_en"] if is_en else ep["category_jp"]
    head = ep["headline_en"] if is_en else ep["headline_jp"]
    sub = ep["subhead_en"] if is_en else ep["subhead_jp"]

    # Subtle gold pill badge (y = 104..152)
    f_cat = get_font(FONT_SANS, int(24 * s))
    cat_w = draw.textlength(cat, font=f_cat) + int(48 * s)
    x0 = (w - cat_w) / 2
    draw.rounded_rectangle(
        [x0, int(102 * s), x0 + cat_w, int(148 * s)],
        radius=int(23 * s),
        fill=(11, 28, 48, 205),
        outline=(217, 155, 58, 240),
        width=max(2, int(2 * s)),
    )
    draw.text((w / 2, int(125 * s)), cat, font=f_cat, fill=(253, 224, 128, 255), anchor="mm")

    # Main Serif headline (y = 198)
    f_head = fit_font(draw, head, FONT_SERIF, int(56 * s), int(38 * s), int(w * 0.88))
    draw_text_with_shadow(draw, (w / 2, int(198 * s)), head, f_head, (255, 255, 255, 255), shadow_offset=int(3 * s))

    # Accent gold subhead (y = 258)
    f_sub = fit_font(draw, sub, FONT_SANS, int(34 * s), int(24 * s), int(w * 0.88))
    draw_text_with_shadow(draw, (w / 2, int(258 * s)), sub, f_sub, (253, 224, 102, 255), shadow_offset=int(2 * s))

    # Ultra-thin gold hairline divider
    draw.line([int(w * 0.30), int(292 * s), int(w * 0.70), int(292 * s)], fill=(217, 155, 58, 175), width=max(1, int(2 * s)))
    return img


def build_plaque_layer(w: int, h: int, label: str, value: str, is_en: bool) -> Image.Image:
    """Compact luxury lacquer data plaque placed cleanly at y=312..392 (zero overlap with center food)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = w / 1080.0

    pw = int(760 * s)
    ph = int(84 * s)
    x0 = (w - pw) // 2
    y0 = int(314 * s)

    draw.rounded_rectangle(
        [x0, y0, x0 + pw, y0 + ph],
        radius=int(14 * s),
        fill=(10, 25, 42, 210),
        outline=(217, 155, 58, 235),
        width=max(2, int(2 * s)),
    )
    # Left gold accent bar
    draw.rounded_rectangle([x0, y0, x0 + int(10 * s), y0 + ph], radius=int(6 * s), fill=(217, 155, 58, 255))

    f_lbl = fit_font(draw, label, FONT_SANS, int(21 * s), int(16 * s), pw - int(56 * s))
    f_val = fit_font(draw, value, FONT_SERIF if not is_en else FONT_SANS, int(30 * s), int(20 * s), pw - int(56 * s))

    draw.text((w / 2 + int(4 * s), y0 + int(24 * s)), label, font=f_lbl, fill=(216, 226, 238, 255), anchor="mm")
    draw.text((w / 2 + int(4 * s), y0 + int(58 * s)), value, font=f_val, fill=(253, 224, 102, 255), anchor="mm")
    return img


def build_subtitle_layer(w: int, h: int, lines: list, is_en: bool) -> Image.Image:
    """Renders crisp cinema subtitles in the lower SNS safe zone (y = 1360..1580 for 1080x1920)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = w / 1080.0

    # Measure text to size the sleek translucent backdrop pill
    max_sz = int(42 * s) if not is_en else int(38 * s)
    min_sz = int(26 * s)
    fonts = [fit_font(draw, ln, FONT_SANS, max_sz, min_sz, int(w * 0.84)) for ln in lines]
    max_tw = max(draw.textlength(ln, font=f) for ln, f in zip(lines, fonts))
    line_h = int(60 * s)
    pad_x = int(42 * s)
    pad_y = int(26 * s)

    box_w = min(int(w * 0.92), int(max_tw + pad_x * 2))
    box_h = line_h * len(lines) + pad_y * 2
    x0 = (w - box_w) // 2
    cy_center = int(1465 * s)
    y0 = cy_center - box_h // 2

    draw.rounded_rectangle(
        [x0, y0, x0 + box_w, y0 + box_h],
        radius=int(18 * s),
        fill=(8, 19, 34, 212),
        outline=(217, 155, 58, 160),
        width=max(1, int(2 * s)),
    )
    # Subtle gold accent underline inside subtitle box
    draw.line(
        [x0 + int(36 * s), y0 + box_h - int(6 * s), x0 + box_w - int(36 * s), y0 + box_h - int(6 * s)],
        fill=(217, 155, 58, 210),
        width=max(2, int(3 * s)),
    )

    for idx, (ln, f) in enumerate(zip(lines, fonts)):
        ly = y0 + pad_y + int(line_h * (idx + 0.5)) - int(2 * s)
        fill = (255, 255, 255, 255) if idx == 0 else (253, 232, 138, 255)
        draw_text_with_shadow(draw, (w / 2, ly), ln, f, fill, shadow_offset=int(2 * s))

    return img


def build_endcard_image(w: int, h: int, bg_frame: Image.Image, is_en: bool) -> Image.Image:
    """
    Renders the prestigious 27.0-30.0s Fine Atlas Brand Closing Card (President's Plan exact copy)
    over a deeply blurred luxury dark-navy rendition of the finished dish frame.
    """
    s = w / 1080.0
    bg = bg_frame.resize((w, h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=int(28 * s)))
    navy = Image.new("RGB", (w, h), (9, 24, 42))
    base = Image.blend(bg, navy, alpha=0.84).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # Stately double gold border
    draw.rounded_rectangle(
        [int(48 * s), int(92 * s), w - int(48 * s), h - int(92 * s)],
        radius=int(28 * s),
        outline=(217, 155, 58, 245),
        width=max(3, int(4 * s)),
    )
    draw.rounded_rectangle(
        [int(64 * s), int(108 * s), w - int(64 * s), h - int(108 * s)],
        radius=int(20 * s),
        outline=(245, 242, 235, 85),
        width=max(1, int(2 * s)),
    )

    # Top brand seal
    draw.rounded_rectangle(
        [int(290 * s), int(270 * s), w - int(290 * s), int(342 * s)],
        radius=int(36 * s),
        fill=(186, 108, 22, 255),
    )
    draw.text((w / 2, int(306 * s)), "FINE ATLAS Co., Ltd.", font=get_font(FONT_SANS, int(32 * s)), fill=(255, 255, 255, 255), anchor="mm")

    comp = "株式会社ファインアトラス" if not is_en else "FINE ATLAS — JAPAN QUALITY FROZEN"
    f_comp = fit_font(draw, comp, FONT_SERIF if not is_en else FONT_SANS, int(46 * s), int(30 * s), int(w * 0.80))
    draw.text((w / 2, int(420 * s)), comp, font=f_comp, fill=(245, 242, 235, 255), anchor="mm")

    draw.line([int(200 * s), int(496 * s), w - int(200 * s), int(496 * s)], fill=(217, 155, 58, 200), width=max(2, int(3 * s)))

    # Hero Brand Catchphrase Card (exact President's Plan copy)
    draw.rounded_rectangle(
        [int(88 * s), int(564 * s), w - int(88 * s), int(972 * s)],
        radius=int(26 * s),
        fill=(14, 38, 64, 245),
        outline=(217, 155, 58, 255),
        width=max(3, int(4 * s)),
    )
    if not is_en:
        f_main = get_font(FONT_SERIF, int(56 * s))
        draw_text_with_shadow(draw, (w / 2, int(684 * s)), "「日本の旬と品質を、一箱に。", f_main, (255, 255, 255, 255), shadow_offset=int(3 * s))
        draw_text_with_shadow(draw, (w / 2, int(786 * s)), "世界の厨房へ。」", f_main, (253, 224, 102, 255), shadow_offset=int(3 * s))
        f_sub = fit_font(draw, CATCHPHRASE_EN, FONT_SANS, int(23 * s), int(16 * s), int(w * 0.78))
        draw.text((w / 2, int(902 * s)), CATCHPHRASE_EN, font=f_sub, fill=(203, 213, 225, 255), anchor="mm")
    else:
        f_main = get_font(FONT_SERIF, int(44 * s))
        en_lines = textwrap.wrap(f'"{CATCHPHRASE_EN}"', width=26)
        y_ln = int(662 * s)
        for ln in en_lines:
            draw_text_with_shadow(draw, (w / 2, y_ln), ln, f_main, (253, 224, 102, 255), shadow_offset=int(3 * s))
            y_ln += int(66 * s)
        draw.text((w / 2, int(904 * s)), f"「{CATCHPHRASE_JP}」", font=get_font(FONT_SERIF, int(27 * s)), fill=(245, 242, 235, 255), anchor="mm")

    # Clean, dignified B2B funnel strip (matches Chapter 1 & 11 honest trial-first policy)
    draw.rounded_rectangle(
        [int(96 * s), int(1070 * s), w - int(96 * s), int(1366 * s)],
        radius=int(22 * s),
        fill=(245, 242, 235, 246),
    )
    f_ft = get_font(FONT_SERIF if not is_en else FONT_SANS, int(33 * s))
    title_f = "まずは少量購入で、貴店の厨房にて品質確認" if not is_en else "Verify Quality First with a Small Trial Order"
    f_ft = fit_font(draw, title_f, FONT_SERIF if not is_en else FONT_SANS, int(34 * s), int(22 * s), int(w * 0.78))
    draw.text((w / 2, int(1136 * s)), title_f, font=f_ft, fill=(12, 34, 56, 255), anchor="mm")

    steps_line = (
        "HP・Amazon少量試作  ▶  リピート仕入れ  ▶  店舗別オリジナル魚BOX"
        if not is_en
        else "Website / Amazon Trial  ▶  Repeat Supply  ▶  Custom Fish Box"
    )
    f_st = fit_font(draw, steps_line, FONT_SANS, int(25 * s), int(18 * s), int(w * 0.78))
    draw.rounded_rectangle([int(128 * s), int(1192 * s), w - int(128 * s), int(1264 * s)], radius=int(14 * s), fill=(14, 38, 64, 255))
    draw.text((w / 2, int(1228 * s)), steps_line, font=f_st, fill=(253, 224, 102, 255), anchor="mm")

    sub_note = (
        "産地で時間を止め、世界の厨房で時間を動かす。"
        if not is_en
        else "Freezing peak freshness at the port. Serving chefs worldwide."
    )
    f_sn = fit_font(draw, sub_note, FONT_SANS, int(24 * s), int(17 * s), int(w * 0.78))
    draw.text((w / 2, int(1318 * s)), sub_note, font=f_sn, fill=(51, 65, 85, 255), anchor="mm")

    # CTA Pill
    draw.rounded_rectangle(
        [int(138 * s), int(1464 * s), w - int(138 * s), int(1572 * s)],
        radius=int(28 * s),
        fill=(164, 54, 34, 255),
        outline=(253, 224, 102, 190),
        width=max(2, int(2 * s)),
    )
    cta = "fineatlas.co.jp ｜ Amazon「ファインアトラス」" if not is_en else "fineatlas.co.jp | Search 'FINE ATLAS' on Amazon"
    f_cta = fit_font(draw, cta, FONT_SANS, int(31 * s), int(21 * s), int(w * 0.72))
    draw.text((w / 2, int(1518 * s)), cta, font=f_cta, fill=(255, 255, 255, 255), anchor="mm")

    return base.convert("RGB")


def composite_cinema_edition(
    clean_base_mp4: Path,
    narration_wav: Path,
    bgm_wav: Path,
    sub_schedule: list,
    ep: dict,
    is_en: bool,
    out_mp4: Path,
    w: int = 1080,
    h: int = 1920,
):
    """
    Composites full-bleed 9:16 cinema video + translucent vignettes + header + synced subtitles +
    verified data plaques + 27.0-30.0s official brand closing card + 3-layer mastered audio.
    """
    total_frames = int(round(TOTAL_FINAL_SEC * FPS))  # 720 frames @ 24fps = 30.00s exact

    # Grab a single frame near the end of cut4 (26.5s) as the blurred base for the closing card
    base_dur = probe_media(clean_base_mp4)["duration"]
    sample_t = max(0.5, base_dur - 1.0)
    fb = w * h * 3
    p_end = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", f"{sample_t:.2f}", "-i", str(clean_base_mp4),
            "-frames:v", "1", "-vf", f"scale={w}:{h}:flags=lanczos",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ],
        capture_output=True,
        check=True,
    )
    end_ref_frame = Image.frombytes("RGB", (w, h), p_end.stdout[:fb])

    # Pre-render static & per-beat RGBA layers once (fast & pixel-accurate)
    vignette = build_cinema_vignette(w, h)
    header_layer = build_top_header_layer(w, h, ep, is_en)
    static_chrome = Image.alpha_composite(vignette, header_layer)

    plaques_spec = ep["plaques_en"] if is_en else ep["plaques_jp"]
    plaque_layers = [
        (st, en, build_plaque_layer(w, h, lbl, val, is_en)) for (st, en, lbl, val) in plaques_spec
    ]
    sub_layers = [
        (item["start"], item["end"], build_subtitle_layer(w, h, item["lines"], is_en)) for item in sub_schedule
    ]

    endcard_rgb = build_endcard_image(w, h, end_ref_frame, is_en)

    # First master the 3-layer audio track (ambient sizzle + neural narration + subtle koto BGM)
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        master_audio_wav = td_path / "master_audio.wav"
        af_graph = (
            f"[0:a]apad=whole_dur={TOTAL_FINAL_SEC:.2f},atrim=0:{TOTAL_FINAL_SEC:.2f},"
            f"volume=0.38,afade=t=in:st=0:d={FADE_IN_DUR:.2f},afade=t=out:st={ENDCARD_START_SEC:.2f}:d=1.20[amb];"
            f"[1:a]apad=whole_dur={TOTAL_FINAL_SEC:.2f},atrim=0:{TOTAL_FINAL_SEC:.2f},volume=1.18[vox];"
            f"[2:a]atrim=0:{TOTAL_FINAL_SEC:.2f},volume=0.14,afade=t=in:st=0:d=0.80,afade=t=out:st={TOTAL_FINAL_SEC - FADE_OUT_DUR:.2f}:d={FADE_OUT_DUR:.2f}[bgm];"
            f"[amb][vox][bgm]amix=inputs=3:normalize=0:duration=first,"
            f"alimiter=limit=0.92:attack=5:release=50[aout]"
        )
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(clean_base_mp4),
                "-i", str(narration_wav),
                "-i", str(bgm_wav),
                "-filter_complex", af_graph,
                "-map", "[aout]",
                "-ar", "48000", "-ac", "2",
                str(master_audio_wav),
            ],
            check=True,
        )

        # Open streaming FFmpeg decoder & encoder pipes (constant ~25MB RAM!)
        dec_cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", str(clean_base_mp4),
            "-vf", f"scale={w}:{h}:flags=lanczos,fps={FPS}",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ]
        enc_cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{w}x{h}", "-pix_fmt", "rgb24", "-r", str(FPS),
            "-i", "-",
            "-i", str(master_audio_wav),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-crf", "17", "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest", "-movflags", "+faststart",
            str(out_mp4),
        ]
        dec_proc = subprocess.Popen(dec_cmd, stdout=subprocess.PIPE)
        enc_proc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)
        black_frame = Image.new("RGB", (w, h), (0, 0, 0))
        last_valid = end_ref_frame

        def fade_alpha(t_cur: float, st: float, en: float, dur: float = 0.28) -> float:
            if t_cur < st or t_cur > en:
                return 0.0
            a_in = min(1.0, (t_cur - st) / dur)
            a_out = min(1.0, (en - t_cur) / dur)
            return max(0.0, min(a_in, a_out))

        for fi in range(total_frames):
            t_sec = fi / FPS
            raw = dec_proc.stdout.read(fb)
            if len(raw) == fb:
                last_valid = Image.frombytes("RGB", (w, h), raw)

            if t_sec < ENDCARD_START_SEC + XFADE_DUR:
                frame_rgba = last_valid.convert("RGBA")
                chrome_a = fade_alpha(t_sec, 0.0, ENDCARD_START_SEC + 0.10, dur=0.45)
                if chrome_a > 0.01:
                    if chrome_a < 0.99:
                        tmp_ch = static_chrome.copy()
                        tmp_ch.putalpha(tmp_ch.getchannel("A").point(lambda v: int(v * chrome_a)))
                        frame_rgba = Image.alpha_composite(frame_rgba, tmp_ch)
                    else:
                        frame_rgba = Image.alpha_composite(frame_rgba, static_chrome)

                for pst, pen, p_img in plaque_layers:
                    pa = fade_alpha(t_sec, pst, pen, dur=0.35)
                    if pa > 0.01:
                        if pa < 0.99:
                            tmp_p = p_img.copy()
                            tmp_p.putalpha(tmp_p.getchannel("A").point(lambda v: int(v * pa)))
                            frame_rgba = Image.alpha_composite(frame_rgba, tmp_p)
                        else:
                            frame_rgba = Image.alpha_composite(frame_rgba, p_img)

                for sst, sen, s_img in sub_layers:
                    sa = fade_alpha(t_sec, sst, sen, dur=0.22)
                    if sa > 0.01:
                        if sa < 0.99:
                            tmp_s = s_img.copy()
                            tmp_s.putalpha(tmp_s.getchannel("A").point(lambda v: int(v * sa)))
                            frame_rgba = Image.alpha_composite(frame_rgba, tmp_s)
                        else:
                            frame_rgba = Image.alpha_composite(frame_rgba, s_img)

                cur_rgb = frame_rgba.convert("RGB")
                if t_sec >= ENDCARD_START_SEC:
                    mix_p = min(1.0, (t_sec - ENDCARD_START_SEC) / XFADE_DUR)
                    mix_smooth = 0.5 - 0.5 * math.cos(math.pi * mix_p)
                    cur_rgb = Image.blend(cur_rgb, endcard_rgb, alpha=mix_smooth)
            else:
                cur_rgb = endcard_rgb

            if t_sec < FADE_IN_DUR:
                cur_rgb = Image.blend(black_frame, cur_rgb, alpha=t_sec / FADE_IN_DUR)
            elif t_sec > TOTAL_FINAL_SEC - FADE_OUT_DUR:
                rem = max(0.0, (TOTAL_FINAL_SEC - t_sec) / FADE_OUT_DUR)
                cur_rgb = Image.blend(black_frame, cur_rgb, alpha=rem)

            enc_proc.stdin.write(cur_rgb.tobytes())

        dec_proc.stdout.close()
        dec_proc.wait()
        enc_proc.stdin.close()
        ret = enc_proc.wait()
        if ret != 0:
            raise RuntimeError(f"FFmpeg cinema composition failed with code {ret}")

    return probe_media(out_mp4)


def main():
    parser = argparse.ArgumentParser(description="Fine Atlas 4K 60fps Master Preparation & 30s Cinema Studio")
    parser.add_argument("--episode", default="DAY-02", choices=list(EPISODE_PRESETS.keys()))
    parser.add_argument("--aspect", default="both", choices=["9x16", "16x9", "both"])
    parser.add_argument("--slow-cuts", default="1", help="Comma-separated 1-based cut indices to slow down to 0.75x with optical flow (e.g. '1' or '1,2' or 'none')")
    parser.add_argument("--crop-centers", default="0.50,0.36,0.50,0.50", help="Comma-separated horizontal focal ratios (0..1) for 9:16 portrait crop per cut")
    parser.add_argument("--skip-cinema", action="store_true", help="Only build clean master_720p.mp4 + contact sheet (skip bilingual cinema overlay editions)")
    parser.add_argument("--reuse-clean", action="store_true", help="Reuse cached output/overlay_tracks/clean_9x16_nofadeout.mp4 for fast narration/subtitle compositing")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    clip_files = sorted(CLIPS_DIR.glob("cut*.mp4"))
    if len(clip_files) < 2:
        print(f"[ERROR] clips/ に cut1.mp4〜 の動画が2本以上必要です（現在 {len(clip_files)} 本）", file=sys.stderr)
        sys.exit(1)

    slow_set = set()
    if args.slow_cuts.strip().lower() != "none":
        slow_set = {int(x.strip()) for x in args.slow_cuts.split(",") if x.strip()}

    crop_ratios = [float(x.strip()) for x in args.crop_centers.split(",") if x.strip()]
    while len(crop_ratios) < len(clip_files):
        crop_ratios.append(0.50)

    ep = EPISODE_PRESETS[args.episode]
    reports = []

    print(f"=== FINE ATLAS 動画マスター制作パイプライン開始 ({args.episode}: {ep['fish_jp']}) ===")
    print(f"入力クリップ: {[p.name for p in clip_files]} | 0.75xスロー補間対象: {sorted(slow_set)}")

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        # ------------------------------------------------------------------
        # 1. Preprocess 9:16 clips ONCE at 1080x1920 @ 24fps (optical-flow 0.75x slow on selected cuts),
        #    then derive BOTH:
        #      a) Clean Colab 4K/60fps Master (`output/master_720p.mp4`, 720x1280 via crisp Lanczos)
        #      b) Ready-to-Share 30.00s Bilingual Cinema Editions (1080x1920 JP & EN)
        # ------------------------------------------------------------------
        base_1080_clean = None
        cached_clean = OVERLAY_DIR / "clean_9x16_nofadeout.mp4"
        if args.reuse_clean and cached_clean.exists() and cached_clean.stat().st_size > 100_000:
            print(f"\n[1/4] キャッシュ済みクリーン映像を再利用します: {cached_clean.name}")
            base_1080_clean = cached_clean
            if (OUTPUT_DIR / "master_720p.mp4").exists():
                reports.append(("縦型9:16 クリーンマスター (Colab 4K60投入用)", probe_media(OUTPUT_DIR / "master_720p.mp4")))
            if (OUTPUT_DIR / "master_720p_16x9.mp4").exists():
                reports.append(("横型16:9 切替マスター (1280x720)", probe_media(OUTPUT_DIR / "master_720p_16x9.mp4")))
        elif args.aspect in ("9x16", "both") or not args.skip_cinema:
            print("\n[1/4] 縦型 9:16 各カット正規化 & オプティカルフロー0.75倍スロー補間を実行中...")
            norm_1080 = []
            for idx, cf in enumerate(clip_files, start=1):
                dst = td_path / f"norm1080_cut{idx}.mp4"
                is_slow = idx in slow_set
                print(
                    f"  - {cf.name} -> 1080x1920 24fps "
                    f"({'★0.75x オプティカルフロー補間(minterpolate) + atempo=0.75' if is_slow else '等速 1.0x'})..."
                )
                preprocess_clip(cf, dst, 1080, 1920, is_slow=is_slow, crop_x_ratio=crop_ratios[idx - 1])
                norm_1080.append(dst)

            base_1080_clean = td_path / "base_1080_clean_nofadeout.mp4"
            concat_with_crossfades(norm_1080, base_1080_clean, apply_end_fade=False)

            if args.aspect in ("9x16", "both"):
                master_9x16 = OUTPUT_DIR / "master_720p.mp4"
                base_dur = probe_media(base_1080_clean)["duration"]
                fo_st = max(0.0, base_dur - FADE_OUT_DUR)
                subprocess.run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-i",
                        str(base_1080_clean),
                        "-vf",
                        f"scale=720:1280:flags=lanczos,fade=t=out:st={fo_st:.3f}:d={FADE_OUT_DUR:.3f},format=yuv420p",
                        "-af",
                        f"afade=t=out:st={fo_st:.3f}:d={FADE_OUT_DUR:.3f}",
                        "-c:v",
                        "libx264",
                        "-crf",
                        "16",
                        "-preset",
                        "fast",
                        "-r",
                        str(FPS),
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-ar",
                        "48000",
                        "-ac",
                        "2",
                        "-movflags",
                        "+faststart",
                        str(master_9x16),
                    ],
                    check=True,
                )
                info_9x16 = probe_media(master_9x16)
                reports.append(("縦型9:16 クリーンマスター (Colab 4K60投入用)", info_9x16))
                # Also export tail-fade-free 720x1280 clip for seamless 27s->30s closing card blending in Colab
                subprocess.run(
                    [
                        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(base_1080_clean),
                        "-vf", "scale=720:1280:flags=lanczos,format=yuv420p",
                        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-r", str(FPS),
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                        "-movflags", "+faststart",
                        str(OVERLAY_DIR / "clean_9x16_nofadeout.mp4"),
                    ],
                    check=True,
                )
                make_contact_sheet_4x2(
                    master_9x16,
                    OUTPUT_DIR / "contact_sheet_4x2.jpg",
                    f"FINE ATLAS {args.episode} クリーン連結マスター（9:16・24fps・cut1 0.75xスロー補間＋0.70sクロスフェード）",
                )
                print(f"  [OK] {master_9x16.name}: {info_9x16['duration']:.2f}s / {info_9x16['size_mb']:.2f} MB")

        # ------------------------------------------------------------------
        # 2. Optional 16:9 Horizontal Master (`output/master_720p_16x9.mp4`, 1280x720 @ 24fps)
        # ------------------------------------------------------------------
        if args.aspect in ("16x9", "both"):
            print("\n[2/4] 横型 16:9 切替マスター (1280x720 @ 24fps) を生成中...")
            norm_16x9 = []
            for idx, cf in enumerate(clip_files, start=1):
                dst = td_path / f"norm16x9_cut{idx}.mp4"
                is_slow = idx in slow_set
                print(f"  - {cf.name} -> 1280x720 24fps ({'0.75x オプティカルフロー補間スロー' if is_slow else '等速 1.0x'})...")
                preprocess_clip(cf, dst, 1280, 720, is_slow=is_slow, crop_x_ratio=0.50)
                norm_16x9.append(dst)

            master_16x9 = OUTPUT_DIR / "master_720p_16x9.mp4"
            info_16x9 = concat_with_crossfades(norm_16x9, master_16x9, apply_end_fade=True)
            reports.append(("横型16:9 切替マスター (1280x720)", info_16x9))
            make_contact_sheet_4x2(
                master_16x9,
                OUTPUT_DIR / "contact_sheet_16x9_4x2.jpg",
                f"FINE ATLAS {args.episode} 横型16:9 切替マスター（1280x720・24fps）",
            )
            print(f"  [OK] {master_16x9.name}: {info_16x9['duration']:.2f}s / {info_16x9['size_mb']:.2f} MB")

        # ------------------------------------------------------------------
        # 3. Ready-to-Share 1080x1920 Bilingual 30.00s Cinema Editions + Colab Overlay Pack
        # ------------------------------------------------------------------
        if not args.skip_cinema:
            print("\n[3/4] 日英プロナレーション (edge-tts) & 和風琴アンビエントBGMを生成中...")

            bgm_wav = OVERLAY_DIR / "bgm_koto_30s.wav"
            generate_koto_cinema_bgm(bgm_wav, duration=TOTAL_FINAL_SEC)

            narration_jp_wav = OVERLAY_DIR / "narration_jp_30s.wav"
            narration_en_wav = OVERLAY_DIR / "narration_en_30s.wav"
            sub_jp = build_synced_narration(ep["beats_jp"], is_en=False, out_wav=narration_jp_wav, tmp_dir=td_path)
            sub_en = build_synced_narration(ep["beats_en"], is_en=True, out_wav=narration_en_wav, tmp_dir=td_path)

            # Save manifest for Google Colab 4K 60fps native-4K overlay compositing
            manifest = {
                "episode": args.episode,
                "code": ep["code"],
                "total_duration_sec": TOTAL_FINAL_SEC,
                "endcard_start_sec": ENDCARD_START_SEC,
                "xfade_sec": XFADE_DUR,
                "fade_in_sec": FADE_IN_DUR,
                "fade_out_sec": FADE_OUT_DUR,
                "slow_cuts": sorted(slow_set),
                "episode_meta": {
                    k: ep[k]
                    for k in (
                        "fish_jp",
                        "fish_en",
                        "category_jp",
                        "category_en",
                        "headline_jp",
                        "subhead_jp",
                        "headline_en",
                        "subhead_en",
                        "plaques_jp",
                        "plaques_en",
                    )
                },
                "subtitles_jp": sub_jp,
                "subtitles_en": sub_en,
                "audio_files": {
                    "narration_jp": narration_jp_wav.name,
                    "narration_en": narration_en_wav.name,
                    "bgm": bgm_wav.name,
                },
            }
            (OVERLAY_DIR / "overlay_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            print("\n[4/4] 社長計画書準拠 30.00秒 日英シネマ完成版 (1080x1920) を合成中...")
            jp_mp4 = OUTPUT_DIR / f"{ep['code']}_9x16_jp.mp4"
            en_mp4 = OUTPUT_DIR / f"{ep['code']}_9x16_en.mp4"

            info_jp = composite_cinema_edition(base_1080_clean, narration_jp_wav, bgm_wav, sub_jp, ep, False, jp_mp4)
            reports.append(("完成版 日本語 30秒シネマ (1080x1920)", info_jp))
            make_contact_sheet_4x2(
                jp_mp4,
                OUTPUT_DIR / "contact_sheet_cinema_jp_4x2.jpg",
                f"FINE ATLAS {args.episode} 日本語30秒シネマ完成版（9:16フル画面・同期字幕・品質証札・公式締め）",
            )

            info_en = composite_cinema_edition(base_1080_clean, narration_en_wav, bgm_wav, sub_en, ep, True, en_mp4)
            reports.append(("完成版 英語 30秒シネマ (1080x1920)", info_en))
            make_contact_sheet_4x2(
                en_mp4,
                OUTPUT_DIR / "contact_sheet_cinema_en_4x2.jpg",
                f"FINE ATLAS {args.episode} English 30s Cinema Edition (9:16 Full-Bleed, Synced Subs & Brand Closing)",
            )

    # Save deterministic JSON report & print summary
    report_path = OUTPUT_DIR / "build_report.json"
    report_path.write_text(
        json.dumps([{"label": lbl, **inf} for lbl, inf in reports], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n================ 出力結果サマリー ================")
    for lbl, inf in reports:
        vs = inf["video"]
        aus = inf["audio"]
        a_str = f"あり ({aus['codec_name']} {aus['sample_rate']}Hz {aus['channels']}ch)" if aus else "なし"
        print(
            f"■ {lbl}\n"
            f"  ファイル: {Path(inf['path']).name}\n"
            f"  解像度  : {vs['width']}x{vs['height']} | fps: {vs['r_frame_rate']} | 再生時間: {inf['duration']:.2f}秒\n"
            f"  サイズ  : {inf['size_mb']:.2f} MB | 音声: {a_str}"
        )
    print("==================================================")


if __name__ == "__main__":
    main()
