#!/bin/bash

# 🚀 クイック送信 - Multi-Agent Worktree間の直接送信

show_usage() {
    cat << EOF
🚀 クイック送信コマンド

使用方法:
  $0 [ペイン] [メッセージ]

ペイン指定:
  boss01, boss02, boss03, boss04          - 各組織のBoss
  worker-a01, worker-b01, worker-c01      - Org-01のWorkers
  worker-a02, worker-b02, worker-c02      - Org-02のWorkers  
  worker-a03, worker-b03, worker-c03      - Org-03のWorkers
  worker-a04, worker-b04, worker-c04      - Org-04のWorkers

使用例:
  $0 boss01 "実装が完了しました。"
  $0 worker-a01 "あなたはWorker-Aです。指示書に従って実装を開始してください。"
  $0 worker-b02 "キャッシュ最適化を担当してください。"
EOF
}

# ペイン番号マッピング
get_pane_number() {
    case "$1" in
        "boss01") echo "0" ;;
        "worker-a01") echo "1" ;;
        "worker-b01") echo "2" ;;
        "worker-c01") echo "3" ;;
        "boss02") echo "4" ;;
        "worker-a02") echo "5" ;;
        "worker-b02") echo "6" ;;
        "worker-c02") echo "7" ;;
        "boss03") echo "8" ;;
        "worker-a03") echo "9" ;;
        "worker-b03") echo "10" ;;
        "worker-c03") echo "11" ;;
        "boss04") echo "12" ;;
        "worker-a04") echo "13" ;;
        "worker-b04") echo "14" ;;
        "worker-c04") echo "15" ;;
        *) echo "" ;;
    esac
}

# メイン処理
main() {
    if [[ $# -lt 2 ]]; then
        show_usage
        exit 1
    fi
    
    local target="$1"
    local message="$2"
    
    local pane_num
    pane_num=$(get_pane_number "$target")
    
    if [[ -z "$pane_num" ]]; then
        echo "❌ エラー: 不明なペイン '$target'"
        show_usage
        exit 1
    fi
    
    # tmuxセッション確認
    if ! tmux has-session -t "multiagent" 2>/dev/null; then
        echo "❌ エラー: tmux セッション 'multiagent' が見つかりません"
        exit 1
    fi
    
    # Claude Code対応メッセージ送信
    echo "📤 送信中: $target (ペイン$pane_num) ← '$message'"
    
    # Claude Codeのプロンプトをクリア
    tmux send-keys -t "multiagent:0.$pane_num" C-c
    sleep 0.3
    
    # メッセージ送信
    tmux send-keys -t "multiagent:0.$pane_num" "$message"
    sleep 0.1
    
    # エンター押下
    tmux send-keys -t "multiagent:0.$pane_num" C-m
    
    echo "✅ 送信完了（Claude Code対応）"
}

main "$@" 