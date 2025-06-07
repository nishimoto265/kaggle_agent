# 🤖 完全自律エージェント連携システム運用ガイド

## 概要

このシステムは、エージェント同士がbashファイル実行により自律的に連携し、Final BossとBossがメッセージベースで完全に独立動作する多エージェント開発フレームワークです。

### 🎯 システムの特徴

- **完全自律動作**: 人間の介入なしにエージェント同士が連携
- **イベント駆動**: bashファイル実行がトリガーとなり次のエージェントが動作
- **真のエージェント間通信**: ファイルベースでメッセージ交換
- **自動ライフサイクル管理**: 組織の作成→作業→完了→削除→新規作成を自動実行

## 🔄 エージェント連携フロー

```
1. Boss作業完了
   ↓ (bashファイル実行)
2. Final Boss メッセージ検知
   ↓ (自動起動)
3. Final Boss 品質評価・統合
   ↓ (bashファイル実行)
4. Final Boss 組織削除・クリーンアップ
   ↓ (bashファイル実行)  
5. Final Boss 新しいタスク割り当て
   ↓ (bashファイル実行)
6. Boss 新しいタスク受信・開始
   ↓ (ループ継続)
```

## 🚀 システム起動

### 初期起動
```bash
# 完全自律システム起動
bash scripts/start_autonomous_agents.sh start
```

### システム状況確認
```bash
# 現在の状況表示
bash scripts/start_autonomous_agents.sh status

# ヘルスチェック実行
bash scripts/start_autonomous_agents.sh health
```

## 📤 Boss → Final Boss 通信

### Boss側操作（組織内で実行）

#### 1. タスク完了報告
```bash
cd orgs/org-01/  # 該当組織内で実行
bash scripts/boss_send_message.sh completed "data_processing_foundation"
```

#### 2. 進捗報告
```bash
bash scripts/boss_send_message.sh progress "Worker-A完了, Worker-B 80%進行中"
```

#### 3. 問題報告
```bash
bash scripts/boss_send_message.sh issue "Worker-Cが依存関係エラーで停止"
```

#### 4. 支援要求
```bash
bash scripts/boss_send_message.sh request "追加のリソースが必要"
```

#### 5. 状況報告
```bash
bash scripts/boss_send_message.sh status "定期状況報告"
```

## 📨 Final Boss → Boss 通信

### Final Boss側操作（自動実行される）

Final Bossは以下を自動実行します：

1. **メッセージ監視**: `final_boss_watcher.sh` がファイル監視
2. **品質評価**: 完了報告受信時に自動品質チェック
3. **統合処理**: 品質合格時に自動統合
4. **組織クリーンアップ**: `final_boss_cleanup.sh` 自動実行
5. **新タスク割り当て**: `final_boss_assign_next.sh` 自動実行
6. **Boss通知**: 新タスク通知メッセージ自動送信

## 📬 Boss メッセージ受信

### Boss側でメッセージ受信（組織内で実行）

#### 1. 新着メッセージ確認
```bash
cd orgs/org-01/  # 該当組織内で実行
bash scripts/boss_receive_message.sh check
```

#### 2. 継続監視モード
```bash
bash scripts/boss_receive_message.sh watch
```

#### 3. メッセージ状況確認
```bash
bash scripts/boss_receive_message.sh status
```

## 🎯 自動処理の詳細

### Final Boss ファイル監視システム

- **監視対象**: `shared_messages/from_boss_*.md`
- **検知方法**: inotify または ポーリング（5秒間隔）
- **処理内容**:
  - 完了報告 → 品質評価 → 統合 → クリーンアップ → 新規割り当て
  - 進捗報告 → 確認応答送信
  - 問題報告 → 支援応答送信
  - 支援要求 → カスタム支援応答

### 組織自動管理

#### 完了時クリーンアップ
1. 成果物アーカイブ（`archives/completed_YYYYMMDD/`）
2. Git worktree削除
3. 組織ディレクトリ削除
4. 関連ファイルクリーンアップ
5. プロジェクトチェックリスト更新
6. 統計情報更新

#### 新規タスク自動割り当て
1. PROJECT_CHECKLIST.mdから次タスク取得（高優先度優先）
2. 利用可能な組織名生成（org-01, org-02...）
3. タスクユニット作成
4. 組織への割り当て実行
5. Boss通知メッセージ送信

## 📊 監視・統計

### システム監視コマンド

```bash
# Final Boss監視システム状況
bash scripts/final_boss_watcher.sh status

# 次タスク割り当てシステム状況  
bash scripts/final_boss_assign_next.sh status

# 一回だけメッセージ処理
bash scripts/final_boss_watcher.sh process-once
```

### 統計ファイル

- `statistics/final_boss_activity_YYYYMMDD.json`: Final Boss活動統計
- `statistics/cleanup_YYYYMMDD.json`: クリーンアップ統計
- `statistics/assignments_YYYYMMDD.json`: タスク割り当て統計
- `statistics/autonomous_system_report_*.json`: システム総合統計

## 🛠️ トラブルシューティング

### よくある問題と解決法

#### 1. Final Boss監視システムが停止している
```bash
# 監視システム再起動
bash scripts/start_autonomous_agents.sh restart
```

#### 2. メッセージが処理されない
```bash
# 手動で一回処理
bash scripts/final_boss_watcher.sh process-once

# メッセージディレクトリ確認
ls -la shared_messages/
```

#### 3. 組織が作成されない
```bash
# 手動でタスク割り当て実行
bash scripts/final_boss_assign_next.sh assign

# 次のタスクがあるか確認
bash scripts/final_boss_assign_next.sh check-next
```

#### 4. 長時間滞留メッセージがある
```bash
# 滞留メッセージ確認
find shared_messages/ -name "*.md" -mtime +1

# 手動で処理
bash scripts/final_boss_watcher.sh process-once
```

### ログファイル確認

```bash
# Final Boss監視ログ
tail -f logs/final_boss_watcher_*.log

# Bossメッセージ受信ログ  
tail -f logs/boss_*_receive_*.log

# システム起動ログ
tail -f logs/autonomous_startup_*.log
```

## 🔧 カスタマイズ

### メッセージタイプ追加

1. `boss_send_message.sh` にメッセージタイプ追加
2. `final_boss_watcher.sh` に処理ロジック追加
3. `boss_receive_message.sh` に受信処理追加

### 品質基準調整

- `scripts/quality_evaluation.py`: 品質評価基準調整
- `final_boss_watcher.sh`: 合格基準スコア調整（現在95%）

### 監視間隔調整

- `final_boss_watcher.sh`: ポーリング間隔調整（現在5秒）
- `boss_receive_message.sh`: 監視間隔調整（現在30秒）

## 🎉 運用開始

### 1. システム起動
```bash
bash scripts/start_autonomous_agents.sh start
```

### 2. 初期タスクが自動割り当てされることを確認
```bash
bash scripts/start_autonomous_agents.sh status
```

### 3. 組織内でBossとしてタスク実行
```bash
cd orgs/org-01/
# Workers への作業指示...
# 作業完了後
bash scripts/boss_send_message.sh completed "タスク名"
```

### 4. 自動でFinal Bossが処理し、次のタスクが割り当てられることを確認
```bash
# 数分待ってから状況確認
bash scripts/start_autonomous_agents.sh status
```

## 🛑 システム停止

```bash
# 安全なシステム停止
bash scripts/start_autonomous_agents.sh stop
```

---

## 📋 重要なポイント

1. **Boss操作は組織内で実行**: `cd orgs/org-XX/` してからコマンド実行
2. **Final Bossは自動動作**: 手動介入は基本的に不要
3. **メッセージファイルベース**: shared_messages/ ディレクトリで通信
4. **完全イベント駆動**: bashファイル実行がトリガー
5. **ログ完備**: 全操作がログファイルに記録

このシステムにより、エージェント同士が完全に自律的に連携し、継続的にタスクを実行・完了・統合・新規割り当てのサイクルを自動実行します。 