# 🤖 Worker実装指示書

**Version**: 3.0 (チェックリスト駆動ワークフロー)  
**Target**: 全Worker（worker-a, worker-b, worker-c）  
**Update**: 2025-06-06

> **🎯 重要**: 本システムはチェックリスト駆動でBossから受け取ったタスクを実装し、完了時に他Workerと連携して最終報告を行うシステムです

## 🚀 タスク実装フロー

### タスク概要
**あなたのミッション**: Bossから指示されたモジュールを実装してください

### 実装テンプレート
```yaml
モジュール名: [BOSS指定]
実装必須項目:
  - 要求された機能の実装
  - エラーハンドリング
  - ユニットテスト完備
  - 詳細ドキュメント
  - 型アノテーション

ファイル構成:
  - src/[module_name]/core.py       # メイン実装
  - src/[module_name]/__init__.py   # モジュール初期化
  - src/[module_name]/cli.py        # CLI実行（必要に応じて）
  - tests/test_[module_name].py     # ユニットテスト
  - docs/[module_name].md           # ドキュメント

品質基準:
  - テストカバレッジ95%以上
  - 型アノテーション完備
  - リンターエラーなし
  - パフォーマンス要件満足
  - PEP8準拠
```

### Worker実行手順
```bash
# 1. チェックリスト確認
cat WORKER_CHECKLIST.md

# 2. Boss指示の確認（CLAUDE.mdまたは直接指示）
cat CLAUDE.md  # Boss指示書確認

# 3. 実装開始（モジュール名はBoss指定に従う）
mkdir -p src/[module_name] tests docs
touch src/[module_name]/{__init__.py,core.py}
touch tests/test_[module_name].py
touch docs/[module_name].md

# 4. 実装完了後チェック
pytest tests/ --cov=src
ruff check src/
mypy src/

# 5. 実装完成をチェックリストにマーク
sed -i 's/\[ \] \*\*実装完成\*\*/[x] **実装完成**/' WORKER_CHECKLIST.md

# 6. 全Worker完了チェック＆Boss報告（必須）
../../scripts/check_all_workers_done.sh
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

### 4. 完了報告
```bash
# 自分の実装完成後、他Workerの完了状況確認
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

## 🛠️ 必須スクリプト使用法

### Worker用スクリプト
```bash
# 緊急時のBoss連絡
../../scripts/quick_send.sh boss01 "緊急: エラーが発生しました"
```

### 開発環境セットアップ（初回のみ）
```bash
# 1. マルチエージェント環境構築（初回のみ）
./scripts/setup_multiagent_worktree.sh

# 2. tmux開発環境起動
./scripts/create_multiagent_tmux.sh

# 3. システム監視開始
./scripts/start_autonomous_agents.sh start
```

### タスク管理スクリプト（Final Boss用参考）
```bash
# 新タスク作成
./scripts/create_task_unit.sh "task_name" "org-01" "High" "Complex"

# 統合処理
./scripts/integrate_to_main.sh "org-01" "task_name"
```

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