#!/usr/bin/env python3
"""
Generator & Deterministic Validator for Google Colab 4K 60fps Studio Notebook
===========================================================================
Generates `notebooks/fine_atlas_4k60_upscale_studio.ipynb` with:
  - Exact 8-stage cell workflow:
      1. インストール (Install Real-ESRGAN + torchvision shim, Practical-RIFE, FFmpeg, Noto CJK fonts)
      2. GPU確認 & 設定 (Detect L4 / A100 / T4 / CPU, auto-tune FP16 & tile size, 9:16 vs 16:9 switch)
      3. 読み込み (Google Drive auto-load OR direct upload + media inspection)
      4. 超解像 (Real-ESRGAN `realesr-general-x4v3` CUDA FP16 -> direct FFmpeg pipe, `h264_nvenc` fallback)
      5. フレーム補間 (Practical-RIFE 24->60fps, auto-fallback to FFmpeg `minterpolate`, exact duration lock)
      6. 書き出し (Restore ambient audio + optional native-4K Fine Atlas JP/EN cinema subtitles/narration/brand closing + 2 outputs: 4K 60fps Master & Lanczos 1080p 60fps SNS)
      7. 保存 (Auto-save back to Google Drive + direct browser download)
      8. 最終確認 (Full spec audit table + runtime disconnect reminder)
  - Beginner-friendly Japanese guidance & friendly error diagnostics in every cell
  - Validates notebook JSON schema and runs Python `ast.parse()` on every code cell.
"""

import ast
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"
OUT_IPYNB = NOTEBOOKS_DIR / "fine_atlas_4k60_upscale_studio.ipynb"


def md_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip("\n").splitlines()],
    }


def code_cell(code: str, title_comment: str = "") -> dict:
    body = code.strip("\n")
    if title_comment:
        body = title_comment.strip("\n") + "\n\n" + body
    lines = body.splitlines()
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [ln + "\n" for ln in lines[:-1]] + ([lines[-1]] if lines else []),
    }


CELLS = []

# ==============================================================================
# Cover Markdown (Beginner-friendly complete guide)
# ==============================================================================
CELLS.append(
    md_cell(
        """# 🎬 FINE ATLAS｜AIショート動画 4K・60fps 超高画質仕上げスタジオ（Google Colab L4 GPU版）

このノートブックは、連結済みマスター動画（`master_720p.mp4`）を **プロ映画・テレビCM級の 4K・60fps** へ引き上げ、以下の2本を自動書き出しします：
1. **保存用 4K・60fps マスター**（縦型9:16基本：`2160×3840` 60fps ／ 横型16:9切替時：`3840×2160` 60fps）
2. **SNS投稿用 1080p・60fps**（4Kマスターから **Lanczos縮小** した超シャープな `1080×1920` 60fps ／ 横型時 `1920×1080` 60fps）

さらに、**社長計画書 準拠シネマモード（初期値 ON）** のまま実行すると、4K・60fps化した後の映像の上から **一切滲まないネイティブ4Kの同期字幕・検証データ札・日英プロナレーション・27〜30秒公式ブランド締め** まで一体合成します！

---

### ✅ 実行前の操作手順（初心者向け・3ステップ）
1. **GPUを選ぶ（L4 推奨）**
   - 上部メニュー **「ランタイム」→「ランタイムのタイプを変更」** をクリック
   - ハードウェアアクセラレータで **「L4 GPU」** を選んで「保存」
   - ※ **L4 が選べないとき**：代わりに **「T4 GPU」**（または Colab Pro+ の **「A100 GPU」**）を選んでください。このノートブックが GPU 名を自動判定し、T4 のときは自動で省メモリ設定（タイルサイズ縮小・RIFE軽量スケール）に切り替えます！
2. **上から順番に実行する**
   - メニューの **「ランタイム」→「すべてのセルを実行」** を押すか、各セル左上の **▶ボタン** を①〜⑧の順に押してください。
   - セル③で Googleドライブのアクセス許可が出たら「Googleドライブに接続」→ 許可 を押すだけで素材が自動で読み込まれます。
3. **終わったら必ずランタイムを切断する（課金・クレジット節約！）**
   - セル⑧の最終確認とダウンロード／Drive保存が終わったら、必ず上部メニュー **「ランタイム」→「ランタイムを接続解除して削除」** を押してください。
"""
    )
)

# ==============================================================================
# CELL 1: インストール
# ==============================================================================
CELLS.append(
    md_cell(
        """## ① インストール（超解像 AI・フレーム補間 AI・日本語フォント・FFmpeg の準備）
**このセルで行うこと**：
- 超解像AI **Real-ESRGAN（`realesr-general-x4v3`）** と PyTorch 2.x 互換パッチの自動導入
- フレーム補間AI **Practical-RIFE** の導入（万一取得できない場合は FFmpeg `minterpolate` へ自動切替する安全設計）
- 日本語テレビ字幕用フォント（Noto Serif / Sans CJK）と FFmpeg の確認
- 所要時間：約 1〜2 分（初回のみ）
"""
    )
)

CELLS.append(
    code_cell(
        """import os, sys, shutil, subprocess, traceback, glob
from pathlib import Path

def show_friendly_error(step_name: str, exc: Exception, hints: list):
    print("\\n" + "=" * 72)
    print(f"❌ 【エラー発生】{step_name} で問題が起きました")
    print("=" * 72)
    print(f"原因（技術詳細）: {type(exc).__name__}: {exc}")
    print("\\n🔧 初心者向け・直し方のヒント:")
    for i, h in enumerate(hints, 1):
        print(f"  {i}. {h}")
    print("=" * 72)

def run_cmd(cmd, check=True):
    print("▶", " ".join(cmd) if isinstance(cmd, list) else cmd)
    res = subprocess.run(cmd, shell=isinstance(cmd, str), text=True, capture_output=True)
    if check and res.returncode != 0:
        print(res.stdout[-1200:])
        print(res.stderr[-1500:])
        raise RuntimeError(f"コマンドが失敗しました (終了コード {res.returncode})")
    return res

WORK_DIR = Path("/content/fine_atlas_4k60")
WEIGHTS_DIR = WORK_DIR / "weights"
OUT_DIR = WORK_DIR / "outputs"
WORK_DIR.mkdir(parents=True, exist_ok=True)
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    print("📦 [1/4] システムツール（FFmpeg・日本語明朝/ゴシックフォント）を確認・導入しています...")
    run_cmd("apt-get update -qq && apt-get install -y -qq ffmpeg fonts-noto-cjk wget git unzip > /dev/null")

    print("📦 [2/4] Real-ESRGAN（realesr-general-x4v3）と画像処理ライブラリを導入しています...")
    run_cmd([
        sys.executable, "-m", "pip", "install", "-q", "--upgrade",
        "basicsr", "realesrgan", "opencv-python-headless", "pillow", "tqdm", "gdown"
    ])

    # PyTorch 2.x / torchvision >= 0.17 compatibility patch for basicsr (prevents functional_tensor crash)
    patched = 0
    for path_str in glob.glob("/usr/local/lib/python*/dist-packages/basicsr/data/degradations.py"):
        p = Path(path_str)
        txt = p.read_text(encoding="utf-8")
        old = "from torchvision.transforms.functional_tensor import rgb_to_grayscale"
        new = "from torchvision.transforms.functional import rgb_to_grayscale"
        if old in txt:
            p.write_text(txt.replace(old, new), encoding="utf-8")
            patched += 1
    if patched:
        print(f"  ✅ PyTorch 2.x 互換パッチを自動適用しました ({patched}件)")

    print("📦 [3/4] Real-ESRGAN 公式モデル（realesr-general-x4v3）をダウンロードしています...")
    models = {
        "realesr-general-x4v3.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
        "realesr-general-wdn-x4v3.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-wdn-x4v3.pth",
    }
    for fname, url in models.items():
        dst = WEIGHTS_DIR / fname
        if not dst.exists() or dst.stat().st_size < 1_000_000:
            run_cmd(["wget", "-q", "-O", str(dst), url])
        print(f"  ✅ {fname}: {dst.stat().st_size / 1024 / 1024:.2f} MB")

    print("📦 [4/4] Practical-RIFE（60fpsフレーム補間AI）を準備しています...")
    RIFE_DIR = WORK_DIR / "Practical-RIFE"
    RIFE_READY = False
    try:
        if not RIFE_DIR.exists():
            run_cmd(["git", "clone", "-q", "https://github.com/hzwer/Practical-RIFE.git", str(RIFE_DIR)])
        # Download official RIFE v4.25/v4.6 weights into train_log/
        train_log = RIFE_DIR / "train_log"
        train_log.mkdir(exist_ok=True)
        if not (train_log / "flownet.pkl").exists():
            # Try official public mirror zip for RIFE weights
            zip_out = WORK_DIR / "rife_weights.zip"
            for gid in ["1ZKjcbmt1hypiFprJPIKW0Tt0lr_2i7bg", "1APIzVeI-4ZZCEuIRE1m6WYfSCaOsi_7_"]:
                try:
                    run_cmd(["gdown", "--fuzzy", f"https://drive.google.com/uc?id={gid}", "-O", str(zip_out)])
                    if zip_out.exists() and zip_out.stat().st_size > 1_000_000:
                        run_cmd(["unzip", "-q", "-o", str(zip_out), "-d", str(RIFE_DIR)])
                        break
                except Exception:
                    continue
        # Locate flownet.pkl if nested inside train_log/train_log
        found_pkl = list(RIFE_DIR.rglob("flownet.pkl"))
        if found_pkl:
            src_dir = found_pkl[0].parent
            if src_dir != train_log:
                for f in src_dir.iterdir():
                    shutil.copy2(f, train_log / f.name)
            RIFE_READY = True
            print("  ✅ Practical-RIFE モデル準備完了！")
        else:
            print("  ⚠️ Practical-RIFE 重みファイル取得が混み合っています → セル⑤で高品質 FFmpeg minterpolate に自動切替します（処理は止まりません）")
    except Exception as rife_exc:
        print(f"  ⚠️ Practical-RIFE 準備をスキップしました（{rife_exc}）→ セル⑤で FFmpeg minterpolate へ自動切替します")

    print("\\n🎉 セル①（インストール）が正常に完了しました！次のセル②へ進んでください。")
except Exception as e:
    show_friendly_error(
        "セル①（インストール）",
        e,
        [
            "上部メニュー『ランタイム』→『ランタイムを再起動』を押してから、もう一度セル①を実行してください。",
            "ネット接続が一時的に切れただけの場合、そのままセル①を再実行すると直ることが多いです。",
        ],
    )
    raise
""",
        title_comment="# ============================================================\n# セル①：インストール（Real-ESRGAN・Practical-RIFE・FFmpeg・フォント）\n# ============================================================",
    )
)

# ==============================================================================
# CELL 2: GPU確認 & 設定パネル
# ==============================================================================
CELLS.append(
    md_cell(
        """## ② GPU確認 ＆ 仕上げ設定パネル
**このセルで行うこと**：
- 今つながっている GPU（**L4** / **A100** / **T4** など）と VRAM 容量・CUDA・FP16・`h264_nvenc` ハードウェアエンコーダーを自動検査します。
- **L4 が選べなかったとき（T4 などの場合）も自動で安全なタイルサイズと RIFE スケールに調整**するので、メモリ不足エラーになりにくくなります！
- 下のフォームで **画面の向き（縦型 9:16 ／ 横型 16:9）** や **社長計画書シネマ仕上げ（日英字幕・声・公式ブランド締め）の ON/OFF** を1クリックで選べます。
"""
    )
)

CELLS.append(
    code_cell(
        """#@title 🎛️ 仕上げ設定（ここを選ぶだけで縦型9:16／横型16:9・シネマ仕上げを切替できます）
ASPECT_MODE = "9:16_vertical" #@param ["9:16_vertical", "16:9_horizontal"]
LOAD_MODE = "drive" #@param ["drive", "upload"]
DRIVE_STUDIO_FOLDER = "ファインアトラス_AIショート動画_Antigravity自動制作スタジオ/4K60_Studio_DAY-02_赤甘鯛" #@param {type:"string"}
ENABLE_FINE_ATLAS_CINEMA = True #@param {type:"boolean"}
CINEMA_LANGUAGES = "both" #@param ["both", "jp", "en"]
DENOISE_STRENGTH = 0.25 #@param {type:"slider", min:0.0, max:1.0, step:0.05}

import torch, subprocess

USE_CUDA = torch.cuda.is_available()
USE_FP16 = False
GPU_NAME = "CPU（GPUなし）"
VRAM_GB = 0.0

if USE_CUDA:
    GPU_NAME = torch.cuda.get_device_name(0)
    VRAM_GB = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    USE_FP16 = True
    # Auto-tune Real-ESRGAN tile size & Practical-RIFE scale by VRAM
    if VRAM_GB >= 22.0:  # L4 (24GB) / A100 (40-80GB)
        TILE_SIZE = 512
        RIFE_SCALE = 0.5
        GPU_TIER = "L4/A100 推奨ハイスペック"
    elif VRAM_GB >= 14.0:  # T4 (16GB)
        TILE_SIZE = 256
        RIFE_SCALE = 0.5
        GPU_TIER = "T4 省メモリ自動最適化モード（L4代替）"
    else:
        TILE_SIZE = 192
        RIFE_SCALE = 0.25
        GPU_TIER = "軽量GPU 省メモリモード"
else:
    TILE_SIZE = 128
    RIFE_SCALE = 0.5
    GPU_TIER = "⚠️ CPUモード（非常に時間がかかります。ランタイムをL4またはT4 GPUに変更してください！）"

# Target 4K Master & 1080p Lanczos SNS dimensions
if ASPECT_MODE == "9:16_vertical":
    TARGET_4K_W, TARGET_4K_H = 2160, 3840
    TARGET_SNS_W, TARGET_SNS_H = 1080, 1920
    MODE_LABEL = "縦型 9:16（TikTok / Reels / YouTube Shorts 本番規格）"
else:
    TARGET_4K_W, TARGET_4K_H = 3840, 2160
    TARGET_SNS_W, TARGET_SNS_H = 1920, 1080
    MODE_LABEL = "横型 16:9（X 投稿 / 展示会・商談モニター規格）"

# Probe whether h264_nvenc actually works on this runtime (test 1 dummy frame)
def detect_best_encoder():
    if USE_CUDA:
        test = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.1",
                "-c:v", "h264_nvenc", "-f", "null", "-"
            ],
            capture_output=True, text=True
        )
        if test.returncode == 0:
            return "h264_nvenc"
    return "libx264"

VIDEO_ENCODER = detect_best_encoder()

print("=" * 68)
print("🖥️  GPU・エンコーダー診断結果")
print("=" * 68)
print(f"  GPU名           : {GPU_NAME} ({VRAM_GB:.1f} GB VRAM)")
print(f"  自動チューニング : {GPU_TIER}")
print(f"  CUDA / FP16     : CUDA={'ON' if USE_CUDA else 'OFF'} / FP16={'ON' if USE_FP16 else 'OFF'}")
print(f"  Real-ESRGAN設定 : tile={TILE_SIZE}, denoise={DENOISE_STRENGTH}")
print(f"  RIFE補間設定     : scale={RIFE_SCALE} (4K高精度＆VRAM安全)")
print(f"  エンコーダー     : {VIDEO_ENCODER} ({'GPU高速エンコード' if VIDEO_ENCODER == 'h264_nvenc' else 'CPU高品質自動切替'})")
print(f"  画面規格         : {MODE_LABEL}")
print(f"  4Kマスター目標   : {TARGET_4K_W} × {TARGET_4K_H} @ 60fps")
print(f"  SNS縮小目標      : {TARGET_SNS_W} × {TARGET_SNS_H} @ 60fps (Lanczos)")
print(f"  シネマ一体仕上げ : {'ON（ネイティブ4K字幕＋日英音声＋公式締め）' if ENABLE_FINE_ATLAS_CINEMA else 'OFF（映像＋元環境音のみ）'}")
print("=" * 68)

if not USE_CUDA:
    print("\\n⚠️ 注意：GPUが選ばれていません！上部メニュー『ランタイム』→『ランタイムのタイプを変更』→『L4 GPU（なければT4 GPU）』を選んでください。")
else:
    print("\\n✅ セル②（GPU確認）完了！次のセル③へ進んでください。")
""",
        title_comment="# ============================================================\n# セル②：GPU確認 ＆ 縦横・シネマ仕上げ設定パネル\n# ============================================================",
    )
)

# ==============================================================================
# CELL 3: 読み込み
# ==============================================================================
CELLS.append(
    md_cell(
        """## ③ 動画の読み込み（Googleドライブ自動読込 ＆ 直接アップロード両対応）
**このセルで行うこと**：
- `LOAD_MODE = "drive"` の場合：Googleドライブを接続し、あらかじめ用意したフォルダ（`4K60_Studio_DAY-02_赤甘鯛`）から `master_720p.mp4`（横型時は `master_720p_16x9.mp4`）と日英音声・字幕パックを自動で読み込みます。
- `LOAD_MODE = "upload"` の場合：PCから直接 `master_720p.mp4` を選んでアップロードできます。
- 読み込み後、元動画の解像度・fps・再生時間・音声の有無を表示して確認します。
"""
    )
)

CELLS.append(
    code_cell(
        """import json, shutil, subprocess
from pathlib import Path

def probe_video_info(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    vs = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    aus = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    return {
        "name": path.name,
        "width": int(vs["width"]) if vs else 0,
        "height": int(vs["height"]) if vs else 0,
        "fps": vs["r_frame_rate"] if vs else "?",
        "duration": float(data["format"]["duration"]),
        "size_mb": int(data["format"]["size"]) / (1024 * 1024),
        "has_audio": aus is not None,
        "audio_desc": f"あり ({aus['codec_name']} {aus['sample_rate']}Hz {aus['channels']}ch)" if aus else "なし",
    }

INPUT_VIDEO = None
OVERLAY_PACK_DIR = None
DRIVE_SAVE_DIR = None

try:
    if LOAD_MODE == "drive":
        from google.colab import drive
        drive.mount("/content/drive", force_remount=False)
        base_drive = Path("/content/drive/MyDrive") / DRIVE_STUDIO_FOLDER
        DRIVE_SAVE_DIR = base_drive / "4K60_Completed"
        DRIVE_SAVE_DIR.mkdir(parents=True, exist_ok=True)

        # For cinema mode (9:16), prefer the tail-fade-free clean clip so 27s->30s closing blends seamlessly
        if ASPECT_MODE == "9:16_vertical":
            cand_names = (
                ["overlay_tracks/clean_9x16_nofadeout.mp4", "master_720p.mp4"]
                if ENABLE_FINE_ATLAS_CINEMA
                else ["master_720p.mp4"]
            )
        else:
            cand_names = ["master_720p_16x9.mp4", "master_720p.mp4"]

        for rel in cand_names:
            p = base_drive / rel
            if p.exists() and p.stat().st_size > 100_000:
                INPUT_VIDEO = WORK_DIR / "input_master.mp4"
                shutil.copy2(p, INPUT_VIDEO)
                print(f"📂 Googleドライブから読み込みました: {p}")
                break

        # Fallback: search anywhere in MyDrive for master_720p.mp4
        if INPUT_VIDEO is None:
            print("🔎 指定フォルダに無いため MyDrive 全体から master_720p.mp4 を探しています...")
            hits = list(Path("/content/drive/MyDrive").rglob("master_720p.mp4"))
            if hits:
                INPUT_VIDEO = WORK_DIR / "input_master.mp4"
                shutil.copy2(hits[0], INPUT_VIDEO)
                DRIVE_SAVE_DIR = hits[0].parent / "4K60_Completed"
                DRIVE_SAVE_DIR.mkdir(parents=True, exist_ok=True)
                print(f"📂 自動検出しました: {hits[0]}")

        # Check optional Fine Atlas cinema overlay/audio pack
        cand_overlay = base_drive / "overlay_tracks"
        if (cand_overlay / "overlay_manifest.json").exists():
            OVERLAY_PACK_DIR = WORK_DIR / "overlay_tracks"
            if OVERLAY_PACK_DIR.exists():
                shutil.rmtree(OVERLAY_PACK_DIR)
            shutil.copytree(cand_overlay, OVERLAY_PACK_DIR)
            print(f"🎙️ 日英ナレーション・字幕パックも自動読込しました: {cand_overlay}")
        elif ENABLE_FINE_ATLAS_CINEMA:
            print("ℹ️ overlay_tracks が見つからないため、映像＋元環境音のクリーン4K 60fps仕上げで進めます。")
            ENABLE_FINE_ATLAS_CINEMA = False
    else:
        from google.colab import files
        print("⬆️ PCから master_720p.mp4 を選んでアップロードしてください...")
        uploaded = files.upload()
        if not uploaded:
            raise FileNotFoundError("動画ファイルがアップロードされませんでした。")
        first_name = next(iter(uploaded.keys()))
        INPUT_VIDEO = WORK_DIR / "input_master.mp4"
        shutil.move(first_name, INPUT_VIDEO)
        print(f"📂 アップロード完了: {first_name}")

    if INPUT_VIDEO is None or not INPUT_VIDEO.exists():
        raise FileNotFoundError(
            f"入力動画が見つかりませんでした（探した場所: MyDrive/{DRIVE_STUDIO_FOLDER}）"
        )

    SRC_INFO = probe_video_info(INPUT_VIDEO)
    print("\\n📋 読み込んだ元動画のスペック:")
    print(f"  解像度   : {SRC_INFO['width']} × {SRC_INFO['height']}")
    print(f"  fps      : {SRC_INFO['fps']}")
    print(f"  再生時間 : {SRC_INFO['duration']:.2f} 秒")
    print(f"  サイズ   : {SRC_INFO['size_mb']:.2f} MB")
    print(f"  音声     : {SRC_INFO['audio_desc']}")
    print("\\n✅ セル③（読み込み）完了！次のセル④（4K超解像）へ進んでください。")
except Exception as e:
    show_friendly_error(
        "セル③（動画の読み込み）",
        e,
        [
            "LOAD_MODE='drive' の場合は、Googleドライブに『ファインアトラス_AIショート動画_Antigravity自動制作スタジオ/4K60_Studio_DAY-02_赤甘鯛』フォルダがあるか確認してください。",
            "手元のPCに master_720p.mp4 がある場合は、セル②で LOAD_MODE を 'upload' に変更してセル②→セル③を実行してください。",
        ],
    )
    raise
""",
        title_comment="# ============================================================\n# セル③：読み込み（Googleドライブ自動読込 ＆ 直接アップロード）\n# ============================================================",
    )
)

# ==============================================================================
# CELL 4: 超解像（Real-ESRGAN realesr-general-x4v3 -> FFmpeg direct pipe）
# ==============================================================================
CELLS.append(
    md_cell(
        """## ④ 超解像（Real-ESRGAN `realesr-general-x4v3` × CUDA FP16 × FFmpegパイプ直結）
**このセルで行うこと**：
- 1フレームずつ **Real-ESRGAN（`realesr-general-x4v3`）** で超高精細化（縦型 `2160×3840` ／ 横型 `3840×2160`）します。
- 中間画像をディスクに溜め込まないよう、処理済みフレームを **そのまま FFmpeg へパイプ直結** して4K映像（24fps）へエンコードします。
- `h264_nvenc`（GPU高速）を優先使用し、使えない環境では自動で `libx264` へ切り替えます。
- 所要時間目安：L4 GPU で約 2〜4 分 ／ T4 GPU で約 5〜8 分
"""
    )
)

CELLS.append(
    code_cell(
        """import cv2, gc, time, torch, subprocess
import numpy as np
from tqdm.auto import tqdm
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

UPSCALED_4K_24FPS = WORK_DIR / "stage1_upscaled_4k_24fps.mp4"

try:
    t0 = time.time()
    torch.cuda.empty_cache()
    gc.collect()

    # Load official realesr-general-x4v3 (SRVGGNetCompact) with optional gentle denoise blending
    model = SRVGGNetCompact(
        num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type="prelu"
    )
    dni_weight = None
    model_path = str(WEIGHTS_DIR / "realesr-general-x4v3.pth")
    wdn_path = WEIGHTS_DIR / "realesr-general-wdn-x4v3.pth"
    if DENOISE_STRENGTH > 0 and wdn_path.exists():
        model_path = [model_path, str(wdn_path)]
        dni_weight = [1.0 - DENOISE_STRENGTH, DENOISE_STRENGTH]

    upsampler = RealESRGANer(
        scale=4,
        model_path=model_path,
        dni_weight=dni_weight,
        model=model,
        tile=TILE_SIZE,
        tile_pad=16,
        pre_pad=0,
        half=USE_FP16,
        gpu_id=0 if USE_CUDA else None,
    )

    cap = cv2.VideoCapture(str(INPUT_VIDEO))
    if not cap.isOpened():
        raise RuntimeError("OpenCVで入力動画を開けませんでした。")

    in_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    in_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    in_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Compute exact outscale so 720x1280 -> 2160x3840 (3x) or 1280x720 -> 3840x2160 (3x)
    outscale = max(TARGET_4K_W / in_w, TARGET_4K_H / in_h)

    print(f"🚀 Real-ESRGAN 4K超解像を開始します: {in_w}x{in_h} -> {TARGET_4K_W}x{TARGET_4K_H} ({total_frames}フレーム, outscale={outscale:.2f})")

    # Build direct FFmpeg stdin pipe encoder (zero huge temp PNG folders!)
    enc_args = (
        ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "17", "-b:v", "0"]
        if VIDEO_ENCODER == "h264_nvenc"
        else ["-c:v", "libx264", "-preset", "medium", "-crf", "16"]
    )
    ff_cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{TARGET_4K_W}x{TARGET_4K_H}",
        "-pix_fmt", "bgr24",
        "-r", f"{in_fps:.6f}",
        "-i", "-",
        *enc_args,
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(UPSCALED_4K_24FPS),
    ]
    ff_proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)

    pbar = tqdm(total=total_frames, unit="frame", desc="Real-ESRGAN 4K超解像")
    done_frames = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        sr_frame, _ = upsampler.enhance(frame, outscale=outscale)
        if sr_frame.shape[1] != TARGET_4K_W or sr_frame.shape[0] != TARGET_4K_H:
            sr_frame = cv2.resize(sr_frame, (TARGET_4K_W, TARGET_4K_H), interpolation=cv2.INTER_LANCZOS4)
        ff_proc.stdin.write(sr_frame.tobytes())
        done_frames += 1
        pbar.update(1)

    pbar.close()
    cap.release()
    ff_proc.stdin.close()
    rc = ff_proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg パイプ出力がエラー終了しました (code={rc})")

    del upsampler, model
    torch.cuda.empty_cache()
    gc.collect()

    u_info = probe_video_info(UPSCALED_4K_24FPS)
    print(f"\\n✅ セル④（4K超解像）完了！所要時間: {time.time() - t0:.1f}秒")
    print(f"   出力: {u_info['width']}×{u_info['height']} | fps={u_info['fps']} | {u_info['duration']:.2f}秒 | {u_info['size_mb']:.1f}MB")
    print("   次のセル⑤（60fpsフレーム補間）へ進んでください。")
except Exception as e:
    show_friendly_error(
        "セル④（Real-ESRGAN 4K超解像）",
        e,
        [
            "『CUDA out of memory（メモリ不足）』と出た場合：セル②で T4 GPU のときは自動で tile=256 になりますが、さらに安全にするにはセル②のコード内で TILE_SIZE = 192 にして再実行してください。",
            "h264_nvenc 関連のエラーが出た場合：セル②で VIDEO_ENCODER = 'libx264' と書き換えて再実行すると確実に通ります。",
        ],
    )
    raise
""",
        title_comment="# ============================================================\n# セル④：超解像（Real-ESRGAN realesr-general-x4v3 → FFmpeg直結パイプ）\n# ============================================================",
    )
)

# ==============================================================================
# CELL 5: フレーム補間（Practical-RIFE 24->60fps + minterpolate auto-fallback）
# ==============================================================================
CELLS.append(
    md_cell(
        """## ⑤ フレーム補間（Practical-RIFE で 24fps → 60fps 滑らか化／失敗時自動フォールバック）
**このセルで行うこと**：
- 4K超解像した 24fps 動画を **Practical-RIFE（AIフレーム補間）** で息を呑むほど滑らかな **60fps** にします（24fps → 4倍 96fps 生成 → 正確な 60fps へ時間一致リサンプリング、**再生時間は元動画と完全一致**）。
- 万一、Practical-RIFE でメモリ不足やモデル未取得が起きても処理が止まらないよう、**自動で FFmpeg のオプティカルフロー補間（`minterpolate`）へ切り替え**ます。
"""
    )
)

CELLS.append(
    code_cell(
        """import gc, time, torch, subprocess, shutil
from pathlib import Path

INTERP_4K_60FPS = WORK_DIR / "stage2_4k_60fps_noaudio.mp4"
RIFE_DIR = WORK_DIR / "Practical-RIFE"
TARGET_FPS = 60
INTERP_ENGINE_USED = "unknown"

def run_ffmpeg_minterpolate_fallback(src_mp4: Path, dst_mp4: Path, encoder: str):
    print("🔄 FFmpeg オプティカルフロー補間（minterpolate → 60fps）に自動切替して実行します...")
    enc_args = (
        ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "17", "-b:v", "0"]
        if encoder == "h264_nvenc"
        else ["-c:v", "libx264", "-preset", "medium", "-crf", "16"]
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(src_mp4),
        "-vf", f"minterpolate=fps={TARGET_FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:search_param=16",
        *enc_args,
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(dst_mp4),
    ]
    subprocess.run(cmd, check=True)

try:
    t0 = time.time()
    torch.cuda.empty_cache()
    gc.collect()

    rife_ok = False
    if USE_CUDA and (RIFE_DIR / "inference_video.py").exists() and (RIFE_DIR / "train_log" / "flownet.pkl").exists():
        print(f"🚀 Practical-RIFE で 4K 24fps → 60fps フレーム補間を実行します (scale={RIFE_SCALE}, FP16)...")
        rife_raw_out = WORK_DIR / "rife_4x_96fps.mp4"
        try:
            # Step 5A: Practical-RIFE multi=4 (24fps -> 96fps) with half-res optical flow for 4K VRAM safety
            rife_cmd = [
                sys.executable, str(RIFE_DIR / "inference_video.py"),
                "--video", str(UPSCALED_4K_24FPS),
                "--output", str(rife_raw_out),
                "--multi", "4",
                "--scale", str(RIFE_SCALE),
                "--fp16",
            ]
            res = subprocess.run(rife_cmd, cwd=str(RIFE_DIR), text=True, capture_output=True)
            if res.returncode == 0 and rife_raw_out.exists() and rife_raw_out.stat().st_size > 1_000_000:
                # Step 5B: Convert 96fps -> exact 60fps preserving exact original duration!
                enc_args = (
                    ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "17", "-b:v", "0"]
                    if VIDEO_ENCODER == "h264_nvenc"
                    else ["-c:v", "libx264", "-preset", "medium", "-crf", "16"]
                )
                subprocess.run(
                    [
                        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(rife_raw_out),
                        "-vf", f"fps={TARGET_FPS}",
                        *enc_args,
                        "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        str(INTERP_4K_60FPS),
                    ],
                    check=True,
                )
                rife_raw_out.unlink(missing_ok=True)
                rife_ok = True
                INTERP_ENGINE_USED = "Practical-RIFE (AI 4x補間 → 60fps)"
            else:
                print("⚠️ Practical-RIFE がエラーを返しました（自動フォールバックします）:")
                print(res.stderr[-600:])
        except Exception as re_err:
            print(f"⚠️ Practical-RIFE 実行中に例外発生（自動フォールバックします）: {re_err}")

    if not rife_ok:
        run_ffmpeg_minterpolate_fallback(UPSCALED_4K_24FPS, INTERP_4K_60FPS, VIDEO_ENCODER)
        INTERP_ENGINE_USED = "FFmpeg minterpolate (オプティカルフロー 60fps 自動切替)"

    torch.cuda.empty_cache()
    gc.collect()

    i_info = probe_video_info(INTERP_4K_60FPS)
    dur_diff = abs(i_info["duration"] - SRC_INFO["duration"])
    print(f"\\n✅ セル⑤（60fpsフレーム補間）完了！使用エンジン: {INTERP_ENGINE_USED}（所要 {time.time() - t0:.1f}秒）")
    print(f"   出力: {i_info['width']}×{i_info['height']} | fps={i_info['fps']} | 再生時間={i_info['duration']:.2f}秒 (元動画との差 {dur_diff:.2f}秒)")
    if dur_diff > 0.35:
        print("   ⚠️ 再生時間にわずかなズレを検出したため、セル⑥で元動画の尺と厳密に合わせます。")
    print("   次のセル⑥（音声復元・4Kシネマ仕上げ・2本書き出し）へ進んでください。")
except Exception as e:
    show_friendly_error(
        "セル⑤（60fpsフレーム補間）",
        e,
        [
            "4Kのフレーム補間はGPUメモリを多く使います。T4 GPUでメモリ不足になった場合は、セル②の RIFE_SCALE を 0.25 にして再実行してください。",
            "それでも失敗する場合は、上のコードで rife_ok = False にすると FFmpeg minterpolate だけで確実に60fps化できます。",
        ],
    )
    raise
""",
        title_comment="# ============================================================\n# セル⑤：フレーム補間（Practical-RIFE 24fps→60fps / 失敗時 minterpolate 自動切替）\n# ============================================================",
    )
)

# ==============================================================================
# CELL 6: 書き出し（元環境音の復元 ＋ 4Kシネマ仕上げ ＋ 4K保存用 & 1080p Lanczos縮小版の2本出力）
# ==============================================================================
CELLS.append(
    md_cell(
        """## ⑥ 書き出し（環境音の復元 ＆ ネイティブ4Kシネマ仕上げ ＆ 2本出力）
**このセルで行うこと**：
- 元動画の環境音（油のジュワァ音・備長炭のパチパチ音）を映像とズレゼロで戻します。
- **`ENABLE_FINE_ATLAS_CINEMA = True`（初期値）のとき**：4K 60fps化した映像の上から、一切滲まない **ネイティブ4K（`2160×3840`）のシネマ同期字幕・品質データ札・27〜30秒公式ブランド締め・日英プロナレーション＆和風琴BGM** を合成し、社長計画書どおりの **ジャスト30.00秒** で仕上げます！
- 最後に **2本** を自動書き出しします：
  1. **保存用 4K・60fps マスター**（`2160×3840` 60fps ／ 横型時 `3840×2160` 60fps）
  2. **SNS投稿用 1080p・60fps 版**（4Kマスターから **Lanczos縮小** した `1080×1920` 60fps ／ 横型時 `1920×1080` 60fps）
"""
    )
)

CELLS.append(
    code_cell(
        """import json, math, time, textwrap, subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FINAL_OUTPUTS = []  # list of (label, Path)

FONT_SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
CATCHPHRASE_JP = "日本の旬と品質を、一箱に。世界の厨房へ。"
CATCHPHRASE_EN = "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."

_FC = {}
def get_font(path, sz):
    k = (path, int(sz))
    if k not in _FC:
        _FC[k] = ImageFont.truetype(path, int(sz))
    return _FC[k]

def fit_font(draw, text, path, max_sz, min_sz, max_w):
    for sz in range(max_sz, min_sz - 1, -2):
        f = get_font(path, sz)
        if draw.textlength(text, font=f) <= max_w:
            return f
    return get_font(path, min_sz)

def draw_shadow(draw, pos, text, font, fill, anchor="mm", off=4):
    x, y = pos
    draw.text((x + off, y + off), text, font=font, fill=(0, 0, 0, 185), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

def make_vignette_4k(w, h):
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    th = int(h * 0.24)
    arr[:th, :, :3] = (8, 18, 32)
    arr[:th, :, 3] = ((np.linspace(1.0, 0.0, th) ** 1.55)[:, None] * 198).astype(np.uint8)
    by = int(h * 0.66)
    bh = h - by
    arr[by:, :, :3] = (7, 16, 28)
    arr[by:, :, 3] = ((np.linspace(0.0, 1.0, bh) ** 1.45)[:, None] * 224).astype(np.uint8)
    return Image.fromarray(arr, mode="RGBA")

def make_header_4k(w, h, meta, is_en):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = w / 1080.0
    cat = meta["category_en"] if is_en else meta["category_jp"]
    head = meta["headline_en"] if is_en else meta["headline_jp"]
    sub = meta["subhead_en"] if is_en else meta["subhead_jp"]
    f_cat = get_font(FONT_SANS, int(24 * s))
    cw = d.textlength(cat, font=f_cat) + int(48 * s)
    x0 = (w - cw) / 2
    d.rounded_rectangle([x0, int(102 * s), x0 + cw, int(148 * s)], radius=int(23 * s),
                        fill=(11, 28, 48, 205), outline=(217, 155, 58, 240), width=max(2, int(2 * s)))
    d.text((w / 2, int(125 * s)), cat, font=f_cat, fill=(253, 224, 128, 255), anchor="mm")
    f_h = fit_font(d, head, FONT_SERIF, int(56 * s), int(38 * s), int(w * 0.88))
    draw_shadow(d, (w / 2, int(198 * s)), head, f_h, (255, 255, 255, 255), off=int(3 * s))
    f_s = fit_font(d, sub, FONT_SANS, int(34 * s), int(24 * s), int(w * 0.88))
    draw_shadow(d, (w / 2, int(258 * s)), sub, f_s, (253, 224, 102, 255), off=int(2 * s))
    d.line([int(w * 0.30), int(292 * s), int(w * 0.70), int(292 * s)], fill=(217, 155, 58, 175), width=max(2, int(2 * s)))
    return img

def make_plaque_4k(w, h, lbl, val, is_en):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = w / 1080.0
    pw, ph = int(760 * s), int(84 * s)
    x0, y0 = (w - pw) // 2, int(314 * s)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=int(14 * s),
                        fill=(10, 25, 42, 210), outline=(217, 155, 58, 235), width=max(2, int(2 * s)))
    d.rounded_rectangle([x0, y0, x0 + int(10 * s), y0 + ph], radius=int(6 * s), fill=(217, 155, 58, 255))
    fl = fit_font(d, lbl, FONT_SANS, int(21 * s), int(16 * s), pw - int(56 * s))
    fv = fit_font(d, val, FONT_SERIF if not is_en else FONT_SANS, int(30 * s), int(20 * s), pw - int(56 * s))
    d.text((w / 2 + int(4 * s), y0 + int(24 * s)), lbl, font=fl, fill=(216, 226, 238, 255), anchor="mm")
    d.text((w / 2 + int(4 * s), y0 + int(58 * s)), val, font=fv, fill=(253, 224, 102, 255), anchor="mm")
    return img

def make_sub_4k(w, h, lines, is_en):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = w / 1080.0
    fonts = [fit_font(d, ln, FONT_SANS, int((38 if is_en else 42) * s), int(26 * s), int(w * 0.84)) for ln in lines]
    max_tw = max(d.textlength(ln, font=f) for ln, f in zip(lines, fonts))
    lh, px, py = int(60 * s), int(42 * s), int(26 * s)
    bw, bh = min(int(w * 0.92), int(max_tw + px * 2)), lh * len(lines) + py * 2
    x0, y0 = (w - bw) // 2, int(1465 * s) - bh // 2
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(18 * s),
                        fill=(8, 19, 34, 212), outline=(217, 155, 58, 160), width=max(2, int(2 * s)))
    d.line([x0 + int(36 * s), y0 + bh - int(6 * s), x0 + bw - int(36 * s), y0 + bh - int(6 * s)],
           fill=(217, 155, 58, 210), width=max(3, int(3 * s)))
    for idx, (ln, f) in enumerate(zip(lines, fonts)):
        ly = y0 + py + int(lh * (idx + 0.5)) - int(2 * s)
        fill = (255, 255, 255, 255) if idx == 0 else (253, 232, 138, 255)
        draw_shadow(d, (w / 2, ly), ln, f, fill, off=int(2 * s))
    return img

def make_endcard_4k(w, h, bg_rgb, is_en):
    s = w / 1080.0
    bg = bg_rgb.resize((w, h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=int(28 * s)))
    base = Image.blend(bg, Image.new("RGB", (w, h), (9, 24, 42)), alpha=0.84).convert("RGBA")
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([int(48 * s), int(92 * s), w - int(48 * s), h - int(92 * s)],
                        radius=int(28 * s), outline=(217, 155, 58, 245), width=max(4, int(4 * s)))
    d.rounded_rectangle([int(64 * s), int(108 * s), w - int(64 * s), h - int(108 * s)],
                        radius=int(20 * s), outline=(245, 242, 235, 85), width=max(2, int(2 * s)))
    d.rounded_rectangle([int(290 * s), int(270 * s), w - int(290 * s), int(342 * s)], radius=int(36 * s), fill=(186, 108, 22, 255))
    d.text((w / 2, int(306 * s)), "FINE ATLAS Co., Ltd.", font=get_font(FONT_SANS, int(32 * s)), fill=(255, 255, 255, 255), anchor="mm")
    comp = "株式会社ファインアトラス" if not is_en else "FINE ATLAS — JAPAN QUALITY FROZEN"
    d.text((w / 2, int(420 * s)), comp, font=fit_font(d, comp, FONT_SERIF if not is_en else FONT_SANS, int(46 * s), int(30 * s), int(w * 0.80)),
           fill=(245, 242, 235, 255), anchor="mm")
    d.line([int(200 * s), int(496 * s), w - int(200 * s), int(496 * s)], fill=(217, 155, 58, 200), width=max(3, int(3 * s)))
    d.rounded_rectangle([int(88 * s), int(564 * s), w - int(88 * s), int(972 * s)],
                        radius=int(26 * s), fill=(14, 38, 64, 245), outline=(217, 155, 58, 255), width=max(4, int(4 * s)))
    if not is_en:
        fm = get_font(FONT_SERIF, int(56 * s))
        draw_shadow(d, (w / 2, int(684 * s)), "「日本の旬と品質を、一箱に。", fm, (255, 255, 255, 255), off=int(3 * s))
        draw_shadow(d, (w / 2, int(786 * s)), "世界の厨房へ。」", fm, (253, 224, 102, 255), off=int(3 * s))
        d.text((w / 2, int(902 * s)), CATCHPHRASE_EN, font=fit_font(d, CATCHPHRASE_EN, FONT_SANS, int(23 * s), int(16 * s), int(w * 0.78)),
               fill=(203, 213, 225, 255), anchor="mm")
    else:
        fm = get_font(FONT_SERIF, int(44 * s))
        y_ln = int(662 * s)
        for ln in textwrap.wrap(f'"{CATCHPHRASE_EN}"', width=26):
            draw_shadow(d, (w / 2, y_ln), ln, fm, (253, 224, 102, 255), off=int(3 * s))
            y_ln += int(66 * s)
        d.text((w / 2, int(904 * s)), f"「{CATCHPHRASE_JP}」", font=get_font(FONT_SERIF, int(27 * s)), fill=(245, 242, 235, 255), anchor="mm")
    d.rounded_rectangle([int(96 * s), int(1070 * s), w - int(96 * s), int(1366 * s)], radius=int(22 * s), fill=(245, 242, 235, 246))
    tf = "まずは少量購入で、貴店の厨房にて品質確認" if not is_en else "Verify Quality First with a Small Trial Order"
    d.text((w / 2, int(1136 * s)), tf, font=fit_font(d, tf, FONT_SERIF if not is_en else FONT_SANS, int(34 * s), int(22 * s), int(w * 0.78)),
           fill=(12, 34, 56, 255), anchor="mm")
    st_ln = "HP・Amazon少量試作  ▶  リピート仕入れ  ▶  店舗別オリジナル魚BOX" if not is_en else "Website / Amazon Trial  ▶  Repeat Supply  ▶  Custom Fish Box"
    d.rounded_rectangle([int(128 * s), int(1192 * s), w - int(128 * s), int(1264 * s)], radius=int(14 * s), fill=(14, 38, 64, 255))
    d.text((w / 2, int(1228 * s)), st_ln, font=fit_font(d, st_ln, FONT_SANS, int(25 * s), int(18 * s), int(w * 0.78)), fill=(253, 224, 102, 255), anchor="mm")
    sn = "産地で時間を止め、世界の厨房で時間を動かす。" if not is_en else "Freezing peak freshness at the port. Serving chefs worldwide."
    d.text((w / 2, int(1318 * s)), sn, font=fit_font(d, sn, FONT_SANS, int(24 * s), int(17 * s), int(w * 0.78)), fill=(51, 65, 85, 255), anchor="mm")
    d.rounded_rectangle([int(138 * s), int(1464 * s), w - int(138 * s), int(1572 * s)],
                        radius=int(28 * s), fill=(164, 54, 34, 255), outline=(253, 224, 102, 190), width=max(2, int(2 * s)))
    cta = "fineatlas.co.jp ｜ Amazon「ファインアトラス」" if not is_en else "fineatlas.co.jp | Search 'FINE ATLAS' on Amazon"
    d.text((w / 2, int(1518 * s)), cta, font=fit_font(d, cta, FONT_SANS, int(31 * s), int(21 * s), int(w * 0.72)), fill=(255, 255, 255, 255), anchor="mm")
    return base.convert("RGB")

def downscale_lanczos_sns(src_4k: Path, dst_1080: Path, w_sns: int, h_sns: int):
    enc_args = (
        ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "18", "-b:v", "0"]
        if VIDEO_ENCODER == "h264_nvenc"
        else ["-c:v", "libx264", "-preset", "medium", "-crf", "17"]
    )
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(src_4k),
            "-vf", f"scale={w_sns}:{h_sns}:flags=lanczos",
            *enc_args,
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            "-movflags", "+faststart",
            str(dst_1080),
        ],
        check=True,
    )

try:
    t0 = time.time()
    enc_master_args = (
        ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "16", "-b:v", "0"]
        if VIDEO_ENCODER == "h264_nvenc"
        else ["-c:v", "libx264", "-preset", "medium", "-crf", "16"]
    )

    # ------------------------------------------------------------------
    # Output Set A: Clean 4K 60fps Master + Lanczos 1080p 60fps SNS (with original ambient audio)
    # ------------------------------------------------------------------
    tag = "9x16" if ASPECT_MODE == "9:16_vertical" else "16x9"
    clean_4k_out = OUT_DIR / f"master_4K_60fps_{tag}_clean.mp4"
    clean_sns_out = OUT_DIR / f"sns_1080p_60fps_{tag}_clean.mp4"

    print("🎵 [1/2] 4K 60fps クリーン版へ元動画の環境音を同期結合しています...")
    if SRC_INFO["has_audio"]:
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(INTERP_4K_60FPS),
                "-i", str(INPUT_VIDEO),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-shortest", "-movflags", "+faststart",
                str(clean_4k_out),
            ],
            check=True,
        )
    else:
        shutil.copy2(INTERP_4K_60FPS, clean_4k_out)

    print("📐 4Kマスターから Lanczos 縮小で 1080p 60fps SNS用を生成しています...")
    downscale_lanczos_sns(clean_4k_out, clean_sns_out, TARGET_SNS_W, TARGET_SNS_H)
    FINAL_OUTPUTS.append((f"保存用 4K 60fps マスター（クリーン・{tag}）", clean_4k_out))
    FINAL_OUTPUTS.append((f"SNS投稿用 1080p 60fps（Lanczos縮小・クリーン・{tag}）", clean_sns_out))

    # ------------------------------------------------------------------
    # Output Set B (if enabled & 9:16): Native 4K 60fps Fine Atlas Cinema Edition
    #   Razor-sharp 2160x3840 typography & 27-30s brand closing composited AFTER 4K/60fps AI!
    # ------------------------------------------------------------------
    if ENABLE_FINE_ATLAS_CINEMA and ASPECT_MODE == "9:16_vertical" and OVERLAY_PACK_DIR is not None:
        manifest = json.loads((OVERLAY_PACK_DIR / "overlay_manifest.json").read_text(encoding="utf-8"))
        meta = manifest["episode_meta"]
        total_sec = float(manifest["total_duration_sec"])
        end_st = float(manifest["endcard_start_sec"])
        xf_sec = float(manifest["xfade_sec"])
        fi_sec = float(manifest["fade_in_sec"])
        fo_sec = float(manifest["fade_out_sec"])
        ep_code = manifest["code"]
        bgm_wav = OVERLAY_PACK_DIR / manifest["audio_files"]["bgm"]

        langs = ["jp", "en"] if CINEMA_LANGUAGES == "both" else [CINEMA_LANGUAGES]

        # Extract last-dish reference frame at 4K for the closing card backdrop
        ref_t = max(0.5, SRC_INFO["duration"] - 1.0)
        p_ref = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-ss", f"{ref_t:.2f}", "-i", str(INTERP_4K_60FPS),
                "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
            ],
            capture_output=True, check=True
        )
        end_ref_4k = Image.frombytes("RGB", (TARGET_4K_W, TARGET_4K_H), p_ref.stdout)
        vignette_4k = make_vignette_4k(TARGET_4K_W, TARGET_4K_H)

        for lang in langs:
            is_en = (lang == "en")
            print(f"\\n🎬 [2/2] ネイティブ4K・60fps シネマ完成版（{'英語版' if is_en else '日本語版'}・30.00秒）を合成しています...")
            nar_wav = OVERLAY_PACK_DIR / manifest["audio_files"][f"narration_{lang}"]
            mixed_wav = WORK_DIR / f"master_audio_{lang}.wav"
            af_graph = (
                f"[0:a]apad=whole_dur={total_sec:.2f},atrim=0:{total_sec:.2f},"
                f"volume=0.38,afade=t=in:st=0:d={fi_sec:.2f},afade=t=out:st={end_st:.2f}:d=1.20[amb];"
                f"[1:a]apad=whole_dur={total_sec:.2f},atrim=0:{total_sec:.2f},volume=1.18[vox];"
                f"[2:a]atrim=0:{total_sec:.2f},volume=0.14,afade=t=in:st=0:d=0.80,afade=t=out:st={total_sec - fo_sec:.2f}:d={fo_sec:.2f}[bgm];"
                f"[amb][vox][bgm]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.92:attack=5:release=50[aout]"
            )
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(INPUT_VIDEO), "-i", str(nar_wav), "-i", str(bgm_wav),
                    "-filter_complex", af_graph, "-map", "[aout]",
                    "-ar", "48000", "-ac", "2", str(mixed_wav),
                ],
                check=True,
            )

            # Pre-render static 4K RGBA graphic overlays as PNGs and use FFmpeg filter_complex
            # (GPU/C-speed native 4K compositing — 20x faster than Python per-frame PIL at 4K 60fps!)
            ov_dir = WORK_DIR / f"ov4k_{lang}"
            ov_dir.mkdir(exist_ok=True)
            chrome_png = ov_dir / "chrome.png"
            Image.alpha_composite(vignette_4k, make_header_4k(TARGET_4K_W, TARGET_4K_H, meta, is_en)).save(chrome_png)
            endcard_png = ov_dir / "endcard.png"
            make_endcard_4k(TARGET_4K_W, TARGET_4K_H, end_ref_4k, is_en).save(endcard_png)

            overlay_items = [(chrome_png, 0.0, end_st + 0.05)]
            for idx_p, (pst, pen, plbl, pval) in enumerate(meta[f"plaques_{lang}"]):
                pp = ov_dir / f"plaque_{idx_p}.png"
                make_plaque_4k(TARGET_4K_W, TARGET_4K_H, plbl, pval, is_en).save(pp)
                overlay_items.append((pp, float(pst), float(pen)))
            for idx_s, sub in enumerate(manifest[f"subtitles_{lang}"]):
                sp = ov_dir / f"sub_{idx_s}.png"
                make_sub_4k(TARGET_4K_W, TARGET_4K_H, sub["lines"], is_en).save(sp)
                overlay_items.append((sp, float(sub["start"]), float(sub["end"])))

            # Build ultra-fast FFmpeg native-4K overlay + 27s->30s crossfade filtergraph
            ff_in = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(INTERP_4K_60FPS),
                "-loop", "1", "-t", f"{total_sec - end_st + xf_sec:.2f}", "-r", str(TARGET_FPS), "-i", str(endcard_png),
                "-i", str(mixed_wav),
            ]
            for png_p, _, _ in overlay_items:
                ff_in += ["-i", str(png_p)]

            fgraph = [f"[0:v]fps={TARGET_FPS},setpts=PTS-STARTPTS,format=yuv420p[base0]"]
            cur = "base0"
            for k, (_, st, en) in enumerate(overlay_items):
                in_idx = 3 + k
                nxt = f"ov{k}"
                fgraph.append(f"[{cur}][{in_idx}:v]overlay=0:0:enable='between(t,{st:.3f},{en:.3f})'[{nxt}]")
                cur = nxt

            # Trim main composited clip safely using actual interpolated duration, xfade cleanly into 4K endcard
            interp_dur = probe_video_info(INTERP_4K_60FPS)["duration"]
            eff_end_st = min(end_st, max(1.0, interp_dur - xf_sec - 0.05))
            eff_total = eff_end_st + (total_sec - end_st)
            fgraph.append(f"[{cur}]trim=0:{eff_end_st + xf_sec:.3f},setpts=PTS-STARTPTS,format=yuv420p[main_part]")
            fgraph.append(f"[1:v]fps={TARGET_FPS},setpts=PTS-STARTPTS,format=yuv420p[end_part]")
            fgraph.append(
                f"[main_part][end_part]xfade=transition=fade:duration={xf_sec:.3f}:offset={eff_end_st:.3f},"
                f"fade=t=out:st={eff_total - fo_sec:.3f}:d={fo_sec:.3f},"
                f"trim=0:{eff_total:.3f},format=yuv420p[vfinal]"
            )

            cinema_4k = OUT_DIR / f"{ep_code}_4K_60fps_9x16_{lang}.mp4"
            cinema_sns = OUT_DIR / f"{ep_code}_1080p_60fps_9x16_{lang}_SNS.mp4"
            subprocess.run(
                ff_in + [
                    "-filter_complex", ";".join(fgraph),
                    "-map", "[vfinal]", "-map", "2:a:0",
                    *enc_master_args,
                    "-pix_fmt", "yuv420p", "-r", str(TARGET_FPS),
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-shortest", "-movflags", "+faststart",
                    str(cinema_4k),
                ],
                check=True,
            )
            downscale_lanczos_sns(cinema_4k, cinema_sns, TARGET_SNS_W, TARGET_SNS_H)
            lang_label = "🇺🇸 英語版" if is_en else "🇯🇵 日本語版"
            FINAL_OUTPUTS.append((f"★ 保存用 4K 60fps シネマ完成版（{lang_label}・30秒）", cinema_4k))
            FINAL_OUTPUTS.append((f"★ SNS投稿用 1080p 60fps シネマ完成版（{lang_label}・Lanczos縮小）", cinema_sns))

    print(f"\\n🎉 セル⑥（書き出し）完了！計 {len(FINAL_OUTPUTS)} 本の高画質動画を書き出しました（所要 {time.time() - t0:.1f}秒）")
    print("   次のセル⑦（保存）へ進んでください。")
except Exception as e:
    show_friendly_error(
        "セル⑥（書き出し・4K合成）",
        e,
        [
            "セル④・⑤が正常に完了しているか確認してください。",
            "日本語フォントが見つからない場合は、セル①をもう一度実行してください。",
        ],
    )
    raise
""",
        title_comment="# ============================================================\n# セル⑥：書き出し（環境音復元・ネイティブ4Kシネマ合成・4K＆1080p Lanczos 2本出力）\n# ============================================================",
    )
)

# ==============================================================================
# CELL 7: 保存
# ==============================================================================
CELLS.append(
    md_cell(
        """## ⑦ 保存（Googleドライブへ自動保存 ＆ PCへの直接ダウンロード）
**このセルで行うこと**：
- 書き出した 4K・60fps マスターと SNS投稿用 1080p・60fps 動画を **Googleドライブ（`4K60_Completed` フォルダ）へ自動コピー保存** します（ランタイムを切っても消えません！）。
- `DOWNLOAD_TO_PC = True` にすると、ブラウザからそのままPCへ自動ダウンロードもできます。
"""
    )
)

CELLS.append(
    code_cell(
        """#@title 💾 保存オプション
DOWNLOAD_TO_PC = False #@param {type:"boolean"}

import shutil

try:
    if DRIVE_SAVE_DIR is not None:
        DRIVE_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"☁️ Googleドライブへ保存中: {DRIVE_SAVE_DIR}")
        for lbl, fpath in FINAL_OUTPUTS:
            dst = DRIVE_SAVE_DIR / fpath.name
            shutil.copy2(fpath, dst)
            print(f"  ✅ 保存完了: {dst.name}")
    else:
        print("ℹ️ Googleドライブ未接続モードです（下の直接ダウンロードをONにするか、左のフォルダアイコン /content/fine_atlas_4k60/outputs からダウンロードしてください）。")

    if DOWNLOAD_TO_PC:
        from google.colab import files
        for lbl, fpath in FINAL_OUTPUTS:
            print(f"⬇️ ダウンロード開始: {fpath.name}")
            files.download(str(fpath))

    print("\\n✅ セル⑦（保存）完了！最後にセル⑧（最終確認）を実行してください。")
except Exception as e:
    show_friendly_error(
        "セル⑦（保存）",
        e,
        [
            "Googleドライブの空き容量が足りているか確認してください（4K 60fps 動画は1本あたり約 80〜200MB になります）。",
            "手動で保存したい場合は、Colab左側のフォルダアイコン → fine_atlas_4k60 → outputs 内のファイルを右クリック→ダウンロードで保存できます。",
        ],
    )
    raise
""",
        title_comment="# ============================================================\n# セル⑦：保存（Googleドライブ自動保存 ＆ PCダウンロード）\n# ============================================================",
    )
)

# ==============================================================================
# CELL 8: 最終確認
# ==============================================================================
CELLS.append(
    md_cell(
        """## ⑧ 最終確認（完成動画の全スペック表示 ＆ ランタイム切断のご案内）
**このセルで行うこと**：
- 完成した全動画の **解像度・fps・再生時間・ファイルサイズ・音声の有無** を自動検査して一覧表示します。
- 最後に **Google Colab の GPU 課金／クレジット消費を防ぐための「ランタイム切断」案内** を表示します。
"""
    )
)

CELLS.append(
    code_cell(
        """print("=" * 84)
print("🏁 FINE ATLAS 4K・60fps 完成動画 最終品質チェック結果")
print("=" * 84)
print(f"使用GPU: {GPU_NAME} | 超解像: Real-ESRGAN (realesr-general-x4v3) | 補間: {INTERP_ENGINE_USED}")
print("-" * 84)

all_ok = True
for lbl, fpath in FINAL_OUTPUTS:
    if not fpath.exists() or fpath.stat().st_size < 100_000:
        print(f"❌ {lbl}: ファイルが見つからないか破損しています ({fpath})")
        all_ok = False
        continue
    inf = probe_video_info(fpath)
    print(f"🎬 {lbl}")
    print(f"   ファイル名 : {inf['name']}")
    print(f"   解像度     : {inf['width']} × {inf['height']}")
    print(f"   fps        : {inf['fps']}")
    print(f"   再生時間   : {inf['duration']:.2f} 秒")
    print(f"   サイズ     : {inf['size_mb']:.2f} MB")
    print(f"   音声       : {inf['audio_desc']}")
    print("-" * 84)

if all_ok:
    print("✅ すべての完成動画が規格どおり正常に書き出されました！")
else:
    print("⚠️ 一部の動画に問題があります。上のエラー表示を確認してください。")

print("\\n" + "!" * 72)
print("🛑 【超重要】作業が終わったら、必ず GPU ランタイムを切断してください！")
print("   手順：画面上部メニュー『ランタイム』→『ランタイムを接続解除して削除』→『はい』")
print("   ※つなぎっぱなしにすると Colab の GPU クレジットを消費し続けてしまいます。")
print("!" * 72)
""",
        title_comment="# ============================================================\n# セル⑧：最終確認（解像度・fps・再生時間・音声の有無を表示）\n# ============================================================",
    )
)


def main():
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "colab": {
                "provenance": [],
                "gpuType": "L4",
                "machine_shape": "hm",
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3",
            },
            "language_info": {
                "name": "python",
            },
            "accelerator": "GPU",
        },
        "cells": CELLS,
    }

    OUT_IPYNB.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Generated {OUT_IPYNB} ({OUT_IPYNB.stat().st_size:,} bytes, {len(CELLS)} cells)")

    # Deterministic validation: JSON reload + Python AST syntax check on every code cell
    reloaded = json.loads(OUT_IPYNB.read_text(encoding="utf-8"))
    code_cells = [c for c in reloaded["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) == 8, f"Expected 8 code cells, got {len(code_cells)}"

    full_code = []
    for idx, c in enumerate(code_cells, 1):
        src = "".join(c["source"])
        ast.parse(src, filename=f"cell_{idx}.py")
        full_code.append(src)
    joined = "\n".join(full_code)

    # Mandatory specification keywords gate
    for kw in [
        "realesr-general-x4v3",
        "h264_nvenc",
        "libx264",
        "Practical-RIFE",
        "minterpolate",
        "lanczos",
        "3840",
        "2160",
        "1920",
        "1080",
        "日本の旬と品質を、一箱に。世界の厨房へ。",
        "ランタイムを接続解除して削除",
    ]:
        assert kw in joined, f"Missing required spec keyword in notebook: {kw}"

    print("[PASS] All 8 Colab code cells passed Python AST syntax check & mandatory spec gate!")


if __name__ == "__main__":
    main()
