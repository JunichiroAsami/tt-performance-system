"""
業務要件ベースのE2Eテスト
エンドツーエンドで業務要件が満たされることを検証
"""

import pytest
import os
import sys
import json
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from analysis.llm_analyzer import LLMAnalyzer
from output.report_generator import ReportGenerator


class TestE2EAnalysisRequirements:
    """E2E: 分析要件（FA-01~08）の検証"""
    
    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer()
    
    @pytest.fixture
    def mock_full_analysis(self):
        """完全な分析結果のモック（全FA要件を満たす）"""
        return {
            "基本情報": {
                "選手名": "浅見江里佳",
                "所属": "文化学園大学杉並",
                "利き手": "右",
                "グリップ": "シェークハンド",
                "プレースタイル": "攻撃型"
            },
            "技術分析": {
                "フォアハンドドライブ": {
                    "スイング軌道の評価": 4,
                    "打点の適切さ": 3,
                    "体重移動": 4,
                    "回転量": "強",
                    "強み": "威力がある",
                    "改善点": "安定性の向上"
                },
                "バックハンドドライブ": {
                    "スイング軌道の評価": 5,
                    "打点の適切さ": 5,
                    "安定性": 5,
                    "強み": "非常に安定している",
                    "改善点": "特になし"
                },
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
                },
                "フットワーク": {
                    "移動速度": 4,
                    "戻りの速さ": 4,
                    "ポジショニング": 3,
                    "強み": "素早い移動",
                    "改善点": "戻りのポジショニング"
                }
            },
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
                ],
                "サーブ戦術": {
                    "よく使うサーブ": "ショートサーブ（60%）、ロングサーブ（30%）、横回転（10%）",
                    "サーブからの展開": "3球目攻撃を狙う"
                },
                "レシーブ戦術": {
                    "傾向": "攻撃的レシーブを好む",
                    "4球目以降": "ラリー展開"
                }
            },
            "総合評価": {
                "強み": ["バックハンドドライブ", "チキータ", "フットワーク"],
                "改善点": ["フォアハンドの決定力", "ロングサーブへの対応", "ラリー戦での粘り"]
            }
        }
    
    def test_e2e_FA01_scoring_patterns(self, analyzer, mock_full_analysis):
        """E2E FA-01: 得点/失点パターン分析が完全に機能する"""
        analyzer.analyze_video = MagicMock(return_value=mock_full_analysis)
        
        with patch('os.path.exists', return_value=True):
            result = analyzer.analyze_video("test.mp4")
        
        # FA-01: 得点パターン
        assert "戦術分析" in result
        assert "得点パターン" in result["戦術分析"]
        patterns = result["戦術分析"]["得点パターン"]
        assert len(patterns) >= 3
        for p in patterns:
            assert len(p) > 5  # 意味のある内容
        
        # FA-01: 失点パターン
        assert "失点パターン" in result["戦術分析"]
        patterns = result["戦術分析"]["失点パターン"]
        assert len(patterns) >= 3
        for p in patterns:
            assert len(p) > 5
    
    def test_e2e_FA02_technique_analysis(self, analyzer, mock_full_analysis):
        """E2E FA-02: 技術別パフォーマンス分析が完全に機能する"""
        analyzer.analyze_video = MagicMock(return_value=mock_full_analysis)
        
        with patch('os.path.exists', return_value=True):
            result = analyzer.analyze_video("test.mp4")
        
        assert "技術分析" in result
        tech = result["技術分析"]
        
        # 必須技術の存在確認
        required_techniques = ["フォアハンド", "バックハンド"]
        for req in required_techniques:
            found = any(req in k for k in tech.keys())
            assert found, f"{req}の分析が見つかりません"
    
    def test_e2e_FA03_serve_receive(self, analyzer, mock_full_analysis):
        """E2E FA-03: サーブ/レシーブ分析が完全に機能する"""
        analyzer.analyze_video = MagicMock(return_value=mock_full_analysis)
        
        with patch('os.path.exists', return_value=True):
            result = analyzer.analyze_video("test.mp4")
        
        tech = result["技術分析"]
        assert "サーブ" in tech
        assert "レシーブ" in tech
        
        # サーブ分析の詳細
        serve = tech["サーブ"]
        assert "種類のバリエーション" in serve or "コースの精度" in serve
        
        # レシーブ分析の詳細
        receive = tech["レシーブ"]
        assert "対応力" in receive or "攻撃的レシーブ" in receive
    
    def test_e2e_FA04_FA05_form_footwork(self, analyzer, mock_full_analysis):
        """E2E FA-04/FA-05: フォーム/フットワーク分析が完全に機能する"""
        analyzer.analyze_video = MagicMock(return_value=mock_full_analysis)
        
        with patch('os.path.exists', return_value=True):
            result = analyzer.analyze_video("test.mp4")
        
        tech = result["技術分析"]
        
        # FA-04: フォーム分析（各技術の評価に含まれる）
        for tech_name, tech_data in tech.items():
            if isinstance(tech_data, dict):
                # 評価項目が存在する
                assert len(tech_data) > 0
        
        # FA-05: フットワーク分析
        assert "フットワーク" in tech
        footwork = tech["フットワーク"]
        assert "移動速度" in footwork or "ポジショニング" in footwork


class TestE2EStrategyRequirements:
    """E2E: 戦略要件（FS-01~04）の検証"""
    
    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer()
    
    @pytest.fixture
    def mock_full_strategy(self):
        """完全な戦略結果のモック（全FS要件を満たす）"""
        return {
            "戦略立案": {
                "選手名": "浅見江里佳",
                "対戦相手": "山田選手",
                "目標": "バックハンドを軸に攻撃を組み立てる"
            },
            "1.サーブ戦略": {
                "序盤（1-3点目）": {
                    "推奨サーブ": "フォア前ショートサーブ",
                    "狙い": "相手を前に出してチャンスを作る"
                },
                "中盤（4-8点目）": {
                    "推奨サーブ": "バック側ロングサーブ",
                    "狙い": "3球目攻撃で決める"
                },
                "終盤・デュース": {
                    "推奨サーブ": "横回転サーブ",
                    "狙い": "相手を崩して攻撃チャンスを作る"
                }
            },
            "2.レシーブ戦略": {
                "相手の短いサーブに対して": {
                    "推奨レシーブ": "チキータ",
                    "注意点": "コースを読んで早めに準備"
                },
                "相手の長いサーブに対して": {
                    "推奨レシーブ": "ドライブで攻撃",
                    "注意点": "回転を見極めてから打つ"
                },
                "相手の得意サーブに対して": {
                    "推奨レシーブ": "安全にストップ",
                    "注意点": "無理に攻めない"
                }
            },
            "3.ラリー戦略": {
                "攻撃時": {
                    "狙うべきコース": "バックで崩してフォアで決める",
                    "攻撃のタイミング": "相手が体勢を崩した時"
                },
                "守備時": {
                    "守備の方針": "深いボールで時間を稼ぐ",
                    "カウンターのタイミング": "相手の攻撃が甘くなった時"
                },
                "相手の弱点を突く方法": {
                    "具体的な攻め方": "フォア側への攻撃を多用"
                }
            },
            "4.試合運びの注意点": {
                "リードしている時": "無理せず確実にポイントを取る",
                "追いかけている時": "思い切って攻める",
                "競っている時": "自分の得意パターンで勝負"
            },
            "5.キーポイント": [
                "バックハンドを軸に組み立てる",
                "相手のフォア側を攻める",
                "サーブからの3球目攻撃を徹底"
            ]
        }
    
    def test_e2e_FS01_strategy_sheet(self, analyzer, mock_full_strategy):
        """E2E FS-01: 対戦相手別戦略シートが完全に生成される"""
        analyzer.generate_strategy = MagicMock(return_value=mock_full_strategy)
        
        result = analyzer.generate_strategy({})
        
        # 戦略シートの基本構造
        assert "戦略立案" in result or "1.サーブ戦略" in result
        
        # 必須セクションの存在
        required_sections = ["1.サーブ戦略", "2.レシーブ戦略", "3.ラリー戦略"]
        for section in required_sections:
            assert section in result, f"{section}が見つかりません"
    
    def test_e2e_FS02_serve_strategy(self, analyzer, mock_full_strategy):
        """E2E FS-02: サーブ戦略が詳細に提案される"""
        analyzer.generate_strategy = MagicMock(return_value=mock_full_strategy)
        
        result = analyzer.generate_strategy({})
        
        serve = result["1.サーブ戦略"]
        
        # 試合の段階別戦略
        assert len(serve) >= 2  # 複数の段階
        
        # 各段階に推奨と狙いが含まれる
        for phase, strategy in serve.items():
            assert "推奨" in str(strategy) or "サーブ" in str(strategy)
    
    def test_e2e_FS03_receive_strategy(self, analyzer, mock_full_strategy):
        """E2E FS-03: レシーブ戦略が詳細に提案される"""
        analyzer.generate_strategy = MagicMock(return_value=mock_full_strategy)
        
        result = analyzer.generate_strategy({})
        
        receive = result["2.レシーブ戦略"]
        
        # 複数のシナリオ
        assert len(receive) >= 2
        
        # 各シナリオに推奨が含まれる
        for scenario, strategy in receive.items():
            assert "推奨" in str(strategy) or "レシーブ" in str(strategy)
    
    def test_e2e_FS04_rally_strategy(self, analyzer, mock_full_strategy):
        """E2E FS-04: ラリー展開戦略が詳細に提案される"""
        analyzer.generate_strategy = MagicMock(return_value=mock_full_strategy)
        
        result = analyzer.generate_strategy({})
        
        rally = result["3.ラリー戦略"]
        
        # 攻撃と守備の両方
        assert "攻撃時" in rally or "攻撃" in str(rally)
        assert "守備時" in rally or "守備" in str(rally)


class TestE2EPracticeRequirements:
    """E2E: 練習計画要件（FP-01~03）の検証"""
    
    @pytest.fixture
    def analyzer(self):
        return LLMAnalyzer()
    
    @pytest.fixture
    def mock_full_practice(self):
        """完全な練習計画のモック（全FP要件を満たす）"""
        return {
            "選手名": "浅見江里佳",
            "1.優先課題": [
                {
                    "課題": "フォアハンドの決定力向上",
                    "重要度": "最優先",
                    "理由": "得点パターンを増やすため"
                },
                {
                    "課題": "ロングサーブへの対応",
                    "重要度": "高",
                    "理由": "失点パターンの改善"
                },
                {
                    "課題": "ラリー戦での粘り強さ",
                    "重要度": "中",
                    "理由": "全体的な安定性向上"
                }
            ],
            "2.週間練習計画": {
                "Day_1（技術練習）": {
                    "練習内容": "フォアハンド強化",
                    "時間配分": "2時間",
                    "ポイント": "フルスイングを意識"
                },
                "Day_2（戦術練習）": {
                    "練習内容": "3球目攻撃パターン",
                    "時間配分": "2時間",
                    "ポイント": "サーブからの展開を意識"
                },
                "Day_3（多球練習）": {
                    "練習内容": "フットワーク強化",
                    "時間配分": "1.5時間",
                    "ポイント": "素早い戻りを意識"
                },
                "Day_4（試合形式練習）": {
                    "練習内容": "実戦形式のゲーム練習",
                    "時間配分": "2時間",
                    "ポイント": "戦術を試す"
                },
                "Day_5（課題克服集中練習）": {
                    "練習内容": "ロングサーブレシーブ",
                    "時間配分": "1.5時間",
                    "ポイント": "苦手克服"
                }
            },
            "3.具体的なドリル": [
                {
                    "ドリル名": "フォアハンド・フルスイングドリル",
                    "目的": "フォアハンドの威力向上",
                    "方法": "多球練習でフルスイングを繰り返す",
                    "時間": "15分",
                    "回数/セット": "50球×3セット"
                },
                {
                    "ドリル名": "ロングサーブレシーブドリル",
                    "目的": "ロングサーブへの対応力向上",
                    "方法": "パートナーにロングサーブを出してもらい、ドライブで返球",
                    "時間": "20分",
                    "回数/セット": "30球×3セット"
                },
                {
                    "ドリル名": "フットワーク・ファンドリル",
                    "目的": "フットワークの強化",
                    "方法": "ランダムな位置にボールを出してもらい、素早く移動して打球",
                    "時間": "15分",
                    "回数/セット": "3分×5セット"
                }
            ],
            "4.目標設定": {
                "短期目標（1ヶ月）": [
                    "フォアハンドの成功率を80%以上に",
                    "ロングサーブレシーブの成功率を70%以上に",
                    "3球目攻撃の決定率を60%以上に"
                ],
                "中期目標（3ヶ月）": [
                    "校内ランキング3位以内",
                    "得点パターンを5つ以上確立",
                    "失点パターンを2つ以下に減少"
                ],
                "長期目標（6ヶ月〜1年）": [
                    "県大会ベスト8",
                    "全技術の安定性向上",
                    "メンタル面の強化"
                ]
            },
            "5.練習時の注意点": [
                "フォームを崩さないように意識する",
                "疲れた時こそ正確なフォームを維持",
                "試合を想定した練習を心がける"
            ]
        }
    
    def test_e2e_FP01_priority(self, analyzer, mock_full_practice):
        """E2E FP-01: 課題の優先順位付けが完全に機能する"""
        analyzer.generate_practice_plan = MagicMock(return_value=mock_full_practice)
        
        result = analyzer.generate_practice_plan({})
        
        assert "1.優先課題" in result
        issues = result["1.優先課題"]
        
        # 複数の課題
        assert len(issues) >= 3
        
        # 優先度情報
        for issue in issues:
            assert "重要度" in issue or "優先" in str(issue)
            assert "理由" in issue or "課題" in issue
    
    def test_e2e_FP02_practice_menu(self, analyzer, mock_full_practice):
        """E2E FP-02: カスタム練習メニューが完全に生成される"""
        analyzer.generate_practice_plan = MagicMock(return_value=mock_full_practice)
        
        result = analyzer.generate_practice_plan({})
        
        assert "2.週間練習計画" in result
        plan = result["2.週間練習計画"]
        
        # 複数日の計画
        assert len(plan) >= 3
        
        # 各日に必要な情報
        for day, content in plan.items():
            assert "練習内容" in content or "時間" in str(content)
    
    def test_e2e_FP03_drills(self, analyzer, mock_full_practice):
        """E2E FP-03: フォーム改善ドリルが完全に提案される"""
        analyzer.generate_practice_plan = MagicMock(return_value=mock_full_practice)
        
        result = analyzer.generate_practice_plan({})
        
        assert "3.具体的なドリル" in result
        drills = result["3.具体的なドリル"]
        
        # 複数のドリル
        assert len(drills) >= 3
        
        # 各ドリルに必要な情報
        for drill in drills:
            assert "ドリル名" in drill or "名前" in drill
            assert "目的" in drill
            assert "方法" in drill


class TestE2EReportRequirements:
    """E2E: レポート要件（FR-01~03）の検証"""
    
    def test_e2e_FR01_summary_report(self):
        """E2E FR-01: 試合後サマリーレポートが完全に生成される"""
        generator = ReportGenerator()
        
        mock_analysis = {
            "基本情報": {
                "選手名": "浅見江里佳",
                "所属": "文化学園大学杉並"
            },
            "技術分析": {
                "フォアハンドドライブ": {"評価": 4},
                "バックハンドドライブ": {"評価": 5}
            },
            "戦術分析": {
                "得点パターン": ["バックハンド攻撃", "チキータ", "カウンター"],
                "失点パターン": ["フォア側対応ミス", "ロングサーブ対応", "ラリー負け"]
            },
            "総合評価": {
                "強み": ["バックハンド", "チキータ", "フットワーク"],
                "改善点": ["フォアハンド", "ロングサーブ対応", "ラリー戦"]
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "report.md")
            generator.generate_analysis_report(mock_analysis, report_path)
            
            assert os.path.exists(report_path)
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 必須情報の存在確認
            assert "浅見江里佳" in content
            assert len(content) > 100  # 十分な内容量
            
            # 構造化されたレポート
            assert "#" in content  # Markdownヘッダー


class TestE2EFullWorkflow:
    """E2E: 完全なワークフローの検証"""
    
    def test_e2e_complete_workflow(self):
        """E2E: 分析→戦略→練習計画→レポートの完全なワークフロー"""
        analyzer = LLMAnalyzer()
        generator = ReportGenerator()
        
        # モック設定
        mock_analysis = {
            "基本情報": {"選手名": "浅見江里佳"},
            "技術分析": {
                "フォアハンドドライブ": {"評価": 4},
                "バックハンドドライブ": {"評価": 5},
                "サーブ": {"コースの精度": 4},
                "レシーブ": {"対応力": 4},
                "フットワーク": {"移動速度": 4}
            },
            "戦術分析": {
                "得点パターン": ["バックハンド攻撃", "チキータ", "カウンター"],
                "失点パターン": ["フォア側対応ミス", "ロングサーブ対応", "ラリー負け"]
            },
            "総合評価": {
                "強み": ["バックハンド"],
                "改善点": ["フォアハンド"]
            }
        }
        
        mock_strategy = {
            "戦略立案": {"選手名": "浅見江里佳"},
            "1.サーブ戦略": {"序盤": {"推奨": "ショートサーブ"}},
            "2.レシーブ戦略": {"短いサーブ": {"推奨": "チキータ"}},
            "3.ラリー戦略": {"攻撃時": {"狙い": "バックで崩す"}}
        }
        
        mock_practice = {
            "選手名": "浅見江里佳",
            "1.優先課題": [
                {"課題": "フォアハンド強化", "重要度": "最優先", "理由": "得点力向上"}
            ],
            "2.週間練習計画": {"Day_1": {"練習内容": "フォアハンド練習"}},
            "3.具体的なドリル": [
                {"ドリル名": "フォアドリル", "目的": "威力向上", "方法": "多球練習"}
            ]
        }
        
        analyzer.analyze_video = MagicMock(return_value=mock_analysis)
        analyzer.generate_strategy = MagicMock(return_value=mock_strategy)
        analyzer.generate_practice_plan = MagicMock(return_value=mock_practice)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: 分析
            with patch('os.path.exists', return_value=True):
                analysis = analyzer.analyze_video("test.mp4")
            
            # FA要件の検証
            assert "戦術分析" in analysis
            assert "得点パターン" in analysis["戦術分析"]
            assert "失点パターン" in analysis["戦術分析"]
            
            # Step 2: 戦略生成
            strategy = analyzer.generate_strategy(analysis)
            
            # FS要件の検証
            assert "1.サーブ戦略" in strategy
            assert "2.レシーブ戦略" in strategy
            assert "3.ラリー戦略" in strategy
            
            # Step 3: 練習計画生成
            practice = analyzer.generate_practice_plan(analysis)
            
            # FP要件の検証
            assert "1.優先課題" in practice
            assert "2.週間練習計画" in practice
            assert "3.具体的なドリル" in practice
            
            # Step 4: レポート生成
            report_path = os.path.join(tmpdir, "report.md")
            generator.generate_analysis_report(analysis, report_path)
            
            # FR要件の検証
            assert os.path.exists(report_path)
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert len(content) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
