#!/bin/bash

# 🗑️ Final Boss 組織クリーンアップシステム
# 完了した組織の削除・アーカイブを実行

set -e

ORG_NAME="$1"
TASK_NAME="$2"

if [ -z "$ORG_NAME" ] || [ -z "$TASK_NAME" ]; then
    echo "使用方法: $0 <ORG_NAME> <TASK_NAME>"
    echo "例: $0 org-01 data_processing_foundation"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🗑️ Final Boss 組織クリーンアップ: $ORG_NAME ($TASK_NAME) - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
CLEANUP_LOG="$LOG_DIR/cleanup_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$CLEANUP_LOG"
}

# アーカイブディレクトリ作成
ARCHIVE_DIR="$PROJECT_ROOT/archives/completed_$(date +%Y%m%d)/$ORG_NAME"
mkdir -p "$ARCHIVE_DIR"

log "🚀 組織クリーンアップ開始: $ORG_NAME"

# 1. 成果物のアーカイブ
archive_organization() {
    log "📦 成果物アーカイブ開始: $ORG_NAME"
    
    local org_path="$PROJECT_ROOT/orgs/$ORG_NAME"
    
    if [ -d "$org_path" ]; then
        # 組織ディレクトリをアーカイブ
        cp -r "$org_path" "$ARCHIVE_DIR/"
        
        # 品質レポートもアーカイブ
        if [ -f "$PROJECT_ROOT/quality_reports/${ORG_NAME}_quality_report.json" ]; then
            cp "$PROJECT_ROOT/quality_reports/${ORG_NAME}_quality_report.json" "$ARCHIVE_DIR/"
        fi
        
        # アーカイブメタデータ作成
        cat > "$ARCHIVE_DIR/completion_metadata.json" << EOF
{
    "organization": "$ORG_NAME",
    "task_name": "$TASK_NAME",
    "completion_date": "$(date -Iseconds)",
    "archive_date": "$(date -Iseconds)",
    "final_boss_approval": "completed",
    "quality_score": $(cat "$PROJECT_ROOT/quality_reports/${ORG_NAME}_quality_report.json" 2>/dev/null | python3 -c "import json, sys; print(json.load(sys.stdin).get('overall_score', 0))" 2>/dev/null || echo 0),
    "archive_size": "$(du -sh "$ARCHIVE_DIR" | cut -f1)",
    "cleanup_reason": "task_completion"
}
EOF
        
        log "✅ アーカイブ完了: $ARCHIVE_DIR"
    else
        log "⚠️ 組織ディレクトリが見つかりません: $org_path"
    fi
}

# 2. Git worktree削除
cleanup_worktree() {
    log "🌿 Git worktree削除開始: $ORG_NAME"
    
    cd "$PROJECT_ROOT"
    
    # worktreeリストをチェック
    if git worktree list | grep -q "$ORG_NAME"; then
        # worktreeを削除
        git worktree remove "orgs/$ORG_NAME" --force 2>/dev/null || {
            log "⚠️ worktree削除で警告が発生（通常は問題ありません）"
        }
        log "✅ Git worktree削除完了: $ORG_NAME"
    else
        log "ℹ️ 対象のworktreeが見つかりません: $ORG_NAME"
    fi
}

# 3. 組織ディレクトリ削除
cleanup_organization_directory() {
    log "🗂️ 組織ディレクトリ削除開始: $ORG_NAME"
    
    local org_path="$PROJECT_ROOT/orgs/$ORG_NAME"
    
    if [ -d "$org_path" ]; then
        # ディレクトリを削除
        rm -rf "$org_path"
        log "✅ 組織ディレクトリ削除完了: $org_path"
    else
        log "ℹ️ 組織ディレクトリが既に存在しません: $org_path"
    fi
}

# 4. 関連ファイルのクリーンアップ
cleanup_related_files() {
    log "📄 関連ファイルクリーンアップ開始: $ORG_NAME"
    
    # 完了報告メッセージを処理済みに移動（既に移動済みの場合は何もしない）
    local completed_msg="$PROJECT_ROOT/shared_messages/from_boss_${ORG_NAME}_completed_*.md"
    if ls $completed_msg 1>/dev/null 2>&1; then
        mkdir -p "$PROJECT_ROOT/shared_messages/processed"
        mv $completed_msg "$PROJECT_ROOT/shared_messages/processed/" 2>/dev/null || true
        log "📄 完了報告メッセージを処理済みに移動"
    fi
    
    # 品質レポートをアーカイブディレクトリに移動
    if [ -f "$PROJECT_ROOT/quality_reports/${ORG_NAME}_quality_report.json" ]; then
        mv "$PROJECT_ROOT/quality_reports/${ORG_NAME}_quality_report.json" "$ARCHIVE_DIR/" 2>/dev/null || true
        log "📊 品質レポートをアーカイブに移動"
    fi
    
    log "✅ 関連ファイルクリーンアップ完了"
}

# 5. プロジェクトチェックリスト更新
update_project_checklist() {
    log "📋 プロジェクトチェックリスト更新開始"
    
    if [ -f "$PROJECT_ROOT/PROJECT_CHECKLIST.md" ]; then
        # タスクを完了としてマーク
        sed -i "s/^- \[ \] $TASK_NAME.*$/- [x] $TASK_NAME ($ORG_NAME) - ✅ $(date +%Y-%m-%d) 完了・アーカイブ済み/" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || {
            # より柔軟なパターンマッチング
            sed -i "s/^- \[⏳\] $TASK_NAME.*$/- [x] $TASK_NAME ($ORG_NAME) - ✅ $(date +%Y-%m-%d) 完了・アーカイブ済み/" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || {
                # タスク名の部分マッチでも更新
                sed -i "s/^- \[ \] .*$TASK_NAME.*$/- [x] $TASK_NAME ($ORG_NAME) - ✅ $(date +%Y-%m-%d) 完了・アーカイブ済み/" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || true
            }
        }
        log "✅ プロジェクトチェックリスト更新完了"
    else
        log "⚠️ PROJECT_CHECKLIST.md が見つかりません"
    fi
}

# 6. 統計情報更新
update_cleanup_statistics() {
    log "📊 クリーンアップ統計更新開始"
    
    local stats_file="$PROJECT_ROOT/statistics/cleanup_$(date +%Y%m%d).json"
    mkdir -p "$PROJECT_ROOT/statistics"
    
    # 既存の統計があれば読み込み、なければ初期化
    local completed_count=1
    if [ -f "$stats_file" ]; then
        completed_count=$(cat "$stats_file" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('completed_organizations_today', 0) + 1)
except:
    print(1)
" 2>/dev/null || echo 1)
    fi
    
    cat > "$stats_file" << EOF
{
    "date": "$(date +%Y-%m-%d)",
    "timestamp": "$(date -Iseconds)",
    "completed_organizations_today": $completed_count,
    "last_cleanup": {
        "organization": "$ORG_NAME",
        "task": "$TASK_NAME",
        "timestamp": "$(date -Iseconds)",
        "archive_location": "$ARCHIVE_DIR"
    },
    "current_status": {
        "active_organizations": $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l),
        "completed_tasks": $(grep -c "^- \[x\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0),
        "pending_tasks": $(grep -c "^- \[ \]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)
    }
}
EOF
    
    log "📈 クリーンアップ統計更新完了: $stats_file"
}

# 7. 成功通知ファイル作成
create_success_notification() {
    log "📢 成功通知作成開始"
    
    local notification_file="$PROJECT_ROOT/shared_messages/.cleanup_success_${ORG_NAME}_$(date +%s)"
    
    cat > "$notification_file" << EOF
{
    "type": "cleanup_completed",
    "organization": "$ORG_NAME",
    "task": "$TASK_NAME",
    "timestamp": "$(date -Iseconds)",
    "archive_location": "$ARCHIVE_DIR",
    "next_action": "assign_new_task"
}
EOF
    
    log "✅ 成功通知作成完了: $(basename "$notification_file")"
}

# メイン実行
main() {
    log "🚀 Final Boss クリーンアップ開始: $ORG_NAME/$TASK_NAME"
    
    # 各ステップを順次実行
    archive_organization
    cleanup_worktree
    cleanup_organization_directory
    cleanup_related_files
    update_project_checklist
    update_cleanup_statistics
    create_success_notification
    
    log "🎉 Final Boss クリーンアップ完了: $ORG_NAME"
    
    # サマリー表示
    echo ""
    echo "🎯 クリーンアップサマリー"
    echo "========================"
    echo "組織名: $ORG_NAME"
    echo "タスク名: $TASK_NAME"
    echo "アーカイブ場所: $ARCHIVE_DIR"
    echo "ログファイル: $CLEANUP_LOG"
    echo "完了時刻: $(date)"
    echo ""
    echo "✅ $ORG_NAME が正常にクリーンアップされました"
}

# 実行
main 