# AI主導型 卓球パフォーマンス最大化システム

**Table Tennis Performance Maximization System**

卓球の試合・練習動画を入力として、AIが自動的に「深い分析」「試合戦略」「練習計画」を生成するシステムです。

## 概要

本システムは、文化学園大学杉並の浅見江里佳選手の卓球成績を最大化することを目的として開発されました。動画分析からコーチングまでをAIが主導し、選手が試合で最大限勝てるよう支援します。

## 主な機能

### 1. 深い分析（Analysis）
- 技術評価（フォアハンド、バックハンド、サーブ、レシーブ）
- 得点/失点パターンの分類
- フォーム・フットワークの評価
- 強み/弱みの特定

### 2. 試合戦略（Strategy）
- サーブ戦略（種類×コース×場面）
- レシーブ戦略（相手サーブ別対応）
- ラリー展開戦略
- 相手の弱点を突く作戦

### 3. 練習計画（Practice）
- 優先課題の特定
- 課題別練習メニュー
- フォーム改善ドリル
- 週間練習スケジュール

## システムアーキテクチャ

```
┌─────────────┐    ┌─────────────────────────────┐    ┌─────────────┐
│   入力層    │───▶│      分析エンジン層          │───▶│  出力生成層  │
│             │    │  ┌─────────┐ ┌─────────┐   │    │             │
│ ・動画      │    │  │CVAnalyzer│ │LLMAnalyzer│  │    │ ・レポート  │
│ ・メタデータ │    │  │(定量分析)│ │(定性分析) │  │    │ ・戦略シート│
│             │    │  └─────────┘ └─────────┘   │    │ ・練習計画  │
└─────────────┘    └─────────────────────────────┘    └─────────────┘
```

## 技術スタック

| 技術 | 用途 |
|:---|:---|
| Python 3.11+ | メイン言語 |
| OpenCV | ボール軌道追跡、コース分析 |
| MediaPipe | 姿勢推定、フットワーク分析 |
| Gemini API | 戦術評価、戦略・練習提案生成 |
| SQLite | データ蓄積 |

## ディレクトリ構成

```
tt-performance-system/
├── README.md                 # 本ファイル
├── docs/                     # ドキュメント
│   ├── business_requirements.md    # 業務要件書
│   ├── system_architecture.md      # 概要設計書
│   └── development_spec.md         # 開発仕様書
├── src/                      # ソースコード
│   ├── analysis/             # 分析モジュール
│   │   ├── llm_analyzer.py   # Gemini API分析
│   │   ├── cv_analyzer.py    # OpenCV分析
│   │   └── integration.py    # 統合分析
│   └── output/               # 出力生成モジュール
│       ├── report_generator.py
│       ├── strategy_generator.py
│       └── practice_generator.py
├── data/                     # データ
│   ├── videos/               # 動画ファイル（Git管理外）
│   └── results/              # 分析結果
├── config/                   # 設定ファイル
│   └── settings.yaml
├── tests/                    # テストコード
└── requirements.txt          # 依存パッケージ
```

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/JunichiroAsami/tt-performance-system.git
cd tt-performance-system
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
export OPENAI_API_KEY="your-api-key"  # Gemini API用
```

## 使用方法

### 基本的な分析

```bash
python src/main.py analyze --video data/videos/match.mp4
```

### 戦略シート生成

```bash
python src/main.py strategy --video data/videos/match.mp4 --opponent "対戦相手名"
```

### 練習計画生成

```bash
python src/main.py practice --player "浅見江里佳" --focus "バックハンド"
```

## 開発状況

- [x] Phase 1: Gemini APIによる定性分析
- [ ] Phase 2: OpenCV/MediaPipeによる定量分析
- [ ] Phase 3: 統合分析と戦略・練習計画生成
- [ ] Phase 4: Web UI

## ライセンス

Private - 文化学園大学杉並 卓球部専用

## 作成者

- **Manus AI** - システム設計・開発
- **浅見淳一郎** - プロジェクトオーナー

## 更新履歴

| 日付 | バージョン | 内容 |
|:---|:---|:---|
| 2026-01-03 | 0.1.0 | 初期バージョン、Gemini API分析モジュール |
