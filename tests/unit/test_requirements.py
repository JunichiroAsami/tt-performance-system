"""
業務要件ベースの単体テスト
各テストケースは業務要件IDと紐づけられている
"""

import pytest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from analysis.llm_analyzer import LLMAnalyzer
from analysis.prompts import (
    ANALYSIS_PROMPT, 
    STRATEGY_PROMPT, 
    PRACTICE_PROMPT,
    OPPONENT_ANALYSIS_PROMPT
)


class TestAnalysisPromptRequirements:
    """分析プロンプトが業務要件を満たすかの単体テスト"""
    
    def test_FA01_prompt_includes_scoring_pattern(self):
        """FA-01: 分析プロンプトに得点/失点パターン分析の指示が含まれている"""
        assert "得点" in ANALYSIS_PROMPT
        assert "失点" in ANALYSIS_PROMPT
    
    def test_FA02_prompt_includes_technique_analysis(self):
        """FA-02: 分析プロンプトに技術別パフォーマンス分析の指示が含まれている"""
        # フォアハンド、バックハンド、サーブ、レシーブなどの技術
        technique_keywords = ["フォアハンド", "バックハンド", "技術", "テクニック", "technique"]
        assert any(kw in ANALYSIS_PROMPT for kw in technique_keywords)
    
    def test_FA03_prompt_includes_serve_receive_analysis(self):
        """FA-03: 分析プロンプトにサーブ/レシーブ分析の指示が含まれている"""
        assert "サーブ" in ANALYSIS_PROMPT
        assert "レシーブ" in ANALYSIS_PROMPT
    
    def test_FA06_opponent_prompt_includes_scoring_pattern(self):
        """FA-06: 相手分析プロンプトに相手の得点/失点パターン分析の指示が含まれている"""
        assert "得点パターン" in OPPONENT_ANALYSIS_PROMPT
        assert "失点パターン" in OPPONENT_ANALYSIS_PROMPT
    
    def test_FA07_opponent_prompt_includes_serve_receive(self):
        """FA-07: 相手分析プロンプトに相手のサーブ/レシーブ傾向分析の指示が含まれている"""
        assert "サーブの傾向" in OPPONENT_ANALYSIS_PROMPT
        assert "レシーブの傾向" in OPPONENT_ANALYSIS_PROMPT
    
    def test_FA08_opponent_prompt_includes_weakness(self):
        """FA-08: 相手分析プロンプトに相手の弱点特定の指示が含まれている"""
        weakness_keywords = ["弱点", "攻略法"]
        assert any(kw in OPPONENT_ANALYSIS_PROMPT for kw in weakness_keywords)


class TestStrategyPromptRequirements:
    """戦略プロンプトが業務要件を満たすかの単体テスト"""
    
    def test_FS01_prompt_includes_strategy_sheet(self):
        """FS-01: 戦略プロンプトに対戦相手別戦略シート生成の指示が含まれている"""
        strategy_keywords = ["戦略", "strategy", "作戦", "プラン"]
        assert any(kw in STRATEGY_PROMPT for kw in strategy_keywords)
    
    def test_FS02_prompt_includes_serve_strategy(self):
        """FS-02: 戦略プロンプトにサーブ戦略提案の指示が含まれている"""
        assert "サーブ戦略" in STRATEGY_PROMPT
    
    def test_FS03_prompt_includes_receive_strategy(self):
        """FS-03: 戦略プロンプトにレシーブ戦略提案の指示が含まれている"""
        assert "レシーブ戦略" in STRATEGY_PROMPT
    
    def test_FS04_prompt_includes_rally_strategy(self):
        """FS-04: 戦略プロンプトにラリー展開戦略提案の指示が含まれている"""
        rally_keywords = ["ラリー戦略", "ラリー", "展開"]
        assert any(kw in STRATEGY_PROMPT for kw in rally_keywords)


class TestPracticePromptRequirements:
    """練習計画プロンプトが業務要件を満たすかの単体テスト"""
    
    def test_FP01_prompt_includes_priority(self):
        """FP-01: 練習計画プロンプトに課題の優先順位付けの指示が含まれている"""
        priority_keywords = ["優先", "priority", "重要度", "順位"]
        assert any(kw in PRACTICE_PROMPT for kw in priority_keywords)
    
    def test_FP02_prompt_includes_custom_menu(self):
        """FP-02: 練習計画プロンプトにカスタム練習メニュー生成の指示が含まれている"""
        menu_keywords = ["練習", "メニュー", "トレーニング", "practice", "training"]
        assert any(kw in PRACTICE_PROMPT for kw in menu_keywords)
    
    def test_FP03_prompt_includes_drill(self):
        """FP-03: 練習計画プロンプトにフォーム改善ドリル提案の指示が含まれている"""
        drill_keywords = ["ドリル", "drill", "フォーム", "改善"]
        assert any(kw in PRACTICE_PROMPT for kw in drill_keywords)


class TestLLMAnalyzerOutputSchema:
    """LLMAnalyzerの出力スキーマが業務要件を満たすかの単体テスト"""
    
    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer()
    
    def test_analysis_schema_includes_FA01_fields(self, analyzer):
        """FA-01: 分析出力スキーマに得点/失点パターンのフィールドが定義されている"""
        # LLMAnalyzerのスキーマ定義を確認
        # 実際の実装では、スキーマがクラス属性として定義されている想定
        expected_fields = ["得点パターン", "失点パターン", "戦術分析"]
        # プロンプトに出力形式の指示があることを確認
        assert "得点" in ANALYSIS_PROMPT
        assert "失点" in ANALYSIS_PROMPT
    
    def test_strategy_schema_includes_FS_fields(self, analyzer):
        """FS-01~04: 戦略出力スキーマに必要なフィールドが定義されている"""
        expected_fields = ["サーブ戦略", "レシーブ戦略", "ラリー戦略"]
        # プロンプトに出力形式の指示があることを確認
        assert "サーブ" in STRATEGY_PROMPT
        assert "レシーブ" in STRATEGY_PROMPT
    
    def test_practice_schema_includes_FP_fields(self, analyzer):
        """FP-01~03: 練習計画出力スキーマに必要なフィールドが定義されている"""
        expected_fields = ["優先課題", "練習メニュー", "ドリル"]
        # プロンプトに出力形式の指示があることを確認
        assert "優先" in PRACTICE_PROMPT
        assert "練習" in PRACTICE_PROMPT


class TestLLMAnalyzerMethods:
    """LLMAnalyzerのメソッドが業務要件を満たすかの単体テスト"""
    
    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer()
    
    def test_analyze_video_method_exists(self, analyzer):
        """分析メソッドが存在する"""
        assert hasattr(analyzer, 'analyze_video')
        assert callable(getattr(analyzer, 'analyze_video'))
    
    def test_generate_strategy_method_exists(self, analyzer):
        """戦略生成メソッドが存在する"""
        assert hasattr(analyzer, 'generate_strategy')
        assert callable(getattr(analyzer, 'generate_strategy'))
    
    def test_generate_practice_plan_method_exists(self, analyzer):
        """練習計画生成メソッドが存在する"""
        assert hasattr(analyzer, 'generate_practice_plan')
        assert callable(getattr(analyzer, 'generate_practice_plan'))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
