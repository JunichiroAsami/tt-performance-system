"""
PracticePlannerのテスト

TDD Step 4: 分析結果から練習計画を生成するテスト
"""
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.practice import PracticePlanner

# テスト用の分析結果（実際の分析結果を使用）
EVIDENCE_PATH = "tests/evidence/analyzer_test_evidence.json"


class TestPracticePlanner:
    """PracticePlannerのテストクラス"""
    
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
    def planner(self):
        """テスト用のPlannerインスタンス"""
        return PracticePlanner()
    
    @pytest.fixture(scope="class")
    def practice_result(self, planner, analysis_result):
        """練習計画の生成結果（クラス内で共有）"""
        return planner.generate(analysis_result)
    
    # ============================================
    # 動作確認テスト
    # ============================================
    
    def test_planner_can_be_instantiated(self, planner):
        """Plannerがインスタンス化できること"""
        assert planner is not None
        assert hasattr(planner, 'generate')
    
    def test_generate_returns_dict(self, practice_result):
        """生成結果が辞書型で返ること"""
        assert isinstance(practice_result, dict), "生成結果は辞書型である必要があります"
    
    def test_generate_does_not_have_parse_error(self, practice_result):
        """生成結果がJSONとして正常にパースされていること"""
        assert "parse_error" not in practice_result, "JSONパースエラーが発生しました"
    
    # ============================================
    # 品質テスト（練習計画の内容検証）
    # ============================================
    
    def test_has_priority_issues(self, practice_result):
        """優先課題が含まれていること"""
        assert "優先課題" in practice_result, "優先課題が含まれていません"
        issues = practice_result["優先課題"]
        
        assert len(issues) >= 1, "優先課題が1つ以上必要です"
    
    def test_priority_issues_have_details(self, practice_result):
        """優先課題に詳細が含まれていること"""
        issues = practice_result["優先課題"]
        
        for issue in issues:
            assert "課題" in issue, "課題の内容が含まれていません"
            assert "理由" in issue or "優先度" in issue, "理由または優先度が含まれていません"
    
    def test_has_weekly_plan(self, practice_result):
        """週間計画が含まれていること"""
        assert "週間計画" in practice_result, "週間計画が含まれていません"
        plan = practice_result["週間計画"]
        
        # 少なくとも5日分の計画があること
        assert len(plan) >= 5, f"週間計画が5日分以上必要です（現在: {len(plan)}日）"
    
    def test_daily_plan_has_theme(self, practice_result):
        """各日の計画にテーマがあること"""
        plan = practice_result["週間計画"]
        
        for day, content in plan.items():
            if isinstance(content, dict):
                assert "テーマ" in content, f"{day}にテーマがありません"
    
    def test_daily_plan_has_menu(self, practice_result):
        """各日の計画にメニューがあること"""
        plan = practice_result["週間計画"]
        
        for day, content in plan.items():
            if isinstance(content, dict):
                assert "メニュー" in content, f"{day}にメニューがありません"
                menu = content["メニュー"]
                assert len(menu) >= 1, f"{day}のメニューが空です"
    
    def test_has_drills(self, practice_result):
        """ドリル集が含まれていること"""
        assert "ドリル集" in practice_result, "ドリル集が含まれていません"
        drills = practice_result["ドリル集"]
        
        assert len(drills) >= 3, f"ドリルが3つ以上必要です（現在: {len(drills)}個）"
    
    def test_drills_have_details(self, practice_result):
        """ドリルに詳細が含まれていること"""
        drills = practice_result["ドリル集"]
        
        for drill in drills:
            assert "名前" in drill, "ドリル名が含まれていません"
            assert "手順" in drill or "ポイント" in drill, "手順またはポイントが含まれていません"
    
    def test_drills_have_steps(self, practice_result):
        """ドリルに手順が含まれていること"""
        drills = practice_result["ドリル集"]
        
        for drill in drills:
            if "手順" in drill:
                steps = drill["手順"]
                assert len(steps) >= 2, f"ドリル「{drill.get('名前', '不明')}」の手順が少なすぎます"
    
    def test_has_goals(self, practice_result):
        """達成目標が含まれていること"""
        assert "達成目標" in practice_result, "達成目標が含まれていません"
        goals = practice_result["達成目標"]
        
        # 短期・中期・長期の目標があること
        assert len(goals) >= 1, "達成目標が空です"
    
    def test_practice_uses_table_tennis_terms(self, practice_result):
        """練習計画に卓球用語が含まれていること"""
        text = json.dumps(practice_result, ensure_ascii=False)
        
        tt_terms = ["サーブ", "レシーブ", "ドライブ", "スマッシュ", "ブロック", 
                    "カット", "ツッツキ", "フリック", "チキータ", "ストップ",
                    "フォア", "バック", "回転", "フットワーク", "多球"]
        
        found_terms = [term for term in tt_terms if term in text]
        assert len(found_terms) >= 5, f"卓球用語が少なすぎます: {found_terms}"
    
    # ============================================
    # エビデンス出力
    # ============================================
    
    def test_save_evidence(self, practice_result, analysis_result):
        """テストエビデンスを保存"""
        evidence = {
            "test_name": "PracticePlanner練習計画生成テスト",
            "input": {
                "analysis_result": analysis_result
            },
            "output": practice_result,
            "validations": {
                "has_priority_issues": "優先課題" in practice_result,
                "has_weekly_plan": "週間計画" in practice_result,
                "has_drills": "ドリル集" in practice_result,
                "has_goals": "達成目標" in practice_result,
                "no_parse_error": "parse_error" not in practice_result,
                "drill_count": len(practice_result.get("ドリル集", [])),
                "day_count": len(practice_result.get("週間計画", {}))
            }
        }
        
        os.makedirs("tests/evidence", exist_ok=True)
        with open("tests/evidence/practice_test_evidence.json", "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
        
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
