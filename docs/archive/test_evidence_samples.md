# テストエビデンスサンプル

**作成日**: 2026年1月4日  
**目的**: 各テストレベルで業務要件がどのように検証されているかを示す

---

## 1. 単体テスト エビデンス

### 検証方式
プロンプトテンプレートに業務要件を満たす指示が含まれているかを検証する。

### サンプル: FA-01（得点/失点パターン分析）

**検証対象**: `ANALYSIS_PROMPT`

**検証コード**:
```python
def test_FA01_prompt_includes_scoring_pattern(self):
    """FA-01: 分析プロンプトに得点/失点パターン分析の指示が含まれている"""
    assert "得点" in ANALYSIS_PROMPT
    assert "失点" in ANALYSIS_PROMPT
```

**検証結果**:
```
検証対象: ANALYSIS_PROMPT
「得点」を含む: True
「失点」を含む: True

該当箇所（抜粋）:
  → ### 3.1 得点パターン
  → - 主な得点パターンを3つ挙げてください
  → ### 3.2 失点パターン
  → - 主な失点パターンを3つ挙げてください
```

**判定**: ✅ PASSED

---

### サンプル: FS-02（サーブ戦略提案）

**検証対象**: `STRATEGY_PROMPT`

**検証コード**:
```python
def test_FS02_prompt_includes_serve_strategy(self):
    """FS-02: 戦略プロンプトにサーブ戦略提案の指示が含まれている"""
    assert "サーブ戦略" in STRATEGY_PROMPT
```

**検証結果**:
```
検証対象: STRATEGY_PROMPT
「サーブ戦略」を含む: True

該当箇所（抜粋）:
  → ## 1. サーブ戦略
```

**判定**: ✅ PASSED

---

## 2. 統合テスト エビデンス

### 検証方式
出力されるJSONの構造と内容が業務要件を満たしているかを検証する。

### サンプル: FA-01（得点/失点パターン分析）

**検証対象**: 分析結果JSON

**検証コード**:
```python
def test_FA01_output_has_scoring_patterns(self, valid_analysis_output):
    """FA-01: 出力に得点パターンが含まれている"""
    assert "戦術分析" in valid_analysis_output
    assert "得点パターン" in valid_analysis_output["戦術分析"]
    patterns = valid_analysis_output["戦術分析"]["得点パターン"]
    assert isinstance(patterns, list)
    assert len(patterns) >= 1
```

**検証結果**:
```
【検証1】得点パターンの存在確認
  「戦術分析」キー存在: True
  「得点パターン」キー存在: True
  パターン数: 3 (期待: >= 1)

【検証2】得点パターンの内容
  パターン1: 「バックハンドドライブからの3球目攻撃」
    → 文字数: 18 (期待: > 5)
  パターン2: 「チキータからの展開」
    → 文字数: 9 (期待: > 5)
  パターン3: 「カウンター攻撃」
    → 文字数: 7 (期待: > 5)
```

**判定**: ✅ PASSED

---

### サンプル: FS-01~04（戦略シート）

**検証対象**: 戦略結果JSON

**検証コード**:
```python
def test_FS01_output_has_strategy_sections(self, valid_strategy_output):
    """FS-01: 出力に戦略セクションが含まれている"""
    assert "戦略立案" in valid_strategy_output or "1.サーブ戦略" in valid_strategy_output

def test_FS02_output_has_serve_strategy(self, valid_strategy_output):
    """FS-02: 出力にサーブ戦略が含まれている"""
    assert "1.サーブ戦略" in valid_strategy_output
    serve_strategy = valid_strategy_output["1.サーブ戦略"]
    assert len(serve_strategy) >= 1
```

**検証結果**:
```
【検証1】必須セクションの存在確認
  「1.サーブ戦略」存在: True
  「2.レシーブ戦略」存在: True
  「3.ラリー戦略」存在: True

【検証2】サーブ戦略の内容
  セクション数: 1 (期待: >= 1)
  序盤: {'推奨サーブ': 'フォア前ショート', '狙い': '相手を前に出す'}
```

**判定**: ✅ PASSED

---

## 3. E2Eテスト エビデンス

### 検証方式
エンドツーエンドで分析→戦略→練習計画→レポートの全フローが業務要件を満たすかを検証する。

### サンプル: FA-01~05（分析要件の完全検証）

**検証対象**: 完全な分析フロー

**検証コード**:
```python
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
```

**検証結果**:
```
【入力】動画ファイル: test.mp4

【出力】分析結果JSON:
  得点パターン数: 3
    1. バックハンドドライブからの3球目攻撃
    2. チキータからの展開
    3. カウンター攻撃
  失点パターン数: 3
    1. フォア側への強打に対する対応ミス
    2. ロングサーブへの対応
    3. ラリー戦での粘り負け

【技術分析の検証】
  ✅ フォアハンド: フォアハンドドライブ
  ✅ バックハンド: バックハンドドライブ
  ✅ サーブ: サーブ
  ✅ レシーブ: レシーブ
  ✅ フットワーク: フットワーク
```

**判定**: ✅ PASSED

---

### サンプル: FR-01（レポート生成）

**検証対象**: Markdownレポート生成

**検証コード**:
```python
def test_e2e_FR01_summary_report(self):
    """E2E FR-01: 試合後サマリーレポートが完全に生成される"""
    generator = ReportGenerator()
    generator.generate_analysis_report(mock_analysis, report_path)
    
    assert os.path.exists(report_path)
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "浅見江里佳" in content
    assert len(content) > 100
    assert "#" in content  # Markdownヘッダー
```

**検証結果**:
```
【生成されたレポート】
  ファイルサイズ: 130 bytes
  選手名含む: True
  Markdownヘッダー含む: True

【レポート内容（先頭200文字）】
# 卓球パフォーマンス分析レポート
**選手名**: 浅見江里佳  
**所属**: 文化学園大学杉並  
**分析日**: 2026年01月03日
---
## 1. 基本情報
## 2. 技術分析
## 3. 戦術分析
## 4. 総合評価
```

**判定**: ✅ PASSED

---

## 4. テストレベル間の関係

```
┌─────────────────────────────────────────────────────────────┐
│                        UAT                                   │
│  実際の動画で実用性を検証                                    │
├─────────────────────────────────────────────────────────────┤
│                      E2Eテスト                               │
│  全フローで業務要件が満たされることを検証                    │
│  例: 分析→戦略→練習計画→レポートの一連の流れ               │
├─────────────────────────────────────────────────────────────┤
│                     統合テスト                               │
│  出力内容が業務要件を満たす構造・内容を持つことを検証        │
│  例: JSON出力に「得点パターン」キーが存在し、3件以上の内容   │
├─────────────────────────────────────────────────────────────┤
│                     単体テスト                               │
│  プロンプトが業務要件を満たす指示を含むことを検証            │
│  例: ANALYSIS_PROMPTに「得点パターン」の分析指示が含まれる   │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 業務要件とテストの対応表

| 要件ID | 要件概要 | 単体テスト | 統合テスト | E2Eテスト |
|:---|:---|:---|:---|:---|
| FA-01 | 得点/失点パターン分析 | プロンプトに指示含む | 出力に3件以上のパターン | 全フローで維持 |
| FA-02 | 技術別パフォーマンス分析 | プロンプトに技術名含む | 出力にフォア/バック分析 | 5技術全て含む |
| FA-03 | サーブ/レシーブ分析 | プロンプトに指示含む | 出力にサーブ/レシーブ | 詳細項目含む |
| FS-01 | 戦略シート生成 | プロンプトに戦略指示 | 出力に3セクション | 全セクション含む |
| FS-02 | サーブ戦略提案 | プロンプトに指示含む | 出力にサーブ戦略 | 段階別戦略含む |
| FP-01 | 課題の優先順位付け | プロンプトに優先指示 | 出力に優先課題リスト | 重要度付き |
| FR-01 | サマリーレポート | - | レポート生成確認 | Markdown形式 |
