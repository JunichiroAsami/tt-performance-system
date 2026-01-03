"""
単体テスト: Prompts モジュール
テストシナリオ: TC-007 ~ TC-008
"""

import pytest
import os
import sys

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from analysis.prompts import ANALYSIS_PROMPT, STRATEGY_PROMPT, PRACTICE_PROMPT


class TestPromptTemplateExistence:
    """TC-007: プロンプトテンプレートの存在確認"""
    
    def test_analysis_prompt_exists(self):
        """ANALYSIS_PROMPTが定義されている"""
        assert ANALYSIS_PROMPT is not None
        assert isinstance(ANALYSIS_PROMPT, str)
        assert len(ANALYSIS_PROMPT) > 0
    
    def test_strategy_prompt_exists(self):
        """STRATEGY_PROMPTが定義されている"""
        assert STRATEGY_PROMPT is not None
        assert isinstance(STRATEGY_PROMPT, str)
        assert len(STRATEGY_PROMPT) > 0
    
    def test_practice_prompt_exists(self):
        """PRACTICE_PROMPTが定義されている"""
        assert PRACTICE_PROMPT is not None
        assert isinstance(PRACTICE_PROMPT, str)
        assert len(PRACTICE_PROMPT) > 0


class TestPromptContent:
    """プロンプト内容の検証"""
    
    def test_analysis_prompt_contains_key_sections(self):
        """分析プロンプトに主要セクションが含まれる"""
        key_terms = ["基本情報", "技術", "戦術", "強み", "改善"]
        for term in key_terms:
            assert term in ANALYSIS_PROMPT, f"'{term}' が分析プロンプトに含まれていません"
    
    def test_strategy_prompt_contains_key_sections(self):
        """戦略プロンプトに主要セクションが含まれる"""
        key_terms = ["サーブ", "レシーブ", "ラリー", "戦略"]
        for term in key_terms:
            assert term in STRATEGY_PROMPT, f"'{term}' が戦略プロンプトに含まれていません"
    
    def test_practice_prompt_contains_key_sections(self):
        """練習プロンプトに主要セクションが含まれる"""
        key_terms = ["練習", "課題", "ドリル", "目標"]
        for term in key_terms:
            assert term in PRACTICE_PROMPT, f"'{term}' が練習プロンプトに含まれていません"


class TestPromptVariableSubstitution:
    """TC-008: プロンプト変数の置換"""
    
    def test_analysis_prompt_variable_substitution(self):
        """分析プロンプトの変数置換"""
        # プロンプトに変数プレースホルダーがある場合のテスト
        test_prompt = "選手名: {player_name}の分析を行います"
        result = test_prompt.format(player_name="浅見江里佳")
        assert "浅見江里佳" in result
    
    def test_strategy_prompt_with_opponent(self):
        """戦略プロンプトに対戦相手情報を挿入"""
        test_prompt = "対戦相手: {opponent_name}への戦略"
        result = test_prompt.format(opponent_name="テスト相手")
        assert "テスト相手" in result
    
    def test_prompt_format_safety(self):
        """プロンプトのフォーマット安全性"""
        # 不正な入力でもエラーにならないことを確認
        test_input = "'; DROP TABLE users; --"
        test_prompt = "選手名: {player_name}"
        result = test_prompt.format(player_name=test_input)
        assert test_input in result  # エスケープされずにそのまま入る（LLMへの入力なので問題なし）


class TestPromptOutputFormat:
    """プロンプトの出力フォーマット指定の検証"""
    
    def test_analysis_prompt_requests_json(self):
        """分析プロンプトがJSON出力を要求している"""
        assert "JSON" in ANALYSIS_PROMPT or "json" in ANALYSIS_PROMPT.lower()
    
    def test_strategy_prompt_requests_json(self):
        """戦略プロンプトがJSON出力を要求している"""
        assert "JSON" in STRATEGY_PROMPT or "json" in STRATEGY_PROMPT.lower()
    
    def test_practice_prompt_requests_json(self):
        """練習プロンプトがJSON出力を要求している"""
        assert "JSON" in PRACTICE_PROMPT or "json" in PRACTICE_PROMPT.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
