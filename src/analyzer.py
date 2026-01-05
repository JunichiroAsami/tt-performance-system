"""
卓球動画分析モジュール（改良版）

TDD Step 2: 動画を分析して選手の技術評価を行う
- 改良: 5秒間隔で20フレームを抽出
- 改良: 具体的なフレーム番号を引用した分析
"""
import cv2
import base64
import json
from typing import Optional
from openai import OpenAI


class VideoAnalyzer:
    """動画から卓球選手のパフォーマンスを分析するクラス"""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = OpenAI()
        self.model = model
        # 改良: フレーム抽出パラメータ
        self.frame_interval = 5  # 秒（従来は等間隔分割）
        self.max_frames = 20     # フレーム数（従来は6）
    
    def extract_frames(self, video_path: str) -> tuple[list[str], list[float]]:
        """
        動画から5秒間隔でフレームを抽出してBase64エンコード
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            (Base64エンコードされた画像のリスト, タイムスタンプのリスト)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"動画を開けません: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            cap.release()
            raise ValueError(f"動画にフレームがありません: {video_path}")
        
        duration = total_frames / fps
        
        frames_base64 = []
        timestamps = []
        
        for i in range(self.max_frames):
            ts = i * self.frame_interval
            if ts >= duration:
                break
            
            frame_num = int(ts * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                # 品質を維持しつつエンコード
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frames_base64.append(base64.b64encode(buffer).decode('utf-8'))
                timestamps.append(ts)
        
        cap.release()
        
        if not frames_base64:
            raise ValueError(f"フレームを抽出できませんでした: {video_path}")
        
        return frames_base64, timestamps
    
    def analyze(self, video_path: str) -> dict:
        """
        動画を分析して選手の技術評価を返す
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            分析結果の辞書
        """
        # フレーム抽出
        frames, timestamps = self.extract_frames(video_path)
        
        # プロンプト作成（改良版）
        prompt = f"""あなたは卓球のプロコーチです。上記の試合動画フレーム（{self.frame_interval}秒間隔、合計{len(frames)}枚）を分析してください。

## 分析対象
赤いユニフォームの選手（背中に「浅見」と書かれている）

## 重要
- 各フレームは{self.frame_interval}秒間隔で抽出されています
- フレーム1は0秒、フレーム2は{self.frame_interval}秒、フレーム3は{self.frame_interval*2}秒...と続きます
- 実際に動画で確認できた内容のみを分析してください
- 推測や一般論ではなく、具体的なフレーム番号を引用してください

## 出力形式
以下のJSON形式で回答してください（他の文章は不要です）:

{{
  "基本情報": {{
    "利き手": {{"値": "右 or 左", "確認フレーム": "フレーム番号"}},
    "グリップ": {{"値": "シェークハンド or ペンホルダー", "確認フレーム": "フレーム番号"}},
    "プレースタイル": {{"値": "タイプ", "確認フレーム": "フレーム番号"}}
  }},
  "技術評価": {{
    "フォアハンド": {{"評価": 1-5, "観察内容": "具体的な観察", "確認フレーム": "番号"}},
    "バックハンド": {{"評価": 1-5, "観察内容": "具体的な観察", "確認フレーム": "番号"}},
    "サーブ": {{"評価": 1-5, "観察内容": "具体的な観察", "確認フレーム": "番号"}},
    "レシーブ": {{"評価": 1-5, "観察内容": "具体的な観察", "確認フレーム": "番号"}},
    "フットワーク": {{"評価": 1-5, "観察内容": "具体的な観察", "確認フレーム": "番号"}}
  }},
  "戦術分析": {{
    "得点パターン": [
      {{"フレーム番号": "番号", "状況": "具体的な説明"}}
    ],
    "失点パターン": [
      {{"フレーム番号": "番号", "状況": "具体的な説明"}}
    ]
  }},
  "改善提案": {{
    "最優先で改善すべき点": {{"内容": "改善点", "根拠フレーム": "番号"}},
    "短期目標（1ヶ月）": "目標",
    "長期目標（3ヶ月）": "目標"
  }}
}}"""

        # API呼び出し用のコンテンツ作成
        content = []
        for frame in frames:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{frame}"}
            })
        content.append({"type": "text", "text": prompt})
        
        # API呼び出し
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            max_tokens=4000
        )
        
        # レスポンスをパース
        result_text = response.choices[0].message.content
        
        # JSONを抽出（マークダウンコードブロックを除去）
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        try:
            result = json.loads(result_text.strip())
        except json.JSONDecodeError:
            # パースに失敗した場合は生のテキストを返す
            result = {"raw_response": result_text, "parse_error": True}
        
        return result


if __name__ == "__main__":
    # 動作確認
    analyzer = VideoAnalyzer()
    result = analyzer.analyze("data/asami_match.mp4")
    print(json.dumps(result, ensure_ascii=False, indent=2))
