"""
戦略シート生成モジュール

TDD Step 3: 分析結果から試合用の戦略シートを生成する
"""
import json
from typing import Optional
from openai import OpenAI


class StrategyGenerator:
    """分析結果から戦略シートを生成するクラス"""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = OpenAI()
        self.model = model
    
    def generate(self, analysis: dict, opponent_info: Optional[dict] = None) -> dict:
        """
        分析結果から戦略シートを生成
        
        Args:
            analysis: VideoAnalyzerからの分析結果
            opponent_info: 対戦相手の情報（オプション）
            
        Returns:
            戦略シートの辞書
        """
        if not analysis:
            raise ValueError("分析結果が空です")
        
        # プロンプト作成
        prompt = f"""あなたは卓球のコーチです。以下の選手分析結果を基に、試合で使える戦略シートを作成してください。

【選手分析結果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

"""
        if opponent_info:
            prompt += f"""
【対戦相手情報】
{json.dumps(opponent_info, ensure_ascii=False, indent=2)}

"""
        
        prompt += """以下のJSON形式で、試合前に読んで理解できる簡潔な戦略シートを作成してください（他の文章は不要です）:

{
  "サーブ戦略": {
    "序盤": {
      "推奨サーブ": "...",
      "狙い": "..."
    },
    "中盤": {
      "推奨サーブ": "...",
      "狙い": "..."
    },
    "終盤": {
      "推奨サーブ": "...",
      "狙い": "..."
    }
  },
  "レシーブ戦略": {
    "短いサーブに対して": "...",
    "長いサーブに対して": "...",
    "横回転サーブに対して": "..."
  },
  "ラリー戦略": {
    "基本方針": "...",
    "得点パターン": ["パターン1", "パターン2"],
    "注意点": "..."
  },
  "メンタル": {
    "試合前": "...",
    "リードしている時": "...",
    "リードされている時": "..."
  },
  "ワンポイントアドバイス": "..."
}

注意: 試合前に読んで理解できるよう、各項目は1-2文で簡潔に。全体でA4一枚程度の分量に収めてください。"""

        # API呼び出し
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
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
    
    generator = StrategyGenerator()
    result = generator.generate(analysis)
    print(json.dumps(result, ensure_ascii=False, indent=2))
