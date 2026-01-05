"""
卓球パフォーマンス分析システム - VideoAnalyzer v2
Google AI API（Gemini 2.0 Flash）を使用した動画直接分析版
高校生でも分かりやすい表現で出力
"""

import os
import json
import time
from typing import Optional
import google.generativeai as genai


class VideoAnalyzerV2:
    """
    動画を直接Gemini APIに送信して分析するクラス
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            api_key: Google AI APIキー（省略時は環境変数から取得）
        """
        self.api_key = api_key or os.environ.get("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY が設定されていません")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-2.0-flash")
    
    def analyze(self, video_path: str, player_identifier: str = "赤いユニフォームの選手") -> dict:
        """
        動画を分析する
        
        Args:
            video_path: 動画ファイルのパス
            player_identifier: 分析対象の選手を特定する説明
        
        Returns:
            分析結果の辞書
        """
        # 動画をアップロード
        print(f"動画をアップロード中: {video_path}")
        video_file = genai.upload_file(video_path)
        print("アップロード完了")
        
        # 動画処理を待機
        print("動画処理中...", end="", flush=True)
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        print(" 完了")
        
        # プロンプトを生成
        prompt = self._create_analysis_prompt(player_identifier)
        
        # 分析実行
        print("分析中...")
        response = self.model.generate_content([video_file, prompt])
        
        # JSON部分を抽出してパース
        result = self._parse_response(response.text)
        
        return result
    
    def _create_analysis_prompt(self, player_identifier: str) -> str:
        """
        高校生向けの分かりやすい分析プロンプトを生成
        """
        return f"""
あなたは高校の卓球部のコーチです。この試合動画を分析して、選手にフィードバックしてください。

## 分析対象
{player_identifier}

## 重要なルール
1. **高校生でも分かる言葉**で書いてください
2. 専門用語を使う場合は、必ず（）で簡単な説明を付けてください
3. 具体的な時間（例: 0分11秒）を引用して、「この場面を見て」と伝えてください
4. 良いところは具体的に褒めてください
5. 改善点は「こうするともっと良くなる」という前向きな表現で書いてください

## 分析項目

### 1. 基本情報
- 利き手と持ち方
- どんなタイプの選手か（攻撃的？守備的？バランス型？）

### 2. 技術の評価（5点満点）
それぞれについて：
- 点数（1〜5点）
- 良いところ（具体的な場面の時間を入れて）
- もっと良くなるポイント

評価する技術：
- フォアハンド（利き手側で打つ打ち方）
- バックハンド（利き手と反対側で打つ打ち方）
- サーブ（最初に打つボール）
- レシーブ（相手のサーブを返すこと）
- フットワーク（足の動き）

### 3. 試合の流れ
- 点を取れたパターン：どんな時に点が取れていた？（時間と状況を3つ）
- 点を取られたパターン：どんな時に点を取られていた？（時間と状況を3つ）

### 4. これからの練習
- **今すぐ直したいこと**：一番大事な改善点（どの場面を見てそう思ったかも書いて）
- **1ヶ月後の目標**：具体的に何ができるようになりたいか
- **3ヶ月後の目標**：さらにレベルアップするために

## 出力形式
JSON形式で出力してください。日本語で、高校生が読んで「なるほど！」と思える内容にしてください。

```json
{{
  "選手名": "選手名（分かれば）",
  "基本情報": {{
    "利き手と持ち方": "右利き、シェークハンド など",
    "プレースタイル": "攻撃的、守備的、バランス型 など"
  }},
  "技術評価": {{
    "フォアハンド": {{
      "点数": 1-5,
      "良いところ": "具体的な場面と時間を入れて",
      "もっと良くなるポイント": "前向きな表現で"
    }},
    "バックハンド": {{ ... }},
    "サーブ": {{ ... }},
    "レシーブ": {{ ... }},
    "フットワーク": {{ ... }}
  }},
  "試合の流れ": {{
    "点数を取れたパターン": [
      {{"時間": "0分11秒", "状況": "どんな状況で点が取れたか"}}
    ],
    "点数を取られたパターン": [
      {{"時間": "0分38秒", "状況": "どんな状況で点を取られたか"}}
    ]
  }},
  "これからの練習": {{
    "今すぐ直したいこと": {{
      "内容": "一番大事な改善点",
      "理由": "どの場面を見てそう思ったか"
    }},
    "1ヶ月後の目標": {{
      "内容": "具体的な目標",
      "理由": "なぜこの目標が大事か"
    }},
    "3ヶ月後の目標": {{
      "内容": "具体的な目標",
      "理由": "なぜこの目標が大事か"
    }}
  }}
}}
```
"""
    
    def _parse_response(self, response_text: str) -> dict:
        """
        レスポンスからJSONを抽出してパース
        """
        # ```json ... ``` の形式を探す
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            # JSON部分を探す
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # パースに失敗した場合は生テキストを返す
            return {"raw_response": response_text}


# 使用例
if __name__ == "__main__":
    import sys
    
    # APIキーを設定
    api_key = os.environ.get("GOOGLE_AI_API_KEY", "AIzaSyCtusQb-YtsqBWyTAHLjPxsbCg3mAC8fK4")
    
    # 動画パス
    video_path = sys.argv[1] if len(sys.argv) > 1 else "data/asami_match.mp4"
    
    # 分析実行
    analyzer = VideoAnalyzerV2(api_key=api_key)
    result = analyzer.analyze(video_path, player_identifier="赤いユニフォームの選手（背中に「浅見」と書かれている）")
    
    # 結果を表示
    print("\n" + "=" * 80)
    print("【分析結果】")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))
