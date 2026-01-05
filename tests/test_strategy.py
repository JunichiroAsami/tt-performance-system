"""
StrategyGeneratorのテスト

TDD Step 3: 分析結果から戦略シートを生成するテスト
"""
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.strategy import StrategyGenerator

# テスト用の分析結果（実際の分析結果を使用）
EVIDENCE_PATH = "tests/evidence/analyzer_test_evidence.json"


class TestStrategyGenerator:
    """StrategyGeneratorのテストクラス"""
    
    @pytest.fixture(scope="class")
    def analysis_result(self):
        """実際の分析結果を読み込む"""
        if os.path.exists(EVIDENCE_PATH):
            with open(EVIDENCE_PATH, "r", encoding="utf-8") as f:
                evidence = json.load(f)
                return evidence["output"]
        else:
            pytest.skip("分析結果のエビデンスが見つかりません")
    
    @pytest.fixture(scope="class")
    def generator(self):
        """テスト用のGeneratorインスタンス"""
        return StrategyGenerator()
    
    @pytest.fixture(scope="class")
    def strategy_result(self, generator, analysis_result):
        """戦略シートの生成結果（クラス内で共有）"""
        return generator.generate(analysis_result)
    
    # ============================================
    # 動作確認テスト
    # ============================================
    
    def test_generator_can_be_instantiated(self, generator):
        """Generatorがインスタンス化できること"""
        assert generator is not None
        assert hasattr(generator, 'generate')
    
    def test_generate_returns_dict(self, strategy_result):
        """生成結果が辞書型で返ること"""
        assert isinstance(strategy_result, dict), "生成結果は辞書型である必要があります"
    
    def test_generate_does_not_have_parse_error(self, strategy_result):
        """生成結果がJSONとして正常にパースされていること"""
        assert "parse_error" not in strategy_result, "JSONパースエラーが発生しました"
    
    # ============================================
    # 品質テスト（戦略シートの内容検証）
    # ============================================
    
    def test_has_serve_strategy(self, strategy_result):
        """サーブ戦略が含まれていること"""
        assert "サーブ戦略" in strategy_result, "サーブ戦略が含まれていません"
        serve = strategy_result["サーブ戦略"]
        
        # 序盤・中盤・終盤の戦略があること
        phases = ["序盤", "中盤", "終盤"]
        for phase in phases:
            assert phase in serve, f"{phase}のサーブ戦略が含まれていません"
    
    def test_serve_strategy_has_details(self, strategy_result):
        """サーブ戦略に推奨サーブと狙いが含まれていること"""
        serve = strategy_result["サーブ戦略"]
        
        for phase, content in serve.items():
            if isinstance(content, dict):
                assert "推奨サーブ" in content or "狙い" in content, \
                    f"{phase}のサーブ戦略に詳細がありません"
    
    def test_has_receive_strategy(self, strategy_result):
        """レシーブ戦略が含まれていること"""
        assert "レシーブ戦略" in strategy_result, "レシーブ戦略が含まれていません"
        receive = strategy_result["レシーブ戦略"]
        
        # 少なくとも1つの戦略があること
        assert len(receive) >= 1, "レシーブ戦略が空です"
    
    def test_has_rally_strategy(self, strategy_result):
        """ラリー戦略が含まれていること"""
        assert "ラリー戦略" in strategy_result, "ラリー戦略が含まれていません"
        rally = strategy_result["ラリー戦略"]
        
        # 基本方針があること
        assert "基本方針" in rally, "ラリー戦略に基本方針がありません"
    
    def test_rally_strategy_has_scoring_patterns(self, strategy_result):
        """ラリー戦略に得点パターンが含まれていること"""
        rally = strategy_result["ラリー戦略"]
        
        assert "得点パターン" in rally, "ラリー戦略に得点パターンがありません"
        patterns = rally["得点パターン"]
        assert len(patterns) >= 1, "得点パターンが1つ以上必要です"
    
    def test_has_mental_strategy(self, strategy_result):
        """メンタル戦略が含まれていること"""
        assert "メンタル" in strategy_result, "メンタル戦略が含まれていません"
    
    def test_has_one_point_advice(self, strategy_result):
        """ワンポイントアドバイスが含まれていること"""
        assert "ワンポイントアドバイス" in strategy_result, "ワンポイントアドバイスが含まれていません"
        advice = strategy_result["ワンポイントアドバイス"]
        assert len(advice) >= 10, "ワンポイントアドバイスが短すぎます"
    
    def test_strategy_uses_table_tennis_terms(self, strategy_result):
        """戦略シートに卓球用語が含まれていること"""
        # 全体をテキスト化
        text = json.dumps(strategy_result, ensure_ascii=False)
        
        # 卓球用語のリスト
        tt_terms = ["サーブ", "レシーブ", "ドライブ", "スマッシュ", "ブロック", 
                    "カット", "ツッツキ", "フリック", "チキータ", "ストップ",
                    "フォア", "バック", "回転", "ラリー", "攻撃"]
        
        found_terms = [term for term in tt_terms if term in text]
        assert len(found_terms) >= 5, f"卓球用語が少なすぎます: {found_terms}"
    
    def test_strategy_is_concise(self, strategy_result):
        """戦略シートがA4一枚程度の分量であること"""
        text = json.dumps(strategy_result, ensure_ascii=False)
        
        # 日本語で約2000-3000文字がA4一枚程度
        assert len(text) <= 5000, f"戦略シートが長すぎます: {len(text)}文字"
        assert len(text) >= 500, f"戦略シートが短すぎます: {len(text)}文字"
    
    # ============================================
    # エビデンス出力
    # ============================================
    
    def test_save_evidence(self, strategy_result, analysis_result):
        """テストエビデンスを保存"""
        evidence = {
            "test_name": "StrategyGenerator戦略生成テスト",
            "input": {
                "analysis_result": analysis_result
            },
            "output": strategy_result,
            "validations": {
                "has_serve_strategy": "サーブ戦略" in strategy_result,
                "has_receive_strategy": "レシーブ戦略" in strategy_result,
                "has_rally_strategy": "ラリー戦略" in strategy_result,
                "has_mental": "メンタル" in strategy_result,
                "has_advice": "ワンポイントアドバイス" in strategy_result,
                "no_parse_error": "parse_error" not in strategy_result,
                "character_count": len(json.dumps(strategy_result, ensure_ascii=False))
            }
        }
        
        # エビデンスを保存
        os.makedirs("tests/evidence", exist_ok=True)
        with open("tests/evidence/strategy_test_evidence.json", "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
        
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
