# CI/CDパイプライン改善提案書

**プロジェクト名**: AI主導型 卓球パフォーマンス最大化システム  
**作成日**: 2026年1月4日  
**作成者**: Manus AI

---

## 1. エグゼクティブサマリー

本提案書は、「テスト成功報告と実動作の乖離」を防ぐための自動化ツールとCI/CDパイプラインの改善案を提示する。核心となる改善は、**実データを使用したスモークテストの必須化**と**多層的なテストゲートの自動化**である。

---

## 2. 現状の問題点

### 2.1 技術的問題

| 問題 | 原因 | 影響 |
|:---|:---|:---|
| モックテストのみ | 実APIを呼び出すテストがない | API障害を検出できない |
| 静的検証のみ | 動的な動作確認がない | ランタイムエラーを検出できない |
| 手動デプロイ | 自動化されていない | ヒューマンエラーのリスク |
| エビデンス不足 | テスト結果の保存がない | 事後検証ができない |

### 2.2 プロセス的問題

```
【現状のフロー】
開発 → テスト実行 → 「成功」報告 → デプロイ
         ↑
    モックのみで検証
    実データなし
    エビデンスなし
```

---

## 3. 改善案: 多層テストゲートCI/CDパイプライン

### 3.1 アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CI/CD パイプライン                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [コミット] → [Gate 0] → [Gate 1] → [Gate 2] → [Gate 3] → [デプロイ] │
│               ビルド     単体       統合       E2E                  │
│               スモーク   テスト     テスト     テスト                │
│                                                                     │
│  各ゲートで失敗 → パイプライン停止 → 通知 → エビデンス保存           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 各ゲートの詳細

#### Gate 0: ビルド＆スモークテスト（最重要）

**目的**: 「システムが起動し、基本機能が動作すること」を確認

```yaml
# .github/workflows/gate0-smoke.yml
name: Gate 0 - Build & Smoke Test

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master]

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-timeout
      
      - name: Download test video
        run: |
          # 実際のテスト用動画をダウンロード（小サイズ版）
          curl -L -o tests/fixtures/smoke_test_video.mp4 \
            "${{ secrets.TEST_VIDEO_URL }}"
      
      - name: Run smoke test with REAL video
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          # 実際の動画を使用したスモークテスト
          python -m pytest tests/smoke/ -v \
            --timeout=300 \
            --tb=long \
            2>&1 | tee smoke_test_output.log
      
      - name: Verify smoke test output
        run: |
          # 出力ファイルが生成されたことを確認
          test -f output/analysis_result.json
          test -f output/strategy_sheet.json
          test -f output/practice_plan.json
          
          # JSONが有効であることを確認
          python -c "import json; json.load(open('output/analysis_result.json'))"
          python -c "import json; json.load(open('output/strategy_sheet.json'))"
          python -c "import json; json.load(open('output/practice_plan.json'))"
      
      - name: Save evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gate0-evidence-${{ github.sha }}
          path: |
            smoke_test_output.log
            output/
          retention-days: 30
      
      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🚨 Gate 0 FAILED: Smoke test with real video failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Gate 0 Failed*\nCommit: ${{ github.sha }}\nBranch: ${{ github.ref }}\n\nSmoke test with real video failed. System may not be functional."
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**スモークテストの実装例**:

```python
# tests/smoke/test_smoke_real_video.py
"""
スモークテスト: 実際の動画を使用してシステム全体が動作することを確認

このテストは以下を検証する:
1. 動画ファイルを読み込めること
2. フレーム抽出が成功すること
3. LLM APIへの送信が成功すること
4. 分析結果が生成されること
5. 戦略シートが生成されること
6. 練習計画が生成されること
"""

import pytest
import json
import os
from pathlib import Path

# テスト用動画のパス
SMOKE_TEST_VIDEO = Path("tests/fixtures/smoke_test_video.mp4")
OUTPUT_DIR = Path("output")


class TestSmokeRealVideo:
    """実動画を使用したスモークテスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト前の準備"""
        OUTPUT_DIR.mkdir(exist_ok=True)
        assert SMOKE_TEST_VIDEO.exists(), f"テスト動画が見つかりません: {SMOKE_TEST_VIDEO}"
    
    def test_video_analysis_completes(self):
        """動画分析が完了すること"""
        from src.analysis.video_analyzer import VideoAnalyzer
        
        analyzer = VideoAnalyzer()
        result = analyzer.analyze(str(SMOKE_TEST_VIDEO))
        
        # 結果がNoneでないこと
        assert result is not None, "分析結果がNoneです"
        
        # 必須フィールドが存在すること
        assert "基本情報" in result, "基本情報が存在しません"
        assert "技術評価" in result, "技術評価が存在しません"
        assert "戦術分析" in result, "戦術分析が存在しません"
        
        # 結果を保存
        with open(OUTPUT_DIR / "analysis_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def test_strategy_generation_completes(self):
        """戦略シート生成が完了すること"""
        from src.strategy.generator import StrategyGenerator
        
        # 分析結果を読み込み
        with open(OUTPUT_DIR / "analysis_result.json", "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        generator = StrategyGenerator()
        result = generator.generate(analysis)
        
        # 結果がNoneでないこと
        assert result is not None, "戦略シートがNoneです"
        
        # 必須フィールドが存在すること
        assert "サーブ戦略" in result or "1.サーブ戦略" in result, "サーブ戦略が存在しません"
        
        # 結果を保存
        with open(OUTPUT_DIR / "strategy_sheet.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def test_practice_plan_generation_completes(self):
        """練習計画生成が完了すること"""
        from src.practice.planner import PracticePlanner
        
        # 分析結果を読み込み
        with open(OUTPUT_DIR / "analysis_result.json", "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        planner = PracticePlanner()
        result = planner.generate(analysis)
        
        # 結果がNoneでないこと
        assert result is not None, "練習計画がNoneです"
        
        # 必須フィールドが存在すること
        assert "優先課題" in result, "優先課題が存在しません"
        assert "週間計画" in result, "週間計画が存在しません"
        
        # 結果を保存
        with open(OUTPUT_DIR / "practice_plan.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def test_output_quality_basic(self):
        """出力の基本品質を確認"""
        # 分析結果の品質確認
        with open(OUTPUT_DIR / "analysis_result.json", "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        # 利き手が有効な値であること
        dominant_hand = analysis.get("基本情報", {}).get("利き手", "")
        assert dominant_hand in ["右", "左"], f"利き手が不正: {dominant_hand}"
        
        # グリップが有効な値であること
        grip = analysis.get("基本情報", {}).get("グリップ", "")
        assert grip in ["シェークハンド", "ペンホルダー", "シェイクハンド"], f"グリップが不正: {grip}"
        
        # 技術評価が1-5の範囲であること
        tech_eval = analysis.get("技術評価", {})
        for skill, score in tech_eval.items():
            if isinstance(score, (int, float)):
                assert 1 <= score <= 5, f"{skill}のスコアが範囲外: {score}"
```

#### Gate 1: 単体テスト

```yaml
# .github/workflows/gate1-unit.yml
name: Gate 1 - Unit Tests

on:
  workflow_run:
    workflows: ["Gate 0 - Build & Smoke Test"]
    types: [completed]

jobs:
  unit-tests:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      
      - name: Run unit tests with coverage
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -m pytest tests/unit/ \
            -v \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-fail-under=80 \
            2>&1 | tee unit_test_output.log
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
          fail_ci_if_error: true
      
      - name: Save evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gate1-evidence-${{ github.sha }}
          path: |
            unit_test_output.log
            htmlcov/
            coverage.xml
```

#### Gate 2: 統合テスト

```yaml
# .github/workflows/gate2-integration.yml
name: Gate 2 - Integration Tests

on:
  workflow_run:
    workflows: ["Gate 1 - Unit Tests"]
    types: [completed]

jobs:
  integration-tests:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      
      - name: Download test fixtures
        run: |
          curl -L -o tests/fixtures/integration_test_video.mp4 \
            "${{ secrets.TEST_VIDEO_URL }}"
      
      - name: Run integration tests with REAL API
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          USE_REAL_API: "true"
        run: |
          python -m pytest tests/integration/ \
            -v \
            --timeout=600 \
            -m "not slow" \
            2>&1 | tee integration_test_output.log
      
      - name: Validate integration outputs
        run: |
          python scripts/validate_integration_outputs.py
      
      - name: Save evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gate2-evidence-${{ github.sha }}
          path: |
            integration_test_output.log
            tests/integration/output/
```

#### Gate 3: E2Eテスト

```yaml
# .github/workflows/gate3-e2e.yml
name: Gate 3 - E2E Tests

on:
  workflow_run:
    workflows: ["Gate 2 - Integration Tests"]
    types: [completed]

jobs:
  e2e-tests:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    timeout-minutes: 45
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      
      - name: Download E2E test fixtures
        run: |
          # 複数のテスト動画をダウンロード
          curl -L -o tests/fixtures/e2e_video_1.mp4 "${{ secrets.E2E_VIDEO_1_URL }}"
          curl -L -o tests/fixtures/e2e_video_2.mp4 "${{ secrets.E2E_VIDEO_2_URL }}"
      
      - name: Run E2E tests with REAL videos
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -m pytest tests/e2e/ \
            -v \
            --timeout=900 \
            2>&1 | tee e2e_test_output.log
      
      - name: Generate E2E test report
        run: |
          python scripts/generate_e2e_report.py \
            --output reports/e2e_report.html
      
      - name: Save evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gate3-evidence-${{ github.sha }}
          path: |
            e2e_test_output.log
            tests/e2e/output/
            reports/
      
      - name: Notify success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ All Gates Passed! Ready for deployment.",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*All Gates Passed*\nCommit: ${{ github.sha }}\n\n✅ Gate 0: Smoke Test\n✅ Gate 1: Unit Tests\n✅ Gate 2: Integration Tests\n✅ Gate 3: E2E Tests"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 4. エビデンス自動収集システム

### 4.1 エビデンス収集スクリプト

```python
# scripts/collect_evidence.py
"""
テストエビデンス自動収集スクリプト

各テスト実行後に以下を収集:
1. 入力データのメタ情報
2. 実行ログ
3. 出力データ
4. スクリーンショット（該当する場合）
5. タイムスタンプ
"""

import json
import hashlib
import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


@dataclass
class TestEvidence:
    """テストエビデンスのデータ構造"""
    test_id: str
    test_name: str
    timestamp: str
    duration_seconds: float
    status: str  # "passed", "failed", "skipped"
    
    # 入力
    input_files: List[Dict[str, Any]]  # ファイル名、サイズ、ハッシュ
    input_parameters: Dict[str, Any]
    
    # 実行
    execution_log: str
    error_message: Optional[str]
    
    # 出力
    output_files: List[Dict[str, Any]]  # ファイル名、サイズ、ハッシュ
    output_summary: Dict[str, Any]
    
    # 検証
    assertions: List[Dict[str, Any]]  # 各アサーションの結果
    
    # メタデータ
    git_commit: str
    git_branch: str
    environment: Dict[str, str]


class EvidenceCollector:
    """エビデンス収集クラス"""
    
    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_file_info(self, file_path: str) -> Dict[str, Any]:
        """ファイル情報を収集"""
        path = Path(file_path)
        if not path.exists():
            return {"path": file_path, "exists": False}
        
        with open(path, "rb") as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()
        
        return {
            "path": file_path,
            "exists": True,
            "size_bytes": path.stat().st_size,
            "sha256": file_hash,
            "modified_at": datetime.datetime.fromtimestamp(
                path.stat().st_mtime
            ).isoformat()
        }
    
    def save_evidence(self, evidence: TestEvidence) -> str:
        """エビデンスを保存"""
        filename = f"{evidence.timestamp}_{evidence.test_id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(evidence), f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def generate_report(self, evidences: List[TestEvidence]) -> str:
        """エビデンスレポートを生成"""
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_tests": len(evidences),
            "passed": sum(1 for e in evidences if e.status == "passed"),
            "failed": sum(1 for e in evidences if e.status == "failed"),
            "skipped": sum(1 for e in evidences if e.status == "skipped"),
            "tests": [asdict(e) for e in evidences]
        }
        
        report_path = self.output_dir / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(report_path)
```

### 4.2 pytest プラグインとしての実装

```python
# conftest.py
"""
pytest用エビデンス収集プラグイン
"""

import pytest
import json
import time
import subprocess
from pathlib import Path
from scripts.collect_evidence import EvidenceCollector, TestEvidence


@pytest.fixture(scope="session")
def evidence_collector():
    """エビデンス収集器のフィクスチャ"""
    return EvidenceCollector(output_dir="evidence")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """各テストの実行結果を収集"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # テスト結果をエビデンスとして保存
        evidence_dir = Path("evidence")
        evidence_dir.mkdir(exist_ok=True)
        
        evidence = {
            "test_name": item.name,
            "test_file": str(item.fspath),
            "status": report.outcome,
            "duration": report.duration,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "git_commit": subprocess.getoutput("git rev-parse HEAD"),
            "git_branch": subprocess.getoutput("git branch --show-current"),
        }
        
        if report.failed:
            evidence["error"] = str(report.longrepr)
        
        # エビデンスを保存
        evidence_file = evidence_dir / f"{item.name}_{int(time.time())}.json"
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
```

---

## 5. 実データ管理システム

### 5.1 テストデータリポジトリ

```yaml
# .github/workflows/sync-test-data.yml
name: Sync Test Data

on:
  schedule:
    - cron: '0 0 * * 0'  # 毎週日曜日
  workflow_dispatch:

jobs:
  sync-test-data:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download test videos from S3
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws s3 sync s3://tt-performance-test-data/videos/ tests/fixtures/videos/
      
      - name: Verify test data integrity
        run: |
          python scripts/verify_test_data.py
      
      - name: Update test data manifest
        run: |
          python scripts/update_manifest.py
```

### 5.2 テストデータマニフェスト

```json
// tests/fixtures/manifest.json
{
  "version": "1.0.0",
  "updated_at": "2026-01-04T00:00:00Z",
  "videos": [
    {
      "id": "smoke_test_video",
      "filename": "smoke_test_video.mp4",
      "description": "スモークテスト用の短い試合動画（30秒）",
      "duration_seconds": 30,
      "size_bytes": 5242880,
      "sha256": "abc123...",
      "player_info": {
        "dominant_hand": "右",
        "grip": "シェークハンド",
        "play_style": "ドライブ主戦型"
      },
      "expected_outputs": {
        "analysis": {
          "dominant_hand": "右",
          "grip": "シェークハンド"
        }
      }
    },
    {
      "id": "integration_test_video",
      "filename": "integration_test_video.mp4",
      "description": "統合テスト用の試合動画（3分）",
      "duration_seconds": 180,
      "size_bytes": 52428800,
      "sha256": "def456..."
    }
  ]
}
```

---

## 6. 監視とアラート

### 6.1 テスト品質ダッシュボード

```python
# scripts/generate_dashboard.py
"""
テスト品質ダッシュボード生成スクリプト
"""

import json
from pathlib import Path
from datetime import datetime, timedelta


def generate_dashboard():
    """ダッシュボードHTMLを生成"""
    evidence_dir = Path("evidence")
    evidences = []
    
    for file in evidence_dir.glob("*.json"):
        with open(file) as f:
            evidences.append(json.load(f))
    
    # 過去7日間のデータを集計
    recent = [e for e in evidences 
              if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(days=7)]
    
    stats = {
        "total": len(recent),
        "passed": sum(1 for e in recent if e["status"] == "passed"),
        "failed": sum(1 for e in recent if e["status"] == "failed"),
        "pass_rate": sum(1 for e in recent if e["status"] == "passed") / len(recent) * 100 if recent else 0
    }
    
    # HTMLダッシュボードを生成
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Quality Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .stats {{ display: flex; gap: 20px; }}
            .stat-card {{ padding: 20px; border-radius: 8px; background: #f5f5f5; }}
            .stat-card.passed {{ background: #d4edda; }}
            .stat-card.failed {{ background: #f8d7da; }}
            .stat-value {{ font-size: 2em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Test Quality Dashboard</h1>
        <p>Generated: {datetime.now().isoformat()}</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{stats['total']}</div>
                <div>Total Tests (7 days)</div>
            </div>
            <div class="stat-card passed">
                <div class="stat-value">{stats['passed']}</div>
                <div>Passed</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-value">{stats['failed']}</div>
                <div>Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['pass_rate']:.1f}%</div>
                <div>Pass Rate</div>
            </div>
        </div>
        
        <h2>Recent Test Results</h2>
        <table border="1" cellpadding="8">
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Timestamp</th>
            </tr>
            {"".join(f'''
            <tr>
                <td>{e.get("test_name", "N/A")}</td>
                <td style="color: {'green' if e['status'] == 'passed' else 'red'}">{e['status']}</td>
                <td>{e.get("duration", 0):.2f}s</td>
                <td>{e.get("timestamp", "N/A")}</td>
            </tr>
            ''' for e in sorted(recent, key=lambda x: x.get("timestamp", ""), reverse=True)[:20])}
        </table>
    </body>
    </html>
    """
    
    with open("reports/dashboard.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    generate_dashboard()
```

### 6.2 アラート設定

```yaml
# .github/workflows/alert-on-failure.yml
name: Alert on Test Failure

on:
  workflow_run:
    workflows: ["Gate 0 - Build & Smoke Test", "Gate 1 - Unit Tests", "Gate 2 - Integration Tests", "Gate 3 - E2E Tests"]
    types: [completed]

jobs:
  alert:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    
    steps:
      - name: Send Slack Alert
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🚨 Test Pipeline Failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Test Pipeline Failed*\n\nWorkflow: ${{ github.event.workflow_run.name }}\nCommit: ${{ github.event.workflow_run.head_sha }}\nBranch: ${{ github.event.workflow_run.head_branch }}\n\n<${{ github.event.workflow_run.html_url }}|View Details>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Create GitHub Issue
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `🚨 Test Failure: ${context.payload.workflow_run.name}`,
              body: `## Test Pipeline Failed
              
              - **Workflow**: ${context.payload.workflow_run.name}
              - **Commit**: ${context.payload.workflow_run.head_sha}
              - **Branch**: ${context.payload.workflow_run.head_branch}
              - **Details**: ${context.payload.workflow_run.html_url}
              
              Please investigate and fix the issue.`,
              labels: ['bug', 'test-failure', 'high-priority']
            })
```

---

## 7. 導入ロードマップ

### 7.1 フェーズ別導入計画

| フェーズ | 期間 | 内容 | 成果物 |
|:---|:---|:---|:---|
| Phase 1 | 1週間 | Gate 0（スモークテスト）の導入 | smoke test workflow |
| Phase 2 | 1週間 | エビデンス収集システムの導入 | evidence collector |
| Phase 3 | 1週間 | Gate 1-3の自動化 | full CI/CD pipeline |
| Phase 4 | 1週間 | 監視・アラートの導入 | dashboard, alerts |

### 7.2 必要なリソース

| リソース | 用途 | 見積もりコスト |
|:---|:---|:---|
| GitHub Actions | CI/CD実行 | 無料（パブリックリポジトリ） |
| AWS S3 | テストデータ保存 | $5/月 |
| Slack | アラート通知 | 無料 |
| OpenAI API | テスト実行 | $10-50/月（テスト頻度による） |

---

## 8. 結論

本提案の核心は、**「実データを使用したスモークテストをCI/CDパイプラインの最初のゲートとして必須化する」**ことである。これにより、「テストは通るが実際には動かない」という問題を根本的に防止できる。

### 主要な改善点

1. **Gate 0（スモークテスト）の新設**: 実動画を使用した動作確認を最初に実施
2. **エビデンス自動収集**: 入力・出力・ログを自動保存
3. **多層ゲート**: 各ゲートを通過しないと次に進めない
4. **監視・アラート**: 失敗時の即座の通知とIssue作成

### 期待される効果

- 「テスト成功報告と実動作の乖離」の防止
- 問題の早期発見
- エビデンスに基づく品質保証
- 開発者の信頼性向上
