"""
LLM Analyzer Module
Gemini APIを使用した卓球動画の定性分析
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI

from .prompts import (
    COMPREHENSIVE_ANALYSIS_PROMPT,
    STRATEGY_GENERATION_PROMPT,
    PRACTICE_PLAN_PROMPT,
    OPPONENT_ANALYSIS_PROMPT
)


class LLMAnalyzer:
    """
    Gemini APIを使用した動画の定性分析クラス
    
    機能:
    - 動画の総合分析（技術・戦術）
    - 試合戦略の生成
    - 練習計画の生成
    - 相手分析
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        初期化
        
        Args:
            api_key: OpenAI API Key（環境変数から取得可能）
            model: 使用するモデル名
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.client = OpenAI()  # 環境変数から自動設定
        
    def _encode_video(self, video_path: str) -> str:
        """
        動画ファイルをBase64エンコード
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            Base64エンコードされた文字列
        """
        with open(video_path, "rb") as video_file:
            return base64.standard_b64encode(video_file.read()).decode("utf-8")
    
    def _get_video_mime_type(self, video_path: str) -> str:
        """
        動画ファイルのMIMEタイプを取得
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            MIMEタイプ文字列
        """
        ext = Path(video_path).suffix.lower()
        mime_types = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".webm": "video/webm"
        }
        return mime_types.get(ext, "video/mp4")
    
    def analyze_video(
        self,
        video_path: str,
        player_name: str = "浅見江里佳",
        team_name: str = "文化学園大学杉並"
    ) -> Dict[str, Any]:
        """
        動画の総合分析を実行
        
        Args:
            video_path: 動画ファイルのパス
            player_name: 選手名
            team_name: 所属チーム名
            
        Returns:
            分析結果の辞書
        """
        # 動画をエンコード
        video_data = self._encode_video(video_path)
        mime_type = self._get_video_mime_type(video_path)
        
        # プロンプトを構築
        prompt = COMPREHENSIVE_ANALYSIS_PROMPT.format(
            player_name=player_name,
            team_name=team_name
        )
        
        # API呼び出し
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": f"data:{mime_type};base64,{video_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.7
        )
        
        # レスポンスを解析
        result_text = response.choices[0].message.content
        
        # JSONを抽出
        try:
            # JSON部分を抽出
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"raw_response": result_text}
        except json.JSONDecodeError:
            return {"raw_response": result_text}
    
    def analyze_multiple_videos(
        self,
        video_paths: list,
        player_name: str = "浅見江里佳",
        team_name: str = "文化学園大学杉並"
    ) -> Dict[str, Any]:
        """
        複数動画の統合分析を実行
        
        Args:
            video_paths: 動画ファイルパスのリスト
            player_name: 選手名
            team_name: 所属チーム名
            
        Returns:
            統合分析結果の辞書
        """
        # 各動画を分析
        analyses = []
        for i, video_path in enumerate(video_paths):
            print(f"動画 {i+1}/{len(video_paths)} を分析中: {video_path}")
            analysis = self.analyze_video(video_path, player_name, team_name)
            analyses.append({
                "video": video_path,
                "analysis": analysis
            })
        
        # 統合分析を実行
        integration_prompt = f"""
以下は同じ選手（{player_name}）の複数の試合動画の分析結果です。
これらを統合し、選手の総合的な評価を作成してください。

【各動画の分析結果】
{json.dumps(analyses, ensure_ascii=False, indent=2)}

【統合分析の出力項目】
1. 一貫した強み
2. 一貫した弱点
3. 試合による変動が大きい点
4. 総合評価
5. 最優先の改善点

JSON形式で出力してください。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": integration_prompt}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        
        try:
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                integrated = json.loads(json_str)
            else:
                integrated = {"raw_response": result_text}
        except json.JSONDecodeError:
            integrated = {"raw_response": result_text}
        
        return {
            "individual_analyses": analyses,
            "integrated_analysis": integrated
        }
    
    def generate_strategy(
        self,
        self_analysis: Dict[str, Any],
        opponent_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        試合戦略を生成
        
        Args:
            self_analysis: 自己分析結果
            opponent_analysis: 相手分析結果（オプション）
            
        Returns:
            試合戦略の辞書
        """
        opponent_info = opponent_analysis if opponent_analysis else {"note": "相手情報なし。一般的な戦略を提案。"}
        
        prompt = STRATEGY_GENERATION_PROMPT.format(
            self_analysis=json.dumps(self_analysis, ensure_ascii=False, indent=2),
            opponent_analysis=json.dumps(opponent_info, ensure_ascii=False, indent=2)
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7
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
        prompt = PRACTICE_PLAN_PROMPT.format(
            analysis=json.dumps(analysis, ensure_ascii=False, indent=2)
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7
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
    
    def analyze_opponent(
        self,
        video_path: str,
        opponent_name: str,
        opponent_team: str = ""
    ) -> Dict[str, Any]:
        """
        相手選手を分析
        
        Args:
            video_path: 動画ファイルのパス
            opponent_name: 相手選手名
            opponent_team: 相手所属チーム名
            
        Returns:
            相手分析結果の辞書
        """
        video_data = self._encode_video(video_path)
        mime_type = self._get_video_mime_type(video_path)
        
        prompt = OPPONENT_ANALYSIS_PROMPT.format(
            opponent_name=opponent_name,
            opponent_team=opponent_team
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": f"data:{mime_type};base64,{video_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.7
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
    """テスト実行用のメイン関数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python llm_analyzer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    analyzer = LLMAnalyzer()
    
    print("=== 動画分析を開始 ===")
    result = analyzer.analyze_video(video_path)
    
    print("\n=== 分析結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n=== 練習計画を生成 ===")
    practice_plan = analyzer.generate_practice_plan(result)
    print(json.dumps(practice_plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
