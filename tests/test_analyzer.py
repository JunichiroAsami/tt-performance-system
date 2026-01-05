"""
VideoAnalyzerのテスト

TDD Step 2: 実際の動画を使用してテストを行う
"""
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analyzer import VideoAnalyzer

# テスト用動画のパス
TEST_VIDEO = "data/asami_match.mp4"


class TestVideoAnalyzer:
    """VideoAnalyzerのテストクラス"""
    
    @pytest.fixture(scope="class")
    def analyzer(self):
        """テスト用のAnalyzerインスタンス"""
        return VideoAnalyzer()
    
    @pytest.fixture(scope="class")
    def analysis_result(self, analyzer):
        """
        実際の動画を分析した結果（クラス内で共有）
        注: このテストは実際にAPIを呼び出すため、時間がかかる
        """
        return analyzer.analyze(TEST_VIDEO)
    
    # ============================================
    # 動作確認テスト（システムが動くことを確認）
    # ============================================
    
    def test_video_file_exists(self):
        """テスト用動画ファイルが存在すること"""
        assert os.path.exists(TEST_VIDEO), f"動画ファイルが見つかりません: {TEST_VIDEO}"
    
    def test_analyzer_can_be_instantiated(self, analyzer):
        """Analyzerがインスタンス化できること"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_analyze_returns_dict(self, analysis_result):
        """分析結果が辞書型で返ること"""
        assert isinstance(analysis_result, dict), "分析結果は辞書型である必要があります"
    
    def test_analyze_does_not_have_parse_error(self, analysis_result):
        """分析結果がJSONとして正常にパースされていること"""
        assert "parse_error" not in analysis_result, "JSONパースエラーが発生しました"
    
    # ============================================
    # 品質テスト（出力内容の品質を確認）
    # ============================================
    
    def test_has_basic_info(self, analysis_result):
        """基本情報が含まれていること"""
        assert "基本情報" in analysis_result, "基本情報が含まれていません"
        basic = analysis_result["基本情報"]
        
        assert "利き手" in basic, "利き手が含まれていません"
        assert "グリップ" in basic, "グリップが含まれていません"
        assert "プレースタイル" in basic, "プレースタイルが含まれていません"
    
    def test_basic_info_values_are_valid(self, analysis_result):
        """基本情報の値が妥当であること"""
        basic = analysis_result["基本情報"]
        
        # 利き手は「右」または「左」
        assert basic["利き手"] in ["右", "左"], f"利き手の値が不正: {basic['利き手']}"
        
        # グリップは「シェークハンド」または「ペンホルダー」を含む
        grip = basic["グリップ"]
        assert "シェーク" in grip or "ペン" in grip, f"グリップの値が不正: {grip}"
    
    def test_has_tech_evaluation(self, analysis_result):
        """技術評価が含まれていること"""
        assert "技術評価" in analysis_result, "技術評価が含まれていません"
        tech = analysis_result["技術評価"]
        
        required_skills = ["フォアハンド", "バックハンド", "サーブ", "レシーブ", "フットワーク"]
        for skill in required_skills:
            assert skill in tech, f"{skill}の評価が含まれていません"
    
    def test_tech_scores_are_valid(self, analysis_result):
        """技術評価のスコアが1-5の範囲であること"""
        tech = analysis_result["技術評価"]
        
        for skill, evaluation in tech.items():
            if isinstance(evaluation, dict) and "スコア" in evaluation:
                score = evaluation["スコア"]
                assert 1 <= score <= 5, f"{skill}のスコアが範囲外: {score}"
    
    def test_has_tactics_analysis(self, analysis_result):
        """戦術分析が含まれていること"""
        assert "戦術分析" in analysis_result, "戦術分析が含まれていません"
        tactics = analysis_result["戦術分析"]
        
        assert "得点パターン" in tactics, "得点パターンが含まれていません"
        assert "失点パターン" in tactics, "失点パターンが含まれていません"
    
    def test_scoring_patterns_are_specific(self, analysis_result):
        """得点パターンが具体的であること（卓球用語を含む）"""
        tactics = analysis_result["戦術分析"]
        patterns = tactics.get("得点パターン", [])
        
        assert len(patterns) >= 1, "得点パターンが1つ以上必要です"
        
        # 卓球用語のリスト
        tt_terms = ["サーブ", "レシーブ", "ドライブ", "スマッシュ", "ブロック", 
                    "カット", "ツッツキ", "フリック", "チキータ", "ストップ",
                    "フォア", "バック", "3球目", "4球目", "攻撃", "回転"]
        
        # 少なくとも1つのパターンに卓球用語が含まれていること
        has_tt_term = False
        for pattern in patterns:
            if any(term in pattern for term in tt_terms):
                has_tt_term = True
                break
        
        assert has_tt_term, f"得点パターンに卓球用語が含まれていません: {patterns}"
    
    def test_has_improvement_suggestions(self, analysis_result):
        """改善提案が含まれていること"""
        assert "改善提案" in analysis_result, "改善提案が含まれていません"
        suggestions = analysis_result["改善提案"]
        
        assert "最優先" in suggestions, "最優先の改善提案が含まれていません"
    
    def test_improvement_suggestions_are_actionable(self, analysis_result):
        """改善提案が具体的で実行可能であること"""
        suggestions = analysis_result["改善提案"]
        priority = suggestions.get("最優先", "")
        
        # 最優先の改善提案が10文字以上であること（具体的な内容）
        assert len(priority) >= 10, f"最優先の改善提案が短すぎます: {priority}"
    
    # ============================================
    # エビデンス出力
    # ============================================
    
    def test_save_evidence(self, analysis_result):
        """テストエビデンスを保存"""
        evidence = {
            "test_name": "VideoAnalyzer分析テスト",
            "input": {
                "video_file": TEST_VIDEO,
                "video_exists": os.path.exists(TEST_VIDEO)
            },
            "output": analysis_result,
            "validations": {
                "has_basic_info": "基本情報" in analysis_result,
                "has_tech_evaluation": "技術評価" in analysis_result,
                "has_tactics": "戦術分析" in analysis_result,
                "has_suggestions": "改善提案" in analysis_result,
                "no_parse_error": "parse_error" not in analysis_result
            }
        }
        
        # エビデンスを保存
        os.makedirs("tests/evidence", exist_ok=True)
        with open("tests/evidence/analyzer_test_evidence.json", "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
        
        assert True  # エビデンス保存成功


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
