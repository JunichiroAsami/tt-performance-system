"""
練習計画生成モジュール

TDD Step 4: 分析結果から練習計画を生成する
"""
import json
from typing import Optional
from openai import OpenAI


class PracticePlanner:
    """分析結果から練習計画を生成するクラス"""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = OpenAI()
        self.model = model
    
    def generate(self, analysis: dict, days: int = 5) -> dict:
        """
        分析結果から練習計画を生成
        
        Args:
            analysis: VideoAnalyzerからの分析結果
            days: 練習計画の日数（デフォルト5日）
            
        Returns:
            練習計画の辞書
        """
        if not analysis:
            raise ValueError("分析結果が空です")
        
        # プロンプト作成
        prompt = f"""あなたは卓球のコーチです。以下の選手分析結果を基に、{days}日間の練習計画を作成してください。

【選手分析結果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

以下のJSON形式で練習計画を作成してください（他の文章は不要です）:

{{
  "優先課題": [
    {{"課題": "...", "理由": "...", "優先度": 1}},
    {{"課題": "...", "理由": "...", "優先度": 2}},
    {{"課題": "...", "理由": "...", "優先度": 3}}
  ],
  "週間計画": {{
    "1日目": {{
      "テーマ": "...",
      "メニュー": [
        {{"名前": "...", "時間": "...分", "目的": "..."}},
        {{"名前": "...", "時間": "...分", "目的": "..."}}
      ]
    }},
    "2日目": {{
      "テーマ": "...",
      "メニュー": [...]
    }},
    "3日目": {{
      "テーマ": "...",
      "メニュー": [...]
    }},
    "4日目": {{
      "テーマ": "...",
      "メニュー": [...]
    }},
    "5日目": {{
      "テーマ": "...",
      "メニュー": [...]
    }}
  }},
  "ドリル集": [
    {{
      "名前": "...",
      "対象技術": "...",
      "手順": ["ステップ1", "ステップ2", "ステップ3"],
      "ポイント": "...",
      "目安時間": "...分"
    }}
  ],
  "達成目標": {{
    "1週間後": "...",
    "1ヶ月後": "...",
    "3ヶ月後": "..."
  }}
}}

注意: 
- 各メニューは具体的で実行可能な内容にしてください
- ドリルは最低3つ含めてください
- 選手の強みを活かし、弱点を改善する計画にしてください"""

        # API呼び出し
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500
        )
        
        # レスポンスをパース
        result_text = response.choices[0].message.content
        
        # JSONを抽出
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        try:
            result = json.loads(result_text.strip())
        except json.JSONDecodeError:
            result = {"raw_response": result_text, "parse_error": True}
        
        return result


if __name__ == "__main__":
    # 動作確認（分析結果を使用）
    import os
    
    # 保存されたエビデンスから分析結果を読み込む
    evidence_path = "tests/evidence/analyzer_test_evidence.json"
    if os.path.exists(evidence_path):
        with open(evidence_path, "r", encoding="utf-8") as f:
            evidence = json.load(f)
            analysis = evidence["output"]
    else:
        # サンプルデータ
        analysis = {
            "基本情報": {"利き手": "右", "グリップ": "シェークハンド", "プレースタイル": "ドライブ主戦型"},
            "技術評価": {"フォアハンド": {"スコア": 4}, "バックハンド": {"スコア": 3}},
            "戦術分析": {"得点パターン": ["3球目攻撃"], "失点パターン": ["バック側への攻撃"]},
            "改善提案": {"最優先": "バックハンドの強化"}
        }
    
    planner = PracticePlanner()
    result = planner.generate(analysis)
    print(json.dumps(result, ensure_ascii=False, indent=2))
