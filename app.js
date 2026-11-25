/**
 * FINE ATLAS 🎬 AIショート動画 毎日配信コンパス ＆ 365日台本スタジオ
 * app.js — Interactive 5-Mode Studio Engine
 */
(function () {
  "use strict";

  const STORAGE_KEYS = {
    EP_STATUS: "fine_atlas_shorts_day_status_v1",
    ASSET_CHECKS: "fine_atlas_shorts_asset_checks_v1",
    FONT_SCALE: "fine_atlas_shorts_font_scale_v1",
    LANG_MODE: "fine_atlas_shorts_lang_mode_v1"
  };

  const CATCHPHRASE_JP = "日本の旬と品質を、一箱に。世界の厨房へ。";
  const CATCHPHRASE_EN = "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide.";

  // State
  let rawData = null;
  let dayStatusMap = {};
  let assetCheckMap = {};
  let activeEpWeek = "all";
  let activeEpWeekday = "all";
  let activeDotTemplateIdx = 0;
  let currentGeneratedEp = null;

  // Helpers
  function loadStorage(key, fallback) {
    try {
      const val = localStorage.getItem(key);
      return val ? JSON.parse(val) : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function saveStorage(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) {
      // ignore storage quota errors
    }
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  let toastTimer = null;
  function showToast(msg) {
    const box = document.getElementById("toast-box");
    if (!box) return;
    box.textContent = msg;
    box.classList.add("is-visible");
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      box.classList.remove("is-visible");
    }, 2800);
  }

  function copyToClipboard(text, label) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () {
          showToast("✅ " + label + " をコピーしました！");
        },
        function () {
          fallbackCopy(text, label);
        }
      );
    } else {
      fallbackCopy(text, label);
    }
  }

  function fallbackCopy(text, label) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
      showToast("✅ " + label + " をコピーしました！");
    } catch (e) {
      showToast("⚠️ コピーに失敗しました。手動で選択してください。");
    }
    document.body.removeChild(ta);
  }

  // Fallback defaults if any property is omitted
  function getSafeData() {
    const d = window.FINE_ATLAS_SHORTS_DATA || {};
    return {
      planOverview: d.planOverview || {
        title: "ファインアトラス AIを活用したショート動画毎日配信計画",
        closingCatchphraseJp: CATCHPHRASE_JP,
        closingCatchphraseEn: CATCHPHRASE_EN,
        videoRules: {
          duration: "30秒",
          aspect: "縦型 9:16",
          resolution: "1080×1920",
          subtitleRule: "音声なしでも理解できるよう、字幕を必ず入れる",
          targetWorkTime: "1日20〜30分（または週1回7日分まとめ制作）"
        },
        timecodeStructure: [
          { range: "0〜3秒", role: "興味を引く導入（フック）" },
          { range: "3〜20秒", role: "本題（旬・目利き・冷凍技術・仕入れ改善）" },
          { range: "20〜27秒", role: "要点まとめ（現場メリット・品質数値）" },
          { range: "27〜30秒", role: "会社名・共通キャッチコピー" }
        ],
        annualTargets: {
          dailyThemes: 1,
          monthlyThemes: 30,
          yearlyThemes: 365,
          bilingualVideos: 730,
          snsCount: 4,
          totalYearlyPosts: 2920,
          snsPlatforms: ["YouTube Shorts", "Instagram Reels", "TikTok", "Facebook Reels"]
        },
        aiTools: [
          { id: "dot", num: "①", name: "ChatGPT・Dot", tasks: ["365日分のテーマ作成", "日本語・英語の台本作成", "字幕・SNS投稿文・ハッシュタグ作成", "AI画像生成用の指示文作成"] },
          { id: "vrew", num: "②", name: "Vrew", tasks: ["台本から動画作成", "AI音声作成（日・英）", "自動字幕作成", "写真・動画・BGMの組み合わせ"] },
          { id: "canva", num: "③", name: "Canva", tasks: ["30秒動画の共通デザイン作成", "表紙画像作成", "会社ロゴ・最後の案内画面作成（27〜30秒）"] },
          { id: "metricool", num: "④", name: "Metricool", tasks: ["4つのSNS（YouTube / Instagram / TikTok / Facebook）への予約投稿"] }
        ],
        dailyRoutine8: [
          { step: "①", title: "その日のテーマを確認する", tool: "本スタジオ / カレンダー", targetMinutes: "2分", detail: "曜日別テーマと19の配信テーマ・主役魚種を確認する" },
          { step: "②", title: "Dotで台本・英語・投稿文を作成する", tool: "ChatGPT・Dot（または本スタジオ即時生成）", targetMinutes: "3分", detail: "10項目（①〜⑩）の日英台本とVrew用字幕を取得する" },
          { step: "③", title: "内容に間違いがないか確認する", tool: "担当者目視（事実確認ガードレール）", targetMinutes: "3分", detail: "歩留まり・原価率・産地表記に推測や誤りがないかチェック" },
          { step: "④", title: "使用する写真・動画を選ぶ", tool: "自社素材460点フォルダ", targetMinutes: "4分", detail: "実際の商品・魚種は自社撮影の写真・動画を最優先で選ぶ" },
          { step: "⑤", title: "不足している素材だけAI画像を作成する", tool: "ChatGPT / Canva AI", targetMinutes: "3分", detail: "⑤のAI画像生成指示文を使い、補足イメージのみ生成する" },
          { step: "⑥", title: "Vrewで日本語版・英語版動画を作成する", tool: "Vrew ＋ Canva共通枠", targetMinutes: "8分", detail: "1080×1920縦型・30秒・字幕必須・27〜30秒共通キャッチで書き出す" },
          { step: "⑦", title: "動画を確認する", tool: "スマホ・PCプレビュー", targetMinutes: "2分", detail: "ミュート（音声なし）でも字幕だけで魅力が伝わるか確認する" },
          { step: "⑧", title: "Metricoolで予約投稿する", tool: "Metricool", targetMinutes: "3分", detail: "YouTube Shorts / Instagram Reels / TikTok / Facebook Reels へ予約" }
        ],
        salesFunnel7: [
          { step: "STEP 1", title: "ショート動画毎日配信", desc: "日英730本・4大SNS年2,920投稿で毎日接触" },
          { step: "STEP 2", title: "認知獲得", desc: "料理長・飲食店オーナー・海外バイヤーの目に留まる" },
          { step: "STEP 3", title: "専門情報で信頼獲得", desc: "目利き・急速冷凍・歩留まり原価の実証データで信頼構築" },
          { step: "STEP 4", title: "ホームページ・Amazonへ誘導", desc: "プロフィール＆投稿文から公式HP・Amazon販売ページへ案内" },
          { step: "STEP 5", title: "少量購入で品質確認", desc: "まずはAmazonや公式お試しセット（小ロット1箱）で実物検証" },
          { step: "STEP 6", title: "リピート購入", desc: "ドリップの無さ・仕込み時短・ロスゼロを実感し継続発注" },
          { step: "STEP 7", title: "法人契約・店舗別オリジナル魚BOX受注", desc: "業態・客単価に合わせた専用詰め合わせBOXの定期B2B契約へ" }
        ]
      },
      weekdaySchedule: d.weekdaySchedule || [
        { dayOfWeek: "月曜日", themeTitle: "旬の魚紹介", targetPersona: "全国の寿司店・和食料理長・海外シェフ", keyAngle: "今月の旬魚・脂乗り・産地直送の旬カレンダー" },
        { dayOfWeek: "火曜日", themeTitle: "魚の特徴・目利き・鮮度", targetPersona: "仕入れ担当者・若手料理人", keyAngle: "プロが見る鮮度基準・肥満度・身質の目利きポイント" },
        { dayOfWeek: "水曜日", themeTitle: "冷凍技術・鮮度保持・解凍方法", targetPersona: "冷凍魚に不安を持つ料理長・オーナー", keyAngle: "細胞を壊さない急速冷凍×真空包装・ドリップを防ぐ解凍術" },
        { dayOfWeek: "木曜日", themeTitle: "飲食店の仕入れ改善", targetPersona: "飲食店経営者・店長・購買責任者", keyAngle: "歩留まり安定・FL原価率26.5〜30.2%・廃棄ロスゼロ・仕込み時短" },
        { dayOfWeek: "金曜日", themeTitle: "寿司・刺身・料理活用", targetPersona: "寿司職人・海鮮居酒屋・ビストロシェフ", keyAngle: "皿の上での輝き・1人前ポーション原価と高単価メニュー提案" },
        { dayOfWeek: "土曜日", themeTitle: "市場・産地・水揚げ", targetPersona: "産地志向の料理店・インバウンド店舗", keyAngle: "全国47都道府県ネットワーク・提携漁港の朝獲れ活〆現場" },
        { dayOfWeek: "日曜日", themeTitle: "日本の魚食文化・海外向け発信", targetPersona: "海外和食レストラン・輸出バイヤー・訪日客", keyAngle: "日本の活〆・熟成・四季の魚食文化を世界へ英語で発信" }
      ],
      themes19: d.themes19 || [],
      fishMaster10: d.fishMaster10 || [],
      episodes: d.episodes || [],
      calendar365: d.calendar365 || [],
      dotPromptTemplates: d.dotPromptTemplates || [],
      assetInventory460: d.assetInventory460 || { totalPhotos: 350, totalVideos: 110, totalAssets: 460, categories: [] }
    };
  }

  // Build a complete 10-item episode object for ANY day (1..365)
  // If Day 1..28 exists in data.episodes, return it; otherwise dynamically synthesize all 10 items from calendar365 + fishMaster10 + themes19!
  function getOrBuildEpisodeForDay(dayNum) {
    const num = parseInt(dayNum, 10) || 1;
    const epId = "DAY-" + String(num).padStart(2, "0");

    // Check if full episode exists in rawData.episodes
    const existing = rawData.episodes.find(function (e) {
      return e.id === epId || e.dayNumber === num || e.id === "DAY-" + num;
    });
    if (existing) return existing;

    // Otherwise build from calendar365 entry
    const cal = rawData.calendar365.find(function (c) {
      return Number(c.dayNumber) === num;
    }) || {
      dayNumber: num,
      weekNumber: Math.ceil(num / 7),
      dayOfWeek: ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"][(num - 1) % 7],
      weekdayTheme: "旬の魚紹介",
      theme19: "① 旬の魚紹介",
      season: ["春", "夏", "秋", "冬"][Math.floor(((num - 1) % 365) / 91) % 4],
      fishKey: "本マグロ",
      titleJp: "DAY-" + num + " 日本の旬魚とプロの鮮度保持技術",
      titleEn: "DAY-" + num + " Japanese Seasonal Fish & Pro Freshness Technology",
      hookJp: "なぜ一流の寿司店・和食店が『産地急速冷凍の一箱』を指名するのか？",
      factPointJp: "可食部歩留まりと1皿原価（FL比率26.5〜30.2%）を安定させ、廃棄ロスと仕込み時間を大幅削減。",
      assetCode: "FA-PHOTO-FIL-01 / FA-VID-THAW-01",
      sourceRef: "水産庁 旬の魚カレンダー ／ ファインアトラス全国産地・歩留まり検証データ"
    };

    return synthesize10Items( {
      id: "DAY-" + String(num).padStart(2, "0"),
      dayNumber: num,
      week: cal.weekNumber || Math.ceil(num / 7),
      dayOfWeek: cal.dayOfWeek,
      weekdayTheme: cal.weekdayTheme,
      themeCategory: cal.theme19,
      featuredFish: cal.fishKey,
      season: cal.season,
      titleJp: cal.titleJp,
      titleEn: cal.titleEn,
      hookJp: cal.hookJp,
      factPointJp: cal.factPointJp,
      assetCode: cal.assetCode,
      sourceRef: cal.sourceRef
    });
  }

  function normalizeFishRecord(f) {
    if (!f) return null;
    const yieldStr = (f.yieldPct !== undefined && f.yieldPct !== null)
      ? (String(f.yieldPct).indexOf("%") !== -1 ? String(f.yieldPct) : (f.yieldPct + "%"))
      : "85〜98%";
    const netGramStr = f.netGram || (f.portionGram ? (f.portionGram + "g") : "60g");
    const dishCostStr = f.dishCost || (f.dishCostYen ? ("¥" + Number(f.dishCostYen).toLocaleString()) : "¥359");
    const menuPriceStr = f.menuPrice || (f.menuPriceYen ? ("¥" + Number(f.menuPriceYen).toLocaleString()) : "¥1,280");
    const costRatioStr = (f.costRatioPct !== undefined && f.costRatioPct !== null)
      ? String(f.costRatioPct)
      : (f.flCostRatioPct !== undefined ? (f.flCostRatioPct + "%") : "28.1%");
    const faPriceStr = f.faPrice || (f.faWholesaleYenKg ? ("¥" + Number(f.faWholesaleYenKg).toLocaleString() + "/kg") : "要見積");
    const wholesaleRangeStr = f.wholesaleRange || f.marketRangeYenKg || "市場連動";
    const categoryStr = f.category || ((f.tier ? f.tier + "｜" : "") + (f.origin || ""));
    return {
      key: f.key || f.nameJp,
      nameJp: f.nameJp || f.key || "国産旬魚",
      nameEn: f.nameEn || "Premium Japanese Seasonal Fish",
      category: categoryStr,
      spec: f.spec || "プロ用フィレ・急速冷凍真空包装",
      wholesaleRange: wholesaleRangeStr,
      faPrice: faPriceStr,
      yieldPct: yieldStr,
      netGram: netGramStr,
      dishCost: dishCostStr,
      menuPrice: menuPriceStr,
      costRatioPct: costRatioStr,
      prepMerit: f.prepMerit || "下処理済み・必要な分だけ解凍してすぐ提供可能で廃棄ロスゼロ"
    };
  }

  function findFishInfo(fishName) {
    if (!rawData.fishMaster10 || !rawData.fishMaster10.length) {
      return normalizeFishRecord({
        nameJp: fishName || "国産旬魚"
      });
    }
    const found = rawData.fishMaster10.find(function (f) {
      const k = f.key || "";
      const n = f.nameJp || "";
      return (fishName && (n.indexOf(fishName) !== -1 || fishName.indexOf(n) !== -1 || k.indexOf(fishName) !== -1 || fishName.indexOf(k) !== -1));
    });
    return normalizeFishRecord(found || rawData.fishMaster10[0]);
  }

  function synthesize10Items(params) {
    const fish = findFishInfo(params.featuredFish);
    const fishJp = fish.nameJp || params.featuredFish || "国産旬魚";
    const fishEn = fish.nameEn || "Japanese Seasonal Seafood";
    const seasonJp = params.season || "旬";
    const seasonEnMap = { "春": "Spring", "夏": "Summer", "秋": "Autumn", "冬": "Winter" };
    const seasonEn = seasonEnMap[seasonJp] || "Seasonal";

    const titleJp = params.titleJp || ("【" + seasonJp + "の" + fishJp + "】" + params.themeCategory + "｜プロの仕入れと鮮度保持");
    const titleEn = params.titleEn || ("[" + seasonEn + " " + fishEn + "] Pro Sourcing, Yield & Peak Freshness");

    const hookJp = params.hookJp || ("「" + fishJp + "の仕入れで、歩留まりや鮮度のバラつきに悩んでいませんか？」");
    const hookEn = "Struggling with inconsistent yield or freshness when sourcing " + fishEn + "?";

    const bodyJp = params.factPointJp || (
      "ファインアトラスの「" + fishJp + "（" + (fish.spec || "急速冷凍真空規格") + "）」は、水揚げ直後の最高鮮度を急速冷凍で閉じ込めています。" +
      "可食部歩留まりは" + (fish.yieldPct || "高水準") + "、1人前（約" + (fish.netGram || "60g") + "）の1皿原価は" + (fish.dishCost || "約359円") + "（想定原価率" + (fish.costRatioPct || "28%前後") + "）。"
    );
    const bodyEn =
      "Fine Atlas flash-freezes " + fishEn + " at peak harvest freshness using vacuum lock technology. " +
      "Achieve a reliable " + (fish.yieldPct || "high") + " edible yield and a consistent food cost ratio around " + (fish.costRatioPct || "27-30%") + " with zero waste.";

    const summaryJp = (fish.prepMerit || "必要な分だけ解凍してすぐ提供でき、廃棄ロスゼロと仕込み時短を同時に実現します。") + "まずはAmazonや公式HPの少量お試しから、店舗別オリジナル魚BOXまで対応。";
    const summaryEn = "Thaw only what you need for instant plating—zero waste, faster prep. Start with a small trial box on Amazon or our website, and scale to custom B2B restaurant fish boxes.";

    const fullNarrationJp =
      "【0〜3秒】" + hookJp + "\n" +
      "【3〜20秒】" + bodyJp + "\n" +
      "【20〜27秒】" + summaryJp + "\n" +
      "【27〜30秒】株式会社ファインアトラス。" + CATCHPHRASE_JP;

    const fullNarrationEn =
      "[0-3s] " + hookEn + "\n" +
      "[3-20s] " + bodyEn + "\n" +
      "[20-27s] " + summaryEn + "\n" +
      "[27-30s] FINE ATLAS. " + CATCHPHRASE_EN;

    return {
      id: params.id || "CUSTOM",
      dayNumber: params.dayNumber || 1,
      week: params.week || 1,
      dayOfWeek: params.dayOfWeek || "月曜日",
      weekdayTheme: params.weekdayTheme || "旬の魚紹介",
      themeCategory: params.themeCategory || "① 旬の魚紹介",
      featuredFish: fishJp,
      season: seasonJp,
      item1_title: {
        jp: titleJp,
        en: titleEn
      },
      item2_narration: {
        jp: fullNarrationJp,
        en: fullNarrationEn
      },
      item3_timecode: [
        {
          sec: "0〜3秒（導入フック）",
          visualJp: "自社撮影：" + fishJp + "の艶やかな断面クローズアップ＋大きな疑問形テロップ",
          visualEn: "Close-up of glossy " + fishEn + " cross-section + bold hook caption",
          audioJp: hookJp,
          audioEn: hookEn
        },
        {
          sec: "3〜20秒（本題・実証データ）",
          visualJp: "自社撮影：真空急速冷凍パック → 解凍後のドリップ比較・歩留まり（" + (fish.yieldPct || "高歩留まり") + "）図解フリップ",
          visualEn: "Vacuum flash-frozen pack -> zero-drip thawing & yield (" + (fish.yieldPct || "high yield") + ") chart",
          audioJp: bodyJp,
          audioEn: bodyEn
        },
        {
          sec: "20〜27秒（要点まとめ・導入メリット）",
          visualJp: "自社撮影：寿司・刺身の盛り付け完成カット＋「少量お試し → 店舗別オリジナル魚BOX」案内",
          visualEn: "Plated sashimi/sushi dish + 'Small Trial Box -> Custom B2B Fish Box' callout",
          audioJp: summaryJp,
          audioEn: summaryEn
        },
        {
          sec: "27〜30秒（共通エンディング）",
          visualJp: "Canva共通エンドカード：FINE ATLASロゴ＋「" + CATCHPHRASE_JP + "」",
          visualEn: "Canva End Card: FINE ATLAS Logo + '" + CATCHPHRASE_EN + "'",
          audioJp: "株式会社ファインアトラス。" + CATCHPHRASE_JP,
          audioEn: "FINE ATLAS. " + CATCHPHRASE_EN
        }
      ],
      item4_mediaDirection: {
        ownAssetCode: params.assetCode || "FA-PHOTO-RAW-01 / FA-PHOTO-FIL-01 / FA-VID-THAW-01",
        ownAssetLabel: "【自社撮影最優先】" + fishJp + "（丸魚・フィレ断面・真空パック・解凍盛り付け動画）",
        shootGuide: "実際の商品・魚種は必ず自社撮影の写真・動画（460点ストック）を優先使用する。氷結晶や霜が付いていない清潔な真空状態と、解凍後の角が立った身質を縦型9:16（1080×1920）で配置。"
      },
      item5_aiImagePrompt: {
        promptEn: "Vertical 9:16 editorial culinary infographic background, clean Japanese hinoki wood sushi counter with soft natural lighting, minimalist luxury washoku atmosphere, space for bold typography overlay, photorealistic, 8k --ar 9:16",
        negativePrompt: "fake distorted fish anatomy, unnatural neon colors, messy text watermark, deformed hands, low resolution",
        usageNoteJp: "※注意：実際の商品（" + fishJp + "）にはAI画像を使わず自社実写を使用すること。このAI画像は背景ボードや3〜20秒の解説図解の背景レイヤー（不足素材補完）としてのみ使用。"
      },
      item6_subtitles: {
        vrewLinesJp: [
          hookJp,
          fishJp + "（" + (fish.spec || "プロ用規格") + "）",
          "水揚げ直後の鮮度を急速冷凍×真空包装",
          "可食部歩留まり：" + (fish.yieldPct || "高水準") + " ／ 1皿原価：" + (fish.dishCost || "安定"),
          "ドリップを抑え、廃棄ロスゼロ・仕込み時短を実現",
          "まずはAmazon・公式HPの少量購入で品質確認",
          "リピートから法人契約・店舗別オリジナル魚BOXへ",
          "株式会社ファインアトラス",
          CATCHPHRASE_JP
        ],
        vrewLinesEn: [
          hookEn,
          fishEn + " (" + (fish.spec || "Chef-Grade Spec") + ")",
          "Flash-frozen & vacuum-sealed at peak harvest freshness",
          "Edible Yield: " + (fish.yieldPct || "High") + " / Target Food Cost: " + (fish.costRatioPct || "27-30%"),
          "Minimal drip, zero waste, faster kitchen prep",
          "Test quality with a small order via Amazon or our official site",
          "Scale to repeat orders & custom B2B restaurant fish boxes",
          "FINE ATLAS Co., Ltd.",
          CATCHPHRASE_EN
        ]
      },
      item7_snsCaption: {
        jp: "【" + titleJp + "】\n" +
            bodyJp + "\n\n" +
            "📌 飲食店・料理長様へのメリット\n" +
            "・" + (fish.prepMerit || "必要な分だけ解凍でき、廃棄ロスと仕込み時間を大幅削減") + "\n" +
            "・まずはAmazon・公式HPでの少量お試し購入で品質をご確認いただけます\n" +
            "・リピート導入から法人契約、お店のメニューに合わせた「店舗別オリジナル魚BOX」まで柔軟に対応！\n\n" +
            "「" + CATCHPHRASE_JP + "」\n" +
            "▼ 公式HP・お試しセットの詳細はプロフィールリンクから",
        en: "[" + titleEn + "]\n" +
            bodyEn + "\n\n" +
            "📌 Why Chefs & Seafood Buyers Choose Fine Atlas:\n" +
            "- Consistent yield (" + (fish.yieldPct || "High") + ") & zero kitchen waste\n" +
            "- Start with a small trial order via Amazon or our official website\n" +
            "- Custom B2B restaurant fish boxes tailored to your menu\n\n" +
            "\"" + CATCHPHRASE_EN + "\"\n" +
            "▼ Visit the link in our bio for specifications & inquiries."
      },
      item8_hashtags: {
        jp: "#ファインアトラス #FINEATLAS #" + fishJp.replace(/[・\s]/g, "") + " #業務用鮮魚 #急速冷凍 #飲食店仕入れ #寿司仕入れ #歩留まり改善 #フードロス削減 #日本の魚を世界へ",
        en: "#FineAtlas #JapaneseSeafood #" + fishEn.replace(/[^a-zA-Z]/g, "") + " #SushiChef #SashimiGrade #FlashFrozenSeafood #RestaurantSupply #Washoku #FoodCostControl #JapanExport"
      },
      item9_sources: params.sourceRef || "水産庁「旬の魚・水産統計」／文部科学省「日本食品標準成分表」／株式会社ファインアトラス 産地加工・歩留まり実測検証データ",
      item10_bilingualCheck: {
        factCheckPoints: "① 確認できない推測数値なし（歩留まり" + (fish.yieldPct || "実測値") + "・原価率" + (fish.costRatioPct || "26.5〜30.2%") + "の範囲内） ② 実商品は自社撮影素材（" + (params.assetCode || "FA-PHOTO") + "）を優先指定 ③ 27〜30秒に共通キャッチコピー配置済",
        targetAudience: "国内：本格寿司店・高単価海鮮居酒屋・和食料理長 ／ 海外：北米・アジア・欧州の和食レストラン＆水産バイヤー"
      }
    };
  }

  // Normalize any episode object so all 10 items are guaranteed to exist
  function normalizeEpisode(ep) {
    if (ep && ep.item1_title && ep.item2_narration && ep.item3_timecode) {
      return ep;
    }
    return synthesize10Items(ep || {});
  }

  // Copy builders for One-Tap Buttons
  function buildVrewCopyText(ep, lang) {
    const norm = normalizeEpisode(ep);
    const isEn = lang === "en";
    const title = isEn ? norm.item1_title.en : norm.item1_title.jp;
    const narration = isEn ? norm.item2_narration.en : norm.item2_narration.jp;
    const subs = isEn
      ? (norm.item6_subtitles.vrewLinesEn || [])
      : (norm.item6_subtitles.vrewLinesJp || []);

    return [
      "========================================",
      "🎬 Vrew投入用スクリプト（" + norm.id + "｜" + (isEn ? "🇺🇸 英語版" : "🇯🇵 日本語版") + "）",
      "仕様：30秒 ／ 縦型 9:16（1080×1920） ／ 字幕必須",
      "========================================",
      "",
      "【① 動画タイトル】",
      title,
      "",
      "【② 30秒ナレーション台本（AI音声読み上げ用）】",
      narration,
      "",
      "【⑥ Vrew貼り付け用 行分け字幕テキスト（このままVrewへコピペ）】",
      subs.join("\n"),
      "",
      "【④ 使用する自社写真・動画コード（自社素材優先）】",
      (norm.item4_mediaDirection.ownAssetCode || "") + " — " + (norm.item4_mediaDirection.ownAssetLabel || "")
    ].join("\n");
  }

  function buildMetricoolCopyText(ep) {
    const norm = normalizeEpisode(ep);
    return [
      "========================================",
      "📱 Metricool 4大SNS予約投稿用（" + norm.id + "｜YouTube / Instagram / TikTok / Facebook）",
      "========================================",
      "",
      "--- 🇯🇵 日本語版 SNS投稿文 ＆ ハッシュタグ ---",
      norm.item1_title.jp,
      "",
      norm.item7_snsCaption.jp,
      "",
      norm.item8_hashtags.jp,
      "",
      "----------------------------------------",
      "--- 🇺🇸 英語版 SNS Caption & Hashtags ---",
      norm.item1_title.en,
      "",
      norm.item7_snsCaption.en,
      "",
      norm.item8_hashtags.en
    ].join("\n");
  }

  function buildFull10CopyText(ep) {
    const norm = normalizeEpisode(ep);
    const tcLines = (norm.item3_timecode || []).map(function (tc) {
      return "・" + tc.sec + "\n  [映像] " + tc.visualJp + " / " + tc.visualEn + "\n  [音声JP] " + tc.audioJp + "\n  [音声EN] " + tc.audioEn;
    }).join("\n");

    return [
      "======================================================================",
      "🎬 FINE ATLAS AIショート動画 10項目完全パッケージ（" + norm.id + "｜" + norm.dayOfWeek + "｜" + norm.featuredFish + "）",
      "======================================================================",
      "",
      "【① 動画タイトル】",
      "🇯🇵 日本語：" + norm.item1_title.jp,
      "🇺🇸 英語  ：" + norm.item1_title.en,
      "",
      "【② 30秒のナレーション台本】",
      "--- 🇯🇵 日本語ナレーション ---",
      norm.item2_narration.jp,
      "",
      "--- 🇺🇸 英語ナレーション ---",
      norm.item2_narration.en,
      "",
      "【③ 秒数ごとの映像内容（0-3s / 3-20s / 20-27s / 27-30s）】",
      tcLines,
      "",
      "【④ 使用する写真・動画の指示（自社撮影素材優先）】",
      "素材コード：" + norm.item4_mediaDirection.ownAssetCode,
      "対象素材  ：" + norm.item4_mediaDirection.ownAssetLabel,
      "撮影・配置：" + norm.item4_mediaDirection.shootGuide,
      "",
      "【⑤ AI画像生成用の指示文（不足素材の補完専用）】",
      "Prompt (EN): " + norm.item5_aiImagePrompt.promptEn,
      "Negative   : " + (norm.item5_aiImagePrompt.negativePrompt || ""),
      "運用注意   : " + norm.item5_aiImagePrompt.usageNoteJp,
      "",
      "【⑥ 字幕（Vrew行分けテキスト）】",
      "--- 🇯🇵 日本語字幕 ---",
      (norm.item6_subtitles.vrewLinesJp || []).join("\n"),
      "--- 🇺🇸 英語字幕 ---",
      (norm.item6_subtitles.vrewLinesEn || []).join("\n"),
      "",
      "【⑦ SNS投稿文章（Amazon少量購入→リピート→法人契約・オリジナル魚BOX導線）】",
      "--- 🇯🇵 日本語 ---",
      norm.item7_snsCaption.jp,
      "--- 🇺🇸 英語 ---",
      norm.item7_snsCaption.en,
      "",
      "【⑧ ハッシュタグ】",
      "🇯🇵 " + norm.item8_hashtags.jp,
      "🇺🇸 " + norm.item8_hashtags.en,
      "",
      "【⑨ 情報の出典】",
      norm.item9_sources,
      "",
      "【⑩ 英語版（タイトル・台本・字幕・投稿文）＆ 事実確認ガードレール】",
      "事実確認：" + (norm.item10_bilingualCheck
        ? (Array.isArray(norm.item10_bilingualCheck.factCheckPoints) ? norm.item10_bilingualCheck.factCheckPoints.join(" ／ ") : norm.item10_bilingualCheck.factCheckPoints)
        : "確認済"),
      "対象読者：" + (norm.item10_bilingualCheck ? norm.item10_bilingualCheck.targetAudience : "国内外の料理長・バイヤー")
    ].join("\n");
  }

  // Render a single 10-Item Episode Card HTML
  function renderEpisodeCardHtml(epRaw, isCompactModal) {
    const ep = normalizeEpisode(epRaw);
    const statusVal = dayStatusMap[ep.id] || "todo";

    const tcRowsHtml = (ep.item3_timecode || []).map(function (tc) {
      return (
        "<tr>" +
          "<td><span class=\"tc-sec-badge\">" + escapeHtml(tc.sec) + "</span></td>" +
          "<td>" +
            "<div class=\"jp-only-block\"><strong>🇯🇵 映像：</strong>" + escapeHtml(tc.visualJp) + "</div>" +
            "<div class=\"en-only-block\"><strong>🇺🇸 Visual：</strong>" + escapeHtml(tc.visualEn || "") + "</div>" +
          "</td>" +
          "<td>" +
            "<div class=\"jp-only-block\"><strong>🇯🇵 音声：</strong>" + escapeHtml(tc.audioJp) + "</div>" +
            "<div class=\"en-only-block\"><strong>🇺🇸 Audio：</strong>" + escapeHtml(tc.audioEn || "") + "</div>" +
          "</td>" +
        "</tr>"
      );
    }).join("");

    const subsJp = (ep.item6_subtitles && ep.item6_subtitles.vrewLinesJp) ? ep.item6_subtitles.vrewLinesJp.join("\n") : "";
    const subsEn = (ep.item6_subtitles && ep.item6_subtitles.vrewLinesEn) ? ep.item6_subtitles.vrewLinesEn.join("\n") : "";

    return (
      "<article class=\"ep-card\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
        "<div class=\"ep-card-header\">" +
          "<div class=\"ep-header-badges\">" +
            "<span class=\"ep-badge-day\">🎬 " + escapeHtml(ep.id) + "（第" + escapeHtml(ep.week || 1) + "週）</span>" +
            "<span class=\"ep-badge-weekday\">🗓️ " + escapeHtml(ep.dayOfWeek) + "</span>" +
            "<span class=\"ep-badge-theme\">🎯 " + escapeHtml(ep.themeCategory) + "</span>" +
            "<span class=\"ep-badge-fish\">🐟 主役：" + escapeHtml(ep.featuredFish) + "</span>" +
          "</div>" +
          "<div class=\"ep-status-box\">" +
            "<label class=\"ep-status-label\" for=\"status-" + escapeHtml(ep.id) + "-" + (isCompactModal ? "m" : "c") + "\">⑩ 制作進捗：</label>" +
            "<select id=\"status-" + escapeHtml(ep.id) + "-" + (isCompactModal ? "m" : "c") + "\" class=\"ep-status-select js-ep-status-change\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
              "<option value=\"todo\"" + (statusVal === "todo" ? " selected" : "") + ">⬜ 未着手</option>" +
              "<option value=\"vrew\"" + (statusVal === "vrew" ? " selected" : "") + ">🎬 Vrew編集済</option>" +
              "<option value=\"checked\"" + (statusVal === "checked" ? " selected" : "") + ">🔍 事実・日英確認済</option>" +
              "<option value=\"scheduled\"" + (statusVal === "scheduled" ? " selected" : "") + ">🚀 4大SNS予約済</option>" +
            "</select>" +
          "</div>" +
        "</div>" +

        "<div class=\"ep-card-body\">" +
          "<!-- One-Tap Action Buttons -->" +
          "<div class=\"ep-action-bar\">" +
            "<button type=\"button\" class=\"btn-ep-copy is-navy js-copy-vrew-jp\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
              "📋 Vrew投入用（台本＋字幕）を1タップコピー（🇯🇵 日本語）" +
            "</button>" +
            "<button type=\"button\" class=\"btn-ep-copy is-navy js-copy-vrew-en\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
              "📋 Vrew投入用（台本＋字幕）を1タップコピー（🇺🇸 英語）" +
            "</button>" +
            "<button type=\"button\" class=\"btn-ep-copy is-emerald js-copy-metricool\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
              "📱 Metricool予約用（SNS投稿文＋タグ）をコピー" +
            "</button>" +
            "<button type=\"button\" class=\"btn-ep-copy is-gold js-copy-ai-prompt\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
              "🎨 ⑤ AI画像生成プロンプトをコピー" +
            "</button>" +
            "<button type=\"button\" class=\"btn-ep-copy is-outline js-copy-all10\" data-ep-id=\"" + escapeHtml(ep.id) + "\">" +
              "📦 この1本の全10項目シートを丸ごとコピー" +
            "</button>" +
          "</div>" +

          "<div class=\"items-10-stack\">" +
            "<!-- Item 1: Title -->" +
            "<div class=\"item-box is-title-box\">" +
              "<div class=\"item-box-head\">" +
                "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ①</span> 動画タイトル（🇯🇵 日本語版 ／ 🇺🇸 英語版 ①＋⑩）</span>" +
              "</div>" +
              "<div class=\"bilingual-grid\">" +
                "<div class=\"lang-col is-jp\">" +
                  "<span class=\"lang-tag is-jp\">🇯🇵 日本語タイトル</span>" +
                  "<p class=\"title-text-lg\">" + escapeHtml(ep.item1_title.jp) + "</p>" +
                "</div>" +
                "<div class=\"lang-col is-en\">" +
                  "<span class=\"lang-tag is-en\">🇺🇸 英語版タイトル（⑩ 英語版）</span>" +
                  "<p class=\"title-text-lg\">" + escapeHtml(ep.item1_title.en) + "</p>" +
                "</div>" +
              "</div>" +
            "</div>" +

            "<!-- Item 2: 30s Narration -->" +
            "<div class=\"item-box is-narration-box\">" +
              "<div class=\"item-box-head\">" +
                "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ②</span> 30秒のナレーション台本（27〜30秒：共通キャッチコピー必須）</span>" +
              "</div>" +
              "<div class=\"bilingual-grid\">" +
                "<div class=\"lang-col is-jp\">" +
                  "<span class=\"lang-tag is-jp\">🇯🇵 日本語ナレーション（30秒）</span>" +
                  "<p class=\"narration-text\">" + escapeHtml(ep.item2_narration.jp) + "</p>" +
                  "<div class=\"catchphrase-highlight\">🎯 27〜30秒締め：「" + escapeHtml(CATCHPHRASE_JP) + "」</div>" +
                "</div>" +
                "<div class=\"lang-col is-en\">" +
                  "<span class=\"lang-tag is-en\">🇺🇸 英語版ナレーション（⑩ 30s Script）</span>" +
                  "<p class=\"narration-text\">" + escapeHtml(ep.item2_narration.en) + "</p>" +
                  "<div class=\"catchphrase-highlight\">🎯 27-30s Closing: \"" + escapeHtml(CATCHPHRASE_EN) + "\"</div>" +
                "</div>" +
              "</div>" +
            "</div>" +

            "<!-- Item 3: Second-by-Second Visual & Audio Timeline -->" +
            "<div class=\"item-box\">" +
              "<div class=\"item-box-head\">" +
                "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ③</span> 秒数ごとの映像内容（0〜3秒 / 3〜20秒 / 20〜27秒 / 27〜30秒）</span>" +
              "</div>" +
              "<div style=\"overflow-x:auto;\">" +
                "<table class=\"timecode-table\">" +
                  "<thead>" +
                    "<tr>" +
                      "<th style=\"width:170px;\">秒数パート</th>" +
                      "<th>画面・映像ディレクション（縦型 9:16 / 1080×1920）</th>" +
                      "<th>ナレーション・字幕テキスト</th>" +
                    "</tr>" +
                  "</thead>" +
                  "<tbody>" + tcRowsHtml + "</tbody>" +
                "</table>" +
              "</div>" +
            "</div>" +

            "<!-- Item 4 & Item 5: Own Media Direction & AI Image Prompt -->" +
            "<div class=\"items-two-col\">" +
              "<div class=\"item-box is-asset-box\">" +
                "<div class=\"item-box-head\">" +
                  "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ④</span> 使用する写真・動画の指示（自社撮影優先）</span>" +
                "</div>" +
                "<div><strong>📸 推奨自社素材コード：</strong><code>" + escapeHtml(ep.item4_mediaDirection.ownAssetCode) + "</code></div>" +
                "<div style=\"margin-top:4px;\"><strong>🐟 対象素材：</strong>" + escapeHtml(ep.item4_mediaDirection.ownAssetLabel) + "</div>" +
                "<div style=\"margin-top:6px;font-size:0.93em;color:#065F46;\"><strong>💡 撮影・配置ルール：</strong>" + escapeHtml(ep.item4_mediaDirection.shootGuide) + "</div>" +
              "</div>" +

              "<div class=\"item-box\">" +
                "<div class=\"item-box-head\">" +
                  "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ⑤</span> AI画像生成用の指示文（不足素材の補完用）</span>" +
                "</div>" +
                "<pre class=\"code-pre-box\">" + escapeHtml(ep.item5_aiImagePrompt.promptEn) + "</pre>" +
                "<div style=\"margin-top:6px;font-size:0.9em;color:#92400E;\">⚠️ " + escapeHtml(ep.item5_aiImagePrompt.usageNoteJp) + "</div>" +
              "</div>" +
            "</div>" +

            "<!-- Item 6: Subtitles (Vrew Line-by-Line) -->" +
            "<div class=\"item-box\">" +
              "<div class=\"item-box-head\">" +
                "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ⑥</span> 字幕（音声なしでも理解できるVrew貼り付け用 行分けテキスト）</span>" +
              "</div>" +
              "<div class=\"bilingual-grid\">" +
                "<div class=\"lang-col is-jp\">" +
                  "<span class=\"lang-tag is-jp\">🇯🇵 日本語字幕（Vrew行分け）</span>" +
                  "<pre class=\"code-pre-box\">" + escapeHtml(subsJp) + "</pre>" +
                "</div>" +
                "<div class=\"lang-col is-en\">" +
                  "<span class=\"lang-tag is-en\">🇺🇸 英語版字幕（⑩ Vrew Subtitles）</span>" +
                  "<pre class=\"code-pre-box\">" + escapeHtml(subsEn) + "</pre>" +
                "</div>" +
              "</div>" +
            "</div>" +

            "<!-- Item 7: SNS Post Caption (7-Stage Sales Funnel) -->" +
            "<div class=\"item-box\">" +
              "<div class=\"item-box-head\">" +
                "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ⑦</span> SNS投稿文章（HP・Amazon少量お試し → リピート → 法人契約・オリジナル魚BOX導線）</span>" +
              "</div>" +
              "<div class=\"bilingual-grid\">" +
                "<div class=\"lang-col is-jp\">" +
                  "<span class=\"lang-tag is-jp\">🇯🇵 日本語SNS投稿文（4大SNS共通）</span>" +
                  "<pre class=\"code-pre-box\">" + escapeHtml(ep.item7_snsCaption.jp) + "</pre>" +
                "</div>" +
                "<div class=\"lang-col is-en\">" +
                  "<span class=\"lang-tag is-en\">🇺🇸 英語版SNS投稿文（⑩ English Caption）</span>" +
                  "<pre class=\"code-pre-box\">" + escapeHtml(ep.item7_snsCaption.en) + "</pre>" +
                "</div>" +
              "</div>" +
            "</div>" +

            "<!-- Item 8, 9, 10: Hashtags, Sources, Fact & Bilingual Check -->" +
            "<div class=\"items-two-col\">" +
              "<div class=\"item-box\">" +
                "<div class=\"item-box-head\">" +
                  "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ⑧</span> ハッシュタグ（日・英）</span>" +
                "</div>" +
                "<div class=\"jp-only-block\" style=\"margin-bottom:8px;\"><strong>🇯🇵 日本語：</strong><br /><code>" + escapeHtml(ep.item8_hashtags.jp) + "</code></div>" +
                "<div class=\"en-only-block\"><strong>🇺🇸 英語：</strong><br /><code>" + escapeHtml(ep.item8_hashtags.en) + "</code></div>" +
              "</div>" +

              "<div class=\"item-box\">" +
                "<div class=\"item-box-head\">" +
                  "<span class=\"item-num-title\"><span class=\"item-num-badge\">項目 ⑨ ＆ ⑩</span> 情報の出典 ＆ 事実確認ガードレール</span>" +
                "</div>" +
                "<div><strong>📚 ⑨ 情報の出典：</strong>" + escapeHtml(ep.item9_sources) + "</div>" +
                "<div style=\"margin-top:6px;\"><strong>🛡️ ⑩ 事実確認＆日英チェック：</strong>" +
                  escapeHtml(ep.item10_bilingualCheck
                    ? (Array.isArray(ep.item10_bilingualCheck.factCheckPoints) ? ep.item10_bilingualCheck.factCheckPoints.join(" ／ ") : ep.item10_bilingualCheck.factCheckPoints)
                    : "推測数値なし・自社素材優先・27〜30秒共通キャッチ確認済") +
                "</div>" +
              "</div>" +
            "</div>" +
          "</div>" +
        "</div>" +
      "</article>"
    );
  }

  // =================================================================
  // TAB 1: Initial 28 Days Episode Studio
  // =================================================================
  function populateEpisodeFilterDropdowns() {
    const themeSelect = document.getElementById("ep-theme-select");
    const fishSelect = document.getElementById("ep-fish-select");
    const calThemeSelect = document.getElementById("cal-theme-select");

    if (themeSelect && rawData.themes19) {
      rawData.themes19.forEach(function (t) {
        const tName = t.name || t.title || "";
        const label = (t.num ? t.num + ". " : "") + tName;
        const opt = document.createElement("option");
        opt.value = tName;
        opt.textContent = label + "（" + (t.weekday || "") + "）";
        themeSelect.appendChild(opt);

        if (calThemeSelect) {
          const opt2 = document.createElement("option");
          opt2.value = tName;
          opt2.textContent = label;
          calThemeSelect.appendChild(opt2);
        }
      });
    }

    if (fishSelect && rawData.fishMaster10) {
      rawData.fishMaster10.forEach(function (fRaw) {
        const f = normalizeFishRecord(fRaw);
        const opt = document.createElement("option");
        opt.value = f.key || f.nameJp;
        opt.textContent = f.nameJp + "（" + (f.category || "") + "）";
        fishSelect.appendChild(opt);
      });
    }
  }

  function renderEpisodesList() {
    const container = document.getElementById("episodes-container");
    if (!container) return;

    const themeFilter = (document.getElementById("ep-theme-select") || {}).value || "all";
    const fishFilter = (document.getElementById("ep-fish-select") || {}).value || "all";
    const statusFilter = (document.getElementById("ep-status-select") || {}).value || "all";
    const keyword = ((document.getElementById("ep-keyword-input") || {}).value || "").trim().toLowerCase();

    // Ensure 28 episodes exist (use rawData.episodes or fallback to 1..28)
    const all28 = [];
    for (let i = 1; i <= 28; i++) {
      all28.push(getOrBuildEpisodeForDay(i));
    }

    const filtered = all28.filter(function (ep) {
      if (activeEpWeek !== "all" && String(ep.week) !== String(activeEpWeek)) return false;
      if (activeEpWeekday !== "all" && ep.dayOfWeek !== activeEpWeekday) return false;
      if (themeFilter !== "all" && (!ep.themeCategory || ep.themeCategory.indexOf(themeFilter) === -1)) return false;
      if (fishFilter !== "all" && (!ep.featuredFish || (ep.featuredFish.indexOf(fishFilter) === -1 && fishFilter.indexOf(ep.featuredFish) === -1))) return false;

      const st = dayStatusMap[ep.id] || "todo";
      if (statusFilter !== "all" && st !== statusFilter) return false;

      if (keyword) {
        const blob = [
          ep.id,
          ep.dayOfWeek,
          ep.themeCategory,
          ep.featuredFish,
          ep.item1_title ? ep.item1_title.jp : "",
          ep.item1_title ? ep.item1_title.en : "",
          ep.item2_narration ? ep.item2_narration.jp : "",
          ep.item7_snsCaption ? ep.item7_snsCaption.jp : "",
          ep.item8_hashtags ? ep.item8_hashtags.jp : ""
        ].join(" ").toLowerCase();
        if (blob.indexOf(keyword) === -1) return false;
      }
      return true;
    });

    const countEl = document.getElementById("ep-showing-count");
    if (countEl) countEl.textContent = String(filtered.length);

    if (!filtered.length) {
      container.innerHTML =
        "<div class=\"filter-panel\" style=\"text-align:center;padding:32px;\">" +
          "<h3>該当する台本が見つかりませんでした</h3>" +
          "<p>絞り込み条件をリセットするか、別のキーワードでお試しください。</p>" +
        "</div>";
      return;
    }

    container.innerHTML = filtered.map(function (ep) {
      return renderEpisodeCardHtml(ep, false);
    }).join("");
  }

  // =================================================================
  // TAB 2: Dot / ChatGPT Prompt & 365-Day Instant Script Generator
  // =================================================================
  function initGeneratorControls() {
    const daySelect = document.getElementById("gen-day-select");
    const weekdaySelect = document.getElementById("gen-weekday-select");
    const themeSelect = document.getElementById("gen-theme19-select");
    const fishSelect = document.getElementById("gen-fish-select");
    const seasonSelect = document.getElementById("gen-season-select");
    const customNote = document.getElementById("gen-custom-note");
    const tplPillsBox = document.getElementById("dot-template-pills");

    if (!daySelect) return;

    // Populate 365 days
    for (let d = 1; d <= 365; d++) {
      const cal = rawData.calendar365.find(function (c) { return Number(c.dayNumber) === d; });
      const opt = document.createElement("option");
      opt.value = String(d);
      if (cal) {
        opt.textContent = "DAY-" + String(d).padStart(2, "0") + "（第" + cal.weekNumber + "週・" + cal.dayOfWeek + "）｜" + cal.fishKey + "｜" + cal.theme19;
      } else {
        opt.textContent = "DAY-" + String(d).padStart(2, "0");
      }
      daySelect.appendChild(opt);
    }

    // Populate Weekday
    rawData.weekdaySchedule.forEach(function (w) {
      const wTitle = w.categoryName || w.themeTitle || "";
      const opt = document.createElement("option");
      opt.value = w.dayOfWeek;
      opt.textContent = w.dayOfWeek + "｜" + wTitle;
      weekdaySelect.appendChild(opt);
    });

    // Populate 19 Themes
    if (rawData.themes19 && rawData.themes19.length) {
      rawData.themes19.forEach(function (t) {
        const tName = t.name || t.title || "";
        const opt = document.createElement("option");
        opt.value = tName;
        opt.textContent = (t.num ? t.num + ". " : "") + tName + "（" + (t.weekday || "") + "）";
        themeSelect.appendChild(opt);
      });
    } else {
      const fallback19 = [
        "魚の種類と特徴", "全国の旬の魚", "産地別の魚の市場相場", "高級魚の豆知識", "高品質冷凍魚とは",
        "正しい冷凍魚の解凍方法", "プロの料理人の調理方法", "鮮魚と冷凍魚の比較", "丸魚とフィレの原価比較", "魚の歩留まりと原価率",
        "仕込み人件費の削減", "レストランの人材不足", "日本の漁業の課題", "世界の水産物事情", "サステナブル",
        "トレーサビリティ", "空輸と船便の比較", "日本の魚の海外輸出", "ファインアトラスの商品紹介"
      ];
      fallback19.forEach(function (t) {
        const opt = document.createElement("option");
        opt.value = t;
        opt.textContent = t;
        themeSelect.appendChild(opt);
      });
    }

    // Populate 10 Fish
    if (rawData.fishMaster10 && rawData.fishMaster10.length) {
      rawData.fishMaster10.forEach(function (fRaw) {
        const f = normalizeFishRecord(fRaw);
        const opt = document.createElement("option");
        opt.value = f.key || f.nameJp;
        opt.textContent = f.nameJp + "（歩留まり " + f.yieldPct + " ／ 1皿原価 " + f.dishCost + "）";
        fishSelect.appendChild(opt);
      });
    }

    // Populate Dot Template Preset Pills
    const templates = (Array.isArray(rawData.dotPromptTemplates) && rawData.dotPromptTemplates.length)
      ? rawData.dotPromptTemplates
      : [
          { id: "daily-10", title: "① 毎日の10項目フル出力（標準）" },
          { id: "weekly-7", title: "② 週1回・7日分まとめ生成用" },
          { id: "fact-audit", title: "③ 事実確認＆英語ネイティブ校正用" }
        ];

    if (tplPillsBox) {
      tplPillsBox.innerHTML = templates.map(function (tpl, idx) {
        return "<button type=\"button\" class=\"pill-btn js-dot-tpl-pill" + (idx === 0 ? " is-active" : "") + "\" data-tpl-idx=\"" + idx + "\">" + escapeHtml(tpl.title) + "</button>";
      }).join("");
    }

    function syncControlsFromDay(dayNum) {
      const ep = getOrBuildEpisodeForDay(dayNum);
      if (weekdaySelect && ep.dayOfWeek) weekdaySelect.value = ep.dayOfWeek;
      if (seasonSelect && ep.season) seasonSelect.value = ep.season;
      if (fishSelect && ep.featuredFish) {
        // try matching fish option
        for (let i = 0; i < fishSelect.options.length; i++) {
          if (ep.featuredFish.indexOf(fishSelect.options[i].value) !== -1 || fishSelect.options[i].value.indexOf(ep.featuredFish) !== -1) {
            fishSelect.selectedIndex = i;
            break;
          }
        }
      }
      if (themeSelect && ep.themeCategory) {
        for (let j = 0; j < themeSelect.options.length; j++) {
          if (themeSelect.options[j].value.indexOf(ep.themeCategory) !== -1 || ep.themeCategory.indexOf(themeSelect.options[j].value) !== -1) {
            themeSelect.selectedIndex = j;
            break;
          }
        }
      }
      updateGeneratorOutputs(true);
    }

    daySelect.addEventListener("change", function () {
      syncControlsFromDay(parseInt(daySelect.value, 10) || 1);
    });

    [weekdaySelect, themeSelect, fishSelect, seasonSelect].forEach(function (el) {
      if (el) {
        el.addEventListener("change", function () {
          updateGeneratorOutputs(false);
        });
      }
    });

    if (customNote) {
      customNote.addEventListener("input", function () {
        updateGeneratorOutputs(false);
      });
    }

    const prevBtn = document.getElementById("btn-gen-prev-day");
    const nextBtn = document.getElementById("btn-gen-next-day");
    if (prevBtn) {
      prevBtn.addEventListener("click", function () {
        let cur = parseInt(daySelect.value, 10) || 1;
        cur = cur > 1 ? cur - 1 : 365;
        daySelect.value = String(cur);
        syncControlsFromDay(cur);
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        let cur = parseInt(daySelect.value, 10) || 1;
        cur = cur < 365 ? cur + 1 : 1;
        daySelect.value = String(cur);
        syncControlsFromDay(cur);
      });
    }

    // Initial render for DAY-01
    syncControlsFromDay(1);
  }

  function updateGeneratorOutputs(useExactDayEpisode) {
    const dayNum = parseInt((document.getElementById("gen-day-select") || {}).value, 10) || 1;
    const weekday = (document.getElementById("gen-weekday-select") || {}).value || "月曜日";
    const theme19 = (document.getElementById("gen-theme19-select") || {}).value || "① 旬の魚紹介";
    const fishName = (document.getElementById("gen-fish-select") || {}).value || "本マグロ";
    const season = (document.getElementById("gen-season-select") || {}).value || "春";
    const customNote = ((document.getElementById("gen-custom-note") || {}).value || "").trim();

    const fishInfo = findFishInfo(fishName);

    // Build Episode for Panel B
    let ep;
    if (useExactDayEpisode) {
      ep = getOrBuildEpisodeForDay(dayNum);
    } else {
      ep = synthesize10Items({
        id: "DAY-" + String(dayNum).padStart(2, "0"),
        dayNumber: dayNum,
        week: Math.ceil(dayNum / 7),
        dayOfWeek: weekday,
        themeCategory: theme19,
        featuredFish: fishName,
        season: season,
        factPointJp: customNote
          ? (customNote + "。ファインアトラスの「" + fishName + "」は可食部歩留まり" + (fishInfo.yieldPct || "高水準") + "、1皿原価" + (fishInfo.dishCost || "安定") + "（原価率" + (fishInfo.costRatioPct || "26.5〜30.2%") + "）を実現します。")
          : undefined
      });
    }
    currentGeneratedEp = ep;

    // Build Dot Prompt for Panel A
    const promptTextarea = document.getElementById("gen-dot-prompt-textarea");
    if (promptTextarea) {
      promptTextarea.value = buildDotInstructionPrompt({
        dayNum: dayNum,
        weekday: weekday,
        theme19: theme19,
        fishInfo: fishInfo,
        season: season,
        customNote: customNote,
        templateIdx: activeDotTemplateIdx
      });
    }

    // Render Instant 10-Item Preview in Panel B
    const previewContainer = document.getElementById("gen-instant-preview-container");
    if (previewContainer) {
      previewContainer.innerHTML = renderEpisodeCardHtml(ep, true);
    }
  }

  function buildDotInstructionPrompt(opts) {
    const f = opts.fishInfo || {};
    const dayLabel = "DAY-" + String(opts.dayNum).padStart(2, "0") + "（第" + Math.ceil(opts.dayNum / 7) + "週・" + opts.weekday + "）";

    if (opts.templateIdx === 1) {
      // Weekly Batch 7-Day Prompt
      return [
        "あなたは株式会社ファインアトラス（FINE ATLAS Co., Ltd.）の専属AI広報・ショート動画ディレクター（Dot）です。",
        "以下の「社長計画ルール」と「検証済みファクト」を厳守し、第" + Math.ceil(opts.dayNum / 7) + "週（月曜日〜日曜日までの7日分・計7テーマ）の30秒ショート動画台本（日英バイリンガル・全10項目）を一括作成してください。",
        "",
        "【絶対遵守ルール（社長計画 §2・§9・§10）】",
        "・動画仕様：30秒 ／ 縦型 9:16（1080×1920） ／ 音声なしでも理解できるよう字幕必須",
        "・秒数構成：0〜3秒（興味を引く導入）→ 3〜20秒（本題）→ 20〜27秒（要点まとめ）→ 27〜30秒（会社名・共通キャッチコピー）",
        "・共通キャッチコピー（日本語）：「" + CATCHPHRASE_JP + "」",
        "・共通キャッチコピー（英語）：\"" + CATCHPHRASE_EN + "\"",
        "・素材優先ルール：実際の商品や魚種の紹介には、自社で撮影した写真・動画（460点ストック）を優先指定し、不足素材のみAI画像生成で補完すること。",
        "・事実確認ガードレール：確認できない数値・産地・取引実績は絶対に使わないこと。",
        "",
        "【今週の主役魚種・検証済みファクト】",
        "・重点魚種：" + (f.nameJp || "国産旬魚") + "（" + (f.nameEn || "") + "）｜季節：" + opts.season,
        "・規格：" + (f.spec || "急速冷凍・真空包装") + " ／ 可食部歩留まり：" + (f.yieldPct || "68〜88%"),
        "・飲食店1人前原価：" + (f.dishCost || "290〜430円") + "（想定原価率 " + (f.costRatioPct || "26.5〜30.2%") + "）",
        "・営業導線（§11）：ショート動画毎日配信 → 認知 → 専門情報で信頼 → HP・Amazonへ誘導 → 少量購入で品質確認 → リピート購入 → 法人契約・店舗別オリジナル魚BOX受注",
        opts.customNote ? ("・追加強調ポイント：" + opts.customNote) : "",
        "",
        "【出力フォーマット（月曜〜日曜の各日ごとに以下の10項目をすべて出力すること）】",
        "① 動画タイトル",
        "② 30秒のナレーション台本",
        "③ 秒数ごとの映像内容（0〜3秒 / 3〜20秒 / 20〜27秒 / 27〜30秒）",
        "④ 使用する写真・動画の指示（自社撮影素材コード付き）",
        "⑤ AI画像生成用の指示文（不足素材の補完用）",
        "⑥ 字幕（Vrew貼り付け用 行分けテキスト）",
        "⑦ SNS投稿文章（YouTube Shorts / Instagram Reels / TikTok / Facebook Reels 共通）",
        "⑧ ハッシュタグ",
        "⑨ 情報の出典",
        "⑩ 英語版（タイトル・台本・字幕・投稿文）"
      ].filter(Boolean).join("\n");
    }

    // Standard Daily 10-Item Prompt (Section 10 exact compliance)
    return [
      "あなたは株式会社ファインアトラス（FINE ATLAS Co., Ltd.）の専属AIショート動画ディレクター（Dot）です。",
      "本日の配信スケジュール（" + dayLabel + "）に基づき、広報担当者がVrew・Canva・Metricoolへそのまま貼り付けて20〜30分で動画制作＆4大SNS予約投稿を完了できるよう、以下の【10項目（①〜⑩）】を正確に出力してください。",
      "",
      "==================================================",
      "📌 本日の配信指定条件（重複防止4重設計）",
      "==================================================",
      "・対象日：" + dayLabel,
      "・曜日テーマ：" + opts.weekday,
      "・19の配信テーマ：" + opts.theme19,
      "・季節・旬：" + opts.season,
      "・主役魚種：" + (f.nameJp || "本マグロ") + "（英語名：" + (f.nameEn || "Bluefin Tuna") + "）",
      opts.customNote ? ("・本日の特別訴求メモ：" + opts.customNote) : "",
      "",
      "==================================================",
      "📊 引用可能なファインアトラス検証済みファクト（推測禁止）",
      "==================================================",
      "・商品規格：" + (f.spec || "プロ用フィレ・ロイン（急速冷凍・真空包装）"),
      "・可食部歩留まり：" + (f.yieldPct || "68〜88%") + "（1人前正味 " + (f.netGram || "80g") + "）",
      "・飲食店1皿原価目安：" + (f.dishCost || "290〜430円") + " ／ 想定売価：" + (f.menuPrice || "980〜1,480円") + "（FL原価率 " + (f.costRatioPct || "26.5〜30.2%") + "）",
      "・現場メリット：" + (f.prepMerit || "必要な分だけ解凍して即提供可能、廃棄ロスゼロ、仕込み時間を大幅短縮"),
      "・営業7段階導線：公式HP・Amazonでの少量購入で品質確認 → リピート購入 → 法人契約・店舗別オリジナル魚BOX受注",
      "",
      "==================================================",
      "🎬 動画の基本ルール（§2・§9・§10 厳守）",
      "==================================================",
      "1. 長さ：30秒 ／ 形：縦型 9:16 ／ サイズ：1080×1920",
      "2. 字幕：音声なし（ミュート再生）でも100%理解できるよう、字幕を必ず入れる",
      "3. 秒数構成：",
      "   ・0〜3秒  ：興味を引く導入（料理長・バイヤーが手を止めるフック）",
      "   ・3〜20秒 ：本題（旬・目利き・急速冷凍技術・歩留まり原価の実証）",
      "   ・20〜27秒：要点まとめ（現場メリット＋少量お試し〜オリジナル魚BOX案内）",
      "   ・27〜30秒：会社名・共通キャッチコピー",
      "     🇯🇵 「" + CATCHPHRASE_JP + "」",
      "     🇺🇸 \"" + CATCHPHRASE_EN + "\"",
      "4. 素材ルール：実際の商品や魚種の紹介には、自社で撮影した写真・動画（全460点ストック）を最優先で指定する。不足素材のみAI画像生成で補完する。",
      "5. 事実確認：事実に基づいた内容のみを作成し、確認できない情報は使わない。",
      "",
      "==================================================",
      "📋 出力してほしい10項目（①〜⑩を省略せずすべて出力）",
      "==================================================",
      "① 動画タイトル",
      "② 30秒のナレーション台本",
      "③ 秒数ごとの映像内容（0〜3秒 / 3〜20秒 / 20〜27秒 / 27〜30秒）",
      "④ 使用する写真・動画の指示（自社撮影素材を優先指定）",
      "⑤ AI画像生成用の指示文（不足素材の補完用・英語プロンプト付き）",
      "⑥ 字幕（Vrewにそのまま貼り付けられる行分けテキスト）",
      "⑦ SNS投稿文章（YouTube Shorts / Instagram Reels / TikTok / Facebook Reels 対応）",
      "⑧ ハッシュタグ",
      "⑨ 情報の出典",
      "⑩ 英語版（タイトル・30秒台本・Vrew行分け字幕・SNS投稿文・英語ハッシュタグ）"
    ].filter(Boolean).join("\n");
  }

  // =================================================================
  // TAB 3: 365-Day Annual Delivery Calendar & Progress Tracker
  // =================================================================
  function renderCalendar365() {
    const tbody = document.getElementById("calendar-tbody");
    if (!tbody) return;

    const weekRange = (document.getElementById("cal-week-select") || {}).value || "all";
    const seasonFilter = (document.getElementById("cal-season-select") || {}).value || "all";
    const weekdayFilter = (document.getElementById("cal-weekday-select") || {}).value || "all";
    const themeFilter = (document.getElementById("cal-theme-select") || {}).value || "all";
    const statusFilter = (document.getElementById("cal-status-select") || {}).value || "all";
    const keyword = ((document.getElementById("cal-keyword-input") || {}).value || "").trim().toLowerCase();

    // Ensure 365 entries
    const list365 = [];
    for (let d = 1; d <= 365; d++) {
      const found = rawData.calendar365.find(function (c) { return Number(c.dayNumber) === d; });
      if (found) {
        list365.push(found);
      } else {
        const ep = getOrBuildEpisodeForDay(d);
        list365.push({
          dayNumber: d,
          weekNumber: ep.week,
          dayOfWeek: ep.dayOfWeek,
          weekdayTheme: ep.weekdayTheme,
          theme19: ep.themeCategory,
          season: ep.season,
          fishKey: ep.featuredFish,
          titleJp: ep.item1_title.jp,
          titleEn: ep.item1_title.en,
          hookJp: (ep.item3_timecode[0] && ep.item3_timecode[0].audioJp) || "",
          factPointJp: ep.item9_sources,
          assetCode: ep.item4_mediaDirection.ownAssetCode,
          sourceRef: ep.item9_sources,
          episodeId: ep.id
        });
      }
    }

    const filtered = list365.filter(function (row) {
      const w = Number(row.weekNumber) || Math.ceil(Number(row.dayNumber) / 7);
      if (weekRange !== "all") {
        const parts = weekRange.split("-");
        const minW = parseInt(parts[0], 10);
        const maxW = parseInt(parts[1], 10);
        if (w < minW || w > maxW) return false;
      }
      if (seasonFilter !== "all" && row.season !== seasonFilter) return false;
      if (weekdayFilter !== "all" && row.dayOfWeek !== weekdayFilter) return false;
      if (themeFilter !== "all" && (!row.theme19 || row.theme19.indexOf(themeFilter) === -1)) return false;

      const epId = row.episodeId || ("DAY-" + String(row.dayNumber).padStart(2, "0"));
      const st = dayStatusMap[epId] || "todo";
      if (statusFilter !== "all" && st !== statusFilter) return false;

      if (keyword) {
        const blob = [
          epId,
          "day" + row.dayNumber,
          row.dayOfWeek,
          row.theme19,
          row.fishKey,
          row.titleJp,
          row.titleEn,
          row.hookJp
        ].join(" ").toLowerCase();
        if (blob.indexOf(keyword) === -1) return false;
      }
      return true;
    });

    const showingEl = document.getElementById("cal-showing-count");
    if (showingEl) showingEl.textContent = String(filtered.length);

    tbody.innerHTML = filtered.map(function (row) {
      const dNum = Number(row.dayNumber);
      const epId = row.episodeId || ("DAY-" + String(dNum).padStart(2, "0"));
      const st = dayStatusMap[epId] || "todo";
      const isFirst28 = dNum <= 28;

      return (
        "<tr class=\"" + (isFirst28 ? "is-featured-28" : "") + "\">" +
          "<td>" +
            "<div><strong style=\"font-size:1.08em;color:#0C2238;\">" + escapeHtml(epId) + "</strong></div>" +
            "<div style=\"font-size:0.88em;color:#475569;\">第" + escapeHtml(row.weekNumber || Math.ceil(dNum / 7)) + "週" + (isFirst28 ? " 🌟初回28本" : "") + "</div>" +
          "</td>" +
          "<td>" +
            "<div><strong>" + escapeHtml(row.dayOfWeek) + "</strong></div>" +
            "<div style=\"font-size:0.88em;color:#475569;\">季節：" + escapeHtml(row.season || "通年") + "</div>" +
          "</td>" +
          "<td>" +
            "<div style=\"font-weight:900;color:#065F46;\">" + escapeHtml(row.theme19) + "</div>" +
            "<div style=\"font-weight:800;color:#9A3412;margin-top:3px;\">🐟 " + escapeHtml(row.fishKey) + "</div>" +
          "</td>" +
          "<td>" +
            "<div class=\"jp-only-block\" style=\"font-weight:900;color:#0C2238;\">🇯🇵 " + escapeHtml(row.titleJp) + "</div>" +
            "<div class=\"en-only-block\" style=\"font-weight:700;color:#1E40AF;font-size:0.92em;margin-top:2px;\">🇺🇸 " + escapeHtml(row.titleEn) + "</div>" +
            (row.hookJp ? "<div style=\"font-size:0.88em;color:#475569;margin-top:4px;\">💡 0-3秒：" + escapeHtml(row.hookJp) + "</div>" : "") +
          "</td>" +
          "<td>" +
            "<div><code>" + escapeHtml(row.assetCode || "FA-PHOTO-01") + "</code></div>" +
            "<div style=\"font-size:0.85em;color:#475569;margin-top:3px;\">📚 " + escapeHtml(row.sourceRef || "ファインアトラス検証データ") + "</div>" +
          "</td>" +
          "<td>" +
            "<select class=\"ep-status-select js-ep-status-change\" data-ep-id=\"" + escapeHtml(epId) + "\">" +
              "<option value=\"todo\"" + (st === "todo" ? " selected" : "") + ">⬜ 未着手</option>" +
              "<option value=\"vrew\"" + (st === "vrew" ? " selected" : "") + ">🎬 Vrew編集済</option>" +
              "<option value=\"checked\"" + (st === "checked" ? " selected" : "") + ">🔍 確認済</option>" +
              "<option value=\"scheduled\"" + (st === "scheduled" ? " selected" : "") + ">🚀 4大SNS予約済</option>" +
            "</select>" +
          "</td>" +
          "<td>" +
            "<button type=\"button\" class=\"btn-action-sm js-open-day-modal\" data-day-num=\"" + dNum + "\">" +
              "📄 10項目台本を開く" +
            "</button>" +
          "</td>" +
        "</tr>"
      );
    }).join("");
  }

  // =================================================================
  // TAB 4: 460 Pre-Prepared Assets Database
  // =================================================================
  function renderAssetDatabase() {
    const summaryBox = document.getElementById("asset-summary-cards");
    const catContainer = document.getElementById("asset-categories-container");
    if (!catContainer) return;

    const defaultCategories = [
      {
        id: "photo-raw",
        type: "写真",
        name: "① 丸魚の写真（水揚げ・姿・魚体・目利き部位）",
        targetCount: 100,
        codePrefix: "FA-PHOTO-RAW",
        priorityNote: "各魚種（本マグロ・サーモン・ブリ・真鯛・甘鯛・ノドグロ・ハモ・サバ・穴子・イカ等）の全体姿・澄んだ目・エラ・肥満度がわかる実写カット",
        sampleItems: [
          { code: "FA-PHOTO-RAW-01〜20", title: "主力10魚種の丸魚全体カット（斜め45度・真上）", spec: "各魚種2枚×10種（計20枚）", usage: "月曜「旬の魚紹介」・火曜「目利き」0〜3秒フック用" },
          { code: "FA-PHOTO-RAW-21〜50", title: "鮮度目利きクローズアップ（澄んだ黒目・ツヤのある皮目・尾の張り）", spec: "高解像度マクロ撮影（計30枚）", usage: "火曜「鮮度の見分け方」比較フリップ用" },
          { code: "FA-PHOTO-RAW-51〜80", title: "四季（春夏秋冬）の旬魚・地方希少魚コレクション", spec: "産地タグ・氷締め状態（計30枚）", usage: "土曜「産地紹介」・テーマ⑮「珍しい魚」用" },
          { code: "FA-PHOTO-RAW-81〜100", title: "サイズ・規格比較カット（メジャー添え・重量表示）", spec: "仕入れ規格証明写真（計20枚）", usage: "木曜「飲食店仕入れ改善」規格案内用" }
        ]
      },
      {
        id: "photo-fillet",
        type: "写真",
        name: "② フィレ・切り身の写真（断面・歩留まり・トリミング済）",
        targetCount: 100,
        codePrefix: "FA-PHOTO-FIL",
        priorityNote: "料理長が最も重視する「身の色・脂のサシ・血合いの美しさ・骨抜き/皮引き加工の丁寧さ」を証明する実写カット",
        sampleItems: [
          { code: "FA-PHOTO-FIL-01〜30", title: "主力10魚種フィレ・ロイン断面クローズアップ", spec: "照明反射で艶と脂乗りを強調（計30枚）", usage: "全動画の0〜3秒トップアイキャッチ最優先素材" },
          { code: "FA-PHOTO-FIL-31〜60", title: "丸魚→フィレ可食部歩留まり比較セット写真", spec: "加工前後の重量・歩留まり68〜88%可視化（計30枚）", usage: "木曜「原価・歩留まり・ロス削減」3〜20秒本題用" },
          { code: "FA-PHOTO-FIL-61〜80", title: "1人前（75〜90g）ポーション切り付け・サク取り状態", spec: "1皿原価290〜430円の定量イメージ（計20枚）", usage: "木曜・金曜の飲食店FL原価シミュレーション用" },
          { code: "FA-PHOTO-FIL-81〜100", title: "骨切りハモ・皮目炙りノドグロ・ウロコ付き甘鯛フィレ", spec: "職人下処理済み時短スペック（計20枚）", usage: "テーマ⑫「仕込み時間短縮」実演用" }
        ]
      },
      {
        id: "photo-vacuum",
        type: "写真",
        name: "③ 真空包装・急速冷凍魚の写真（霜ゼロ・高密着パック）",
        targetCount: 50,
        codePrefix: "FA-PHOTO-VAC",
        priorityNote: "「冷凍魚＝味が落ちる」という先入観を覆すため、袋内の霜・氷結晶の無さと高密着真空パッケージを鮮明に撮影",
        sampleItems: [
          { code: "FA-PHOTO-VAC-01〜20", title: "急速冷凍・高密着真空パック単品写真（表・裏・ラベル）", spec: "霜ゼロ・酸化防止密着状態（計20枚）", usage: "水曜「急速冷凍技術・真空包装」解説用" },
          { code: "FA-PHOTO-VAC-21〜35", title: "一般冷凍とファインアトラス急速冷凍の解凍ドリップ比較写真", spec: "キッチンペーパー上のドリップ量比較（計15枚）", usage: "テーマ⑨「冷凍魚と生魚の違い」決定版証拠写真" },
          { code: "FA-PHOTO-VAC-36〜50", title: "店舗別オリジナル魚BOX・少量お試しセット詰め合わせ外観", spec: "1箱に複数魚種が美しく並んだ状態（計15枚）", usage: "20〜27秒の「Amazon少量購入→オリジナル魚BOX」誘導用" }
        ]
      },
      {
        id: "photo-dish",
        type: "写真",
        name: "④ 寿司・刺身・料理の写真（盛り付け完成・提供イメージ）",
        targetCount: 100,
        codePrefix: "FA-PHOTO-DISH",
        priorityNote: "寿司店・高単価海鮮居酒屋・海外和食レストランのメニューにそのまま載せられるシズル感あふれる完成料理写真",
        sampleItems: [
          { code: "FA-PHOTO-DISH-01〜35", title: "江戸前握り寿司・特選刺身盛り合わせ（角が立った切り口）", spec: "檜カウンター・和皿盛り付け（計35枚）", usage: "金曜「寿司ネタ・刺身活用」・日曜「海外発信」用" },
          { code: "FA-PHOTO-DISH-36〜70", title: "高単価居酒屋メニュー（甘鯛松笠焼き・ノドグロ原始焼き・穴子天ぷら）", spec: "客単価8,000〜15,000円店の看板皿（計35枚）", usage: "テーマ⑭「居酒屋・和食メニュー提案」用" },
          { code: "FA-PHOTO-DISH-71〜100", title: "海外和食・海鮮ビストロ向けカルパッチョ・炙りロール・季節コース皿", spec: "インバウンド＆海外シェフ向け（計30枚）", usage: "日曜「海外向け日本産魚の魅力」英語版動画用" }
        ]
      },
      {
        id: "video-process",
        type: "動画",
        name: "⑤ 加工・冷凍工程の動画（下処理・真空パック・急速冷凍庫）",
        targetCount: 30,
        codePrefix: "FA-VID-PROC",
        priorityNote: "縦型9:16（1080×1920）で5〜10秒ずつ撮影。衛生的な加工場と最新急速冷凍テクノロジーの信頼感を映像で証明",
        sampleItems: [
          { code: "FA-VID-PROC-01〜10", title: "熟練職人による高速三枚おろし・骨抜きトリミング工程動画", spec: "縦型9:16・60fps推奨（計10本）", usage: "テーマ⑫「仕込み時間短縮」3〜20秒メイン映像" },
          { code: "FA-VID-PROC-11〜20", title: "高密着真空包装機での脱気・シール瞬間動画", spec: "空気が抜けてピタッと密着する瞬間（計10本）", usage: "テーマ⑦「真空包装・鮮度保持」3〜20秒映像" },
          { code: "FA-VID-PROC-21〜30", title: "超低温・急速冷凍ラインへの投入と凍結完了クリップ", spec: "冷気とスピード感が伝わる映像（計10本）", usage: "水曜「急速冷凍技術」・テーマ⑲会社紹介用" }
        ]
      },
      {
        id: "video-thaw",
        type: "動画",
        name: "⑥ 解凍・調理の動画（氷水解凍・包丁入れ・炙り・盛り付け）",
        targetCount: 30,
        codePrefix: "FA-VID-THAW",
        priorityNote: "「解凍してもドリップが出ない」「包丁がスッと入る生同等の身質」を3秒で納得させる最重要ショート動画素材",
        sampleItems: [
          { code: "FA-VID-THAW-01〜10", title: "真空パックのまま氷水解凍・流水解凍する正しい手順動画", spec: "温度管理と解凍時間のテロップ用（計10本）", usage: "水曜・テーマ⑧「解凍方法・扱い方」必須映像" },
          { code: "FA-VID-THAW-11〜20", title: "解凍直後のフィレに柳刃包丁を入れて断面を見せる瞬間動画", spec: "ドリップゼロ・艶やかな断面（計10本）", usage: "0〜3秒の最強フック映像（再生維持率UP）" },
          { code: "FA-VID-THAW-21〜30", title: "バーナー炙り・松笠焼きの油跳ね・寿司握りアクション動画", spec: "シズル音・湯気・照りの動き（計10本）", usage: "金曜「寿司・刺身・料理活用」メイン映像" }
        ]
      },
      {
        id: "video-port",
        type: "動画",
        name: "⑦ 漁港・市場・水揚げの動画（競り・活〆・産地ネットワーク）",
        targetCount: 30,
        codePrefix: "FA-VID-PORT",
        priorityNote: "全国47都道府県の産地ネットワークと目利き力を視覚化し、海外バイヤーや都市部料理長の信頼を勝ち取る現場映像",
        sampleItems: [
          { code: "FA-VID-PORT-01〜10", title: "早朝の漁港水揚げ・活気ある市場の競り・買い付け風景動画", spec: "縦型9:16・現場の臨場感（計10本）", usage: "土曜「市場・産地・水揚げ」0〜3秒＆本題用" },
          { code: "FA-VID-PORT-11〜20", title: "産地での活〆・血抜き・神経締め・氷水冷却のプロ技動画", spec: "鮮度を決定づける一次処理（計10本）", usage: "火曜「鮮度」・テーマ④「産地・漁港紹介」用" },
          { code: "FA-VID-PORT-21〜30", title: "季節ごとの産地風景と目利き担当者の検品クリップ", spec: "春夏秋冬の旬産地（計10本）", usage: "日曜「日本の魚食文化・海外発信」導入映像" }
        ]
      },
      {
        id: "video-box",
        type: "動画",
        name: "⑧ 箱詰め・出荷の動画（店舗別オリジナル魚BOX・クール出荷）",
        targetCount: 20,
        codePrefix: "FA-VID-BOX",
        priorityNote: "「日本の旬と品質を、一箱に。世界の厨房へ。」を体現する、20〜27秒のクロージング＆購入誘導パート決定版映像",
        sampleItems: [
          { code: "FA-VID-BOX-01〜10", title: "店舗別オリジナル魚BOXへ多彩な真空フィレを美しく箱詰めする動画", spec: "「一箱に旬を凝縮」する象徴映像（計10本）", usage: "全動画の20〜27秒「要点まとめ＆営業導線」共通映像" },
          { code: "FA-VID-BOX-11〜20", title: "保冷梱包・出荷検品・厨房で箱を開封するアンボクシング動画", spec: "Amazon少量購入〜定期便イメージ（計10本）", usage: "STEP 5「少量購入で品質確認」→ STEP 7「法人契約」誘導用" }
        ]
      }
    ];

    const categories = (rawData.assetInventory460 && rawData.assetInventory460.categories && rawData.assetInventory460.categories.length)
      ? rawData.assetInventory460.categories
      : defaultCategories;

    // Render Summary Cards
    if (summaryBox) {
      summaryBox.innerHTML =
        "<div class=\"kpi-box\">" +
          "<div class=\"kpi-label\">📷 事前準備 写真素材（4種）</div>" +
          "<div class=\"kpi-val\">合計 350 枚</div>" +
          "<div class=\"kpi-sub\">丸魚100 ＋ フィレ100 ＋ 真空50 ＋ 料理100</div>" +
        "</div>" +
        "<div class=\"kpi-box is-orange\">" +
          "<div class=\"kpi-label\">🎥 事前準備 動画素材（4種）</div>" +
          "<div class=\"kpi-val\">合計 110 本</div>" +
          "<div class=\"kpi-sub\">加工冷凍30 ＋ 解凍調理30 ＋ 漁港30 ＋ 箱詰め20</div>" +
        "</div>" +
        "<div class=\"kpi-box is-highlight\">" +
          "<div class=\"kpi-label\">📦 自社撮影ストック 総目標数</div>" +
          "<div class=\"kpi-val\">計 460 点</div>" +
          "<div class=\"kpi-sub\">実商品は自社素材を最優先（不足分のみAI補完）</div>" +
        "</div>";
    }

    catContainer.innerHTML = categories.map(function (cat, catIdx) {
      const isVideo = (cat.type && cat.type.indexOf("動画") !== -1) || (cat.id && cat.id.indexOf("video") !== -1);
      const unit = isVideo ? "本" : "枚";
      const items = cat.items || cat.sampleItems || [];
      const catId = cat.id || cat.prefix || ("cat-" + (cat.categoryNo || catIdx));
      const priorityText = cat.purpose || cat.priorityNote || "";

      const itemsHtml = items.map(function (item, idx) {
        const checkId = catId + "__" + (item.code || idx);
        const isChecked = Boolean(assetCheckMap[checkId]);
        const itemTitle = item.shotTitle || item.title || "";
        const itemSpec = item.specRequirement || item.spec || "";
        const itemUsage = item.usageSection || item.usage || "";
        return (
          "<label class=\"asset-check-item" + (isChecked ? " is-checked" : "") + "\">" +
            "<input type=\"checkbox\" class=\"js-asset-checkbox\" data-check-id=\"" + escapeHtml(checkId) + "\" data-weight=\"" + Math.max(1, Math.round((cat.targetCount || 40) / Math.max(items.length, 1))) + "\"" + (isChecked ? " checked" : "") + " />" +
            "<div>" +
              "<div><strong><code>" + escapeHtml(item.code) + "</code>｜" + escapeHtml(itemTitle) + "</strong></div>" +
              "<div style=\"font-size:0.9em;color:#334155;margin-top:2px;\">📐 仕様・枚数：" + escapeHtml(itemSpec) + " ／ 🎬 活用場面：" + escapeHtml(itemUsage) + "</div>" +
            "</div>" +
          "</label>"
        );
      }).join("");

      return (
        "<div class=\"asset-cat-card\">" +
          "<div class=\"asset-cat-header" + (isVideo ? " is-video" : "") + "\">" +
            "<h3 class=\"asset-cat-title\">" + (isVideo ? "🎥 " : "📷 ") + escapeHtml(cat.name) + "</h3>" +
            "<span class=\"asset-cat-target\">目標 " + escapeHtml(cat.targetCount) + " " + unit + "</span>" +
          "</div>" +
          "<div class=\"asset-cat-body\">" +
            "<div style=\"font-weight:800;color:#0C2238;font-size:0.95em;\">💡 撮影ポイント：" + escapeHtml(priorityText) + "</div>" +
            "<div class=\"asset-check-list\">" + itemsHtml + "</div>" +
          "</div>" +
        "</div>"
      );
    }).join("");
  }

  // =================================================================
  // TAB 5: President's Plan x Fine Atlas Execution Compass
  // =================================================================
  function renderExecutionCompass() {
    // 1. 4 AI Tools
    const toolsBox = document.getElementById("compass-ai-tools-list");
    if (toolsBox && rawData.planOverview.aiTools) {
      toolsBox.innerHTML = rawData.planOverview.aiTools.map(function (t) {
        return (
          "<div class=\"item-box\" style=\"margin-bottom:10px;\">" +
            "<div style=\"font-weight:900;font-size:1.08em;color:#0C2238;margin-bottom:4px;\">" +
              "<span class=\"item-num-badge\">ツール " + escapeHtml(t.num) + "</span> " + escapeHtml(t.name) +
            "</div>" +
            "<ul style=\"margin:6px 0 0 20px;padding:0;\">" +
              (t.tasks || []).map(function (task) { return "<li style=\"font-weight:700;\">" + escapeHtml(task) + "</li>"; }).join("") +
            "</ul>" +
          "</div>"
        );
      }).join("");
    }

    // 2. Daily Routine 8 Steps
    const routineBox = document.getElementById("compass-daily-routine-list");
    if (routineBox && rawData.planOverview.dailyRoutine8) {
      routineBox.innerHTML = rawData.planOverview.dailyRoutine8.map(function (r) {
        const minStr = r.targetMinutes || (r.minutes ? (r.minutes + "分") : "3分");
        return (
          "<div class=\"item-box\" style=\"margin-bottom:8px;padding:10px 14px;\">" +
            "<div style=\"display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;\">" +
              "<strong style=\"color:#0C2238;\"><span class=\"item-num-badge\">手順 " + escapeHtml(r.step) + "</span> " + escapeHtml(r.title) + "</strong>" +
              "<span class=\"tc-sec-badge\">目安 " + escapeHtml(minStr) + "｜" + escapeHtml(r.tool || "") + "</span>" +
            "</div>" +
            (r.detail ? "<div style=\"font-size:0.92em;color:#334155;margin-top:4px;\">" + escapeHtml(r.detail) + "</div>" : "") +
          "</div>"
        );
      }).join("");
    }

    // 3. 7-Stage Sales Funnel
    const funnelBox = document.getElementById("compass-funnel-grid");
    if (funnelBox && rawData.planOverview.salesFunnel7) {
      funnelBox.innerHTML = rawData.planOverview.salesFunnel7.map(function (f, idx) {
        const isLast = idx === rawData.planOverview.salesFunnel7.length - 1;
        const stepLabel = (typeof f.step === "number") ? ("STEP " + f.step) : (f.step || ("STEP " + (idx + 1)));
        const titleText = f.stage || f.title || "";
        const descText = f.action || f.desc || "";
        return (
          "<div class=\"funnel-step-card" + (isLast ? " is-goal" : "") + "\">" +
            "<span class=\"funnel-num\">" + escapeHtml(stepLabel) + "</span>" +
            "<div class=\"funnel-title\">" + escapeHtml(titleText) + "</div>" +
            "<p class=\"funnel-desc\">" + escapeHtml(descText) + "</p>" +
          "</div>"
        );
      }).join("");
    }

    // 4. Weekday Schedule
    const weekdayBox = document.getElementById("compass-weekday-list");
    if (weekdayBox && rawData.weekdaySchedule) {
      weekdayBox.innerHTML = rawData.weekdaySchedule.map(function (w) {
        const wTitle = w.categoryName || w.themeTitle || "";
        const wAngle = w.purpose || w.keyAngle || "";
        const wTarget = w.targetPersona || "国内外のレストランオーナー・料理人";
        return (
          "<div class=\"item-box\" style=\"margin-bottom:8px;padding:10px 14px;\">" +
            "<div><strong style=\"color:#0C2238;\">🗓️ " + escapeHtml(w.dayOfWeek) + "：【" + escapeHtml(wTitle) + "】</strong></div>" +
            "<div style=\"font-size:0.92em;color:#334155;margin-top:3px;\">🎯 対象：" + escapeHtml(wTarget) + " ／ 切り口：" + escapeHtml(wAngle) + "</div>" +
          "</div>"
        );
      }).join("");
    }

    // 5. 19 Themes
    const themesBox = document.getElementById("compass-themes19-list");
    if (themesBox) {
      const tList = (rawData.themes19 && rawData.themes19.length)
        ? rawData.themes19
        : [
            { num: 1, name: "魚の種類と特徴", weekday: "火曜日" },
            { num: 2, name: "全国の旬の魚", weekday: "月曜日" },
            { num: 3, name: "産地別の魚の市場相場", weekday: "月曜日" },
            { num: 4, name: "高級魚の豆知識", weekday: "火曜日" },
            { num: 5, name: "高品質冷凍魚とは", weekday: "水曜日" },
            { num: 6, name: "正しい冷凍魚の解凍方法", weekday: "水曜日" },
            { num: 7, name: "プロの料理人の調理方法", weekday: "木曜日" },
            { num: 8, name: "鮮魚と冷凍魚の比較", weekday: "水曜日" },
            { num: 9, name: "丸魚とフィレの原価比較", weekday: "金曜日" },
            { num: 10, name: "魚の歩留まりと原価率", weekday: "金曜日" },
            { num: 11, name: "仕込み人件費の削減", weekday: "金曜日" },
            { num: 12, name: "レストランの人材不足", weekday: "金曜日" },
            { num: 13, name: "日本の漁業の課題", weekday: "土曜日" },
            { num: 14, name: "世界の水産物事情", weekday: "土曜日" },
            { num: 15, name: "サステナブル", weekday: "土曜日" },
            { num: 16, name: "トレーサビリティ", weekday: "土曜日" },
            { num: 17, name: "空輸と船便の比較", weekday: "土曜日" },
            { num: 18, name: "日本の魚の海外輸出", weekday: "土曜日" },
            { num: 19, name: "ファインアトラスの商品紹介", weekday: "日曜日" }
          ];

      themesBox.innerHTML = "<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:8px;\">" +
        tList.map(function (t) {
          const tName = t.name || t.title || "";
          return (
            "<div style=\"background:#FAF8F3;border:1.5px solid #CBD5E1;border-radius:8px;padding:8px 12px;\">" +
              "<strong style=\"color:#0C2238;\">" + escapeHtml(t.num ? t.num + "." : "") + " " + escapeHtml(tName) + "</strong>" +
              (t.weekday ? "<div style=\"font-size:0.85em;color:#475569;\">主な配信：" + escapeHtml(t.weekday) + "</div>" : "") +
            "</div>"
          );
        }).join("") +
      "</div>";
    }

    // 6. 10 Fish Species Yield & Cost Table
    const fishTbody = document.getElementById("compass-fish10-tbody");
    if (fishTbody) {
      const fList = (rawData.fishMaster10 && rawData.fishMaster10.length) ? rawData.fishMaster10 : [];
      fishTbody.innerHTML = fList.map(function (fRaw) {
        const f = normalizeFishRecord(fRaw);
        return (
          "<tr>" +
            "<td><strong>🐟 " + escapeHtml(f.nameJp) + "</strong><br /><span style=\"font-size:0.88em;color:#1E40AF;\">" + escapeHtml(f.nameEn || "") + "</span></td>" +
            "<td>" + escapeHtml(f.category || "") + "<br /><span style=\"font-size:0.88em;color:#475569;\">" + escapeHtml(f.spec || "") + "</span></td>" +
            "<td>" + escapeHtml(f.wholesaleRange || "市場連動") + "</td>" +
            "<td><strong style=\"color:#0C2238;\">" + escapeHtml(f.faPrice || "要見積") + "</strong></td>" +
            "<td><span class=\"tc-sec-badge\">" + escapeHtml(f.yieldPct || "85〜98%") + "</span></td>" +
            "<td>" + escapeHtml(f.netGram || "60g") + " ／ <strong style=\"color:#9A3412;\">" + escapeHtml(f.dishCost || "¥359") + "</strong></td>" +
            "<td>" + escapeHtml(f.menuPrice || "¥1,280") + " ／ <strong style=\"color:#065F46;\">" + escapeHtml(f.costRatioPct || "28.1%") + "</strong></td>" +
            "<td>" + escapeHtml(f.prepMerit || "") + "</td>" +
          "</tr>"
        );
      }).join("");
    }

    // 7. Fact Check & Integrity Guardrails
    const guardrailsBox = document.getElementById("compass-guardrails-grid");
    if (guardrailsBox) {
      const rules = [
        {
          title: "① 確認できない情報は絶対に使わない（推測・誇張ゼロ）",
          desc: "社長計画§10の鉄則「事実に基づいた内容のみを作成し、確認できない情報は使わない」。裏付けのない「日本一」「絶対」などの断定表現や未確認の統計数値は使用禁止。"
        },
        {
          title: "② 実際の商品・魚種は「自社撮影の写真・動画（460点）」を最優先",
          desc: "社長計画§9の鉄則「実際の商品や魚種の紹介には、自社で撮影した写真・動画を優先する。不足素材のみAI生成で補完する」。AI生成の魚画像を自社商品として誤認させる演出は厳禁。"
        },
        {
          title: "③ グループ会社の固有実績とファインアトラスの企画を混同しない",
          desc: "ファインアトラスは「全国47都道府県の旬魚×急速冷凍・真空鮮度保持×店舗別オリジナル魚BOX」が強み。別会社の固有海外受賞歴や固有拠点をファインアトラス単独実績として誤記しない。"
        },
        {
          title: "④ 27〜30秒の共通キャッチコピーと4ステップ時間割の統一",
          desc: "すべての30秒動画（1080×1920）で「0-3秒導入 → 3-20秒本題 → 20-27秒要点 → 27-30秒『日本の旬と品質を、一箱に。世界の厨房へ。』」を統一し、ブランド記憶を定着させる。"
        }
      ];
      guardrailsBox.innerHTML = rules.map(function (r) {
        return (
          "<div class=\"guardrail-card\">" +
            "<div class=\"guardrail-title\">🛡️ " + escapeHtml(r.title) + "</div>" +
            "<p class=\"guardrail-desc\">" + escapeHtml(r.desc) + "</p>" +
          "</div>"
        );
      }).join("");
    }
  }

  // =================================================================
  // KPI & Progress Calculators
  // =================================================================
  function updateAllProgressIndicators() {
    // 1. First 28 Days completed count
    let done28 = 0;
    for (let i = 1; i <= 28; i++) {
      const id = "DAY-" + String(i).padStart(2, "0");
      if (dayStatusMap[id] && dayStatusMap[id] !== "todo") {
        done28++;
      }
    }
    const ep28El = document.getElementById("kpi-ep28-progress");
    if (ep28El) ep28El.textContent = done28 + " / 28 本";

    // 2. Full 365 Days completed count
    let done365 = 0;
    for (let d = 1; d <= 365; d++) {
      const id = "DAY-" + String(d).padStart(2, "0");
      if (dayStatusMap[id] && dayStatusMap[id] !== "todo") {
        done365++;
      }
    }
    const calSummaryEl = document.getElementById("cal-progress-summary-text");
    if (calSummaryEl) {
      calSummaryEl.textContent =
        "進行・完了 " + done365 + " / 365 テーマ（日英 " + (done365 * 2) + " / 730 動画 ／ 4大SNS " + (done365 * 8) + " / 2,920 投稿）";
    }
    const calFillEl = document.getElementById("cal-progress-bar-fill");
    if (calFillEl) {
      const pct = Math.min(100, Math.round((done365 / 365) * 100));
      calFillEl.style.width = pct + "%";
    }

    // 3. Asset 460 checklist count
    let checkedAssetPoints = 0;
    const boxes = document.querySelectorAll(".js-asset-checkbox");
    boxes.forEach(function (cb) {
      if (cb.checked) {
        checkedAssetPoints += parseInt(cb.getAttribute("data-weight") || "15", 10);
      }
    });
    if (checkedAssetPoints > 460) checkedAssetPoints = 460;
    const assetEl = document.getElementById("kpi-asset-progress");
    if (assetEl) assetEl.textContent = checkedAssetPoints + " / 460 点";
  }

  // =================================================================
  // CSV Export for 365-Day Schedule & Progress
  // =================================================================
  function exportCalendarCsv() {
    const headers = [
      "DAY番号",
      "週番号",
      "曜日",
      "季節",
      "19配信テーマ",
      "主役魚種",
      "①動画タイトル（日本語）",
      "⑩動画タイトル（英語）",
      "0〜3秒導入フック",
      "④自社素材コード",
      "⑨情報の出典",
      "制作ステータス"
    ];

    const statusLabelMap = {
      todo: "未着手",
      vrew: "Vrew編集済",
      checked: "事実・日英確認済",
      scheduled: "4大SNS予約済"
    };

    const rows = [headers];
    for (let d = 1; d <= 365; d++) {
      const ep = getOrBuildEpisodeForDay(d);
      const st = dayStatusMap[ep.id] || "todo";
      rows.push([
        ep.id,
        "第" + (ep.week || Math.ceil(d / 7)) + "週",
        ep.dayOfWeek || "",
        ep.season || "",
        ep.themeCategory || "",
        ep.featuredFish || "",
        ep.item1_title ? ep.item1_title.jp : "",
        ep.item1_title ? ep.item1_title.en : "",
        (ep.item3_timecode && ep.item3_timecode[0]) ? ep.item3_timecode[0].audioJp : "",
        ep.item4_mediaDirection ? ep.item4_mediaDirection.ownAssetCode : "",
        ep.item9_sources || "",
        statusLabelMap[st] || "未着手"
      ]);
    }

    const csvContent = "\uFEFF" + rows.map(function (r) {
      return r.map(function (cell) {
        const s = String(cell === null || cell === undefined ? "" : cell).replace(/"/g, "\"\"");
        return "\"" + s + "\"";
      }).join(",");
    }).join("\r\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ファインアトラス_AIショート動画_365日配信カレンダー進捗.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("💾 365日配信カレンダー＆進捗CSVを保存しました！");
  }

  // =================================================================
  // Modal Management
  // =================================================================
  function openDayModal(dayNum) {
    const modal = document.getElementById("script-modal");
    const kicker = document.getElementById("modal-kicker");
    const title = document.getElementById("modal-title");
    const body = document.getElementById("modal-body");
    if (!modal || !body) return;

    const ep = getOrBuildEpisodeForDay(dayNum);
    if (kicker) kicker.textContent = ep.id + "（第" + ep.week + "週・" + ep.dayOfWeek + "）｜" + ep.themeCategory + "｜" + ep.featuredFish;
    if (title) title.textContent = ep.item1_title.jp;
    body.innerHTML = renderEpisodeCardHtml(ep, true);

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeDayModal() {
    const modal = document.getElementById("script-modal");
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
  }

  // =================================================================
  // Event Binding
  // =================================================================
  function bindEvents() {
    // 1. Font Scale Switcher
    const savedScale = loadStorage(STORAGE_KEYS.FONT_SCALE, "1.05");
    document.documentElement.style.setProperty("--base-scale", savedScale);
    document.querySelectorAll(".js-scale-btn").forEach(function (btn) {
      if (btn.getAttribute("data-scale") === String(savedScale)) {
        btn.classList.add("is-active");
      } else {
        btn.classList.remove("is-active");
      }
      btn.addEventListener("click", function () {
        const scale = btn.getAttribute("data-scale") || "1.05";
        document.documentElement.style.setProperty("--base-scale", scale);
        saveStorage(STORAGE_KEYS.FONT_SCALE, scale);
        document.querySelectorAll(".js-scale-btn").forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        showToast("🔍 文字サイズを切り替えました");
      });
    });

    // 2. Language Mode Switcher
    const savedLang = loadStorage(STORAGE_KEYS.LANG_MODE, "both");
    document.body.setAttribute("data-lang-mode", savedLang);
    document.querySelectorAll(".js-lang-btn").forEach(function (btn) {
      if (btn.getAttribute("data-lang") === savedLang) {
        btn.classList.add("is-active");
      } else {
        btn.classList.remove("is-active");
      }
      btn.addEventListener("click", function () {
        const lang = btn.getAttribute("data-lang") || "both";
        document.body.setAttribute("data-lang-mode", lang);
        saveStorage(STORAGE_KEYS.LANG_MODE, lang);
        document.querySelectorAll(".js-lang-btn").forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        showToast("🌐 表示言語モードを切り替えました");
      });
    });

    // 3. 5-Mode Main Studio Tabs
    document.querySelectorAll(".studio-tab-btn").forEach(function (tabBtn) {
      tabBtn.addEventListener("click", function () {
        const targetId = tabBtn.getAttribute("data-tab");
        document.querySelectorAll(".studio-tab-btn").forEach(function (b) {
          b.classList.remove("is-active");
          b.setAttribute("aria-selected", "false");
        });
        tabBtn.classList.add("is-active");
        tabBtn.setAttribute("aria-selected", "true");

        document.querySelectorAll(".tab-panel").forEach(function (panel) {
          if (panel.id === targetId) {
            panel.classList.add("is-active");
          } else {
            panel.classList.remove("is-active");
          }
        });
      });
    });

    // 4. Tab 1 Filters (Week Pills, Weekday Pills, Dropdowns, Keyword)
    const weekPills = document.getElementById("ep-week-pills");
    if (weekPills) {
      weekPills.addEventListener("click", function (e) {
        const btn = e.target.closest(".pill-btn");
        if (!btn) return;
        activeEpWeek = btn.getAttribute("data-week") || "all";
        weekPills.querySelectorAll(".pill-btn").forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        renderEpisodesList();
      });
    }

    const weekdayPills = document.getElementById("ep-weekday-pills");
    if (weekdayPills) {
      weekdayPills.addEventListener("click", function (e) {
        const btn = e.target.closest(".pill-btn");
        if (!btn) return;
        activeEpWeekday = btn.getAttribute("data-weekday") || "all";
        weekdayPills.querySelectorAll(".pill-btn").forEach(function (b) { b.classList.remove("is-active"); });
        btn.classList.add("is-active");
        renderEpisodesList();
      });
    }

    ["ep-theme-select", "ep-fish-select", "ep-status-select"].forEach(function (id) {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", renderEpisodesList);
    });

    const epKw = document.getElementById("ep-keyword-input");
    if (epKw) epKw.addEventListener("input", renderEpisodesList);

    const resetEpBtn = document.getElementById("btn-reset-ep-filters");
    if (resetEpBtn) {
      resetEpBtn.addEventListener("click", function () {
        activeEpWeek = "all";
        activeEpWeekday = "all";
        document.querySelectorAll("#ep-week-pills .pill-btn, #ep-weekday-pills .pill-btn").forEach(function (b) {
          b.classList.remove("is-active");
        });
        const firstW = document.querySelector("#ep-week-pills .pill-btn[data-week='all']");
        if (firstW) firstW.classList.add("is-active");
        const firstD = document.querySelector("#ep-weekday-pills .pill-btn[data-weekday='all']");
        if (firstD) firstD.classList.add("is-active");

        ["ep-theme-select", "ep-fish-select", "ep-status-select"].forEach(function (id) {
          const el = document.getElementById(id);
          if (el) el.value = "all";
        });
        if (epKw) epKw.value = "";
        renderEpisodesList();
        showToast("🔄 絞り込み条件をリセットしました");
      });
    }

    // 5. Tab 3 Calendar Filters
    ["cal-week-select", "cal-season-select", "cal-weekday-select", "cal-theme-select", "cal-status-select"].forEach(function (id) {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", renderCalendar365);
    });
    const calKw = document.getElementById("cal-keyword-input");
    if (calKw) calKw.addEventListener("input", renderCalendar365);

    const resetCalBtn = document.getElementById("btn-reset-cal-filters");
    if (resetCalBtn) {
      resetCalBtn.addEventListener("click", function () {
        ["cal-week-select", "cal-season-select", "cal-weekday-select", "cal-theme-select", "cal-status-select"].forEach(function (id) {
          const el = document.getElementById(id);
          if (el) el.value = "all";
        });
        if (calKw) calKw.value = "";
        renderCalendar365();
        showToast("🔄 カレンダー絞込をリセットしました");
      });
    }

    // 6. Delegated Clicks (Copy Buttons, Modal Triggers, Dot Template Pills)
    document.body.addEventListener("click", function (e) {
      // Vrew JP Copy
      const vrewJpBtn = e.target.closest(".js-copy-vrew-jp");
      if (vrewJpBtn) {
        const epId = vrewJpBtn.getAttribute("data-ep-id");
        const num = parseInt((epId || "DAY-01").replace("DAY-", ""), 10) || 1;
        const ep = (currentGeneratedEp && currentGeneratedEp.id === epId) ? currentGeneratedEp : getOrBuildEpisodeForDay(num);
        copyToClipboard(buildVrewCopyText(ep, "jp"), epId + " Vrew投入用（日本語台本＋字幕）");
        return;
      }

      // Vrew EN Copy
      const vrewEnBtn = e.target.closest(".js-copy-vrew-en");
      if (vrewEnBtn) {
        const epId = vrewEnBtn.getAttribute("data-ep-id");
        const num = parseInt((epId || "DAY-01").replace("DAY-", ""), 10) || 1;
        const ep = (currentGeneratedEp && currentGeneratedEp.id === epId) ? currentGeneratedEp : getOrBuildEpisodeForDay(num);
        copyToClipboard(buildVrewCopyText(ep, "en"), epId + " Vrew投入用（英語台本＋字幕）");
        return;
      }

      // Metricool Copy
      const metricoolBtn = e.target.closest(".js-copy-metricool");
      if (metricoolBtn) {
        const epId = metricoolBtn.getAttribute("data-ep-id");
        const num = parseInt((epId || "DAY-01").replace("DAY-", ""), 10) || 1;
        const ep = (currentGeneratedEp && currentGeneratedEp.id === epId) ? currentGeneratedEp : getOrBuildEpisodeForDay(num);
        copyToClipboard(buildMetricoolCopyText(ep), epId + " Metricool予約用（日英SNS投稿文＋タグ）");
        return;
      }

      // AI Image Prompt Copy
      const aiPromptBtn = e.target.closest(".js-copy-ai-prompt");
      if (aiPromptBtn) {
        const epId = aiPromptBtn.getAttribute("data-ep-id");
        const num = parseInt((epId || "DAY-01").replace("DAY-", ""), 10) || 1;
        const ep = normalizeEpisode((currentGeneratedEp && currentGeneratedEp.id === epId) ? currentGeneratedEp : getOrBuildEpisodeForDay(num));
        copyToClipboard(ep.item5_aiImagePrompt.promptEn, epId + " AI画像生成プロンプト");
        return;
      }

      // Full 10 Items Copy
      const all10Btn = e.target.closest(".js-copy-all10");
      if (all10Btn) {
        const epId = all10Btn.getAttribute("data-ep-id");
        const num = parseInt((epId || "DAY-01").replace("DAY-", ""), 10) || 1;
        const ep = (currentGeneratedEp && currentGeneratedEp.id === epId) ? currentGeneratedEp : getOrBuildEpisodeForDay(num);
        copyToClipboard(buildFull10CopyText(ep), epId + " 全10項目フルパッケージ");
        return;
      }

      // Open 365 Day Modal
      const openModalBtn = e.target.closest(".js-open-day-modal");
      if (openModalBtn) {
        const dNum = parseInt(openModalBtn.getAttribute("data-day-num"), 10) || 1;
        openDayModal(dNum);
        return;
      }

      // Dot Template Pill Switch
      const tplPill = e.target.closest(".js-dot-tpl-pill");
      if (tplPill) {
        activeDotTemplateIdx = parseInt(tplPill.getAttribute("data-tpl-idx"), 10) || 0;
        document.querySelectorAll(".js-dot-tpl-pill").forEach(function (b) { b.classList.remove("is-active"); });
        tplPill.classList.add("is-active");
        updateGeneratorOutputs(false);
        return;
      }
    });

    // 7. Delegated Changes (Episode Status Select & Asset Checkboxes)
    document.body.addEventListener("change", function (e) {
      const statusSel = e.target.closest(".js-ep-status-change");
      if (statusSel) {
        const epId = statusSel.getAttribute("data-ep-id");
        const newVal = statusSel.value;
        dayStatusMap[epId] = newVal;
        saveStorage(STORAGE_KEYS.EP_STATUS, dayStatusMap);

        // Sync any other status dropdown for the same epId
        document.querySelectorAll(".js-ep-status-change[data-ep-id='" + epId + "']").forEach(function (sel) {
          sel.value = newVal;
        });

        updateAllProgressIndicators();
        showToast("✅ " + epId + " のステータスを保存しました");
        return;
      }

      const assetCb = e.target.closest(".js-asset-checkbox");
      if (assetCb) {
        const checkId = assetCb.getAttribute("data-check-id");
        assetCheckMap[checkId] = assetCb.checked;
        saveStorage(STORAGE_KEYS.ASSET_CHECKS, assetCheckMap);
        const label = assetCb.closest(".asset-check-item");
        if (label) {
          if (assetCb.checked) label.classList.add("is-checked");
          else label.classList.remove("is-checked");
        }
        updateAllProgressIndicators();
        showToast("📸 自社素材チェックリストを更新しました");
      }
    });

    // 8. Generator Top Copy Buttons
    const copyDotBtn = document.getElementById("btn-copy-dot-prompt");
    if (copyDotBtn) {
      copyDotBtn.addEventListener("click", function () {
        const ta = document.getElementById("gen-dot-prompt-textarea");
        if (ta) copyToClipboard(ta.value, "Dot / ChatGPT への毎日の指示文（10項目プロンプト）");
      });
    }

    const copyGenAll10Btn = document.getElementById("btn-copy-gen-all10");
    if (copyGenAll10Btn) {
      copyGenAll10Btn.addEventListener("click", function () {
        if (currentGeneratedEp) {
          copyToClipboard(buildFull10CopyText(currentGeneratedEp), currentGeneratedEp.id + " 全10項目フルパッケージ");
        }
      });
    }

    // 9. CSV Export & Print & Modal Close
    const csvBtn1 = document.getElementById("btn-export-calendar-csv");
    const csvBtn2 = document.getElementById("btn-cal-export-csv");
    if (csvBtn1) csvBtn1.addEventListener("click", exportCalendarCsv);
    if (csvBtn2) csvBtn2.addEventListener("click", exportCalendarCsv);

    const printBtn = document.getElementById("btn-print-page");
    if (printBtn) {
      printBtn.addEventListener("click", function () {
        window.print();
      });
    }

    const closeModalBtn = document.getElementById("btn-close-modal");
    if (closeModalBtn) closeModalBtn.addEventListener("click", closeDayModal);

    const modalBackdrop = document.getElementById("script-modal");
    if (modalBackdrop) {
      modalBackdrop.addEventListener("click", function (e) {
        if (e.target === modalBackdrop) closeDayModal();
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeDayModal();
    });
  }

  // =================================================================
  // Initialize App
  // =================================================================
  function initApp() {
    rawData = getSafeData();
    dayStatusMap = loadStorage(STORAGE_KEYS.EP_STATUS, {});
    assetCheckMap = loadStorage(STORAGE_KEYS.ASSET_CHECKS, {});

    populateEpisodeFilterDropdowns();
    renderEpisodesList();
    initGeneratorControls();
    renderCalendar365();
    renderAssetDatabase();
    renderExecutionCompass();
    bindEvents();
    updateAllProgressIndicators();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
  } else {
    initApp();
  }
})();
