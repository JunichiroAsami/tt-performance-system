"""
卓球動画分析モジュール

TDD Step 2: 動画を分析して選手の技術評価を行う
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
    
    def extract_frames(self, video_path: str, num_frames: int = 6) -> list[str]:
        """
        動画から等間隔でフレームを抽出してBase64エンコード
        
        Args:
            video_path: 動画ファイルのパス
            num_frames: 抽出するフレーム数
            
        Returns:
            Base64エンコードされた画像のリスト
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"動画を開けません: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            cap.release()
            raise ValueError(f"動画にフレームがありません: {video_path}")
        
        # 等間隔でフレームを抽出
        interval = total_frames // (num_frames + 1)
        frames_base64 = []
        
        for i in range(1, num_frames + 1):
            frame_pos = i * interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                # リサイズして軽量化
                frame = cv2.resize(frame, (640, 360))
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frames_base64.append(base64.b64encode(buffer).decode('utf-8'))
        
        cap.release()
        
        if not frames_base64:
            raise ValueError(f"フレームを抽出できませんでした: {video_path}")
        
        return frames_base64
    
    def analyze(self, video_path: str) -> dict:
        """
        動画を分析して選手の技術評価を返す
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            分析結果の辞書
        """
        # フレーム抽出
        frames = self.extract_frames(video_path)
        
        # プロンプト作成
        prompt = """あなたは卓球のコーチです。以下の試合動画のフレームを分析し、選手のパフォーマンスを評価してください。

以下のJSON形式で回答してください（他の文章は不要です）:

{
  "基本情報": {
    "利き手": "右 or 左",
    "グリップ": "シェークハンド or ペンホルダー",
    "プレースタイル": "ドライブ主戦型 など"
  },
  "技術評価": {
    "フォアハンド": {"スコア": 1-5, "コメント": "..."},
    "バックハンド": {"スコア": 1-5, "コメント": "..."},
    "サーブ": {"スコア": 1-5, "コメント": "..."},
    "レシーブ": {"スコア": 1-5, "コメント": "..."},
    "フットワーク": {"スコア": 1-5, "コメント": "..."}
  },
  "戦術分析": {
    "得点パターン": ["パターン1", "パターン2", "パターン3"],
    "失点パターン": ["パターン1", "パターン2", "パターン3"]
  },
  "改善提案": {
    "最優先": "...",
    "短期目標": "...",
    "長期目標": "..."
  }
}"""

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
            max_tokens=2000
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
