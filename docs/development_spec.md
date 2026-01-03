# 開発仕様書：AI主導型 卓球パフォーマンス最大化システム

**バージョン**: 1.0  
**作成日**: 2026年1月3日  
**作成者**: Manus AI

---

## 1. 開発概要

### 1.1. 目的

本ドキュメントは、AI主導型卓球パフォーマンス最大化システムの開発仕様を定義する。

### 1.2. 開発フェーズ

| フェーズ | 内容 | 優先度 | 状態 |
|:---|:---|:---|:---|
| Phase 1 | Gemini APIによる定性分析 | 高 | 開発中 |
| Phase 2 | OpenCV/MediaPipeによる定量分析 | 中 | 未着手 |
| Phase 3 | 統合分析と出力生成 | 中 | 未着手 |
| Phase 4 | Web UI | 低 | 未着手 |

---

## 2. Phase 1: Gemini API定性分析モジュール

### 2.1. モジュール構成

```
src/analysis/
├── __init__.py
├── llm_analyzer.py      # メイン分析モジュール
├── prompts.py           # プロンプトテンプレート
└── schemas.py           # 出力スキーマ定義
```

### 2.2. llm_analyzer.py

#### クラス設計

```python
class LLMAnalyzer:
    """Gemini APIを使用した動画の定性分析"""
    
    def __init__(self, api_key: str = None):
        """初期化"""
        
    def analyze_video(self, video_path: str, analysis_type: str) -> dict:
        """動画を分析"""
        
    def analyze_technique(self, video_path: str) -> dict:
        """技術分析"""
        
    def analyze_tactics(self, video_path: str) -> dict:
        """戦術分析"""
        
    def generate_strategy(self, self_analysis: dict, opponent_analysis: dict) -> dict:
        """試合戦略を生成"""
        
    def generate_practice_plan(self, analysis: dict) -> dict:
        """練習計画を生成"""
```

#### メソッド仕様

| メソッド | 入力 | 出力 | 説明 |
|:---|:---|:---|:---|
| `analyze_video` | video_path, analysis_type | dict | 動画の総合分析 |
| `analyze_technique` | video_path | dict | 技術面の詳細分析 |
| `analyze_tactics` | video_path | dict | 戦術面の詳細分析 |
| `generate_strategy` | self_analysis, opponent_analysis | dict | 試合戦略の生成 |
| `generate_practice_plan` | analysis | dict | 練習計画の生成 |

### 2.3. プロンプト設計

#### 技術分析プロンプト

```
あなたは卓球の専門コーチです。以下の動画を分析し、選手の技術を評価してください。

【評価項目】
1. フォアハンドドライブ
   - スイング軌道
   - 打点
   - 体重移動
   - 回転量（推定）

2. バックハンドドライブ
   - スイング軌道
   - 打点
   - 安定性

3. サーブ
   - 種類のバリエーション
   - コースの精度
   - 回転の質

4. レシーブ
   - 対応力
   - 攻撃的レシーブの割合

5. フットワーク
   - 移動速度
   - 戻りの速さ
   - ポジショニング

【出力形式】
JSON形式で出力してください。
```

#### 戦術分析プロンプト

```
あなたは卓球の戦術アナリストです。以下の動画を分析し、選手の戦術傾向を評価してください。

【評価項目】
1. 得点パターン
   - どのような展開で得点しているか
   - 得意な攻撃パターン

2. 失点パターン
   - どのような展開で失点しているか
   - 苦手な状況

3. サーブ戦術
   - サーブの種類と使用頻度
   - 3球目攻撃の成功率

4. レシーブ戦術
   - レシーブの種類と傾向
   - 4球目以降の展開

5. 試合運び
   - 競った場面での傾向
   - メンタル面の強さ

【出力形式】
JSON形式で出力してください。
```

### 2.4. 出力スキーマ

```python
# 技術分析結果
TechniqueAnalysisSchema = {
    "player_info": {
        "name": str,
        "dominant_hand": str,  # "right" or "left"
        "grip": str,           # "shakehand" or "penhold"
        "play_style": str      # "offensive", "defensive", "all-round"
    },
    "techniques": {
        "forehand_drive": {
            "rating": int,     # 1-5
            "strengths": list,
            "weaknesses": list,
            "comments": str
        },
        "backhand_drive": {...},
        "serve": {...},
        "receive": {...},
        "footwork": {...}
    },
    "overall_assessment": str,
    "priority_improvements": list
}

# 戦術分析結果
TacticsAnalysisSchema = {
    "scoring_patterns": list,
    "losing_patterns": list,
    "serve_tactics": {
        "types": list,
        "effectiveness": int
    },
    "receive_tactics": {...},
    "match_management": {
        "under_pressure": str,
        "mental_strength": int
    },
    "recommendations": list
}

# 試合戦略
StrategySchema = {
    "serve_strategy": {
        "first_serve": list,
        "second_serve": list,
        "deuce_serve": list
    },
    "receive_strategy": {
        "against_short": str,
        "against_long": str,
        "against_spin": str
    },
    "rally_strategy": {
        "attack_targets": list,
        "defensive_approach": str
    },
    "key_points": list
}

# 練習計画
PracticePlanSchema = {
    "priority_issues": list,
    "weekly_plan": {
        "day1": list,
        "day2": list,
        ...
    },
    "drills": [
        {
            "name": str,
            "purpose": str,
            "duration": str,
            "method": str
        }
    ],
    "goals": {
        "short_term": list,
        "long_term": list
    }
}
```

---

## 3. Phase 2: OpenCV/MediaPipe定量分析モジュール

### 3.1. モジュール構成

```
src/analysis/
├── cv_analyzer.py       # メインCVモジュール
├── ball_tracker.py      # ボール追跡
├── pose_estimator.py    # 姿勢推定
└── court_mapper.py      # コート座標変換
```

### 3.2. 主要機能

| モジュール | 機能 | 出力 |
|:---|:---|:---|
| ball_tracker | ボール軌道追跡 | 座標列、速度、バウンス位置 |
| pose_estimator | 姿勢推定 | 関節座標、角度 |
| court_mapper | コート座標変換 | 正規化座標 |

### 3.3. 技術仕様

#### ボール追跡

- **アルゴリズム**: 背景差分 + Hough変換 + カルマンフィルタ
- **出力フレームレート**: 30fps
- **検出精度目標**: 90%以上

#### 姿勢推定

- **使用モデル**: MediaPipe Pose
- **キーポイント数**: 33点
- **主要計測角度**: 肘角度、膝角度、体幹角度

---

## 4. 設定ファイル

### 4.1. config/settings.yaml

```yaml
# API設定
api:
  gemini:
    model: "gemini-2.5-flash"
    max_tokens: 4096
    temperature: 0.7

# 動画処理設定
video:
  max_duration: 600  # 秒
  frame_rate: 30
  resolution: [1280, 720]

# 分析設定
analysis:
  technique_weight: 0.4
  tactics_weight: 0.4
  mental_weight: 0.2

# 出力設定
output:
  format: "markdown"
  language: "ja"
```

---

## 5. テスト仕様

### 5.1. 単体テスト

| テスト対象 | テスト内容 | 期待結果 |
|:---|:---|:---|
| LLMAnalyzer.analyze_video | 動画分析実行 | JSON形式の分析結果 |
| LLMAnalyzer.generate_strategy | 戦略生成 | 戦略シートJSON |
| LLMAnalyzer.generate_practice_plan | 練習計画生成 | 練習計画JSON |

### 5.2. 統合テスト

| テストシナリオ | 入力 | 期待結果 |
|:---|:---|:---|
| 完全分析フロー | 試合動画1本 | 分析レポート、戦略シート、練習計画 |
| 複数動画分析 | 試合動画3本 | 統合分析レポート |

---

## 6. エラーハンドリング

### 6.1. エラーコード

| コード | 説明 | 対処 |
|:---|:---|:---|
| E001 | 動画読込エラー | ファイル形式・パス確認 |
| E002 | API呼び出しエラー | リトライ、API制限確認 |
| E003 | 分析タイムアウト | 動画分割、設定調整 |
| E004 | 出力生成エラー | テンプレート確認 |

---

## 7. 依存パッケージ

### requirements.txt

```
# Core
openai>=1.0.0
google-generativeai>=0.3.0

# Video Processing
opencv-python>=4.8.0
mediapipe>=0.10.0

# Data Processing
numpy>=1.24.0
pandas>=2.0.0

# Output Generation
markdown>=3.4.0
weasyprint>=59.0

# Utilities
pyyaml>=6.0
python-dotenv>=1.0.0
```
