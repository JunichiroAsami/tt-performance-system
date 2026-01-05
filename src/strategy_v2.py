"""
卓球パフォーマンス分析システム - StrategyGenerator v2
高校生でも分かりやすい表現で戦略シートを生成
"""

import os
import json
from typing import Optional
from openai import OpenAI


class StrategyGeneratorV2:
    """
    分析結果から戦略シートを生成するクラス（高校生向け）
    """
    
    def __init__(self):
        """初期化"""
        self.client = OpenAI()
        self.model = "gemini-2.5-flash"
    
    def generate(self, analysis_result: dict) -> dict:
        """
        分析結果から戦略シートを生成
        
        Args:
            analysis_result: VideoAnalyzerV2の分析結果
        
        Returns:
            戦略シートの辞書
        """
        prompt = self._create_strategy_prompt(analysis_result)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "あなたは高校の卓球部のコーチです。選手が試合前に読んで「よし、これでいこう！」と思える戦略シートを作ってください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _create_strategy_prompt(self, analysis_result: dict) -> str:
        """戦略生成プロンプトを作成"""
        return f"""
以下の分析結果をもとに、次の試合で使える戦略シートを作ってください。

## 分析結果
```json
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}
```

## 戦略シートの条件
1. **高校生でも分かる言葉**で書いてください
2. 専門用語には（）で説明を付けてください
3. **A4用紙1枚**で読める量にしてください（試合前にサッと読める）
4. 具体的な行動を書いてください（「頑張る」ではなく「フォア前にサーブを出す」など）

## 戦略シートの構成

### 1. 今日の作戦（3つまで）
- 一番大事な作戦
- 二番目に大事な作戦
- 三番目に大事な作戦

### 2. サーブの作戦
- 序盤（1〜3点目）：どこに、どんなサーブを出すか
- 中盤（4〜7点目）：どこに、どんなサーブを出すか
- 終盤（8点目以降）：どこに、どんなサーブを出すか

### 3. レシーブの作戦
- 短いサーブが来たら：どう返すか
- 長いサーブが来たら：どう返すか
- 困ったら：安全な返し方

### 4. ラリーの作戦
- 自分が有利なとき：どう攻めるか
- 五分五分のとき：どうするか
- 自分が不利なとき：どう立て直すか

### 5. 心がけること
- 試合中に意識すること（2〜3個）

## 出力形式
JSON形式で出力してください。

```json
{{
  "今日の作戦": [
    {{"順位": 1, "作戦": "具体的な作戦"}},
    {{"順位": 2, "作戦": "具体的な作戦"}},
    {{"順位": 3, "作戦": "具体的な作戦"}}
  ],
  "サーブの作戦": {{
    "序盤": {{"場所": "どこに", "種類": "どんなサーブ", "狙い": "なぜそうするか"}},
    "中盤": {{"場所": "どこに", "種類": "どんなサーブ", "狙い": "なぜそうするか"}},
    "終盤": {{"場所": "どこに", "種類": "どんなサーブ", "狙い": "なぜそうするか"}}
  }},
  "レシーブの作戦": {{
    "短いサーブ": {{"返し方": "どう返すか", "狙い": "なぜそうするか"}},
    "長いサーブ": {{"返し方": "どう返すか", "狙い": "なぜそうするか"}},
    "困ったら": {{"返し方": "安全な返し方", "狙い": "なぜそうするか"}}
  }},
  "ラリーの作戦": {{
    "有利なとき": {{"やること": "どう攻めるか", "狙い": "なぜそうするか"}},
    "五分五分のとき": {{"やること": "どうするか", "狙い": "なぜそうするか"}},
    "不利なとき": {{"やること": "どう立て直すか", "狙い": "なぜそうするか"}}
  }},
  "心がけること": [
    "意識すること1",
    "意識すること2",
    "意識すること3"
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
        "基本情報": {
            "利き手と持ち方": "右利き、シェークハンド",
            "プレースタイル": "攻撃的"
        },
        "技術評価": {
            "フォアハンド": {"点数": 4, "良いところ": "威力がある", "もっと良くなるポイント": "打点を早く"},
            "バックハンド": {"点数": 3, "良いところ": "安定している", "もっと良くなるポイント": "攻撃パターンを増やす"}
        }
    }
    
    generator = StrategyGeneratorV2()
    result = generator.generate(test_analysis)
    print(json.dumps(result, ensure_ascii=False, indent=2))
