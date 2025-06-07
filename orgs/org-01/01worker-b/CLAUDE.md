# 🤖 Worker実装指示書

**Version**: 3.0 (チェックリスト駆動ワークフロー)  
**Target**: 全Worker（worker-a, worker-b, worker-c）  
**Update**: 2025-06-06

> **🎯 重要**: 本システムはチェックリスト駆動でBossから受け取ったタスクを実装し、完了時に他Workerと連携して最終報告を行うシステムです

## 🚀 現在のタスク: ハローワールドモジュール作成

### タスク概要
**あなたのミッション**: "Hello, World!" を出力するモジュールを実装してください

### 具体的要件
```yaml
モジュール名: hello_world
実装必須項目:
  - "Hello, World!" を出力する関数
  - コマンドライン実行可能
  - ユニットテスト完備
  - 詳細ドキュメント
  - エラーハンドリング

ファイル構成:
  - src/hello_world/core.py       # メイン実装
  - src/hello_world/__init__.py   # モジュール初期化
  - src/hello_world/cli.py        # CLI実行
  - tests/test_hello_world.py     # ユニットテスト
  - docs/hello_world.md           # ドキュメント

品質基準:
  - テストカバレッジ100%
  - 型アノテーション完備
  - リンターエラーなし
  - 実行時間1秒以内
  - PEP8準拠
```

### 実装例（参考）
```python
# src/hello_world/core.py
def hello_world() -> str:
    """Hello, Worldを返す関数"""
    return "Hello, World!"

def print_hello_world() -> None:
    """Hello, Worldを出力する関数"""
    print(hello_world())

# CLI実行
if __name__ == "__main__":
    print_hello_world()
```

### Worker実行手順
```bash
# 1. チェックリスト確認
cat WORKER_CHECKLIST.md

# 2. 実装開始
mkdir -p src/hello_world tests docs
touch src/hello_world/{__init__.py,core.py,cli.py}
touch tests/test_hello_world.py
touch docs/hello_world.md

# 3. 実装完了後チェック
pytest tests/ --cov=src
ruff check src/
mypy src/

# 4. 実装完成をチェックリストにマーク
sed -i 's/\[ \] \*\*実装完成\*\*/[x] **実装完成**/' WORKER_CHECKLIST.md

# 5. 全Worker完了チェック＆Boss報告（自動）
../../scripts/check_all_workers_done.sh

# または手動で他Worker確認
# ORG_NUM=$(pwd | grep -o 'org-[0-9][0-9]' | tail -1)
# grep "\[x\] \*\*実装完成\*\*" ../01worker-*/WORKER_CHECKLIST.md
```

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

## ⚡ チェックリスト駆動実装プロセス

### 1. タスク受信・チェックリスト確認
```bash
# Boss通知確認
ls ../../../shared_messages/to_worker-*.md

# Workerチェックリスト確認
cat WORKER_CHECKLIST.md

# Boss指示書確認
cat CLAUDE.md
```

### 2. チェックリスト駆動実装
```bash
# チェックリスト項目に沿って順次実装
# 各項目完了時にチェックマーク更新

# 要件理解・設計フェーズ
vim WORKER_CHECKLIST.md  # 設計項目チェック

# コア実装フェーズ
vim src/[module]/  # 実装
vim WORKER_CHECKLIST.md  # 実装項目チェック

# テスト実装フェーズ
vim tests/  # テスト作成
vim WORKER_CHECKLIST.md  # テスト項目チェック

# ドキュメント作成フェーズ
vim docs/  # ドキュメント作成
vim WORKER_CHECKLIST.md  # ドキュメント項目チェック
```

### 3. 品質確認・自己チェック
```bash
# 全項目完了確認
grep "\[ \]" WORKER_CHECKLIST.md  # 未完了項目確認

# 品質基準クリア確認
pytest tests/ --cov=src
ruff check src/
mypy src/

# 自己確認完了
vim WORKER_CHECKLIST.md  # "実装完成"にチェック
```

### 4. 他Worker確認・最終報告
```bash
# 自分の実装完成後、他Workerチェック開始
echo "🔍 他Workerの完成状況を確認中..."

# 現在の組織番号を取得
ORG_NUM=$(pwd | grep -o 'org-[0-9][0-9]' | tail -1)

# 他Workerの完成状況確認
WORKER_A_DONE=$(grep "\[x\] \*\*実装完成\*\*" ../01worker-a/WORKER_CHECKLIST.md 2>/dev/null && echo "1" || echo "0")
WORKER_B_DONE=$(grep "\[x\] \*\*実装完成\*\*" ../01worker-b/WORKER_CHECKLIST.md 2>/dev/null && echo "1" || echo "0")
WORKER_C_DONE=$(grep "\[x\] \*\*実装完成\*\*" ../01worker-c/WORKER_CHECKLIST.md 2>/dev/null && echo "1" || echo "0")

echo "Worker-A: $([ $WORKER_A_DONE -eq 1 ] && echo '✅完了' || echo '⏳作業中')"
echo "Worker-B: $([ $WORKER_B_DONE -eq 1 ] && echo '✅完了' || echo '⏳作業中')"
echo "Worker-C: $([ $WORKER_C_DONE -eq 1 ] && echo '✅完了' || echo '⏳作業中')"

# 全Worker完成判定
TOTAL_DONE=$((WORKER_A_DONE + WORKER_B_DONE + WORKER_C_DONE))

if [ $TOTAL_DONE -eq 3 ]; then
    echo "🎉 全Worker完成！Boss に報告します"
    
    # 組織番号からboss指定を決定
    case $ORG_NUM in
        "org-01") BOSS_TARGET="boss01" ;;
        "org-02") BOSS_TARGET="boss02" ;;
        "org-03") BOSS_TARGET="boss03" ;;
        "org-04") BOSS_TARGET="boss04" ;;
        *) BOSS_TARGET="boss01" ;;
    esac
    
    # Boss報告実行
    ../../scripts/quick_send.sh $BOSS_TARGET "実装が完了しました。"
    
    # チェックリスト更新
    sed -i 's/\[ \] \*\*Boss報告完了\*\*/[x] **Boss報告完了**/' WORKER_CHECKLIST.md
    
    echo "✅ Boss報告完了"
else
    echo "⏳ 他のWorkerの完了を待機中 ($TOTAL_DONE/3)"
    echo "💡 30秒後に再チェックします"
    
    # 30秒待機後に再チェック（バックグラウンド）
    (sleep 30 && bash -c '
        # 再チェック実行
        WORKER_A_DONE=$(grep "\[x\] \*\*実装完成\*\*" ../01worker-a/WORKER_CHECKLIST.md 2>/dev/null && echo "1" || echo "0")
        WORKER_B_DONE=$(grep "\[x\] \*\*実装完成\*\*" ../01worker-b/WORKER_CHECKLIST.md 2>/dev/null && echo "1" || echo "0")
        WORKER_C_DONE=$(grep "\[x\] \*\*実装完成\*\*" ../01worker-c/WORKER_CHECKLIST.md 2>/dev/null && echo "1" || echo "0")
        TOTAL_DONE=$((WORKER_A_DONE + WORKER_B_DONE + WORKER_C_DONE))
        
        if [ $TOTAL_DONE -eq 3 ]; then
            echo "🎉 全Worker完成確認！Boss に報告"
            ORG_NUM=$(pwd | grep -o "org-[0-9][0-9]" | tail -1)
            case $ORG_NUM in
                "org-01") BOSS_TARGET="boss01" ;;
                "org-02") BOSS_TARGET="boss02" ;;
                "org-03") BOSS_TARGET="boss03" ;;
                "org-04") BOSS_TARGET="boss04" ;;
                *) BOSS_TARGET="boss01" ;;
            esac
            ../../scripts/quick_send.sh $BOSS_TARGET "実装が完了しました。"
            sed -i "s/\[ \] \*\*Boss報告完了\*\*/[x] **Boss報告完了**/" WORKER_CHECKLIST.md
        fi
    ') &
fi
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