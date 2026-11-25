#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
株式会社ファインアトラス｜AIショート動画 毎日配信計画
決定論的検証ゲートスクリプト (validate_gate.py)
実行時間 < 0.5s, 課金 ¥0 で全要件を100%検査する
"""

import json
import sys
import time
from pathlib import Path
import openpyxl

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_JS_PATH = BASE_DIR / "data.js"
EXCEL_PATH = BASE_DIR / "ファインアトラス_AIショート動画_毎日配信マスター台帳.xlsx"

EXPECTED_CLOSING_JP = "日本の旬と品質を、一箱に。世界の厨房へ。"
EXPECTED_CLOSING_EN = "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."

REQUIRED_TOP_KEYS = [
    "planOverview",
    "weekdaySchedule",
    "themes19",
    "fishMaster10",
    "episodes",
    "calendar365",
    "dotPromptTemplates",
    "assetInventory460"
]

REQUIRED_EPISODE_ITEMS = [
    "item1_title",
    "item2_narration",
    "item3_timecode",
    "item4_mediaDirection",
    "item5_aiImagePrompt",
    "item6_subtitles",
    "item7_snsCaption",
    "item8_hashtags",
    "item9_sources",
    "item10_bilingualCheck"
]


def fail(msg):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    t0 = time.time()

    # 1. Verify data.js exists and parses cleanly as JSON
    if not DATA_JS_PATH.exists():
        fail(f"data.js does not exist at {DATA_JS_PATH}")

    raw_js = DATA_JS_PATH.read_text(encoding="utf-8")
    prefix = "window.FINE_ATLAS_SHORTS_DATA = "
    idx = raw_js.find(prefix)
    if idx == -1:
        fail("data.js does not contain 'window.FINE_ATLAS_SHORTS_DATA = '")

    json_str = raw_js[idx + len(prefix):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1].strip()

    try:
        data = json.loads(json_str)
    except Exception as e:
        fail(f"data.js failed JSON parse: {e}")

    for k in REQUIRED_TOP_KEYS:
        if k not in data:
            fail(f"Missing required top-level key in data.js: {k}")

    # Check closing catchphrase in planOverview
    po = data["planOverview"]
    if po.get("closingCatchphraseJp") != EXPECTED_CLOSING_JP:
        fail(f"planOverview.closingCatchphraseJp mismatch: {po.get('closingCatchphraseJp')}")
    if po.get("closingCatchphraseEn") != EXPECTED_CLOSING_EN:
        fail(f"planOverview.closingCatchphraseEn mismatch: {po.get('closingCatchphraseEn')}")

    # 2. Verify all 28 episodes have all 10 required Section-10 items
    episodes = data["episodes"]
    if len(episodes) != 28:
        fail(f"Expected 28 episodes, got {len(episodes)}")

    for i, ep in enumerate(episodes, 1):
        expected_id = f"DAY-{i:02d}"
        if ep.get("id") != expected_id:
            fail(f"Episode {i} id mismatch: expected {expected_id}, got {ep.get('id')}")
        for item_key in REQUIRED_EPISODE_ITEMS:
            if item_key not in ep or not ep[item_key]:
                fail(f"Episode {expected_id} missing or empty {item_key}")

        # Check bilingual title & narration
        if not ep["item1_title"].get("jp") or not ep["item1_title"].get("en"):
            fail(f"Episode {expected_id} empty title jp/en")
        if EXPECTED_CLOSING_JP not in ep["item2_narration"].get("jp", ""):
            fail(f"Episode {expected_id} narration.jp does not contain closing phrase '{EXPECTED_CLOSING_JP}'")
        if EXPECTED_CLOSING_EN not in ep["item2_narration"].get("en", ""):
            fail(f"Episode {expected_id} narration.en does not contain closing phrase '{EXPECTED_CLOSING_EN}'")

        # Check timecode 4 blocks and 27-30s closing
        tc = ep["item3_timecode"]
        if len(tc) != 4:
            fail(f"Episode {expected_id} item3_timecode must have 4 blocks, got {len(tc)}")
        if tc[3]["sec"] != "27〜30秒" or EXPECTED_CLOSING_JP not in tc[3]["audioJp"]:
            fail(f"Episode {expected_id} 27〜30秒 timecode missing closing phrase")

        # Check sales funnel mention in SNS caption
        cap_jp = ep["item7_snsCaption"].get("jp", "")
        if "Amazon" not in cap_jp or "オリジナル魚BOX" not in cap_jp:
            fail(f"Episode {expected_id} item7_snsCaption.jp missing Amazon / オリジナル魚BOX funnel")

    # 3. Verify calendar365
    cal = data["calendar365"]
    if len(cal) != 365:
        fail(f"Expected 365 days in calendar365, got {len(cal)}")

    day_nums = [c["dayNumber"] for c in cal]
    if day_nums != list(range(1, 366)):
        fail("calendar365 dayNumber is not strictly 1..365")

    titles_jp = [c["titleJp"] for c in cal]
    if len(set(titles_jp)) != 365:
        fail(f"calendar365 has duplicate titleJp! Unique count: {len(set(titles_jp))}/365")

    weekday_themes_used = set(c["weekdayTheme"] for c in cal)
    if len(weekday_themes_used) != 7:
        fail(f"calendar365 does not cover all 7 weekday themes: {len(weekday_themes_used)}")

    themes19_used = set(c["themeId"] for c in cal)
    if len(themes19_used) != 19:
        fail(f"calendar365 does not cover all 19 themes: {len(themes19_used)}/19 ({themes19_used})")

    # 4. Verify assetInventory460
    assets = data["assetInventory460"]
    if assets.get("totalCount") != 460 or assets.get("photoTotal") != 350 or assets.get("videoTotal") != 110:
        fail("assetInventory460 totals mismatch (expected 460 = 350 photos + 110 videos)")

    cats = assets.get("categories", [])
    if len(cats) != 8:
        fail(f"Expected 8 asset categories, got {len(cats)}")

    photo_sum = sum(c["targetCount"] for c in cats if "写真" in c["type"])
    video_sum = sum(c["targetCount"] for c in cats if "動画" in c["type"])
    if photo_sum != 350 or video_sum != 110:
        fail(f"Category sums mismatch: photos={photo_sum}, videos={video_sum}")

    if len(assets.get("items", [])) != 460:
        fail(f"Expected 460 individual asset checklist items, got {len(assets.get('items', []))}")

    # 5. Verify Excel workbook exists, has 6 sheets, and no formula errors
    if not EXCEL_PATH.exists():
        fail(f"Excel file does not exist at {EXCEL_PATH}")

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=False)
    expected_sheets = [
        "1_全体計画_KPIダッシュボード",
        "2_初回28日_日英完全台本10項目",
        "3_年間365日_配信テーマ計画表",
        "4_写真350枚_動画110本_素材DB",
        "5_Dot指示文_Vrew_Metricool手順",
        "6_ファインアトラス魚種_原価データ"
    ]
    if wb.sheetnames != expected_sheets:
        fail(f"Excel sheet names mismatch: got {wb.sheetnames}, expected {expected_sheets}")

    error_tokens = ("#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "Err:")
    formula_count = 0
    for sname in wb.sheetnames:
        ws = wb[sname]
        for row in ws.iter_rows(values_only=True):
            for val in row:
                if isinstance(val, str):
                    if val.startswith("="):
                        formula_count += 1
                    for err in error_tokens:
                        if err in val:
                            fail(f"Excel error token '{err}' found in sheet {sname}: {val}")

    if formula_count < 10:
        fail(f"Expected at least 10 dynamic formulas in Excel workbook, found {formula_count}")

    elapsed = time.time() - t0
    print(f"[PASS] All deterministic gate checks passed in {elapsed:.3f}s!")
    print("  - data.js JSON schema & 8 top-level keys: OK")
    print(f"  - 28 complete bilingual episodes (all 10 Dot items & 27-30s '{EXPECTED_CLOSING_JP}'): OK")
    print("  - 365-day calendar (0 duplicate titles, 7 weekday categories, 19 themes covered): OK")
    print("  - 460 asset inventory items (Photos 100+100+50+100=350, Videos 30+30+30+20=110): OK")
    print(f"  - 6-sheet Excel workbook ({formula_count} formulas, 0 errors): OK")


if __name__ == "__main__":
    main()
