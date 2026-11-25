#!/usr/bin/env python3
"""
FINE ATLAS 🎬 Antigravity Direct Short Video Renderer (`render_short_video.py`)
=============================================================================
Replaces Vrew + Canva completely inside Antigravity!
Combines real Tsushima Suisan photos & vertical/horizontal videos from Google Drive
with neural AI narration (Japanese & English), ambient Japanese koto-style BGM,
high-contrast burned-in subtitles (for mute playback), and the official 27-30s closing card:
  JP: 「日本の旬と品質を、一箱に。世界の厨房へ。」
  EN: "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."

Output spec (President's Plan Section 4):
  - Duration: 30.0 seconds (0-3s Hook / 3-20s Main / 20-27s Climax / 27-30s Brand Closing)
  - Aspect Ratio: Vertical 9:16
  - Resolution: 1080x1920 (H.264 MP4 + AAC 44.1kHz stereo)
"""

import argparse
import asyncio
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import textwrap
import wave
from pathlib import Path
import edge_tts
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "assets" / "gdrive_raw"
VIDEOS_DIR = ROOT_DIR / "videos"
DATA_JS_PATH = ROOT_DIR / "data.js"

FONT_SANS_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

CATCHPHRASE_JP = "日本の旬と品質を、一箱に。世界の厨房へ。"
CATCHPHRASE_EN = "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."

# Default Google Drive file mapping per fish species (verified real Tsushima Suisan assets)
FISH_GDRIVE_ASSETS = {
    "のどぐろ": {
        "hook": {"id": "1wrzyfcmnXPoGt0HK-xnb1BUKMbvNmg4m", "file": "nodoguro_aburi.jpg", "type": "image", "driveLabel": "のどぐろ茶漬け（炙り中）.jpg"},
        "body1": {"id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe", "file": "toumin_machine.jpg", "type": "image", "driveLabel": "凍眠機械と甘鯛と田中.jpg（急速冷凍ライン）"},
        "body2": {"id": "14liGrV4JrkmuAXYboPdtNoFib9im_COE", "file": "nodoguro_course1.jpg", "type": "image", "driveLabel": "_MG_6971のどぐろのコース1.jpg"},
        "climax": {"id": "1fpyKM6SuPUtotPZtmlnFbj_ejDHjbQLc", "file": "nodoguro_sashimi.jpg", "type": "image", "driveLabel": "_MG_7092のどぐろ刺身.jpg"},
    },
    "甘鯛": {
        "hook": {"id": "1VcdZFkmB7abt0kCI0fNi4duiOrh_YTE5", "file": "amadai_uroko.jpg", "type": "image", "driveLabel": "甘鯛鱗揚げ(焼きシーン).jpg"},
        "body1": {"id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe", "file": "toumin_machine.jpg", "type": "image", "driveLabel": "凍眠機械と甘鯛と田中.jpg"},
        "body2": {"id": "1nF52eOGaVlD5QxqycXsj7V7Mo2qx7jQZ", "file": "amadai_thaw_cook.mp4", "type": "video", "driveLabel": "解凍甘鯛作り方20230106.mp4"},
        "climax": {"id": "1VcdZFkmB7abt0kCI0fNi4duiOrh_YTE5", "file": "amadai_uroko.jpg", "type": "image", "driveLabel": "甘鯛鱗揚げ(焼きシーン).jpg"},
    },
    "煮穴子": {
        "hook": {"id": "1IIHi5-emj7Q0DZY3WNRFPFs3NndhRoVe", "file": "densuke_nianago_sushi.mp4", "type": "video", "driveLabel": "20221212_久乃様_伝助煮穴子寿司.mp4"},
        "body1": {"id": "1w-XTD0ou6kLd6-JECMcW1rWdroC6nevp", "file": "anago_pack.jpg", "type": "image", "driveLabel": "2509穴子飯梱包_中見せ.jpg"},
        "body2": {"id": "1YvmW3-yBtELNXtJZz3y65dSC-mYrnbYs", "file": "anago_sashimi_insta.mp4", "type": "video", "driveLabel": "0240621_INSTA_穴子フィレ_刺身.mp4"},
        "climax": {"id": "1nVUkKKNDAhv7w1VAytXlp9Tk53VLFgPe", "file": "nianago_sushi.png", "type": "image", "driveLabel": "煮穴子握り寿司2貫S.png"},
    },
    "穴子フィレ": {
        "hook": {"id": "1YvmW3-yBtELNXtJZz3y65dSC-mYrnbYs", "file": "anago_sashimi_insta.mp4", "type": "video", "driveLabel": "0240621_INSTA_穴子フィレ_刺身.mp4"},
        "body1": {"id": "1w-XTD0ou6kLd6-JECMcW1rWdroC6nevp", "file": "anago_pack.jpg", "type": "image", "driveLabel": "2509穴子飯梱包_中見せ.jpg"},
        "body2": {"id": "1IIHi5-emj7Q0DZY3WNRFPFs3NndhRoVe", "file": "densuke_nianago_sushi.mp4", "type": "video", "driveLabel": "20221212_久乃様_伝助煮穴子寿司.mp4"},
        "climax": {"id": "1nVUkKKNDAhv7w1VAytXlp9Tk53VLFgPe", "file": "nianago_sushi.png", "type": "image", "driveLabel": "煮穴子握り寿司2貫S.png"},
    },
    "剣先イカ": {
        "hook": {"id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM", "file": "kensaki_ika.jpg", "type": "image", "driveLabel": "剣先イカ補正2.jpg"},
        "body1": {"id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe", "file": "toumin_machine.jpg", "type": "image", "driveLabel": "凍眠機械と甘鯛と田中.jpg"},
        "body2": {"id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM", "file": "kensaki_ika.jpg", "type": "image", "driveLabel": "剣先イカ補正2.jpg"},
        "climax": {"id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM", "file": "kensaki_ika.jpg", "type": "image", "driveLabel": "剣先イカ補正2.jpg"},
    }
}


def load_data_js():
    text = DATA_JS_PATH.read_text(encoding="utf-8")
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


def ensure_gdrive_asset(asset_info):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    local_path = RAW_DIR / asset_info["file"]
    if not local_path.exists() or local_path.stat().st_size == 0:
        print(f"  [gdrive] Downloading {asset_info['driveLabel']} ({asset_info['id']}) -> {local_path.name}")
        subprocess.run(
            ["gdrive", "readonly", "download", asset_info["id"], "--out", str(local_path)],
            check=True
        )
    return local_path


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text_lines(text, is_en, max_chars_jp=19, max_chars_en=34):
    if is_en:
        return textwrap.wrap(text, width=max_chars_en)
    # Japanese line wrapping avoiding orphan punctuation at start of line
    lines = []
    buf = ""
    for ch in text:
        buf += ch
        if len(buf) >= max_chars_jp and ch not in "、。！？）」』":
            lines.append(buf)
            buf = ""
    if buf:
        if lines and len(buf) <= 2:
            lines[-1] += buf
        else:
            lines.append(buf)
    return lines[:4]


def create_overlay_png(
    out_path: Path,
    ep_id: str,
    weekday_label: str,
    theme_label: str,
    fish_label: str,
    top_title: str,
    sec_badge: str,
    subtitle_text: str,
    fact_badge: str,
    asset_credit: str,
    is_en: bool,
    is_closing: bool = False
):
    """
    Renders a transparent 1080x1920 PNG overlay containing:
    - Top header bar (Fine Atlas branding + Episode ID + Theme + Top Hook Title)
    - Fact badge pill (Yield % / FL Cost Ratio / Rapid Freezing spec)
    - High-contrast subtitle box in the lower safe zone (y=1240..1580) for mute playback
    - Bottom footer strip (Google Drive real asset credit + Fine Atlas slogan)
    """
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = get_font(FONT_SANS_BOLD, 28)
    f_title = get_font(FONT_SANS_BOLD, 42 if not is_en else 36)
    f_sub = get_font(FONT_SANS_BOLD, 44 if not is_en else 38)
    f_fact = get_font(FONT_SANS_BOLD, 30)
    f_small = get_font(FONT_SANS_BOLD, 23)
    f_closing_big = get_font(FONT_SERIF_BOLD, 56 if not is_en else 44)
    f_closing_sub = get_font(FONT_SANS_BOLD, 34 if not is_en else 30)

    if is_closing:
        # Full 1080x1920 luxury Deep Ocean Navy & Gold Closing Card (27-30s)
        draw.rectangle([0, 0, W, H], fill=(12, 34, 56, 242))
        # Gold border frame
        draw.rounded_rectangle([48, 80, W - 48, H - 80], radius=32, outline=(217, 119, 6, 255), width=5)
        draw.rounded_rectangle([64, 96, W - 64, H - 96], radius=24, outline=(245, 242, 235, 90), width=2)

        # Top emblem
        draw.rounded_rectangle([320, 210, 760, 286], radius=38, fill=(217, 119, 6, 255))
        draw.text((540, 248), "FINE ATLAS Co., Ltd.", font=get_font(FONT_SANS_BOLD, 34), fill=(255, 255, 255, 255), anchor="mm")

        company_jp = "株式会社ファインアトラス" if not is_en else "FINE ATLAS — JAPANESE SEAFOOD MEDIA"
        draw.text((540, 355), company_jp, font=get_font(FONT_SERIF_BOLD, 48 if not is_en else 36), fill=(245, 242, 235, 255), anchor="mm")

        # Divider
        draw.line([180, 430, 900, 430], fill=(217, 119, 6, 200), width=3)

        # Core Catchphrase (27-30s exact President's Plan specification)
        draw.rounded_rectangle([88, 490, W - 88, 830], radius=28, fill=(18, 49, 79, 255), outline=(217, 119, 6, 255), width=4)
        if not is_en:
            draw.text((540, 595), "「日本の旬と品質を、一箱に。", font=f_closing_big, fill=(255, 255, 255, 255), anchor="mm")
            draw.text((540, 695), "　世界の厨房へ。」", font=f_closing_big, fill=(253, 224, 71, 255), anchor="mm")
            draw.text((540, 780), CATCHPHRASE_EN, font=get_font(FONT_SANS_BOLD, 25), fill=(203, 213, 225, 255), anchor="mm")
        else:
            en_lines = textwrap.wrap(f'"{CATCHPHRASE_EN}"', width=28)
            y_en = 575
            for line in en_lines:
                draw.text((540, y_en), line, font=f_closing_big, fill=(253, 224, 71, 255), anchor="mm")
                y_en += 68
            draw.text((540, 780), f"（{CATCHPHRASE_JP}）", font=get_font(FONT_SANS_BOLD, 28), fill=(245, 242, 235, 255), anchor="mm")

        # Sales Funnel Call-To-Action Box (Section 1 & 11)
        draw.rounded_rectangle([88, 900, W - 88, 1420], radius=24, fill=(245, 242, 235, 250))
        funnel_head = "📦 ご注文・品質確認から法人契約まで" if not is_en else "📦 From Small Trial Order to Custom B2B Box"
        draw.text((540, 965), funnel_head, font=get_font(FONT_SANS_BOLD, 36), fill=(12, 34, 56, 255), anchor="mm")

        steps = (
            [
                "STEP 1｜ホームページ・Amazonへアクセス",
                "STEP 2｜まずは少量購入で品質・歩留まりを確認",
                "STEP 3｜リピート購入・定期仕入れで仕込み時短",
                "STEP 4｜法人契約・店舗別オリジナル魚BOX受注"
            ]
            if not is_en
            else [
                "STEP 1 | Visit fineatlas.co.jp or Amazon",
                "STEP 2 | Small trial order to verify yield & quality",
                "STEP 3 | Repeat orders for zero-waste kitchen prep",
                "STEP 4 | B2B Contract & Custom Restaurant Fish Box"
            ]
        )
        y_st = 1055
        for st in steps:
            draw.rounded_rectangle([130, y_st - 34, W - 130, y_st + 34], radius=14, fill=(12, 34, 56, 255))
            draw.text((165, y_st), st, font=f_closing_sub, fill=(255, 255, 255, 255), anchor="lm")
            y_st += 88

        # Bottom URL banner
        draw.rounded_rectangle([140, 1490, W - 140, 1610], radius=30, fill=(200, 75, 49, 255))
        cta_bottom = "🔗 fineatlas.co.jp ｜ Amazon「ファインアトラス」検索" if not is_en else "🔗 fineatlas.co.jp | Search 'FINE ATLAS' on Amazon"
        draw.text((540, 1550), cta_bottom, font=get_font(FONT_SANS_BOLD, 33), fill=(255, 255, 255, 255), anchor="mm")

        img.save(out_path)
        return

    # 1. Top dark gradient / header card (y=0..360)
    draw.rectangle([0, 0, W, 355], fill=(12, 34, 56, 218))
    draw.line([0, 355, W, 355], fill=(217, 119, 6, 255), width=5)

    # Top Badges row (y=68)
    draw.rounded_rectangle([44, 48, 340, 108], radius=16, fill=(217, 119, 6, 255))
    draw.text((192, 78), f"FINE ATLAS｜{ep_id}", font=f_tag, fill=(255, 255, 255, 255), anchor="mm")

    draw.rounded_rectangle([358, 48, 760, 108], radius=16, fill=(24, 62, 98, 255), outline=(217, 119, 6, 220), width=2)
    draw.text((559, 78), f"{weekday_label}｜{fish_label}", font=f_tag, fill=(253, 224, 71, 255), anchor="mm")

    draw.rounded_rectangle([778, 48, 1036, 108], radius=16, fill=(200, 75, 49, 255))
    draw.text((907, 78), sec_badge, font=f_tag, fill=(255, 255, 255, 255), anchor="mm")

    # Top Hook Title (2 lines max)
    title_lines = wrap_text_lines(top_title, is_en, max_chars_jp=21, max_chars_en=38)[:2]
    y_t = 165 if len(title_lines) > 1 else 195
    for tline in title_lines:
        draw.text((540, y_t), tline, font=f_title, fill=(255, 255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 220))
        y_t += 58

    # Theme sub-pill inside header
    draw.rounded_rectangle([60, 282, W - 60, 336], radius=12, fill=(245, 242, 235, 235))
    draw.text((540, 309), fact_badge, font=f_fact, fill=(12, 34, 56, 255), anchor="mm")

    # 2. High-Contrast Burned-In Subtitle Box (y=1240..1620) — 100% readable on mute!
    sub_lines = wrap_text_lines(subtitle_text, is_en, max_chars_jp=19, max_chars_en=34)
    box_h = max(170, 70 + len(sub_lines) * 64)
    box_top = 1580 - box_h
    box_bottom = 1580

    # Subtitle card with gold accent bar
    draw.rounded_rectangle([38, box_top, W - 38, box_bottom], radius=24, fill=(12, 34, 56, 232), outline=(217, 119, 6, 255), width=4)
    draw.rounded_rectangle([38, box_top, 60, box_bottom], radius=12, fill=(217, 119, 6, 255))

    y_sub = box_top + 54
    for idx, sline in enumerate(sub_lines):
        # Highlight numbers/yield/catchphrase in warm gold on first or key lines
        text_color = (253, 224, 71, 255) if ("85%" in sline or "27.9%" in sline or "一箱" in sline or "one box" in sline) else (255, 255, 255, 255)
        draw.text((548, y_sub), sline, font=f_sub, fill=text_color, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 240))
        y_sub += 62

    # 3. Bottom Footer Bar (y=1635..1870) — Real Google Drive Asset Badge + Catchphrase
    draw.rounded_rectangle([38, 1625, W - 38, 1715], radius=16, fill=(0, 0, 0, 185), outline=(255, 255, 255, 90), width=2)
    draw.text((540, 1652), f"📸 自社実写素材（Google Drive）: {asset_credit}", font=f_small, fill=(167, 243, 208, 255), anchor="mm")
    footer_catch = f"「{CATCHPHRASE_JP}」" if not is_en else f'"{CATCHPHRASE_EN}"'
    draw.text((540, 1688), footer_catch, font=f_small, fill=(245, 242, 235, 240), anchor="mm")

    img.save(out_path)


def prepare_vertical_canvas_image(src_img_path: Path, out_img_path: Path):
    """
    Converts any horizontal or vertical photo into a rich 1080x1920 vertical canvas:
    - Blurred, darkened full-bleed background of the same photo
    - Sharp, vibrant center photo frame (y=360..1360) so nothing is cropped awkwardly
    """
    W, H = 1080, 1920
    src = Image.open(src_img_path).convert("RGB")
    sw, sh = src.size

    # Background cover + blur
    scale_bg = max(W / sw, H / sh)
    bg_w, bg_h = int(sw * scale_bg), int(sh * scale_bg)
    bg = src.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    left = (bg_w - W) // 2
    top = (bg_h - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(radius=28))
    # Darken background slightly
    dark = Image.new("RGB", (W, H), (12, 34, 56))
    bg = Image.blend(bg, dark, alpha=0.45)

    # Foreground hero image inside y=355..1355 (height=1000, width=1080)
    target_w, target_h = 1040, 920
    scale_fg = max(target_w / sw, target_h / sh)
    fg_w, fg_h = int(sw * scale_fg), int(sh * scale_fg)
    fg = src.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    f_left = (fg_w - target_w) // 2
    f_top = (fg_h - target_h) // 2
    fg = fg.crop((f_left, f_top, f_left + target_w, f_top + target_h))

    bg.paste(fg, (20, 368))
    bg.save(out_img_path, quality=95)


def render_segment_video(
    media_path: Path,
    media_type: str,
    overlay_png: Path,
    out_mp4: Path,
    duration: float,
    zoom_dir: str = "in"
):
    """
    Renders a single segment MP4 (1080x1920, 30fps, H.264) combining a photo (with Ken Burns motion)
    or a real video clip with the transparent PNG overlay.
    """
    fps = 30
    frames = int(round(duration * fps))

    if media_type == "video":
        # Scale/pad video into 1080x1920 with blurred background and overlay PNG
        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
            f"[0:v]scale=1040:920:force_original_aspect_ratio=increase,crop=1040:920[fg];"
            f"[bg][fg]overlay=20:368[base];"
            f"[base][1:v]overlay=0:0:format=auto,fps={fps},format=yuv420p[v]"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-stream_loop", "-1", "-i", str(media_path),
            "-loop", "1", "-i", str(overlay_png),
            "-filter_complex", filter_complex,
            "-map", "[v]", "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
            str(out_mp4)
        ]
    else:
        # Prepare vertical canvas photo first, then apply gentle Ken Burns zoom on the foreground
        canvas_jpg = out_mp4.with_suffix(".canvas.jpg")
        prepare_vertical_canvas_image(media_path, canvas_jpg)
        z_expr = "min(zoom+0.0005,1.06)" if zoom_dir == "in" else "if(eq(on,1),1.06,max(zoom-0.0005,1.0))"
        filter_complex = (
            f"[0:v]zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps}[bg];"
            f"[bg][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-i", str(canvas_jpg),
            "-loop", "1", "-i", str(overlay_png),
            "-filter_complex", filter_complex,
            "-map", "[v]", "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
            str(out_mp4)
        ]
    subprocess.run(cmd, check=True)


def generate_japanese_ambient_bgm(wav_path: Path, duration: float = 30.0, sample_rate: int = 44100):
    """
    Synthesizes a warm, copyright-free Japanese pentatonic (Yo/In scale) ambient koto/marimba
    background music track in pure Python so videos have classy restaurant ambiance with zero copyright risk.
    """
    total_samples = int(duration * sample_rate)
    # Japanese Miyako-bushi / Pentatonic notes (D4, F4, G4, A4, C5, D5, F5, A5)
    notes = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46, 880.00]
    pattern = [0, 2, 3, 4, 3, 2, 1, 0, 2, 4, 5, 4, 3, 2, 0, 3]
    note_interval = 0.75  # seconds per plucked note

    buf = [0.0] * total_samples

    # Warm sub-pad drone (D3 = 146.83 Hz + A3 = 220.0 Hz)
    for i in range(total_samples):
        t = i / sample_rate
        env = min(1.0, t / 1.5) * min(1.0, (duration - t) / 1.8)
        drone = 0.12 * math.sin(2 * math.pi * 146.83 * t) + 0.08 * math.sin(2 * math.pi * 220.0 * t)
        buf[i] += drone * env

    # Plucked koto notes
    num_notes = int(duration / note_interval)
    for n_idx in range(num_notes):
        start_t = n_idx * note_interval
        freq = notes[pattern[n_idx % len(pattern)]]
        start_sample = int(start_t * sample_rate)
        decay_len = int(2.2 * sample_rate)
        for j in range(min(decay_len, total_samples - start_sample)):
            dt = j / sample_rate
            # Fast attack, exponential koto decay with harmonics
            pluck_env = min(1.0, dt / 0.012) * math.exp(-2.4 * dt)
            sig = (
                0.22 * math.sin(2 * math.pi * freq * dt)
                + 0.09 * math.sin(2 * math.pi * (freq * 2.0) * dt) * math.exp(-4.0 * dt)
                + 0.04 * math.sin(2 * math.pi * (freq * 3.0) * dt) * math.exp(-6.0 * dt)
            )
            buf[start_sample + j] += sig * pluck_env

    # Write stereo 16-bit WAV
    with wave.open(str(wav_path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for val in buf:
            clamped = max(-0.95, min(0.95, val))
            s16 = int(clamped * 32767)
            frames.extend(struct.pack("<hh", s16, s16))
        wf.writeframes(frames)


async def synthesize_tts_clip(text: str, voice: str, rate: str, out_mp3: Path):
    comm = edge_tts.Communicate(text, voice=voice, rate=rate)
    await comm.save(str(out_mp3))


def get_audio_duration(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True
    )
    return float(res.stdout.strip() or "0.0")


def fit_narration_to_slot(src_mp3: Path, slot_sec: float, out_wav: Path):
    """
    Ensures a narration audio clip fits cleanly inside `slot_sec` (e.g. 0-3s = 3.0s, 3-20s = 17.0s, etc.).
    If the TTS speech is slightly longer than `slot_sec - 0.15`, speeds it up gently with `atempo`
    and pads with silence to exact `slot_sec`.
    """
    dur = get_audio_duration(src_mp3)
    max_speech = max(1.0, slot_sec - 0.15)
    atempo_filter = "anull"
    if dur > max_speech:
        ratio = min(1.45, dur / max_speech)
        atempo_filter = f"atempo={ratio:.3f}"

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src_mp3),
        "-af", f"{atempo_filter},apad=whole_dur={slot_sec:.3f}",
        "-t", f"{slot_sec:.3f}",
        "-ar", "44100", "-ac", "2",
        str(out_wav)
    ]
    subprocess.run(cmd, check=True)


def render_episode(ep: dict, lang: str, include_bgm: bool = True) -> Path:
    """
    Renders a complete 30.0s 1080x1920 vertical MP4 for `ep` in `lang` ('jp' or 'en').
    """
    import edge_tts  # ensure imported

    is_en = (lang == "en")
    ep_id = ep["id"]
    fish_key = ep.get("featuredFish", "のどぐろ")
    assets_map = FISH_GDRIVE_ASSETS.get(fish_key, FISH_GDRIVE_ASSETS["のどぐろ"])

    # Ensure all 4 Google Drive real media files exist locally
    p_hook = ensure_gdrive_asset(assets_map["hook"])
    p_body1 = ensure_gdrive_asset(assets_map["body1"])
    p_body2 = ensure_gdrive_asset(assets_map["body2"])
    p_climax = ensure_gdrive_asset(assets_map["climax"])

    tc = ep["item3_timecode"]
    top_title = ep["item1_title"]["en" if is_en else "jp"]
    weekday = ep.get("dayOfWeek", "月曜日")
    theme = ep.get("themeCategory", "全国の旬の魚")

    # Split 3-20s narration into two sentences for visual pacing (3-11.5s and 11.5-20s)
    audio_0_3 = tc[0]["audioEn" if is_en else "audioJp"]
    audio_3_20_full = tc[1]["audioEn" if is_en else "audioJp"]
    audio_20_27 = tc[2]["audioEn" if is_en else "audioJp"]
    audio_27_30 = tc[3]["audioEn" if is_en else "audioJp"]

    if not is_en and "。" in audio_3_20_full:
        parts = [p.strip() + "。" for p in audio_3_20_full.split("。") if p.strip()]
        sub_3_11 = parts[0]
        sub_11_20 = "".join(parts[1:]) if len(parts) > 1 else parts[0]
    elif is_en and ", achieving" in audio_3_20_full:
        idx = audio_3_20_full.find(", achieving")
        sub_3_11 = audio_3_20_full[:idx] + "."
        sub_11_20 = "Achieving" + audio_3_20_full[idx + 11:]
    else:
        mid = len(audio_3_20_full) // 2
        sub_3_11 = audio_3_20_full[:mid]
        sub_11_20 = audio_3_20_full[mid:]

    fact_badge = (
        f"🎯 {theme}｜可食歩留まり85〜98%・飲食店原価率26.5〜30.2%"
        if not is_en
        else f"🎯 {fish_key} | 85-98% Usable Yield & 26.5-30.2% Food Cost Ratio"
    )

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"{ep_id}_{lang}" + ("" if include_bgm else "_nobgm")
    out_mp4 = VIDEOS_DIR / f"FA_{suffix}.mp4"

    with tempfile.TemporaryDirectory(prefix=f"fa_render_{suffix}_") as tmp:
        tdir = Path(tmp)

        # 1. Generate 5 transparent overlay PNGs (0-3s, 3-11.5s, 11.5-20s, 20-27s, 27-30s)
        ov1 = tdir / "ov1.png"
        ov2 = tdir / "ov2.png"
        ov3 = tdir / "ov3.png"
        ov4 = tdir / "ov4.png"
        ov5 = tdir / "ov5.png"

        create_overlay_png(ov1, ep_id, weekday, theme, fish_key, top_title, "0〜3s HOOK", audio_0_3, fact_badge, assets_map["hook"]["driveLabel"], is_en)
        create_overlay_png(ov2, ep_id, weekday, theme, fish_key, top_title, "3〜11s FACT 1", sub_3_11, fact_badge, assets_map["body1"]["driveLabel"], is_en)
        create_overlay_png(ov3, ep_id, weekday, theme, fish_key, top_title, "11〜20s FACT 2", sub_11_20, fact_badge, assets_map["body2"]["driveLabel"], is_en)
        create_overlay_png(ov4, ep_id, weekday, theme, fish_key, top_title, "20〜27s DISH", audio_20_27, fact_badge, assets_map["climax"]["driveLabel"], is_en)
        create_overlay_png(ov5, ep_id, weekday, theme, fish_key, top_title, "27〜30s LOGO", audio_27_30, fact_badge, "FINE ATLAS Official", is_en, is_closing=True)

        # 2. Render 5 video segments totaling exactly 30.0s (3.0 + 8.5 + 8.5 + 7.0 + 3.0 = 30.0s)
        seg1 = tdir / "seg1.mp4"
        seg2 = tdir / "seg2.mp4"
        seg3 = tdir / "seg3.mp4"
        seg4 = tdir / "seg4.mp4"
        seg5 = tdir / "seg5.mp4"

        render_segment_video(p_hook, assets_map["hook"]["type"], ov1, seg1, 3.0, zoom_dir="in")
        render_segment_video(p_body1, assets_map["body1"]["type"], ov2, seg2, 8.5, zoom_dir="out")
        render_segment_video(p_body2, assets_map["body2"]["type"], ov3, seg3, 8.5, zoom_dir="in")
        render_segment_video(p_climax, assets_map["climax"]["type"], ov4, seg4, 7.0, zoom_dir="out")
        render_segment_video(p_climax, "image" if assets_map["climax"]["type"] == "image" else "video", ov5, seg5, 3.0, zoom_dir="in")

        concat_list = tdir / "concat_v.txt"
        concat_list.write_text("\n".join([f"file '{s}'" for s in [seg1, seg2, seg3, seg4, seg5]]), encoding="utf-8")
        v_joined = tdir / "v_joined.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(v_joined)],
            check=True
        )

        # 3. Synthesize 4 AI Narration slots (0-3s = 3.0s, 3-20s = 17.0s, 20-27s = 7.0s, 27-30s = 3.0s)
        voice = "en-US-AndrewNeural" if is_en else "ja-JP-KeitaNeural"
        rate = "+8%" if is_en else "+12%"

        mp3_1, mp3_2, mp3_3, mp3_4 = tdir / "tts1.mp3", tdir / "tts2.mp3", tdir / "tts3.mp3", tdir / "tts4.mp3"

        async def run_all_tts():
            await asyncio.gather(
                synthesize_tts_clip(audio_0_3, voice, rate, mp3_1),
                synthesize_tts_clip(audio_3_20_full, voice, rate, mp3_2),
                synthesize_tts_clip(audio_20_27, voice, rate, mp3_3),
                synthesize_tts_clip(audio_27_30, voice, "+5%", mp3_4),
            )

        asyncio.run(run_all_tts())

        wav_1, wav_2, wav_3, wav_4 = tdir / "s1.wav", tdir / "s2.wav", tdir / "s3.wav", tdir / "s4.wav"
        fit_narration_to_slot(mp3_1, 3.0, wav_1)
        fit_narration_to_slot(mp3_2, 17.0, wav_2)
        fit_narration_to_slot(mp3_3, 7.0, wav_3)
        fit_narration_to_slot(mp3_4, 3.0, wav_4)

        concat_a = tdir / "concat_a.txt"
        concat_a.write_text("\n".join([f"file '{w}'" for w in [wav_1, wav_2, wav_3, wav_4]]), encoding="utf-8")
        narration_wav = tdir / "narration_30s.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_a), "-c", "copy", str(narration_wav)],
            check=True
        )

        # 4. Mix Narration + Optional Japanese Ambient BGM and mux with Video
        if include_bgm:
            bgm_wav = tdir / "bgm_30s.wav"
            generate_japanese_ambient_bgm(bgm_wav, duration=30.0)
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(v_joined),
                    "-i", str(narration_wav),
                    "-i", str(bgm_wav),
                    "-filter_complex", "[1:a]volume=1.35[na];[2:a]volume=0.26[bg];[na][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "30.0",
                    "-movflags", "+faststart",
                    str(out_mp4)
                ],
                check=True
            )
        else:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(v_joined),
                    "-i", str(narration_wav),
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "30.0",
                    "-movflags", "+faststart",
                    str(out_mp4)
                ],
                check=True
            )

    size_mb = out_mp4.stat().st_size / (1024 * 1024)
    print(f"  [OK] Rendered {out_mp4.name} ({size_mb:.2f} MB, 1080x1920, 30.0s)")
    return out_mp4


def main():
    parser = argparse.ArgumentParser(description="Render Fine Atlas 30s vertical short videos directly from Google Drive assets.")
    parser.add_argument("--day", type=int, default=1, help="Episode Day number (1..28)")
    parser.add_argument("--lang", choices=["jp", "en", "both"], default="both", help="Language to render")
    parser.add_argument("--include-nobgm", action="store_true", help="Also output no-BGM versions")
    args = parser.parse_args()

    data = load_data_js()
    ep_id = f"DAY-{args.day:02d}"
    ep = next((e for e in data["episodes"] if e["id"] == ep_id), data["episodes"][0])

    print(f"=== Rendering {ep['id']} ({ep['featuredFish']}) : {ep['item1_title']['jp']} ===")
    langs = ["jp", "en"] if args.lang == "both" else [args.lang]
    outputs = []
    for lg in langs:
        outputs.append(render_episode(ep, lg, include_bgm=True))
        if args.include_nobgm:
            outputs.append(render_episode(ep, lg, include_bgm=False))

    # Also save a poster thumbnail from 1.5s of the JP video
    jp_video = VIDEOS_DIR / f"FA_{ep_id}_jp.mp4"
    poster_jpg = VIDEOS_DIR / f"FA_{ep_id}_poster.jpg"
    if jp_video.exists():
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "1.5", "-i", str(jp_video), "-frames:v", "1", "-q:v", "2", str(poster_jpg)],
            check=True
        )
        print(f"  [OK] Saved poster thumbnail: {poster_jpg.name}")


if __name__ == "__main__":
    main()
