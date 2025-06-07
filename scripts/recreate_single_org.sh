#!/bin/bash

# 単一組織 worktree 再生成スクリプト
# Usage: ./scripts/recreate_single_org.sh org-01

set -e

ORG_ID=$1

if [ -z "$ORG_ID" ]; then
    echo "Usage: $0 <org-id>"
    echo "Example: $0 org-01"
    echo "Available orgs: org-01, org-02, org-03, org-04"
    exit 1
fi

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

BASE_DIR="orgs/$ORG_ID"

echo "🔄 $ORG_ID 単一組織 worktree 再生成開始"
echo "========================================"

# 既存worktreeの削除
if [[ -d "$BASE_DIR" ]]; then
    log_warn "既存のworktreeを削除中: $BASE_DIR"
    
    # 各worktreeを個別に削除
    for agent in "01boss" "01worker-a" "01worker-b" "01worker-c"; do
        if [[ -d "$BASE_DIR/$agent" ]]; then
            git worktree remove "$BASE_DIR/$agent" 2>/dev/null || true
            log_info "削除: $BASE_DIR/$agent"
        fi
    done
    
    # ブランチ削除
    for agent in "01boss" "01worker-a" "01worker-b" "01worker-c"; do
        branch_name="orgs/$ORG_ID/$agent"
        git branch -D "$branch_name" 2>/dev/null || log_warn "ブランチ $branch_name は存在しません"
    done
    
    # ベースディレクトリも削除
    rm -rf "$BASE_DIR" 2>/dev/null || true
    log_success "$ORG_ID 完全削除完了"
fi

# ベースディレクトリ作成
mkdir -p "$BASE_DIR"

# ベースブランチ確認・作成
log_info "ベースブランチを確認中..."
if ! git show-ref --verify --quiet "refs/heads/orgs/$ORG_ID/base" 2>/dev/null; then
    log_info "ベースブランチを作成中: orgs/$ORG_ID/base"
    git checkout -b "orgs/$ORG_ID/base" 2>/dev/null || true
    git push -u origin "orgs/$ORG_ID/base" 2>/dev/null || log_warn "ブランチプッシュに失敗（リモートなし？）"
    git checkout main 2>/dev/null || true
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
    log_info "ブランチ作成: $branch_name"
    if ! git branch "$branch_name" main 2>/dev/null; then
        log_warn "ブランチ作成に失敗、リセットして再試行: $branch_name"
        git checkout main 2>/dev/null || true
        git branch -D "$branch_name" 2>/dev/null || true
        git branch "$branch_name" main 2>/dev/null || log_error "ブランチ作成に失敗: $branch_name"
    fi
    
    # Worktree作成
    log_info "Worktree作成: $worktree_path"
    git worktree add "$worktree_path" "$branch_name"
    
    # 確実にディレクトリが作成されたか確認
    if [[ ! -d "$worktree_path" ]]; then
        log_error "Worktree作成に失敗: $worktree_path"
        continue
    fi
    
    # Agent指示書配置
    log_info "指示書配置: docs/$instruction → $worktree_path/CLAUDE.md"
    cp "docs/$instruction" "$worktree_path/CLAUDE.md"
    
    # 初期commit
    cd "$worktree_path"
    git add CLAUDE.md 2>/dev/null || true
    if ! git diff --cached --quiet 2>/dev/null; then
        git commit -m "Add $agent agent instructions for $ORG_ID" 2>/dev/null || log_info "コミット済み"
    fi
    cd - > /dev/null
    
    log_success "$ORG_ID/$agent セットアップ完了"
    
    # 作成確認
    if [[ -f "$worktree_path/CLAUDE.md" ]]; then
        log_success "✅ $worktree_path/CLAUDE.md 作成確認"
    else
        log_error "❌ $worktree_path/CLAUDE.md 作成失敗"
    fi
done

echo ""
log_success "🏢 組織 $ORG_ID 再生成完了！"
echo ""

# 作成確認
echo "📂 作成確認:"
echo "  $ORG_ID:"
for agent in "01boss" "01worker-a" "01worker-b" "01worker-c"; do
    if [[ -f "orgs/$ORG_ID/$agent/CLAUDE.md" ]]; then
        echo "    ✅ orgs/$ORG_ID/$agent        - $(head -1 orgs/$ORG_ID/$agent/CLAUDE.md | cut -c1-50)..."
    else
        echo "    ❌ orgs/$ORG_ID/$agent        - 作成失敗"
    fi
done
echo ""

echo "🚀 次のステップ:"
echo "  1. Boss・Workerに新タスク指示"
echo "  2. ./scripts/quick_send.sh boss0X \"新タスク開始\""
echo ""

# Worktree一覧表示
log_info "現在のWorktree一覧:"
git worktree list 