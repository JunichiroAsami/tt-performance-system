# 開発仕様書（詳細設計書） v2.0

**ドキュメントID**: DES-02  
**バージョン**: 2.0  
**作成日**: 2026年1月4日  
**作成者**: Manus AI (PM)  
**ステータス**: レビュー完了

---

## 1. はじめに

本ドキュメントは、「概要設計書 v2.0 (DES-01)」を基に、各モジュールの内部実装、クラス設計、データ構造、アルゴリズム、API連携の詳細を定義する。

---

## 2. 業務要件と詳細設計の対応

| 要件ID | 要件名 | 対応クラス/メソッド/プロンプト | 設計状況 |
|:---|:---|:---|:---:|
| **FA-01** | 得点/失点パターン分析 | `IntegrationEngine.analyze_rally_patterns()` | ✅ |
| **FA-02** | 技術別パフォーマンス分析 | `IntegrationEngine.calculate_technique_stats()` | ✅ |
| **FA-03** | サーブ/レシーブ分析 | `IntegrationEngine.analyze_serve_receive()` | ✅ |
| **FA-04** | フォーム分析 | `PoseEstimator`, `TechniqueAI` (Prompt: `FORM_ANALYSIS_PROMPT`) | ✅ |
| **FA-05** | フットワーク分析 | `PoseEstimator`, `CourtMapper` | ✅ |
| **FA-06** | 相手の得点/失点パターン分析 | `IntegrationEngine.analyze_rally_patterns(is_opponent=True)` | ✅ |
| **FA-07** | 相手のサーブ/レシーブ傾向分析 | `IntegrationEngine.analyze_serve_receive(is_opponent=True)` | ✅ |
| **FA-08** | 相手の弱点特定 | `IntegrationEngine.identify_opponent_weakness()` | ✅ |
| **FS-01** | 対戦相手別戦略シート生成 | `StrategyGenerator.generate()` | ✅ |
| **FS-02** | サーブ戦略提案 | `StrategyGenerator` (Prompt: `STRATEGY_PROMPT`) | ✅ |
| **FS-03** | レシーブ戦略提案 | `StrategyGenerator` (Prompt: `STRATEGY_PROMPT`) | ✅ |
| **FS-04** | ラリー展開戦略提案 | `StrategyGenerator` (Prompt: `STRATEGY_PROMPT`) | ✅ |
| **FP-01** | 課題の優先順位付け | `PracticeGenerator.prioritize_issues()` | ✅ |
| **FP-02** | カスタム練習メニュー生成 | `PracticeGenerator.generate_menus()` | ✅ |
| **FP-03** | フォーム改善ドリル提案 | `TechniqueAI` (Prompt: `FORM_DRILL_PROMPT`) | ✅ |
| **FR-01** | 試合後サマリーレポート | `ReportGenerator.generate_summary()` | ✅ |
| **FR-02** | パフォーマンスダッシュボード | (Phase 3) | ❌ |
| **FR-03** | プレー動画へのアノテーション | (Phase 3) | ❌ |

---

## 3. クラス設計

### 3.1. `CVAnalyzer` (定量分析)

```python
class CVAnalyzer:
    def __init__(self, video_path):
        # ...

    def run_analysis(self) -> dict:
        # ボール追跡、姿勢推定、コートマッピングを並列実行
        ball_data = self.track_ball()
        pose_data = self.estimate_pose()
        court_data = self.map_court()
        return {"ball": ball_data, "pose": pose_data, "court": court_data}

    def track_ball(self) -> list:
        # ...

    def estimate_pose(self) -> list:
        # ...

    def map_court(self) -> dict:
        # ...
```

### 3.2. `LLMAnalyzer` (定性分析)

```python
class LLMAnalyzer:
    def __init__(self, api_key):
        # ...

    def analyze_tactics(self, video_frames, cv_data) -> dict:
        # Prompt: TACTICS_ANALYSIS_PROMPT
        # ...

    def analyze_technique(self, video_frames, pose_data) -> dict:
        # Prompt: TECHNIQUE_ANALYSIS_PROMPT
        # ...

    def suggest_form_drills(self, form_analysis_result) -> dict:
        # Prompt: FORM_DRILL_PROMPT
        # ...
```

### 3.3. `IntegrationEngine` (統合分析)

```python
class IntegrationEngine:
    def __init__(self, cv_result, llm_result):
        # ...

    def run_integration(self) -> dict:
        # ...

    def analyze_rally_patterns(self, is_opponent=False) -> dict:
        # FA-01, FA-06
        # ...

    def calculate_technique_stats(self) -> dict:
        # FA-02
        # ...

    def analyze_serve_receive(self, is_opponent=False) -> dict:
        # FA-03, FA-07
        # ...

    def identify_opponent_weakness(self) -> dict:
        # FA-08
        # ...
```

### 3.4. `StrategyGenerator` / `PracticeGenerator` / `ReportGenerator`

（設計はv1.0から大きな変更なし、入力データとして`IntegrationEngine`の出力を受け取る）

---

## 4. プロンプト設計

### 4.1. `TACTICS_ANALYSIS_PROMPT` (戦術分析)

**役割**: あなたは世界トップクラスの卓球コーチです。
**入力**: プレーシーンの動画、ボールと選手の軌道データ
**タスク**: 以下の観点で戦術を評価してください。
- 展開の意図は何か？
- その判断は適切か？
- より良い選択肢はあったか？
- 相手の戦術は何か？

### 4.2. `TECHNIQUE_ANALYSIS_PROMPT` (技術分析)

**役割**: あなたは卓球のフォーム分析の専門家です。
**入力**: スイング動画、関節角度データ
**タスク**: 以下の観点でフォームを評価してください。
- 体重移動は適切か？
- 打点は適切か？
- スイングの軌道は理想的か？
- 改善すべき点は何か？

### 4.3. `FORM_DRILL_PROMPT` (フォーム改善ドリル提案)

**役割**: あなたは経験豊富な卓球コーチです。
**入力**: フォーム分析の結果（改善すべき点）
**タスク**: 指摘された問題点を改善するための、具体的な練習ドリルを3つ提案してください。

### 4.4. `STRATEGY_PROMPT` (試合戦略提案)

**役割**: あなたは戦術立案の専門家です。
**入力**: 自己分析レポート、相手分析レポート
**タスク**: 以下の項目を含む試合戦略シートを作成してください。
- 基本戦略（コンセプト）
- サーブ戦略（コース、回転、3球目）
- レシーブ戦略（チキータ、ストップ、ドライブの使い分け）
- ラリー展開（相手の弱点をどう突くか）

---

## 5. データ構造

（v1.0から大きな変更なし、各分析結果を格納するキーを追加）
