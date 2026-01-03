# AI主導型 卓球パフォーマンス最大化システム

**Table Tennis Performance Maximization System**

**バージョン**: 2.0  
**最終更新日**: 2026年1月4日

---

## 概要

本システムは、文化学園大学杉並の浅見江里佳選手の卓球成績を最大化することを目的としたAI主導型の分析システムです。

動画を入力として、AIが自動的に以下を生成します：

1. **深い分析レポート** - 技術、戦術、フットワークの多角的評価
2. **試合戦略シート** - 対戦相手に対する具体的な戦い方
3. **練習計画書** - 課題克服のための練習メニュー

---

## システム構成

| フェーズ | 機能 | 技術 | 状態 |
|:---|:---|:---|:---:|
| Phase 1 | 定性分析（LLM） | Gemini API | ✅完了 |
| Phase 2 | 定量分析（CV） | OpenCV, MediaPipe | 🔄開発中 |
| Phase 3 | 可視化・永続化 | SQLite, Flask | ❌未着手 |

---

## アーキテクチャ

```
┌─────────────┐    ┌─────────────────────────────┐    ┌─────────────┐
│   入力層    │───▶│      分析エンジン層          │───▶│  出力生成層  │
│             │    │  ┌─────────┐ ┌─────────┐   │    │             │
│ ・動画      │    │  │CVAnalyzer│ │LLMAnalyzer│  │    │ ・レポート  │
│ ・メタデータ │    │  │(定量分析)│ │(定性分析) │  │    │ ・戦略シート│
│             │    │  └─────────┘ └─────────┘   │    │ ・練習計画  │
└─────────────┘    └─────────────────────────────┘    └─────────────┘
```

---

## クイックスタート

### 前提条件

- Python 3.11+
- Gemini API キー（環境変数 `OPENAI_API_KEY` に設定済み）

### インストール

```bash
git clone https://github.com/JunichiroAsami/tt-performance-system.git
cd tt-performance-system
pip install -r requirements.txt
```

### 実行

```bash
# 動画の全機能分析
python src/main.py full --video data/videos/match.mp4 -v

# 分析のみ
python src/main.py analyze --video data/videos/match.mp4

# 戦略生成のみ
python src/main.py strategy --video data/videos/match.mp4

# 練習計画生成のみ
python src/main.py practice --video data/videos/match.mp4
```

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
| **品質管理** | テスト仕様書 | `docs/test_scenarios.md` |
| | UAT計画書 | `docs/uat_plan.md` |

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
│   └── ...
├── src/                     # ソースコード
│   ├── main.py
│   ├── analysis/
│   │   ├── llm_analyzer.py
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
```

---

## 業務要件との対応

本システムは、業務要件書 (REQ-01) で定義された以下の要件を満たします：

| 要件ID | 要件名 | 実装状態 |
|:---|:---|:---:|
| FA-01〜03 | 自己分析（定性） | ✅Phase 1 |
| FA-04〜05 | 自己分析（定量） | 🔄Phase 2 |
| FA-06〜08 | 相手分析 | ✅Phase 1 |
| FS-01〜04 | 戦略生成 | ✅Phase 1 |
| FP-01〜02 | 練習計画生成 | ✅Phase 1 |
| FP-03 | フォーム改善ドリル | 🔄Phase 2 |
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
| 2026-01-04 | 2.0 | ドキュメント体系の全面改訂に伴う更新 |
| 2026-01-04 | 1.0 | 初版作成 |
