"""
Report Generator Module
分析結果をMarkdown/PDF形式のレポートに変換
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ReportGenerator:
    """
    分析結果からレポートを生成するクラス
    """
    
    def __init__(self, output_dir: str = "data/results"):
        """
        初期化
        
        Args:
            output_dir: 出力ディレクトリ
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_analysis_report(
        self,
        analysis: Dict[str, Any],
        player_name: str = "浅見江里佳",
        team_name: str = "文化学園大学杉並"
    ) -> str:
        """
        分析レポートを生成
        
        Args:
            analysis: 分析結果
            player_name: 選手名
            team_name: 所属チーム名
            
        Returns:
            生成されたレポートのパス
        """
        timestamp = datetime.now().strftime("%Y年%m月%d日")
        
        report = f"""# 卓球パフォーマンス分析レポート

**選手名**: {player_name}  
**所属**: {team_name}  
**分析日**: {timestamp}

---

## 1. 基本情報

"""
        
        # 基本情報を追加
        if "player_info" in analysis:
            info = analysis["player_info"]
            report += f"""| 項目 | 内容 |
|:---|:---|
| 利き手 | {info.get('dominant_hand', '右')} |
| グリップ | {info.get('grip', 'シェークハンド')} |
| プレースタイル | {info.get('play_style', '攻撃型')} |

"""
        
        # 技術分析を追加
        report += """## 2. 技術分析

"""
        
        if "techniques" in analysis:
            techniques = analysis["techniques"]
            
            for tech_name, tech_data in techniques.items():
                if isinstance(tech_data, dict):
                    report += f"""### {self._translate_technique_name(tech_name)}

| 評価項目 | スコア |
|:---|:---|
"""
                    if "rating" in tech_data:
                        report += f"| 総合評価 | {'★' * tech_data['rating']}{'☆' * (5 - tech_data['rating'])} ({tech_data['rating']}/5) |\n"
                    
                    report += f"""
**強み**: {', '.join(tech_data.get('strengths', ['なし']))}

**改善点**: {', '.join(tech_data.get('weaknesses', ['なし']))}

"""
        
        # 戦術分析を追加
        report += """## 3. 戦術分析

"""
        
        if "scoring_patterns" in analysis:
            report += """### 得点パターン

"""
            for i, pattern in enumerate(analysis["scoring_patterns"], 1):
                report += f"{i}. {pattern}\n"
            report += "\n"
        
        if "losing_patterns" in analysis:
            report += """### 失点パターン

"""
            for i, pattern in enumerate(analysis["losing_patterns"], 1):
                report += f"{i}. {pattern}\n"
            report += "\n"
        
        # 総合評価を追加
        report += """## 4. 総合評価

"""
        
        if "overall_assessment" in analysis:
            report += f"""{analysis['overall_assessment']}

"""
        
        if "priority_improvements" in analysis:
            report += """### 優先改善点

"""
            for i, item in enumerate(analysis["priority_improvements"], 1):
                report += f"{i}. {item}\n"
        
        # ファイルに保存
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"analysis_report_{timestamp_file}.md"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        return str(output_file)
    
    def generate_strategy_sheet(
        self,
        strategy: Dict[str, Any],
        player_name: str = "浅見江里佳",
        opponent_name: Optional[str] = None
    ) -> str:
        """
        試合戦略シートを生成（A4一枚）
        
        Args:
            strategy: 戦略データ
            player_name: 選手名
            opponent_name: 対戦相手名
            
        Returns:
            生成されたシートのパス
        """
        timestamp = datetime.now().strftime("%Y年%m月%d日")
        opponent_str = f" vs {opponent_name}" if opponent_name else ""
        
        sheet = f"""# 試合戦略シート

**選手**: {player_name}{opponent_str}  
**作成日**: {timestamp}

---

## サーブ戦略

| 場面 | サーブ | コース | 狙い |
|:---|:---|:---|:---|
"""
        
        if "serve_strategy" in strategy:
            serve = strategy["serve_strategy"]
            if "first_serve" in serve:
                for s in serve["first_serve"][:2]:
                    sheet += f"| 序盤 | {s.get('type', '-')} | {s.get('course', '-')} | {s.get('purpose', '-')} |\n"
            if "deuce_serve" in serve:
                for s in serve["deuce_serve"][:2]:
                    sheet += f"| デュース | {s.get('type', '-')} | {s.get('course', '-')} | {s.get('purpose', '-')} |\n"
        
        sheet += """
## レシーブ戦略

| 相手サーブ | 対応 |
|:---|:---|
"""
        
        if "receive_strategy" in strategy:
            recv = strategy["receive_strategy"]
            sheet += f"| 短いサーブ | {recv.get('against_short', '-')} |\n"
            sheet += f"| 長いサーブ | {recv.get('against_long', '-')} |\n"
        
        sheet += """
## ラリー戦略

"""
        
        if "rally_strategy" in strategy:
            rally = strategy["rally_strategy"]
            sheet += f"**攻撃時**: {', '.join(rally.get('attack_targets', []))}\n\n"
            sheet += f"**守備時**: {rally.get('defensive_approach', '-')}\n\n"
        
        sheet += """## キーポイント（試合前に確認！）

"""
        
        if "key_points" in strategy:
            for i, point in enumerate(strategy["key_points"][:3], 1):
                sheet += f"**{i}. {point}**\n\n"
        
        # ファイルに保存
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"strategy_sheet_{timestamp_file}.md"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(sheet)
        
        return str(output_file)
    
    def generate_practice_plan(
        self,
        practice_plan: Dict[str, Any],
        player_name: str = "浅見江里佳"
    ) -> str:
        """
        練習計画書を生成
        
        Args:
            practice_plan: 練習計画データ
            player_name: 選手名
            
        Returns:
            生成された計画書のパス
        """
        timestamp = datetime.now().strftime("%Y年%m月%d日")
        
        plan = f"""# 練習計画書

**選手**: {player_name}  
**作成日**: {timestamp}

---

## 1. 優先課題

"""
        
        if "priority_issues" in practice_plan:
            for i, issue in enumerate(practice_plan["priority_issues"], 1):
                if isinstance(issue, dict):
                    plan += f"### 課題{i}: {issue.get('issue', '-')}\n\n"
                    plan += f"**理由**: {issue.get('reason', '-')}\n\n"
                else:
                    plan += f"### 課題{i}: {issue}\n\n"
        
        plan += """## 2. 週間練習計画

"""
        
        if "weekly_plan" in practice_plan:
            for day, content in practice_plan["weekly_plan"].items():
                plan += f"### {day}\n\n"
                if isinstance(content, list):
                    for item in content:
                        plan += f"- {item}\n"
                else:
                    plan += f"{content}\n"
                plan += "\n"
        
        plan += """## 3. 具体的なドリル

"""
        
        if "drills" in practice_plan:
            for i, drill in enumerate(practice_plan["drills"], 1):
                plan += f"""### ドリル{i}: {drill.get('name', '-')}

| 項目 | 内容 |
|:---|:---|
| 目的 | {drill.get('purpose', '-')} |
| 時間 | {drill.get('duration', '-')} |
| 方法 | {drill.get('method', '-')} |

"""
        
        plan += """## 4. 目標設定

"""
        
        if "goals" in practice_plan:
            goals = practice_plan["goals"]
            
            if "short_term" in goals:
                plan += "### 短期目標（1ヶ月）\n\n"
                for goal in goals["short_term"]:
                    plan += f"- {goal}\n"
                plan += "\n"
            
            if "long_term" in goals:
                plan += "### 長期目標（6ヶ月〜1年）\n\n"
                for goal in goals["long_term"]:
                    plan += f"- {goal}\n"
                plan += "\n"
        
        # ファイルに保存
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"practice_plan_{timestamp_file}.md"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(plan)
        
        return str(output_file)
    
    def _translate_technique_name(self, name: str) -> str:
        """技術名を日本語に変換"""
        translations = {
            "forehand_drive": "フォアハンドドライブ",
            "backhand_drive": "バックハンドドライブ",
            "serve": "サーブ",
            "receive": "レシーブ",
            "footwork": "フットワーク"
        }
        return translations.get(name, name)
