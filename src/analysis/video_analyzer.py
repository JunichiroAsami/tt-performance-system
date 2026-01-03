"""
Video Analyzer Module
動画からフレームを抽出してGemini APIで分析する
"""

import subprocess
import base64
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from openai import OpenAI


class VideoAnalyzer:
    """
    動画分析クラス
    
    動画からフレームを抽出し、Gemini APIで卓球のプレーを分析する
    """
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        """
        初期化
        
        Args:
            model: 使用するモデル名
        """
        self.model = model
        self.client = OpenAI()
        self.frame_dir = Path("/tmp/tt_frames")
        self.frame_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_video_duration(self, video_path: str) -> float:
        """動画の長さを取得"""
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ], capture_output=True, text=True)
        return float(result.stdout.strip())
    
    def _extract_frames(
        self, 
        video_path: str, 
        interval: int = 30,
        max_frames: int = 8
    ) -> List[Dict[str, Any]]:
        """
        動画からフレームを抽出
        
        Args:
            video_path: 動画ファイルのパス
            interval: フレーム抽出間隔（秒）
            max_frames: 最大フレーム数
            
        Returns:
            抽出したフレームのリスト
        """
        duration = self._get_video_duration(video_path)
        timestamps = [i * interval for i in range(min(int(duration // interval) + 1, max_frames))]
        
        frames = []
        for ts in timestamps:
            frame_path = self.frame_dir / f"frame_{ts:04d}.jpg"
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-ss', str(ts),
                '-vframes', '1',
                '-q:v', '3',
                str(frame_path)
            ], capture_output=True)
            
            if frame_path.exists():
                with open(frame_path, 'rb') as f:
                    img_data = base64.standard_b64encode(f.read()).decode('utf-8')
                frames.append({
                    'timestamp': ts,
                    'data': img_data
                })
        
        return frames
    
    def analyze_video(
        self,
        video_path: str,
        player_name: str = "浅見江里佳",
        team_name: str = "文化学園大学杉並"
    ) -> Dict[str, Any]:
        """
        動画を分析
        
        Args:
            video_path: 動画ファイルのパス
            player_name: 選手名
            team_name: 所属チーム名
            
        Returns:
            分析結果の辞書
        """
        print(f"動画を分析中: {video_path}")
        print(f"選手: {player_name} ({team_name})")
        
        # フレーム抽出
        print("フレームを抽出中...")
        frames = self._extract_frames(video_path)
        print(f"  {len(frames)} フレームを抽出")
        
        # API用のコンテンツを構築
        content = []
        for frame in frames:
            content.append({
                'type': 'text',
                'text': f'【{frame["timestamp"]}秒時点のフレーム】'
            })
            content.append({
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{frame["data"]}'
                }
            })
        
        # プロンプト
        prompt = f'''これは卓球の試合動画から抽出したフレームです。
選手「{player_name}」（{team_name}）のプレーを分析してください。

以下の点を分析し、JSON形式で出力してください：
{{
  "基本情報": {{
    "選手名": "{player_name}",
    "所属": "{team_name}",
    "利き手": "",
    "グリップ": "",
    "プレースタイル": ""
  }},
  "技術分析": {{
    "フォアハンド": {{"評価": "1-5の数値", "特徴": "", "改善点": ""}},
    "バックハンド": {{"評価": "1-5の数値", "特徴": "", "改善点": ""}},
    "サーブ": {{"評価": "1-5の数値", "特徴": "", "改善点": ""}},
    "レシーブ": {{"評価": "1-5の数値", "特徴": "", "改善点": ""}},
    "フットワーク": {{"評価": "1-5の数値", "特徴": "", "改善点": ""}}
  }},
  "戦術分析": {{
    "得点パターン": ["パターン1", "パターン2", "パターン3"],
    "失点パターン": ["パターン1", "パターン2", "パターン3"]
  }},
  "総合評価": "",
  "最優先改善点": ""
}}

JSONのみを出力してください。'''
        
        content.append({
            'type': 'text',
            'text': prompt
        })
        
        # API呼び出し
        print("APIで分析中...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': content}],
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content
        
        # JSONを抽出
        try:
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_response": result_text}
        except json.JSONDecodeError:
            return {"raw_response": result_text}
    
    def generate_strategy(
        self,
        analysis: Dict[str, Any],
        opponent_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        試合戦略を生成
        
        Args:
            analysis: 自己分析結果
            opponent_analysis: 相手分析結果（オプション）
            
        Returns:
            戦略の辞書
        """
        opponent_info = opponent_analysis if opponent_analysis else {"note": "相手情報なし"}
        
        prompt = f'''以下の分析結果に基づいて、試合で勝つための具体的な戦略を立案してください。

【自己分析】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

【相手分析】
{json.dumps(opponent_info, ensure_ascii=False, indent=2)}

以下の形式でJSON出力してください：
{{
  "サーブ戦略": {{
    "序盤（1-3点目）": {{"推奨サーブ": "", "狙い": ""}},
    "中盤（4-8点目）": {{"推奨サーブ": "", "狙い": ""}},
    "終盤・デュース": {{"推奨サーブ": "", "狙い": ""}}
  }},
  "レシーブ戦略": {{
    "短いサーブに対して": {{"推奨レシーブ": "", "注意点": ""}},
    "長いサーブに対して": {{"推奨レシーブ": "", "注意点": ""}}
  }},
  "ラリー戦略": {{
    "攻撃時": {{"狙うべきコース": "", "攻撃のタイミング": ""}},
    "守備時": {{"守備の方針": "", "カウンターのタイミング": ""}}
  }},
  "キーポイント": ["ポイント1", "ポイント2", "ポイント3"]
}}

JSONのみを出力してください。'''
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content
        
        try:
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_response": result_text}
        except json.JSONDecodeError:
            return {"raw_response": result_text}
    
    def generate_practice_plan(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        練習計画を生成
        
        Args:
            analysis: 分析結果
            
        Returns:
            練習計画の辞書
        """
        prompt = f'''以下の分析結果に基づいて、選手の弱点を克服するための練習計画を作成してください。

【分析結果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

以下の形式でJSON出力してください：
{{
  "優先課題": [
    {{"順位": 1, "課題": "", "理由": "", "優先度": "高/中/低"}},
    {{"順位": 2, "課題": "", "理由": "", "優先度": "高/中/低"}},
    {{"順位": 3, "課題": "", "理由": "", "優先度": "高/中/低"}}
  ],
  "週間練習計画": {{
    "Day1（月曜）": {{"テーマ": "", "内容": "", "時間": "", "ポイント": ""}},
    "Day2（火曜）": {{"テーマ": "", "内容": "", "時間": "", "ポイント": ""}},
    "Day3（水曜）": {{"テーマ": "", "内容": "", "時間": "", "ポイント": ""}},
    "Day4（木曜）": {{"テーマ": "", "内容": "", "時間": "", "ポイント": ""}},
    "Day5（金曜）": {{"テーマ": "", "内容": "", "時間": "", "ポイント": ""}}
  }},
  "ドリル": [
    {{"名前": "", "目的": "", "方法": "", "時間": "", "回数": ""}},
    {{"名前": "", "目的": "", "方法": "", "時間": "", "回数": ""}},
    {{"名前": "", "目的": "", "方法": "", "時間": "", "回数": ""}}
  ]
}}

JSONのみを出力してください。'''
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content
        
        try:
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_response": result_text}
        except json.JSONDecodeError:
            return {"raw_response": result_text}


def main():
    """テスト実行"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_analyzer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    analyzer = VideoAnalyzer()
    
    print("=== 動画分析を開始 ===")
    analysis = analyzer.analyze_video(video_path)
    
    print("\n=== 分析結果 ===")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    print("\n=== 戦略生成 ===")
    strategy = analyzer.generate_strategy(analysis)
    print(json.dumps(strategy, ensure_ascii=False, indent=2))
    
    print("\n=== 練習計画生成 ===")
    practice = analyzer.generate_practice_plan(analysis)
    print(json.dumps(practice, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
