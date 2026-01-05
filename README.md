# AI主導型 卓球パフォーマンス最大化システム

**Table Tennis Performance Maximization System**

**バージョン**: 2.2  
**最終更新日**: 2026年1月5日

---

## 概要

本システムは、文化学園大学杉並の浅見江里佳選手の卓球成績を最大化することを目的としたAI主導型の分析システムです。

動画を入力として、AIが自動的に以下を生成します：

1. **深い分析レポート** - 技術、戦術、フットワークの多角的評価
2. **相手選手の分析** - 対戦相手の強み・弱点・対策
3. **定量分析** - 姿勢推定、フットワーク分析（v2.2で追加）
4. **試合戦略シート** - 対戦相手に対する具体的な戦い方
5. **練習計画書** - 課題克服のための練習メニュー
6. **フォーム改善ドリル** - 定量分析に基づく具体的な練習ドリル（v2.2で追加）

---

## システム構成

| フェーズ | 機能 | 技術 | 状態 |
|:---|:---|:---|:---:|
| Phase 1 | 定性分析（LLM） | Gemini 2.5 Flash | ✅完了 |
| Phase 1.1 | 相手選手分析 | Gemini 2.5 Flash | ✅完了 |
| Phase 2 | 定量分析（CV） | OpenCV, MediaPipe | ✅完了 |
| Phase 2.1 | 統合分析 | CV + LLM | ✅完了 |
| Phase 3 | 可視化・永続化 | SQLite, Flask | ❌未着手 |

---

## アーキテクチャ

```
┌─────────────┐    ┌─────────────────────────────────────┐    ┌─────────────┐
│   入力層    │───▶│         分析エンジン層               │───▶│  出力生成層  │
│             │    │  ┌───────────┐ ┌───────────────┐   │    │             │
│ ・動画      │    │  │CVAnalyzer │ │ LLMAnalyzer   │   │    │ ・レポート  │
│ ・メタデータ │    │  │(姿勢推定) │ │ (定性分析)    │   │    │ ・戦略シート│
│             │    │  └─────┬─────┘ └───────┬───────┘   │    │ ・練習計画  │
│             │    │        │               │           │    │ ・ドリル    │
│             │    │        └───────┬───────┘           │    │             │
│             │    │        ┌───────▼───────┐           │    │             │
│             │    │        │IntegrationEngine│          │    │             │
│             │    │        │  (統合分析)    │           │    │             │
│             │    │        └───────────────┘           │    │             │
└─────────────┘    └─────────────────────────────────────┘    └─────────────┘
```

---

## クイックスタート

### 前提条件

- Python 3.11+
- OpenAI互換API キー（環境変数 `OPENAI_API_KEY` に設定済み）
- MediaPipe（姿勢推定用）

### インストール

```bash
git clone https://github.com/JunichiroAsami/tt-performance-system.git
cd tt-performance-system
pip install -r requirements.txt
```

### 実行

```bash
# 動画の全機能分析（自己分析 + 相手分析 + 戦略 + 練習計画）
python src/main.py full --video data/videos/match.mp4 -v

# 自己分析のみ
python src/main.py analyze --video data/videos/match.mp4

# 相手選手の分析
python src/main.py opponent --video data/videos/match.mp4

# 定量分析（姿勢推定 + フットワーク）（v2.2 NEW）
python src/analysis/cv_analyzer.py data/videos/match.mp4

# 統合分析（定量 + 定性）（v2.2 NEW）
python src/analysis/integration_engine.py data/results/v2/cv_analysis.json

# 戦略生成のみ
python src/main.py strategy --video data/videos/match.mp4

# 練習計画生成のみ
python src/main.py practice --video data/videos/match.mp4
```

---

## Phase 2 定量分析の詳細

### CVAnalyzer（姿勢推定）

MediaPipeを使用して、動画から選手の姿勢を推定します。

**出力データ:**
- 関節角度（肘、膝、体幹）の統計
- スイング検出（回数、タイミング）
- フットワーク（移動距離、速度、左右/前後比率）

### IntegrationEngine（統合分析）

CVAnalyzerの数値データとLLMの定性分析を組み合わせて、より詳細な分析を行います。

**出力データ:**
- フォーム分析（フォアハンド、バックハンド、全体姿勢）
- フットワーク分析（効率性、改善点）
- フォーム改善ドリル（具体的な練習メニュー）

---

## ドキュメント

| カテゴリ | ドキュメント | パス |
|:---|:---|:---|
| **プロジェクト管理** | プロジェクト計画書 | `docs/project_plan.md` |
| | WBS | `docs/WBS.md` |
| | 進捗管理表 | `docs/progress_tracker.md` |
| | 課題管理表 | `docs/issue_tracker.md` |
| **要件・設計** | 業務要件書 | `docs/business_requirements.md` |
| | 概要設計書 | `docs/system_architecture.md` |
| | 詳細設計書 | `docs/development_spec.md` |
| | Webアプリ仕様書 | `docs/webapp_spec.md` |
| **品質管理** | テスト仕様書 | `docs/test_scenarios.md` |
| | UAT計画書 | `docs/uat_plan.md` |
| | アウトプットレビュー | `docs/v2_output_review.md` |

全ドキュメントの一覧は `docs/document_list.md` を参照してください。

---

## ディレクトリ構成

```
tt-performance-system/
├── README.md
├── requirements.txt
├── config/
│   └── settings.yaml
├── docs/                    # ドキュメント
│   ├── project_plan.md
│   ├── WBS.md
│   ├── business_requirements.md
│   ├── system_architecture.md
│   ├── development_spec.md
│   ├── webapp_spec.md       # Webアプリ仕様書
│   └── mockup/              # UIモックアップ
├── src/                     # ソースコード
│   ├── main.py
│   ├── analysis/
│   │   ├── llm_analyzer.py
│   │   ├── cv_analyzer.py   # 姿勢推定（v2.2）
│   │   ├── ball_tracker.py  # ボールトラッキング（v2.2）
│   │   ├── integration_engine.py  # 統合分析（v2.2）
│   │   └── prompts.py
│   └── output/
│       └── report_generator.py
├── tests/                   # テストコード
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── data/                    # データ
    ├── videos/
    └── results/
        └── v2/
            ├── analysis.json
            ├── opponent_analysis.json
            ├── cv_analysis.json        # 姿勢推定結果（v2.2）
            ├── integrated_analysis.json # 統合分析結果（v2.2）
            ├── strategy.json
            ├── strategy_summary.md
            └── practice_plan.json
```

---

## 業務要件との対応

本システムは、業務要件書 (REQ-01) で定義された以下の要件を満たします：

| 要件ID | 要件名 | 実装状態 |
|:---|:---|:---:|
| FA-01〜03 | 自己分析（定性） | ✅Phase 1 |
| FA-04 | フォーム分析（定量） | ✅Phase 2 |
| FA-05 | フットワーク分析（定量） | ✅Phase 2 |
| FA-06〜08 | 相手分析 | ✅Phase 1 |
| FS-01〜04 | 戦略生成 | ✅Phase 1 |
| FP-01〜02 | 練習計画生成 | ✅Phase 1 |
| FP-03 | フォーム改善ドリル | ✅Phase 2 |
| FR-01〜03 | レポート・可視化 | ❌Phase 3 |

---

## ライセンス

Private - 文化学園大学杉並 卓球部専用

---

## 作成者

- **Manus AI** - PM / システム設計・開発
- **浅見淳一郎** - プロジェクトオーナー

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|:---|:---|:---|
| 2026-01-05 | 2.2 | Phase 2完了: 姿勢推定、フットワーク分析、統合分析、フォーム改善ドリル |
| 2026-01-05 | 2.1 | 相手選手の分析機能を追加 |
| 2026-01-04 | 2.0 | V2システム（動画直接送信方式）へ移行 |
| 2026-01-04 | 1.0 | 初版作成 |
