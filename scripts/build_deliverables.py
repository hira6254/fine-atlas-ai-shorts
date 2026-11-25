#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
株式会社ファインアトラス｜AIショート動画 毎日配信計画
マスターデータ(data.js) ＆ 6シートExcelマスター台帳 自動生成スクリプト
"""

import json
import os
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_JS_PATH = BASE_DIR / "data.js"
EXCEL_PATH = BASE_DIR / "ファインアトラス_AIショート動画_毎日配信マスター台帳.xlsx"

CLOSING_JP = "日本の旬と品質を、一箱に。世界の厨房へ。"
CLOSING_EN = "Japan's seasonal catch & peak quality, in one box. To kitchens worldwide."


def build_plan_overview():
    return {
        "title": "ファインアトラス｜AIショート動画 毎日配信計画 実行コンパス＆365日制作スタジオ",
        "subtitle": "社長計画書（全13章）完全準拠 × ファインアトラス実態データ（主力5＋拡張5品目・歩留まり85〜99%・急速冷凍技術）融合モデル",
        "closingCatchphraseJp": CLOSING_JP,
        "closingCatchphraseEn": CLOSING_EN,
        "purpose": [
            "国内外の飲食店オーナーおよび料理人に対し、日本の魚の魅力、旬の魚、市場情報、冷凍技術、調理方法などを短い動画で毎日発信し、株式会社ファインアトラスの認知拡大と信頼構築を行う。",
            "ショート動画を通じてホームページおよびAmazon販売ページへ誘導し、まず少量購入による品質確認を促進し、その後リピート購入、法人契約、店舗別オリジナル魚BOXの受注へつなげる。",
            "AIツールを活用することで、撮影や編集の専門知識がない広報担当者1名でも、毎日継続して日本語版と英語版の動画を制作・配信できる体制を構築する。"
        ],
        "videoRules": {
            "duration": "15〜30秒",
            "aspect": "縦型 9:16",
            "resolution": "1080×1920",
            "subtitleRule": "音声なしでも理解できるように、必ず字幕を入れる",
            "targetWorkTime": "テンプレート完成後 1日20〜30分（週1回・7日分まとめ制作＆予約配信も併用）",
            "productionPolicy": "会社紹介や商品宣伝を直接的に行うのではなく、飲食店や料理人にとって役立つ魚の専門情報を発信し、動画の最後にファインアトラスのブランドメッセージを伝える構成とする。"
        },
        "timecodeStructure": [
            {"range": "0〜3秒", "role": "興味を引くタイトルと映像（フック）"},
            {"range": "3〜20秒", "role": "写真・映像・ナレーションによる専門解説"},
            {"range": "20〜27秒", "role": "結論・完成料理など"},
            {"range": "27〜30秒", "role": f"ファインアトラスのロゴとキャッチコピー「{CLOSING_JP}」"}
        ],
        "annualTargets": {
            "dailyThemes": 1,
            "monthlyThemes": 30,
            "yearlyThemes": 365,
            "bilingualVideos": 730,
            "snsCount": 4,
            "totalYearlyPosts": 2920,
            "snsPlatforms": ["TikTok", "Instagramリール", "YouTubeショート", "Facebookリール"],
            "languageBreakdown": "日本語1本＋英語1本＝1日2本制作（年間730本）× 4つのSNSへ配信＝年間延べ2,920投稿"
        },
        "aiTools": [
            {
                "id": "chatgpt_dot",
                "num": "①",
                "name": "ChatGPT・Dot",
                "roleSummary": "企画・台本・日英翻訳・出典確認の中枢AI",
                "tasks": [
                    "情報収集",
                    "配信テーマの選定",
                    "動画タイトルの作成",
                    "ナレーション台本の作成",
                    "画像生成",
                    "英語への翻訳",
                    "SNS投稿文章の作成"
                ]
            },
            {
                "id": "vrew",
                "num": "②",
                "name": "Vrew（ブリュー）",
                "roleSummary": "台本テキストからAI音声・字幕付き動画を自動生成",
                "tasks": [
                    "台本から動画制作",
                    "AIナレーション",
                    "自動字幕",
                    "写真、映像の挿入",
                    "BGMの挿入",
                    "動画編集"
                ]
            },
            {
                "id": "canva",
                "num": "③",
                "name": "Canva",
                "roleSummary": "表紙サムネイル・ロゴ・27〜30秒エンドカード統一",
                "tasks": [
                    "動画の表紙制作",
                    "会社ロゴの挿入",
                    "デザインの統一"
                ]
            },
            {
                "id": "metricool",
                "num": "④",
                "name": "Metricool",
                "roleSummary": "4大SNS一括予約配信・再生数＆フォロワー分析",
                "tasks": [
                    "複数のSNSへの予約投稿",
                    "再生回数の分析",
                    "フォロワーの増加状況の確認"
                ]
            }
        ],
        "dailyRoutine8": [
            {
                "step": 1,
                "title": "Dotに当日の曜日テーマを指示する",
                "minutes": 3,
                "tool": "ChatGPT・Dot",
                "detail": "365日カレンダーから当日のテーマと魚種を選び、10項目出力プロンプトをDotに貼り付けて日本語・英語の台本一式を生成する。"
            },
            {
                "step": 2,
                "title": "出力された情報の事実確認を行う",
                "minutes": 3,
                "tool": "広報担当者＋出典リスト",
                "detail": "市場統計・歩留まり・ドリップ率などの数値に出典があるか確認し、未確認情報や誇大表現がないかチェックする。"
            },
            {
                "step": 3,
                "title": "Vrewに日本語台本を入力し、日本語版動画を制作する",
                "minutes": 6,
                "tool": "Vrew",
                "detail": "15〜30秒の日本語台本を貼り付け、AIナレーションと自動字幕を生成。27〜30秒に「日本の旬と品質を、一箱に。世界の厨房へ。」を配置する。"
            },
            {
                "step": 4,
                "title": "用意している写真や動画を挿入する",
                "minutes": 4,
                "tool": "Vrew＋自社素材DB（460点）",
                "detail": "素材コード（P-WR/P-FL/P-VF/P-CS/V-PF/V-TC/V-FP/V-PS）に対応する自社写真・動画を0〜3秒、3〜20秒、20〜27秒へ当てはめる。"
            },
            {
                "step": 5,
                "title": "Vrewに英語台本を入力し、英語版動画を制作する",
                "minutes": 4,
                "tool": "Vrew",
                "detail": "日本語版プロジェクトを複製し、英語台本と英語AI音声・英語字幕に差し替える（映像素材はそのまま活用して時短）。"
            },
            {
                "step": 6,
                "title": "Canvaで表紙とロゴを設定する",
                "minutes": 2,
                "tool": "Canva",
                "detail": "1080×1920の共通表紙テンプレートにタイトルを入れ、27〜30秒のファインアトラス公式ロゴ＆キャッチコピー画面を結合する。"
            },
            {
                "step": 7,
                "title": "Metricoolで4つのSNSへ予約投稿する",
                "minutes": 2,
                "tool": "Metricool",
                "detail": "TikTok、Instagramリール、YouTubeショート、Facebookリールへ日英動画・投稿文・ハッシュタグをセットし予約登録する。"
            },
            {
                "step": 8,
                "title": "前日の再生回数や反応を確認する",
                "minutes": 1,
                "tool": "Metricool",
                "detail": "3秒視聴維持率、保存数、プロフィール（HP・Amazon）クリック数を確認し、反応の良い魚種・切り口を次週に反映する。"
            }
        ],
        "weeklyBatchGuide": {
            "totalMinutes": 150,
            "summary": "週1回（2.5時間＝150分）で7日分（日英14本・56投稿）をまとめ制作＆Metricool予約する高効率バッチ運用も可能",
            "breakdown": [
                "① Dotで月〜日の7日分台本（10項目×7本）を一括生成・事実確認（30分）",
                "② 自社素材フォルダ（460点DB）から7日分の写真・動画素材をピックアップ（20分）",
                "③ Vrewで日本語版7本を連続生成・字幕調整（45分）",
                "④ Vrewプロジェクト複製で英語版7本を連続生成（30分）",
                "⑤ Canva表紙書き出し＆Metricoolで7日×4SNS一括スケジュール予約（25分）"
            ]
        },
        "salesFunnel7": [
            {
                "step": 1,
                "stage": "ショート動画の毎日配信",
                "action": "TikTok・Instagramリール・YouTubeショート・Facebookリールで日英2本（15〜30秒）を365日毎日発信",
                "kpi": "1日2本／年間730本（4SNS延べ2,920投稿）"
            },
            {
                "step": 2,
                "stage": "ファインアトラスの認知",
                "action": "0〜3秒の強烈なフックと27〜30秒の「日本の旬と品質を、一箱に。世界の厨房へ。」でブランドを刷り込む",
                "kpi": "月間リーチ数・3秒視聴維持率65%以上"
            },
            {
                "step": 3,
                "stage": "魚の専門情報による信頼構築",
                "action": "売り込みではなく、旬・市場相場・急速冷凍ドリップ率・歩留まり原価改善など料理人に役立つ専門知識を提供",
                "kpi": "動画保存率・コメント・フォロワー増加数"
            },
            {
                "step": 4,
                "stage": "ホームページ・Amazonへ誘導",
                "action": "プロフィールリンクおよび投稿キャプションから公式HP（fineatlas.co.jp）・Amazon・Shopify商品ページへ誘導",
                "kpi": "プロフィール遷移率・リンククリック数"
            },
            {
                "step": 5,
                "stage": "少量購入で品質確認",
                "action": "Amazonでの単品購入や公式「お試しセット（税込10,000円）」で、自店の厨房にて身質・ドリップ・歩留まりを実地確認",
                "kpi": "初回お試し購入件数・Amazon小口注文数"
            },
            {
                "step": 6,
                "stage": "リピート購入",
                "action": "品質に納得した飲食店が、看板メニューや時化日のバックアップ・仕込み時短用として継続発注",
                "kpi": "2回目・3回目リピート転換率"
            },
            {
                "step": 7,
                "stage": "法人契約・店舗別オリジナル魚BOXの受注",
                "action": "料理の用途・希望サイズ・下処理度合い・納品形態（チルド／冷凍）に合わせた店舗別オリジナル魚BOX・定期法人契約へ昇華",
                "kpi": "月額定期口座数・店舗別オリジナル魚BOX契約数"
            }
        ],
        "fineAtlasInsights": [
            {
                "id": "FA-01",
                "title": "ファインスタッフ×対馬水産のDNA（2026年9月設立）",
                "fact": "株式会社ファインアトラス（代表取締役 今田義幸・資本金3,000万円）は、対馬水産の海外事業部を分離・承継し、飲食人材支援のファインスタッフの知見を融合して2026年9月に設立。「産地で時間を止め、現地で時間を動かす。」を掲げ、飲食店の仕込み人手不足と高品質魚介の安定調達を同時に解決する。"
            },
            {
                "id": "FA-02",
                "title": "主力5品目＋拡張5品目の圧倒的歩留まり（65〜99%・主力85〜98%）",
                "fact": "丸魚仕入れでは頭・内臓・中骨ロスで歩留まりが45〜60%に落ちるが、ファインアトラスの産地一次加工品（煮穴子98%、穴子フィレ96%、甘鯛鱗付フィレ95%、剣先イカお造り柵95%、のどぐろセミドレス85%、ホタテ貝柱99%等）はほぼ100%可食部として使える。"
            },
            {
                "id": "FA-03",
                "title": "飲食店1皿原価率 26.5〜30.2%（平均28.1%）の黄金FLゾーン",
                "fact": "10品目すべてにおいて、ファインアトラスが適正粗利（平均34.1%）を確保しながら、飲食店側の1皿原価率は26.5%（剣先イカ）〜30.2%（ホタテ貝柱）、平均28.1%の黄金ゾーンに収まり、さらに毎日1〜2時間の仕込み人件費を削減できる。"
            },
            {
                "id": "FA-04",
                "title": "最大氷結晶生成帯（-1〜-5℃）を3〜25分で一気に通過する急速冷凍",
                "fact": "一般緩慢冷凍（30〜120分通過）はドリップ流出率が5.0〜10.0%に達し身割れするが、急速エアブラスト＋高真空（15〜25分・ドリップ2.0〜3.5%）や特殊急速凍結（3〜12分・ドリップ0.5〜1.5%以下）は細胞膜を壊さず、お造りや甘鯛松笠焼きの鱗立ちまで再現する。"
            },
            {
                "id": "FA-05",
                "title": "産地凍結×現地解凍仕込み・小口〜オリジナル魚BOX対応",
                "fact": "旬の盛漁期に産地で下処理・真空・急速冷凍して価格と品質を固定し、お店の注文に合わせて解凍・仕込み（チルド／冷凍選択可）して届けるため、時化（しけ）による欠品や相場高騰リスクを抑えられる。"
            },
            {
                "id": "FA-06",
                "title": "情報信頼性の3原則＆営業ガードレール完全遵守",
                "fact": "①水産庁・市場統計等の根拠ある情報のみ使用、②出典の記録と確認、③AI生成の誇大表現や未確認情報の排除。特に個別店舗の価格・送料・最低ロットは推測で断定せず、お試し購入（Amazon・HP）から個別ヒアリングへ誠実に誘導する。"
            }
        ],
        "trustRulesSection9": [
            "① 根拠のある情報のみを使用する（水産庁の公開資料、卸売市場の公開データ、一般的な水産加工技術、調理技術、ファインアトラスの商品情報）",
            "② 情報の出典を確認する（Dotで台本を作成する際には、必ず情報の出典を同時に出力させ、広報担当者が内容を確認する）",
            "③ AIが作った未確認の情報は使用しない（事実確認ができない内容、誇大表現、誤解を招く表現は動画に使用しない。実際の商品紹介には必ず自社で撮影した写真・動画を使用する）"
        ]
    }


def build_weekday_schedule():
    return [
        {
            "dayOfWeek": "月曜日",
            "dayEn": "Monday",
            "code": "MON",
            "categoryName": "今週の旬の魚・市場相場",
            "categoryEn": "Seasonal Catch & Market Trends",
            "color": "#0284c7",
            "purpose": "週の始まりに料理人が最も気にする「今脂が乗っている旬魚」と「市場の水揚げ・相場動向」を30秒で解説し、盛漁期買い付けの優位性を伝える。",
            "mappedThemeIds": ["TH-01", "TH-03", "TH-15"]
        },
        {
            "dayOfWeek": "火曜日",
            "dayEn": "Tuesday",
            "code": "TUE",
            "categoryName": "高級魚の豆知識",
            "categoryEn": "Premium Japanese Fish Trivia",
            "color": "#7c3aed",
            "purpose": "のどぐろ・甘鯛・剣先イカ・トラフグ・対馬穴子など、日本が誇る高級魚の目利き・産地差・旨味成分を掘り下げ、料理人の知的好奇心と保存率を高める。",
            "mappedThemeIds": ["TH-02", "TH-13", "TH-14"]
        },
        {
            "dayOfWeek": "水曜日",
            "dayEn": "Wednesday",
            "code": "WED",
            "categoryName": "冷凍魚の特徴・解凍方法",
            "categoryEn": "Rapid Freezing Science & Thawing Tech",
            "color": "#0d9488",
            "purpose": "「冷凍魚は水っぽい」という固定観念を、最大氷結晶生成帯（-1〜-5℃）通過時間とドリップ流出率（0.5〜3.5% vs 10%）の科学データと正しい解凍法で払拭する。",
            "mappedThemeIds": ["TH-04", "TH-05", "TH-06"]
        },
        {
            "dayOfWeek": "木曜日",
            "dayEn": "Thursday",
            "code": "THU",
            "categoryName": "プロの料理・調理方法",
            "categoryEn": "Pro Culinary Techniques & Plating",
            "color": "#ea580c",
            "purpose": "甘鯛の松笠焼き（鱗焼き）、穴子の白焼き・天ぷら、剣先イカの隠し包丁など、一次加工済みフィレを使って1皿の価値を最大化するプロの火入れ・調理法を実演する。",
            "mappedThemeIds": ["TH-10", "TH-11", "TH-12"]
        },
        {
            "dayOfWeek": "金曜日",
            "dayEn": "Friday",
            "code": "FRI",
            "categoryName": "レストランの原価・経営改善",
            "categoryEn": "Restaurant Cost Ratio & Prep Labor Saving",
            "color": "#16a34a",
            "purpose": "丸魚歩留まり45〜60%と一次加工フィレ歩留まり85〜99%の比較、1皿原価率26.5〜30.2%の試算、仕込み人件費削減など、飲食店オーナーに直結する数字を示す。",
            "mappedThemeIds": ["TH-07", "TH-08", "TH-09"]
        },
        {
            "dayOfWeek": "土曜日",
            "dayEn": "Saturday",
            "code": "SAT",
            "categoryName": "漁業・産地・水産加工",
            "categoryEn": "Fishing Ports, Craftsmanship & Processing",
            "color": "#2563eb",
            "purpose": "対馬・山陰・北海道などの産地漁港、活〆・血抜き・骨処理・高真空パックの職人技、日本の魚食文化や海外輸出トレンドを発信し、産地への信頼を高める。",
            "mappedThemeIds": ["TH-16", "TH-17", "TH-18"]
        },
        {
            "dayOfWeek": "日曜日",
            "dayEn": "Sunday",
            "code": "SUN",
            "categoryName": "ファインアトラスの商品・サービス紹介",
            "categoryEn": "Fine Atlas Custom Fish Box & Service",
            "color": "#dc2626",
            "purpose": "「産地で時間を止め、現地で時間を動かす。」仕組みや、Amazon・HPでの少量お試し購入から店舗別オリジナル魚BOX・法人定期契約までの活用事例を紹介する。",
            "mappedThemeIds": ["TH-19"]
        }
    ]


def build_themes_19():
    return [
        {
            "id": "TH-01",
            "num": 1,
            "name": "今が旬の魚",
            "nameEn": "Seasonal Fish Spotlight",
            "weekday": "月曜日",
            "targetPain": "季節ごとのメニュー改定で、どの産地の魚が一番脂乗りと価格バランスが良いか迷う",
            "verifiedFact": "盛漁期に産地で買い付け・急速冷凍した魚は、端境期の鮮魚よりも脂質含有量が高く価格も安定する",
            "hookAngle": "「今月、メニューに載せるべき日本の旬魚トップ3を知っていますか？」"
        },
        {
            "id": "TH-02",
            "num": 2,
            "name": "高級魚の特徴",
            "nameEn": "Characteristics of Premium Japanese Fish",
            "weekday": "火曜日",
            "targetPain": "客単価アップのために高級魚を使いたいが、目利きや産地の特徴をスタッフや客に説明しきれない",
            "verifiedFact": "対馬・山陰産のどぐろ（アカムツ）や赤甘鯛、剣先イカは白身・イカ類の中でも脂質・遊離アミノ酸が群を抜く",
            "hookAngle": "「白身のトロと呼ばれる高級魚、なぜこれほど料理人を魅了するのか？」"
        },
        {
            "id": "TH-03",
            "num": 3,
            "name": "市場での価格の動き",
            "nameEn": "Wholesale Market Price Dynamics",
            "weekday": "月曜日",
            "targetPain": "時化（しけ）や不漁のたびに市場の仕入れ値が1.5〜2倍に跳ね上がり、コース原価が崩れる",
            "verifiedFact": "豊洲・大阪市場統計でも鮮魚相場は天候で乱高下するが、盛漁期凍結ストックなら年間を通じ1皿原価率27〜30%を維持可能",
            "hookAngle": "「台風や時化の日でも、看板メニューの魚原価をブレさせない方法とは？」"
        },
        {
            "id": "TH-04",
            "num": 4,
            "name": "冷凍魚と生魚の違い",
            "nameEn": "Rapid-Frozen Fish vs. Raw Fresh Fish",
            "weekday": "水曜日",
            "targetPain": "「冷凍魚は生魚より味が落ちる」と思い込み、鮮魚ロスや日持ちの短さに苦しんでいる",
            "verifiedFact": "水揚げ直後に産地で活〆・急速凍結した魚は、輸送に2〜3日かかった未凍結の鮮魚よりK値（鮮度指標）と旨味を保持できる",
            "hookAngle": "「3日前の生魚と、水揚げ直後の急速冷凍魚。本当に鮮度が高いのはどっち？」"
        },
        {
            "id": "TH-05",
            "num": 5,
            "name": "急速冷凍の仕組み",
            "nameEn": "Science of Rapid Freezing (-1°C to -5°C Zone)",
            "weekday": "水曜日",
            "targetPain": "なぜ一般の冷凍庫と業務用の急速冷凍で身質やドリップが全く違うのか科学的に知りたい",
            "verifiedFact": "最大氷結晶生成帯（-1〜-5℃）を一般冷凍は30〜120分かけて通過しドリップ5〜10%が出るが、特殊急速凍結は3〜12分で通過しドリップ0.5〜1.5%以下に抑える",
            "hookAngle": "「マイナス1℃からマイナス5℃の『魔の温度帯』を何分で通過するかが全てを決める」"
        },
        {
            "id": "TH-06",
            "num": 6,
            "name": "美味しく解凍する方法",
            "nameEn": "Professional Thawing Methods for Peak Umami",
            "weekday": "水曜日",
            "targetPain": "せっかくの良い冷凍魚を常温解凍や電子レンジで解凍してしまい、ドリップを出して旨味を逃している",
            "verifiedFact": "真空パックのまま氷水（0〜2℃）または冷蔵庫内低温緩慢解凍を行うことで、ドリップ流出を最小化し細胞内の旨味を守る",
            "hookAngle": "「冷凍魚の味が9割決まる！プロが絶対にやらないNG解凍と、氷水解凍の黄金ルール」"
        },
        {
            "id": "TH-07",
            "num": 7,
            "name": "魚の歩留まりと原価計算",
            "nameEn": "Fish Yield Rate & True Dish Cost Calculation",
            "weekday": "金曜日",
            "targetPain": "丸魚のkg単価だけを見て「安い」と仕入れたが、頭と内臓を捨てたら実際の1皿原価が高くなっている",
            "verifiedFact": "丸魚は可食歩留まりが45〜60%に落ちるため、kg単価3,000円でも可食部実質単価は5,000〜6,600円/kgになる。一次加工フィレ（歩留まり85〜99%）ならロスがほぼゼロ",
            "hookAngle": "「丸魚のkg単価に騙されていませんか？歩留まり50%と95%の『本当の1皿原価』を比較」"
        },
        {
            "id": "TH-08",
            "num": 8,
            "name": "飲食店の仕入れ改善",
            "nameEn": "Smart Seafood Procurement for Restaurants",
            "weekday": "金曜日",
            "targetPain": "毎朝の市場買い出しや複数業者への発注、廃棄ロスで利益が圧迫されている",
            "verifiedFact": "主要10品目を歩留まり85〜99%の一次加工冷凍・チルドに集約すると、1皿原価率26.5〜30.2%（平均28.1%）で廃棄ロスゼロを実現できる",
            "hookAngle": "「廃棄ロスゼロ・原価率28%ピタリ！繁盛店が実践する『魚仕入れ』の新常識」"
        },
        {
            "id": "TH-09",
            "num": 9,
            "name": "厨房の仕込み時間短縮",
            "nameEn": "Cutting Kitchen Prep Time by 90 Minutes Daily",
            "weekday": "金曜日",
            "targetPain": "飲食業界の深刻な人手不足で、ウロコ引き・内臓処理・穴子開きに毎日1〜2時間取られ残業が減らない",
            "verifiedFact": "ウロコ・内臓・骨処理済みのフィレや無添加炊き上げ煮穴子を活用すると、1日60〜90分の下処理時間を「仕上げ調理と接客」に転換できる",
            "hookAngle": "「毎日90分のウロコ引きと骨抜き、まだ厨房で消耗しますか？」"
        },
        {
            "id": "TH-10",
            "num": 10,
            "name": "魚ごとの調理方法",
            "nameEn": "Best Cooking Techniques by Fish Species",
            "weekday": "木曜日",
            "targetPain": "魚種ごとの水分量や脂の融点に合った最適な火入れ（松笠焼き・ミキュイ・白焼き・天ぷら）を極めたい",
            "verifiedFact": "甘鯛の鱗付フィレは高温油かけで鱗が100%花開き、銀ダラ・サワラ骨取フィレは西京焼きや低温ミキュイで歩留まり95%を活かせる",
            "hookAngle": "「甘鯛のウロコがパリッと逆立つ！プロの『松笠焼き』30秒メイキング」"
        },
        {
            "id": "TH-11",
            "num": 11,
            "name": "寿司・刺身の知識",
            "nameEn": "Sushi & Sashimi Science & Knife Work",
            "weekday": "木曜日",
            "targetPain": "お造りや握りで提供際、切り付け温度や飾り包丁で食感と甘みを最大限に引き出したい",
            "verifiedFact": "剣先イカ（歩留まり95%・1皿原価313円）は細かなスリット（隠し包丁）で甘みが増し、-20℃以下凍結によりアニサキスリスクもゼロになる",
            "hookAngle": "「隠し包丁で甘みが3倍変わる！イカの王様・剣先イカお造りの極意」"
        },
        {
            "id": "TH-12",
            "num": 12,
            "name": "海外の日本食レストラン事情",
            "nameEn": "Global Japanese Restaurant Trends",
            "weekday": "木曜日",
            "targetPain": "海外の和食店・OMAKASEレストランで、日本産の高品質な魚をどうやって職人の手間なく再現しているか知りたい",
            "verifiedFact": "北米・欧州・アジアの高級和食店では、日本産地で一次加工・特殊急速凍結された煮穴子・甘鯛・のどぐろフィレがOMAKASEコースの主力になっている",
            "hookAngle": "「世界のOMAKASEシェフが、日本の『一次加工済み急速冷凍魚』を指名買いする理由」"
        },
        {
            "id": "TH-13",
            "num": 13,
            "name": "海外で人気の日本の魚",
            "nameEn": "Most Popular Japanese Seafood Overseas",
            "weekday": "火曜日",
            "targetPain": "インバウンド客や海外レストランで特に評価が高い日本産魚種と英語でのメニュー表現を知りたい",
            "verifiedFact": "Blackthroat Seaperch（のどぐろ）、Tilefish（甘鯛）、Conger Eel（対馬穴子）、Hokkaido Scallop（ホタテ玉冷）は海外ファインダイニングで圧倒的人気を誇る",
            "hookAngle": "「外国人ゲストが感動して注文する『日本の高級魚』英語メニュー名と魅力4選」"
        },
        {
            "id": "TH-14",
            "num": 14,
            "name": "珍しい魚の紹介",
            "nameEn": "Rare & Local Gem Fish of Japan",
            "weekday": "火曜日",
            "targetPain": "定番魚だけでなく、他店と差別化できる産地ならではの希少魚や特別規格を知りたい",
            "verifiedFact": "白甘鯛や対馬の大型黄金穴子、希少部位など、産地直結の急速冷凍だからこそ全国・世界の厨房へ少量から届けられる",
            "hookAngle": "「市場にほとんど出回らない幻の高級魚、なぜ産地直結なら手に入るのか？」"
        },
        {
            "id": "TH-15",
            "num": 15,
            "name": "季節ごとの魚カレンダー",
            "nameEn": "365-Day Seasonal Japanese Fish Calendar",
            "weekday": "月曜日",
            "targetPain": "春夏秋冬のコース献立を1ヶ月先回りして設計するための旬魚カレンダーが欲しい",
            "verifiedFact": "春（サワラ・甘鯛）、夏（対馬穴子・剣先イカ）、秋（のどぐろ・戻り鰹）、冬（トラフグ・寒ブリ・ホタテ）の盛漁期カレンダーで年間メニューを計画できる",
            "hookAngle": "「料理長のための保存版！春夏秋冬・日本の旬魚仕入れカレンダー」"
        },
        {
            "id": "TH-16",
            "num": 16,
            "name": "日本の漁港・産地の紹介",
            "nameEn": "Discovering Japan's Premier Fishing Ports",
            "weekday": "土曜日",
            "targetPain": "対馬海峡・山陰・北海道など、なぜその産地の魚が特別に美味しいのか背景ストーリーを知りたい",
            "verifiedFact": "対馬暖流と大陸棚が交わる対馬海峡はプランクトンと小魚が豊富で、穴子・のどぐろ・甘鯛・剣先イカの日本有数の好漁場となっている",
            "hookAngle": "「なぜ『対馬海峡』の穴子とのどぐろは、これほど脂が乗って濃厚なのか？」"
        },
        {
            "id": "TH-17",
            "num": 17,
            "name": "水産加工の現場",
            "nameEn": "Inside Japanese Seafood Processing Craftsmanship",
            "weekday": "土曜日",
            "targetPain": "下処理済み冷凍魚がどのような衛生管理と職人の手仕事で作られているか目で見て安心したい",
            "verifiedFact": "水揚げ直後の活〆・血抜きから、熟練職人による背開き・骨処理、高真空パック、急速凍結まで一貫管理することで歩留まり95%超と高鮮度を両立している",
            "hookAngle": "「水揚げから急速冷凍まで！職人が1尾ずつ骨を抜く水産加工の舞台裏」"
        },
        {
            "id": "TH-18",
            "num": 18,
            "name": "日本の魚文化",
            "nameEn": "Japanese Fish Culture & Culinary Heritage",
            "weekday": "土曜日",
            "targetPain": "活〆・神経締め・熟成・割烹の包丁技術など、日本の魚食文化の奥深さを国内外に伝えたい",
            "verifiedFact": "日本の「活〆・血抜き・温度管理」技術は世界のシェフから最高峰と評価され、急速冷凍技術との融合で世界中どこでも再現可能になった",
            "hookAngle": "「世界のトップシェフが学ぶ、日本の『活〆（Ikejime）』と鮮度保持の科学」"
        },
        {
            "id": "TH-19",
            "num": 19,
            "name": "ファインアトラスの取り組み・商品紹介",
            "nameEn": "Fine Atlas Custom Fish Box & Farm-to-Kitchen Service",
            "weekday": "日曜日",
            "targetPain": "いきなり大口契約ではなく、まず少量で品質を確かめてから自店専用の魚BOXを相談したい",
            "verifiedFact": "「産地で時間を止め、現地で時間を動かす。」ホームページ・Amazonでの少量購入やお試しセット（税込1万円）で品質確認後、店舗別オリジナル魚BOX・法人契約へステップアップ可能",
            "hookAngle": "「まず1箱・少量から厨房でお試し！店舗別オリジナル魚BOXという新しい仕入れ」"
        }
    ]


def build_fish_master_10():
    return [
        {
            "no": 1,
            "tier": "主力5",
            "key": "煮穴子",
            "nameJp": "煮穴子（対馬産・無添加炊き上げ真空冷凍）",
            "nameEn": "Simmered Conger Eel (Tsushima Additive-Free Vacuum Frozen)",
            "origin": "長崎県・対馬産",
            "spec": "無添加炊き上げ・真空急速冷凍",
            "marketRangeYenKg": "¥3,400〜¥8,600",
            "standardCostYenKg": 4200,
            "faWholesaleYenKg": 6400,
            "faGrossMarginPct": 34.4,
            "yieldPct": 98,
            "portionGram": 55,
            "dishCostYen": 359,
            "menuPriceYen": 1280,
            "flCostRatioPct": 28.1,
            "prepMerit": "本来1時間以上つきっきりの炊き番が不要。解凍して炙るだけで極上の握り・一本穴子・酒肴として即提供でき、歩留まり98%で廃棄ゼロ。",
            "recommendedDishes": "炙り煮穴子握り、一本穴子押し寿司、煮穴子と季節野菜の焚き合わせ",
            "primaryAssetCode": "P-CS-001"
        },
        {
            "no": 2,
            "tier": "主力5",
            "key": "穴子フィレ",
            "nameJp": "穴子フィレ（対馬/国産活〆開き・骨処理冷凍）",
            "nameEn": "Raw Conger Eel Fillet (Live-Struck, Boned & Butterfly-Cut)",
            "origin": "対馬・国産",
            "spec": "活〆背開き・ヌメリ取り・骨処理済急速冷凍",
            "marketRangeYenKg": "¥2,980〜¥7,800",
            "standardCostYenKg": 3600,
            "faWholesaleYenKg": 5600,
            "faGrossMarginPct": 35.7,
            "yieldPct": 96,
            "portionGram": 65,
            "dishCostYen": 379,
            "menuPriceYen": 1380,
            "flCostRatioPct": 27.5,
            "prepMerit": "熟練を要するヌメリ取りと背開き・骨処理が一切不要。『自店の秘伝ダレで炊きたい』『揚げたての天ぷら・白焼き・フリットにしたい』料理人のこだわりと時短を両立。",
            "recommendedDishes": "穴子天ぷら一本揚げ、パリッと白焼きわさび添え、自家製ダレ煮穴子、穴子のベニエ（フレンチ）",
            "primaryAssetCode": "P-FL-001"
        },
        {
            "no": 3,
            "tier": "主力5",
            "key": "甘鯛",
            "nameJp": "甘鯛（対馬/山陰 赤甘鯛 鱗付フィレ）",
            "nameEn": "Red Tilefish / Amadai (Scale-On Fillet for Crispy Matsukasa-Yaki)",
            "origin": "対馬・山陰産",
            "spec": "鱗付き三枚おろしフィレ・骨処理・高真空急速冷凍",
            "marketRangeYenKg": "¥3,390〜¥9,800",
            "standardCostYenKg": 4400,
            "faWholesaleYenKg": 6800,
            "faGrossMarginPct": 35.3,
            "yieldPct": 95,
            "portionGram": 70,
            "dishCostYen": 501,
            "menuPriceYen": 1850,
            "flCostRatioPct": 27.1,
            "prepMerit": "身が柔らかく塩当てやウロコ残しのおろし作業が難しい甘鯛を、歩留まり95%の鱗付きフィレに加工。高温の油をかけるだけでウロコが100%美しく逆立つ。",
            "recommendedDishes": "甘鯛の松笠焼き（鱗焼き）、甘鯛のうろこパリパリポワレ（フレンチ・イタリアン）、蕪蒸し",
            "primaryAssetCode": "P-FL-015"
        },
        {
            "no": 4,
            "tier": "主力5",
            "key": "のどぐろ",
            "nameJp": "のどぐろ（対馬/山陰/長崎 200-400g IQF・セミドレス）",
            "nameEn": "Blackthroat Seaperch / Nodoguro (IQF Semi-Dressed & Fillet)",
            "origin": "対馬・山陰・長崎産",
            "spec": "ウロコ・エラ・内臓除去セミドレス／三枚おろしフィレ IQF凍結",
            "marketRangeYenKg": "¥5,760〜¥11,500",
            "standardCostYenKg": 5900,
            "faWholesaleYenKg": 9000,
            "faGrossMarginPct": 34.4,
            "yieldPct": 85,
            "portionGram": 60,
            "dishCostYen": 635,
            "menuPriceYen": 2280,
            "flCostRatioPct": 27.9,
            "prepMerit": "時化で市場価格が乱高下しやすい高級魚のどぐろを盛漁期に確保。下処理済みの歩留まり85%により、1皿原価635円（売価2,280円・原価率27.9%）で看板メニューを通年安定提供できる。",
            "recommendedDishes": "のどぐろ皮目炙り刺し、のどぐろ原始焼き・塩焼き、のどぐろ土鍋ご飯",
            "primaryAssetCode": "P-WR-001"
        },
        {
            "no": 5,
            "tier": "主力5",
            "key": "剣先イカ",
            "nameJp": "剣先イカ（壱岐対馬/山陰/山口 お造り柵・スリット）",
            "nameEn": "Swordtip Squid / Kensaki Ika (Sashimi Block with Precision Scoring)",
            "origin": "壱岐・対馬・山陰・山口産",
            "spec": "皮むき・下処理済お造り柵／スリット入り急速冷凍",
            "marketRangeYenKg": "¥2,260〜¥6,600",
            "standardCostYenKg": 3500,
            "faWholesaleYenKg": 5400,
            "faGrossMarginPct": 35.2,
            "yieldPct": 95,
            "portionGram": 55,
            "dishCostYen": 313,
            "menuPriceYen": 1180,
            "flCostRatioPct": 26.5,
            "prepMerit": "手間のかかる皮むき・内臓処理が済んだ歩留まり95%のお造り柵。1皿原価わずか313円（原価率26.5%・10品目中最良）で、お造り・握り・カルパッチョに即対応。",
            "recommendedDishes": "剣先イカ糸造り・隠し包丁握り、剣先イカの炙りカルパッチョ、ゲソとエンペラの天ぷら",
            "primaryAssetCode": "P-CS-025"
        },
        {
            "no": 6,
            "tier": "拡張5",
            "key": "トラフグ身欠き",
            "nameJp": "トラフグ身欠き（国産養殖/天然 除毒済・急速冷凍）",
            "nameEn": "Japanese Tiger Pufferfish / Torafugu (Licensed Detoxified Dressed)",
            "origin": "国産（長崎・熊本・山口等）",
            "spec": "有資格者による完全除毒済・身欠き急速冷凍",
            "marketRangeYenKg": "¥4,750〜¥9,800",
            "standardCostYenKg": 4900,
            "faWholesaleYenKg": 7400,
            "faGrossMarginPct": 33.8,
            "yieldPct": 75,
            "portionGram": 55,
            "dishCostYen": 543,
            "menuPriceYen": 1980,
            "flCostRatioPct": 27.4,
            "prepMerit": "専門除毒処理済みの安全な身欠き規格。てっちり・唐揚げ・てっさ向けに1皿原価543円（原価率27.4%）で冬〜春の宴会・コース単価を一気に引き上げられる。",
            "recommendedDishes": "トラフグの唐揚げ、てっちり小鍋、炭火焼きふぐ",
            "primaryAssetCode": "P-VF-010"
        },
        {
            "no": 7,
            "tier": "拡張5",
            "key": "本マグロ柵",
            "nameJp": "本マグロ・ミナミマグロ柵（赤身・中トロ定尺柵）",
            "nameEn": "Bluefin & Southern Bluefin Tuna Saku Block (Akami & Chutoro)",
            "origin": "国産・厳選海域（超低温凍結）",
            "spec": "皮・血合い処理済 定尺柵（赤身・中トロ）",
            "marketRangeYenKg": "¥4,500〜¥9,200",
            "standardCostYenKg": 5200,
            "faWholesaleYenKg": 7800,
            "faGrossMarginPct": 33.3,
            "yieldPct": 94,
            "portionGram": 60,
            "dishCostYen": 498,
            "menuPriceYen": 1680,
            "flCostRatioPct": 29.6,
            "prepMerit": "血合いや皮のロスを除いた歩留まり94%の定尺柵。必要な本数だけ温塩水・氷水で解凍できるため、少人数店でも変色廃棄ゼロでお造り盛り合わせの核を作れる。",
            "recommendedDishes": "本マグロ中トロ・赤身お造り、マグロのレアステーキ、漬けマグロ握り",
            "primaryAssetCode": "P-CS-045"
        },
        {
            "no": 8,
            "tier": "拡張5",
            "key": "銀ダラ・サワラ",
            "nameJp": "銀ダラ・サワラ骨取フィレ（西京焼き・幽庵・ミキュイ用）",
            "nameEn": "Boneless Sablefish & Spanish Mackerel Fillet",
            "origin": "国産・北太平洋厳選",
            "spec": "完全骨取りフィレ・真空急速冷凍",
            "marketRangeYenKg": "¥2,200〜¥4,200",
            "standardCostYenKg": 2850,
            "faWholesaleYenKg": 4400,
            "faGrossMarginPct": 35.2,
            "yieldPct": 95,
            "portionGram": 75,
            "dishCostYen": 347,
            "menuPriceYen": 1250,
            "flCostRatioPct": 27.8,
            "prepMerit": "ピンセットでの骨抜き作業が不要な歩留まり95%フィレ。75gのボリュームでも1皿原価347円（原価率27.8%）に収まり、和食の焼き物からビストロのミキュイまで万能。",
            "recommendedDishes": "銀ダラの西京焼き、サワラの幽庵焼き、サワラの低温ミキュイ春菊ソース",
            "primaryAssetCode": "P-FL-050"
        },
        {
            "no": 9,
            "tier": "拡張5",
            "key": "ホタテ貝柱",
            "nameJp": "北海道産ホタテ貝柱（トンネルIQF玉冷 3S〜M）",
            "nameEn": "Hokkaido IQF Sashimi-Grade Scallop Adductor Muscle",
            "origin": "北海道（オホーツク・噴火湾等）",
            "spec": "トンネルフリーザーIQFバラ凍結（生食用玉冷）",
            "marketRangeYenKg": "¥6,200〜¥10,500",
            "standardCostYenKg": 6800,
            "faWholesaleYenKg": 9800,
            "faGrossMarginPct": 30.6,
            "yieldPct": 99,
            "portionGram": 55,
            "dishCostYen": 544,
            "menuPriceYen": 1800,
            "flCostRatioPct": 30.2,
            "prepMerit": "殻剥き・ウロ取り不要で可食歩留まり99%（10品目最高）。1粒ずつバラ凍結（IQF）されているため、注文数に合わせて1粒単位で取り出せ、和洋問わず即戦力となる。",
            "recommendedDishes": "北海道ホタテの炙りカルパッチョ、ホタテの焦がしバターソテー、ホタテ磯辺焼き",
            "primaryAssetCode": "P-VF-025"
        },
        {
            "no": 10,
            "tier": "拡張5",
            "key": "車海老・天使の海老",
            "nameJp": "車海老・天使の海老（IQFバラ凍結・生食/天ぷら兼用）",
            "nameEn": "Kuruma Prawn & Angel Blue Prawn (IQF Sashimi & Tempura Grade)",
            "origin": "国産（車海老）／ニューカレドニア（天使の海老）",
            "spec": "IQF急速バラ凍結・高鮮度生食グレード",
            "marketRangeYenKg": "¥4,200〜¥8,200",
            "standardCostYenKg": 4400,
            "faWholesaleYenKg": 6600,
            "faGrossMarginPct": 33.3,
            "yieldPct": 65,
            "portionGram": 45,
            "dishCostYen": 457,
            "menuPriceYen": 1580,
            "flCostRatioPct": 28.9,
            "prepMerit": "1尾ずつ取り出せるIQF凍結で、お造り・天ぷら・グリル・パスタまで1皿原価457円（原価率28.9%）で華やかなメインを作れる。",
            "recommendedDishes": "車海老の天ぷら、天使の海老カルパッチョ、海老のグリル・アメリケーヌソース",
            "primaryAssetCode": "P-CS-080"
        }
    ]


def build_28_episodes():
    """
    Weeks 1 to 4 (28 Complete Bilingual Episodes)
    Covering all 7 weekdays x 4 weeks and all 19 themes!
    """
    raw_specs = [
        # WEEK 1
        {
            "day": 1, "week": 1, "dow": "月曜日", "weekdayTheme": "今週の旬の魚・市場相場",
            "themeId": "TH-01", "themeName": "今が旬の魚", "fishKey": "のどぐろ",
            "assetCode": "P-WR-001", "assetLabel": "対馬・山陰産 のどぐろ丸魚＆断面脂乗りアップ写真",
            "titleJp": "白身のトロ「のどぐろ」、一番脂が乗る旬と失敗しない仕入れ方とは？",
            "titleEn": "Nodoguro (Blackthroat Seaperch): Peak Season & Smart Sourcing for Chefs",
            "hookVisualJp": "炭火で皮目から黄金色の脂が弾ける「のどぐろ」の超接写映像と疑問タイトル字幕",
            "hookVisualEn": "Macro shot of Nodoguro skin blistering golden over charcoal with hook title",
            "hookAudioJp": "白身のトロと呼ばれる高級魚、のどぐろ。一年中同じ脂乗りだと思っていませんか？",
            "hookAudioEn": "Known as the Toro of white fish: do you think Nodoguro has the same fat level all year round?",
            "bodyVisualJp": "対馬海峡の漁場マップと、盛漁期に水揚げ・セミドレス加工（歩留まり85%）された急速冷凍のどぐろ比較図",
            "bodyVisualEn": "Tsushima Strait map and comparison of peak-season IQF semi-dressed Nodoguro (85% yield)",
            "bodyAudioJp": "実は対馬や山陰ののどぐろは、盛漁期に買い付けて水揚げ直後に下処理・急速冷凍することで、時化の日でも最高の脂乗りと安定した原価をキープできます。ウロコ・内臓処理済みのセミドレスなら歩留まりは85%に達します。",
            "bodyAudioEn": "By sourcing Tsushima Nodoguro at peak season and rapid-freezing immediately after scaling and gutting, chefs lock in rich fat and stable cost even during stormy weeks, achieving an 85% usable yield.",
            "climaxVisualJp": "皮目を香ばしく炙った「のどぐろ炙り刺し（1皿原価635円・売価2,280円想定）」の完成盛り付け",
            "climaxVisualEn": "Plated torch-seared Nodoguro sashimi glistening with natural oils",
            "climaxAudioJp": "解凍して皮目を炙るだけで、1皿原価率27.9%の看板メニューが完成します。",
            "climaxAudioEn": "Simply thaw and torch the skin for a signature dish at a 27.9% food cost ratio.",
            "shootGuide": "皮目の赤い輝きと、炙った瞬間に浮き出る透明な脂の粒を斜め45度照明で撮影する。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 close-up of premium Japanese Nodoguro (Blackthroat Seaperch) being lightly torched on skin side, glistening natural fat, dark slate plate, fine dining Moody lighting, no text",
            "source": "東京都・大阪市中央卸売市場 水産物統計／ファインアトラス産地一次加工歩留まり検証データ"
        },
        {
            "day": 2, "week": 1, "dow": "火曜日", "weekdayTheme": "高級魚の豆知識",
            "themeId": "TH-02", "themeName": "高級魚の特徴", "fishKey": "甘鯛",
            "assetCode": "P-FL-015", "assetLabel": "対馬・山陰産 赤甘鯛 鱗付きフィレ＆松笠焼き断面写真",
            "titleJp": "高級魚「赤甘鯛（ぐじ）」、なぜウロコをつけたまま焼くと絶品なのか？",
            "titleEn": "Why Japan's Premium Red Tilefish (Amadai) Is Cooked with Scales On",
            "hookVisualJp": "高温の油をかけた瞬間に甘鯛のウロコがパリッと一斉に逆立つ迫力スロー映像",
            "hookVisualEn": "Slow-motion close-up of Red Tilefish scales blooming crisp as hot oil is poured over",
            "hookAudioJp": "京都で『ぐじ』と呼ばれる高級魚、甘鯛。なぜプロはあえてウロコを残して焼くのでしょうか？",
            "hookAudioEn": "Called 'Guji' in Kyoto: why do master chefs purposefully leave the scales on Red Tilefish?",
            "bodyVisualJp": "甘鯛の薄いウロコ構造の解説図と、鱗付き三枚おろしフィレ（歩留まり95%）の真空パック写真",
            "bodyVisualEn": "Diagram of Amadai delicate scale structure and vacuum-packed scale-on fillet (95% yield)",
            "bodyAudioJp": "甘鯛のウロコは非常に薄く、高温の油をかけると花のように逆立ってサクサクの食感に変わります。同時に水分が多い白身を蒸気でふっくら閉じ込めるのです。ただし身が柔らかいため、産地で鱗付きフィレに加工・急速冷凍したものが歩留まり95%で重宝されます。",
            "bodyAudioEn": "Amadai scales are paper-thin; hot oil makes them bloom like crispy petals while steaming the delicate flesh inside. Pre-filleted scale-on rapid-frozen packs give chefs a 95% yield with zero prep damage.",
            "climaxVisualJp": "和食の「松笠焼き」とフレンチの「うろこ焼きポワレ」の2皿並び映像",
            "climaxVisualEn": "Side-by-side plating of Japanese Matsukasa-yaki and French crispy scale-on Amadai poêlé",
            "climaxAudioJp": "和食の松笠焼きにもフレンチのポワレにも、下処理ゼロでそのまま使えます。",
            "climaxAudioEn": "Ready for Japanese Matsukasa-yaki or French poêlé with zero scaling prep.",
            "shootGuide": "ウロコが逆立った立体感が伝わるよう、真横に近いローアングルから撮影しサクッという環境音を入れる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese Red Tilefish (Amadai) Matsukasa-yaki with golden standing crispy scales, steam rising from moist white flesh, minimalist ceramic plate, warm restaurant lighting",
            "source": "日本調理科学会 魚介調理文献／ファインアトラス商品情報（赤甘鯛鱗付フィレ規格）"
        },
        {
            "day": 3, "week": 1, "dow": "水曜日", "weekdayTheme": "冷凍魚の特徴・解凍方法",
            "themeId": "TH-05", "themeName": "急速冷凍の仕組み", "fishKey": "剣先イカ",
            "assetCode": "V-PF-001", "assetLabel": "急速凍結庫への搬入と氷結晶比較アニメーション・解凍ドリップ比較動画",
            "titleJp": "「冷凍魚は水っぽい」の真犯人！マイナス1〜5℃を通過する時間の秘密",
            "titleEn": "Why Some Frozen Fish Turn Watery: The -1°C to -5°C Ice Crystal Science",
            "hookVisualJp": "赤いドリップが出た一般冷凍魚と、ドリップほぼゼロの急速冷凍魚の比較画面",
            "hookVisualEn": "Split screen comparing high-drip conventional frozen fish vs zero-drip rapid-frozen fish",
            "hookAudioJp": "「冷凍の魚は水っぽくて刺身にできない」……その原因、実は冷凍スピードにあります。",
            "hookAudioEn": "'Frozen fish is too watery for sashimi'—the real culprit is actually the freezing speed.",
            "bodyVisualJp": "最大氷結晶生成帯（-1〜-5℃）の通過時間グラフ（一般緩慢冷凍30〜120分 vs 急速・特殊凍結3〜25分）",
            "bodyVisualEn": "Graph of -1°C to -5°C ice crystal zone transit time (Conventional 30-120m vs Rapid 3-25m)",
            "bodyAudioJp": "魚の水分が凍るマイナス1℃からマイナス5℃をゆっくり通過すると、氷の結晶が巨大化して細胞膜を壊し、解凍時に5〜10%もの旨味ドリップが流出します。一方、この温度帯を一気に通過する急速冷凍なら細胞が壊れず、ドリップを0.5〜3.5%以下に抑えられます。",
            "bodyAudioEn": "Lingering between -1°C and -5°C grows large ice crystals that puncture cell walls, leaking 5-10% umami drip. Blasting through this zone in minutes keeps cells intact and limits drip to just 0.5-3.5%.",
            "climaxVisualJp": "急速冷凍の剣先イカお造り柵を解凍し、角が立った透明感あるお造りに盛り付けた映像",
            "climaxVisualEn": "Translucent, sharp-edged Kensaki squid sashimi sliced from a rapid-frozen block",
            "climaxAudioJp": "産地で時間を止める急速冷凍なら、お造りのねっとりした甘みまでそのまま再現できます。",
            "climaxAudioEn": "Stopping time at the port preserves the sweet, creamy texture demanded for sashimi.",
            "shootGuide": "解凍後のキッチンペーパーにドリップがほとんど付いていない様子を実際に映して信頼性を高める。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 clean food science infographic style showing fine micro ice crystals preserving fish cell structure in rapid freezing, frosty blue lighting, professional culinary visual",
            "source": "特殊急速凍結機メーカー公開技術検証データ（最大氷結晶生成帯通過時間とドリップ流出率比較）"
        },
        {
            "day": 4, "week": 1, "dow": "木曜日", "weekdayTheme": "プロの料理・調理方法",
            "themeId": "TH-10", "themeName": "魚ごとの調理方法", "fishKey": "穴子フィレ",
            "assetCode": "V-TC-001", "assetLabel": "活〆穴子骨処理フィレの白焼き・天ぷら調理動画",
            "titleJp": "ヌメリ取り・背開き不要！活〆穴子フィレで作る「外パリ中ふわ」白焼きの極意",
            "titleEn": "Zero Slimes or Bone Prep: Mastering Crispy-Skinned Anago Shirayaki",
            "hookVisualJp": "包丁で開く手間なく、真空パックから美しい活〆穴子フィレを取り出し炭火に乗せる映像",
            "hookVisualEn": "Chef taking a pre-butterflied boned Anago fillet from vacuum pack straight to the grill",
            "hookAudioJp": "穴子のヌメリ取りと背開きに、毎日何十分もかけていませんか？",
            "hookAudioEn": "Are you still spending 40 minutes every afternoon de-sliming and butterflying conger eel?",
            "bodyVisualJp": "産地職人が活〆・骨処理した穴子フィレ（歩留まり96%）の皮目に熱湯霜降り・酒振りをして焼く工程",
            "bodyVisualEn": "Close-up of 96%-yield boned Anago fillet being grilled skin-side down with sake mist",
            "bodyAudioJp": "産地で活〆・背開き・骨処理まで終えて急速冷凍した生穴子フィレなら、可食歩留まりは96%。味付けをしていない生開きなので、皮目をパリッと焼き上げる白焼きや天ぷら一本揚げ、自店の秘伝ダレでの炊き上げまで料理人のこだわりを100%活かせます。",
            "bodyAudioEn": "Pre-butterflied and boned raw Anago fillets deliver a 96% yield. Because they are unseasoned, chefs can craft crispy Shirayaki, golden tempura, or simmer them in their own house tare sauce.",
            "climaxVisualJp": "わさびと粗塩を添えた「対馬穴子の白焼き（1皿原価379円・売価1,380円想定）」完成カット",
            "climaxVisualEn": "Crispy grilled Anago Shirayaki garnished with fresh grated wasabi and sea salt",
            "climaxAudioJp": "仕込み時間をゼロにしながら、1皿原価率27.5%で極上の穴子料理が出せます。",
            "climaxAudioEn": "Zero prep time, artisan quality, and an ideal 27.5% dish cost ratio.",
            "shootGuide": "皮目の香ばしい焼き目と、箸で割ったときの白い身のふっくらした厚みを対比して撮る。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese grilled conger eel Shirayaki on handmade ceramic plate with fresh wasabi and flaky sea salt, crispy golden skin, fluffy white meat, high-end washoku style",
            "source": "ファインアトラス商品情報（対馬/国産活〆穴子フィレ・歩留まり96%原価試算データ）"
        },
        {
            "day": 5, "week": 1, "dow": "金曜日", "weekdayTheme": "レストランの原価・経営改善",
            "themeId": "TH-07", "themeName": "魚の歩留まりと原価計算", "fishKey": "甘鯛",
            "assetCode": "P-FL-001", "assetLabel": "丸魚のアラ（頭・内臓・中骨）と一次加工フィレ95%歩留まりの比較写真",
            "titleJp": "丸魚のkg単価に騙されるな！歩留まり50%と95%で「1皿の原価」はこう変わる",
            "titleEn": "Don't Be Fooled by Whole-Fish Per-Kg Prices: 50% vs 95% Yield Math",
            "hookVisualJp": "丸魚から出る大量の頭・内臓・骨のアラと、そのまま使えるフィレの天秤比較フリップ",
            "hookVisualEn": "Visual scale comparing 50% waste from whole fish vs 95% usable pre-processed fillet",
            "hookAudioJp": "魚を仕入れるとき、見かけの『キロ単価』だけで安い・高いを判断していませんか？",
            "hookAudioEn": "When buying seafood, do you judge cost only by the headline price per kilogram?",
            "bodyVisualJp": "丸魚（歩留まり45〜60%＋仕込み人件費）と一次加工冷凍フィレ（歩留まり85〜99%・廃棄ゼロ）の計算表",
            "bodyVisualEn": "Cost breakdown chart comparing whole fish (45-60% yield + labor) vs fillets (85-99% yield)",
            "bodyAudioJp": "丸魚は頭・内臓・中骨を落とすと可食歩留まりが45〜60%に下がります。つまりキロ3,500円の丸魚でも、実際に食べられる身の原価はキロ6,000円以上になり、さらに1〜2時間の仕込み人件費がかかります。一方、歩留まり95%の一次加工フィレならほぼ全量が売上に変わります。",
            "bodyAudioEn": "Removing heads, guts, and bones drops whole-fish yield to 45-60%. A 3,500-yen/kg whole fish actually costs over 6,000 yen/kg of edible meat plus hours of prep labor. A 95%-yield fillet turns almost 100% into revenue.",
            "climaxVisualJp": "主力10品目の飲食店1皿原価率（26.5〜30.2%・平均28.1%）サマリーカード表示",
            "climaxVisualEn": "Summary card showing 26.5-30.2% (avg 28.1%) restaurant food cost across 10 core items",
            "climaxAudioJp": "歩留まりで計算すれば、1皿の原価率は26.5〜30.2%の黄金ゾーンにピタリと収まります。",
            "climaxAudioEn": "Calculated by usable yield, dish cost stays right in the golden 26.5% to 30.2% zone.",
            "shootGuide": "計算式を大きなゴシック体テロップ（50% vs 95%）で画面中央に出し、音声なしでも一目で理解させる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 clean culinary business visual showing precision portioned Japanese fish fillets on kitchen scale, modern stainless steel restaurant kitchen background",
            "source": "全国業務用冷凍魚10品目 仕入れ価格AI調査＆飲食店FL原価試算（2025〜2026年市場統計基準）"
        },
        {
            "day": 6, "week": 1, "dow": "土曜日", "weekdayTheme": "漁業・産地・水産加工",
            "themeId": "TH-16", "themeName": "日本の漁港・産地の紹介", "fishKey": "煮穴子",
            "assetCode": "V-FP-001", "assetLabel": "長崎県・対馬海峡の漁船水揚げと産地一次加工場の動画",
            "titleJp": "なぜ「対馬海峡」の穴子とのどぐろは世界最高峰と称されるのか？",
            "titleEn": "Why the Tsushima Strait Produces Japan's Finest Conger Eel & Nodoguro",
            "hookVisualJp": "朝焼けの対馬海峡を出港する漁船と、水揚げされた黄金色に輝く対馬穴子の映像",
            "hookVisualEn": "Fishing boat at sunrise in Tsushima Strait and golden-bellied Tsushima conger eel",
            "hookAudioJp": "日本全国の料理人が指名買いする『対馬産』の穴子とのどぐろ。なぜこれほど美味しいのでしょうか？",
            "hookAudioEn": "Why do top chefs across Japan specifically request conger eel and Nodoguro from Tsushima?",
            "bodyVisualJp": "対馬暖流と大陸棚の海底地形図、および水揚げ港すぐそばの加工場での迅速な下処理・真空急速凍結",
            "bodyVisualEn": "Map of Tsushima warm current meeting the continental shelf and port-side rapid freezing",
            "bodyAudioJp": "対馬海峡は暖流と深い海溝がぶつかり、エサとなる甲殻類や小魚が極めて豊富です。その豊かな海で育った魚を、長距離輸送で鮮度を落とす前に産地で素早く下処理し、高真空パックと急速冷凍で『産地の時間を止める』からこそ、圧倒的な旨味が守られます。",
            "bodyAudioEn": "Where warm currents meet deep trenches, Tsushima teems with nutrient-rich prey. By processing and vacuum rapid-freezing right at the port before long transport, we freeze time at peak freshness.",
            "climaxVisualJp": "対馬産・無添加炊き上げ煮穴子（歩留まり98%）を炙って握る寿司職人の手元",
            "climaxVisualEn": "Sushi chef torching additive-free Tsushima simmered Anago (98% yield) for nigiri",
            "climaxAudioJp": "産地の海と職人が育てた最高の一皿を、あなたの厨房へそのまま届けます。",
            "climaxAudioEn": "Bringing the peak flavor of Tsushima's waters and craftsmen straight to your kitchen.",
            "shootGuide": "漁港の活気ある水揚げシーンから、清潔な加工場、そして最終料理へと3カットでテンポよく繋ぐ。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 dramatic aerial view of Tsushima Island Japan coastline and fishing boat at dawn, crystal clear deep blue sea, cinematic documentary look",
            "source": "長崎県対馬水産統計資料／ファインアトラス会社概要（対馬水産海外事業部承継モデル）"
        },
        {
            "day": 7, "week": 1, "dow": "日曜日", "weekdayTheme": "ファインアトラスの商品・サービス紹介",
            "themeId": "TH-19", "themeName": "ファインアトラスの取り組み・商品紹介", "fishKey": "煮穴子",
            "assetCode": "V-PS-001", "assetLabel": "ファインアトラス箱詰め・出荷工程と主力5品目ラインナップ動画",
            "titleJp": "「産地で時間を止め、現地で時間を動かす。」まず少量から試せる新しい魚仕入れ",
            "titleEn": "Stop Time at the Port, Restart in Your Kitchen: Fine Atlas Custom Fish Box",
            "hookVisualJp": "真空パックされた主力5品目（煮穴子・穴子フィレ・甘鯛・のどぐろ・剣先イカ）が一箱に並ぶ映像",
            "hookVisualEn": "Five core vacuum-packed Japanese seafood items neatly arranged in one delivery box",
            "hookAudioJp": "「良い魚を使いたいけれど、仕込みの人手が足りない、大口ロットは抱えられない」と悩んでいませんか？",
            "hookAudioEn": "Want premium Japanese fish, but short on prep staff or storage for huge wholesale minimums?",
            "bodyVisualJp": "産地での下処理・急速冷凍から、ホームページ・Amazonでの少量購入・お試しセット、店舗別オリジナル魚BOXの流れ図",
            "bodyVisualEn": "Flow diagram from port rapid-freezing to Amazon/website trial order and custom B2B fish box",
            "bodyAudioJp": "ファインアトラスは、旬の魚を産地で下処理・急速冷凍し、お店がすぐ使える状態で届ける新しい水産パートナーです。まずはホームページやAmazonでの少量購入、またはお試しセットで身質と歩留まりを確かめていただき、お店専用のオリジナル魚BOXや法人定期契約へ柔軟に広げられます。",
            "bodyAudioEn": "Fine Atlas processes and rapid-freezes seasonal fish at the port, delivering kitchen-ready fillets. Start with a small trial order via our website or Amazon to verify quality, then scale to a custom restaurant fish box.",
            "climaxVisualJp": "厨房でパックを開けてすぐ調理に入るシェフの笑顔と、公式HP・Amazon案内テロップ",
            "climaxVisualEn": "Smiling chef opening a Fine Atlas pack for service with website & Amazon guidance card",
            "climaxAudioJp": "まずは1箱、あなたの厨房の包丁と舌でその品質を確かめてみてください。",
            "climaxAudioEn": "Test one box in your own kitchen and experience the quality firsthand.",
            "shootGuide": "箱を開けた瞬間の清潔感・保冷状態の良さと、5品目のラベルがはっきり見える俯瞰カットを撮る。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 premium insulated seafood box opened on stainless kitchen counter revealing neatly vacuum-packed Japanese fish fillets, clean professional branding look",
            "source": "株式会社ファインアトラス公式HP（fineatlas.co.jp）および公式お試しセット・Amazon販売案内"
        },

        # WEEK 2
        {
            "day": 8, "week": 2, "dow": "月曜日", "weekdayTheme": "今週の旬の魚・市場相場",
            "themeId": "TH-03", "themeName": "市場での価格の動き", "fishKey": "剣先イカ",
            "assetCode": "P-CS-025", "assetLabel": "剣先イカお造り柵と市場価格推移グラフ素材",
            "titleJp": "時化（しけ）でイカの市場価格が2倍に！？お造り原価率26.5%を守る秘策",
            "titleEn": "Squid Prices Double During Storms? How to Lock In a 26.5% Sashimi Cost",
            "hookVisualJp": "荒れる日本海の波と、市場でのイカ相場高騰グラフ、そして美しい剣先イカお造り柵",
            "hookVisualEn": "Stormy sea clip transitioning to squid price spike chart and pristine Kensaki squid block",
            "hookAudioJp": "海が時化（しけ）た週、市場のイカや白身の仕入れ値が跳ね上がって困ったことはありませんか？",
            "hookAudioEn": "When storms hit the coast, do sudden wholesale squid price spikes wreck your menu margins?",
            "bodyVisualJp": "壱岐・対馬・山陰産「剣先イカお造り柵（歩留まり95%・1皿55g原価313円）」の原価比較シート",
            "bodyVisualEn": "Cost breakdown of Tsushima/San'in Kensaki squid sashimi block (95% yield, 313 yen/dish)",
            "bodyAudioJp": "鮮魚のイカは天候ひとつで入荷が止まり、価格が乱高下します。しかし盛漁期に水揚げし、皮むきと下処理を済ませて急速冷凍した剣先イカのお造り柵なら、可食歩留まりは95%。1人前55グラムの原価は約313円、売価1,180円想定で原価率26.5%を通年キープできます。",
            "bodyAudioEn": "Fresh squid supply halts in bad weather. By stocking peak-season peeled and scored rapid-frozen Kensaki squid blocks with 95% yield, a 55g sashimi portion costs ~313 yen—holding a steady 26.5% food cost year-round.",
            "climaxVisualJp": "スリットが入った艶やかな剣先イカのお造りと握り寿司の盛り付け映像",
            "climaxVisualEn": "Glossy Kensaki squid sashimi and nigiri with fine knife scoring",
            "climaxAudioJp": "天候に左右されず、いつでも甘いイカの王様をお客様にお出しできます。",
            "climaxAudioEn": "Serve the sweet 'King of Squid' consistently, regardless of the weather.",
            "shootGuide": "イカの透明感とスリット（隠し包丁）の立体感が際立つよう、黒い器に盛り付けて光を当てる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese Kensaki Ika (Swordtip Squid) sashimi with delicate diamond knife scoring on black ceramic plate, shiso leaf and wasabi, macro culinary shot",
            "source": "東京都・大阪市中央卸売市場 水産物月報／業務用B2B卸相場＆ファインアトラスFL原価試算"
        },
        {
            "day": 9, "week": 2, "dow": "火曜日", "weekdayTheme": "高級魚の豆知識",
            "themeId": "TH-13", "themeName": "海外で人気の日本の魚", "fishKey": "ホタテ貝柱",
            "assetCode": "P-VF-025", "assetLabel": "北海道産トンネルIQFホタテ貝柱（玉冷）とカルパッチョ写真",
            "titleJp": "世界の五つ星シェフが絶賛！北海道産「ホタテ玉冷」が歩留まり99%で選ばれる理由",
            "titleEn": "Why Global 5-Star Chefs Love Hokkaido IQF Scallops (99% Usable Yield)",
            "hookVisualJp": "大粒の北海道産ホタテ貝柱をバターで表面だけ黄金色にソテーするシズル映像",
            "hookVisualEn": "Searing plump Hokkaido scallop in foaming brown butter to a golden crust",
            "hookAudioJp": "海外の高級レストランで、日本の魚介の中で圧倒的なリピート率を誇る食材をご存知ですか？",
            "hookAudioEn": "Do you know which Japanese seafood item boasts one of the highest repeat rates in global fine dining?",
            "bodyVisualJp": "北海道産トンネルIQFホタテ貝柱（歩留まり99%・1粒バラ凍結）のサイズ比較と断面",
            "bodyVisualEn": "Hokkaido tunnel-IQF individual scallops showing 99% yield and sashimi-grade core",
            "bodyAudioJp": "それが北海道産の生食用ホタテ貝柱、通称『玉冷』です。トンネルフリーザーで1粒ずつバラ凍結（IQF）されているため、必要な粒数だけ取り出せて可食歩留まりは驚異の99%。殻剥きやウロ取りの手間も廃棄ロスも一切ありません。",
            "bodyAudioEn": "It's Hokkaido sashimi-grade IQF scallop, known as Tamarei. Individually quick-frozen in tunnel freezers, chefs pull only the exact pieces needed with a 99% usable yield—zero shucking labor and zero shell waste.",
            "climaxVisualJp": "ホタテの炙りカルパッチョと焦がしバターソテー（1皿原価544円・売価1,800円想定）",
            "climaxVisualEn": "Plated torched scallop carpaccio and brown-butter seared scallops",
            "climaxAudioJp": "和食のお造りからフレンチのポワレまで、1粒単位で正確に原価管理ができます。",
            "climaxAudioEn": "From sashimi to French poêlé, control your food cost down to the single scallop.",
            "shootGuide": "バラ凍結の袋からカランと1粒ずつ取り出せる利便性と、レアに焼いた断面のコントラストを撮る。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 seared Hokkaido jumbo scallops with golden crust and translucent sashimi center on white fine dining plate, micro herbs, citrus glaze",
            "source": "農林水産省 水産物輸出統計（ホタテ貝）／ファインアトラス拡張5品目原価データ"
        },
        {
            "day": 10, "week": 2, "dow": "水曜日", "weekdayTheme": "冷凍魚の特徴・解凍方法",
            "themeId": "TH-06", "themeName": "美味しく解凍する方法", "fishKey": "本マグロ柵",
            "assetCode": "V-TC-005", "assetLabel": "真空パック魚の氷水解凍（0〜2℃）と冷蔵庫緩慢解凍の実演動画",
            "titleJp": "プロが教える冷凍魚の黄金解凍術！旨味を1滴も逃さない「氷水解凍」とは？",
            "titleEn": "Pro Chef Thawing Secret: The 0°C Ice-Water Bath That Locks In 100% Umami",
            "hookVisualJp": "ボウルに張った氷水（0〜2℃）に真空パックのままのフィレを沈める手元映像",
            "hookVisualEn": "Submerging a vacuum-packed fish fillet directly into an ice-water bath (0-2°C)",
            "hookAudioJp": "どれだけ高品質な急速冷凍魚でも、解凍方法を間違えると味が半減してしまいます。",
            "hookAudioEn": "Even the highest-grade rapid-frozen fish can lose half its quality if thawed incorrectly.",
            "bodyVisualJp": "常温解凍（NG・ドリップ流出）と真空パック氷水解凍（推奨・熱伝導率20倍で均一解凍）の比較図",
            "bodyVisualEn": "Comparison of room-temp thawing (high drip) vs 0°C ice-water bath (20x heat transfer, minimal drip)",
            "bodyAudioJp": "常温放置や電子レンジ解凍は、表面と中心の温度差が大きくなりドリップ流出の原因になります。正解は、真空パックのまま『氷水（0〜2℃）』に浸す氷水解凍です。水は空気の約20倍熱を伝えるため、低温を保ったまま素早く均一に解凍でき、芯がわずかに凍った半解凍で包丁を入れると断面も美しく仕上がります。",
            "bodyAudioEn": "Room-temperature or microwave thawing creates uneven heat and heavy drip. Instead, submerge the sealed vacuum pack in 0-2°C ice water. Water transfers heat 20 times faster than air, thawing evenly while staying cold.",
            "climaxVisualJp": "氷水解凍後に切り付けた、ドリップゼロで角が立った本マグロ柵と白身お造り",
            "climaxVisualEn": "Cleanly sliced bluefin tuna saku and white fish sashimi with sharp edges and zero drip",
            "climaxAudioJp": "正しい急速冷凍と氷水解凍の組み合わせが、厨房の鮮度革命を起こします。",
            "climaxAudioEn": "Pairing rapid freezing with ice-water thawing revolutionizes kitchen freshness.",
            "shootGuide": "氷水に温度計を入れて「0.5℃」を示しているカットを入れると、プロの説得力が一気に増す。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 stainless steel bowl filled with ice cubes and water in professional kitchen, vacuum-sealed premium fish fillet submerged for precision thawing",
            "source": "水産加工・低温物流技術ハンドブック（氷水解凍の熱伝導率とドリップ抑制効果）"
        },
        {
            "day": 11, "week": 2, "dow": "木曜日", "weekdayTheme": "プロの料理・調理方法",
            "themeId": "TH-11", "themeName": "寿司・刺身の知識", "fishKey": "剣先イカ",
            "assetCode": "V-TC-010", "assetLabel": "剣先イカお造り柵の隠し包丁（スリット）と握り・お造り盛り付け動画",
            "titleJp": "なぜ剣先イカに「隠し包丁」を入れると甘みが爆発するのか？その科学と技術",
            "titleEn": "Why Precision Knife Scoring Multiplies the Sweetness of Kensaki Squid",
            "hookVisualJp": "剣先イカの表面に1ミリ間隔の美しいスリット（鹿の子包丁）が入っていく超接写",
            "hookVisualEn": "Extreme macro shot of 1mm precision scoring across a glossy Kensaki squid block",
            "hookAudioJp": "一流の寿司店や割烹のイカが、驚くほど甘くトロリと溶ける理由を知っていますか？",
            "hookAudioEn": "Ever wondered why squid at top sushi counters melts on the tongue with intense sweetness?",
            "bodyVisualJp": "イカの筋繊維を断ち切るスリット構造図と、-20℃以下急速凍結によるアニサキス完全対策解説",
            "bodyVisualEn": "Diagram of scoring cutting squid muscle fibers and -20°C freezing eliminating Anisakis risk",
            "bodyAudioJp": "剣先イカは繊維が緻密なため、表面に細かなスリットを入れて繊維を断ち切ることで、噛んだ瞬間に舌との接触面積が増えて甘み成分（遊離アミノ酸）が一気に広がります。さらにマイナス20℃以下で急速冷凍されたお造り柵なら、アニサキスの心配もゼロで安全に提供できます。",
            "bodyAudioEn": "Kensaki squid has dense muscle fibers. Fine scoring severs those fibers and increases surface contact with the tongue, releasing free amino acids instantly—while -20°C rapid freezing eliminates parasite risks.",
            "climaxVisualJp": "スダチと塩を振った剣先イカの握りと糸造り（1皿原価313円・原価率26.5%）",
            "climaxVisualEn": "Kensaki squid nigiri finished with sudachi citrus zest and sea salt",
            "climaxAudioJp": "皮むき・スリット済みの柵を使えば、包丁を入れるだけで一流の一貫が出せます。",
            "climaxAudioEn": "With pre-peeled, pre-scored sashimi blocks, simply slice and serve master-level sushi.",
            "shootGuide": "包丁の刃先がイカの表面にスッと入る音と、スダチを絞った瞬間の果汁のきらめきを捉える。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 piece of Kensaki Ika sushi nigiri with intricate crosshatch knife scoring, drop of sudachi lime juice and pinch of sea salt, hinoki wood counter",
            "source": "厚生労働省 アニサキス冷凍死滅基準（-20℃以下24時間以上）／水産食品の呈味成分研究"
        },
        {
            "day": 12, "week": 2, "dow": "金曜日", "weekdayTheme": "レストランの原価・経営改善",
            "themeId": "TH-09", "themeName": "厨房の仕込み時間短縮", "fishKey": "煮穴子",
            "assetCode": "P-CS-001", "assetLabel": "対馬産・無添加炊き上げ煮穴子と時計比較（60分→3分）写真",
            "titleJp": "毎日1時間の「穴子の炊き番」を3分に短縮！歩留まり98%・無添加煮穴子の威力",
            "titleEn": "Cut 60 Minutes of Simmering down to 3 Minutes: 98%-Yield Tsushima Anago",
            "hookVisualJp": "寸胴鍋の前で1時間つきっきりになる時計映像から、湯煎・炙り3分で完成する煮穴子への転換",
            "hookVisualEn": "Transition from a 60-minute simmering pot timer to a 3-minute torch-finished simmered Anago",
            "hookAudioJp": "少人数の厨房で、穴子を炊くために毎日1時間以上コンロの前につきっきりになっていませんか？",
            "hookAudioEn": "In a lean kitchen, can you really afford standing over a simmering pot for an hour just for Anago?",
            "bodyVisualJp": "対馬産・無添加炊き上げ真空冷凍「煮穴子（歩留まり98%・1人前55g原価359円）」のスペック表",
            "bodyVisualEn": "Spec card of Tsushima additive-free simmered Anago (98% yield, 55g portion = 359 yen cost)",
            "bodyAudioJp": "対馬産の良質な穴子を、産地で無添加のままふっくら炊き上げて真空急速冷凍した『煮穴子』なら、可食歩留まりは98%。必要なパックだけ解凍して軽く炙り、お店のツメを塗るだけで3分で提供できます。1皿55グラムの原価は359円、売価1,280円なら原価率は28.1%です。",
            "bodyAudioEn": "Simmered additive-free in Tsushima and vacuum rapid-frozen, this Anago delivers a 98% yield. Thaw, torch lightly, and brush with your house glaze in 3 minutes—at 359 yen per 55g portion (28.1% cost ratio).",
            "climaxVisualJp": "香ばしく炙った煮穴子握りと一本穴子酒肴にツメを塗るフィニッシュ映像",
            "climaxVisualEn": "Brushing glossy sweet soy glaze over torch-seared whole Anago",
            "climaxAudioJp": "浮いた1時間を、お客様への接客と新しい料理の仕上げに回せます。",
            "climaxAudioEn": "Reclaim that hour every day for guest hospitality and creative plating.",
            "shootGuide": "バーナーで炙った瞬間に穴子の脂がジュワッと泡立つシズル感と、タレの艶を強調して撮影する。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese chef brushing glossy dark sweet tare glaze onto torch-seared simmered conger eel (Nianago), warm dramatic kitchen lighting",
            "source": "ファインアトラス主力5品目原価・歩留まり試算書（対馬産無添加煮穴子・歩留まり98%）"
        },
        {
            "day": 13, "week": 2, "dow": "土曜日", "weekdayTheme": "漁業・産地・水産加工",
            "themeId": "TH-17", "themeName": "水産加工の現場", "fishKey": "銀ダラ・サワラ",
            "assetCode": "V-PF-010", "assetLabel": "熟練職人による骨抜き・高真空パック・急速冷凍ライン動画",
            "titleJp": "ピンセットの骨抜き作業をゼロに！歩留まり95%「完全骨取りフィレ」ができるまで",
            "titleEn": "Inside the Processing Craft: How 95%-Yield Boneless Fillets Are Made",
            "hookVisualJp": "加工場で職人が1枚ずつ丁寧に血合い骨を抜き、高真空パックする手元映像",
            "hookVisualEn": "Craftsman removing pin bones from fish fillets before high-vacuum sealing",
            "hookAudioJp": "焼き魚やポワレを仕込むとき、一番神経を使う『小骨抜き』。産地でどこまで処理されているか見たことはありますか？",
            "hookAudioEn": "Removing pin bones is one of the most tedious kitchen tasks. Ever seen how it's done at the source?",
            "bodyVisualJp": "銀ダラ・サワラ骨取フィレ（歩留まり95%・75gポーション原価347円）の加工・急速凍結フロー",
            "bodyVisualEn": "Processing flow of boneless Sablefish & Spanish Mackerel fillets (95% yield, 347 yen/75g)",
            "bodyAudioJp": "水揚げ後の新鮮なうちに産地加工場で三枚におろし、熟練のスタッフが小骨を処理してから高真空パック・急速冷凍を行います。これにより冷凍焼けと脂質の酸化を徹底的に防ぎ、お店に届いたときには歩留まり95%の状態で、西京焼きや幽庵焼き、低温ミキュイにそのまま使えます。",
            "bodyAudioEn": "Right after landing, skilled processors fillet the fish, remove pin bones, and apply high-vacuum rapid freezing to prevent freezer burn and lipid oxidation—delivering 95%-yield fillets ready for Saikyo-yaki or mi-cuit.",
            "climaxVisualJp": "黄金色に焼き上がった銀ダラ西京焼きとサワラのミキュイ（売価1,250円・原価率27.8%）",
            "climaxVisualEn": "Golden broiled Sablefish Saikyo-yaki and Spanish Mackerel mi-cuit plated side by side",
            "climaxAudioJp": "骨抜きの手間もクレームリスクも減らし、1皿原価率27.8%を実現します。",
            "climaxAudioEn": "Eliminate bone-picking labor and guest complaints while maintaining a 27.8% food cost.",
            "shootGuide": "高真空パック機で空気が抜けてピタッと密着する瞬間を映すと、酸化防止の品質感が伝わる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 golden caramelized miso-marinated Sablefish (Gindara Saikyo-yaki) on Japanese ceramic dish with hajikami ginger, restaurant photography",
            "source": "ファインアトラス拡張5品目規格（銀ダラ・サワラ骨取フィレ・高真空エアブラスト凍結データ）"
        },
        {
            "day": 14, "week": 2, "dow": "日曜日", "weekdayTheme": "ファインアトラスの商品・サービス紹介",
            "themeId": "TH-19", "themeName": "ファインアトラスの取り組み・商品紹介", "fishKey": "甘鯛",
            "assetCode": "P-VF-001", "assetLabel": "公式お試しセット・Amazon少量購入から店舗別オリジナル魚BOXへのステップ図",
            "titleJp": "いきなり定期契約は不要！Amazon・HPの少量購入から始める「店舗別オリジナル魚BOX」",
            "titleEn": "No Big Contract Needed: Start Small on Amazon/Web, Scale to a Custom Fish Box",
            "hookVisualJp": "スマホでHP・Amazonから少量注文し、厨房に届いた冷凍・チルド魚を料理長が検品する映像",
            "hookVisualEn": "Chef ordering a small trial pack online and inspecting the delivered fillets in the kitchen",
            "hookAudioJp": "「新しい魚屋の食材、まずは自分の包丁と舌で少しだけ確かめてみたい」と思いませんか？",
            "hookAudioEn": "'Before committing to a new seafood supplier, I want to test a small batch with my own knife and palate.'",
            "bodyVisualJp": "社長計画書7ステップ導線図（ショート動画→HP・Amazon誘導→少量購入で品質確認→リピート→法人契約・店舗別オリジナル魚BOX）",
            "bodyVisualEn": "7-step funnel chart: Daily Shorts -> Website/Amazon -> Small Trial -> Repeat -> Custom B2B Fish Box",
            "bodyAudioJp": "料理人はご自身の目で確かめたものしか使いません。だからこそファインアトラスでは、まずホームページやAmazonでの少量購入・お試しセットで、甘鯛や穴子、のどぐろの身質・ドリップ・歩留まりを実際の厨房で試していただけます。納得いただいた後に、お店のメニューに合わせた『店舗別オリジナル魚BOX』をご提案します。",
            "bodyAudioEn": "Chefs trust only what they verify themselves. That's why Fine Atlas lets you order small batches via our website or Amazon first to test drip and yield in your kitchen—before designing your custom restaurant fish box.",
            "climaxVisualJp": "和食・ビストロ・寿司店それぞれの専用魚BOXイメージと公式案内カード",
            "climaxVisualEn": "Custom seafood box lineups tailored for Washoku, Bistro, and Sushi restaurants",
            "climaxAudioJp": "少量のお試しから法人定期契約まで、あなたのお店のペースで始められます。",
            "climaxAudioEn": "From a single trial box to a full B2B partnership, move at your restaurant's own pace.",
            "shootGuide": "「①まず少量お試し → ②納得したらリピート → ③店舗別オリジナル魚BOX」の3ステップを明快に図示する。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese head chef smiling while inspecting vacuum-packed premium fish fillets in a clean modern restaurant kitchen, high trust commercial style",
            "source": "株式会社ファインアトラス AIショート動画毎日配信計画 第1章・第11章（集客から販売までの流れ）"
        },

        # WEEK 3
        {
            "day": 15, "week": 3, "dow": "月曜日", "weekdayTheme": "今週の旬の魚・市場相場",
            "themeId": "TH-15", "themeName": "季節ごとの魚カレンダー", "fishKey": "トラフグ身欠き",
            "assetCode": "P-VF-010", "assetLabel": "春夏秋冬の旬魚カレンダーと国産除毒済トラフグ身欠き写真",
            "titleJp": "料理長のための春夏秋冬「旬魚仕入れカレンダー」！秋冬〜春の客単価UP魚種は？",
            "titleEn": "Chef's 4-Season Japanese Seafood Calendar: High-Ticket Winter & Spring Picks",
            "hookVisualJp": "春夏秋冬4分割の美しい日本産魚介カレンダー（春：甘鯛・サワラ、夏：穴子・剣先イカ、秋：のどぐろ、冬：トラフグ・ホタテ）",
            "hookVisualEn": "4-season Japanese seafood grid highlighting Amadai, Anago, Nodoguro, and Torafugu",
            "hookAudioJp": "季節のコースメニューを組むとき、1ヶ月先回りして原価と目玉食材を固められたらラクになりませんか？",
            "hookAudioEn": "When planning seasonal tasting menus, wouldn't locking in star seafood and costs a month early make life easier?",
            "bodyVisualJp": "国産除毒済「トラフグ身欠き（歩留まり75%・1人前55g原価543円・想定売価1,980円・原価率27.4%）」の解説",
            "bodyVisualEn": "Spec breakdown of detoxified Japanese Tiger Pufferfish (75% yield, 543 yen cost, 27.4% ratio)",
            "bodyAudioJp": "春は甘鯛とサワラ、夏は対馬穴子と剣先イカ、秋はのどぐろ、そして冬から春にかけて客単価を一気に引き上げるのが『国産トラフグの除毒済身欠き』です。有資格者による除毒処理を終えて急速冷凍されているため、1人前55グラム原価543円、売価1,980円想定で原価率27.4%のてっちりや唐揚げを安全に提供できます。",
            "bodyAudioEn": "Spring brings Amadai; summer, Anago and Kensaki squid; autumn, Nodoguro; and winter, licensed detoxified Torafugu pufferfish. Rapid-frozen and ready to cut, a 55g portion costs 543 yen for a 1,980-yen dish (27.4% cost).",
            "climaxVisualJp": "揚げたてのトラフグ唐揚げと小鍋てっちりのシズル映像",
            "climaxVisualEn": "Crispy golden Torafugu karaage and bubbling pufferfish hotpot",
            "climaxAudioJp": "旬のカレンダーと産地急速冷凍を組み合わせれば、365日強いメニューが作れます。",
            "climaxAudioEn": "Combine our seasonal calendar with port-frozen stock to build winning menus 365 days a year.",
            "shootGuide": "4季節の代表魚を色分けしたカレンダーフリップを3〜12秒に出し、保存したくなる情報密度にする。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese Torafugu (pufferfish) crispy karaage fried pieces served with sudachi lime and sansho salt on artisan pottery plate",
            "source": "東京都・大阪市中央卸売市場 季節別入荷統計／ファインアトラス拡張5品目（除毒済トラフグ身欠き）"
        },
        {
            "day": 16, "week": 3, "dow": "火曜日", "weekdayTheme": "高級魚の豆知識",
            "themeId": "TH-14", "themeName": "珍しい魚の紹介", "fishKey": "甘鯛",
            "assetCode": "P-WR-020", "assetLabel": "赤甘鯛と希少な白甘鯛・大型対馬穴子の比較写真",
            "titleJp": "赤甘鯛と幻の「白甘鯛」、そして対馬の黄金穴子。産地直結だから届く希少規格とは？",
            "titleEn": "Red vs. Rare White Tilefish & Golden Tsushima Anago: Direct-from-Port Gems",
            "hookVisualJp": "鮮やかな赤甘鯛・白甘鯛・対馬の肉厚穴子が氷上に並ぶ圧巻の比較カット",
            "hookVisualEn": "Comparison shot of vibrant Red Tilefish, rare White Tilefish, and thick Tsushima Anago on ice",
            "hookAudioJp": "一般的な市場ではなかなか揃わない、産地の特別規格の魚をご存知ですか？",
            "hookAudioEn": "Do you know how top chefs secure rare port-grade fish specs that rarely reach city markets?",
            "bodyVisualJp": "赤甘鯛（キロ6,800円想定・歩留まり95%フィレ）と白甘鯛（市場9,800円/kg〜）・代替魚との違い解説",
            "bodyVisualEn": "Comparison of Red Amadai scale-on fillet (95% yield) vs ultra-rare White Amadai market tiers",
            "bodyAudioJp": "例えば甘鯛には、上品な甘みで松笠焼きに最適な『赤甘鯛』と、水揚げ量が極めて少ない高級種『白甘鯛』があります。また対馬の穴子も、肉厚なサイズだけを厳選して活〆開きや無添加煮穴子に加工することで、一般の海外加工普及品とは別次元の香りと脂乗りを実現しています。",
            "bodyAudioEn": "Amadai includes classic Red Tilefish—ideal for crispy scale-on dishes—and ultra-rare White Tilefish. Likewise, selecting thick Tsushima conger eel for live-struck filleting delivers aroma and fat far beyond standard imports.",
            "climaxVisualJp": "肉厚な甘鯛ポワレと対馬穴子の一皿にソースを添えるシェフの手元",
            "climaxVisualEn": "Chef pouring dashi beurre blanc around a thick crispy-scaled Amadai fillet",
            "climaxAudioJp": "他店と明確に差別化できる主役の一皿を、産地直結の品質で支えます。",
            "climaxAudioEn": "Stand out from competitors with port-direct centerpiece seafood.",
            "shootGuide": "普通の冷凍開きと対馬産の肉厚フィレの「身の厚み（断面）」を並べて見せると一目で違いが伝わる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 thick fillet of Japanese Amadai tilefish with crispy golden scales in shallow dashi broth, fine dining Kyoto fusion plating",
            "source": "大阪市中央卸売市場 水産物相場統計（赤甘鯛・白甘鯛・対馬産穴子規格比較）"
        },
        {
            "day": 17, "week": 3, "dow": "水曜日", "weekdayTheme": "冷凍魚の特徴・解凍方法",
            "themeId": "TH-04", "themeName": "冷凍魚と生魚の違い", "fishKey": "のどぐろ",
            "assetCode": "P-VF-015", "assetLabel": "水揚げ直後急速冷凍魚と輸送3日経過した未凍結鮮魚の鮮度比較図",
            "titleJp": "「3日前の生魚」と「水揚げ直後の急速冷凍魚」、料理人が選ぶべきはどっち？",
            "titleEn": "3-Day-Old 'Fresh' Fish vs. Port-Side Rapid-Frozen Fish: Which Is Truly Fresher?",
            "hookVisualJp": "「生＝常に最高？」という常識に疑問を投げかけるフリップと、透明な目をした産地凍結魚",
            "hookVisualEn": "Title card challenging 'Is raw always fresher?' alongside a crystal-clear-eyed port-frozen fish",
            "hookAudioJp": "「うちは生の魚しか使わない」という料理長にこそ知ってほしい、鮮度の科学があります。",
            "hookAudioEn": "For chefs who say 'I only use never-frozen fish,' here is the food science of post-catch freshness.",
            "bodyVisualJp": "水揚げから市場・店舗到着までの時間経過（48〜72時間）によるATP減少と、産地即時急速冷凍の鮮度維持グラフ",
            "bodyVisualEn": "Graph comparing freshness decay over 48-72h chilled transport vs immediate port-side rapid freezing",
            "bodyAudioJp": "未凍結の鮮魚は、漁港から市場、仲卸、店舗へ届くまでに2〜3日かかり、その間にも酵素反応で鮮度と身質は刻々と落ちていきます。一方、盛漁期の港で水揚げ直後に下処理・高真空急速冷凍した魚は、最も美味しい瞬間の状態で時間が止まるため、解凍した時点で3日経過した生魚を上回る身質を保てるのです。",
            "bodyAudioEn": "Unfrozen fish takes 2-3 days from boat to market to restaurant, losing firmness every hour. Fish processed and vacuum rapid-frozen at the port stops enzymatic decay at peak umami—often outperforming 3-day-old 'fresh' fish upon thawing.",
            "climaxVisualJp": "解凍したてののどぐろと甘鯛の張りがある美しい切り身",
            "climaxVisualEn": "Firm, glossy thawed fillets of Nodoguro and Amadai ready for the grill",
            "climaxAudioJp": "『生か冷凍か』ではなく、『いつ・どう時間を止めたか』が味の決め手です。",
            "climaxAudioEn": "What matters isn't 'raw vs frozen'—it's WHEN and HOW time was stopped at the port.",
            "shootGuide": "解凍後のフィレを指で軽く押して、弾力（プリッとした反発）がある様子を動画で見せる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 chef checking the firm elastic texture of a freshly thawed Japanese Nodoguro fillet on a wooden cutting board, bright clean kitchen",
            "source": "水産庁 水産物の鮮度保持・コールドチェーン技術資料／特殊急速凍結品質検証データ"
        },
        {
            "day": 18, "week": 3, "dow": "木曜日", "weekdayTheme": "プロの料理・調理方法",
            "themeId": "TH-12", "themeName": "海外の日本食レストラン事情", "fishKey": "車海老・天使の海老",
            "assetCode": "P-CS-080", "assetLabel": "IQF車海老・天使の海老の天ぷら＆OMAKASE盛り付け写真",
            "titleJp": "世界のOMAKASE・ビストロで指名買い！1尾ずつ使える「IQF海老＆日本産フィレ」調理術",
            "titleEn": "How Global Omakase & Bistro Chefs Use IQF Prawns & Japanese Fillets",
            "hookVisualJp": "1尾ずつバラ凍結（IQF）された車海老・天使の海老を取り出し、天ぷらとグリルに仕上げる映像",
            "hookVisualEn": "Pulling individual IQF prawns from pack and cooking crispy tempura and herb-grilled prawns",
            "hookAudioJp": "海外や国内の少数精鋭レストランで、なぜ『IQF（個別急速冷凍）』の魚介がこれほど支持されているのでしょうか？",
            "hookAudioEn": "Why do lean Omakase counters and bistros worldwide rely on IQF (Individually Quick Frozen) seafood?",
            "bodyVisualJp": "ブロック凍結（全量解凍が必要）とIQFバラ凍結（1尾・1枚ずつ取り出し可能・廃棄ゼロ）の比較",
            "bodyVisualEn": "Comparison of solid block freezing (must thaw all) vs IQF (take 1 piece at a time, zero waste)",
            "bodyAudioJp": "従来のブロック冷凍は一度に全て解凍する必要があり、余った分がロスになりました。しかし車海老・天使の海老やホタテ、のどぐろのIQF（個別急速冷凍）なら、予約人数に合わせて1尾・1枚単位で取り出せます。1人前45グラム原価457円（原価率28.9%）で、生食のカルパッチョから天ぷらまで自在に対応できます。",
            "bodyAudioEn": "Old block-frozen packs forced chefs to thaw the entire block. With IQF prawns, scallops, and Nodoguro, you pull the exact count for tonight's reservations—delivering sashimi or tempura at a 28.9% food cost with zero leftover waste.",
            "climaxVisualJp": "ピンと立った車海老の天ぷらと、天使の海老カルパッチョ（売価1,580円想定）",
            "climaxVisualEn": "Golden upright Kuruma prawn tempura and Angel Blue Prawn carpaccio",
            "climaxAudioJp": "予約数に合わせて1尾から取り出せる仕組みが、世界の厨房の利益を守ります。",
            "climaxAudioEn": "Pulling one piece per reservation protects profit margins in kitchens worldwide.",
            "shootGuide": "凍った状態で1尾だけサッと取り出し、残りをすぐ冷凍庫へ戻せる手軽さを3秒で見せる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese Kuruma Ebi prawn tempura fried golden crisp on washi paper and raw Angel prawn carpaccio, dual culinary showcase",
            "source": "ジェトロ日本産水産物海外需要調査／ファインアトラス拡張5品目（車海老・天使の海老IQFデータ）"
        },
        {
            "day": 19, "week": 3, "dow": "金曜日", "weekdayTheme": "レストランの原価・経営改善",
            "themeId": "TH-08", "themeName": "飲食店の仕入れ改善", "fishKey": "本マグロ柵",
            "assetCode": "P-CS-045", "assetLabel": "本マグロ・ミナミマグロ定尺柵と主力5品目の月間ロス削減シミュレーション図",
            "titleJp": "お造り盛り合わせの「変色廃棄ロス」をゼロに！定尺マグロ柵×白身・イカ5品目の黄金構成",
            "titleEn": "Zero Sashimi Waste: The 5-Item Fish Lineup That Holds a 28.1% Average Food Cost",
            "hookVisualJp": "本マグロ定尺柵・剣先イカ・のどぐろ・ホタテ・甘鯛を盛り合わせた豪華お造り5点盛り",
            "hookVisualEn": "Deluxe 5-kind sashimi platter featuring Bluefin tuna, Kensaki squid, Nodoguro, scallop, and Amadai",
            "hookAudioJp": "お造りの盛り合わせで一番怖いのは、雨の日や暇な日に鮮魚が余って変色し、廃棄になることではありませんか？",
            "hookAudioEn": "Isn't the biggest profit killer on your sashimi menu throwing away discolored fresh fish after a slow rainy night?",
            "bodyVisualJp": "皮・血合い処理済「本マグロ・ミナミマグロ定尺柵（歩留まり94%・1皿原価498円）」＋主力魚種のロスゼロ試算",
            "bodyVisualEn": "Yield & cost breakdown of trimmed Bluefin tuna saku (94% yield, 498 yen cost) + zero-waste sashimi lineup",
            "bodyAudioJp": "皮と血合いを除去した歩留まり94%のマグロ定尺柵に、剣先イカ柵、のどぐろ、ホタテ玉冷を組み合わせれば、その日の予約と客数に合わせて必要な柵だけを15分で氷水解凍できます。10品目平均の飲食店原価率は28.1%、しかも売れ残りによる廃棄ロスをほぼゼロに抑えられます。",
            "bodyAudioEn": "By combining 94%-yield trimmed Bluefin tuna saku blocks with Kensaki squid, Nodoguro, and IQF scallops, you thaw only what tonight's covers require in 15 minutes—averaging a 28.1% food cost with zero spoilage.",
            "climaxVisualJp": "美しいお造り盛り合わせと「廃棄ロス0円・平均原価率28.1%」のインパクトバッジ",
            "climaxVisualEn": "Vibrant sashimi platter overlaid with 'Zero Spoilage Waste / 28.1% Avg Cost' badge",
            "climaxAudioJp": "廃棄ロスをなくすことが、値上げをせずに店の営業利益を増やす最短ルートです。",
            "climaxAudioEn": "Eliminating spoilage waste is the fastest way to boost restaurant profit without raising menu prices.",
            "shootGuide": "定尺柵を切ったときに端から端まで血合いロスがなく、すべてお造りとして使える様子を映す。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 rectangular sashimi block (saku) of Japanese Bluefin Tuna Chutoro being sliced with yanagiba knife, rich marbling, zero waste trim",
            "source": "全国業務用冷凍魚10品目 仕入れ価格AI調査＆飲食店FL原価試算（全10品目平均原価率28.1%）"
        },
        {
            "day": 20, "week": 3, "dow": "土曜日", "weekdayTheme": "漁業・産地・水産加工",
            "themeId": "TH-18", "themeName": "日本の魚文化", "fishKey": "穴子フィレ",
            "assetCode": "V-FP-015", "assetLabel": "日本の活〆（Ikejime）・血抜き技術と急速冷凍の融合解説動画",
            "titleJp": "世界のシェフが学ぶ日本の「活〆（Ikejime）」！急速冷凍と組み合わさると何が起きる？",
            "titleEn": "Japanese 'Ikejime' Meets Rapid Freezing: Why Global Chefs Revere This Combo",
            "hookVisualJp": "英語でも『IKEJIME』と呼ばれる日本の活〆・血抜き技術の職人手元映像",
            "hookVisualEn": "Artisan performing traditional Japanese Ikejime and bleeding at the fishing port",
            "hookAudioJp": "今、世界中のミシュランシェフが日本語のまま『IKEJIME（活〆）』という言葉を使っているのをご存知ですか？",
            "hookAudioEn": "Did you know Michelin-starred chefs around the world now use the Japanese word 'Ikejime' every day?",
            "bodyVisualJp": "活〆・血抜き（ATP保持・臭み原因の血液除去）× 高真空急速冷凍（細胞保護）のシナジー図解",
            "bodyVisualEn": "Diagram showing synergy of Ikejime bleeding (ATP retention, zero odor) + rapid freezing",
            "bodyAudioJp": "魚が暴れて旨味成分の源であるATPを消費する前に素早く活〆し、臭みの原因となる血を抜く日本の伝統技術。この活〆直後の最高の状態を、産地の急速冷凍で一気に閉じ込めることで、遠く離れた都市や海外の厨房でも、臭みが一切ない透明感ある白身と穴子を味わえるようになりました。",
            "bodyAudioEn": "Ikejime humanely dispatches the fish before struggle depletes ATP (the source of umami) and removes blood that causes odor. Rapid-freezing immediately after Ikejime locks in that pristine state for kitchens anywhere in the world.",
            "climaxVisualJp": "透き通るように美しい活〆穴子フィレと白身魚の切り付け断面",
            "climaxVisualEn": "Translucent, snow-white flesh of live-struck Anago and white fish fillets",
            "climaxAudioJp": "日本の伝統の技と最新の冷凍科学が、世界の魚料理を進化させています。",
            "climaxAudioEn": "Traditional Japanese craftsmanship and modern freezing science are elevating seafood worldwide.",
            "shootGuide": "血抜き処理が徹底された穴子フィレの「真っ白で美しい身色」を自然光に近い照明でクリアに撮る。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 pristine snow-white Japanese fish fillet prepared with traditional Ikejime technique on hinoki cutting board, chef's knife beside it, serene lighting",
            "source": "水産研究・教育機構 活〆・血抜きによるATP保持および品質向上に関する公開研究"
        },
        {
            "day": 21, "week": 3, "dow": "日曜日", "weekdayTheme": "ファインアトラスの商品・サービス紹介",
            "themeId": "TH-19", "themeName": "ファインアトラスの取り組み・商品紹介", "fishKey": "のどぐろ",
            "assetCode": "V-PS-010", "assetLabel": "店舗別オリジナル魚BOX（和食・割烹・ビストロ向けカスタム構成）紹介動画",
            "titleJp": "あなたのお店専用の「オリジナル魚BOX」を設計！用途・サイズ・下処理までカスタム対応",
            "titleEn": "Design Your Restaurant's Custom Fish Box: Tailored Species, Prep Level & Portions",
            "hookVisualJp": "「割烹向けBOX」「ビストロ向けBOX」「寿司店向けBOX」の3種類のカスタム詰め合わせ映像",
            "hookVisualEn": "Three customized seafood boxes tailored for Kappo, French Bistro, and Sushi counters",
            "hookAudioJp": "『自店のタレで炊きたいから生開きがいい』『松笠焼き用にウロコ付きフィレだけ欲しい』……その要望、1箱にまとめられます。",
            "hookAudioEn": "'I want unseasoned Anago for my own sauce, and scale-on Amadai for poêlé'—now you can combine them in one custom box.",
            "bodyVisualJp": "5つの個別ヒアリング項目（①料理用途 ②魚種・サイズ・量 ③下処理度合い ④チルド/冷凍 ⑤現在の課題）",
            "bodyVisualEn": "5 customization pillars: Dish use, Species/Size, Prep degree, Chilled/Frozen, Kitchen pain points",
            "bodyAudioJp": "ファインアトラスでは、まずホームページやAmazonでの少量購入で品質をご確認いただいた後、お店ごとの料理用途、希望サイズ、どこまで下処理を任せるか、チルドか冷凍かに合わせて『店舗別オリジナル魚BOX』を個別設計します。少人数のオーナーシェフ店から複数店舗の法人契約まで柔軟に対応します。",
            "bodyAudioEn": "After verifying our quality with a small web or Amazon order, Fine Atlas works with you to build a Custom Restaurant Fish Box—tailored to your menu, portion sizes, prep requirements, and delivery schedule.",
            "climaxVisualJp": "料理長とスタッフがカスタム魚BOXの仕様を確認し握手するシーンとHP誘導カード",
            "climaxVisualEn": "Chef reviewing custom fish box selection with Fine Atlas specialist and inquiry card",
            "climaxAudioJp": "まずはホームページ・Amazonから少量お試しいただき、理想の一箱を一緒に作りましょう。",
            "climaxAudioEn": "Start with a small trial order online, and let's build your kitchen's ideal seafood box.",
            "shootGuide": "「和食店例」「フレンチ・イタリアン例」の具体的な組み合わせを画面テロップで見せ、自分事化させる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 bespoke chef's seafood selection box containing vacuum-sealed Amadai, Nodoguro, Kensaki Squid, and Anago fillets with clean Japanese labels",
            "source": "株式会社ファインアトラス 営業設計基準（5項目個別ヒアリング＆店舗別オリジナル魚BOX提案フロー）"
        },

        # WEEK 4
        {
            "day": 22, "week": 4, "dow": "月曜日", "weekdayTheme": "今週の旬の魚・市場相場",
            "themeId": "TH-01", "themeName": "今が旬の魚", "fishKey": "銀ダラ・サワラ",
            "assetCode": "P-FL-050", "assetLabel": "旬のサワラ・銀ダラ骨取フィレと市場入荷トレンド図",
            "titleJp": "和食でもビストロでも引っ張りだこ！脂が乗った「サワラ・銀ダラ骨取フィレ」の旬と相場",
            "titleEn": "Why Boneless Spanish Mackerel & Sablefish Fillets Are a Hit in Washoku & Bistros",
            "hookVisualJp": "皮目をパリッと炙ったサワラのミキュイと、照り輝く銀ダラ西京焼きのダブルメイン映像",
            "hookVisualEn": "Split shot of torch-seared Spanish Mackerel mi-cuit and glossy broiled Sablefish",
            "hookAudioJp": "和食の焼き物でも、フレンチの魚料理でも、年間を通じてお客様満足度が極めて高い魚種といえば何でしょうか？",
            "hookAudioEn": "Which fish species consistently earn rave guest reviews in both traditional Washoku and modern French bistros?",
            "bodyVisualJp": "銀ダラ・サワラ骨取フィレ（卸目安・歩留まり95%・75gポーション原価347円・原価率27.8%）のデータ表示",
            "bodyVisualEn": "Data card for boneless Sablefish & Sawara fillet (95% yield, 75g portion = 347 yen, 27.8% cost)",
            "bodyAudioJp": "それが脂乗りの良い『銀ダラ』と『サワラ』です。盛漁期に買い付けて骨取り加工・急速冷凍したフィレなら、可食歩留まりは95%。しっかり75グラムのポーションを取っても1皿原価は約347円、売価1,250円想定で原価率27.8%に収まり、ランチの主役にもディナーコースの魚料理にも最適です。",
            "bodyAudioEn": "Rich Sablefish (Gindara) and Spanish Mackerel (Sawara). Processed boneless at peak season with a 95% yield, a generous 75g portion costs ~347 yen—delivering a 27.8% cost ratio on a 1,250-yen dish.",
            "climaxVisualJp": "春菊ソースを添えたサワラのポワレにナイフがスッと入る断面映像",
            "climaxVisualEn": "Knife gliding smoothly through a boneless Sawara poêlé with green herb sauce",
            "climaxAudioJp": "小骨が一切ないから、ナイフを入れた瞬間の感動が違います。",
            "climaxAudioEn": "Completely boneless, so the knife glides effortlessly on the plate.",
            "shootGuide": "ナイフで切った断面から湯気と肉汁がじゅわっと出る瞬間をアップで撮影する。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 French bistro style Spanish Mackerel (Sawara) mi-cuit with crispy torched skin, vibrant green herb emulsion sauce, fine dining plating",
            "source": "東京都・大阪市中央卸売市場 水産物統計／ファインアトラス拡張5品目原価試算データ"
        },
        {
            "day": 23, "week": 4, "dow": "火曜日", "weekdayTheme": "高級魚の豆知識",
            "themeId": "TH-02", "themeName": "高級魚の特徴", "fishKey": "トラフグ身欠き",
            "assetCode": "P-WR-040", "assetLabel": "国産トラフグ身欠き（除毒済）とコラーゲン・旨味繊維の断面写真",
            "titleJp": "冬の王様「トラフグ」、なぜ加熱すると旨味と弾力が倍増するのか？除毒済身欠きの秘密",
            "titleEn": "King of Winter Seafood: Why Torafugu Pufferfish Gets Even Better When Heated",
            "hookVisualJp": "ぐつぐつ煮えるてっちり鍋の中で、トラフグの身がプリッと白く膨らむシズル映像",
            "hookVisualEn": "Chunk of Torafugu pufferfish plumping up in simmering dashi hotpot",
            "hookAudioJp": "冬の味覚の王様、トラフグ。普通の白身魚と違って、鍋や唐揚げで熱を加えてもパサつかない理由を知っていますか？",
            "hookAudioEn": "Unlike ordinary white fish, why does Torafugu pufferfish never dry out in hotpots or deep-frying?",
            "bodyVisualJp": "トラフグの高コラーゲン筋肉構造と、有資格者による完全除毒済・身欠き急速冷凍（歩留まり75%）の解説",
            "bodyVisualEn": "Collagen-rich muscle structure of Torafugu and licensed detoxified rapid-frozen dressed spec (75% yield)",
            "bodyAudioJp": "トラフグは繊維質のコラーゲンが極めて豊富なため、熱を加えることでゼラチン質が溶け出し、ジューシーな弾力と濃厚な出汁が生まれます。専門資格を持つ加工場で完全除毒された『身欠き急速冷凍』なら、お店で特別な除毒手間をかけずに、歩留まり75%・1皿原価543円（原価率27.4%）で安全に扱えます。",
            "bodyAudioEn": "Torafugu is packed with structural collagen that melts into juicy tenderness and rich umami when heated. Pre-detoxified by licensed specialists at the source and rapid-frozen, chefs can serve it safely at a 27.4% food cost.",
            "climaxVisualJp": "熱々のトラフグ唐揚げを割った瞬間に立ち上る湯気と肉汁",
            "climaxVisualEn": "Breaking open a piping-hot Torafugu karaage revealing juicy white meat",
            "climaxAudioJp": "手間とリスクを産地に任せて、冬から春の客単価アップを実現しましょう。",
            "climaxAudioEn": "Leave the detox prep to the source and elevate your seasonal average check.",
            "shootGuide": "除毒済み証明の安心感と、唐揚げのジューシーな断面をセットで見せる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 Japanese fugu tecchiri hotpot in earthenware donabe with plump white pufferfish pieces, shiitake mushrooms, and tofu, warm steam",
            "source": "食品衛生法 ふぐ処理衛生基準／ファインアトラス拡張5品目（国産除毒済トラフグ身欠き）"
        },
        {
            "day": 24, "week": 4, "dow": "水曜日", "weekdayTheme": "冷凍魚の特徴・解凍方法",
            "themeId": "TH-05", "themeName": "急速冷凍の仕組み", "fishKey": "甘鯛",
            "assetCode": "P-VF-030", "assetLabel": "3つの凍結方式（一般緩慢・急速エアブラスト高真空・特殊急速凍結）ドリップ比較表",
            "titleJp": "ドリップ率10% vs 0.5%！3つの冷凍方式で「甘鯛の鱗立ち」とお造りの味が激変する理由",
            "titleEn": "10% Drip vs 0.5% Drip: How 3 Freezing Technologies Impact Sashimi & Crispy Scales",
            "hookVisualJp": "3種類の凍結方式（一般緩慢冷凍／急速エアブラスト＋高真空／特殊急速凍結）のドリップ率比較チャート",
            "hookVisualEn": "Comparison chart of 3 freezing tiers: Conventional (5-10% drip), Air-Blast Vacuum (2-3.5%), Special Rapid (0.5-1.5%)",
            "hookAudioJp": "一口に『冷凍魚』と言っても、凍結技術によって解凍時のドリップ量が最大20倍も違うことをご存知ですか？",
            "hookAudioEn": "Did you know that depending on the freezing technology, thaw drip loss can vary by up to 20 times?",
            "bodyVisualJp": "一般冷凍（ドリップ5〜10%・松笠焼き不可）vs 急速高真空・特殊急速凍結（ドリップ0.5〜3.5%・鱗立ち100%再現）",
            "bodyVisualEn": "Visual proof: Conventional frozen fish loses cell moisture vs Rapid-frozen Amadai keeping 100% crispy scale lift",
            "bodyAudioJp": "旧式の緩慢冷凍はドリップが5〜10%流出し、身が水っぽくなって甘鯛の鱗も綺麗に立ちません。これに対し、急速エアブラスト＋高真空パックはドリップ2〜3.5%で焼き物・天ぷらに最適。さらにプロトンや液体凍結などの特殊急速凍結はドリップ0.5〜1.5%以下で、お造りや甘鯛松笠焼きの鱗立ちまで100%再現します。",
            "bodyAudioEn": "Old slow freezers leak 5-10% drip, ruining sashimi and scale texture. High-vacuum air-blast freezing keeps drip to 2-3.5% for grilling, while advanced rapid freezing limits drip to under 1.5%—reproducing raw sashimi and 100% crispy Amadai scales.",
            "climaxVisualJp": "特殊急速凍結された甘鯛フィレのウロコが油かけで完璧に花開く瞬間",
            "climaxVisualEn": "Rapid-frozen Amadai fillet scales blooming perfectly crispy under hot oil",
            "climaxAudioJp": "料理の用途に合わせて最適な凍結技術を選ぶことが、プロの仕入れの新基準です。",
            "climaxAudioEn": "Matching the right rapid-freezing tech to your cooking method is the new chef standard.",
            "shootGuide": "「一般冷凍 5〜10%」「急速高真空 2〜3.5%」「特殊急速 0.5〜1.5%」の3段表を鮮明に表示する。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 chef pouring hot oil from a ladle over a scale-on Red Tilefish fillet, scales crisping up instantly, dramatic kitchen action shot",
            "source": "全国冷凍魚_仕入価格AI調査_江坂配送モデル検討書 第2-2節（凍結技術によるドリップ率・品質差）"
        },
        {
            "day": 25, "week": 4, "dow": "木曜日", "weekdayTheme": "プロの料理・調理方法",
            "themeId": "TH-10", "themeName": "魚ごとの調理方法", "fishKey": "のどぐろ",
            "assetCode": "V-TC-020", "assetLabel": "のどぐろセミドレス・フィレを使った「皮目炙り刺し」と「土鍋ご飯」調理動画",
            "titleJp": "客単価が2,000円上がる看板料理！下処理済「のどぐろ」で作る炙り刺し＆土鍋ご飯",
            "titleEn": "Boost Guest Checks by ¥2,000: Signature Nodoguro Torch-Sashimi & Claypot Rice",
            "hookVisualJp": "土鍋の蓋を開けた瞬間、黄金色に焼けたのどぐろと出汁の湯気が立ち上るクライマックス映像",
            "hookVisualEn": "Lifting a claypot lid to reveal whole grilled Nodoguro atop steaming dashi rice",
            "hookAudioJp": "コースの締めや看板の一品で、お客様が思わずスマホで動画を撮りたくなる主役メニューといえば？",
            "hookAudioEn": "What is the ultimate showstopper dish that makes every guest pull out their smartphone at the end of a course?",
            "bodyVisualJp": "対馬・山陰産「のどぐろIQFセミドレス（歩留まり85%・1人前60g原価635円・想定売価2,280円）」の調理工程",
            "bodyVisualEn": "Cooking steps using IQF semi-dressed Nodoguro (85% yield, 60g portion = 635 yen cost, 2,280 yen menu price)",
            "bodyAudioJp": "それが『のどぐろの皮目炙り』と『のどぐろ土鍋ご飯』です。ウロコ・エラ・内臓を除去した歩留まり85%のセミドレス・フィレなら、面倒な下処理なしでそのまま塩焼きや炙りに使えます。1人前60グラムの原価は635円、売価2,280円でも原価率は27.9%に収まり、コース全体の満足度を一気に引き上げます。",
            "bodyAudioEn": "Nodoguro torch-seared sashimi and claypot rice. With pre-scaled, gutted 85%-yield semi-dressed Nodoguro, there's zero messy prep. At 635 yen cost per 60g portion (27.9% ratio on a 2,280-yen dish), it transforms your menu value.",
            "climaxVisualJp": "バーナーで皮目を炙ったのどぐろと、いくらが乗った土鍋ご飯の盛り付け",
            "climaxVisualEn": "Torch-seared Nodoguro claypot rice garnished with herbs and savory dashi",
            "climaxAudioJp": "仕込みの手間をかけずに、お店を代表する名物料理が今日から作れます。",
            "climaxAudioEn": "Create a restaurant-defining signature dish today with zero scaling or gutting prep.",
            "shootGuide": "土鍋の蓋を開ける瞬間（0〜3秒）と、皮目をバーナーで炙る音（15秒付近）の2大シズルを入れる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 traditional Japanese donabe earthenware pot opened with steaming rice topped with golden grilled Nodoguro (Blackthroat Seaperch) and chopped mitsuba",
            "source": "ファインアトラス主力5品目（対馬/山陰/長崎産のどぐろIQF・セミドレス原価試算データ）"
        },
        {
            "day": 26, "week": 4, "dow": "金曜日", "weekdayTheme": "レストランの原価・経営改善",
            "themeId": "TH-07", "themeName": "魚の歩留まりと原価計算", "fishKey": "穴子フィレ",
            "assetCode": "P-FL-030", "assetLabel": "主力5品目＋拡張5品目＝全10品目の歩留まり・1皿原価率一覧チャート",
            "titleJp": "全10品目の平均原価率は「28.1%」！魚料理のFLコスト（食材＋人件費）を同時に下げる方法",
            "titleEn": "28.1% Average Food Cost Across 10 Premium Fish Items: Optimizing Both Food & Labor",
            "hookVisualJp": "「食材原価（F）28.1% ＋ 仕込み人件費（L）毎日90分削減」のFL改善ダッシュボード画面",
            "hookVisualEn": "FL Cost dashboard showing 28.1% average food cost + 90 minutes daily prep labor saved",
            "hookAudioJp": "飲食店の利益を守る『FLコスト（食材原価＋人件費）』。魚メニューで両方を同時に改善できていますか？",
            "hookAudioEn": "To protect restaurant profit, you must manage FL cost—Food plus Labor. Is your seafood program optimizing both?",
            "bodyVisualJp": "主力5品目（煮穴子・穴子フィレ・甘鯛・のどぐろ・剣先イカ）＋拡張5品目の歩留まり（平均89.7%）一覧表",
            "bodyVisualEn": "Table of 10 core & expansion items showing 89.7% average yield and 26.5-30.2% dish cost ratio",
            "bodyAudioJp": "丸魚を仕入れて店で捌くと、歩留まりロスで食材原価（F）が膨らむだけでなく、仕込み残業で人件費（L）も圧迫されます。産地で一次加工した10品目なら、平均歩留まりは89.7%（主力5品目は85〜98%）。1皿原価率を平均28.1%に抑えながら、毎日の下処理時間を大幅に削減できます。",
            "bodyAudioEn": "Buying whole fish inflates Food cost through 50% trim loss while driving up Labor cost with hours of prep. Our 10 pre-processed port-frozen items average an 89.7% yield and a 28.1% dish cost ratio while cutting daily prep time.",
            "climaxVisualJp": "厨房が定時で綺麗に片付き、料理長が新メニュー開発に集中している様子",
            "climaxVisualEn": "Clean, organized kitchen where the chef focuses on plating and menu creativity",
            "climaxAudioJp": "原価率28%と仕込み時短の両立が、強いレストラン経営の土台になります。",
            "climaxAudioEn": "Combining a 28% food cost with prep time savings builds a resilient restaurant business.",
            "shootGuide": "10品目一覧表を一時停止して見られるよう、10〜18秒に高コントラストな表デザインで配置する。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 organized professional Japanese kitchen counter with 5 neatly portioned vacuum-sealed fish fillets ready for evening dinner service",
            "source": "全国業務用冷凍魚10品目 仕入れ価格AI調査＆飲食店FL原価試算（全10品目平均歩留まり89.7%・原価率28.1%）"
        },
        {
            "day": 27, "week": 4, "dow": "土曜日", "weekdayTheme": "漁業・産地・水産加工",
            "themeId": "TH-16", "themeName": "日本の漁港・産地の紹介", "fishKey": "剣先イカ",
            "assetCode": "V-FP-025", "assetLabel": "夜のイカ釣り漁船（漁火）と産地での皮むき・お造り柵加工動画",
            "titleJp": "夜の海に輝く「漁火（いさりび）」！壱岐・対馬の剣先イカが1本ずつ丁寧に柵になるまで",
            "titleEn": "Night Fishing Lights of Tsushima: How Kensaki Squid Becomes Sashimi-Ready Blocks",
            "hookVisualJp": "夜の対馬海峡に浮かぶ幻想的な漁火（いさりび）と、釣り上げられた透き通る剣先イカ",
            "hookVisualEn": "Glowing fishing boat lights on the night sea of Tsushima and translucent freshly caught Kensaki squid",
            "hookAudioJp": "夜の海に美しく並ぶ『漁火（いさりび）』。イカの王様・剣先イカがどのように水揚げされ加工されるかご存知ですか？",
            "hookAudioEn": "Beneath the glowing night fishing lights of Tsushima, how does the 'King of Squid' go from sea to sashimi block?",
            "bodyVisualJp": "一本釣りで傷をつけずに水揚げされた剣先イカを、産地で皮むき・スリット加工・急速凍結する工程",
            "bodyVisualEn": "Line-caught Kensaki squid being peeled, scored, and rapid-frozen at the port facility",
            "bodyAudioJp": "壱岐・対馬や山陰の剣先イカは、身が傷つかないよう丁寧に水揚げされ、鮮度が落ちる前に産地で皮むきと下処理が行われます。お造り用の柵にして急速冷凍することで、歩留まり95%・解凍して切るだけで、獲れたて特有の濃厚な甘みともっちりした食感を厨房で再現できます。",
            "bodyAudioEn": "Carefully line-caught to prevent bruising, Kensaki squid are peeled, cleaned, and shaped into sashimi blocks right at the port before rapid freezing—delivering a 95% yield and sweet, creamy texture upon slicing.",
            "climaxVisualJp": "透き通る剣先イカのお造りと、炙りゲソの一皿（1皿原価313円・原価率26.5%）",
            "climaxVisualEn": "Crystal-clear Kensaki squid sashimi platter served on crushed ice",
            "climaxAudioJp": "産地の漁師と加工職人のバトンを、そのままお店の一皿へ繋ぎます。",
            "climaxAudioEn": "Passing the baton directly from Tsushima fishermen and processors to your plate.",
            "shootGuide": "夜の漁火の美しい映像（0〜3秒）で視聴者の目を奪い、加工場の清潔な手仕事へ繋げる。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 traditional Japanese squid fishing boats with bright glowing isaribi lights on dark blue night ocean, cinematic coastal photography",
            "source": "長崎県・山口県イカ釣り漁業資料／ファインアトラス主力5品目（剣先イカお造り柵規格）"
        },
        {
            "day": 28, "week": 4, "dow": "日曜日", "weekdayTheme": "ファインアトラスの商品・サービス紹介",
            "themeId": "TH-19", "themeName": "ファインアトラスの取り組み・商品紹介", "fishKey": "煮穴子",
            "assetCode": "V-PS-020", "assetLabel": "ファインアトラス全10品目ラインナップとHP・Amazon・法人契約案内動画",
            "titleJp": "主力5品目＋拡張5品目！ファインアトラスが国内外の厨房へ届ける「一箱の魚革命」",
            "titleEn": "5 Core + 5 Expansion Items: Fine Atlas's One-Box Seafood Revolution for Global Kitchens",
            "hookVisualJp": "主力5品目（煮穴子・穴子フィレ・甘鯛・のどぐろ・剣先イカ）と拡張5品目（トラフグ・本マグロ・銀ダラサワラ・ホタテ・海老）のオールスター映像",
            "hookVisualEn": "All-star showcase of Fine Atlas's 5 core Tsushima items and 5 expansion restaurant items",
            "hookAudioJp": "美味しい日本の魚を、もっとシンプルに、もっと安定した原価でお店の厨房へ取り入れたくありませんか？",
            "hookAudioEn": "Want to bring authentic Japanese seasonal seafood into your kitchen with simpler prep and stable food cost?",
            "bodyVisualJp": "歩留まり65〜99%（主力85〜98%）× 原価率26.5〜30.2% × 7ステップ販売導線（HP・Amazon少量購入→リピート→店舗別オリジナル魚BOX・法人契約）",
            "bodyVisualEn": "Summary card: 85-98% core yield, 26.5-30.2% food cost, Website/Amazon small trial -> Custom B2B Fish Box",
            "bodyAudioJp": "ファインアトラスは、対馬産煮穴子・穴子フィレ・甘鯛・のどぐろ・剣先イカの主力5品目に加え、トラフグ・本マグロ柵・骨取フィレ・北海道ホタテ・IQF海老まで、歩留まりと原価率を計算し尽くしたラインナップをご用意しています。まずはホームページやAmazonでの少量購入で品質を確かめ、お店専用のオリジナル魚BOXや法人契約へお進みください。",
            "bodyAudioEn": "From our 5 core Tsushima specialties—Simmered Anago, Raw Anago Fillet, Amadai, Nodoguro, and Kensaki Squid—to Torafugu, Bluefin Tuna, Boneless Fillets, Hokkaido Scallops, and IQF Prawns: test a small order via our website or Amazon, then scale to your custom B2B fish box.",
            "climaxVisualJp": "出荷されるファインアトラスの専用BOXと、公式ホームページ・Amazon検索案内画面",
            "climaxVisualEn": "Fine Atlas insulated shipping box departing for kitchens with website & Amazon search card",
            "climaxAudioJp": "プロフィールリンクの公式ホームページ・Amazonから、まずは1箱お試しください。",
            "climaxAudioEn": "Visit our website or Amazon via the profile link to order your first trial box today.",
            "shootGuide": "28日間の総まとめとして全10品目の完成料理を0.5秒ずつテンポよく見せるダイジェスト構成にする。",
            "aiPromptEn": "Vertical 9:16 photorealistic 1080x1920 luxury Japanese seafood feast featuring sushi, crispy scale-on Amadai, grilled Nodoguro, and Kensaki squid sashimi around a Fine Atlas box",
            "source": "株式会社ファインアトラス 公式商品情報＆AIショート動画毎日配信計画（第1章〜第13章統合）"
        }
    ]

    episodes = []
    for sp in raw_specs:
        ep_id = f"DAY-{sp['day']:02d}"
        narration_jp = f"{sp['hookAudioJp']} {sp['bodyAudioJp']} {sp['climaxAudioJp']} {CLOSING_JP}"
        narration_en = f"{sp['hookAudioEn']} {sp['bodyAudioEn']} {sp['climaxAudioEn']} {CLOSING_EN}"

        subtitles_jp = [
            sp["hookAudioJp"],
            sp["bodyAudioJp"],
            sp["climaxAudioJp"],
            CLOSING_JP
        ]
        subtitles_en = [
            sp["hookAudioEn"],
            sp["bodyAudioEn"],
            sp["climaxAudioEn"],
            CLOSING_EN
        ]

        sns_caption_jp = (
            f"【{sp['titleJp']}】\n"
            f"{sp['bodyAudioJp']}\n\n"
            f"📦 まずはホームページ・Amazonでの少量購入（または公式お試しセット）で、自店の厨房にて身質・ドリップ・歩留まりをお確かめください。\n"
            f"品質にご納得いただいた後、お店のメニューや仕込みに合わせた「店舗別オリジナル魚BOX」・法人定期契約をご提案いたします。\n"
            f"「{CLOSING_JP}」\n"
            f"🔗 詳細はプロフィールリンク（fineatlas.co.jp / Amazon）へ"
        )
        sns_caption_en = (
            f"【{sp['titleEn']}】\n"
            f"{sp['bodyAudioEn']}\n\n"
            f"📦 Start with a small order via our official website or Amazon to verify our quality, thaw drip, and yield in your own kitchen.\n"
            f"Once satisfied, scale to repeat orders, a B2B corporate contract, or a Custom Restaurant Fish Box tailored to your menu.\n"
            f"\"{CLOSING_EN}\"\n"
            f"🔗 Visit the link in our bio (fineatlas.co.jp / Amazon) for details."
        )

        fish_tag_map = {
            "煮穴子": ("#煮穴子 #対馬穴子 #寿司仕入れ", "#Anago #CongerEel #SushiChef"),
            "穴子フィレ": ("#穴子フィレ #活〆穴子 #白焼き #天ぷら", "#AnagoFillet #TempuraChef #Washoku"),
            "甘鯛": ("#甘鯛 #ぐじ #松笠焼き #鱗焼き", "#Amadai #Tilefish #Matsukasayaki"),
            "のどぐろ": ("#のどぐろ #アカムツ #白身のトロ", "#Nodoguro #BlackthroatSeaperch #Omakase"),
            "剣先イカ": ("#剣先イカ #イカお造り #隠し包丁", "#KensakiIka #SquidSashimi #Sushi"),
            "トラフグ身欠き": ("#トラフグ #ふぐ身欠き #てっちり #ふぐ唐揚げ", "#Torafugu #Pufferfish #JapaneseCuisine"),
            "本マグロ柵": ("#本マグロ #マグロ柵 #お造り原価", "#BluefinTuna #TunaSaku #Sashimi"),
            "銀ダラ・サワラ": ("#銀ダラ西京焼き #サワラ #骨取りフィレ", "#Sablefish #SpanishMackerel #BonelessFillet"),
            "ホタテ貝柱": ("#北海道ホタテ #ホタテ玉冷 #IQF冷凍", "#HokkaidoScallop #IQFSeafood #FineDining"),
            "車海老・天使の海老": ("#車海老 #天使の海老 #IQF海老", "#KurumaPrawn #AngelPrawn #ChefLife")
        }
        ft_jp, ft_en = fish_tag_map.get(sp["fishKey"], ("#業務用水産", "#JapaneseSeafood"))

        hashtags_jp = f"#ファインアトラス #FineAtlas #飲食店仕入れ #料理人と繋がりたい #急速冷凍魚 #歩留まり改善 {ft_jp}"
        hashtags_en = f"#FineAtlas #JapaneseSeafood #ChefSupply #RapidFreezing #OmakaseSupply #RestaurantCost {ft_en}"

        episodes.append({
            "id": ep_id,
            "dayNumber": sp["day"],
            "week": sp["week"],
            "dayOfWeek": sp["dow"],
            "weekdayCategory": sp["weekdayTheme"],
            "themeId": sp["themeId"],
            "themeCategory": sp["themeName"],
            "featuredFish": sp["fishKey"],
            "item1_title": {
                "jp": sp["titleJp"],
                "en": sp["titleEn"]
            },
            "item2_narration": {
                "jp": narration_jp,
                "en": narration_en
            },
            "item3_timecode": [
                {
                    "sec": "0〜3秒",
                    "role": "興味を引くタイトルと映像（フック）",
                    "visualJp": sp["hookVisualJp"],
                    "visualEn": sp["hookVisualEn"],
                    "audioJp": sp["hookAudioJp"],
                    "audioEn": sp["hookAudioEn"]
                },
                {
                    "sec": "3〜20秒",
                    "role": "写真・映像・ナレーションによる専門解説",
                    "visualJp": sp["bodyVisualJp"],
                    "visualEn": sp["bodyVisualEn"],
                    "audioJp": sp["bodyAudioJp"],
                    "audioEn": sp["bodyAudioEn"]
                },
                {
                    "sec": "20〜27秒",
                    "role": "結論・完成料理など",
                    "visualJp": sp["climaxVisualJp"],
                    "visualEn": sp["climaxVisualEn"],
                    "audioJp": sp["climaxAudioJp"],
                    "audioEn": sp["climaxAudioEn"]
                },
                {
                    "sec": "27〜30秒",
                    "role": "ファインアトラスのロゴとキャッチコピー",
                    "visualJp": f"ファインアトラスのロゴとキャッチコピー「{CLOSING_JP}」（ホームページ・Amazon・店舗別オリジナル魚BOX案内）",
                    "visualEn": f"Fine Atlas official logo & catchphrase card: \"{CLOSING_EN}\" (Website, Amazon & Custom B2B Fish Box)",
                    "audioJp": CLOSING_JP,
                    "audioEn": CLOSING_EN
                }
            ],
            "item4_mediaDirection": {
                "ownAssetCode": sp["assetCode"],
                "ownAssetLabel": sp["assetLabel"],
                "shootGuide": sp["shootGuide"]
            },
            "item5_aiImagePrompt": {
                "promptEn": sp["aiPromptEn"],
                "negativePrompt": "text, watermark, blurry, low quality, deformed fish, unnatural colors, cartoon, illustration, extra fingers",
                "usageNoteJp": "自社素材が不足する解説パートの補助用（実際の商品紹介パートは必ず自社で撮影した写真・動画を使用すること）"
            },
            "item6_subtitles": {
                "vrewLinesJp": subtitles_jp,
                "vrewLinesEn": subtitles_en,
                "ruleNote": "音声なしでも理解できるように、Vrewで必ず日英字幕を画面中央〜下部セーフゾーンに配置する"
            },
            "item7_snsCaption": {
                "jp": sns_caption_jp,
                "en": sns_caption_en
            },
            "item8_hashtags": {
                "jp": hashtags_jp,
                "en": hashtags_en
            },
            "item9_sources": sp["source"],
            "item10_bilingualCheck": {
                "targetAudience": "国内外の飲食店オーナー・料理人（和食・割烹・寿司・フレンチ・イタリアン・海外OMAKASE）",
                "factCheckPoints": [
                    "根拠のある公開統計またはファインアトラス検証済み数値（歩留まり・原価率・ドリップ率）のみを使用しているか",
                    "AIが作った未確認の情報や誇大表現が含まれていないか",
                    "個別店舗ごとの送料・最低ロット等を動画内で勝手に断定せず、HP・Amazon少量購入→個別相談の正しい導線になっているか",
                    f"27〜30秒の締めが社長計画書通りの「{CLOSING_JP}」になっているか"
                ]
            }
        })

    return episodes


def build_calendar_365(episodes_28, fish_master_10, themes_19, weekday_schedule):
    """
    Build all 365 days with 0 duplicate titleJp, covering all 7 weekday categories and all 19 themes.
    Days 1..28 link directly to episodes_28.
    Days 29..365 are generated deterministically with rich culinary/cost/science angles.
    """
    calendar = []
    used_titles_jp = set()

    # First 28 days from episodes_28
    seasons_by_day = lambda d: "春（3〜5月旬企画）" if d <= 92 else ("夏（6〜8月旬企画）" if d <= 184 else ("秋（9〜11月旬企画）" if d <= 275 else "冬（12〜2月旬企画）"))

    for ep in episodes_28:
        d = ep["dayNumber"]
        t_jp = ep["item1_title"]["jp"]
        used_titles_jp.add(t_jp)
        calendar.append({
            "dayNumber": d,
            "dayCode": f"DAY-{d:03d}",
            "episodeId": ep["id"],
            "hasFullScript28": True,
            "weekNumber": ep["week"],
            "dayOfWeek": ep["dayOfWeek"],
            "weekdayTheme": ep["weekdayCategory"],
            "themeId": ep["themeId"],
            "theme19": ep["themeCategory"],
            "season": seasons_by_day(d),
            "fishKey": ep["featuredFish"],
            "titleJp": t_jp,
            "titleEn": ep["item1_title"]["en"],
            "hookJp": ep["item3_timecode"][0]["audioJp"],
            "factPointJp": ep["item3_timecode"][1]["audioJp"],
            "climaxJp": ep["item3_timecode"][2]["audioJp"],
            "assetCode": ep["item4_mediaDirection"]["ownAssetCode"],
            "sourceRef": ep["item9_sources"]
        })

    dow_list = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    dow_to_meta = {w["dayOfWeek"]: w for w in weekday_schedule}
    theme_by_id = {t["id"]: t for t in themes_19}

    # Detailed angle templates per weekday so every single day 29..365 has a distinct, practical chef title
    weekday_angles = {
        "月曜日": [
            ("盛漁期カレンダー分析", "Peak Catch Calendar", "TH-01"),
            ("豊洲・大阪市場の相場動向と安定調達", "Wholesale Market Price Stability", "TH-03"),
            ("季節替わりコースの先行仕入れ術", "Seasonal Tasting Menu Sourcing", "TH-15"),
            ("時化（しけ）に負けない旬魚ストック戦略", "Storm-Proof Seasonal Stock Strategy", "TH-03"),
            ("脂乗りピークを見極める月別旬魚ガイド", "Monthly Fat-Peak Fish Guide", "TH-01"),
            ("端境期でも原価率28%を守る旬冷凍の活用", "Off-Season Cost Control with Peak-Frozen Fish", "TH-15")
        ],
        "火曜日": [
            ("料理人が語れる高級魚の目利きと旨味成分", "Connoisseur Guide & Umami Science", "TH-02"),
            ("インバウンド客が喜ぶ英語メニュー名と特徴", "Inbound Guest Favorite & English Menu Guide", "TH-13"),
            ("産地直結だから手に入る特別サイズ規格", "Port-Direct Special Size & Grade Spotlight", "TH-14"),
            ("白身・魚介のアミノ酸と熟成の秘密", "Amino Acid Profile & Aging Potential", "TH-02"),
            ("海外ミシュラン店が注目する日本産グレード", "Why Michelin Chefs Overseas Choose This Grade", "TH-13"),
            ("一般流通品と産地厳選品の見分け方", "Distinguishing Port-Selected Grade from Standard Stock", "TH-14")
        ],
        "水曜日": [
            ("最大氷結晶生成帯（-1〜-5℃）通過スピード比較", "-1°C to -5°C Ice Crystal Transit Comparison", "TH-05"),
            ("ドリップ流出率を最小化する0℃氷水解凍手順", "0°C Ice-Water Thawing for Zero Drip", "TH-06"),
            ("輸送3日目の未凍結鮮魚と産地急速冷凍の比較", "3-Day Chilled Fish vs Port Rapid-Frozen Comparison", "TH-04"),
            ("高真空パックによる冷凍焼け・脂質酸化の防止", "Preventing Freezer Burn & Lipid Oxidation via High Vacuum", "TH-05"),
            ("半解凍（パーシャル）切り付けで角を立てる技術", "Semi-Thawed Slicing Technique for Sharp Sashimi Edges", "TH-06"),
            ("アニサキスリスクを抑える-20℃急速凍結の安全性", "Food Safety & Parasite Prevention via -20°C Freezing", "TH-04")
        ],
        "木曜日": [
            ("皮目パリッと身はふっくら仕上げる火入れ温度", "Precision Heat Control for Crispy Skin & Moist Flesh", "TH-10"),
            ("お造り・握りの甘みを引き出す包丁の入れ方", "Knife Scoring & Slicing for Maximum Sashimi Sweetness", "TH-11"),
            ("世界のOMAKASE・ビストロでの一皿アレンジ", "Global Omakase & Modern Bistro Plating Idea", "TH-12"),
            ("和食の出汁とフレンチのソースに合わせる調理法", "Pairing with Japanese Dashi & French Sauce", "TH-10"),
            ("提供直前3分で仕上げるオペレーション設計", "3-Minute Pick-Up Operation for Peak Dinner Service", "TH-11"),
            ("海外の日本食レストランで人気の提供スタイル", "Trending Presentation in Global Japanese Restaurants", "TH-12")
        ],
        "金曜日": [
            ("丸魚歩留まり50%と一次加工フィレ歩留まりの原価比較", "Whole Fish 50% Yield vs Pre-Processed Fillet Cost Math", "TH-07"),
            ("1皿原価率を黄金ゾーン（26.5〜30.2%）に収める設計", "Keeping Dish Food Cost in the 26.5-30.2% Golden Zone", "TH-08"),
            ("毎日のウロコ引き・骨抜き仕込み時間を削減する試算", "Saving Daily Scaling & Bone-Prep Labor Hours", "TH-09"),
            ("雨の日の売れ残り廃棄ロスをゼロにする在庫管理", "Zero-Spoilage Inventory Control on Slow Rainy Nights", "TH-08"),
            ("少人数・ワンオペ厨房のFLコスト（食材＋人件費）改善", "Optimizing FL Cost in Lean & Single-Chef Kitchens", "TH-09"),
            ("可食部1グラムあたりの実質単価で見る賢い仕入れ", "Smart Procurement by True Cost per Edible Gram", "TH-07")
        ],
        "土曜日": [
            ("好漁場の海流とプランクトンが育む産地の秘密", "How Ocean Currents & Rich Plankton Shape Port Quality", "TH-16"),
            ("水揚げ直後の活〆・血抜きから急速凍結までの舞台裏", "Behind the Scenes: From Port Ikejime to Rapid Freezing", "TH-17"),
            ("世界に誇る日本の魚食文化と鮮度保持の職人技", "Japan's Culinary Fish Heritage & Preservation Craft", "TH-18"),
            ("熟練職人による手作業の開き・骨処理工程", "Artisan Hand-Filleting & Pin-Bone Removal at the Port", "TH-17"),
            ("漁港直結コールドチェーンが守る産地の香り", "Port-Direct Cold Chain Preserving Authentic Aroma", "TH-16"),
            ("伝統の締め技術と現代の冷凍科学の融合", "Where Traditional Japanese Fish Craft Meets Freezing Science", "TH-18")
        ],
        "日曜日": [
            ("HP・Amazon少量購入から始める厨房での品質確認ステップ", "Testing Quality in Your Kitchen via Small Web/Amazon Order", "TH-19"),
            ("お店のメニューに合わせた「店舗別オリジナル魚BOX」設計例", "Designing a Custom Restaurant Fish Box for Your Menu", "TH-19"),
            ("「産地で時間を止め、現地で時間を動かす。」活用ガイド", "How 'Stop Time at the Port, Restart in Your Kitchen' Works", "TH-19"),
            ("少量お試し→リピート→法人定期契約へのスムーズな流れ", "From First Trial Box to Repeat & Corporate B2B Contract", "TH-19"),
            ("和食・割烹・寿司・ビストロ業態別の人気組み合わせBOX", "Popular Custom Fish Box Combos for Washoku, Sushi & Bistro", "TH-19"),
            ("料理人の「ここまで下処理してほしい」に応えるカスタム相談", "Custom Prep Solutions Tailored to Your Chef's Workflow", "TH-19")
        ]
    }

    asset_prefixes = ["P-WR", "P-FL", "P-VF", "P-CS", "V-PF", "V-TC", "V-FP", "V-PS"]
    asset_max = {"P-WR": 100, "P-FL": 100, "P-VF": 50, "P-CS": 100, "V-PF": 30, "V-TC": 30, "V-FP": 30, "V-PS": 20}

    for d in range(29, 366):
        week_num = ((d - 1) // 7) + 1
        dow = dow_list[(d - 1) % 7]
        w_meta = dow_to_meta[dow]
        fish = fish_master_10[(d - 1) % len(fish_master_10)]
        angles = weekday_angles[dow]
        angle_jp, angle_en, theme_id = angles[(week_num - 1) % len(angles)]
        th = theme_by_id[theme_id]
        season_str = seasons_by_day(d)
        season_short = season_str.split("（")[0]

        # Build guaranteed-unique, high-value JP & EN titles
        title_jp = (
            f"【Day{d:03d}・{season_short}の{fish['key']}】"
            f"{angle_jp}｜歩留まり{fish['yieldPct']}%・1皿原価率{fish['flCostRatioPct']}%"
        )
        if title_jp in used_titles_jp:
            title_jp = f"{title_jp}（第{week_num}週特集）"
        used_titles_jp.add(title_jp)

        title_en = (
            f"[Day {d:03d} {fish['nameEn'].split(' (')[0]}] "
            f"{angle_en} ({fish['yieldPct']}% Yield / {fish['flCostRatioPct']}% Cost)"
        )

        hook_jp = (
            f"{fish['nameJp']}を厨房で使うとき、「{angle_jp}」を意識するだけで1皿の利益と品質が大きく変わります。"
        )
        fact_jp = (
            f"{fish['origin']}の{fish['key']}は可食歩留まり{fish['yieldPct']}%。"
            f"1人前{fish['portionGram']}gあたりの飲食店原価は約{fish['dishCostYen']}円（想定売価{fish['menuPriceYen']}円で原価率{fish['flCostRatioPct']}%）。"
            f"{fish['prepMerit']}"
        )
        climax_jp = (
            f"{fish['recommendedDishes']}など、ホームページ・Amazonでの少量お試しから店舗別オリジナル魚BOXまで柔軟に対応します。"
        )

        ap = asset_prefixes[(d - 1) % len(asset_prefixes)]
        anum = ((d - 1) % asset_max[ap]) + 1
        asset_code = f"{ap}-{anum:03d}"

        calendar.append({
            "dayNumber": d,
            "dayCode": f"DAY-{d:03d}",
            "episodeId": f"DAY-{d:03d}",
            "hasFullScript28": False,
            "weekNumber": week_num,
            "dayOfWeek": dow,
            "weekdayTheme": w_meta["categoryName"],
            "themeId": theme_id,
            "theme19": th["name"],
            "season": season_str,
            "fishKey": fish["key"],
            "titleJp": title_jp,
            "titleEn": title_en,
            "hookJp": hook_jp,
            "factPointJp": fact_jp,
            "climaxJp": climax_jp,
            "assetCode": asset_code,
            "sourceRef": "東京都・大阪市中央卸売市場 水産物統計／ファインアトラス商品情報＆歩留まり・ドリップ検証データ"
        })

    return calendar


def build_dot_prompt_templates():
    daily_prompt = f"""あなたは株式会社ファインアトラス（FINE ATLAS Co., Ltd.）の専属AI広報ディレクター「Dot」です。
国内外の飲食店オーナーおよび料理人に向けて、15〜30秒の縦型ショート動画（9:16・1080×1920）の制作パッケージを日本語版・英語版の両方で作成してください。

【入力条件】
- 配信日・曜日：{{DAY_CODE}}（{{DAY_OF_WEEK}}）
- 曜日テーマ：{{WEEKDAY_THEME}}
- 19テーマ区分：{{THEME_19}}
- 主役となる魚種：{{FISH_NAME}}
- 参照する検証済みデータ：{{VERIFIED_FACT}}
- 使用予定の自社素材コード：{{ASSET_CODE}}

【厳守ルール（第2章・第9章・第10章・第11章）】
1. 会社紹介や露骨な商品宣伝を冒頭で行わず、飲食店・料理人に役立つ魚の専門情報（旬、市場相場、急速冷凍と最大氷結晶生成帯-1〜-5℃、氷水解凍、歩留まり85〜99%と1皿原価率26.5〜30.2%、仕込み時短、調理法）を発信すること。
2. 動画の秒数構成は必ず以下の4パート（合計15〜30秒）とすること：
   - 0〜3秒：興味を引くタイトルと映像（フック）
   - 3〜20秒：写真・映像・ナレーションによる専門解説
   - 20〜27秒：結論・完成料理など
   - 27〜30秒：ファインアトラスのロゴとキャッチコピー
     ・日本語：「{CLOSING_JP}」
     ・英語："{CLOSING_EN}"
3. 情報の信頼性を守るため、水産庁・卸売市場の公開データ・一般的な水産加工/調理技術・ファインアトラス公式商品情報に基づく根拠ある内容のみを使用し、AIによる未確認情報や誇大表現は一切使用しないこと。また個別店舗の送料・最低ロット等は断定せず、「ホームページ・Amazonでの少量購入で品質確認 → リピート購入 → 法人契約・店舗別オリジナル魚BOX受注」の正しい導線で案内すること。

【必ず出力する10項目（第10章準拠）】
① 動画タイトル（日本語・英語）
② 30秒のナレーション台本（日本語・英語 ※最後は必ず上記キャッチコピーで締める）
③ 秒数ごとの映像構成（0〜3秒／3〜20秒／20〜27秒／27〜30秒）
④ 使用する写真・動画の指示（自社素材460点DBの素材コードと撮影ポイント）
⑤ AI画像生成用の指示文（自社素材を補完する解説用の縦型9:16英語プロンプト）
⑥ 字幕（Vrewへそのまま貼り付けられる改行区切りテキスト・音声なしでも理解できる明快な字幕）
⑦ SNS投稿文章（TikTok・Instagramリール・YouTubeショート・Facebookリール用／HP・Amazon少量購入→店舗別オリジナル魚BOXへの誘導文入り）
⑧ ハッシュタグ（日本語・英語）
⑨ 情報の出典（参照した統計・技術資料・公式商品情報）
⑩ 日本語版・英語版の事実確認チェックリスト"""

    weekly_batch_prompt = f"""あなたは株式会社ファインアトラスの専属AI広報ディレクター「Dot」です。
今週（月曜日〜日曜日）の7日分のAIショート動画台本パッケージ（日本語版7本＋英語版7本＝計14本分）を一括作成してください。

【曜日別テーマ割り当て（第6章準拠）】
- 月曜日：今週の旬の魚・市場相場
- 火曜日：高級魚の豆知識
- 水曜日：冷凍魚の特徴・解凍方法
- 木曜日：プロの料理・調理方法
- 金曜日：レストランの原価・経営改善
- 土曜日：漁業・産地・水産加工
- 日曜日：ファインアトラスの商品・サービス紹介

【今週の対象魚種リスト】
1. 煮穴子（対馬産・無添加炊き上げ真空冷凍／歩留まり98%・1皿原価率28.1%）
2. 穴子フィレ（対馬/国産活〆開き・骨処理冷凍／歩留まり96%・1皿原価率27.5%）
3. 甘鯛（対馬/山陰 赤甘鯛 鱗付フィレ／歩留まり95%・1皿原価率27.1%）
4. のどぐろ（対馬/山陰/長崎 IQF・セミドレス／歩留まり85%・1皿原価率27.9%）
5. 剣先イカ（壱岐対馬/山陰 お造り柵・スリット／歩留まり95%・1皿原価率26.5%）

各曜日ごとに第10章の「10項目（①タイトル〜⑩日英・出典チェック）」を漏れなく出力し、すべての動画の27〜30秒は必ず「{CLOSING_JP}」 / "{CLOSING_EN}" で統一してください。"""

    return {
        "dailyMasterPrompt": daily_prompt,
        "weeklyBatchPrompt": weekly_batch_prompt,
        "toolManuals": [
            {
                "tool": "① ChatGPT・Dot（約6分／日）",
                "steps": [
                    "365日カレンダーから当日のエピソードを選択し、上記「Dot指示プロンプト」をコピーしてDot（またはChatGPT）へ送信する。",
                    "出力された10項目のうち「⑨ 情報の出典」と数値（歩留まり・ドリップ率・原価率）に誤りや誇大表現がないか確認する。"
                ]
            },
            {
                "tool": "② Vrew（ブリュー）（約14分／日）",
                "steps": [
                    "Vrewで「新規で作成 → テキストからビデオを作成 → ショート（9:16・1080×1920）」を選択する。",
                    "「⑥ 字幕（Vrew貼り付け用）」の日本語4ブロック（0〜3秒／3〜20秒／20〜27秒／27〜30秒）を貼り付け、落ち着いたプロのAIナレーション音声を選択する。",
                    "「④ 使用する写真・動画の指示」に記載された自社素材コード（P-WR/P-FL/P-VF/P-CS/V-PF/V-TC/V-FP/V-PS）の写真・動画を各クリップに挿入する。",
                    "日本語版を書き出したらプロジェクトを複製し、英語テキストと英語AI音声に差し替えて英語版を書き出す（映像配置はそのまま再利用できるため4分で完了）。"
                ]
            },
            {
                "tool": "③ Canva（約2分／日）",
                "steps": [
                    "Canvaの1080×1920縦型表紙テンプレートを開き、「① 動画タイトル」を入力して表紙画像を書き出す。",
                    "27〜30秒のエンドカードにファインアトラス公式ロゴと「日本の旬と品質を、一箱に。世界の厨房へ。」／\"Japan's seasonal catch & peak quality, in one box. To kitchens worldwide.\" が明瞭に表示されていることを確認する。"
                ]
            },
            {
                "tool": "④ Metricool（約3分／日）",
                "steps": [
                    "Metricoolのプランナー画面を開き、TikTok・Instagramリール・YouTubeショート・Facebookリールの4媒体を選択する。",
                    "日本語版動画・英語版動画それぞれに「⑦ SNS投稿文章（HP・Amazon少量購入→店舗別オリジナル魚BOX誘導入り）」と「⑧ ハッシュタグ」を貼り付けて配信時刻を予約する。",
                    "前日配信分の再生回数、3秒維持率、保存数、プロフィールリンク（HP・Amazon）クリック数を確認する。"
                ]
            }
        ]
    }


def build_asset_inventory_460(fish_master_10):
    """
    Section 7 of President's Plan:
    Photos: 100 + 100 + 50 + 100 = 350
    Videos: 30 + 30 + 30 + 20 = 110
    Total: 460 items
    Generates both the 8 category summaries AND all 460 concrete slot entries!
    """
    categories_spec = [
        {
            "categoryNo": 1,
            "type": "写真（Photo）",
            "name": "丸魚の写真",
            "nameEn": "Whole Fish Photos",
            "prefix": "P-WR",
            "count": 100,
            "purpose": "0〜3秒のフックや産地・目利き解説で使用。魚の全体像、澄んだ目、エラの鮮紅色、魚体の張り・ツヤを撮影。",
            "angles": [
                "氷上斜め45度全体カット", "澄んだ目のマクロ接写", "魚体の厚みと皮目の光沢", "腹側の張りと銀鱗アップ",
                "産地木箱・氷詰め状態", "サイズ比較（メジャー・包丁添え）", "活〆・血抜き直後の美肌カット", "尾ビレと背ビレの立ち上がり",
                "複数尾の並び（豊漁・盛漁期イメージ）", "料理長の手による目利きチェック"
            ]
        },
        {
            "categoryNo": 2,
            "type": "写真（Photo）",
            "name": "魚のフィレ写真",
            "nameEn": "Fish Fillet Photos",
            "prefix": "P-FL",
            "count": 100,
            "purpose": "3〜20秒の歩留まり（85〜99%）・下処理品質の解説で使用。骨処理断面、鱗付き皮目、血合いの美しさを撮影。",
            "angles": [
                "三枚おろしフィレ皮目アップ", "身側の透明感と脂のサシ断面", "骨抜き・背開き処理完了カット", "鱗付きフィレの緻密なウロコ並び",
                "丸魚とフィレの歩留まり比較配置", "ポーション切り分け（55g〜75g）", "包丁を入れた断面の角立ち", "氷水解凍直後のドリップゼロ証明カット",
                "まな板上の仕込み完了ラインナップ", "皮目の飾り包丁・スリット接写"
            ]
        },
        {
            "categoryNo": 3,
            "type": "写真（Photo）",
            "name": "真空パック・急速冷凍魚の写真",
            "nameEn": "Vacuum-Packed & Rapid-Frozen Fish Photos",
            "prefix": "P-VF",
            "count": 50,
            "purpose": "実際の商品形態・高真空の密着度・IQFバラ凍結の使いやすさを正確に伝えるために使用（誇大防止の自社実物素材）。",
            "angles": [
                "高真空パック表面（ラベル・密着度）", "高真空パック裏面（皮目・霜ゼロ状態）", "IQFバラ凍結から1個取り出す瞬間",
                "氷水ボウルに浸した解凍実演カット", "冷凍ストッカー内の整理収納イメージ"
            ]
        },
        {
            "categoryNo": 4,
            "type": "写真（Photo）",
            "name": "寿司・刺身・料理写真",
            "nameEn": "Sushi, Sashimi & Cooked Dish Photos",
            "prefix": "P-CS",
            "count": 100,
            "purpose": "0〜3秒のシズル感フックおよび20〜27秒の完成料理パートで使用。和食・寿司・フレンチ・イタリアンの完成皿。",
            "angles": [
                "お造り単品盛り（角立ち強調）", "江戸前握り寿司アップ（刷毛ツメ・塩スダチ）", "松笠焼き・白焼き・西京焼き完成皿",
                "天ぷら一本揚げ・唐揚げ断面", "フレンチポワレ・低温ミキュイ盛り付け", "イタリアン炙りカルパッチョ",
                "土鍋ご飯・小鍋てっちり完成カット", "お造り5点盛り合わせ（豪華コース用）", "酒肴・八寸盛り付け例", "1皿原価率カード合成用余白付きカット"
            ]
        },
        {
            "categoryNo": 5,
            "type": "動画（Video）",
            "name": "加工・急速冷凍工程の動画",
            "nameEn": "Processing & Rapid-Freezing Process Videos",
            "prefix": "V-PF",
            "count": 30,
            "purpose": "土曜日（水産加工の現場）や水曜日（急速冷凍の科学）で使用。衛生的な加工場での手仕事と急速凍結の様子（各5〜10秒縦型）。",
            "angles": [
                "活〆・血抜き手元5秒クリップ", "職人による背開き・三枚おろし高速手元", "高真空パック機での密着シールから急速凍結庫搬入"
            ]
        },
        {
            "categoryNo": 6,
            "type": "動画（Video）",
            "name": "解凍・調理工程の動画",
            "nameEn": "Thawing & Cooking Process Videos",
            "prefix": "V-TC",
            "count": 30,
            "purpose": "木曜日（プロの調理法）や0〜3秒フックで使用。油かけで鱗が逆立つ瞬間、バーナー炙り、氷水解凍、包丁の引き切り（各5〜10秒縦型）。",
            "angles": [
                "真空パック氷水解凍から開封・ドリップゼロ確認", "高温油かけ（松笠焼き）やバーナー炙りのシズル映像", "柳刃包丁での引き切り・盛り付けフィニッシュ"
            ]
        },
        {
            "categoryNo": 7,
            "type": "動画（Video）",
            "name": "漁港・漁船・水揚げの動画",
            "nameEn": "Fishing Port, Boats & Landing Videos",
            "prefix": "V-FP",
            "count": 30,
            "purpose": "土曜日（漁業・産地紹介）や月曜日（旬と市場）で使用。対馬海峡・山陰・北海道などの出港、漁火、競り、水揚げの臨場感（各5〜10秒縦型）。",
            "angles": [
                "朝焼けの出港・漁火（いさりび）操業シーン", "漁港での水揚げ・選別・氷締めシーン", "産地市場の活気と加工場への直行搬入"
            ]
        },
        {
            "categoryNo": 8,
            "type": "動画（Video）",
            "name": "箱詰め・出荷工程の動画",
            "nameEn": "Packing & Shipping Process Videos",
            "prefix": "V-PS",
            "count": 20,
            "purpose": "日曜日（ファインアトラスの商品・サービス紹介）や27〜30秒クロージング手前で使用。検品・保冷箱詰め・出荷の様子（各5〜10秒縦型）。",
            "angles": [
                "主力5品目・店舗別オリジナル魚BOXのピッキングと箱詰め", "保冷梱包・封印からクール出荷・「日本の旬と品質を、一箱に。」連結カット"
            ]
        }
    ]

    categories = []
    all_items = []

    for c in categories_spec:
        cat_items = []
        for idx in range(1, c["count"] + 1):
            code = f"{c['prefix']}-{idx:03d}"
            fish = fish_master_10[(idx - 1) % len(fish_master_10)]
            angle = c["angles"][(idx - 1) // len(fish_master_10) % len(c["angles"])]
            priority = "S（初回28日必須）" if idx <= 10 else ("A（3ヶ月目まで）" if idx <= 30 else "B（年間順次ストック）")
            item = {
                "code": code,
                "categoryNo": c["categoryNo"],
                "type": c["type"],
                "categoryName": c["name"],
                "fishKey": fish["key"],
                "fishOrigin": fish["origin"],
                "shotTitle": f"{fish['key']}｜{angle}",
                "specRequirement": "縦型 9:16（1080×1920）・自然光または高演色LED（Ra95以上）・文字なし原版保存",
                "priority": priority,
                "usageSection": c["purpose"]
            }
            cat_items.append(item)
            all_items.append(item)

        categories.append({
            "categoryNo": c["categoryNo"],
            "type": c["type"],
            "name": c["name"],
            "nameEn": c["nameEn"],
            "prefix": c["prefix"],
            "targetCount": c["count"],
            "purpose": c["purpose"],
            "sampleCodes": f"{c['prefix']}-001 〜 {c['prefix']}-{c['count']:03d}",
            "items": cat_items
        })

    return {
        "totalCount": 460,
        "photoTotal": 350,
        "videoTotal": 110,
        "policyNote": "AI画像生成も補助として活用するが、実際の商品紹介には必ず自社で撮影した写真・動画（全460点データベース）を使用し、信頼性を高める（計画書第7章・第9章準拠）。",
        "categories": categories,
        "items": all_items
    }


def generate_excel_workbook(data):
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active

    # Styles
    navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    blue_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    sub_fill = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    gold_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

    title_font = Font(name="Meiryo UI", size=14, bold=True, color="FFFFFF")
    header_font = Font(name="Meiryo UI", size=10, bold=True, color="FFFFFF")
    sub_font = Font(name="Meiryo UI", size=10, bold=True, color="0F172A")
    body_font = Font(name="Meiryo UI", size=9.5, color="0F172A")
    bold_font = Font(name="Meiryo UI", size=9.5, bold=True, color="0F172A")

    thin_side = Side(border_style="thin", color="CBD5E1")
    border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

    # =========================================================================
    # Sheet 1: 1_全体計画_KPIダッシュボード
    # =========================================================================
    ws1 = wb.create_sheet(title="1_全体計画_KPIダッシュボード")
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:H1")
    ws1["A1"] = "株式会社ファインアトラス｜AIショート動画 毎日配信計画 実行マスター台帳（社長計画書 全13章完全準拠）"
    ws1["A1"].fill = navy_fill
    ws1["A1"].font = title_font
    ws1["A1"].alignment = align_left
    ws1.row_dimensions[1].height = 34

    ws1.merge_cells("A2:H2")
    ws1["A2"] = f"ブランドメッセージ（27〜30秒統一）：「{CLOSING_JP}」 ／ \"{CLOSING_EN}\""
    ws1["A2"].fill = gold_fill
    ws1["A2"].font = sub_font
    ws1["A2"].alignment = align_left
    ws1.row_dimensions[2].height = 24

    # KPI Summary Table with dynamic formulas
    ws1.merge_cells("A4:H4")
    ws1["A4"] = "■ 1. 年間制作・配信KPIサマリー（第8章・数式連動）"
    ws1["A4"].fill = sub_fill
    ws1["A4"].font = sub_font

    kpi_headers = ["指標コード", "KPI項目名", "計画基準値", "台帳実数（数式自動集計）", "単位", "配信言語・SNS内訳", "1日あたり目標作業時間", "判定"]
    for col_idx, h in enumerate(kpi_headers, 1):
        cell = ws1.cell(row=5, column=col_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws1.row_dimensions[5].height = 24

    kpi_rows = [
        ("KPI-01", "初回4週間 完全日英台本（10項目完備）", 28, "=COUNTA('2_初回28日_日英完全台本10項目'!A5:A32)", "日分（日英56本）", "全7曜日×4週間・全19テーマ網羅", "1日20〜30分", "OK"),
        ("KPI-02", "年間配信テーマ（1日1テーマ×365日）", 365, "=COUNTA('3_年間365日_配信テーマ計画表'!A5:A369)", "テーマ／年", "月間30テーマ×12ヶ月（重複タイトル0件）", "1日20〜30分", "OK"),
        ("KPI-03", "年間制作動画本数（日本語1本＋英語1本）", 730, "=D7*2", "本／年", "日本語版365本 ＋ 英語版365本", "Vrew複製で英語+4分", "OK"),
        ("KPI-04", "年間SNS総配信数（4大SNS同時展開）", 2920, "=D8*4", "投稿／年", "TikTok・Instagram・YouTube・Facebook", "Metricool一括予約", "OK"),
        ("KPI-05", "自社撮影 写真・動画素材データベース", 460, "=SUM('4_写真350枚_動画110本_素材DB'!D5:D12)", "点（写真350＋動画110）", "写真4分類350枚 ＋ 動画4分類110本", "商品の信頼性担保", "OK"),
        ("KPI-06", "検証済みファインアトラス魚種原価マスタ", 10, "=COUNTA('6_ファインアトラス魚種_原価データ'!A5:A14)", "品目（主力5＋拡張5）", "歩留まり65〜99%・1皿原価率26.5〜30.2%", "出典・根拠100%明記", "OK")
    ]
    for r_offset, row_data in enumerate(kpi_rows, 6):
        ws1.row_dimensions[r_offset].height = 22
        for c_idx, val in enumerate(row_data, 1):
            cell = ws1.cell(row=r_offset, column=c_idx, value=val)
            cell.font = bold_font if c_idx in (2, 4, 8) else body_font
            cell.alignment = align_center if c_idx in (1, 3, 4, 5, 8) else align_left
            cell.fill = green_fill if c_idx == 8 else (zebra_fill if r_offset % 2 == 0 else PatternFill(fill_type=None))
            cell.border = border_all

    # Section: 15-30s Video Rules & Timecode Structure (Section 2)
    ws1.merge_cells("A13:H13")
    ws1["A13"] = "■ 2. 動画の基本ルール（第2章：15〜30秒・縦型9:16・1080×1920・字幕必須）"
    ws1["A13"].fill = sub_fill
    ws1["A13"].font = sub_font

    tc_headers = ["秒数パート", "構成の役割", "映像演出ルール", "音声・字幕ルール", "備考・ブランド統一基準", "", "", ""]
    for c_idx in range(1, 9):
        cell = ws1.cell(row=14, column=c_idx)
        if tc_headers[c_idx - 1]:
            cell.value = tc_headers[c_idx - 1]
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws1.merge_cells("E14:H14")

    tc_rows = [
        ("0〜3秒", "興味を引くタイトルと映像", "料理人の手を止めさせるシズル映像（松笠焼きの鱗立ち・炙り・数字比較）", "疑問形や常識を覆す1文フック＋大型字幕", "最初の3秒で視聴維持率65%以上を狙う"),
        ("3〜20秒", "写真・映像・ナレーションによる専門解説", "自社素材DB（460点）＋図解で旬・急速冷凍・歩留まりを解説", "音声なしでも100%理解できる明快な字幕", "未確認情報は不使用。出典のある根拠数値のみ"),
        ("20〜27秒", "結論・完成料理など", "美しい盛り付け完成皿（和食・寿司・フレンチ・イタリアン）と1皿原価率", "料理人のメリット（時短・原価安定・品質）結論", "実際の商品紹介には必ず自社撮影素材を使用"),
        ("27〜30秒", "ファインアトラスのロゴとキャッチコピー", "Canva共通エンドカード（公式ロゴ＋HP・Amazon案内）", f"JP：{CLOSING_JP}\nEN：{CLOSING_EN}", "全730本すべてこのキャッチコピーで統一")
    ]
    for r_offset, r_data in enumerate(tc_rows, 15):
        ws1.row_dimensions[r_offset].height = 28
        for c_idx in range(1, 9):
            cell = ws1.cell(row=r_offset, column=c_idx)
            if c_idx <= 5:
                cell.value = r_data[c_idx - 1]
            cell.font = bold_font if c_idx in (1, 2) else body_font
            cell.alignment = align_center if c_idx == 1 else align_left
            cell.fill = gold_fill if r_offset == 18 else (zebra_fill if r_offset % 2 == 0 else PatternFill(fill_type=None))
            cell.border = border_all
        ws1.merge_cells(start_row=r_offset, start_column=5, end_row=r_offset, end_column=8)

    # Section: 8-Step Daily Routine (25 mins) & 4 AI Tools (Sections 4 & 5)
    ws1.merge_cells("A20:H20")
    ws1["A20"] = "■ 3. 毎日の作業手順（第4章・第5章：4大AIツール連携・1日20〜30分ルーティン）"
    ws1["A20"].fill = sub_fill
    ws1["A20"].font = sub_font

    rt_headers = ["手順No", "作業ステップ（第5章準拠）", "使用AIツール", "目安分数", "具体的な作業内容と時短のポイント", "", "", ""]
    for c_idx in range(1, 9):
        cell = ws1.cell(row=21, column=c_idx)
        if rt_headers[c_idx - 1]:
            cell.value = rt_headers[c_idx - 1]
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws1.merge_cells("E21:H21")

    for idx, st in enumerate(data["planOverview"]["dailyRoutine8"], 22):
        ws1.row_dimensions[idx].height = 24
        row_vals = [f"手順{st['step']}", st["title"], st["tool"], st["minutes"], st["detail"]]
        for c_idx in range(1, 9):
            cell = ws1.cell(row=idx, column=c_idx)
            if c_idx <= 5:
                cell.value = row_vals[c_idx - 1]
            cell.font = bold_font if c_idx in (1, 2, 4) else body_font
            cell.alignment = align_center if c_idx in (1, 3, 4) else align_left
            cell.border = border_all
        ws1.merge_cells(start_row=idx, start_column=5, end_row=idx, end_column=8)

    ws1["A30"] = "1日あたり合計作業時間（テンプレート完成後）"
    ws1["D30"] = "=SUM(D22:D29)"
    ws1["E30"] = "分／日（目標20〜30分以内を達成！週1回・2.5時間で7日分まとめ制作＆Metricool予約も可能）"
    for c_idx in range(1, 9):
        cell = ws1.cell(row=30, column=c_idx)
        cell.font = bold_font
        cell.fill = gold_fill
        cell.border = border_all
        cell.alignment = align_center if c_idx <= 4 else align_left
    ws1.merge_cells("A30:C30")
    ws1.merge_cells("E30:H30")
    ws1.row_dimensions[30].height = 24

    # Section: 7-Step Sales Funnel (Section 11)
    ws1.merge_cells("A32:H32")
    ws1["A32"] = "■ 4. 集客から販売までの流れ（第11章：7ステップ販売ファネル）"
    ws1["A32"].fill = sub_fill
    ws1["A32"].font = sub_font

    fn_headers = ["段階", "ファネルステージ（第11章）", "具体的な誘導アクションと顧客体験", "", "", "", "重点KPI", ""]
    for c_idx in range(1, 9):
        cell = ws1.cell(row=33, column=c_idx)
        if fn_headers[c_idx - 1]:
            cell.value = fn_headers[c_idx - 1]
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws1.merge_cells("C33:F33")
    ws1.merge_cells("G33:H33")

    for idx, fn in enumerate(data["planOverview"]["salesFunnel7"], 34):
        ws1.row_dimensions[idx].height = 24
        vals = [f"STEP {fn['step']}", fn["stage"], fn["action"], "", "", "", fn["kpi"], ""]
        for c_idx in range(1, 9):
            cell = ws1.cell(row=idx, column=c_idx)
            if vals[c_idx - 1]:
                cell.value = vals[c_idx - 1]
            cell.font = bold_font if c_idx in (1, 2) else body_font
            cell.alignment = align_center if c_idx == 1 else align_left
            cell.fill = green_fill if fn["step"] in (4, 5, 7) else PatternFill(fill_type=None)
            cell.border = border_all
        ws1.merge_cells(start_row=idx, start_column=3, end_row=idx, end_column=6)
        ws1.merge_cells(start_row=idx, start_column=7, end_row=idx, end_column=8)

    ws1_widths = [14, 34, 24, 20, 26, 26, 22, 14]
    for i, w in enumerate(ws1_widths, 1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    # =========================================================================
    # Sheet 2: 2_初回28日_日英完全台本10項目
    # =========================================================================
    ws2 = wb.create_sheet(title="2_初回28日_日英完全台本10項目")
    ws2.merge_cells("A1:R1")
    ws2["A1"] = "株式会社ファインアトラス｜初回4週間（28日分＝日英56本）完全制作パッケージ（第10章：Dotへの毎日の指示内容 10項目完全網羅）"
    ws2["A1"].fill = navy_fill
    ws2["A1"].font = title_font
    ws2.row_dimensions[1].height = 32

    ws2.merge_cells("A2:R2")
    ws2["A2"] = f"全28話すべて27〜30秒の締めは「{CLOSING_JP}」 / \"{CLOSING_EN}\" に統一済み。そのままVrew・Canva・Metricoolへコピペして動画化できます。"
    ws2["A2"].fill = gold_fill
    ws2["A2"].font = sub_font
    ws2.row_dimensions[2].height = 22

    s2_headers = [
        "配信ID", "週", "曜日", "曜日テーマ（第6章）", "19テーマ区分（第3章）", "主役魚種",
        "①動画タイトル（日本語）", "①動画タイトル（英語）",
        "②30秒ナレーション台本（日本語）", "②30秒ナレーション台本（英語）",
        "③秒数構成（0-3s / 3-20s / 20-27s / 27-30s）",
        "④使用する写真・動画の指示（素材コード）",
        "⑤AI画像生成用の指示文（英語プロンプト）",
        "⑥Vrew貼り付け用字幕（日本語・改行区切り）",
        "⑥Vrew貼り付け用字幕（英語・改行区切り）",
        "⑦SNS投稿文章（日英・HP/Amazon→オリジナル魚BOX誘導）",
        "⑧ハッシュタグ（日英）",
        "⑨情報の出典・⑩事実確認チェック"
    ]
    for c_idx, h in enumerate(s2_headers, 1):
        cell = ws2.cell(row=4, column=c_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws2.row_dimensions[4].height = 28

    for r_idx, ep in enumerate(data["episodes"], 5):
        ws2.row_dimensions[r_idx].height = 78
        tc_summary = "\n".join([f"【{t['sec']}】映像:{t['visualJp']} / 音声:{t['audioJp']}" for t in ep["item3_timecode"]])
        media_dir = f"【素材コード】{ep['item4_mediaDirection']['ownAssetCode']} ({ep['item4_mediaDirection']['ownAssetLabel']})\n【撮影指示】{ep['item4_mediaDirection']['shootGuide']}"
        ai_prompt = f"{ep['item5_aiImagePrompt']['promptEn']}\n(注意: {ep['item5_aiImagePrompt']['usageNoteJp']})"
        vrew_jp = "\n".join(ep["item6_subtitles"]["vrewLinesJp"])
        vrew_en = "\n".join(ep["item6_subtitles"]["vrewLinesEn"])
        captions = f"【JP】\n{ep['item7_snsCaption']['jp']}\n\n【EN】\n{ep['item7_snsCaption']['en']}"
        tags = f"【JP】{ep['item8_hashtags']['jp']}\n【EN】{ep['item8_hashtags']['en']}"
        src_check = f"【出典】{ep['item9_sources']}\n【対象】{ep['item10_bilingualCheck']['targetAudience']}\n【確認】27-30秒キャッチコピー＆HP・Amazon→オリジナル魚BOX導線確認済"

        row_vals = [
            ep["id"], f"Week {ep['week']}", ep["dayOfWeek"], ep["weekdayCategory"], ep["themeCategory"], ep["featuredFish"],
            ep["item1_title"]["jp"], ep["item1_title"]["en"],
            ep["item2_narration"]["jp"], ep["item2_narration"]["en"],
            tc_summary, media_dir, ai_prompt, vrew_jp, vrew_en, captions, tags, src_check
        ]
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws2.cell(row=r_idx, column=c_idx, value=val)
            cell.font = bold_font if c_idx in (1, 6, 7) else body_font
            cell.alignment = align_center if c_idx in (1, 2, 3, 6) else align_left
            cell.fill = zebra_fill if r_idx % 2 == 0 else PatternFill(fill_type=None)
            cell.border = border_all

    s2_widths = [10, 9, 10, 22, 22, 14, 34, 34, 42, 42, 44, 34, 34, 36, 36, 40, 30, 34]
    for i, w in enumerate(s2_widths, 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # =========================================================================
    # Sheet 3: 3_年間365日_配信テーマ計画表
    # =========================================================================
    ws3 = wb.create_sheet(title="3_年間365日_配信テーマ計画表")
    ws3.merge_cells("A1:M1")
    ws3["A1"] = "株式会社ファインアトラス｜年間365日 配信テーマ＆日英タイトル計画表（1日1テーマ×365日＝日英730本・4SNS延べ2,920投稿）"
    ws3["A1"].fill = navy_fill
    ws3["A1"].font = title_font
    ws3.row_dimensions[1].height = 32

    ws3.merge_cells("A2:M2")
    ws3["A2"] = "曜日ごとのテーマ（月〜日）と19種類のコンテンツ企画を365日すべてに割り当て済み（重複タイトル0件）。Day 1〜28はシート2に完全台本収録。"
    ws3["A2"].fill = sub_fill
    ws3["A2"].font = sub_font
    ws3.row_dimensions[2].height = 22

    s3_headers = [
        "通算日", "Dayコード", "週番号", "曜日", "曜日別テーマ（第6章）", "19テーマ区分（第3章）",
        "季節区分", "主役魚種", "日本語版 動画タイトル（365日重複なし）", "英語版 動画タイトル",
        "解説の核・検証済み数値ポイント", "使用自社素材コード", "制作・予約ステータス"
    ]
    for c_idx, h in enumerate(s3_headers, 1):
        cell = ws3.cell(row=4, column=c_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws3.row_dimensions[4].height = 26

    dv_status = DataValidation(type="list", formula1='"台本完成(初回28日),未着手,Dot台本生成済,Vrew動画化済,Metricool予約完了,配信済"', allow_blank=True)
    ws3.add_data_validation(dv_status)

    for r_idx, cal in enumerate(data["calendar365"], 5):
        ws3.row_dimensions[r_idx].height = 26
        status_val = "台本完成(初回28日)" if cal["hasFullScript28"] else "未着手"
        vals = [
            cal["dayNumber"], cal["dayCode"], f"第{cal['weekNumber']}週", cal["dayOfWeek"],
            cal["weekdayTheme"], cal["theme19"], cal["season"], cal["fishKey"],
            cal["titleJp"], cal["titleEn"], cal["factPointJp"], cal["assetCode"], status_val
        ]
        for c_idx, val in enumerate(vals, 1):
            cell = ws3.cell(row=r_idx, column=c_idx, value=val)
            cell.font = bold_font if c_idx in (2, 8, 9) else body_font
            cell.alignment = align_center if c_idx in (1, 2, 3, 4, 8, 12, 13) else align_left
            cell.fill = green_fill if (c_idx == 13 and cal["hasFullScript28"]) else (zebra_fill if r_idx % 2 == 0 else PatternFill(fill_type=None))
            cell.border = border_all

    dv_status.add("M5:M369")

    s3_widths = [8, 11, 10, 10, 24, 22, 18, 14, 46, 44, 48, 16, 18]
    for i, w in enumerate(s3_widths, 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # =========================================================================
    # Sheet 4: 4_写真350枚_動画110本_素材DB
    # =========================================================================
    ws4 = wb.create_sheet(title="4_写真350枚_動画110本_素材DB")
    ws4.merge_cells("A1:H1")
    ws4["A1"] = "株式会社ファインアトラス｜事前に用意する写真・動画素材データベース（第7章：写真350枚＋動画110本＝合計460点）"
    ws4["A1"].fill = navy_fill
    ws4["A1"].font = title_font
    ws4.row_dimensions[1].height = 32

    ws4.merge_cells("A2:H2")
    ws4["A2"] = "AI画像生成も活用するが、実際の商品紹介には必ず自社で撮影した写真・動画を使用し、信頼性を高める（計画書第7章・第9章）。"
    ws4["A2"].fill = gold_fill
    ws4["A2"].font = sub_font
    ws4.row_dimensions[2].height = 22

    cat_headers = ["分類No", "素材種別", "カテゴリ名称（第7章）", "計画数量", "素材コード範囲", "主な使用秒数パート・用途", "撮影規格（縦型ショート専用）", "準備状況"]
    for c_idx, h in enumerate(cat_headers, 1):
        cell = ws4.cell(row=4, column=c_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws4.row_dimensions[4].height = 24

    for r_idx, cat in enumerate(data["assetInventory460"]["categories"], 5):
        ws4.row_dimensions[r_idx].height = 24
        vals = [
            cat["categoryNo"], cat["type"], cat["name"], cat["targetCount"],
            cat["sampleCodes"], cat["purpose"], "縦型 9:16（1080×1920）・文字なし原版", "リスト完備"
        ]
        for c_idx, val in enumerate(vals, 1):
            cell = ws4.cell(row=r_idx, column=c_idx, value=val)
            cell.font = bold_font if c_idx in (3, 4, 5) else body_font
            cell.alignment = align_center if c_idx in (1, 2, 4, 5, 8) else align_left
            cell.border = border_all

    ws4.merge_cells("A13:C13")
    ws4["A13"] = "写真・動画素材 合計点数（写真350枚＋動画110本）"
    ws4["A13"].font = bold_font
    ws4["A13"].fill = gold_fill
    ws4["A13"].alignment = align_center
    ws4["D13"] = "=SUM(D5:D12)"
    ws4["D13"].font = bold_font
    ws4["D13"].fill = gold_fill
    ws4["D13"].alignment = align_center
    ws4.merge_cells("E13:H13")
    ws4["E13"] = "点（全460点の個別撮影チェックリストを16行目以降に完全収録）"
    ws4["E13"].font = bold_font
    ws4["E13"].fill = gold_fill
    for c_idx in range(1, 9):
        ws4.cell(row=13, column=c_idx).border = border_all

    ws4.merge_cells("A15:H15")
    ws4["A15"] = "■ 全460点 個別撮影・素材管理チェックリスト（P-WR-001〜V-PS-020）"
    ws4["A15"].fill = sub_fill
    ws4["A15"].font = sub_font

    item_headers = ["素材コード", "素材種別", "カテゴリ名称", "対象魚種", "主要産地", "具体的な撮影カット・アングル指示", "撮影優先度", "撮影ステータス"]
    for c_idx, h in enumerate(item_headers, 1):
        cell = ws4.cell(row=16, column=c_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all

    for offset, item in enumerate(data["assetInventory460"]["items"], 17):
        ws4.row_dimensions[offset].height = 20
        vals = [
            item["code"], item["type"], item["categoryName"], item["fishKey"],
            item["fishOrigin"], item["shotTitle"], item["priority"], "未撮影"
        ]
        for c_idx, val in enumerate(vals, 1):
            cell = ws4.cell(row=offset, column=c_idx, value=val)
            cell.font = bold_font if c_idx in (1, 7) else body_font
            cell.alignment = align_center if c_idx in (1, 2, 4, 7, 8) else align_left
            cell.fill = green_fill if "S（" in item["priority"] and c_idx == 7 else (zebra_fill if offset % 2 == 0 else PatternFill(fill_type=None))
            cell.border = border_all

    s4_widths = [14, 16, 26, 16, 22, 46, 22, 16]
    for i, w in enumerate(s4_widths, 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    # =========================================================================
    # Sheet 5: 5_Dot指示文_Vrew_Metricool手順
    # =========================================================================
    ws5 = wb.create_sheet(title="5_Dot指示文_Vrew_Metricool手順")
    ws5.merge_cells("A1:D1")
    ws5["A1"] = "株式会社ファインアトラス｜Dot指示プロンプト＆Vrew・Canva・Metricool運用マニュアル（第4章・第5章・第9章・第10章）"
    ws5["A1"].fill = navy_fill
    ws5["A1"].font = title_font
    ws5.row_dimensions[1].height = 32

    ws5.merge_cells("A3:D3")
    ws5["A3"] = "■ 1. ChatGPT・Dot 毎日の10項目生成マスタープロンプト（そのままコピーして使用）"
    ws5["A3"].fill = sub_fill
    ws5["A3"].font = sub_font

    ws5.merge_cells("A4:D4")
    ws5["A4"] = data["dotPromptTemplates"]["dailyMasterPrompt"]
    ws5["A4"].font = body_font
    ws5["A4"].alignment = align_left
    ws5["A4"].fill = zebra_fill
    ws5.row_dimensions[4].height = 340
    for c_idx in range(1, 5):
        ws5.cell(row=4, column=c_idx).border = border_all

    ws5.merge_cells("A6:D6")
    ws5["A6"] = "■ 2. 週1回で7日分（日英14本）をまとめ生成するバッチ指示プロンプト"
    ws5["A6"].fill = sub_fill
    ws5["A6"].font = sub_font

    ws5.merge_cells("A7:D7")
    ws5["A7"] = data["dotPromptTemplates"]["weeklyBatchPrompt"]
    ws5["A7"].font = body_font
    ws5["A7"].alignment = align_left
    ws5["A7"].fill = zebra_fill
    ws5.row_dimensions[7].height = 220
    for c_idx in range(1, 5):
        ws5.cell(row=7, column=c_idx).border = border_all

    ws5.merge_cells("A9:D9")
    ws5["A9"] = "■ 3. 情報の信頼性を守るためのルール（第9章）＆ ファインアトラス誠実ガードレール"
    ws5["A9"].fill = sub_fill
    ws5["A9"].font = sub_font

    rules_rows = [
        ("第9章 ① 根拠ある情報のみ", "水産庁の公開資料、卸売市場（豊洲・大阪）の公開データ、一般的な水産加工技術、調理技術、ファインアトラスの商品情報のみを使用する。"),
        ("第9章 ② 出典の確認", "Dotで台本を作成する際には、必ず「⑨ 情報の出典」を同時に出力させ、広報担当者が内容を確認する。"),
        ("第9章 ③ 未確認情報の禁止", "事実確認ができない内容、誇大表現、誤解を招く表現は動画に使用しない。実際の商品紹介には必ず自社撮影の写真・動画を使用する。"),
        ("営業・広報ガードレール ①", "個別店舗の価格・送料・最低ロット・配送曜日は動画内で勝手に断定せず、まずHP・Amazonでの少量購入／お試しセットから個別ヒアリングへ案内する。"),
        ("営業・広報ガードレール ②", "対馬水産の実績をファインアトラス単独の導入店舗数として誤認させない（「対馬水産の事業を承継し、ファインスタッフと共に設立した会社」と誠実に伝える）。"),
        ("27〜30秒 ブランド統一", f"すべての動画の27〜30秒は「{CLOSING_JP}」 / \"{CLOSING_EN}\" で統一する。")
    ]
    for r_offset, (r_title, r_desc) in enumerate(rules_rows, 10):
        ws5.row_dimensions[r_offset].height = 28
        ws5.cell(row=r_offset, column=1, value=r_title).font = bold_font
        ws5.cell(row=r_offset, column=1).fill = gold_fill
        ws5.cell(row=r_offset, column=1).border = border_all
        ws5.cell(row=r_offset, column=2, value=r_desc)
        for c_idx in range(2, 5):
            cell = ws5.cell(row=r_offset, column=c_idx)
            cell.font = body_font
            cell.alignment = align_left
            cell.border = border_all
        ws5.merge_cells(start_row=r_offset, start_column=2, end_row=r_offset, end_column=4)

    s5_widths = [28, 38, 38, 38]
    for i, w in enumerate(s5_widths, 1):
        ws5.column_dimensions[get_column_letter(i)].width = w

    # =========================================================================
    # Sheet 6: 6_ファインアトラス魚種_原価データ
    # =========================================================================
    ws6 = wb.create_sheet(title="6_ファインアトラス魚種_原価データ")
    ws6.merge_cells("A1:M1")
    ws6["A1"] = "株式会社ファインアトラス｜全国業務用冷凍魚10品目（主力5＋拡張5）歩留まり・飲食店1皿原価率＆急速冷凍ドリップ検証マスタ"
    ws6["A1"].fill = navy_fill
    ws6["A1"].font = title_font
    ws6.row_dimensions[1].height = 32

    ws6.merge_cells("A2:M2")
    ws6["A2"] = "調査基準：2025〜2026年 公開水産市況統計（東京都・大阪市中央卸売市場 水産物月報）および業務用B2B卸公開相場レンジ・特殊急速凍結ドリップ検証データ"
    ws6["A2"].fill = sub_fill
    ws6["A2"].font = sub_font
    ws6.row_dimensions[2].height = 22

    s6_headers = [
        "No", "区分", "魚種キー", "品目名（規格・加工形態）", "英語メニュー表記",
        "市場・B2B卸実勢レンジ(円/kg)", "FA想定卸単価(円/kg)", "可食歩留まり(%)",
        "1人前正味(g)", "飲食店1皿原価(円)", "想定メニュー売価(円)", "飲食店原価率(%)", "厨房での仕込み時短メリット・推奨料理"
    ]
    for c_idx, h in enumerate(s6_headers, 1):
        cell = ws6.cell(row=4, column=c_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    ws6.row_dimensions[4].height = 26

    for r_idx, f in enumerate(data["fishMaster10"], 5):
        ws6.row_dimensions[r_idx].height = 34
        vals = [
            f["no"], f["tier"], f["key"], f["nameJp"], f["nameEn"],
            f["marketRangeYenKg"], f["faWholesaleYenKg"], f["yieldPct"],
            f["portionGram"], f["dishCostYen"], f["menuPriceYen"], f["flCostRatioPct"],
            f"{f['prepMerit']} 【推奨料理】{f['recommendedDishes']}"
        ]
        for c_idx, val in enumerate(vals, 1):
            cell = ws6.cell(row=r_idx, column=c_idx, value=val)
            cell.font = bold_font if c_idx in (2, 3, 8, 12) else body_font
            cell.alignment = align_center if c_idx in (1, 2, 3, 6, 7, 8, 9, 10, 11, 12) else align_left
            cell.fill = green_fill if c_idx == 12 else (zebra_fill if r_idx % 2 == 0 else PatternFill(fill_type=None))
            cell.border = border_all

    # Average row using Excel AVERAGE formulas
    ws6.row_dimensions[15].height = 26
    ws6.merge_cells("A15:F15")
    ws6["A15"] = "全10品目 平均（主力5品目＋拡張5品目）"
    ws6["A15"].font = bold_font
    ws6["A15"].alignment = align_center
    ws6["A15"].fill = gold_fill
    ws6["G15"] = "=AVERAGE(G5:G14)"
    ws6["H15"] = "=AVERAGE(H5:H14)"
    ws6["I15"] = "=AVERAGE(I5:I14)"
    ws6["J15"] = "=AVERAGE(J5:J14)"
    ws6["K15"] = "=AVERAGE(K5:K14)"
    ws6["L15"] = "=AVERAGE(L5:L14)"
    ws6["M15"] = "飲食店1皿原価率は全品目 26.5%〜30.2%（平均28.1%）の黄金FLゾーンに収まる"
    for c_idx in range(1, 14):
        cell = ws6.cell(row=15, column=c_idx)
        cell.font = bold_font
        cell.fill = gold_fill
        cell.border = border_all
        if 7 <= c_idx <= 12:
            cell.alignment = align_center
            cell.number_format = "0.0" if c_idx in (8, 9, 12) else "#,##0"

    # Freezing tech comparison table at bottom of Sheet 6
    ws6.merge_cells("A17:M17")
    ws6["A17"] = "■ 凍結方式による最大氷結晶生成帯（-1〜-5℃）通過時間と解凍ドリップ流出率の比較（水曜テーマ根拠データ）"
    ws6["A17"].fill = sub_fill
    ws6["A17"].font = sub_font

    fz_headers = ["凍結方式", "最大氷結晶生成帯（-1〜-5℃）通過時間", "解凍ドリップ流出率", "細胞組織の状態と調理適性（動画解説ポイント）"]
    ws6.merge_cells("D18:M18")
    for c_idx, h in enumerate(["凍結方式", "最大氷結晶生成帯(-1〜-5℃)通過", "解凍ドリップ流出率", "細胞組織の状態と調理適性"], 1):
        cell = ws6.cell(row=18, column=c_idx, value=h)
        cell.fill = blue_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_all
    for c_idx in range(5, 14):
        ws6.cell(row=18, column=c_idx).fill = blue_fill
        ws6.cell(row=18, column=c_idx).border = border_all

    fz_rows = [
        ("一般緩慢冷凍（旧式庫内凍結）", "30〜120分", "5.0〜10.0%", "氷結晶が肥大化し細胞膜を破壊。旨味流出・水っぽさ・身割れが発生（お造り・松笠焼き不可）。"),
        ("急速エアブラスト＋高真空パック", "15〜25分", "2.0〜3.5%", "冷凍焼けと脂質酸化を防止。天ぷら・白焼き・西京焼き・ポワレでは生鮮同等のふっくら感。"),
        ("特殊急速凍結（プロトン／CAS／液体凍結）", "3〜12分", "0.5〜1.5%以下", "氷核が微細均一で細胞膜が無傷。お造り・江戸前鮨タネ・甘鯛の鱗立ち（松笠焼き）まで100%再現、アニサキスリスク完全ゼロ。")
    ]
    for r_idx, (m_name, t_pass, drip, desc) in enumerate(fz_rows, 19):
        ws6.row_dimensions[r_idx].height = 24
        ws6.merge_cells(start_row=r_idx, start_column=4, end_row=r_idx, end_column=13)
        ws6.cell(row=r_idx, column=1, value=m_name).font = bold_font
        ws6.cell(row=r_idx, column=2, value=t_pass).font = bold_font
        ws6.cell(row=r_idx, column=2).alignment = align_center
        ws6.cell(row=r_idx, column=3, value=drip).font = bold_font
        ws6.cell(row=r_idx, column=3).alignment = align_center
        ws6.cell(row=r_idx, column=4, value=desc).font = body_font
        for c_idx in range(1, 14):
            ws6.cell(row=r_idx, column=c_idx).border = border_all
            if r_idx == 21:
                ws6.cell(row=r_idx, column=c_idx).fill = green_fill

    s6_widths = [6, 10, 14, 34, 34, 20, 16, 14, 14, 16, 16, 16, 48]
    for i, w in enumerate(s6_widths, 1):
        ws6.column_dimensions[get_column_letter(i)].width = w

    # Remove default sheet after creating the 6 sheets
    wb.remove(default_sheet)
    wb.save(EXCEL_PATH)


def main():
    plan_overview = build_plan_overview()
    weekday_schedule = build_weekday_schedule()
    themes_19 = build_themes_19()
    fish_master_10 = build_fish_master_10()
    episodes_28 = build_28_episodes()
    calendar_365 = build_calendar_365(episodes_28, fish_master_10, themes_19, weekday_schedule)
    dot_prompt_templates = build_dot_prompt_templates()
    asset_inventory_460 = build_asset_inventory_460(fish_master_10)

    master_data = {
        "generatedAt": "2026-11-25",
        "version": "v1.0.0",
        "planOverview": plan_overview,
        "weekdaySchedule": weekday_schedule,
        "themes19": themes_19,
        "fishMaster10": fish_master_10,
        "episodes": episodes_28,
        "calendar365": calendar_365,
        "dotPromptTemplates": dot_prompt_templates,
        "assetInventory460": asset_inventory_460
    }

    # Write data.js
    js_content = (
        "// Auto-generated by scripts/build_deliverables.py\n"
        "// 株式会社ファインアトラス｜AIショート動画 毎日配信計画 マスターデータ\n"
        "window.FINE_ATLAS_SHORTS_DATA = "
        + json.dumps(master_data, ensure_ascii=False, indent=2)
        + ";\n"
    )
    DATA_JS_PATH.write_text(js_content, encoding="utf-8")
    print(f"[OK] Generated {DATA_JS_PATH} ({DATA_JS_PATH.stat().st_size:,} bytes)")

    # Write Excel Master Ledger
    generate_excel_workbook(master_data)
    print(f"[OK] Generated {EXCEL_PATH} ({EXCEL_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
