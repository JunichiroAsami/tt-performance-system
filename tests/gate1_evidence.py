#!/usr/bin/env python3
"""
Gate 1: 単体テスト エビデンス取得スクリプト
テスト仕様書に基づき、プロンプトの品質を検証する
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/home/ubuntu/tt-performance-system/src')
from analysis.prompts import (
    ANALYSIS_PROMPT, 
    STRATEGY_PROMPT, 
    PRACTICE_PROMPT,
    OPPONENT_ANALYSIS_PROMPT
)

def print_section(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def print_subsection(title):
    print(f"\n--- {title} ---")

def check_keyword(prompt, keyword, description):
    """キーワードの存在確認と該当箇所の表示"""
    found = keyword in prompt
    status = "✅ PASS" if found else "❌ FAIL"
    print(f"  {status} | {description}: 「{keyword}」")
    
    if found:
        # 該当箇所を抽出して表示
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            if keyword in line:
                print(f"         → 該当箇所(行{i+1}): {line.strip()[:60]}...")
                break
    return found

def run_ut01():
    """UT-01: 分析プロンプトの品質検証"""
    print_section("UT-01: 分析プロンプトの品質検証")
    
    print_subsection("入力データ")
    print(f"  検証対象: ANALYSIS_PROMPT")
    print(f"  文字数: {len(ANALYSIS_PROMPT)} 文字")
    print(f"  行数: {len(ANALYSIS_PROMPT.split(chr(10)))} 行")
    
    print_subsection("プロンプト内容（先頭500文字）")
    print("-" * 50)
    print(ANALYSIS_PROMPT[:500])
    print("-" * 50)
    
    print_subsection("合格基準との照合")
    
    results = []
    
    # FA-01: 得点/失点パターン分析
    print("\n【FA-01: 得点/失点パターン分析】")
    results.append(check_keyword(ANALYSIS_PROMPT, "得点パターン", "得点パターンの分析指示"))
    results.append(check_keyword(ANALYSIS_PROMPT, "失点パターン", "失点パターンの分析指示"))
    results.append(check_keyword(ANALYSIS_PROMPT, "3つ", "具体的な数値指定"))
    
    # FA-02: 技術別パフォーマンス分析
    print("\n【FA-02: 技術別パフォーマンス分析】")
    results.append(check_keyword(ANALYSIS_PROMPT, "フォアハンド", "フォアハンド技術"))
    results.append(check_keyword(ANALYSIS_PROMPT, "バックハンド", "バックハンド技術"))
    results.append(check_keyword(ANALYSIS_PROMPT, "サーブ", "サーブ技術"))
    results.append(check_keyword(ANALYSIS_PROMPT, "レシーブ", "レシーブ技術"))
    
    # FA-03: サーブ/レシーブ分析
    print("\n【FA-03: サーブ/レシーブ分析】")
    results.append(check_keyword(ANALYSIS_PROMPT, "種類", "サーブの種類"))
    results.append(check_keyword(ANALYSIS_PROMPT, "コース", "コースの分析"))
    results.append(check_keyword(ANALYSIS_PROMPT, "回転", "回転の分析"))
    
    # FA-04: フォーム分析
    print("\n【FA-04: フォーム分析】")
    results.append(check_keyword(ANALYSIS_PROMPT, "スイング", "スイング軌道"))
    results.append(check_keyword(ANALYSIS_PROMPT, "打点", "打点の分析"))
    results.append(check_keyword(ANALYSIS_PROMPT, "体重移動", "体の使い方"))
    
    # FA-05: フットワーク分析
    print("\n【FA-05: フットワーク分析】")
    results.append(check_keyword(ANALYSIS_PROMPT, "フットワーク", "フットワーク"))
    results.append(check_keyword(ANALYSIS_PROMPT, "移動", "移動の分析"))
    results.append(check_keyword(ANALYSIS_PROMPT, "ポジショニング", "ポジショニング"))
    
    # 出力形式
    print("\n【出力形式の指定】")
    results.append(check_keyword(ANALYSIS_PROMPT, "JSON", "JSON形式指定"))
    
    return all(results), results

def run_ut01_opponent():
    """UT-01追加: 相手分析プロンプトの品質検証"""
    print_section("UT-01追加: 相手分析プロンプトの品質検証")
    
    print_subsection("入力データ")
    print(f"  検証対象: OPPONENT_ANALYSIS_PROMPT")
    print(f"  文字数: {len(OPPONENT_ANALYSIS_PROMPT)} 文字")
    
    print_subsection("プロンプト内容（先頭400文字）")
    print("-" * 50)
    print(OPPONENT_ANALYSIS_PROMPT[:400])
    print("-" * 50)
    
    print_subsection("合格基準との照合")
    
    results = []
    
    # FA-06: 相手の得点/失点パターン分析
    print("\n【FA-06: 相手の得点/失点パターン分析】")
    results.append(check_keyword(OPPONENT_ANALYSIS_PROMPT, "得点パターン", "得点パターン"))
    results.append(check_keyword(OPPONENT_ANALYSIS_PROMPT, "失点パターン", "失点パターン"))
    
    # FA-07: 相手のサーブ/レシーブ傾向分析
    print("\n【FA-07: 相手のサーブ/レシーブ傾向分析】")
    results.append(check_keyword(OPPONENT_ANALYSIS_PROMPT, "サーブ", "サーブ傾向"))
    results.append(check_keyword(OPPONENT_ANALYSIS_PROMPT, "レシーブ", "レシーブ傾向"))
    
    # FA-08: 相手の弱点特定
    print("\n【FA-08: 相手の弱点特定】")
    results.append(check_keyword(OPPONENT_ANALYSIS_PROMPT, "弱点", "弱点特定"))
    results.append(check_keyword(OPPONENT_ANALYSIS_PROMPT, "攻略", "攻略法"))
    
    return all(results), results

def run_ut02():
    """UT-02: 戦略プロンプトの品質検証"""
    print_section("UT-02: 戦略プロンプトの品質検証")
    
    print_subsection("入力データ")
    print(f"  検証対象: STRATEGY_PROMPT")
    print(f"  文字数: {len(STRATEGY_PROMPT)} 文字")
    
    print_subsection("プロンプト内容（先頭500文字）")
    print("-" * 50)
    print(STRATEGY_PROMPT[:500])
    print("-" * 50)
    
    print_subsection("合格基準との照合")
    
    results = []
    
    # FS-01: 戦略シート生成
    print("\n【FS-01: 対戦相手別戦略シート生成】")
    results.append(check_keyword(STRATEGY_PROMPT, "戦略", "戦略の指示"))
    results.append(check_keyword(STRATEGY_PROMPT, "自己分析", "自己分析の参照"))
    results.append(check_keyword(STRATEGY_PROMPT, "相手分析", "相手分析の参照"))
    
    # FS-02: サーブ戦略提案
    print("\n【FS-02: サーブ戦略提案】")
    results.append(check_keyword(STRATEGY_PROMPT, "サーブ戦略", "サーブ戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "序盤", "序盤の戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "中盤", "中盤の戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "終盤", "終盤の戦略"))
    
    # FS-03: レシーブ戦略提案
    print("\n【FS-03: レシーブ戦略提案】")
    results.append(check_keyword(STRATEGY_PROMPT, "レシーブ戦略", "レシーブ戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "短い", "短いサーブへの対応"))
    results.append(check_keyword(STRATEGY_PROMPT, "長い", "長いサーブへの対応"))
    
    # FS-04: ラリー展開戦略提案
    print("\n【FS-04: ラリー展開戦略提案】")
    results.append(check_keyword(STRATEGY_PROMPT, "ラリー戦略", "ラリー戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "攻撃", "攻撃時の戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "守備", "守備時の戦略"))
    results.append(check_keyword(STRATEGY_PROMPT, "弱点", "弱点を突く方法"))
    
    return all(results), results

def run_ut03():
    """UT-03: 練習計画プロンプトの品質検証"""
    print_section("UT-03: 練習計画プロンプトの品質検証")
    
    print_subsection("入力データ")
    print(f"  検証対象: PRACTICE_PROMPT")
    print(f"  文字数: {len(PRACTICE_PROMPT)} 文字")
    
    print_subsection("プロンプト内容（先頭500文字）")
    print("-" * 50)
    print(PRACTICE_PROMPT[:500])
    print("-" * 50)
    
    print_subsection("合格基準との照合")
    
    results = []
    
    # FP-01: 課題の優先順位付け
    print("\n【FP-01: 課題の優先順位付け】")
    results.append(check_keyword(PRACTICE_PROMPT, "優先", "優先順位の指示"))
    results.append(check_keyword(PRACTICE_PROMPT, "重要度", "重要度の指示"))
    
    # FP-02: カスタム練習メニュー生成
    print("\n【FP-02: カスタム練習メニュー生成】")
    results.append(check_keyword(PRACTICE_PROMPT, "練習", "練習メニュー"))
    results.append(check_keyword(PRACTICE_PROMPT, "多球練習", "多球練習"))
    results.append(check_keyword(PRACTICE_PROMPT, "時間", "時間配分"))
    
    # FP-03: フォーム改善ドリル提案
    print("\n【FP-03: フォーム改善ドリル提案】")
    results.append(check_keyword(PRACTICE_PROMPT, "ドリル", "ドリル提案"))
    results.append(check_keyword(PRACTICE_PROMPT, "回数", "回数/セット"))
    
    return all(results), results

def main():
    """メイン実行"""
    print("\n" + "#" * 70)
    print(" Gate 1: 単体テスト エビデンス")
    print(f" 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 70)
    
    all_passed = True
    
    # UT-01実行
    ut01_passed, ut01_results = run_ut01()
    ut01_opp_passed, ut01_opp_results = run_ut01_opponent()
    all_passed = all_passed and ut01_passed and ut01_opp_passed
    
    # UT-02実行
    ut02_passed, ut02_results = run_ut02()
    all_passed = all_passed and ut02_passed
    
    # UT-03実行
    ut03_passed, ut03_results = run_ut03()
    all_passed = all_passed and ut03_passed
    
    # 総合判定
    print_section("Gate 1 総合判定")
    
    print("\n【テスト結果サマリー】")
    print(f"  UT-01 (分析プロンプト):     {'✅ PASS' if ut01_passed else '❌ FAIL'}")
    print(f"  UT-01 (相手分析プロンプト): {'✅ PASS' if ut01_opp_passed else '❌ FAIL'}")
    print(f"  UT-02 (戦略プロンプト):     {'✅ PASS' if ut02_passed else '❌ FAIL'}")
    print(f"  UT-03 (練習計画プロンプト): {'✅ PASS' if ut03_passed else '❌ FAIL'}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print(" ★★★ Gate 1 通過: 全ての単体テストに合格 ★★★")
        print(" → Gate 2（統合テスト）に進むことができます")
    else:
        print(" ✗✗✗ Gate 1 不通過: 一部のテストが不合格 ✗✗✗")
        print(" → プロンプトを修正し、再テストが必要です")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
