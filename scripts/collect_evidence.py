"""
テストエビデンス自動収集スクリプト

各テスト実行後に以下を収集:
1. 入力データのメタ情報
2. 実行ログ
3. 出力データ
4. タイムスタンプ
5. Git情報
"""

import json
import hashlib
import datetime
import subprocess
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
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
    input_files: List[Dict[str, Any]] = field(default_factory=list)
    input_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # 実行
    execution_log: str = ""
    error_message: Optional[str] = None
    
    # 出力
    output_files: List[Dict[str, Any]] = field(default_factory=list)
    output_summary: Dict[str, Any] = field(default_factory=dict)
    
    # 検証
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    
    # メタデータ
    git_commit: str = ""
    git_branch: str = ""
    environment: Dict[str, str] = field(default_factory=dict)


class EvidenceCollector:
    """エビデンス収集クラス"""
    
    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_git_info(self) -> Dict[str, str]:
        """Git情報を取得"""
        try:
            commit = subprocess.getoutput("git rev-parse HEAD").strip()
            branch = subprocess.getoutput("git branch --show-current").strip()
            return {"commit": commit, "branch": branch}
        except Exception:
            return {"commit": "unknown", "branch": "unknown"}
    
    def get_environment_info(self) -> Dict[str, str]:
        """環境情報を取得"""
        return {
            "python_version": subprocess.getoutput("python --version").strip(),
            "os": subprocess.getoutput("uname -a").strip()[:100],
            "user": os.environ.get("USER", "unknown"),
            "hostname": subprocess.getoutput("hostname").strip()
        }
    
    def collect_file_info(self, file_path: str) -> Dict[str, Any]:
        """ファイル情報を収集"""
        path = Path(file_path)
        if not path.exists():
            return {"path": file_path, "exists": False}
        
        try:
            with open(path, "rb") as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
        except Exception as e:
            return {"path": file_path, "exists": True, "error": str(e)}
        
        return {
            "path": file_path,
            "exists": True,
            "size_bytes": path.stat().st_size,
            "sha256": file_hash,
            "modified_at": datetime.datetime.fromtimestamp(
                path.stat().st_mtime
            ).isoformat()
        }
    
    def create_evidence(
        self,
        test_id: str,
        test_name: str,
        status: str,
        duration: float,
        input_files: List[str] = None,
        output_files: List[str] = None,
        execution_log: str = "",
        error_message: str = None,
        assertions: List[Dict] = None
    ) -> TestEvidence:
        """エビデンスを作成"""
        git_info = self.get_git_info()
        env_info = self.get_environment_info()
        
        evidence = TestEvidence(
            test_id=test_id,
            test_name=test_name,
            timestamp=datetime.datetime.now().isoformat(),
            duration_seconds=duration,
            status=status,
            input_files=[self.collect_file_info(f) for f in (input_files or [])],
            output_files=[self.collect_file_info(f) for f in (output_files or [])],
            execution_log=execution_log,
            error_message=error_message,
            assertions=assertions or [],
            git_commit=git_info["commit"],
            git_branch=git_info["branch"],
            environment=env_info
        )
        
        return evidence
    
    def save_evidence(self, evidence: TestEvidence) -> str:
        """エビデンスを保存"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{evidence.test_id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(evidence), f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def generate_report(self, evidence_files: List[str] = None) -> str:
        """エビデンスレポートを生成"""
        if evidence_files is None:
            evidence_files = list(self.output_dir.glob("*.json"))
        
        evidences = []
        for file in evidence_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    evidences.append(json.load(f))
            except Exception as e:
                print(f"Warning: Failed to load {file}: {e}")
        
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_tests": len(evidences),
            "passed": sum(1 for e in evidences if e.get("status") == "passed"),
            "failed": sum(1 for e in evidences if e.get("status") == "failed"),
            "skipped": sum(1 for e in evidences if e.get("status") == "skipped"),
            "tests": evidences
        }
        
        report_path = self.output_dir / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(report_path)
    
    def generate_html_report(self, evidence_files: List[str] = None) -> str:
        """HTMLレポートを生成"""
        if evidence_files is None:
            evidence_files = list(self.output_dir.glob("*.json"))
        
        evidences = []
        for file in evidence_files:
            if "report_" in str(file):
                continue
            try:
                with open(file, "r", encoding="utf-8") as f:
                    evidences.append(json.load(f))
            except Exception:
                pass
        
        total = len(evidences)
        passed = sum(1 for e in evidences if e.get("status") == "passed")
        failed = sum(1 for e in evidences if e.get("status") == "failed")
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Evidence Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ 
            padding: 20px; 
            border-radius: 8px; 
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-width: 150px;
        }}
        .stat-card.passed {{ border-left: 4px solid #28a745; }}
        .stat-card.failed {{ border-left: 4px solid #dc3545; }}
        .stat-card.total {{ border-left: 4px solid #007bff; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background: #f8f9fa; }}
        
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-skipped {{ color: #ffc107; font-weight: bold; }}
        
        .details {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Test Evidence Report</h1>
        <p>Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-card total">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card passed">
                <div class="stat-value">{passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-value">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Timestamp</th>
                <th>Git Commit</th>
            </tr>
            {"".join(f'''
            <tr>
                <td>
                    <strong>{e.get("test_name", "N/A")}</strong>
                    <div class="details">{e.get("test_id", "")}</div>
                </td>
                <td class="status-{e.get('status', 'unknown')}">{e.get('status', 'N/A').upper()}</td>
                <td>{e.get("duration_seconds", 0):.2f}s</td>
                <td>{e.get("timestamp", "N/A")[:19]}</td>
                <td class="details">{e.get("git_commit", "N/A")[:8]}</td>
            </tr>
            ''' for e in sorted(evidences, key=lambda x: x.get("timestamp", ""), reverse=True))}
        </table>
    </div>
</body>
</html>"""
        
        report_path = self.output_dir / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return str(report_path)


if __name__ == "__main__":
    # テスト実行
    collector = EvidenceCollector()
    
    # サンプルエビデンスを作成
    evidence = collector.create_evidence(
        test_id="smoke_test_001",
        test_name="test_video_analysis_completes",
        status="passed",
        duration=15.5,
        input_files=["data/asami_match.mp4"],
        output_files=["output/analysis_result.json"],
        assertions=[
            {"name": "result_not_none", "passed": True},
            {"name": "has_basic_info", "passed": True}
        ]
    )
    
    # 保存
    filepath = collector.save_evidence(evidence)
    print(f"Evidence saved to: {filepath}")
    
    # レポート生成
    report_path = collector.generate_html_report()
    print(f"Report generated: {report_path}")
