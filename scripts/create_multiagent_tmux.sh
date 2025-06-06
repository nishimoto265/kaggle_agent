#!/bin/bash

# Kaggle Agent Multi-Agent tmux Session Creator
# 4x4ペイン構成でマルチエージェント開発環境を構築
# セッション名: multiagent  
# ペイン構成: 4組織 × 4エージェント = 16ペイン (組織レベル配置)

SESSION_NAME="multiagent"

# 色付きログ関数
log_info() {
    echo -e "\033[1;32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# プロジェクトルートディレクトリの確認
declare -a organizations=("org-01" "org-02" "org-03" "org-04")
missing_orgs=()

for org in "${organizations[@]}"; do
    if [[ ! -d "orgs/$org" ]]; then
        missing_orgs+=("$org")
    fi
done

if [[ ${#missing_orgs[@]} -gt 0 ]]; then
    log_error "以下の組織ディレクトリが見つかりません: ${missing_orgs[*]}"
    log_info "まず worktree を作成してください:"
    echo "  ./scripts/setup_multiagent_worktree.sh"
    exit 1
fi

# 既存のセッションがある場合は確認して削除
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    log_warn "既存のセッション '$SESSION_NAME' が見つかりました"
    read -p "削除して新しく作成しますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux kill-session -t $SESSION_NAME
        log_info "既存セッションを削除しました"
    else
        log_info "既存セッションにアタッチします"
        tmux attach-session -t $SESSION_NAME
        exit 0
    fi
fi

log_info "tmuxセッション '$SESSION_NAME' を作成中..."

# 新しいセッションを作成
tmux new-session -d -s $SESSION_NAME
tmux rename-window -t $SESSION_NAME:0 "multiagent"

# 4x4グリッド作成
log_info "4x4ペイン構成を作成中..."

# まず横に3回分割して4列にする
tmux split-window -h -t $SESSION_NAME:0.0
tmux split-window -h -t $SESSION_NAME:0.0  
tmux split-window -h -t $SESSION_NAME:0.1

# 各列を縦に3回分割して4行にする
# 1列目を4分割
tmux split-window -v -t $SESSION_NAME:0.0
tmux split-window -v -t $SESSION_NAME:0.0
tmux split-window -v -t $SESSION_NAME:0.1

# 2列目を4分割  
tmux split-window -v -t $SESSION_NAME:0.4
tmux split-window -v -t $SESSION_NAME:0.4
tmux split-window -v -t $SESSION_NAME:0.5

# 3列目を4分割
tmux split-window -v -t $SESSION_NAME:0.8
tmux split-window -v -t $SESSION_NAME:0.8  
tmux split-window -v -t $SESSION_NAME:0.9

# 4列目を4分割
tmux split-window -v -t $SESSION_NAME:0.12
tmux split-window -v -t $SESSION_NAME:0.12
tmux split-window -v -t $SESSION_NAME:0.13

# ペイン名と組織の設定
declare -a pane_names=(
    "ORG01-Boss" "ORG01-Worker-A" "ORG01-Worker-B" "ORG01-Worker-C"
    "ORG02-Boss" "ORG02-Worker-A" "ORG02-Worker-B" "ORG02-Worker-C"
    "ORG03-Boss" "ORG03-Worker-A" "ORG03-Worker-B" "ORG03-Worker-C"
    "ORG04-Boss" "ORG04-Worker-A" "ORG04-Worker-B" "ORG04-Worker-C"
)

declare -a org_dirs=(
    "orgs/org-01" "orgs/org-01" "orgs/org-01" "orgs/org-01"
    "orgs/org-02" "orgs/org-02" "orgs/org-02" "orgs/org-02"
    "orgs/org-03" "orgs/org-03" "orgs/org-03" "orgs/org-03"
    "orgs/org-04" "orgs/org-04" "orgs/org-04" "orgs/org-04"
)

# 各ペインの設定
log_info "各ペインを設定中..."
for i in {0..15}; do
    pane_name=${pane_names[$i]}
    org_dir=${org_dirs[$i]}
    
    # ペインタイトルを設定
    tmux send-keys -t $SESSION_NAME:0.$i "printf '\033]2;${pane_name}\033\\'" C-m
    
    # 組織レベルディレクトリに移動
    tmux send-keys -t $SESSION_NAME:0.$i "cd $org_dir" C-m
    
    # 仮想環境があれば有効化
    if [[ -f "venv/bin/activate" ]]; then
        tmux send-keys -t $SESSION_NAME:0.$i "source ../../venv/bin/activate" C-m
    fi
    
    # プロンプトをカスタマイズ
    tmux send-keys -t $SESSION_NAME:0.$i "export PS1='(\[\033[1;36m\]${pane_name}\[\033[0m\]) \[\033[1;32m\]\w\[\033[0m\]\$ '" C-m
    
    # 組織構成を表示
    tmux send-keys -t $SESSION_NAME:0.$i "echo '=== ${pane_name} ==='" C-m
    tmux send-keys -t $SESSION_NAME:0.$i "echo 'Agent Directory Structure:'" C-m
    tmux send-keys -t $SESSION_NAME:0.$i "ls -la" C-m
    tmux send-keys -t $SESSION_NAME:0.$i "echo '=================='" C-m
done

# レイアウトを調整（均等に配置）
tmux select-layout -t $SESSION_NAME:0 tiled

# 最初のペイン（ORG01-Boss）を選択
tmux select-pane -t $SESSION_NAME:0.0

log_info "セットアップ完了！"
echo ""
echo "🤖 Multi-Agent Development Environment - 4組織対応"
echo "=================================================="
echo "  Session: $SESSION_NAME"
echo "  Layout:  4x4 Grid (16 panes)"
echo "  Config:  組織レベル配置"
echo ""
echo "ペイン構成 (組織レベル):"
echo "  ORG01-Boss      ORG01-Worker-A   ORG01-Worker-B   ORG01-Worker-C"
echo "  ORG02-Boss      ORG02-Worker-A   ORG02-Worker-B   ORG02-Worker-C"
echo "  ORG03-Boss      ORG03-Worker-A   ORG03-Worker-B   ORG03-Worker-C"
echo "  ORG04-Boss      ORG04-Worker-A   ORG04-Worker-B   ORG04-Worker-C"
echo ""
echo "📂 各ペインのディレクトリ:"
echo "  行1 (0-3):   orgs/org-01/ (01boss, 01worker-a, 01worker-b, 01worker-c)"
echo "  行2 (4-7):   orgs/org-02/ (組織ディレクトリレベル)"
echo "  行3 (8-11):  orgs/org-03/ (組織ディレクトリレベル)"
echo "  行4 (12-15): orgs/org-04/ (組織ディレクトリレベル)"
echo ""
echo "🔗 tmux操作:"
echo "  Prefix: Ctrl+b (デフォルト)"
echo "  ペイン移動: Prefix + h/j/k/l"
echo "  レイアウト調整: Prefix + ="
echo "  セッション終了: Prefix + d (detach)"
echo ""
echo "📋 他AIの監視:"
echo "  ORG01から: ls 01worker-*/ で他ワーカー確認"
echo "  比較: diff 01worker-a/hello.py 01worker-b/hello.py"
echo ""

# セッションにアタッチ
log_info "セッションにアタッチ中..."
tmux attach-session -t $SESSION_NAME 