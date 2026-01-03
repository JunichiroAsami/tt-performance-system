# WBS (Work Breakdown Structure) - AI卓球パフォーマンス最大化システム

**プロジェクト名**: AI主導型 卓球パフォーマンス最大化システム  
**作成日**: 2026年1月3日  
**更新日**: 2026年1月3日  
**作成者**: Manus AI

---

## 1.0 プロジェクト管理

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 1.1 | プロジェクト計画策定 | ユーザー要件（口頭） | WBS、スケジュール | Manus AI | 完了 |
| 1.2 | 進捗管理と報告 | WBS | 週次進捗報告 | Manus AI | 進行中 |
| 1.3 | ドキュメント管理 | 全成果物 | GitHubリポジトリ | Manus AI | 進行中 |

---

## 2.0 要件定義

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 2.1 | 業務要件定義 | ユーザー要件、動画サンプル | `business_requirements_document.md` | Manus AI | 完了 |
| 2.2 | システム要件定義 | 業務要件書 | `development_spec.md` | Manus AI | 完了 |

---

## 3.0 設計

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 3.1 | 概要設計 | 業務要件書、システム要件書 | `system_architecture_design.md`, `architecture_diagram.png` | Manus AI | 完了 |
| 3.2 | 詳細設計 | 概要設計書 | 各モジュール詳細設計書 | Manus AI | 一部完了 |
| 3.2.1 | 分析エンジン詳細設計 | 概要設計書 | `analysis_engine_design.md` | Manus AI | 未着手 |
| 3.2.2 | データベース設計 | 概要設計書 | `database_design.md` | Manus AI | 未着手 |
| 3.2.3 | UI/UX設計（将来拡張） | 概要設計書 | `ui_ux_design.md` | Manus AI | 未着手 |

---

## 4.0 実装 (Phase 1: 定性分析)

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 4.1 | 開発環境構築 | システム要件書 | `requirements.txt`, `config/settings.yaml` | Manus AI | 完了 |
| 4.2 | プロジェクト構造設定 | 概要設計書 | ディレクトリ構造、`.gitignore` | Manus AI | 完了 |
| 4.3 | 定性分析モジュール実装 | 概要設計書、プロンプト設計 | `llm_analyzer.py`, `prompts.py` | Manus AI | 完了 |
| 4.4 | レポート生成モジュール実装 | 概要設計書 | `report_generator.py` | Manus AI | 完了 |
| 4.5 | CLIインターフェース実装 | 概要設計書 | `main.py` | Manus AI | 完了 |

---

## 5.0 テスト

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 5.1 | テスト計画 | 業務要件書、システム要件書 | `test_scenarios.md` | Manus AI | 完了 |
| 5.2 | 単体テスト実装 | テスト計画、ソースコード | `tests/unit/*.py` | Manus AI | 完了 |
| 5.3 | 統合テスト実装 | テスト計画、ソースコード | `tests/integration/*.py` | Manus AI | 完了 |
| 5.4 | E2Eテスト実装 | テスト計画、ソースコード | `tests/e2e/*.py` | Manus AI | 完了 |
| 5.5 | テスト実行と結果報告 | テストコード | テスト結果レポート | Manus AI | 完了 |

---

## 6.0 デプロイと運用

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 6.1 | GitHubへのプッシュ | 全ソースコード、ドキュメント | コミットログ、リポジトリ | Manus AI | 完了 |
| 6.2 | 運用マニュアル作成 | 全成果物 | `README.md`, `manual.md` | Manus AI | 一部完了 |

---

## 7.0 実装 (Phase 2: 定量分析) - 将来拡張

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 7.1 | 定量分析モジュール設計 | 概要設計書 | `cv_analyzer_design.md` | Manus AI | 未着手 |
| 7.2 | ボールトラッキング実装 | 定量分析設計書 | `ball_tracker.py` (OpenCV) | Manus AI | 未着手 |
| 7.3 | 姿勢推定実装 | 定量分析設計書 | `pose_estimator.py` (MediaPipe) | Manus AI | 未着手 |
| 7.4 | 統合分析モジュール実装 | Phase 1成果物、定量分析モジュール | `integrated_analyzer.py` | Manus AI | 未着手 |

---

## 8.0 実装 (Phase 3: データ管理・UI) - 将来拡張

| WBS ID | タスク名 | インプット | 成果物 | 担当 | 状態 |
|:---|:---|:---|:---|:---|:---|
| 8.1 | データベース連携実装 | データベース設計書 | `database.py` (SQLite) | Manus AI | 未着手 |
| 8.2 | Web UI実装 | UI/UX設計書 | Flask/FastAPIアプリケーション | Manus AI | 未着手 |

---

## 成果物一覧

| カテゴリ | 成果物 | パス | 状態 |
|:---|:---|:---|:---|
| **要件** | 業務要件書 | `docs/business_requirements.md` | 完了 |
| **設計** | 概要設計書 | `docs/system_architecture.md` | 完了 |
| **設計** | アーキテクチャ図 | `docs/architecture_diagram.png` | 完了 |
| **設計** | 開発仕様書 | `docs/development_spec.md` | 完了 |
| **テスト** | テストシナリオ | `docs/test_scenarios.md` | 完了 |
| **管理** | WBS | `docs/WBS.md` | 完了 |
| **コード** | 分析モジュール | `src/analysis/` | 完了 |
| **コード** | 出力モジュール | `src/output/` | 完了 |
| **コード** | メインCLI | `src/main.py` | 完了 |
| **テスト** | 単体テスト | `tests/unit/` | 完了 |
| **テスト** | 統合テスト | `tests/integration/` | 完了 |
| **テスト** | E2Eテスト | `tests/e2e/` | 完了 |
| **設定** | 依存関係 | `requirements.txt` | 完了 |
| **設定** | 設定ファイル | `config/settings.yaml` | 完了 |
| **運用** | README | `README.md` | 完了 |

---

## 依存関係

```
2.1 業務要件定義
    ↓
2.2 システム要件定義
    ↓
3.1 概要設計
    ↓
┌───────────────┬───────────────┐
↓               ↓               ↓
4.x Phase 1   7.x Phase 2   8.x Phase 3
実装           実装（将来）    実装（将来）
    ↓
5.x テスト
    ↓
6.x デプロイ
```
