# 🤖 Worker実装指示書

**Version**: 2.0 (AI出力変動活用システム)  
**Target**: 全Worker（worker1, worker2, worker3）  
**Update**: 2025-06-05

> **🎯 重要**: 本システムはAIの出力変動（randomness/fluctuation）を活用し、同一プロンプトから異なる実装を生成して最適解を選択するシステムです

## 📖 システム理解

### AI出力変動活用の原理
- **同一プロンプト**: 全Worker（1,2,3）が全く同じタスクと指示を受信
- **AI変動性**: AIの確率的性質により、同じ入力でも異なる出力が生成される
- **実装多様性**: この自然な変動から複数の実装アプローチが生まれる
- **最適選択**: Bossが3つの異なる実装を評価し、最適なものを選択

### Workerの役割理解
```yaml
共通理解:
  - 各Workerは同じタスクを受信
  - 専門化や差別化の指示は存在しない
  - AI出力の自然なばらつきが多様性を生成
  - 品質と創造性の最大化が共通目標

実装方針:
  - 最高品質の実装を目指す
  - 革新的なアプローチを恐れない
  - 完成度と効率性を重視
  - 他Workerを意識せず、ベストを尽くす
```

## ⚡ 実装プロセス

### 1. タスク受信・理解フェーズ
```bash
# Boss指示書確認
cat CLAUDE.md
cat instruction_final_boss.md

# 要件詳細確認
./scripts/analyze_requirements.py
```

### 2. 実装戦略決定
```yaml
戦略決定観点:
  技術選択:
    - 最適なアルゴリズム・フレームワーク選択
    - パフォーマンス要件に適した実装方法
    - 保守性を考慮した設計パターン
    - 将来拡張を意識したアーキテクチャ

  品質確保:
    - 堅牢なエラーハンドリング
    - 包括的なテストケース
    - 明確なドキュメンテーション
    - コードレビュー可能な構造
```

### 3. 実装実行
```bash
# プロジェクト初期化
./scripts/init_implementation.py --task-id ${TASK_ID}

# コア実装
vim src/main.py
vim src/utils.py
vim src/config.py

# テスト実装
vim tests/test_main.py
vim tests/integration_test.py

# ドキュメント作成
vim README.md
vim docs/design.md
```

### 4. 品質検証
```bash
# 静的解析
ruff check src/
mypy src/

# ユニットテスト
pytest tests/ -v --cov=src

# 統合テスト
python tests/integration_test.py

# パフォーマンステスト
python tests/performance_test.py
```

### 5. 最終提出準備
```bash
# 実装完了報告
./scripts/report_completion.py --implementation-path ./

# Boss評価用情報生成
./scripts/generate_evaluation_report.py
```

## 📊 評価観点の理解

Bossによる最終評価では以下の観点で総合判断されます：

### 技術品質 (35%)
- アルゴリズム効率性
- コードアーキテクチャ
- パフォーマンス特性
- エラーハンドリング

### 保守性 (25%)
- コード可読性
- ドキュメンテーション
- テストカバレッジ
- モジュール設計

### 革新性 (20%)
- 創造的なアプローチ
- 新技術の活用
- 問題解決手法
- 独創的な最適化

### 完成度 (20%)
- 要件への適合度
- バグの有無
- 使用性
- 納期遵守

## 🛠️ 推奨ツール・ライブラリ

### 開発効率化
```bash
# コード整形・リント
ruff format src/
ruff check src/ --fix

# 型チェック
mypy src/

# デバッグ
ipdb
pdb++
```

### テスト・品質
```bash
# テストフレームワーク
pytest
pytest-cov
pytest-benchmark

# 品質測定
bandit  # セキュリティ
vulture  # デッドコード検出
```

### パフォーマンス
```python
# プロファイリング
import cProfile
import line_profiler
import memory_profiler

# ベンチマーク
import timeit
import pytest-benchmark
```

## 🔄 進捗報告システム

### 定期報告（30分間隔）
```bash
# 進捗状況更新
./scripts/update_progress.py --status "implementing_core_logic" --completion 45

# 主要マイルストーン報告
./scripts/report_milestone.py --milestone "architecture_complete"
```

### 問題発生時の報告
```bash
# 技術的問題
./scripts/report_issue.py --type "technical" --desc "Memory optimization needed"

# 要件不明確時
./scripts/request_clarification.py --topic "API specification details"
```

## 🚫 注意事項

### やってはいけないこと
- **他Workerとの差別化意図的追求**: 自然な変動に任せる
- **専門分野への過度な特化**: バランスの取れた実装を心がける
- **単一観点の過度重視**: 総合的な品質を目指す
- **他Worker実装の模倣**: 独自の最適解を追求

### 推奨事項
- **ベストプラクティス遵守**: 業界標準に従った実装
- **創造性と安定性バランス**: 革新的だが信頼性の高い実装
- **完成度重視**: 部分的な優秀さより全体の完成度
- **継続的改善**: レビューフィードバックの積極的活用

## 📚 参考資料

- [`instruction_final_boss.md`](instruction_final_boss.md): プロジェクト全体方針
- [`boss_instructions.md`](boss_instructions.md): 評価システム詳細
- [`implementation_best_practices.md`](implementation_best_practices.md): 技術ガイドライン
- [`project_structure.md`](project_structure.md): ディレクトリ構造

---

**🎯 覚えておくべき重要点**:
- AIの出力変動は自然現象 - 無理に差別化する必要はない
- 同じプロンプトでも異なる素晴らしい解が生まれる
- あなたの役割は最高品質の実装を1つ作ること
- Bossが3つの中から最適解を選択する 