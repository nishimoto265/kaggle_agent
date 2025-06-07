# 🏆 Final Boss 運用ガイド

**Version**: 3.0 (実装運用版)  
**Date**: 2025-06-07  
**Target**: Final Boss担当者

## 🎯 Final Boss運用フロー概要

```
1つの仕事単位チェックリスト作成
    ↓
orgにワークツリー作成・Boss割り当て
    ↓
Worker実装・Boss統合管理
    ↓
Boss完了報告受信
    ↓
品質評価・統合テスト
    ↓
【分岐】
├─ 高品質 → そのまま統合
├─ 軽微問題 → 自動修正後統合
└─ 重大問題 → Boss再作成指示
    ↓
メインブランチ統合・チェックリスト更新
```

## 🚀 実行コマンド集

### 1. 新規タスク作成
```bash
# 基本タスク作成
./scripts/create_task_unit.sh "データ処理基盤" "org-01" "High" "Complex"

# 複数タスク一括作成
./scripts/create_task_unit.sh "特徴量エンジニアリング" "org-02" "High" "Complex"
./scripts/create_task_unit.sh "モデル学習システム" "org-03" "High" "Complex"
./scripts/create_task_unit.sh "評価・バリデーション" "org-04" "High" "Complex"
```

### 2. Boss割り当て・ワークツリー作成
```bash
# 単体割り当て
./scripts/assign_task_to_boss.sh "org-01" "データ処理基盤"

# 全組織一括割り当て（基盤モジュール）
./scripts/assign_task_to_boss.sh "org-01" "データ処理基盤"
./scripts/assign_task_to_boss.sh "org-02" "特徴量エンジニアリング"
./scripts/assign_task_to_boss.sh "org-03" "モデル学習システム"
./scripts/assign_task_to_boss.sh "org-04" "評価・バリデーション"
```

### 3. 進捗監視・品質確認
```bash
# 日次運用
./scripts/daily_operations.sh morning   # 09:00
./scripts/daily_operations.sh noon     # 13:00
./scripts/daily_operations.sh evening  # 17:00

# 週次運用
./scripts/daily_operations.sh weekly   # 金曜日
```

### 4. 個別品質評価
```bash
# 特定組織・タスクの評価
python scripts/quality_evaluation.py "org-01" "データ処理基盤"

# JSON形式で詳細確認
python scripts/quality_evaluation.py "org-01" "データ処理基盤" --output json
```

### 5. 統合実行
```bash
# 完了タスクの統合
./scripts/integrate_to_main.sh "org-01" "データ処理基盤"

# 複数タスク一括統合
for org in org-01 org-02 org-03 org-04; do
  ./scripts/integrate_to_main.sh "$org" "対象タスク名"
done
```

### 6. プロジェクト状況確認
```bash
# 全体進捗確認
cat PROJECT_CHECKLIST.md

# 組織別進捗確認
for org in orgs/org-*/*/; do
  if [ -f "$org/TASK_CHECKLIST.md" ]; then
    echo "=== $org ==="
    grep -c "\[x\]" "$org/TASK_CHECKLIST.md" || echo "0"
  fi
done
```

## 📋 日次運用スケジュール

### 🌅 朝 (09:00)
```bash
./scripts/daily_operations.sh morning
```
- 完了報告確認
- 進行中タスク進捗チェック
- 新規タスク優先度確認

### 🌞 昼 (13:00)
```bash
./scripts/daily_operations.sh noon
```
- 完了報告の品質評価実行
- 統合可能タスクの統合実行

### 🌆 夕方 (17:00)
```bash
./scripts/daily_operations.sh evening
```
- 本日の統合実績まとめ
- 翌日タスク準備
- プロジェクト全体進捗更新

### 📊 週次 (金曜日)
```bash
./scripts/daily_operations.sh weekly
```
- 週次統合レポート作成
- 来週のタスク計画策定
- 品質メトリクス分析

## 🎯 実装例：基盤モジュール開始

### Step 1: タスク一括作成
```bash
# 基盤モジュール4タスク作成
./scripts/create_task_unit.sh "データ処理基盤" "org-01" "High" "Complex"
./scripts/create_task_unit.sh "特徴量エンジニアリング" "org-02" "High" "Complex"
./scripts/create_task_unit.sh "モデル学習システム" "org-03" "High" "Complex"
./scripts/create_task_unit.sh "評価・バリデーション" "org-04" "High" "Complex"
```

### Step 2: 全組織に一斉割り当て
```bash
# 全Boss割り当て
./scripts/assign_task_to_boss.sh "org-01" "データ処理基盤"
./scripts/assign_task_to_boss.sh "org-02" "特徴量エンジニアリング"
./scripts/assign_task_to_boss.sh "org-03" "モデル学習システム"
./scripts/assign_task_to_boss.sh "org-04" "評価・バリデーション"
```

### Step 3: Boss通知確認
```bash
# Boss通知メッセージ確認
ls -la orgs/*/*/shared_messages/to_boss_*.md

# 各BossのTMUXセッション確認
tmux list-sessions | grep boss
```

### Step 4: 日次監視開始
```bash
# 朝の確認
./scripts/daily_operations.sh morning

# cron設定例
echo "0 9 * * * /path/to/scripts/daily_operations.sh morning" >> /tmp/crontab
echo "0 13 * * * /path/to/scripts/daily_operations.sh noon" >> /tmp/crontab
echo "0 17 * * * /path/to/scripts/daily_operations.sh evening" >> /tmp/crontab
echo "0 17 * * 5 /path/to/scripts/daily_operations.sh weekly" >> /tmp/crontab
crontab /tmp/crontab
```

## 🔍 トラブルシューティング

### Boss完了報告が来ない場合
```bash
# Boss進捗確認
for org in org-01 org-02 org-03 org-04; do
  if tmux has-session -t "${org}-boss" 2>/dev/null; then
    echo "✅ $org Boss session active"
  else
    echo "❌ $org Boss session not found"
  fi
done

# Boss直接連絡
tmux send-keys -t "org-01-boss" "echo 'Final Boss より: 進捗確認をお願いします'" Enter
```

### 品質評価エラーの場合
```bash
# 詳細エラー確認
python scripts/quality_evaluation.py "org-01" "データ処理基盤" --output json 2>&1

# 手動ディレクトリ確認
ls -la orgs/org-01/データ処理基盤/integrated/
```

### 統合失敗の場合
```bash
# 軽微修正の手動実行
./scripts/apply_minor_fixes.sh "org-01" "データ処理基盤"

# 再評価
python scripts/quality_evaluation.py "org-01" "データ処理基盤"

# 再統合
./scripts/integrate_to_main.sh "org-01" "データ処理基盤"
```

## 📈 成功指標

### 週次目標
- **完了タスク**: 4件/週
- **統合成功率**: 90%以上
- **品質スコア平均**: 85点以上
- **再作成率**: 10%以下

### 月次目標
- **全タスク進捗**: 80%以上
- **品質問題件数**: 5件以下
- **組織間連携**: スムーズ
- **システム稼働率**: 95%以上

---

**緊急連絡先**: Final Boss (この端末)  
**サポート**: `tmux attach -t final-boss`  
**ログ場所**: `./logs/final_boss_operations.log` 