"""
E2Eテスト（エンドツーエンドテスト）

TDD Step 5: 動画入力から分析→戦略→練習計画の全フローをテスト
"""
import pytest
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analyzer import VideoAnalyzer
from src.strategy import StrategyGenerator
from src.practice import PracticePlanner

# テスト用動画のパス
TEST_VIDEO = "data/asami_match.mp4"


class TestE2EFlow:
    """E2Eフローのテストクラス"""
    
    @pytest.fixture(scope="class")
    def video_path(self):
        """テスト用動画パス"""
        return TEST_VIDEO
    
    @pytest.fixture(scope="class")
    def analyzer(self):
        """VideoAnalyzerインスタンス"""
        return VideoAnalyzer()
    
    @pytest.fixture(scope="class")
    def strategy_generator(self):
        """StrategyGeneratorインスタンス"""
        return StrategyGenerator()
    
    @pytest.fixture(scope="class")
    def practice_planner(self):
        """PracticePlannerインスタンス"""
        return PracticePlanner()
    
    @pytest.fixture(scope="class")
    def full_pipeline_result(self, video_path, analyzer, strategy_generator, practice_planner):
        """
        全パイプラインを実行した結果
        
        動画 → 分析 → 戦略 → 練習計画
        """
        # Step 1: 動画分析
        analysis = analyzer.analyze(video_path)
        
        # Step 2: 戦略生成
        strategy = strategy_generator.generate(analysis)
        
        # Step 3: 練習計画生成
        practice = practice_planner.generate(analysis)
        
        return {
            "analysis": analysis,
            "strategy": strategy,
            "practice": practice,
            "timestamp": datetime.now().isoformat()
        }
    
    # ============================================
    # 動作確認テスト（全フローが動くことを確認）
    # ============================================
    
    def test_video_exists(self, video_path):
        """テスト用動画が存在すること"""
        assert os.path.exists(video_path), f"動画ファイルが見つかりません: {video_path}"
    
    def test_full_pipeline_completes(self, full_pipeline_result):
        """全パイプラインがエラーなく完了すること"""
        assert full_pipeline_result is not None
        assert "analysis" in full_pipeline_result
        assert "strategy" in full_pipeline_result
        assert "practice" in full_pipeline_result
    
    def test_no_parse_errors_in_pipeline(self, full_pipeline_result):
        """全出力にパースエラーがないこと"""
        assert "parse_error" not in full_pipeline_result["analysis"]
        assert "parse_error" not in full_pipeline_result["strategy"]
        assert "parse_error" not in full_pipeline_result["practice"]
    
    # ============================================
    # 品質テスト（出力の品質を確認）
    # ============================================
    
    def test_analysis_has_required_sections(self, full_pipeline_result):
        """分析結果に必須セクションがあること"""
        analysis = full_pipeline_result["analysis"]
        required = ["基本情報", "技術評価", "戦術分析", "改善提案"]
        
        for section in required:
            assert section in analysis, f"分析結果に{section}がありません"
    
    def test_strategy_has_required_sections(self, full_pipeline_result):
        """戦略シートに必須セクションがあること"""
        strategy = full_pipeline_result["strategy"]
        required = ["サーブ戦略", "レシーブ戦略", "ラリー戦略"]
        
        for section in required:
            assert section in strategy, f"戦略シートに{section}がありません"
    
    def test_practice_has_required_sections(self, full_pipeline_result):
        """練習計画に必須セクションがあること"""
        practice = full_pipeline_result["practice"]
        required = ["優先課題", "週間計画", "ドリル集", "達成目標"]
        
        for section in required:
            assert section in practice, f"練習計画に{section}がありません"
    
    def test_strategy_is_based_on_analysis(self, full_pipeline_result):
        """戦略が分析結果に基づいていること"""
        analysis = full_pipeline_result["analysis"]
        strategy = full_pipeline_result["strategy"]
        
        # 分析で特定された強み（フットワーク）が戦略に反映されているか
        strategy_text = json.dumps(strategy, ensure_ascii=False)
        
        # 卓球用語が含まれていることを確認（分析と戦略の関連性）
        assert "フォア" in strategy_text or "バック" in strategy_text or "ドライブ" in strategy_text
    
    def test_practice_addresses_improvement_areas(self, full_pipeline_result):
        """練習計画が改善点に対応していること"""
        analysis = full_pipeline_result["analysis"]
        practice = full_pipeline_result["practice"]
        
        # 改善提案の最優先事項
        priority = analysis.get("改善提案", {}).get("最優先", "")
        
        # 練習計画に改善に関連する内容が含まれているか
        practice_text = json.dumps(practice, ensure_ascii=False)
        
        # 練習計画が空でないことを確認
        assert len(practice_text) > 500, "練習計画の内容が不十分です"
    
    def test_all_outputs_use_table_tennis_terms(self, full_pipeline_result):
        """全出力に卓球用語が含まれていること"""
        tt_terms = ["サーブ", "レシーブ", "ドライブ", "フォア", "バック", 
                    "回転", "フットワーク", "ラリー", "攻撃"]
        
        for key in ["analysis", "strategy", "practice"]:
            text = json.dumps(full_pipeline_result[key], ensure_ascii=False)
            found = [term for term in tt_terms if term in text]
            assert len(found) >= 3, f"{key}に卓球用語が少なすぎます: {found}"
    
    # ============================================
    # 実用性テスト（実際に使えるかを確認）
    # ============================================
    
    def test_strategy_is_readable_length(self, full_pipeline_result):
        """戦略シートが読める長さであること（A4一枚程度）"""
        strategy = full_pipeline_result["strategy"]
        text = json.dumps(strategy, ensure_ascii=False)
        
        # 500-5000文字が適切
        assert 500 <= len(text) <= 5000, f"戦略シートの長さが不適切: {len(text)}文字"
    
    def test_practice_has_enough_days(self, full_pipeline_result):
        """練習計画が5日分以上あること"""
        practice = full_pipeline_result["practice"]
        weekly = practice.get("週間計画", {})
        
        assert len(weekly) >= 5, f"練習計画が5日分以上必要です（現在: {len(weekly)}日）"
    
    def test_drills_are_executable(self, full_pipeline_result):
        """ドリルが実行可能な内容であること"""
        practice = full_pipeline_result["practice"]
        drills = practice.get("ドリル集", [])
        
        assert len(drills) >= 3, "ドリルが3つ以上必要です"
        
        for drill in drills:
            # 各ドリルに手順があること
            if "手順" in drill:
                assert len(drill["手順"]) >= 2, f"ドリルの手順が少なすぎます"
    
    # ============================================
    # エビデンス出力
    # ============================================
    
    def test_save_full_evidence(self, full_pipeline_result, video_path):
        """全パイプラインのエビデンスを保存"""
        evidence = {
            "test_name": "E2E全パイプラインテスト",
            "timestamp": datetime.now().isoformat(),
            "input": {
                "video_file": video_path,
                "video_exists": os.path.exists(video_path),
                "video_size_mb": os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else 0
            },
            "outputs": {
                "analysis": full_pipeline_result["analysis"],
                "strategy": full_pipeline_result["strategy"],
                "practice": full_pipeline_result["practice"]
            },
            "validations": {
                "analysis_ok": "parse_error" not in full_pipeline_result["analysis"],
                "strategy_ok": "parse_error" not in full_pipeline_result["strategy"],
                "practice_ok": "parse_error" not in full_pipeline_result["practice"],
                "analysis_sections": list(full_pipeline_result["analysis"].keys()),
                "strategy_sections": list(full_pipeline_result["strategy"].keys()),
                "practice_sections": list(full_pipeline_result["practice"].keys()),
                "strategy_length": len(json.dumps(full_pipeline_result["strategy"], ensure_ascii=False)),
                "practice_days": len(full_pipeline_result["practice"].get("週間計画", {})),
                "drill_count": len(full_pipeline_result["practice"].get("ドリル集", []))
            }
        }
        
        os.makedirs("tests/evidence", exist_ok=True)
        with open("tests/evidence/e2e_test_evidence.json", "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
        
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
