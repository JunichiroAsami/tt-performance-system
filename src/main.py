#!/usr/bin/env python3
"""
AI主導型 卓球パフォーマンス最大化システム
メインエントリーポイント
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from analysis.llm_analyzer import LLMAnalyzer


def analyze_command(args):
    """動画分析コマンド"""
    analyzer = LLMAnalyzer()
    
    print(f"=== 動画分析を開始 ===")
    print(f"対象: {args.video}")
    print(f"選手: {args.player}")
    print(f"所属: {args.team}")
    print()
    
    result = analyzer.analyze_video(
        video_path=args.video,
        player_name=args.player,
        team_name=args.team
    )
    
    # 結果を保存
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"analysis_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"=== 分析完了 ===")
    print(f"結果を保存しました: {output_file}")
    
    # 結果を表示
    if args.verbose:
        print("\n=== 分析結果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result


def strategy_command(args):
    """戦略生成コマンド"""
    analyzer = LLMAnalyzer()
    
    print(f"=== 戦略生成を開始 ===")
    
    # 自己分析を実行
    print("自己分析を実行中...")
    self_analysis = analyzer.analyze_video(
        video_path=args.video,
        player_name=args.player,
        team_name=args.team
    )
    
    # 相手分析（オプション）
    opponent_analysis = None
    if args.opponent_video:
        print(f"相手分析を実行中: {args.opponent}")
        opponent_analysis = analyzer.analyze_opponent(
            video_path=args.opponent_video,
            opponent_name=args.opponent,
            opponent_team=args.opponent_team or ""
        )
    
    # 戦略生成
    print("戦略を生成中...")
    strategy = analyzer.generate_strategy(self_analysis, opponent_analysis)
    
    # 結果を保存
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"strategy_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "self_analysis": self_analysis,
            "opponent_analysis": opponent_analysis,
            "strategy": strategy
        }, f, ensure_ascii=False, indent=2)
    
    print(f"=== 戦略生成完了 ===")
    print(f"結果を保存しました: {output_file}")
    
    if args.verbose:
        print("\n=== 戦略 ===")
        print(json.dumps(strategy, ensure_ascii=False, indent=2))
    
    return strategy


def practice_command(args):
    """練習計画生成コマンド"""
    analyzer = LLMAnalyzer()
    
    print(f"=== 練習計画生成を開始 ===")
    
    # 分析結果を読み込むか、新規分析を実行
    if args.analysis_file:
        print(f"分析結果を読み込み中: {args.analysis_file}")
        with open(args.analysis_file, "r", encoding="utf-8") as f:
            analysis = json.load(f)
    else:
        print("動画分析を実行中...")
        analysis = analyzer.analyze_video(
            video_path=args.video,
            player_name=args.player,
            team_name=args.team
        )
    
    # 練習計画生成
    print("練習計画を生成中...")
    practice_plan = analyzer.generate_practice_plan(analysis)
    
    # 結果を保存
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"practice_plan_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "analysis": analysis,
            "practice_plan": practice_plan
        }, f, ensure_ascii=False, indent=2)
    
    print(f"=== 練習計画生成完了 ===")
    print(f"結果を保存しました: {output_file}")
    
    if args.verbose:
        print("\n=== 練習計画 ===")
        print(json.dumps(practice_plan, ensure_ascii=False, indent=2))
    
    return practice_plan


def full_command(args):
    """フル分析コマンド（分析→戦略→練習計画）"""
    analyzer = LLMAnalyzer()
    
    print(f"=== フル分析を開始 ===")
    print(f"対象: {args.video}")
    print(f"選手: {args.player}")
    print()
    
    # 1. 動画分析
    print("【Step 1/3】動画分析を実行中...")
    analysis = analyzer.analyze_video(
        video_path=args.video,
        player_name=args.player,
        team_name=args.team
    )
    
    # 2. 戦略生成
    print("【Step 2/3】戦略を生成中...")
    strategy = analyzer.generate_strategy(analysis)
    
    # 3. 練習計画生成
    print("【Step 3/3】練習計画を生成中...")
    practice_plan = analyzer.generate_practice_plan(analysis)
    
    # 結果を統合
    full_result = {
        "player": args.player,
        "team": args.team,
        "video": args.video,
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "strategy": strategy,
        "practice_plan": practice_plan
    }
    
    # 結果を保存
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"full_analysis_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(full_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== フル分析完了 ===")
    print(f"結果を保存しました: {output_file}")
    
    if args.verbose:
        print("\n=== 分析結果 ===")
        print(json.dumps(full_result, ensure_ascii=False, indent=2))
    
    return full_result


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="AI主導型 卓球パフォーマンス最大化システム"
    )
    subparsers = parser.add_subparsers(dest="command", help="コマンド")
    
    # 共通引数
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--player", "-p",
        default="浅見江里佳",
        help="選手名（デフォルト: 浅見江里佳）"
    )
    common_parser.add_argument(
        "--team", "-t",
        default="文化学園大学杉並",
        help="所属チーム名"
    )
    common_parser.add_argument(
        "--output", "-o",
        default="data/results",
        help="出力ディレクトリ"
    )
    common_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細出力"
    )
    
    # analyze コマンド
    analyze_parser = subparsers.add_parser(
        "analyze",
        parents=[common_parser],
        help="動画を分析"
    )
    analyze_parser.add_argument(
        "--video",
        required=True,
        help="分析する動画ファイル"
    )
    
    # strategy コマンド
    strategy_parser = subparsers.add_parser(
        "strategy",
        parents=[common_parser],
        help="試合戦略を生成"
    )
    strategy_parser.add_argument(
        "--video",
        required=True,
        help="自己分析用の動画ファイル"
    )
    strategy_parser.add_argument(
        "--opponent",
        help="対戦相手名"
    )
    strategy_parser.add_argument(
        "--opponent-video",
        help="相手分析用の動画ファイル"
    )
    strategy_parser.add_argument(
        "--opponent-team",
        help="相手所属チーム名"
    )
    
    # practice コマンド
    practice_parser = subparsers.add_parser(
        "practice",
        parents=[common_parser],
        help="練習計画を生成"
    )
    practice_parser.add_argument(
        "--video",
        help="分析する動画ファイル"
    )
    practice_parser.add_argument(
        "--analysis-file",
        help="既存の分析結果ファイル"
    )
    
    # full コマンド
    full_parser = subparsers.add_parser(
        "full",
        parents=[common_parser],
        help="フル分析（分析→戦略→練習計画）"
    )
    full_parser.add_argument(
        "--video",
        required=True,
        help="分析する動画ファイル"
    )
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        analyze_command(args)
    elif args.command == "strategy":
        strategy_command(args)
    elif args.command == "practice":
        if not args.video and not args.analysis_file:
            print("Error: --video または --analysis-file が必要です")
            return
        practice_command(args)
    elif args.command == "full":
        full_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
