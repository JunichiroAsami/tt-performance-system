"""
スモークテスト: 実際の動画を使用してシステム全体が動作することを確認

このテストは以下を検証する:
1. 動画ファイルを読み込めること
2. フレーム抽出が成功すること
3. LLM APIへの送信が成功すること
4. 分析結果が生成されること
5. 戦略シートが生成されること
6. 練習計画が生成されること

重要: このテストは実際のAPIを呼び出すため、API費用が発生します。
"""

import pytest
import json
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# テスト用動画のパス
SMOKE_TEST_VIDEO = Path("tests/fixtures/smoke_test_video.mp4")
FALLBACK_VIDEO = Path("data/asami_match.mp4")
OUTPUT_DIR = Path("output")


class TestSmokeRealVideo:
    """実動画を使用したスモークテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト前の準備"""
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        # テスト動画の存在確認
        if SMOKE_TEST_VIDEO.exists():
            self.video_path = SMOKE_TEST_VIDEO
        elif FALLBACK_VIDEO.exists():
            self.video_path = FALLBACK_VIDEO
        else:
            pytest.skip("テスト動画が見つかりません")
    
    def test_01_video_file_exists(self):
        """動画ファイルが存在すること"""
        assert self.video_path.exists(), f"動画ファイルが存在しません: {self.video_path}"
        
        # ファイルサイズが0より大きいこと
        file_size = self.video_path.stat().st_size
        assert file_size > 0, f"動画ファイルが空です: {file_size} bytes"
        
        print(f"✅ 動画ファイル確認: {self.video_path} ({file_size / 1024 / 1024:.2f} MB)")
    
    def test_02_video_analysis_completes(self):
        """動画分析が完了すること"""
        from src.analysis.video_analyzer import VideoAnalyzer
        
        analyzer = VideoAnalyzer()
        result = analyzer.analyze(str(self.video_path))
        
        # 結果がNoneでないこと
        assert result is not None, "分析結果がNoneです"
        
        # 必須フィールドが存在すること
        assert "基本情報" in result, "基本情報が存在しません"
        assert "技術評価" in result, "技術評価が存在しません"
        assert "戦術分析" in result, "戦術分析が存在しません"
        
        # 結果を保存
        output_path = OUTPUT_DIR / "analysis_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析結果を保存: {output_path}")
        print(f"   - 基本情報: {result.get('基本情報', {})}")
    
    def test_03_strategy_generation_completes(self):
        """戦略シート生成が完了すること"""
        from src.strategy.generator import StrategyGenerator
        
        # 分析結果を読み込み
        analysis_path = OUTPUT_DIR / "analysis_result.json"
        assert analysis_path.exists(), "分析結果ファイルが存在しません（test_02が先に実行される必要があります）"
        
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        generator = StrategyGenerator()
        result = generator.generate(analysis)
        
        # 結果がNoneでないこと
        assert result is not None, "戦略シートがNoneです"
        
        # 結果を保存
        output_path = OUTPUT_DIR / "strategy_sheet.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 戦略シートを保存: {output_path}")
    
    def test_04_practice_plan_generation_completes(self):
        """練習計画生成が完了すること"""
        from src.practice.planner import PracticePlanner
        
        # 分析結果を読み込み
        analysis_path = OUTPUT_DIR / "analysis_result.json"
        assert analysis_path.exists(), "分析結果ファイルが存在しません"
        
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        planner = PracticePlanner()
        result = planner.generate(analysis)
        
        # 結果がNoneでないこと
        assert result is not None, "練習計画がNoneです"
        
        # 結果を保存
        output_path = OUTPUT_DIR / "practice_plan.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 練習計画を保存: {output_path}")
    
    def test_05_output_quality_basic(self):
        """出力の基本品質を確認"""
        # 分析結果の品質確認
        analysis_path = OUTPUT_DIR / "analysis_result.json"
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        # 利き手が有効な値であること
        basic_info = analysis.get("基本情報", {})
        dominant_hand = basic_info.get("利き手", "")
        assert dominant_hand in ["右", "左"], f"利き手が不正: {dominant_hand}"
        print(f"✅ 利き手: {dominant_hand}")
        
        # グリップが有効な値であること
        grip = basic_info.get("グリップ", "")
        valid_grips = ["シェークハンド", "ペンホルダー", "シェイクハンド"]
        assert grip in valid_grips, f"グリップが不正: {grip}"
        print(f"✅ グリップ: {grip}")
        
        # 技術評価が存在すること
        tech_eval = analysis.get("技術評価", {})
        assert len(tech_eval) > 0, "技術評価が空です"
        print(f"✅ 技術評価項目数: {len(tech_eval)}")
        
        # 戦術分析が存在すること
        tactics = analysis.get("戦術分析", {})
        assert len(tactics) > 0, "戦術分析が空です"
        print(f"✅ 戦術分析項目数: {len(tactics)}")
    
    def test_06_output_files_are_valid_json(self):
        """出力ファイルが有効なJSONであること"""
        output_files = [
            "analysis_result.json",
            "strategy_sheet.json",
            "practice_plan.json"
        ]
        
        for filename in output_files:
            filepath = OUTPUT_DIR / filename
            assert filepath.exists(), f"{filename}が存在しません"
            
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    assert data is not None, f"{filename}の内容がNoneです"
                    print(f"✅ {filename}: 有効なJSON ({len(str(data))} chars)")
                except json.JSONDecodeError as e:
                    pytest.fail(f"{filename}が無効なJSONです: {e}")
    
    def test_07_evidence_summary(self):
        """エビデンスサマリーを生成"""
        evidence = {
            "test_type": "smoke_test",
            "video_path": str(self.video_path),
            "video_size_mb": self.video_path.stat().st_size / 1024 / 1024,
            "outputs": {}
        }
        
        for filename in ["analysis_result.json", "strategy_sheet.json", "practice_plan.json"]:
            filepath = OUTPUT_DIR / filename
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                evidence["outputs"][filename] = {
                    "exists": True,
                    "size_bytes": filepath.stat().st_size,
                    "keys": list(data.keys()) if isinstance(data, dict) else "N/A"
                }
        
        # エビデンスを保存
        evidence_path = OUTPUT_DIR / "smoke_test_evidence.json"
        with open(evidence_path, "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print("スモークテスト エビデンスサマリー")
        print(f"{'='*60}")
        print(f"動画: {evidence['video_path']}")
        print(f"サイズ: {evidence['video_size_mb']:.2f} MB")
        print(f"出力ファイル:")
        for name, info in evidence["outputs"].items():
            print(f"  - {name}: {info['size_bytes']} bytes")
        print(f"{'='*60}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])
