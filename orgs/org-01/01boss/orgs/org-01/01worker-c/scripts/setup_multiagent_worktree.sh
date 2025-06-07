#!/bin/bash

# Kaggle Agent Multi-Agent Worktree Setup Script
# Git worktreeとAgent指示書を自動設定 - 4組織対応

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

log_success() {
    echo -e "\033[1;34m[SUCCESS]\033[0m $1"
}

# 必要なファイルの存在確認
if [[ ! -f "docs/boss_instructions.md" ]]; then
    log_error "docs/boss_instructions.md が見つかりません"
    exit 1
fi

if [[ ! -f "docs/worker_instructions.md" ]]; then
    log_error "docs/worker_instructions.md が見つかりません"
    exit 1
fi

echo "🤖 Kaggle Agent Multi-Agent Worktree Setup - 4組織対応"
echo "========================================================"
echo ""

# 4組織すべてのworktreeを作成
declare -a organizations=("org-01" "org-02" "org-03" "org-04")

for ORG_ID in "${organizations[@]}"; do
    BASE_DIR="orgs/$ORG_ID"
    
    echo "🏢 組織 $ORG_ID のセットアップ中..."
    echo "================================="
    
    # 既存worktreeの確認
    log_info "既存worktreeの確認中..."
    if [[ -d "$BASE_DIR" ]]; then
        log_warn "既存のworktreeが見つかりました: $BASE_DIR"
        echo ""
        git worktree list | grep "$ORG_ID" || true
        echo ""
        read -p "$ORG_ID の既存worktreeを削除して再作成しますか? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "既存worktreeを削除中..."
            
            # 各worktreeを個別に削除
            for agent in "01boss" "01worker-a" "01worker-b" "01worker-c"; do
                if [[ -d "$BASE_DIR/$agent" ]]; then
                    git worktree remove "$BASE_DIR/$agent" 2>/dev/null || true
                    log_info "削除: $BASE_DIR/$agent"
                fi
            done
            
            # ベースディレクトリも削除
            rm -rf "$BASE_DIR" 2>/dev/null || true
        else
            log_info "$ORG_ID の既存worktreeを保持してスキップします"
            continue
        fi
    fi

    # ベースブランチ確認・作成
    log_info "ベースブランチを確認中..."
    if ! git show-ref --verify --quiet "refs/heads/orgs/$ORG_ID/base"; then
        log_info "ベースブランチを作成中: orgs/$ORG_ID/base"
        git checkout -b "orgs/$ORG_ID/base"
        git push -u origin "orgs/$ORG_ID/base" 2>/dev/null || log_warn "ブランチプッシュに失敗（リモートなし？）"
        git checkout main
    fi

    # 各Agentブランチ作成・worktree設定
    declare -a agents=("01boss" "01worker-a" "01worker-b" "01worker-c")
    declare -a instructions=("boss_instructions.md" "worker_instructions.md" "worker_instructions.md" "worker_instructions.md")

    for i in "${!agents[@]}"; do
        agent="${agents[$i]}"
        instruction="${instructions[$i]}"
        branch_name="orgs/$ORG_ID/$agent"
        worktree_path="$BASE_DIR/$agent"
        
        log_info "🔧 $ORG_ID/$agent の設定中..."
        
        # ブランチ作成
        if ! git show-ref --verify --quiet "refs/heads/$branch_name"; then
            log_info "ブランチ作成: $branch_name"
            git branch "$branch_name" "orgs/$ORG_ID/base"
        fi
        
        # Worktree作成
        if [[ ! -d "$worktree_path" ]]; then
            log_info "Worktree作成: $worktree_path"
            git worktree add "$worktree_path" "$branch_name"
        fi
        
        # Agent指示書配置
        log_info "指示書配置: docs/$instruction → $worktree_path/CLAUDE.md"
        cp "docs/$instruction" "$worktree_path/CLAUDE.md"
        
        # 初期commit
        cd "$worktree_path"
        git add CLAUDE.md
        if ! git diff --cached --quiet; then
            git commit -m "Add $agent agent instructions for $ORG_ID" 2>/dev/null || log_info "コミット済み"
        fi
        cd - > /dev/null
        
        log_success "$ORG_ID/$agent セットアップ完了"
    done
    
    echo ""
    log_success "🏢 組織 $ORG_ID セットアップ完了！"
    echo ""
done

echo ""
echo "✅ 全4組織 Multi-Agent Worktree セットアップ完了！"
echo ""
echo "📂 作成されたWorktree構成:"
for ORG_ID in "${organizations[@]}"; do
    echo "  $ORG_ID:"
    echo "    orgs/$ORG_ID/01boss        - Boss Agent"
    echo "    orgs/$ORG_ID/01worker-a    - Worker-A"
    echo "    orgs/$ORG_ID/01worker-b    - Worker-B"
    echo "    orgs/$ORG_ID/01worker-c    - Worker-C"
done
echo ""
echo "🚀 次のステップ:"
echo "  1. tmux環境起動: ./scripts/create_multiagent_tmux.sh"
echo "  2. 各Agentで指示書確認: cat CLAUDE.md"
echo "  3. 具体的タスク設定後、実装開始"
echo ""
echo "🔗 確認コマンド:"
echo "  git worktree list"
echo "  ls -la orgs/"
echo ""

# Worktree一覧表示
log_info "現在のWorktree一覧:"
git worktree list 