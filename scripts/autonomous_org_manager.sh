#!/bin/bash

# 🤖 Final Boss 自律組織管理システム
# 完了したorgの自動削除・新タスク割り当て

set -e

echo "🤖 Final Boss 自律組織管理システム起動 - $(date)"
echo "================================================================"

# 設定
COMPLETION_THRESHOLD=95  # 完了閾値 (%)
WORKTREE_BASE="orgs"
SHARED_MESSAGES="shared_messages"

# ログ設定
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/autonomous_manager_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 完了組織の検出
detect_completed_orgs() {
    log "🔍 完了組織の検出を開始..."
    
    completed_orgs=()
    
    for org_dir in orgs/org-*/; do
        if [ ! -d "$org_dir" ]; then
            continue
        fi
        
        org_name=$(basename "$org_dir")
        log "📊 $org_name の完了状況をチェック中..."
        
        # Boss完了報告の確認
        boss_report="$SHARED_MESSAGES/from_boss_${org_name}_completed.md"
        if [ -f "$boss_report" ]; then
            log "✅ $org_name: Boss完了報告あり"
            
            # 品質評価確認
            quality_report="quality_reports/${org_name}_quality_report.json"
            if [ -f "$quality_report" ]; then
                score=$(python3 -c "
import json
with open('$quality_report', 'r') as f:
    data = json.load(f)
print(data.get('overall_score', 0))
" 2>/dev/null || echo 0)
                
                if (( $(echo "$score >= $COMPLETION_THRESHOLD" | bc -l) )); then
                    log "🎯 $org_name: 品質基準クリア ($score%)"
                    completed_orgs+=("$org_name")
                else
                    log "⚠️ $org_name: 品質基準未達 ($score%)"
                fi
            else
                log "❌ $org_name: 品質評価レポート未発見"
            fi
        else
            log "⏳ $org_name: Boss完了報告なし"
        fi
    done
    
    log "🎯 完了組織数: ${#completed_orgs[@]}"
    printf '%s\n' "${completed_orgs[@]}"
}

# 完了組織のアーカイブと削除
archive_and_cleanup_org() {
    local org_name=$1
    
    log "🗂️ $org_name のアーカイブと削除を開始..."
    
    # アーカイブディレクトリ作成
    archive_dir="archives/completed_$(date +%Y%m%d)/$org_name"
    mkdir -p "$archive_dir"
    
    # 成果物をアーカイブ
    if [ -d "orgs/$org_name" ]; then
        log "📦 $org_name の成果物をアーカイブ中..."
        cp -r "orgs/$org_name" "$archive_dir/"
        
        # メタデータ追加
        cat > "$archive_dir/completion_metadata.json" << EOF
{
    "completion_date": "$(date -Iseconds)",
    "final_boss_verification": "completed",
    "quality_score": $(cat "quality_reports/${org_name}_quality_report.json" 2>/dev/null | python3 -c "import json, sys; print(json.load(sys.stdin).get('overall_score', 0))" 2>/dev/null || echo 0),
    "archive_reason": "autonomous_completion_cleanup"
}
EOF
        
        log "✅ $org_name アーカイブ完了: $archive_dir"
    fi
    
    # 作業ディレクトリの削除
    if [ -d "orgs/$org_name" ]; then
        log "🗑️ $org_name 作業ディレクトリを削除中..."
        rm -rf "orgs/$org_name"
        log "✅ $org_name 削除完了"
    fi
    
    # worktreeがある場合は削除
    if git worktree list | grep -q "$org_name"; then
        log "🌿 $org_name worktreeを削除中..."
        git worktree remove "orgs/$org_name" --force 2>/dev/null || true
        log "✅ $org_name worktree削除完了"
    fi
    
    # 完了報告ファイルを処理済みディレクトリに移動
    if [ -f "$SHARED_MESSAGES/from_boss_${org_name}_completed.md" ]; then
        mkdir -p "$SHARED_MESSAGES/processed"
        mv "$SHARED_MESSAGES/from_boss_${org_name}_completed.md" "$SHARED_MESSAGES/processed/"
        log "📄 完了報告ファイルを処理済みに移動"
    fi
}

# 次のタスクを取得
get_next_task() {
    log "🎯 次のタスクを取得中..."
    
    # PROJECT_CHECKLIST.mdから未完了の高優先度タスクを取得
    if [ -f "PROJECT_CHECKLIST.md" ]; then
        next_task=$(grep "^- \[ \].*高優先度" PROJECT_CHECKLIST.md | head -1 | sed 's/^- \[ \] //' | cut -d' ' -f1)
        
        if [ -z "$next_task" ]; then
            # 高優先度がなければ通常のタスクを取得
            next_task=$(grep "^- \[ \]" PROJECT_CHECKLIST.md | head -1 | sed 's/^- \[ \] //' | cut -d' ' -f1)
        fi
        
        if [ ! -z "$next_task" ]; then
            log "📋 次のタスク発見: $next_task"
            echo "$next_task"
        else
            log "✅ 全てのタスクが完了しています"
            echo ""
        fi
    else
        log "❌ PROJECT_CHECKLIST.md が見つかりません"
        echo ""
    fi
}

# 利用可能な組織名を生成
get_available_org_name() {
    for i in {01..99}; do
        org_name="org-$i"
        if [ ! -d "orgs/$org_name" ]; then
            echo "$org_name"
            return
        fi
    done
    echo ""  # 利用可能な組織名がない場合
}

# 新しいタスクを割り当て
assign_new_task() {
    local task_name=$1
    local org_name=$2
    
    log "🚀 新しいタスクの割り当て開始: $task_name -> $org_name"
    
    # タスクユニット作成
    if ./scripts/create_task_unit.sh "$task_name" "自動生成タスク"; then
        log "✅ タスクユニット作成完了: $task_name"
        
        # 組織にタスクを割り当て
        if ./scripts/assign_task_to_boss.sh "$task_name" "$org_name"; then
            log "✅ タスク割り当て完了: $task_name -> $org_name"
            
            # プロジェクトチェックリスト更新
            sed -i "s/^- \[ \] $task_name/- [⏳] $task_name ($org_name) - 割り当て済み $(date +%Y-%m-%d)/" PROJECT_CHECKLIST.md
            
            # Boss通知メッセージ作成
            cat > "$SHARED_MESSAGES/to_boss_${org_name}_new_task.md" << EOF
# 🎯 新しいタスク割り当て通知

## タスク情報
- **タスク名**: $task_name
- **組織**: $org_name  
- **割り当て日時**: $(date)
- **優先度**: 高
- **期限**: $(date -d "+7 days" +%Y-%m-%d)

## 実行指示
1. タスク要件書を確認: \`tasks/${task_name}_requirements.md\`
2. チェックリストを確認: \`tasks/${task_name}_checklist.md\`
3. 3名のWorkerに作業分担を指示
4. 定期的な進捗報告を実行
5. 完了時はFinal Bossに報告

## 品質基準
- テストカバレッジ95%以上
- 静的解析エラー0件
- ドキュメント完備
- パフォーマンス基準満足

🎯 早期完了を目指して効率的に進めてください！
EOF
            
            log "📨 Boss通知メッセージ作成完了"
            return 0
        else
            log "❌ タスク割り当て失敗: $task_name -> $org_name"
            return 1
        fi
    else
        log "❌ タスクユニット作成失敗: $task_name"
        return 1
    fi
}

# 統計情報の更新
update_statistics() {
    log "📊 統計情報を更新中..."
    
    # 統計ファイル作成
    stats_file="statistics/autonomous_operations_$(date +%Y%m%d).json"
    mkdir -p "statistics"
    
    # 現在の状況を集計
    total_orgs=$(ls -1d orgs/org-*/ 2>/dev/null | wc -l)
    active_tasks=$(grep "^- \[⏳\]" PROJECT_CHECKLIST.md | wc -l)
    completed_tasks=$(grep "^- \[x\]" PROJECT_CHECKLIST.md | wc -l)
    pending_tasks=$(grep "^- \[ \]" PROJECT_CHECKLIST.md | wc -l)
    
    cat > "$stats_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "operation_type": "autonomous_management",
    "current_status": {
        "active_organizations": $total_orgs,
        "active_tasks": $active_tasks,
        "completed_tasks": $completed_tasks,
        "pending_tasks": $pending_tasks
    },
    "completed_organizations_today": ${#completed_orgs[@]},
    "new_assignments_today": $(grep "$(date +%Y-%m-%d)" PROJECT_CHECKLIST.md | grep "割り当て済み" | wc -l)
}
EOF
    
    log "📈 統計情報更新完了: $stats_file"
}

# メイン処理
main() {
    log "🚀 自律組織管理メイン処理開始"
    
    # 完了組織の検出
    completed_orgs=($(detect_completed_orgs))
    
    # 完了組織の処理
    for org_name in "${completed_orgs[@]}"; do
        log "🎉 完了組織の処理開始: $org_name"
        archive_and_cleanup_org "$org_name"
        
        # 次のタスクがあれば新しい組織に割り当て
        next_task=$(get_next_task)
        if [ ! -z "$next_task" ]; then
            new_org_name=$(get_available_org_name)
            if [ ! -z "$new_org_name" ]; then
                log "🔄 継続的タスク割り当て: $next_task -> $new_org_name"
                assign_new_task "$next_task" "$new_org_name"
            else
                log "⚠️ 利用可能な組織名がありません"
            fi
        else
            log "🏁 全てのタスクが完了しました！"
        fi
    done
    
    # 統計情報更新
    update_statistics
    
    log "✅ 自律組織管理完了 - 処理組織数: ${#completed_orgs[@]}"
    
    # サマリー出力
    echo ""
    echo "📊 自律管理サマリー"
    echo "===================="
    echo "処理した組織: ${#completed_orgs[@]}"
    echo "アクティブ組織: $(ls -1d orgs/org-*/ 2>/dev/null | wc -l)"
    echo "ログファイル: $LOG_FILE"
    echo ""
}

# 実行
main "$@" 