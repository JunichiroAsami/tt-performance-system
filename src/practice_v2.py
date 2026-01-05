"""
卓球パフォーマンス分析システム - PracticePlanGenerator v2
高校生でも分かりやすい表現で練習計画を生成
"""

import os
import json
from typing import Optional
from openai import OpenAI


class PracticePlanGeneratorV2:
    """
    分析結果から練習計画を生成するクラス（高校生向け）
    """
    
    def __init__(self):
        """初期化"""
        self.client = OpenAI()
        self.model = "gemini-2.5-flash"
    
    def generate(self, analysis_result: dict) -> dict:
        """
        分析結果から練習計画を生成
        
        Args:
            analysis_result: VideoAnalyzerV2の分析結果
        
        Returns:
            練習計画の辞書
        """
        prompt = self._create_practice_prompt(analysis_result)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "あなたは高校の卓球部のコーチです。選手が「この練習をすれば上手くなれる！」とやる気が出る練習計画を作ってください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _create_practice_prompt(self, analysis_result: dict) -> str:
        """練習計画生成プロンプトを作成"""
        return f"""
以下の分析結果をもとに、1週間の練習計画を作ってください。

## 分析結果
```json
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}
```

## 練習計画の条件
1. **高校生でも分かる言葉**で書いてください
2. 専門用語には（）で説明を付けてください
3. 各練習は**具体的な手順**を書いてください
4. **時間の目安**を入れてください
5. **なぜこの練習をするのか**を説明してください

## 練習計画の構成

### 1. 今週の目標
- メインの目標（1つ）
- サブの目標（2つ）

### 2. 1週間の練習メニュー（5日分）
各日について：
- その日のテーマ
- ウォームアップ（10分）
- メイン練習1（20分）
- メイン練習2（20分）
- クールダウン（10分）

### 3. おすすめドリル集
分析結果で見つかった課題を克服するためのドリルを3つ

## 出力形式
JSON形式で出力してください。

```json
{{
  "今週の目標": {{
    "メイン": "一番大事な目標",
    "サブ": ["サブ目標1", "サブ目標2"]
  }},
  "1週間の練習メニュー": [
    {{
      "日目": 1,
      "テーマ": "その日のテーマ",
      "メニュー": [
        {{
          "種類": "ウォームアップ",
          "時間": "10分",
          "内容": "何をするか",
          "ポイント": "意識すること"
        }},
        {{
          "種類": "メイン練習1",
          "時間": "20分",
          "内容": "何をするか",
          "ポイント": "意識すること"
        }},
        {{
          "種類": "メイン練習2",
          "時間": "20分",
          "内容": "何をするか",
          "ポイント": "意識すること"
        }},
        {{
          "種類": "クールダウン",
          "時間": "10分",
          "内容": "何をするか",
          "ポイント": "意識すること"
        }}
      ]
    }}
  ],
  "おすすめドリル集": [
    {{
      "ドリル名": "ドリルの名前",
      "目的": "何を鍛えるか",
      "やり方": [
        "手順1",
        "手順2",
        "手順3"
      ],
      "時間": "何分",
      "回数": "何回または何セット",
      "コツ": "上手くやるためのポイント"
    }}
  ]
}}
```
"""
    
    def _parse_response(self, response_text: str) -> dict:
        """レスポンスからJSONを抽出してパース"""
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"raw_response": response_text}


if __name__ == "__main__":
    # テスト用
    test_analysis = {
        "選手名": "浅見選手",
        "これからの練習": {
            "今すぐ直したいこと": {
                "内容": "フォアハンドの打点を早くすること",
                "理由": "打点が遅れて相手に時間を与えている"
            }
        }
    }
    
    generator = PracticePlanGeneratorV2()
    result = generator.generate(test_analysis)
    print(json.dumps(result, ensure_ascii=False, indent=2))
