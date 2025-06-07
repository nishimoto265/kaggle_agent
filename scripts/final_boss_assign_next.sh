#!/bin/bash

# 🎯 Final Boss 次タスク自動割り当てシステム
# 利用可能な組織に次のタスクを自動割り当て

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🎯 Final Boss 次タスク自動割り当て - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
ASSIGN_LOG="$LOG_DIR/assign_next_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$ASSIGN_LOG"
}

# 次のタスクを取得
get_next_task() {
    log "🔍 次のタスクを検索中..."
    
    if [ ! -f "$PROJECT_ROOT/PROJECT_CHECKLIST.md" ]; then
        log "❌ PROJECT_CHECKLIST.md が見つかりません"
        return 1
    fi
    
    # 高優先度タスクを優先的に取得
    local next_task=$(grep "^- \[ \].*高優先度" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" | head -1 | sed 's/^- \[ \] //' | cut -d'(' -f1 | xargs)
    
    if [ -z "$next_task" ]; then
        # 高優先度がなければ通常のタスクを取得
        next_task=$(grep "^- \[ \]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" | head -1 | sed 's/^- \[ \] //' | cut -d'(' -f1 | xargs)
    fi
    
    if [ ! -z "$next_task" ]; then
        log "📋 次のタスク発見: $next_task"
        echo "$next_task"
        return 0
    else
        log "✅ 全てのタスクが完了しています"
        return 1
    fi
}

# 利用可能な組織名を生成
get_available_org_name() {
    log "🏢 利用可能な組織を検索中..."
    
    for i in $(seq -f "%02g" 1 99); do
        local org_name="org-$i"
        if [ ! -d "$PROJECT_ROOT/orgs/$org_name" ]; then
            log "🆕 利用可能な組織発見: $org_name"
            echo "$org_name"
            return 0
        fi
    done
    
    log "⚠️ 利用可能な組織名がありません（最大99組織）"
    return 1
}

# タスクユニット作成
create_task_unit() {
    local task_name="$1"
    
    log "📝 タスクユニット作成開始: $task_name"
    
    cd "$PROJECT_ROOT"
    if bash scripts/create_task_unit.sh "$task_name" "自動生成タスク - Final Boss Auto Assignment"; then
        log "✅ タスクユニット作成完了: $task_name"
        return 0
    else
        log "❌ タスクユニット作成失敗: $task_name"
        return 1
    fi
}

# 組織にタスク割り当て
assign_task_to_organization() {
    local task_name="$1"
    local org_name="$2"
    
    log "🎯 タスク割り当て開始: $task_name -> $org_name"
    
    cd "$PROJECT_ROOT"
    if bash scripts/assign_task_to_boss.sh "$task_name" "$org_name"; then
        log "✅ タスク割り当て完了: $task_name -> $org_name"
        return 0
    else
        log "❌ タスク割り当て失敗: $task_name -> $org_name"
        return 1
    fi
}

# プロジェクトチェックリスト更新
update_project_checklist() {
    local task_name="$1"
    local org_name="$2"
    
    log "📋 プロジェクトチェックリスト更新: $task_name"
    
    if [ -f "$PROJECT_ROOT/PROJECT_CHECKLIST.md" ]; then
        # タスクを進行中としてマーク
        sed -i "s/^- \[ \] $task_name.*$/- [⏳] $task_name ($org_name) - 自動割り当て済み $(date +%Y-%m-%d)/" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || {
            # より柔軟なパターンマッチング
            sed -i "s/^- \[ \] .*$task_name.*$/- [⏳] $task_name ($org_name) - 自動割り当て済み $(date +%Y-%m-%d)/" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || true
        }
        log "✅ プロジェクトチェックリスト更新完了"
    else
        log "⚠️ PROJECT_CHECKLIST.md が見つかりません"
    fi
}

# Boss通知メッセージ送信
send_boss_notification() {
    local task_name="$1"
    local org_name="$2"
    
    log "📨 Boss通知メッセージ作成: $org_name"
    
    local notification_file="$PROJECT_ROOT/shared_messages/to_boss_${org_name}_new_task_$(date +%s).md"
    
    cat > "$notification_file" << EOF
# 🎯 新しいタスク割り当て通知

## タスク情報
- **タスク名**: $task_name
- **組織**: $org_name
- **割り当て日時**: $(date)
- **割り当て者**: Final Boss (自動)
- **優先度**: 高
- **期限**: $(date -d "+7 days" +%Y-%m-%d)

## 実行指示
1. タスク要件書を確認: \`tasks/${task_name}_requirements.md\`
2. チェックリストを確認: \`tasks/${task_name}_checklist.md\`
3. 3名のWorkerに作業分担を指示
4. 定期的な進捗報告を実行 (24時間毎)
5. 完了時はFinal Bossに完了報告を送信

## 品質基準
- ✅ テストカバレッジ95%以上
- ✅ 静的解析エラー0件
- ✅ ドキュメント完備
- ✅ パフォーマンス基準満足

## 完了報告方法
タスク完了時は以下のコマンドを実行してください：
\`\`\`bash
bash scripts/boss_send_message.sh completed "$task_name"
\`\`\`

## 支援・質問
問題が発生した場合は以下で報告してください：
\`\`\`bash
bash scripts/boss_send_message.sh issue "問題の詳細"
bash scripts/boss_send_message.sh request "支援要求の詳細"
\`\`\`

🎯 **早期完了を目指して効率的に進めてください！**

---
**Final Boss - 自動タスク割り当てシステム**
EOF
    
    log "✅ Boss通知メッセージ作成完了: $notification_file"
}

# 統計情報更新
update_assignment_statistics() {
    local task_name="$1"
    local org_name="$2"
    
    log "📊 割り当て統計更新開始"
    
    local stats_file="$PROJECT_ROOT/statistics/assignments_$(date +%Y%m%d).json"
    mkdir -p "$PROJECT_ROOT/statistics"
    
    # 既存の統計があれば読み込み、なければ初期化
    local assignment_count=1
    if [ -f "$stats_file" ]; then
        assignment_count=$(cat "$stats_file" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('assignments_today', 0) + 1)
except:
    print(1)
" 2>/dev/null || echo 1)
    fi
    
    cat > "$stats_file" << EOF
{
    "date": "$(date +%Y-%m-%d)",
    "timestamp": "$(date -Iseconds)",
    "assignments_today": $assignment_count,
    "last_assignment": {
        "task": "$task_name",
        "organization": "$org_name",
        "timestamp": "$(date -Iseconds)",
        "assignment_type": "automatic"
    },
    "current_status": {
        "active_organizations": $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l),
        "pending_tasks": $(grep -c "^- \[ \]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0),
        "in_progress_tasks": $(grep -c "^- \[⏳\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0),
        "completed_tasks": $(grep -c "^- \[x\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)
    }
}
EOF
    
    log "📈 割り当て統計更新完了: $stats_file"
}

# 成功通知ファイル作成
create_assignment_notification() {
    local task_name="$1"
    local org_name="$2"
    
    log "📢 割り当て成功通知作成"
    
    local notification_file="$PROJECT_ROOT/shared_messages/.assignment_success_${org_name}_$(date +%s)"
    
    cat > "$notification_file" << EOF
{
    "type": "task_assigned",
    "task": "$task_name",
    "organization": "$org_name",
    "timestamp": "$(date -Iseconds)",
    "assignment_method": "automatic",
    "next_action": "monitor_progress"
}
EOF
    
    log "✅ 割り当て成功通知作成完了: $(basename "$notification_file")"
}

# メイン処理
main() {
    log "🚀 Final Boss 次タスク自動割り当て開始"
    
    # 次のタスクを取得
    local next_task=$(get_next_task)
    if [ $? -ne 0 ] || [ -z "$next_task" ]; then
        log "🏁 割り当て可能なタスクがありません"
        echo "🏁 全てのタスクが完了または進行中です"
        return 0
    fi
    
    # 利用可能な組織を取得
    local available_org=$(get_available_org_name)
    if [ $? -ne 0 ] || [ -z "$available_org" ]; then
        log "⚠️ 利用可能な組織がありません"
        echo "⚠️ 現在、新しいタスクを割り当てる組織がありません"
        return 1
    fi
    
    log "🎯 割り当て実行: $next_task -> $available_org"
    
    # タスクユニット作成
    if ! create_task_unit "$next_task"; then
        log "❌ タスクユニット作成失敗により処理を中断"
        return 1
    fi
    
    # 組織にタスク割り当て
    if ! assign_task_to_organization "$next_task" "$available_org"; then
        log "❌ タスク割り当て失敗により処理を中断"
        return 1
    fi
    
    # プロジェクトチェックリスト更新
    update_project_checklist "$next_task" "$available_org"
    
    # Boss通知メッセージ送信
    send_boss_notification "$next_task" "$available_org"
    
    # 統計情報更新
    update_assignment_statistics "$next_task" "$available_org"
    
    # 成功通知作成
    create_assignment_notification "$next_task" "$available_org"
    
    log "🎉 次タスク自動割り当て完了: $next_task -> $available_org"
    
    # サマリー表示
    echo ""
    echo "🎯 割り当てサマリー"
    echo "=================="
    echo "新しいタスク: $next_task"
    echo "割り当て組織: $available_org"
    echo "期限: $(date -d "+7 days" +%Y-%m-%d)"
    echo "ログファイル: $ASSIGN_LOG"
    echo ""
    echo "✅ $available_org に $next_task が自動割り当てされました"
    echo "📨 Boss通知メッセージを送信済み"
    
    return 0
}

# 引数処理
case "${1:-assign}" in
    "assign")
        main
        ;;
    "check-next")
        echo "🔍 次のタスク確認"
        next_task=$(get_next_task)
        if [ $? -eq 0 ]; then
            echo "次のタスク: $next_task"
        else
            echo "割り当て可能なタスクなし"
        fi
        ;;
    "check-org")
        echo "🏢 利用可能な組織確認"
        available_org=$(get_available_org_name)
        if [ $? -eq 0 ]; then
            echo "利用可能な組織: $available_org"
        else
            echo "利用可能な組織なし"
        fi
        ;;
    "status")
        echo "📊 次タスク割り当てシステム状況"
        echo "==============================="
        echo "保留タスク: $(grep -c "^- \[ \]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)"
        echo "進行中タスク: $(grep -c "^- \[⏳\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)"
        echo "完了タスク: $(grep -c "^- \[x\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)"
        echo "アクティブ組織: $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)"
        ;;
    *)
        echo "使用方法: $0 {assign|check-next|check-org|status}"
        echo ""
        echo "  assign      - 次のタスクを自動割り当て"
        echo "  check-next  - 次のタスクを確認"
        echo "  check-org   - 利用可能な組織を確認" 
        echo "  status      - システム状況を表示"
        exit 1
        ;;
esac 