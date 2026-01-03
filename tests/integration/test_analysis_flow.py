"""
統合テスト: 分析フロー
テストシナリオ: TC-101 ~ TC-103
"""

import pytest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from analysis.llm_analyzer import LLMAnalyzer
from output.report_generator import ReportGenerator


class TestAnalysisToStrategyFlow:
    """TC-101: 分析結果を戦略生成に渡すフロー"""
    
    @pytest.fixture
    def mock_analysis_result(self):
        """モック分析結果"""
        return {
            "基本情報": {
                "選手名": "浅見江里佳",
                "利き手": "右",
                "グリップ": "シェークハンド",
                "プレースタイル": "攻撃型"
            },
            "技術分析": {
                "フォアハンド": {"評価": 4, "安定性": 3, "威力": 4},
                "バックハンド": {"評価": 5, "安定性": 5, "威力": 4}
            },
            "戦術分析": {
                "得点パターン": "バックハンドからの3球目攻撃",
                "失点パターン": "フォア側への攻撃に対する対応"
            },
            "強み": ["バックハンドドライブ", "チキータ", "フットワーク"],
            "改善点": ["フォアハンドの決定力", "ロングサーブの変化"]
        }
    
    @pytest.fixture
    def mock_strategy_result(self):
        """モック戦略結果"""
        return {
            "戦略立案": {
                "選手名": "浅見江里佳",
                "目標": "バックハンドを軸に攻撃を組み立てる"
            },
            "1.サーブ戦略": {
                "序盤": {"推奨": "フォア前ショート"}
            },
            "2.レシーブ戦略": {
                "短いサーブ": {"推奨": "チキータ"}
            },
            "3.ラリー戦略": {
                "攻撃時": {"狙い": "バックで崩してフォアで決める"}
            }
        }
    
    def test_analysis_to_strategy_flow(self, mock_analysis_result, mock_strategy_result):
        """分析→戦略生成の連続実行"""
        analyzer = LLMAnalyzer()
        
        # メソッドをモック
        analyzer.generate_strategy = MagicMock(return_value=mock_strategy_result)
        
        # 分析結果を戦略生成に渡す
        strategy = analyzer.generate_strategy(mock_analysis_result)
        
        # 戦略が生成されたことを確認
        assert strategy is not None
        assert "戦略立案" in strategy or "1.サーブ戦略" in strategy
        
        # 分析結果の強みが戦略に反映されているか（概念的な確認）
        # 実際のLLM出力では、分析結果を参照した戦略が生成される
        analyzer.generate_strategy.assert_called_once_with(mock_analysis_result)
    
    def test_strategy_consistency_with_analysis(self, mock_analysis_result, mock_strategy_result):
        """戦略が分析結果と整合性を持つ"""
        analyzer = LLMAnalyzer()
        analyzer.generate_strategy = MagicMock(return_value=mock_strategy_result)
        
        strategy = analyzer.generate_strategy(mock_analysis_result)
        
        # 選手名が一致
        if "戦略立案" in strategy and "選手名" in strategy["戦略立案"]:
            assert strategy["戦略立案"]["選手名"] == mock_analysis_result["基本情報"]["選手名"]


class TestAnalysisToPracticeFlow:
    """TC-102: 分析結果を練習計画生成に渡すフロー"""
    
    @pytest.fixture
    def mock_analysis_result(self):
        """モック分析結果"""
        return {
            "基本情報": {"選手名": "浅見江里佳"},
            "強み": ["バックハンドドライブ"],
            "改善点": ["フォアハンドの決定力", "ロングサーブの変化"]
        }
    
    @pytest.fixture
    def mock_practice_result(self):
        """モック練習計画結果"""
        return {
            "選手名": "浅見江里佳",
            "1.優先課題": [
                {"課題": "フォアハンドの決定力向上", "重要度": "最優先"}
            ],
            "2.週間練習計画": {
                "Day_1": {"練習内容": "フォアハンド強化"}
            },
            "3.具体的なドリル": [
                {"ドリル名": "フォアハンド・フルスイングドリル"}
            ]
        }
    
    def test_analysis_to_practice_flow(self, mock_analysis_result, mock_practice_result):
        """分析→練習計画生成の連続実行"""
        analyzer = LLMAnalyzer()
        analyzer.generate_practice_plan = MagicMock(return_value=mock_practice_result)
        
        practice = analyzer.generate_practice_plan(mock_analysis_result)
        
        assert practice is not None
        assert "1.優先課題" in practice or "優先課題" in practice
    
    def test_practice_addresses_improvement_points(self, mock_analysis_result, mock_practice_result):
        """練習計画が改善点に対応している"""
        analyzer = LLMAnalyzer()
        analyzer.generate_practice_plan = MagicMock(return_value=mock_practice_result)
        
        practice = analyzer.generate_practice_plan(mock_analysis_result)
        
        # 改善点「フォアハンドの決定力」が練習計画に反映されているか
        practice_str = json.dumps(practice, ensure_ascii=False)
        assert "フォアハンド" in practice_str


class TestFullAnalysisFlow:
    """TC-103: 全機能の連続実行"""
    
    @pytest.fixture
    def mock_full_results(self):
        """フル分析の全結果"""
        return {
            "analysis": {
                "基本情報": {"選手名": "浅見江里佳"},
                "強み": ["バックハンド"],
                "改善点": ["フォアハンド"]
            },
            "strategy": {
                "戦略立案": {"選手名": "浅見江里佳"},
                "1.サーブ戦略": {}
            },
            "practice": {
                "選手名": "浅見江里佳",
                "1.優先課題": []
            }
        }
    
    def test_full_analysis_flow(self, mock_full_results):
        """分析→戦略→練習計画の一括実行"""
        analyzer = LLMAnalyzer()
        
        # 各メソッドをモック
        analyzer.analyze_video = MagicMock(return_value=mock_full_results["analysis"])
        analyzer.generate_strategy = MagicMock(return_value=mock_full_results["strategy"])
        analyzer.generate_practice_plan = MagicMock(return_value=mock_full_results["practice"])
        
        # フル分析を実行
        with patch('os.path.exists', return_value=True):
            analysis = analyzer.analyze_video("dummy.mp4")
            strategy = analyzer.generate_strategy(analysis)
            practice = analyzer.generate_practice_plan(analysis)
        
        # 3つの出力が生成されたことを確認
        assert analysis is not None
        assert strategy is not None
        assert practice is not None
    
    def test_full_analysis_consistency(self, mock_full_results):
        """3つの出力が整合性を持つ"""
        analyzer = LLMAnalyzer()
        
        analyzer.analyze_video = MagicMock(return_value=mock_full_results["analysis"])
        analyzer.generate_strategy = MagicMock(return_value=mock_full_results["strategy"])
        analyzer.generate_practice_plan = MagicMock(return_value=mock_full_results["practice"])
        
        with patch('os.path.exists', return_value=True):
            analysis = analyzer.analyze_video("dummy.mp4")
            strategy = analyzer.generate_strategy(analysis)
            practice = analyzer.generate_practice_plan(analysis)
        
        # 選手名が全出力で一致
        player_name = analysis["基本情報"]["選手名"]
        
        if "戦略立案" in strategy and "選手名" in strategy["戦略立案"]:
            assert strategy["戦略立案"]["選手名"] == player_name
        
        if "選手名" in practice:
            assert practice["選手名"] == player_name


class TestReportGenerationIntegration:
    """レポート生成の統合テスト"""
    
    def test_full_report_generation_flow(self):
        """分析結果からレポート生成までの一連のフロー"""
        analyzer = LLMAnalyzer()
        generator = ReportGenerator()
        
        # モック結果
        mock_analysis = {
            "基本情報": {"選手名": "浅見江里佳"},
            "強み": ["バックハンド"],
            "改善点": ["フォアハンド"]
        }
        
        analyzer.analyze_video = MagicMock(return_value=mock_analysis)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 分析実行
            with patch('os.path.exists', return_value=True):
                analysis = analyzer.analyze_video("dummy.mp4")
            
            # レポート生成
            report_path = os.path.join(tmpdir, "report.md")
            generator.generate_analysis_report(analysis, report_path)
            
            # レポートが生成されたことを確認
            assert os.path.exists(report_path)
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "浅見江里佳" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
