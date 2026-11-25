#!/usr/bin/env python3
"""
FINE ATLAS — Antigravity Direct Short Video Renderer (`render_short_video.py` v2.0)
===================================================================================
Documentary-grade culinary short video engine ("Cambria Palace / NHK Professional" style)
designed to honor President Imada's 13-Chapter Plan:
  - 100% authentic Tsushima Suisan / Fine Atlas real photography & vertical video clips
    (zero artificial AI food morphing that would undermine professional chef trust)
  - Two-layer gallery composition: rock-steady Deep Ocean Navy & Antique Gold broadcast frame
    with silky sub-pixel bicubic camera motion ONLY inside the central culinary window
  - ~3.5–4.25s visual pacing on still photos: automatic "Establishing Wide -> Appetizing Detail
    Close-up" progression so no photo ever sits frozen for 8.5 seconds
  - Gentle 0.45s cosine cross-dissolves at every cut boundary (zero harsh slideshow cuts)
  - 1.35s delayed fade-in + subtle upward float of verified culinary data plaques
    (Usable Yield %, Dish Cost, FL Cost Ratio from `fishMaster10`)
  - Mandatory 27–30s official brand closing card:
      JP: 「日本の旬と品質を、一箱に。世界の厨房へ。」
      EN: "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."

Output spec (President's Plan Chapter 2 & 4):
  - Duration: 30.00 seconds exact (900 frames @ 30fps)
  - Aspect Ratio: Vertical 9:16 (1080x1920, H.264 MP4 + AAC 44.1kHz stereo)
"""

import argparse
import asyncio
import json
import math
import re
import struct
import subprocess
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

FPS = 30
TOTAL_DURATION = 30.0
TOTAL_FRAMES = int(round(TOTAL_DURATION * FPS))  # 900 frames exact
W_CANVAS, H_CANVAS = 1080, 1920
WIN_X, WIN_Y, WIN_W, WIN_H = 24, 372, 1032, 920
CROSSFADE_SEC = 0.45

WEEKDAY_EN_MAP = {
    "月曜日": "MON",
    "火曜日": "TUE",
    "水曜日": "WED",
    "木曜日": "THU",
    "金曜日": "FRI",
    "土曜日": "SAT",
    "日曜日": "SUN",
}

FISH_EN_MAP = {
    "のどぐろ": "Nodoguro (Blackthroat)",
    "甘鯛": "Red Amadai (Tilefish)",
    "煮穴子": "Tsushima Simmered Anago",
    "穴子フィレ": "Live-Struck Anago Fillet",
    "剣先イカ": "Kensaki Swordtip Squid",
    "トラフグ身欠き": "Licensed Torafugu",
    "本マグロ柵": "Bluefin Tuna Saku",
    "銀ダラ・サワラ": "Boneless Sablefish & Sawara",
    "ホタテ貝柱": "Hokkaido IQF Scallop",
    "車海老・天使の海老": "IQF Kuruma & Blue Prawn",
}

THEME_EN_MAP = {
    "今が旬の魚": "Seasonal Peak Catch",
    "高級魚の特徴": "Luxury Fish Craft",
    "市場での価格の動き": "Market Price Stability",
    "冷凍魚と生魚の違い": "Rapid-Frozen vs. Fresh",
    "急速冷凍の仕組み": "Rapid Freezing Science",
    "美味しく解凍する方法": "Chef's Optimal Thawing",
    "魚の歩留まりと原価計算": "Yield & Dish Cost Math",
    "飲食店の仕入れ改善": "Smart Kitchen Sourcing",
    "厨房の仕込み時間短縮": "Prep Time Reduction",
    "魚ごとの調理方法": "Master Culinary Technique",
    "寿司・刺身の知識": "Sushi & Sashimi Craft",
    "海外の日本食レストラン事情": "Global Washoku Kitchens",
    "海外で人気の日本の魚": "Top Japanese Fish Abroad",
    "珍しい魚の紹介": "Rare Regional Catch",
    "季節ごとの魚カレンダー": "Four-Season Calendar",
    "日本の漁港・産地の紹介": "Tsushima & Port Origins",
    "水産加工の現場": "Artisan Processing",
    "日本の魚文化": "Japanese Culinary Heritage",
    "ファインアトラスの取り組み・商品紹介": "Fine Atlas Quality Promise",
}

# Verified real Tsushima Suisan Google Drive assets with art-directed wide -> closeup focal choreography
# Motion tuple: (z0, z1, fx0, fy0, fx1, fy1)
FISH_GDRIVE_SCENES = {
    "のどぐろ": {
        "hook": [
            {
                "id": "1wrzyfcmnXPoGt0HK-xnb1BUKMbvNmg4m",
                "file": "nodoguro_aburi.jpg",
                "type": "image",
                "creditJp": "のどぐろ皮目炙り（自社実写）",
                "creditEn": "Torch-Seared Nodoguro (In-House)",
                "motion": (1.04, 1.18, 0.49, 0.47, 0.44, 0.41),
            }
        ],
        "body1": [
            {
                "id": "1Le_jV2wBEN0eDb2S42kDZ8XnlWU7RHnj",
                "file": "nodoguro_landing.jpg",
                "type": "image",
                "creditJp": "対馬・山陰産 水揚げのどぐろ（自社実写）",
                "creditEn": "Freshly Landed Nodoguro (In-House)",
                "motion": (1.06, 1.15, 0.42, 0.49, 0.56, 0.48),
            },
            {
                "id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe",
                "file": "toumin_machine.jpg",
                "type": "image",
                "creditJp": "液体急速冷凍「凍眠」凍結工程（自社実写）",
                "creditEn": "Toumin Liquid Rapid Freezer (In-House)",
                "motion": (1.18, 1.32, 0.48, 0.44, 0.45, 0.43),
            },
        ],
        "body2": [
            {
                "id": "14liGrV4JrkmuAXYboPdtNoFib9im_COE",
                "file": "nodoguro_course1.jpg",
                "type": "image",
                "creditJp": "のどぐろ会席コース盛り付け（全体）",
                "creditEn": "Nodoguro Kaiseki Course (Wide View)",
                "motion": (1.04, 1.13, 0.54, 0.48, 0.46, 0.49),
            },
            {
                "id": "14liGrV4JrkmuAXYboPdtNoFib9im_COE",
                "file": "nodoguro_course1.jpg",
                "type": "image",
                "creditJp": "のどぐろ炙り薄造り（断面クローズアップ）",
                "creditEn": "Seared Nodoguro Slices (Detail View)",
                "motion": (1.34, 1.46, 0.43, 0.55, 0.54, 0.56),
            },
        ],
        "climax": [
            {
                "id": "1fpyKM6SuPUtotPZtmlnFbj_ejDHjbQLc",
                "file": "nodoguro_sashimi.jpg",
                "type": "image",
                "creditJp": "のどぐろ姿造り・炙り刺し（全体）",
                "creditEn": "Nodoguro Sashimi Platter (Wide View)",
                "motion": (1.03, 1.12, 0.50, 0.53, 0.50, 0.46),
            },
            {
                "id": "1fpyKM6SuPUtotPZtmlnFbj_ejDHjbQLc",
                "file": "nodoguro_sashimi.jpg",
                "type": "image",
                "creditJp": "皮目の香ばしさと脂の照り（寄り）",
                "creditEn": "Golden Seared Skin & Rich Marbling",
                "motion": (1.35, 1.48, 0.52, 0.56, 0.62, 0.56),
            },
        ],
    },
    "甘鯛": {
        "hook": [
            {
                "id": "1VcdZFkmB7abt0kCI0fNi4duiOrh_YTE5",
                "file": "amadai_uroko.jpg",
                "type": "image",
                "creditJp": "赤甘鯛の鱗焼き・松笠仕立て（自社実写）",
                "creditEn": "Crispy Scale-On Red Amadai (In-House)",
                "motion": (1.05, 1.19, 0.50, 0.52, 0.50, 0.46),
            }
        ],
        "body1": [
            {
                "id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe",
                "file": "toumin_machine.jpg",
                "type": "image",
                "creditJp": "急速冷凍ライン全景（自社実写）",
                "creditEn": "Rapid Freezing Facility (Wide View)",
                "motion": (1.04, 1.13, 0.48, 0.46, 0.48, 0.42),
            },
            {
                "id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe",
                "file": "toumin_machine.jpg",
                "type": "image",
                "creditJp": "職人手作業による急速凍結セット（寄り）",
                "creditEn": "Craftsman Loading Rapid-Freeze Rack",
                "motion": (1.22, 1.35, 0.47, 0.44, 0.44, 0.43),
            },
        ],
        "body2": [
            {
                "id": "1nF52eOGaVlD5QxqycXsj7V7Mo2qx7jQZ",
                "file": "amadai_thaw_cook.mp4",
                "type": "video",
                "creditJp": "解凍甘鯛の調理工程（自社実写動画）",
                "creditEn": "Thawing & Cooking Amadai (Real Video)",
            }
        ],
        "climax": [
            {
                "id": "1VcdZFkmB7abt0kCI0fNi4duiOrh_YTE5",
                "file": "amadai_uroko.jpg",
                "type": "image",
                "creditJp": "甘鯛鱗焼き 完成一皿（全体）",
                "creditEn": "Crispy Matsukasa-Yaki Dish (Wide)",
                "motion": (1.03, 1.12, 0.50, 0.53, 0.50, 0.47),
            },
            {
                "id": "1VcdZFkmB7abt0kCI0fNi4duiOrh_YTE5",
                "file": "amadai_uroko.jpg",
                "type": "image",
                "creditJp": "花開く鱗の立体感（クローズアップ）",
                "creditEn": "Blooming Crispy Scales (Detail View)",
                "motion": (1.30, 1.44, 0.46, 0.48, 0.55, 0.48),
            },
        ],
    },
    "煮穴子": {
        "hook": [
            {
                "id": "1IIHi5-emj7Q0DZY3WNRFPFs3NndhRoVe",
                "file": "densuke_nianago_sushi.mp4",
                "type": "video",
                "creditJp": "対馬産 伝助煮穴子握り（自社実写動画）",
                "creditEn": "Tsushima Simmered Anago Sushi (Real Video)",
            }
        ],
        "body1": [
            {
                "id": "1w-XTD0ou6kLd6-JECMcW1rWdroC6nevp",
                "file": "anago_pack.jpg",
                "type": "image",
                "creditJp": "対馬産天然穴子 凍眠パック箱詰め（全体）",
                "creditEn": "Tsushima Wild Anago Boxed Packs (Wide)",
                "motion": (1.03, 1.12, 0.50, 0.55, 0.50, 0.46),
            },
            {
                "id": "1w-XTD0ou6kLd6-JECMcW1rWdroC6nevp",
                "file": "anago_pack.jpg",
                "type": "image",
                "creditJp": "無添加・凍眠急速冷凍パッケージ（寄り）",
                "creditEn": "Additive-Free Toumin Frozen Pack (Detail)",
                "motion": (1.28, 1.42, 0.46, 0.36, 0.54, 0.36),
            },
        ],
        "body2": [
            {
                "id": "1YvmW3-yBtELNXtJZz3y65dSC-mYrnbYs",
                "file": "anago_sashimi_insta.mp4",
                "type": "video",
                "creditJp": "対馬産 穴子フィレ切り付け（自社実写動画）",
                "creditEn": "Slicing Tsushima Anago Fillet (Real Video)",
            }
        ],
        "climax": [
            {
                "id": "1nVUkKKNDAhv7w1VAytXlp9Tk53VLFgPe",
                "file": "nianago_sushi.png",
                "type": "image",
                "creditJp": "煮穴子握り二貫・器盛り付け（全体）",
                "creditEn": "Simmered Anago Nigiri Duo (Wide View)",
                "motion": (1.03, 1.12, 0.50, 0.52, 0.50, 0.45),
            },
            {
                "id": "1nVUkKKNDAhv7w1VAytXlp9Tk53VLFgPe",
                "file": "nianago_sushi.png",
                "type": "image",
                "creditJp": "ふっくら炊き上げた身の照り（寄り）",
                "creditEn": "Rich Glaze & Tender Texture (Close-Up)",
                "motion": (1.32, 1.46, 0.40, 0.42, 0.58, 0.42),
            },
        ],
    },
    "穴子フィレ": {
        "hook": [
            {
                "id": "1YvmW3-yBtELNXtJZz3y65dSC-mYrnbYs",
                "file": "anago_sashimi_insta.mp4",
                "type": "video",
                "creditJp": "活〆穴子フィレ包丁入れ（自社実写動画）",
                "creditEn": "Live-Struck Anago Fillet Prep (Real Video)",
            }
        ],
        "body1": [
            {
                "id": "1w-XTD0ou6kLd6-JECMcW1rWdroC6nevp",
                "file": "anago_pack.jpg",
                "type": "image",
                "creditJp": "対馬産天然穴子 業務用梱包（全体）",
                "creditEn": "Tsushima Anago Commercial Pack (Wide)",
                "motion": (1.03, 1.12, 0.50, 0.54, 0.50, 0.46),
            },
            {
                "id": "1w-XTD0ou6kLd6-JECMcW1rWdroC6nevp",
                "file": "anago_pack.jpg",
                "type": "image",
                "creditJp": "高真空・凍眠凍結パック詳細（寄り）",
                "creditEn": "Vacuum Rapid-Frozen Label (Detail)",
                "motion": (1.28, 1.42, 0.45, 0.36, 0.55, 0.36),
            },
        ],
        "body2": [
            {
                "id": "1IIHi5-emj7Q0DZY3WNRFPFs3NndhRoVe",
                "file": "densuke_nianago_sushi.mp4",
                "type": "video",
                "creditJp": "伝助穴子の仕上げ工程（自社実写動画）",
                "creditEn": "Chef Finishing Densuke Anago (Real Video)",
            }
        ],
        "climax": [
            {
                "id": "1nVUkKKNDAhv7w1VAytXlp9Tk53VLFgPe",
                "file": "nianago_sushi.png",
                "type": "image",
                "creditJp": "完成した穴子握り一皿（全体）",
                "creditEn": "Finished Anago Dish (Wide View)",
                "motion": (1.03, 1.12, 0.50, 0.52, 0.50, 0.45),
            },
            {
                "id": "1nVUkKKNDAhv7w1VAytXlp9Tk53VLFgPe",
                "file": "nianago_sushi.png",
                "type": "image",
                "creditJp": "肉厚な身質と香ばしい照り（寄り）",
                "creditEn": "Plump Fillet & Savory Glaze (Detail)",
                "motion": (1.32, 1.46, 0.40, 0.42, 0.58, 0.42),
            },
        ],
    },
    "剣先イカ": {
        "hook": [
            {
                "id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM",
                "file": "kensaki_ika.jpg",
                "type": "image",
                "creditJp": "壱岐・対馬産 剣先イカ（自社実写）",
                "creditEn": "Tsushima Kensaki Swordtip Squid (In-House)",
                "motion": (1.04, 1.18, 0.50, 0.50, 0.50, 0.45),
            }
        ],
        "body1": [
            {
                "id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe",
                "file": "toumin_machine.jpg",
                "type": "image",
                "creditJp": "最大氷結晶生成帯を高速通過する凍眠設備",
                "creditEn": "Toumin Liquid Rapid-Freezing System",
                "motion": (1.04, 1.13, 0.48, 0.46, 0.48, 0.42),
            },
            {
                "id": "1vnoolDS9mw4rOz0KjyL87oW4AWEzZfXe",
                "file": "toumin_machine.jpg",
                "type": "image",
                "creditJp": "細胞を壊さない急速凍結手元（寄り）",
                "creditEn": "Cell-Preserving Rapid Freeze (Detail)",
                "motion": (1.22, 1.35, 0.47, 0.44, 0.44, 0.43),
            },
        ],
        "body2": [
            {
                "id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM",
                "file": "kensaki_ika.jpg",
                "type": "image",
                "creditJp": "下処理・皮むき済み剣先イカ全体",
                "creditEn": "Cleaned Kensaki Squid Sashimi Grade",
                "motion": (1.05, 1.14, 0.44, 0.50, 0.56, 0.50),
            },
            {
                "id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM",
                "file": "kensaki_ika.jpg",
                "type": "image",
                "creditJp": "透明感ある身質クローズアップ",
                "creditEn": "Translucent Sweet Flesh (Close-Up)",
                "motion": (1.28, 1.42, 0.52, 0.48, 0.46, 0.46),
            },
        ],
        "climax": [
            {
                "id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM",
                "file": "kensaki_ika.jpg",
                "type": "image",
                "creditJp": "剣先イカお造り・握り用柵（全体）",
                "creditEn": "Ready-to-Slice Sashimi Block (Wide)",
                "motion": (1.04, 1.12, 0.50, 0.52, 0.50, 0.46),
            },
            {
                "id": "1A_3TfZ1GZPDOQos8qmD9hxLjcPPGN6OM",
                "file": "kensaki_ika.jpg",
                "type": "image",
                "creditJp": "ねっとり濃厚な甘みと艶（寄り）",
                "creditEn": "Glossy Sashimi Finish (Detail)",
                "motion": (1.30, 1.44, 0.45, 0.47, 0.56, 0.47),
            },
        ],
    },
}


def load_data_js():
    text = DATA_JS_PATH.read_text(encoding="utf-8")
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


def ensure_gdrive_asset(asset_info: dict) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    local_path = RAW_DIR / asset_info["file"]
    if not local_path.exists() or local_path.stat().st_size == 0:
        label = asset_info.get("creditJp", asset_info["file"])
        print(f"  [gdrive] Downloading {label} ({asset_info['id']}) -> {local_path.name}")
        subprocess.run(
            ["gdrive", "readonly", "download", asset_info["id"], "--out", str(local_path)],
            check=True,
        )
    return local_path


_FONT_CACHE = {}


def get_font(path: str, size: int):
    key = (path, int(size))
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = ImageFont.truetype(path, int(size))
        except Exception:
            _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def fit_font_to_width(draw: ImageDraw.ImageDraw, text: str, font_path: str, start_size: int, min_size: int, max_width: int):
    for sz in range(start_size, min_size - 1, -1):
        f = get_font(font_path, sz)
        if draw.textlength(text, font=f) <= max_width:
            return f
    return get_font(font_path, min_size)


_JP_TOKEN_RE = re.compile(
    r"[「『（【][^」』）】]{1,12}[」』）】][、。！？・]?"
    r"|[¥￥]?\d[\d,\.〜~]*[%％円度℃分秒時間尾貫皿箱gkg]*[、。！？・]?"
    r"|[A-Za-z0-9_.\-+/%]+[、。！？・]?"
    r"|[\u4e00-\u9fff々ヶ]+[ぁ-ん]{0,2}[、。！？・]?"
    r"|[ァ-ヴー]+[、。！？・]?"
    r"|[ぁ-ん]+[、。！？・]?"
    r"|."
)


def wrap_text_lines(text: str, is_en: bool, max_chars_jp: int = 19, max_chars_en: int = 34, max_lines: int = 4):
    if is_en:
        return textwrap.wrap(text, width=max_chars_en)[:max_lines]

    tokens = _JP_TOKEN_RE.findall(text)
    lines = []
    buf = ""
    for tok in tokens:
        # Never start a new line with closing brackets or punctuation
        if buf and len(buf) + len(tok) > max_chars_jp and tok[0] not in "、。！？）」』）】・":
            lines.append(buf)
            buf = tok
        else:
            buf += tok
    if buf:
        if lines and len(buf) <= 3:
            lines[-1] += buf
        else:
            lines.append(buf)

    # Fallback split if a single huge token exceeded max_chars_jp + 4
    cleaned = []
    for ln in lines:
        while len(ln) > max_chars_jp + 4:
            cleaned.append(ln[:max_chars_jp])
            ln = ln[max_chars_jp:]
        cleaned.append(ln)
    return cleaned[:max_lines]


def draw_gold_diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 9, fill=(217, 119, 6, 255)):
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def draw_camera_emblem(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    # Clean vector camera icon (prevents missing emoji tofu boxes)
    draw.rounded_rectangle([cx - 14, cy - 9, cx + 14, cy + 10], radius=4, fill=(167, 243, 208, 255))
    draw.polygon([(cx - 6, cy - 9), (cx - 3, cy - 13), (cx + 3, cy - 13), (cx + 6, cy - 9)], fill=(167, 243, 208, 255))
    draw.ellipse([cx - 5, cy - 4, cx + 5, cy + 6], fill=(12, 34, 56, 255))


def build_blurred_backdrop(src_rgb: Image.Image) -> Image.Image:
    """
    Creates a stationary 1080x1920 blurred & darkened luxury navy backdrop from an image.
    """
    sw, sh = src_rgb.size
    scale_bg = max(W_CANVAS / sw, H_CANVAS / sh)
    bg_w, bg_h = int(sw * scale_bg), int(sh * scale_bg)
    bg = src_rgb.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    left = (bg_w - W_CANVAS) // 2
    top = (bg_h - H_CANVAS) // 2
    bg = bg.crop((left, top, left + W_CANVAS, top + H_CANVAS)).filter(ImageFilter.GaussianBlur(radius=34))
    navy = Image.new("RGB", (W_CANVAS, H_CANVAS), (10, 28, 46))
    return Image.blend(bg, navy, alpha=0.56)


def render_photo_window_frame(src_rgb: Image.Image, motion_spec: tuple, progress: float) -> Image.Image:
    """
    Sub-pixel bicubic Ken Burns camera work strictly inside the 1032x920 gallery window.
    Combines 35% linear drift + 65% cosine ease so movement is silky-smooth with zero integer stepping
    and never freezes abruptly during cross-dissolves.
    """
    z0, z1, fx0, fy0, fx1, fy1 = motion_spec
    p = max(0.0, min(1.0, progress))
    p_smooth = 0.35 * p + 0.65 * (0.5 - 0.5 * math.cos(math.pi * p))

    zoom = z0 + (z1 - z0) * p_smooth
    fx = fx0 + (fx1 - fx0) * p_smooth
    fy = fy0 + (fy1 - fy0) * p_smooth

    sw, sh = src_rgb.size
    base_scale = max(WIN_W / sw, WIN_H / sh)
    crop_w = min(float(sw), WIN_W / (base_scale * zoom))
    crop_h = min(float(sh), WIN_H / (base_scale * zoom))

    cx = max(crop_w * 0.5, min(sw - crop_w * 0.5, fx * sw))
    cy = max(crop_h * 0.5, min(sh - crop_h * 0.5, fy * sh))

    ext = (cx - crop_w * 0.5, cy - crop_h * 0.5, cx + crop_w * 0.5, cy + crop_h * 0.5)
    return src_rgb.transform((WIN_W, WIN_H), Image.Transform.EXTENT, ext, resample=Image.Resampling.BICUBIC)


def build_window_bottom_vignette() -> Image.Image:
    """
    Pre-builds a subtle bottom-edge gradient vignette for the 1032x920 window so delayed gold plaques
    remain effortlessly legible even over bright porcelain plates.
    """
    vig = Image.new("RGBA", (WIN_W, WIN_H), (0, 0, 0, 0))
    px = vig.load()
    start_y = WIN_H - 150
    for y in range(start_y, WIN_H):
        t = (y - start_y) / 150.0
        alpha = int(125 * (t ** 1.6))
        for x in range(WIN_W):
            px[x, y] = (8, 22, 38, alpha)
    return vig


def create_stationary_chrome_overlay(
    ep_id: str,
    weekday_str: str,
    fish_str: str,
    chapter_badge: str,
    top_title: str,
    spec_pill_text: str,
    asset_credit: str,
    is_en: bool,
) -> Image.Image:
    """
    Renders the stationary 1080x1920 broadcast chrome (top Deep Ocean Navy header, Serif headline,
    auto-fitted verified spec pill, Antique Gold gallery window frame, and bottom source credit strip).
    """
    img = Image.new("RGBA", (W_CANVAS, H_CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Top Broadcast Header (y=0..356)
    draw.rectangle([0, 0, W_CANVAS, 356], fill=(11, 31, 51, 240))
    draw.line([0, 353, W_CANVAS, 353], fill=(217, 119, 6, 255), width=4)
    draw.line([0, 357, W_CANVAS, 357], fill=(253, 224, 71, 130), width=1)

    # Top 3 pills (y=44..102)
    f_tag = get_font(FONT_SANS_BOLD, 26)
    draw.rounded_rectangle([40, 44, 332, 102], radius=14, fill=(194, 106, 12, 255))
    draw.text((186, 73), f"FINE ATLAS | {ep_id}", font=f_tag, fill=(255, 255, 255, 255), anchor="mm")

    mid_text = f"{weekday_str}｜{fish_str}" if not is_en else f"{weekday_str} | {fish_str}"
    f_mid = fit_font_to_width(draw, mid_text, FONT_SANS_BOLD, 26, 20, 396)
    draw.rounded_rectangle([348, 44, 772, 102], radius=14, fill=(20, 52, 84, 255), outline=(217, 119, 6, 220), width=2)
    draw.text((560, 73), mid_text, font=f_mid, fill=(253, 224, 71, 255), anchor="mm")

    f_chap = fit_font_to_width(draw, chapter_badge, FONT_SANS_BOLD, 25, 19, 232)
    draw.rounded_rectangle([788, 44, 1040, 102], radius=14, fill=(154, 52, 34, 255), outline=(245, 242, 235, 90), width=1)
    draw.text((914, 73), chapter_badge, font=f_chap, fill=(255, 255, 255, 255), anchor="mm")

    # Main Documentary Headline in Serif Bold (明朝体・2行均等バランス折り返し)
    max_single = 22 if not is_en else 38
    if len(top_title) <= max_single:
        title_lines = [top_title]
    elif is_en:
        words = top_title.split()
        best_i, best_diff = 1, 999
        for i in range(1, len(words)):
            l1, l2 = " ".join(words[:i]), " ".join(words[i:])
            diff = abs(len(l1) - len(l2))
            if diff < best_diff:
                best_i, best_diff = i, diff
        title_lines = [" ".join(words[:best_i]), " ".join(words[best_i:])]
    else:
        toks = _JP_TOKEN_RE.findall(top_title)
        best_i, best_diff = 1, 999
        for i in range(1, len(toks)):
            if toks[i][0] in "、。！？）」』）】・":
                continue
            l1, l2 = "".join(toks[:i]), "".join(toks[i:])
            diff = abs(len(l1) - len(l2))
            if diff < best_diff:
                best_i, best_diff = i, diff
        title_lines = ["".join(toks[:best_i]), "".join(toks[best_i:])]

    y_t = 158 if len(title_lines) > 1 else 188
    for tline in title_lines:
        f_title = fit_font_to_width(draw, tline, FONT_SERIF_BOLD if not is_en else FONT_SANS_BOLD, 41 if not is_en else 35, 25, 980)
        draw.text(
            (540, y_t),
            tline,
            font=f_title,
            fill=(255, 255, 255, 255),
            anchor="mm",
            stroke_width=2,
            stroke_fill=(6, 18, 32, 230),
        )
        y_t += 56

    # Verified Spec Pill inside Header (y=280..334) — guaranteed zero text overflow & zero broken emoji
    draw.rounded_rectangle([52, 280, W_CANVAS - 52, 334], radius=12, fill=(245, 242, 235, 244))
    draw_gold_diamond(draw, 84, 307, r=9, fill=(180, 83, 9, 255))
    f_spec = fit_font_to_width(draw, spec_pill_text, FONT_SANS_BOLD, 28, 19, W_CANVAS - 170)
    draw.text((552, 307), spec_pill_text, font=f_spec, fill=(12, 34, 56, 255), anchor="mm")

    # 2. Stationary Antique Gold Gallery Frame around Culinary Window (x=24..1056, y=372..1292)
    draw.rounded_rectangle(
        [WIN_X - 4, WIN_Y - 4, WIN_X + WIN_W + 4, WIN_Y + WIN_H + 4],
        radius=12,
        outline=(217, 119, 6, 235),
        width=4,
    )
    draw.rounded_rectangle(
        [WIN_X - 9, WIN_Y - 9, WIN_X + WIN_W + 9, WIN_Y + WIN_H + 9],
        radius=16,
        outline=(255, 255, 255, 48),
        width=1,
    )

    # 3. Bottom Authentic Source & Brand Strip (y=1624..1716)
    draw.rounded_rectangle([38, 1624, W_CANVAS - 38, 1716], radius=16, fill=(8, 22, 38, 208), outline=(217, 119, 6, 120), width=2)
    credit_prefix = "自社実写素材 : " if not is_en else "Authentic In-House Media : "
    full_credit = f"{credit_prefix}{asset_credit}"
    f_cred = fit_font_to_width(draw, full_credit, FONT_SANS_BOLD, 23, 18, W_CANVAS - 160)
    total_cred_w = draw.textlength(full_credit, font=f_cred)
    start_cx = int(540 - (total_cred_w + 38) / 2)
    draw_camera_emblem(draw, start_cx + 14, 1652)
    draw.text((start_cx + 38, 1652), full_credit, font=f_cred, fill=(167, 243, 208, 255), anchor="lm")

    footer_catch = f"「{CATCHPHRASE_JP}」" if not is_en else f'"{CATCHPHRASE_EN}"'
    f_foot = fit_font_to_width(draw, footer_catch, FONT_SERIF_BOLD if not is_en else FONT_SANS_BOLD, 23, 18, W_CANVAS - 110)
    draw.text((540, 1689), footer_catch, font=f_foot, fill=(245, 242, 235, 242), anchor="mm")

    return img


def create_subtitle_card_layer(subtitle_text: str, highlight_tokens: list, is_en: bool) -> Image.Image:
    """
    Renders the stationary lower Navy & Gold subtitle card (y=1320..1598) for 100% mute readability.
    """
    img = Image.new("RGBA", (W_CANVAS, H_CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    sub_lines = wrap_text_lines(subtitle_text, is_en, max_chars_jp=19, max_chars_en=35)
    box_h = max(172, 68 + len(sub_lines) * 60)
    box_bottom = 1598
    box_top = box_bottom - box_h

    draw.rounded_rectangle([38, box_top, W_CANVAS - 38, box_bottom], radius=22, fill=(11, 31, 51, 238), outline=(217, 119, 6, 255), width=3)
    draw.rounded_rectangle([38, box_top, 58, box_bottom], radius=10, fill=(217, 119, 6, 255))

    y_sub = box_top + 52
    for sline in sub_lines:
        is_hl = any(tok and tok in sline for tok in highlight_tokens)
        text_color = (253, 224, 71, 255) if is_hl else (255, 255, 255, 255)
        f_sub = fit_font_to_width(draw, sline, FONT_SANS_BOLD, 43 if not is_en else 36, 28, W_CANVAS - 135)
        draw.text(
            (548, y_sub),
            sline,
            font=f_sub,
            fill=text_color,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0, 235),
        )
        y_sub += 59

    return img


def create_delayed_plaque_badge(plaque_title: str, plaque_metric: str, is_en: bool) -> Image.Image:
    """
    Creates a compact, dignified Japanese lacquer/woodblock-inspired data plaque (紺×金縁の品質証札)
    that gently fades in 1.35s after a main scene starts, guiding the viewer's eye from food -> verified fact.
    """
    pw, ph = 650, 108
    badge = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    # Outer dark navy lacquer card + double gold border
    draw.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=16, fill=(10, 27, 45, 232), outline=(217, 119, 6, 255), width=3)
    draw.rounded_rectangle([7, 7, pw - 8, ph - 8], radius=11, outline=(253, 224, 71, 95), width=1)
    # Left gold seal accent strip
    draw.rounded_rectangle([0, 0, 16, ph - 1], radius=8, fill=(217, 119, 6, 255))

    draw_gold_diamond(draw, 38, 33, r=7, fill=(253, 224, 71, 255))
    f_top = fit_font_to_width(draw, plaque_title, FONT_SANS_BOLD, 23, 17, pw - 74)
    draw.text((54, 33), plaque_title, font=f_top, fill=(226, 232, 240, 255), anchor="lm")

    f_val = fit_font_to_width(draw, plaque_metric, FONT_SERIF_BOLD if not is_en else FONT_SANS_BOLD, 31, 21, pw - 56)
    draw.text((34, 74), plaque_metric, font=f_val, fill=(253, 224, 71, 255), anchor="lm")
    return badge


def create_closing_card_frame(backdrop_rgb: Image.Image, is_en: bool, progress: float) -> Image.Image:
    """
    Renders the mandatory 27–30s Official Brand Closing Card (Deep Ocean Navy & Gold, zero broken glyphs)
    with a subtle, stately breathing luminance on the ambient backdrop.
    """
    base = backdrop_rgb.copy()
    navy_overlay = Image.new("RGBA", (W_CANVAS, H_CANVAS), (11, 30, 50, int(238 - 8 * math.sin(math.pi * progress))))
    frame = Image.alpha_composite(base.convert("RGBA"), navy_overlay)
    draw = ImageDraw.Draw(frame)

    # Stately double gold border
    draw.rounded_rectangle([46, 78, W_CANVAS - 46, H_CANVAS - 78], radius=30, outline=(217, 119, 6, 255), width=5)
    draw.rounded_rectangle([62, 94, W_CANVAS - 62, H_CANVAS - 94], radius=22, outline=(245, 242, 235, 95), width=2)

    # Top emblem
    draw.rounded_rectangle([310, 204, 770, 280], radius=38, fill=(194, 106, 12, 255))
    draw.text((540, 242), "FINE ATLAS Co., Ltd.", font=get_font(FONT_SANS_BOLD, 33), fill=(255, 255, 255, 255), anchor="mm")

    company_str = "株式会社ファインアトラス" if not is_en else "FINE ATLAS — JAPANESE SEAFOOD"
    draw.text(
        (540, 348),
        company_str,
        font=get_font(FONT_SERIF_BOLD, 48 if not is_en else 36),
        fill=(245, 242, 235, 255),
        anchor="mm",
    )

    draw.line([180, 422, 900, 422], fill=(217, 119, 6, 210), width=3)

    # Core Brand Catchphrase Box (27-30s President's Plan exact copy)
    draw.rounded_rectangle([84, 478, W_CANVAS - 84, 832], radius=26, fill=(16, 45, 74, 255), outline=(217, 119, 6, 255), width=4)
    if not is_en:
        f_big = get_font(FONT_SERIF_BOLD, 54)
        draw.text((540, 585), "「日本の旬と品質を、一箱に。", font=f_big, fill=(255, 255, 255, 255), anchor="mm")
        draw.text((540, 682), "　世界の厨房へ。」", font=f_big, fill=(253, 224, 71, 255), anchor="mm")
        f_en_sub = fit_font_to_width(draw, CATCHPHRASE_EN, FONT_SANS_BOLD, 24, 18, W_CANVAS - 220)
        draw.text((540, 778), CATCHPHRASE_EN, font=f_en_sub, fill=(203, 213, 225, 255), anchor="mm")
    else:
        en_lines = textwrap.wrap(f'"{CATCHPHRASE_EN}"', width=28)
        f_big_en = get_font(FONT_SERIF_BOLD, 42)
        y_en = 562
        for line in en_lines:
            draw.text((540, y_en), line, font=f_big_en, fill=(253, 224, 71, 255), anchor="mm")
            y_en += 64
        draw.text((540, 778), f"（{CATCHPHRASE_JP}）", font=get_font(FONT_SERIF_BOLD, 27), fill=(245, 242, 235, 255), anchor="mm")

    # 4-Step Sales Funnel Box (Section 1 & 11 — clean vector diamonds, zero broken emojis)
    draw.rounded_rectangle([84, 896, W_CANVAS - 84, 1424], radius=24, fill=(245, 242, 235, 250))
    funnel_head = "ご注文・品質確認から法人契約まで" if not is_en else "From Small Trial Order to Custom B2B Box"
    f_fh = fit_font_to_width(draw, funnel_head, FONT_SERIF_BOLD if not is_en else FONT_SANS_BOLD, 35, 26, W_CANVAS - 260)
    draw_gold_diamond(draw, 148, 962, r=11, fill=(180, 83, 9, 255))
    draw_gold_diamond(draw, W_CANVAS - 148, 962, r=11, fill=(180, 83, 9, 255))
    draw.text((540, 962), funnel_head, font=f_fh, fill=(12, 34, 56, 255), anchor="mm")

    steps = (
        [
            "STEP 1｜ホームページ・Amazonへアクセス",
            "STEP 2｜まずは少量購入で品質・歩留まりを確認",
            "STEP 3｜リピート購入・定期仕入れで仕込み時短",
            "STEP 4｜法人契約・店舗別オリジナル魚BOX受注",
        ]
        if not is_en
        else [
            "STEP 1 | Visit fineatlas.co.jp or Amazon",
            "STEP 2 | Small trial order to verify yield & quality",
            "STEP 3 | Repeat orders for zero-waste kitchen prep",
            "STEP 4 | B2B Contract & Custom Restaurant Fish Box",
        ]
    )
    y_st = 1054
    for st in steps:
        draw.rounded_rectangle([126, y_st - 34, W_CANVAS - 126, y_st + 34], radius=14, fill=(12, 34, 56, 255))
        f_st = fit_font_to_width(draw, st, FONT_SANS_BOLD, 33 if not is_en else 29, 22, W_CANVAS - 310)
        draw.text((162, y_st), st, font=f_st, fill=(255, 255, 255, 255), anchor="lm")
        y_st += 88

    # Bottom URL CTA Banner
    draw.rounded_rectangle([124, 1490, W_CANVAS - 124, 1608], radius=28, fill=(168, 58, 36, 255), outline=(253, 224, 71, 180), width=2)
    cta_bottom = "fineatlas.co.jp ｜ Amazon「ファインアトラス」検索" if not is_en else "fineatlas.co.jp | Search 'FINE ATLAS' on Amazon"
    f_cta = fit_font_to_width(draw, cta_bottom, FONT_SANS_BOLD, 32, 23, W_CANVAS - 300)
    draw.text((540, 1549), cta_bottom, font=f_cta, fill=(255, 255, 255, 255), anchor="mm")

    return frame.convert("RGB")


def decode_video_window_frames(video_path: Path, num_frames: int) -> list:
    """
    Decodes a real vertical/horizontal video clip into `num_frames` PIL RGB images sized `1032x920` @ 30fps.
    """
    vf = f"scale={WIN_W}:{WIN_H}:force_original_aspect_ratio=increase,crop={WIN_W}:{WIN_H},fps={FPS}"
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-stream_loop",
        "-1",
        "-i",
        str(video_path),
        "-vf",
        vf,
        "-frames:v",
        str(num_frames),
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    frame_bytes = WIN_W * WIN_H * 3
    raw = res.stdout
    frames = []
    for i in range(num_frames):
        chunk = raw[i * frame_bytes : (i + 1) * frame_bytes]
        if len(chunk) < frame_bytes:
            frames.append(frames[-1] if frames else Image.new("RGB", (WIN_W, WIN_H), (12, 34, 56)))
        else:
            frames.append(Image.frombytes("RGB", (WIN_W, WIN_H), chunk))
    return frames


def generate_japanese_ambient_bgm(wav_path: Path, duration: float = 30.0, sample_rate: int = 44100):
    """
    Synthesizes a warm, copyright-free Japanese pentatonic (Miyako-bushi / Yo blend) koto ambient track
    with subtle, dignified harmonic fifth chords aligned to the documentary section transitions
    (0.0s, 3.0s, 11.5s, 20.0s, 27.0s) — zero cheap pop sound effects.
    """
    total_samples = int(duration * sample_rate)
    notes = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46, 880.00]
    pattern = [0, 2, 3, 4, 3, 2, 1, 0, 2, 4, 5, 4, 3, 2, 0, 3]
    note_interval = 0.75

    buf = [0.0] * total_samples

    # Warm sub-pad drone (D3 + A3)
    for i in range(total_samples):
        t = i / sample_rate
        env = min(1.0, t / 1.4) * min(1.0, (duration - t) / 1.8)
        drone = 0.11 * math.sin(2 * math.pi * 146.83 * t) + 0.075 * math.sin(2 * math.pi * 220.0 * t)
        buf[i] += drone * env

    # Plucked koto melody notes
    num_notes = int(duration / note_interval)
    for n_idx in range(num_notes):
        start_t = n_idx * note_interval
        freq = notes[pattern[n_idx % len(pattern)]]
        start_sample = int(start_t * sample_rate)
        decay_len = int(2.2 * sample_rate)
        for j in range(min(decay_len, total_samples - start_sample)):
            dt = j / sample_rate
            pluck_env = min(1.0, dt / 0.014) * math.exp(-2.35 * dt)
            sig = (
                0.20 * math.sin(2 * math.pi * freq * dt)
                + 0.08 * math.sin(2 * math.pi * (freq * 2.0) * dt) * math.exp(-4.0 * dt)
                + 0.035 * math.sin(2 * math.pi * (freq * 3.0) * dt) * math.exp(-6.0 * dt)
            )
            buf[start_sample + j] += sig * pluck_env

    # Subtle harmonic koto chord accents at major narrative transitions
    chord_times = [0.04, 3.00, 11.50, 20.00, 27.00]
    chord_freqs = (293.66, 440.00, 587.33)  # D4 + A4 + D5 open fifth chord
    for ct in chord_times:
        s_idx = int(ct * sample_rate)
        c_len = int(2.6 * sample_rate)
        for j in range(min(c_len, total_samples - s_idx)):
            dt = j / sample_rate
            c_env = min(1.0, dt / 0.035) * math.exp(-1.75 * dt)
            chord_sig = (
                0.09 * math.sin(2 * math.pi * chord_freqs[0] * dt)
                + 0.07 * math.sin(2 * math.pi * chord_freqs[1] * dt)
                + 0.05 * math.sin(2 * math.pi * chord_freqs[2] * dt)
            )
            buf[s_idx + j] += chord_sig * c_env

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
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(res.stdout.strip() or "0.0")


def fit_narration_to_slot(src_mp3: Path, slot_sec: float, out_wav: Path):
    dur = get_audio_duration(src_mp3)
    max_speech = max(1.0, slot_sec - 0.15)
    atempo_filter = "anull"
    if dur > max_speech:
        ratio = min(1.45, dur / max_speech)
        atempo_filter = f"atempo={ratio:.3f}"

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src_mp3),
        "-af",
        f"{atempo_filter},apad=whole_dur={slot_sec:.3f}",
        "-t",
        f"{slot_sec:.3f}",
        "-ar",
        "44100",
        "-ac",
        "2",
        str(out_wav),
    ]
    subprocess.run(cmd, check=True)


def lookup_fish_master(data: dict, fish_key: str) -> dict:
    for item in data.get("fishMaster10", []):
        if item.get("key") == fish_key or fish_key in item.get("nameJp", ""):
            return item
    return {
        "key": fish_key,
        "yieldPct": 90,
        "portionGram": 60,
        "dishCostYen": 458,
        "menuPriceYen": 1620,
        "flCostRatioPct": 28.1,
    }


def prepare_shot_resource(shot_def: dict, pad_frames: int) -> dict:
    """
    Loads & prepares a single visual sub-shot (either sub-pixel photo camera rig or decoded real video clip).
    """
    local_path = ensure_gdrive_asset(shot_def)
    mtype = shot_def["type"]
    if mtype == "image":
        src_rgb = Image.open(local_path).convert("RGB")
        backdrop = build_blurred_backdrop(src_rgb)
        return {
            "type": "image",
            "src_rgb": src_rgb,
            "backdrop": backdrop,
            "motion": shot_def.get("motion", (1.04, 1.16, 0.50, 0.50, 0.50, 0.46)),
            "creditJp": shot_def["creditJp"],
            "creditEn": shot_def["creditEn"],
        }
    else:
        v_frames = decode_video_window_frames(local_path, pad_frames)
        backdrop = build_blurred_backdrop(v_frames[min(10, len(v_frames) - 1)])
        return {
            "type": "video",
            "v_frames": v_frames,
            "backdrop": backdrop,
            "creditJp": shot_def["creditJp"],
            "creditEn": shot_def["creditEn"],
        }


def get_shot_window_and_backdrop(shot_res: dict, local_t: float, total_shot_dur: float):
    if shot_res["type"] == "image":
        prog = local_t / max(0.001, total_shot_dur)
        win = render_photo_window_frame(shot_res["src_rgb"], shot_res["motion"], prog)
        return win, shot_res["backdrop"]
    else:
        idx = max(0, min(len(shot_res["v_frames"]) - 1, int(round(local_t * FPS))))
        return shot_res["v_frames"][idx], shot_res["backdrop"]


def render_episode_pair(data: dict, ep: dict, lang: str, include_nobgm: bool = True) -> list:
    """
    Renders the complete 30.00s (900 frames @ 30fps) documentary-grade MP4 for `(ep, lang)`,
    outputting the BGM version and optionally the No-BGM version in a single video encode pass.
    """
    is_en = lang == "en"
    ep_id = ep["id"]
    fish_key = ep.get("featuredFish", "のどぐろ")
    fish_info = lookup_fish_master(data, fish_key)
    scenes_cfg = FISH_GDRIVE_SCENES.get(fish_key, FISH_GDRIVE_SCENES["のどぐろ"])

    yield_pct = fish_info["yieldPct"]
    dish_cost = fish_info["dishCostYen"]
    fl_pct = fish_info["flCostRatioPct"]
    portion_g = fish_info["portionGram"]

    tc = ep["item3_timecode"]
    top_title = ep["item1_title"]["en" if is_en else "jp"]
    weekday_jp = ep.get("dayOfWeek", "月曜日")
    weekday_disp = WEEKDAY_EN_MAP.get(weekday_jp, "MON") if is_en else weekday_jp
    fish_disp = FISH_EN_MAP.get(fish_key, fish_key) if is_en else fish_key

    theme_jp = ep.get("themeCategory", "今が旬の魚")
    theme_disp = THEME_EN_MAP.get(theme_jp, theme_jp) if is_en else theme_jp

    spec_pill_text = (
        f"{theme_disp}｜可食歩留まり{yield_pct}%・1皿原価¥{dish_cost}（原価率{fl_pct}%）"
        if not is_en
        else f"{theme_disp} | {yield_pct}% Usable Yield · ¥{dish_cost}/Dish ({fl_pct}% Cost)"
    )

    # Split 3-20s narration cleanly into two sentences for visual pacing (3.0-11.5s and 11.5-20.0s)
    audio_0_3 = tc[0]["audioEn" if is_en else "audioJp"]
    audio_3_20_full = tc[1]["audioEn" if is_en else "audioJp"]
    audio_20_27 = tc[2]["audioEn" if is_en else "audioJp"]
    audio_27_30 = tc[3]["audioEn" if is_en else "audioJp"]

    if not is_en and "。" in audio_3_20_full:
        parts = [p.strip() + "。" for p in audio_3_20_full.split("。") if p.strip()]
        sub_3_11 = parts[0]
        sub_11_20 = "".join(parts[1:]) if len(parts) > 1 else parts[0]
    elif is_en and ". " in audio_3_20_full:
        parts = [p.strip() for p in audio_3_20_full.split(". ") if p.strip()]
        sub_3_11 = parts[0] + ("" if parts[0].endswith(".") else ".")
        rest = ". ".join(parts[1:]) if len(parts) > 1 else parts[0]
        sub_11_20 = rest
    elif is_en and ", achieving" in audio_3_20_full:
        idx = audio_3_20_full.find(", achieving")
        sub_3_11 = audio_3_20_full[:idx] + "."
        sub_11_20 = "Achieving" + audio_3_20_full[idx + 11 :]
    else:
        mid = len(audio_3_20_full) // 2
        sub_3_11 = audio_3_20_full[:mid]
        sub_11_20 = audio_3_20_full[mid:]

    # Build continuous shot timeline across 0.0 -> 27.0s (plus 27.0 -> 30.0s Closing Card)
    # Long photo slots (8.5s / 7.0s) automatically expand into 2 sub-shots (Wide -> Close-up)!
    section_defs = [
        {
            "t0": 0.0,
            "t1": 3.0,
            "chapter": "導入｜目利き" if not is_en else "INTRO | HOOK",
            "subtitle": audio_0_3,
            "shots": scenes_cfg["hook"],
            "plaque": None,
        },
        {
            "t0": 3.0,
            "t1": 11.5,
            "chapter": "解説①｜産地と鮮度" if not is_en else "PART 1 | QUALITY",
            "subtitle": sub_3_11,
            "shots": scenes_cfg["body1"],
            "plaque": (
                ("急速冷凍・鮮度封印の証", "氷結晶を抑えドリップロス極小化")
                if not is_en
                else ("RAPID-FROZEN PEAK QUALITY", "Cell-Intact Freezing · Minimal Drip Loss")
            ),
        },
        {
            "t0": 11.5,
            "t1": 20.0,
            "chapter": "解説②｜歩留まり実証" if not is_en else "PART 2 | YIELD",
            "subtitle": sub_11_20,
            "shots": scenes_cfg["body2"],
            "plaque": (
                (f"プロ厨房の実証データ（1人前 {portion_g}g）", f"可食歩留まり {yield_pct}% ／ 原価率 {fl_pct}%")
                if not is_en
                else (f"VERIFIED KITCHEN METRICS ({portion_g}g Portion)", f"{yield_pct}% Usable Yield · {fl_pct}% Food Cost")
            ),
        },
        {
            "t0": 20.0,
            "t1": 27.0,
            "chapter": "一皿｜プロの仕上がり" if not is_en else "CLIMAX | DISH",
            "subtitle": audio_20_27,
            "shots": scenes_cfg["climax"],
            "plaque": (
                ("仕込み時短・廃棄ロスゼロ", f"1皿原価 ¥{dish_cost} で看板メニューへ")
                if not is_en
                else ("ZERO WASTE · FAST PREP", f"Signature Dish at ¥{dish_cost} Portion Cost")
            ),
        },
    ]

    # Expand sections into concrete timed sub-shots with preloaded resources
    timeline_shots = []
    hl_numbers = re.findall(r"\d+(?:\.\d+)?%?", f"{audio_0_3} {audio_3_20_full} {audio_20_27}")
    highlight_tokens = list(set(hl_numbers + ["一箱", "one box", "旬", "対馬", "Tsushima"]))

    for sec in section_defs:
        n_sub = len(sec["shots"])
        sub_dur = (sec["t1"] - sec["t0"]) / n_sub
        sub_card = create_subtitle_card_layer(sec["subtitle"], highlight_tokens, is_en)
        plaque_img = (
            create_delayed_plaque_badge(sec["plaque"][0], sec["plaque"][1], is_en) if sec["plaque"] else None
        )

        for idx, sdef in enumerate(sec["shots"]):
            st0 = sec["t0"] + idx * sub_dur
            st1 = sec["t0"] + (idx + 1) * sub_dur
            pad_frames = int(math.ceil((sub_dur + 1.0) * FPS))
            sres = prepare_shot_resource(sdef, pad_frames)
            credit_txt = sres["creditEn"] if is_en else sres["creditJp"]
            chrome_ov = create_stationary_chrome_overlay(
                ep_id=ep_id,
                weekday_str=weekday_disp,
                fish_str=fish_disp,
                chapter_badge=sec["chapter"],
                top_title=top_title,
                spec_pill_text=spec_pill_text,
                asset_credit=credit_txt,
                is_en=is_en,
            )
            static_rgba = Image.alpha_composite(sres["backdrop"].convert("RGBA"), chrome_ov)
            static_rgba = Image.alpha_composite(static_rgba, sub_card)
            timeline_shots.append(
                {
                    "t0": st0,
                    "t1": st1,
                    "sec_t0": sec["t0"],
                    "sec_t1": sec["t1"],
                    "res": sres,
                    "chrome": chrome_ov,
                    "sub_card": sub_card,
                    "static_base_rgb": static_rgba.convert("RGB"),
                    "plaque": plaque_img,
                }
            )

    win_vignette_strip = build_window_bottom_vignette().crop((0, WIN_H - 150, WIN_W, WIN_H))
    closing_backdrop = timeline_shots[-1]["res"]["backdrop"]

    def apply_window_vignette(win_rgb: Image.Image) -> Image.Image:
        out = win_rgb.copy()
        btm = Image.alpha_composite(out.crop((0, WIN_H - 150, WIN_W, WIN_H)).convert("RGBA"), win_vignette_strip).convert("RGB")
        out.paste(btm, (0, WIN_H - 150))
        return out

    def paste_delayed_plaque(canvas_rgb: Image.Image, sh_curr: dict, t_clamped: float):
        plaque = sh_curr["plaque"]
        if plaque is None:
            return
        sec_elapsed = t_clamped - sh_curr["sec_t0"]
        sec_remain = sh_curr["sec_t1"] - t_clamped
        if sec_elapsed >= 1.30 and sec_remain > 0.15:
            fade_in = min(1.0, (sec_elapsed - 1.30) / 0.50)
            fade_out = min(1.0, (sec_remain - 0.15) / 0.35)
            p_alpha = (0.5 - 0.5 * math.cos(math.pi * fade_in)) * min(1.0, fade_out)
            float_dy = int(round((1.0 - (0.5 - 0.5 * math.cos(math.pi * fade_in))) * 10))
            if p_alpha > 0.02:
                px_x = WIN_X + WIN_W - plaque.width - 18
                px_y = WIN_Y + WIN_H - plaque.height - 16 + float_dy
                if p_alpha >= 0.995:
                    canvas_rgb.paste(plaque.convert("RGB"), (px_x, px_y), plaque.split()[3])
                else:
                    mask = plaque.split()[3].point(lambda v: int(v * p_alpha))
                    canvas_rgb.paste(plaque.convert("RGB"), (px_x, px_y), mask)

    def render_story_composite_at(t_sec: float) -> Image.Image:
        """
        Renders the 0..27s story composite at timestamp `t_sec` with 0.45s cosine cross-dissolves
        between adjacent sub-shots, stationary outer chrome, and 1.35s delayed data plaque fade-in.
        """
        t_clamped = max(0.0, min(26.999, t_sec))
        active_idx = len(timeline_shots) - 1
        for i, sh in enumerate(timeline_shots):
            if sh["t0"] <= t_clamped < sh["t1"]:
                active_idx = i
                break

        sh_curr = timeline_shots[active_idx]
        half_cf = CROSSFADE_SEC * 0.5

        blend_pair = None
        if active_idx > 0 and (t_clamped - sh_curr["t0"]) < half_cf:
            sh_prev = timeline_shots[active_idx - 1]
            u = (t_clamped - (sh_curr["t0"] - half_cf)) / CROSSFADE_SEC
            blend_pair = (sh_prev, sh_curr, u)
        elif active_idx < len(timeline_shots) - 1 and (sh_curr["t1"] - t_clamped) < half_cf:
            sh_next = timeline_shots[active_idx + 1]
            u = (t_clamped - (sh_curr["t1"] - half_cf)) / CROSSFADE_SEC
            blend_pair = (sh_curr, sh_next, u)

        if blend_pair is not None:
            sh_a, sh_b, u_raw = blend_pair
            alpha = 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, u_raw)))
            win_a, _ = get_shot_window_and_backdrop(sh_a["res"], t_clamped - sh_a["t0"], sh_a["t1"] - sh_a["t0"])
            win_b, _ = get_shot_window_and_backdrop(sh_b["res"], t_clamped - sh_b["t0"], sh_b["t1"] - sh_b["t0"])
            win_img = apply_window_vignette(Image.blend(win_a, win_b, alpha))
            canvas_rgb = Image.blend(sh_a["static_base_rgb"], sh_b["static_base_rgb"], alpha)
            canvas_rgb.paste(win_img, (WIN_X, WIN_Y))
            paste_delayed_plaque(canvas_rgb, sh_curr, t_clamped)
            return canvas_rgb
        else:
            win_img, _ = get_shot_window_and_backdrop(
                sh_curr["res"], t_clamped - sh_curr["t0"], sh_curr["t1"] - sh_curr["t0"]
            )
            win_img = apply_window_vignette(win_img)
            canvas_rgb = sh_curr["static_base_rgb"].copy()
            canvas_rgb.paste(win_img, (WIN_X, WIN_Y))
            paste_delayed_plaque(canvas_rgb, sh_curr, t_clamped)
            return canvas_rgb

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    out_with_bgm = VIDEOS_DIR / f"FA_{ep_id}_{lang}.mp4"
    out_nobgm = VIDEOS_DIR / f"FA_{ep_id}_{lang}_nobgm.mp4"

    with tempfile.TemporaryDirectory(prefix=f"fa_v2_{ep_id}_{lang}_") as tmp:
        tdir = Path(tmp)
        v_silent = tdir / "video_30s.mp4"

        # 1. Stream all 900 RGB frames (30.00s @ 30fps) directly into H.264 encoder
        ff_cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{W_CANVAS}x{H_CANVAS}",
            "-r",
            str(FPS),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            str(v_silent),
        ]
        proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)
        try:
            for f_idx in range(TOTAL_FRAMES):
                t = f_idx / float(FPS)
                # 26.75s -> 27.25s: smooth 0.50s cosine cross-dissolve into Official Closing Card
                if t < 26.75:
                    rgb_frame = render_story_composite_at(t)
                elif t < 27.25:
                    u_close = (t - 26.75) / 0.50
                    a_close = 0.5 - 0.5 * math.cos(math.pi * u_close)
                    story_f = render_story_composite_at(26.75)
                    close_f = create_closing_card_frame(closing_backdrop, is_en, (t - 26.75) / 3.25)
                    rgb_frame = Image.blend(story_f, close_f, a_close)
                else:
                    rgb_frame = create_closing_card_frame(closing_backdrop, is_en, (t - 27.0) / 3.0)
                proc.stdin.write(rgb_frame.tobytes())
        finally:
            proc.stdin.close()
            ret = proc.wait()
            if ret != 0:
                raise RuntimeError(f"FFmpeg video encode exited with code {ret}")

        # 2. Synthesize 4 AI Narration slots (0-3s = 3.0s, 3-20s = 17.0s, 20-27s = 7.0s, 27-30s = 3.0s)
        voice = "en-US-AndrewNeural" if is_en else "ja-JP-KeitaNeural"
        rate = "+6%" if is_en else "+10%"

        mp3_1, mp3_2, mp3_3, mp3_4 = tdir / "tts1.mp3", tdir / "tts2.mp3", tdir / "tts3.mp3", tdir / "tts4.mp3"

        async def run_all_tts():
            await asyncio.gather(
                synthesize_tts_clip(audio_0_3, voice, rate, mp3_1),
                synthesize_tts_clip(audio_3_20_full, voice, rate, mp3_2),
                synthesize_tts_clip(audio_20_27, voice, rate, mp3_3),
                synthesize_tts_clip(audio_27_30, voice, "+4%", mp3_4),
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
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_a),
                "-c",
                "copy",
                str(narration_wav),
            ],
            check=True,
        )

        # 3. Mux Narration + Japanese Koto Ambient BGM
        bgm_wav = tdir / "bgm_30s.wav"
        generate_japanese_ambient_bgm(bgm_wav, duration=30.0)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(v_silent),
                "-i",
                str(narration_wav),
                "-i",
                str(bgm_wav),
                "-filter_complex",
                "[1:a]volume=1.35[na];[2:a]volume=0.25[bg];[na][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
                "-map",
                "0:v",
                "-map",
                "[a]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-t",
                "30.0",
                "-movflags",
                "+faststart",
                str(out_with_bgm),
            ],
            check=True,
        )

        rendered = [out_with_bgm]
        size_mb = out_with_bgm.stat().st_size / (1024 * 1024)
        print(f"  [OK] Rendered {out_with_bgm.name} ({size_mb:.2f} MB, 1080x1920, 30.0s)")

        if include_nobgm:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(v_silent),
                    "-i",
                    str(narration_wav),
                    "-map",
                    "0:v",
                    "-map",
                    "1:a",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-t",
                    "30.0",
                    "-movflags",
                    "+faststart",
                    str(out_nobgm),
                ],
                check=True,
            )
            rendered.append(out_nobgm)
            nb_mb = out_nobgm.stat().st_size / (1024 * 1024)
            print(f"  [OK] Rendered {out_nobgm.name} ({nb_mb:.2f} MB, 1080x1920, 30.0s)")

    return rendered


def main():
    parser = argparse.ArgumentParser(
        description="Render Fine Atlas 30s documentary-style vertical short videos from authentic Google Drive assets."
    )
    parser.add_argument("--day", type=int, default=1, help="Episode Day number (1..28)")
    parser.add_argument("--lang", choices=["jp", "en", "both"], default="both", help="Language to render")
    parser.add_argument("--include-nobgm", action="store_true", help="Also output no-BGM versions")
    args = parser.parse_args()

    data = load_data_js()
    ep_id = f"DAY-{args.day:02d}"
    ep = next((e for e in data["episodes"] if e["id"] == ep_id), data["episodes"][0])

    print(f"=== Rendering {ep['id']} ({ep['featuredFish']}) : {ep['item1_title']['jp']} ===")
    langs = ["jp", "en"] if args.lang == "both" else [args.lang]
    for lg in langs:
        render_episode_pair(data, ep, lg, include_nobgm=args.include_nobgm)

    # Save crisp poster thumbnail from 1.6s of the JP video
    jp_video = VIDEOS_DIR / f"FA_{ep_id}_jp.mp4"
    poster_jpg = VIDEOS_DIR / f"FA_{ep_id}_poster.jpg"
    if jp_video.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                "1.6",
                "-i",
                str(jp_video),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(poster_jpg),
            ],
            check=True,
        )
        print(f"  [OK] Saved poster thumbnail: {poster_jpg.name}")


if __name__ == "__main__":
    main()
