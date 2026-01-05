"""
IntegrationEngine - 定量分析と定性分析の統合モジュール

Phase 2で実装する機能:
- CVAnalyzer（姿勢推定、フットワーク）の結果とLLM分析を統合
- フォーム分析（FA-04）: 関節角度データ + LLMによる評価
- フットワーク分析（FA-05）: 移動データ + LLMによる評価
- フォーム改善ドリル提案（FP-03）: フォーム分析結果を基にLLMが提案
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI


@dataclass
class FormAnalysisResult:
    """フォーム分析結果"""
    technique: str  # 技術名
    timestamp_sec: float  # タイムスタンプ
    joint_angles: Dict  # 関節角度
    evaluation: str  # LLMによる評価
    improvement_points: List[str]  # 改善点
    score: int  # 1-5のスコア


@dataclass
class FootworkAnalysisResult:
    """フットワーク分析結果"""
    total_distance: float
    avg_speed: float
    lateral_ratio: float  # 左右移動の割合
    evaluation: str  # LLMによる評価
    improvement_points: List[str]
    score: int


@dataclass
class FormDrill:
    """フォーム改善ドリル"""
    name: str
    purpose: str
    description: str
    duration: str
    points: List[str]


class IntegrationEngine:
    """
    定量分析と定性分析の統合エンジン
    
    CVAnalyzerの数値データとLLMの定性分析を組み合わせて、
    より詳細で根拠のある分析結果を生成します。
    """
    
    def __init__(self):
        """OpenAI互換APIを使用（環境変数で設定済み）"""
        self.client = OpenAI()
        self.model_name = "gemini-2.5-flash"
        
        # 分析結果格納用
        self.cv_results: Optional[Dict] = None
        self.llm_results: Optional[Dict] = None
        self.form_analysis: List[FormAnalysisResult] = []
        self.footwork_analysis: Optional[FootworkAnalysisResult] = None
        self.form_drills: List[FormDrill] = []
    
    def _call_llm(self, prompt: str) -> str:
        """LLMを呼び出す"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def _extract_json(self, text: str) -> str:
        """テキストからJSONを抽出"""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        return text
    
    def load_cv_results(self, cv_results_path: str):
        """CVAnalyzerの結果を読み込む"""
        with open(cv_results_path, "r", encoding="utf-8") as f:
            self.cv_results = json.load(f)
        return self
    
    def load_llm_results(self, llm_results_path: str):
        """LLM分析の結果を読み込む"""
        with open(llm_results_path, "r", encoding="utf-8") as f:
            self.llm_results = json.load(f)
        return self
    
    def analyze_form(self, verbose: bool = False) -> List[FormAnalysisResult]:
        """
        フォーム分析（FA-04）
        
        関節角度データとLLMの評価を組み合わせて、
        フォームの問題点を特定します。
        """
        if not self.cv_results:
            raise ValueError("CV分析結果が読み込まれていません")
        
        if verbose:
            print("[IntegrationEngine] フォーム分析を実行中...")
        
        # 関節角度の統計を取得
        angle_stats = self.cv_results.get("joint_angles", {}).get("statistics", {})
        swing_events = self.cv_results.get("swing_analysis", {}).get("swing_events", [])
        
        # LLMにフォーム分析を依頼
        prompt = f"""
あなたは卓球のフォーム分析の専門家です。
以下の関節角度データを分析し、フォームの評価を行ってください。

## 関節角度データ（統計）

### 右肘
- 平均: {angle_stats.get('right_elbow', {}).get('avg', 0):.1f}度
- 最小: {angle_stats.get('right_elbow', {}).get('min', 0):.1f}度
- 最大: {angle_stats.get('right_elbow', {}).get('max', 0):.1f}度
- 標準偏差: {angle_stats.get('right_elbow', {}).get('std', 0):.1f}度

### 左肘
- 平均: {angle_stats.get('left_elbow', {}).get('avg', 0):.1f}度
- 最小: {angle_stats.get('left_elbow', {}).get('min', 0):.1f}度
- 最大: {angle_stats.get('left_elbow', {}).get('max', 0):.1f}度
- 標準偏差: {angle_stats.get('left_elbow', {}).get('std', 0):.1f}度

### 右膝
- 平均: {angle_stats.get('right_knee', {}).get('avg', 0):.1f}度
- 最小: {angle_stats.get('right_knee', {}).get('min', 0):.1f}度
- 最大: {angle_stats.get('right_knee', {}).get('max', 0):.1f}度
- 標準偏差: {angle_stats.get('right_knee', {}).get('std', 0):.1f}度

### 左膝
- 平均: {angle_stats.get('left_knee', {}).get('avg', 0):.1f}度
- 最小: {angle_stats.get('left_knee', {}).get('min', 0):.1f}度
- 最大: {angle_stats.get('left_knee', {}).get('max', 0):.1f}度
- 標準偏差: {angle_stats.get('left_knee', {}).get('std', 0):.1f}度

### 体幹の傾き
- 平均: {angle_stats.get('trunk_angle', {}).get('avg', 0):.1f}度
- 最小: {angle_stats.get('trunk_angle', {}).get('min', 0):.1f}度
- 最大: {angle_stats.get('trunk_angle', {}).get('max', 0):.1f}度
- 標準偏差: {angle_stats.get('trunk_angle', {}).get('std', 0):.1f}度

### スイング検出
- 検出されたスイング数: {len(swing_events)}回

## 分析してほしいこと

1. **フォアハンドのフォーム評価**
   - 肘の角度は適切か？（理想: 90-120度）
   - 膝の使い方は適切か？（理想: 軽く曲げた状態を維持）
   - 体幹の安定性は？

2. **バックハンドのフォーム評価**
   - 同様に評価

3. **全体的な姿勢の評価**
   - 重心の安定性
   - 体の使い方

以下のJSON形式で出力してください：

```json
{{
  "フォアハンド": {{
    "評価": "良い/普通/要改善",
    "スコア": 1-5,
    "良い点": ["良い点1", "良い点2"],
    "改善点": ["改善点1", "改善点2"],
    "詳細": "具体的な評価コメント"
  }},
  "バックハンド": {{
    "評価": "良い/普通/要改善",
    "スコア": 1-5,
    "良い点": ["良い点1", "良い点2"],
    "改善点": ["改善点1", "改善点2"],
    "詳細": "具体的な評価コメント"
  }},
  "全体姿勢": {{
    "評価": "良い/普通/要改善",
    "スコア": 1-5,
    "良い点": ["良い点1", "良い点2"],
    "改善点": ["改善点1", "改善点2"],
    "詳細": "具体的な評価コメント"
  }}
}}
```

高校生でも分かるように、専門用語には（）で説明を付けてください。
"""
        
        result_text = self._call_llm(prompt)
        json_str = self._extract_json(result_text)
        
        try:
            form_data = json.loads(json_str)
            
            # 結果を構造化
            for technique, data in form_data.items():
                self.form_analysis.append(FormAnalysisResult(
                    technique=technique,
                    timestamp_sec=0,
                    joint_angles=angle_stats,
                    evaluation=data.get("詳細", ""),
                    improvement_points=data.get("改善点", []),
                    score=data.get("スコア", 3)
                ))
        except json.JSONDecodeError:
            if verbose:
                print(f"[IntegrationEngine] JSONパースエラー: {result_text[:200]}")
        
        if verbose:
            print(f"[IntegrationEngine] フォーム分析完了: {len(self.form_analysis)}項目")
        
        return self.form_analysis
    
    def analyze_footwork(self, verbose: bool = False) -> FootworkAnalysisResult:
        """
        フットワーク分析（FA-05）
        
        移動データとLLMの評価を組み合わせて、
        フットワークの問題点を特定します。
        """
        if not self.cv_results:
            raise ValueError("CV分析結果が読み込まれていません")
        
        if verbose:
            print("[IntegrationEngine] フットワーク分析を実行中...")
        
        footwork_data = self.cv_results.get("footwork", {})
        video_info = self.cv_results.get("video_info", {})
        
        total_distance = footwork_data.get("total_distance", 0)
        avg_speed = footwork_data.get("avg_speed", 0)
        lateral = footwork_data.get("lateral_movement", 0)
        forward_backward = footwork_data.get("forward_backward", 0)
        duration = video_info.get("duration_sec", 1)
        
        # 左右移動の割合を計算
        total_movement = lateral + forward_backward
        lateral_ratio = lateral / total_movement if total_movement > 0 else 0
        
        prompt = f"""
あなたは卓球のフットワーク分析の専門家です。
以下の移動データを分析し、フットワークの評価を行ってください。

## フットワークデータ

- **総移動距離**: {total_distance:.2f}（正規化座標）
- **平均移動速度**: {avg_speed:.4f}
- **最大移動速度**: {footwork_data.get('max_speed', 0):.4f}
- **左右移動量**: {lateral:.2f}
- **前後移動量**: {forward_backward:.2f}
- **左右移動の割合**: {lateral_ratio*100:.1f}%
- **動画の長さ**: {duration:.1f}秒

## 分析してほしいこと

1. **移動量の評価**
   - 卓球の試合として適切な移動量か？
   - 左右と前後のバランスは適切か？

2. **フットワークの効率性**
   - 無駄な動きはないか？
   - 戻りの動きは適切か？

3. **改善点**
   - 具体的にどう改善すべきか？

以下のJSON形式で出力してください：

```json
{{
  "評価": "良い/普通/要改善",
  "スコア": 1-5,
  "良い点": ["良い点1", "良い点2"],
  "改善点": ["改善点1", "改善点2"],
  "詳細": "具体的な評価コメント",
  "アドバイス": "改善のための具体的なアドバイス"
}}
```

高校生でも分かるように、専門用語には（）で説明を付けてください。
"""
        
        result_text = self._call_llm(prompt)
        json_str = self._extract_json(result_text)
        
        try:
            fw_data = json.loads(json_str)
            
            self.footwork_analysis = FootworkAnalysisResult(
                total_distance=total_distance,
                avg_speed=avg_speed,
                lateral_ratio=lateral_ratio,
                evaluation=fw_data.get("詳細", ""),
                improvement_points=fw_data.get("改善点", []),
                score=fw_data.get("スコア", 3)
            )
        except json.JSONDecodeError:
            if verbose:
                print(f"[IntegrationEngine] JSONパースエラー: {result_text[:200]}")
            
            self.footwork_analysis = FootworkAnalysisResult(
                total_distance=total_distance,
                avg_speed=avg_speed,
                lateral_ratio=lateral_ratio,
                evaluation="分析エラー",
                improvement_points=[],
                score=3
            )
        
        if verbose:
            print(f"[IntegrationEngine] フットワーク分析完了")
        
        return self.footwork_analysis
    
    def generate_form_drills(self, verbose: bool = False) -> List[FormDrill]:
        """
        フォーム改善ドリル提案（FP-03）
        
        フォーム分析の結果を基に、具体的な練習ドリルを提案します。
        """
        if not self.form_analysis:
            if verbose:
                print("[IntegrationEngine] フォーム分析を先に実行します...")
            self.analyze_form(verbose=verbose)
        
        if verbose:
            print("[IntegrationEngine] フォーム改善ドリルを生成中...")
        
        # 改善点を収集
        all_improvements = []
        for fa in self.form_analysis:
            all_improvements.extend(fa.improvement_points)
        
        if not all_improvements:
            all_improvements = ["基本フォームの確認", "体幹の安定性向上"]
        
        prompt = f"""
あなたは経験豊富な卓球コーチです。
以下の改善点に対応するための、具体的な練習ドリルを提案してください。

## 改善が必要な点

{chr(10).join(f"- {imp}" for imp in all_improvements)}

## 提案してほしいこと

各改善点に対応する練習ドリルを3つ提案してください。
高校生が一人でも、または練習相手と一緒にできるドリルを提案してください。

以下のJSON形式で出力してください：

```json
{{
  "ドリル": [
    {{
      "名前": "ドリルの名前",
      "目的": "このドリルで何が改善されるか",
      "説明": "具体的なやり方",
      "時間": "推奨練習時間",
      "ポイント": ["注意点1", "注意点2"]
    }}
  ]
}}
```

高校生でも分かるように、専門用語には（）で説明を付けてください。
"""
        
        result_text = self._call_llm(prompt)
        json_str = self._extract_json(result_text)
        
        try:
            drills_data = json.loads(json_str)
            
            for drill in drills_data.get("ドリル", []):
                self.form_drills.append(FormDrill(
                    name=drill.get("名前", ""),
                    purpose=drill.get("目的", ""),
                    description=drill.get("説明", ""),
                    duration=drill.get("時間", "10分"),
                    points=drill.get("ポイント", [])
                ))
        except json.JSONDecodeError:
            if verbose:
                print(f"[IntegrationEngine] JSONパースエラー: {result_text[:200]}")
        
        if verbose:
            print(f"[IntegrationEngine] ドリル生成完了: {len(self.form_drills)}個")
        
        return self.form_drills
    
    def run_full_analysis(self, verbose: bool = False) -> Dict:
        """全ての統合分析を実行"""
        if verbose:
            print("[IntegrationEngine] 統合分析を開始...")
        
        self.analyze_form(verbose=verbose)
        self.analyze_footwork(verbose=verbose)
        self.generate_form_drills(verbose=verbose)
        
        if verbose:
            print("[IntegrationEngine] 統合分析完了")
        
        return self.compile_results()
    
    def compile_results(self) -> Dict:
        """結果をまとめる"""
        return {
            "form_analysis": [asdict(fa) for fa in self.form_analysis],
            "footwork_analysis": asdict(self.footwork_analysis) if self.footwork_analysis else {},
            "form_drills": [asdict(fd) for fd in self.form_drills],
            "summary": {
                "form_avg_score": sum(fa.score for fa in self.form_analysis) / len(self.form_analysis) if self.form_analysis else 0,
                "footwork_score": self.footwork_analysis.score if self.footwork_analysis else 0,
                "total_drills": len(self.form_drills)
            }
        }
    
    def save_results(self, output_path: str):
        """結果をJSONファイルに保存"""
        results = self.compile_results()
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return output_path


# テスト用
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python integration_engine.py <cv_results_path>")
        sys.exit(1)
    
    cv_results_path = sys.argv[1]
    
    engine = IntegrationEngine()
    engine.load_cv_results(cv_results_path)
    
    results = engine.run_full_analysis(verbose=True)
    
    print("\n=== 統合分析結果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
