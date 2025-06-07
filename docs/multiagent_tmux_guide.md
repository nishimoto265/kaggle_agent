# 🤖 Multi-Agent tmux Development Guide

Kaggle Agent プロジェクトの4x4ペイン構成マルチエージェント開発環境使用ガイド

## 🚀 クイックスタート

### 1. Worktree環境構築
```bash
# プロジェクトルートで実行
./scripts/setup_multiagent_worktree.sh

# 特定組織IDで実行
./scripts/setup_multiagent_worktree.sh org-02
```

### 2. tmux環境起動
```bash
# 4x4ペイン構成でマルチエージェント環境起動
./scripts/create_multiagent_tmux.sh
```

### 3. 即座開発開始
各ペインでAgent指示書を確認し、実装開始
```bash
# 各ペインで実行
cat CLAUDE.md
```

## 📋 ペイン構成

### 4x4グリッドレイアウト
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   boss01    │ worker-a01  │ worker-b01  │ worker-c01  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│   boss02    │ worker-a02  │ worker-b02  │ worker-c02  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│   boss03    │ worker-a03  │ worker-b03  │ worker-c03  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│   boss04    │ worker-a04  │ worker-b04  │ worker-c04  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Agent役割分担
- **Boss列**: 統括・評価・統合 (`orgs/org-01/01boss`)
- **Worker-A列**: AI出力変動実装1 (`orgs/org-01/01worker-a`)
- **Worker-B列**: AI出力変動実装2 (`orgs/org-01/01worker-b`)
- **Worker-C列**: AI出力変動実装3 (`orgs/org-01/01worker-c`)

> **重要**: Worker-A/B/Cは同一プロンプトを受信し、AI出力の自然な変動により異なる実装を生成

### 行用途例
- **行1**: メイン開発・実装
- **行2**: テスト・デバッグ
- **行3**: ドキュメント・設計
- **行4**: ベンチマーク・品質チェック

## ⌨️ tmux操作ガイド

### 基本操作（Prefix: Ctrl+b）

#### ペイン移動
```bash
# Vi風ペイン移動
Prefix + h/j/k/l    # 左/下/上/右

# Agent間ショートカット移動
Prefix + M          # Boss01へ
Prefix + A          # Worker-A01へ
Prefix + B          # Worker-B01へ  
Prefix + C          # Worker-C01へ

# 行内移動
Prefix + 1          # 各Agent 1行目へ
Prefix + 2          # 各Agent 2行目へ
Prefix + 3          # 各Agent 3行目へ
Prefix + 4          # 各Agent 4行目へ
```

#### ペイン管理
```bash
# ペイン分割
Prefix + |          # 縦分割
Prefix + -          # 横分割

# ペイン削除
Prefix + q          # 現在ペイン削除
Prefix + Q          # 他ペイン全削除（確認あり）

# レイアウト調整
Prefix + =          # タイル型（均等配置）
Prefix + +          # 水平均等
Prefix + *          # 垂直均等
```

#### 便利機能
```bash
# 全ペイン同期（危険注意）
Prefix + S          # 同期ON/OFF切り替え
Prefix + I          # 同期状態表示

# 設定リロード
Prefix + r          # .tmux.conf再読み込み

# コピーモード
Prefix + [          # コピーモード開始
v                   # 選択開始（Vi風）
y                   # コピー
```

## 🔄 ワークフロー例

### 基本開発サイクル
```bash
# 1. Boss（統括）: タスク設計・指示
boss01> cat CLAUDE.md           # 指示書確認
boss01> vim task_specification.md  # タスク仕様作成

# 2. Workers（実装）: 並列開発
worker-a01> cat CLAUDE.md       # 同一指示確認
worker-a01> python main.py      # AI変動実装1開始

worker-b01> cat CLAUDE.md       # 同一指示確認
worker-b01> python main.py      # AI変動実装2開始

worker-c01> cat CLAUDE.md       # 同一指示確認
worker-c01> python main.py      # AI変動実装3開始

# 3. Boss（評価）: 品質チェック・統合
boss02> ./scripts/evaluate_implementations.py
boss03> python integration_test.py
boss04> vim final_report.md
```

### 並列テスト環境
```bash
# 各行で異なるテスト実行
boss01> pytest tests/unit/           # 単体テスト
boss02> pytest tests/integration/    # 統合テスト
boss03> python performance_test.py   # 性能テスト
boss04> python security_scan.py      # セキュリティテスト
```

## 🛠️ 環境カスタマイズ

### プロンプトカスタマイズ
各ペインで自動設定されるプロンプト:
```bash
(boss01) /path/to/orgs/org-01/01boss $
(worker-a01) /path/to/orgs/org-01/01worker-a $
```

### 仮想環境自動有効化
スクリプトが自動で以下を試行:
1. `worktree/venv/bin/activate` （各worktree内）
2. `../../venv/bin/activate` （プロジェクトルート）

### ペインタイトル表示
各ペインの上部にAgent名が表示:
```
┌─ boss01 ─────────┐
│                  │
│ $ command here   │
│                  │
└──────────────────┘
```

## 🚨 トラブルシューティング

### よくある問題

#### セッション接続エラー
```bash
# セッション確認
tmux list-sessions

# 強制削除して再作成
tmux kill-session -t multiagent
./scripts/create_multiagent_tmux.sh
```

#### ペイン構成が崩れた
```bash
# レイアウト修復
Prefix + =          # タイル型に戻す
Prefix + r          # 設定リロード
```

#### Worktreeが見つからない
```bash
# Worktree状態確認
git worktree list

# 再作成
./scripts/setup_multiagent_worktree.sh
```

#### ペイン同期が勝手にON
```bash
# 同期解除
Prefix + S          # 同期切り替え
Prefix + I          # 状態確認
```

### パフォーマンス最適化
```bash
# 履歴制限調整（メモリ使用量削減）
set -g history-limit 5000

# 視覚効果無効化（高速化）
set -g visual-activity off
set -g monitor-activity off
```

## 📊 監視・ログ

### セッション情報確認
```bash
# 現在のセッション情報
tmux display-message -p "Session: #{session_name}, Window: #{window_index}, Pane: #{pane_index}"

# ペイン一覧
tmux list-panes -a

# Agent別ペイン確認
tmux list-panes -F "#{pane_index}: #{pane_title} (#{pane_current_path})"
```

### 開発進捗監視
```bash
# 各ペインで実行中コマンド確認
tmux list-panes -F "#{pane_index}: #{pane_current_command}"

# ペイン別CPU/メモリ使用量（要htop）
htop -p $(tmux list-panes -F "#{pane_pid}" | tr '\n' ',')
```

## 🔧 高度な使用法

### ペイン同期活用
```bash
# 全Agentに共通コマンド実行
Prefix + S          # 同期ON
git status          # 全ペインで実行
Prefix + S          # 同期OFF
```

### スクリプト実行の並列化
```bash
# 各Agentでテストを並列実行
boss01> pytest tests/boss/
worker-a01> pytest tests/performance/
worker-b01> pytest tests/quality/  
worker-c01> pytest tests/extensibility/
```

### ログ収集自動化
```bash
# 各ペインの出力をファイル保存
tmux pipe-pane -t multiagent:0.0 'cat >> logs/boss01.log'
tmux pipe-pane -t multiagent:0.1 'cat >> logs/worker-a01.log'
```

---

## 📚 関連文書

- [`boss_instructions.md`](boss_instructions.md) - Boss Agent専用指示書
- [`worker_instructions.md`](worker_instructions.md) - Worker Agent統合指示書
- [`tmux_parallel_development_spec.md`](tmux_parallel_development_spec.md) - tmux並列開発仕様
- [`worker_instructions.md`](worker_instructions.md) - Worker実装指示書
- [`boss_instructions.md`](boss_instructions.md) - Boss管理指示書

---

**セットアップ時間**: ~2分  
**推奨ターミナルサイズ**: 120x40以上  
**推奨メモリ**: 8GB以上 