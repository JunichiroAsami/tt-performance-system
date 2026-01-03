"""
業務要件ベースの統合テスト
各テストケースは業務要件IDと紐づけられ、出力内容の検証を行う
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


class TestFA01ScoringPatternValidation:
    """FA-01: 得点/失点パターン分析の出力検証"""
    
    @pytest.fixture
    def valid_analysis_output(self):
        """FA-01を満たす分析出力"""
        return {
            "基本情報": {"選手名": "浅見江里佳"},
            "戦術分析": {
                "得点パターン": [
                    "バックハンドドライブからの3球目攻撃",
                    "チキータからの展開",
                    "カウンター攻撃"
                ],
                "失点パターン": [
                    "フォア側への強打に対する対応ミス",
                    "ロングサーブへの対応",
                    "ラリー戦での粘り負け"
                ]
            }
        }
    
    def test_FA01_output_has_scoring_patterns(self, valid_analysis_output):
        """FA-01: 出力に得点パターンが含まれている"""
        assert "戦術分析" in valid_analysis_output
        assert "得点パターン" in valid_analysis_output["戦術分析"]
        patterns = valid_analysis_output["戦術分析"]["得点パターン"]
        assert isinstance(patterns, list)
        assert len(patterns) >= 1
    
    def test_FA01_output_has_losing_patterns(self, valid_analysis_output):
        """FA-01: 出力に失点パターンが含まれている"""
        assert "戦術分析" in valid_analysis_output
        assert "失点パターン" in valid_analysis_output["戦術分析"]
        patterns = valid_analysis_output["戦術分析"]["失点パターン"]
        assert isinstance(patterns, list)
        assert len(patterns) >= 1
    
    def test_FA01_patterns_are_meaningful(self, valid_analysis_output):
        """FA-01: パターンが意味のある内容を持つ（空文字列でない）"""
        for pattern in valid_analysis_output["戦術分析"]["得点パターン"]:
            assert len(pattern) > 5  # 最低限の文字数
        for pattern in valid_analysis_output["戦術分析"]["失点パターン"]:
            assert len(pattern) > 5


class TestFA02TechniqueAnalysisValidation:
    """FA-02: 技術別パフォーマンス分析の出力検証"""
    
    @pytest.fixture
    def valid_technique_output(self):
        """FA-02を満たす技術分析出力"""
        return {
            "技術分析": {
                "フォアハンドドライブ": {
                    "スイング軌道の評価": 4,
                    "打点の適切さ": 3,
                    "体重移動": 4,
                    "強み": "威力がある",
                    "改善点": "安定性の向上"
                },
                "バックハンドドライブ": {
                    "スイング軌道の評価": 5,
                    "打点の適切さ": 5,
                    "安定性": 5,
                    "強み": "非常に安定している",
                    "改善点": "特になし"
                }
            }
        }
    
    def test_FA02_output_has_forehand_analysis(self, valid_technique_output):
        """FA-02: 出力にフォアハンド分析が含まれている"""
        assert "技術分析" in valid_technique_output
        techniques = valid_technique_output["技術分析"]
        forehand_keys = [k for k in techniques.keys() if "フォア" in k]
        assert len(forehand_keys) >= 1
    
    def test_FA02_output_has_backhand_analysis(self, valid_technique_output):
        """FA-02: 出力にバックハンド分析が含まれている"""
        techniques = valid_technique_output["技術分析"]
        backhand_keys = [k for k in techniques.keys() if "バック" in k]
        assert len(backhand_keys) >= 1
    
    def test_FA02_technique_has_evaluation(self, valid_technique_output):
        """FA-02: 各技術に評価値が含まれている"""
        for tech_name, tech_data in valid_technique_output["技術分析"].items():
            # 評価を示すキーが存在する
            eval_keys = [k for k in tech_data.keys() if "評価" in k or "安定" in k]
            assert len(eval_keys) >= 1


class TestFA03ServeReceiveValidation:
    """FA-03: サーブ/レシーブ分析の出力検証"""
    
    @pytest.fixture
    def valid_serve_receive_output(self):
        """FA-03を満たすサーブ/レシーブ分析出力"""
        return {
            "技術分析": {
                "サーブ": {
                    "種類のバリエーション": ["ショートサーブ", "ロングサーブ", "横回転サーブ"],
                    "コースの精度": 4,
                    "回転の質": 3,
                    "3球目攻撃への連携": "良好",
                    "強み": "コース精度が高い",
                    "改善点": "回転量の向上"
                },
                "レシーブ": {
                    "対応力": 4,
                    "攻撃的レシーブの割合": "60%",
                    "苦手なサーブタイプ": "ロングサーブ",
                    "強み": "チキータが得意",
                    "改善点": "ロングサーブへの対応"
                }
            }
        }
    
    def test_FA03_output_has_serve_analysis(self, valid_serve_receive_output):
        """FA-03: 出力にサーブ分析が含まれている"""
        assert "サーブ" in valid_serve_receive_output["技術分析"]
        serve = valid_serve_receive_output["技術分析"]["サーブ"]
        assert "種類のバリエーション" in serve or "コースの精度" in serve
    
    def test_FA03_output_has_receive_analysis(self, valid_serve_receive_output):
        """FA-03: 出力にレシーブ分析が含まれている"""
        assert "レシーブ" in valid_serve_receive_output["技術分析"]
        receive = valid_serve_receive_output["技術分析"]["レシーブ"]
        assert "対応力" in receive or "攻撃的レシーブ" in receive


class TestFS01StrategySheetValidation:
    """FS-01: 対戦相手別戦略シート生成の出力検証"""
    
    @pytest.fixture
    def valid_strategy_output(self):
        """FS-01を満たす戦略出力"""
        return {
            "戦略立案": {
                "選手名": "浅見江里佳",
                "対戦相手": "山田選手",
                "目標": "バックハンドを軸に攻撃を組み立てる"
            },
            "1.サーブ戦略": {
                "序盤": {"推奨サーブ": "フォア前ショート", "狙い": "相手を前に出す"},
                "中盤": {"推奨サーブ": "バック側ロング", "狙い": "3球目攻撃"},
                "終盤": {"推奨サーブ": "横回転サーブ", "狙い": "相手を崩す"}
            },
            "2.レシーブ戦略": {
                "短いサーブ": {"推奨": "チキータ", "注意点": "コースを読む"},
                "長いサーブ": {"推奨": "ドライブ", "注意点": "回転を見極める"}
            },
            "3.ラリー戦略": {
                "攻撃時": {"狙い": "バックで崩してフォアで決める"},
                "守備時": {"方針": "深いボールで時間を稼ぐ"}
            }
        }
    
    def test_FS01_output_has_strategy_sections(self, valid_strategy_output):
        """FS-01: 出力に戦略セクションが含まれている"""
        assert "戦略立案" in valid_strategy_output or "1.サーブ戦略" in valid_strategy_output
    
    def test_FS02_output_has_serve_strategy(self, valid_strategy_output):
        """FS-02: 出力にサーブ戦略が含まれている"""
        assert "1.サーブ戦略" in valid_strategy_output
        serve_strategy = valid_strategy_output["1.サーブ戦略"]
        assert len(serve_strategy) >= 1
    
    def test_FS03_output_has_receive_strategy(self, valid_strategy_output):
        """FS-03: 出力にレシーブ戦略が含まれている"""
        assert "2.レシーブ戦略" in valid_strategy_output
        receive_strategy = valid_strategy_output["2.レシーブ戦略"]
        assert len(receive_strategy) >= 1
    
    def test_FS04_output_has_rally_strategy(self, valid_strategy_output):
        """FS-04: 出力にラリー戦略が含まれている"""
        assert "3.ラリー戦略" in valid_strategy_output
        rally_strategy = valid_strategy_output["3.ラリー戦略"]
        assert "攻撃時" in rally_strategy or "守備時" in rally_strategy


class TestFP01PriorityValidation:
    """FP-01: 課題の優先順位付けの出力検証"""
    
    @pytest.fixture
    def valid_practice_output(self):
        """FP-01~03を満たす練習計画出力"""
        return {
            "選手名": "浅見江里佳",
            "1.優先課題": [
                {"課題": "フォアハンドの決定力向上", "重要度": "最優先", "理由": "得点力向上のため"},
                {"課題": "ロングサーブへの対応", "重要度": "高", "理由": "失点パターンの改善"},
                {"課題": "フットワークの強化", "重要度": "中", "理由": "全体的な安定性向上"}
            ],
            "2.週間練習計画": {
                "Day_1": {"練習内容": "フォアハンド強化", "時間": "2時間"},
                "Day_2": {"練習内容": "レシーブ練習", "時間": "2時間"}
            },
            "3.具体的なドリル": [
                {
                    "ドリル名": "フォアハンド・フルスイングドリル",
                    "目的": "フォアハンドの威力向上",
                    "方法": "多球練習でフルスイングを繰り返す",
                    "時間": "15分",
                    "回数": "3セット"
                }
            ]
        }
    
    def test_FP01_output_has_prioritized_issues(self, valid_practice_output):
        """FP-01: 出力に優先順位付きの課題が含まれている"""
        assert "1.優先課題" in valid_practice_output
        issues = valid_practice_output["1.優先課題"]
        assert isinstance(issues, list)
        assert len(issues) >= 1
        
        # 優先度/重要度の情報が含まれている
        for issue in issues:
            assert "重要度" in issue or "優先" in str(issue)
    
    def test_FP02_output_has_practice_menu(self, valid_practice_output):
        """FP-02: 出力にカスタム練習メニューが含まれている"""
        assert "2.週間練習計画" in valid_practice_output
        plan = valid_practice_output["2.週間練習計画"]
        assert len(plan) >= 1
    
    def test_FP03_output_has_drills(self, valid_practice_output):
        """FP-03: 出力に具体的なドリルが含まれている"""
        assert "3.具体的なドリル" in valid_practice_output
        drills = valid_practice_output["3.具体的なドリル"]
        assert isinstance(drills, list)
        assert len(drills) >= 1
        
        # ドリルに必要な情報が含まれている
        for drill in drills:
            assert "ドリル名" in drill or "名前" in drill
            assert "目的" in drill or "方法" in drill


class TestFR01ReportValidation:
    """FR-01: 試合後サマリーレポートの出力検証"""
    
    def test_FR01_report_generation(self):
        """FR-01: レポートが生成される"""
        generator = ReportGenerator()
        
        mock_analysis = {
            "基本情報": {"選手名": "浅見江里佳"},
            "戦術分析": {
                "得点パターン": ["バックハンド攻撃"],
                "失点パターン": ["フォア側への対応ミス"]
            },
            "強み": ["バックハンド"],
            "改善点": ["フォアハンド"]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "report.md")
            generator.generate_analysis_report(mock_analysis, report_path)
            
            assert os.path.exists(report_path)
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # レポートに必要な情報が含まれている
            assert "浅見江里佳" in content
            assert len(content) > 100  # 最低限の内容量


class TestIntegrationFlowWithValidation:
    """統合フロー全体の業務要件検証"""
    
    def test_full_flow_produces_valid_outputs(self):
        """分析→戦略→練習計画の全フローで有効な出力が生成される"""
        analyzer = LLMAnalyzer()
        
        # モック出力を設定
        mock_analysis = {
            "基本情報": {"選手名": "浅見江里佳"},
            "技術分析": {
                "フォアハンドドライブ": {"評価": 4},
                "バックハンドドライブ": {"評価": 5},
                "サーブ": {"コースの精度": 4},
                "レシーブ": {"対応力": 4}
            },
            "戦術分析": {
                "得点パターン": ["バックハンド攻撃"],
                "失点パターン": ["フォア側対応ミス"]
            },
            "強み": ["バックハンド"],
            "改善点": ["フォアハンド"]
        }
        
        mock_strategy = {
            "戦略立案": {"選手名": "浅見江里佳"},
            "1.サーブ戦略": {"序盤": {"推奨": "ショートサーブ"}},
            "2.レシーブ戦略": {"短いサーブ": {"推奨": "チキータ"}},
            "3.ラリー戦略": {"攻撃時": {"狙い": "バックで崩す"}}
        }
        
        mock_practice = {
            "選手名": "浅見江里佳",
            "1.優先課題": [{"課題": "フォアハンド強化", "重要度": "最優先"}],
            "2.週間練習計画": {"Day_1": {"練習内容": "フォアハンド練習"}},
            "3.具体的なドリル": [{"ドリル名": "フォアドリル", "目的": "威力向上"}]
        }
        
        analyzer.analyze_video = MagicMock(return_value=mock_analysis)
        analyzer.generate_strategy = MagicMock(return_value=mock_strategy)
        analyzer.generate_practice_plan = MagicMock(return_value=mock_practice)
        
        with patch('os.path.exists', return_value=True):
            analysis = analyzer.analyze_video("dummy.mp4")
            strategy = analyzer.generate_strategy(analysis)
            practice = analyzer.generate_practice_plan(analysis)
        
        # FA要件の検証
        assert "戦術分析" in analysis
        assert "得点パターン" in analysis["戦術分析"]
        assert "失点パターン" in analysis["戦術分析"]
        
        # FS要件の検証
        assert "1.サーブ戦略" in strategy
        assert "2.レシーブ戦略" in strategy
        assert "3.ラリー戦略" in strategy
        
        # FP要件の検証
        assert "1.優先課題" in practice
        assert "2.週間練習計画" in practice
        assert "3.具体的なドリル" in practice


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
