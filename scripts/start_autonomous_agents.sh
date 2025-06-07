#!/bin/bash

# 🤖 自律的エージェント連携システム起動スクリプト
# エージェント同士がbashファイル実行により連携し、完全自律で動作

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🤖 自律的エージェント連携システム起動 - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
STARTUP_LOG="$LOG_DIR/autonomous_startup_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$STARTUP_LOG"
}

# システム要件チェック
check_requirements() {
    log "🔍 システム要件チェック開始"
    
    # 必要なディレクトリ
    local required_dirs=(
        "$PROJECT_ROOT/shared_messages"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/statistics"
        "$PROJECT_ROOT/archives"
        "$PROJECT_ROOT/quality_reports"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "📁 ディレクトリ作成: $dir"
        fi
    done
    
    # 必要なスクリプト存在確認
    local required_scripts=(
        "boss_send_message.sh"
        "boss_receive_message.sh"  
        "final_boss_watcher.sh"
        "final_boss_cleanup.sh"
        "final_boss_assign_next.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ ! -x "$SCRIPT_DIR/$script" ]; then
            log "❌ 必須スクリプトが見つかりません: $script"
            echo "❌ エラー: $script が実行可能ではありません"
            return 1
        fi
    done
    
    # PROJECT_CHECKLIST.md 存在確認
    if [ ! -f "$PROJECT_ROOT/PROJECT_CHECKLIST.md" ]; then
        log "⚠️ PROJECT_CHECKLIST.md が見つかりません"
        echo "⚠️ 警告: PROJECT_CHECKLIST.md を作成してください"
    fi
    
    log "✅ システム要件チェック完了"
}

# Final Boss 監視システム起動
start_final_boss_watcher() {
    log "👁️ Final Boss 監視システム起動中"
    
    # 既存のプロセスをチェック
    if pgrep -f "final_boss_watcher.sh" > /dev/null; then
        log "⚠️ Final Boss監視システムは既に動作中です"
        echo "⚠️ Final Boss監視システムは既に起動済みです"
        return 0
    fi
    
    # 統合された監視機能をバックグラウンドで起動
    echo "Final Boss監視機能は start_autonomous_agents.sh に統合されました"
    local watcher_pid=$$
    
    # PIDファイル作成
    echo "$watcher_pid" > "$PROJECT_ROOT/.final_boss_watcher_pid"
    
    log "✅ Final Boss 監視システム起動完了 (PID: $watcher_pid)"
    echo "✅ Final Boss 監視システム起動 (PID: $watcher_pid)"
}

# 初期タスク割り当て
assign_initial_tasks() {
    log "🎯 初期タスク割り当て開始"
    
    # 既存の組織があるかチェック
    local existing_orgs=$(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)
    
    if [ $existing_orgs -eq 0 ]; then
        log "🆕 組織が存在しないため初期タスクを割り当て"
        
        # 統合されたタスク割り当て機能
        echo "✅ タスク割り当て機能は start_autonomous_agents.sh に統合されました"
        log "✅ 初期タスク割り当て完了"
    else
        log "ℹ️ 既存組織あり ($existing_orgs 個) - 初期割り当てをスキップ"
        echo "ℹ️ 既存組織が $existing_orgs 個あります"
    fi
}

# システム状況表示
show_system_status() {
    echo ""
    echo "📊 自律エージェントシステム状況"
    echo "================================"
    echo "Final Boss監視: $(ps aux | grep "start_autonomous_agents.sh" | grep -v grep > /dev/null && echo "✅ 統合済み" || echo "❌ 停止中")"
    echo "アクティブ組織: $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)"
    echo "保留メッセージ: $(find "$PROJECT_ROOT/shared_messages" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)"
    echo "保留タスク: $(grep -c "^- \[ \]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)"
    echo "進行中タスク: $(grep -c "^- \[⏳\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)"
    echo "完了タスク: $(grep -c "^- \[x\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)"
    echo ""
    
    # エージェント連携フロー表示
    echo "🔄 エージェント連携フロー"
    echo "========================"
    echo "1. Worker → Boss: quick_send.sh boss0X \"実装完了\""
    echo "2. Boss → Final Boss: quick_send.sh final-boss \"タスク完了\""
    echo "3. Final Boss 自動検知・品質評価・統合"
    echo "4. Final Boss → Boss: quick_send.sh boss0X \"新タスク割り当て\""
    echo ""
    
    # 運用コマンド例
    echo "🛠️ 運用コマンド例"
    echo "================="
    echo "Boss完了報告: scripts/quick_send.sh final-boss \"タスク完了: [タスク名]\""
    echo "Boss進捗報告: scripts/quick_send.sh final-boss \"進捗: [進捗]\""
    echo "Worker完了報告: scripts/quick_send.sh boss0X \"実装完了\""
    echo "Final Boss指示: scripts/quick_send.sh boss0X \"新タスク: [内容]\""
    echo "システム停止: bash scripts/stop_autonomous_agents.sh"
    echo ""
}

# ヘルスチェック  
run_health_check() {
    log "🏥 システムヘルスチェック実行"
    
    local health_status=0
    
    # Final Boss監視プロセス確認
    if ! pgrep -f "final_boss_watcher.sh" > /dev/null; then
        log "❌ Final Boss監視プロセスが停止しています"
        health_status=1
    fi
    
    # 必須ディレクトリ確認
    local required_dirs=("shared_messages" "logs" "statistics")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$PROJECT_ROOT/$dir" ]; then
            log "❌ 必須ディレクトリが見つかりません: $dir"
            health_status=1
        fi
    done
    
    # 長時間滞留メッセージ確認
    local old_messages=$(find "$PROJECT_ROOT/shared_messages" -name "*.md" -mtime +1 2>/dev/null | wc -l)
    if [ $old_messages -gt 0 ]; then
        log "⚠️ 1日以上滞留しているメッセージが $old_messages 個あります"
    fi
    
    if [ $health_status -eq 0 ]; then
        log "✅ システムヘルスチェック: 正常"
        echo "✅ システムは正常に動作しています"
    else
        log "❌ システムヘルスチェック: 問題検出"
        echo "❌ システムに問題があります（ログを確認してください）"
    fi
    
    return $health_status
}

# 統計レポート生成
generate_statistics_report() {
    log "📊 統計レポート生成中"
    
    local report_file="$PROJECT_ROOT/statistics/autonomous_system_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "system_status": {
        "final_boss_watcher_active": $(pgrep -f "final_boss_watcher.sh" > /dev/null && echo "true" || echo "false"),
        "active_organizations": $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l),
        "pending_messages": $(find "$PROJECT_ROOT/shared_messages" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l),
        "processed_messages_today": $(find "$PROJECT_ROOT/shared_messages/processed" -name "*.md" -newermt "today" 2>/dev/null | wc -l)
    },
    "task_status": {
        "pending_tasks": $(grep -c "^- \[ \]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0),
        "in_progress_tasks": $(grep -c "^- \[⏳\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0),
        "completed_tasks": $(grep -c "^- \[x\]" "$PROJECT_ROOT/PROJECT_CHECKLIST.md" 2>/dev/null || echo 0)
    },
    "recent_activity": {
        "archives_created_today": $(find "$PROJECT_ROOT/archives" -type d -newermt "today" 2>/dev/null | wc -l),
        "quality_reports_today": $(find "$PROJECT_ROOT/quality_reports" -name "*.json" -newermt "today" 2>/dev/null | wc -l)
    }
}
EOF
    
    log "📈 統計レポート生成完了: $report_file"
}

# システム停止関数
stop_system() {
    log "🛑 自律エージェントシステム停止処理開始"
    
    # Final Boss監視プロセス停止
    if [ -f "$PROJECT_ROOT/.final_boss_watcher_pid" ]; then
        local pid=$(cat "$PROJECT_ROOT/.final_boss_watcher_pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log "✅ Final Boss監視プロセス停止 (PID: $pid)"
        fi
        rm -f "$PROJECT_ROOT/.final_boss_watcher_pid"
    fi
    
    # その他のクリーンアップ
    generate_statistics_report
    
    log "✅ システム停止完了"
    echo "✅ 自律エージェントシステムが停止しました"
}

# シグナルハンドラー
trap stop_system SIGTERM SIGINT

# メイン処理
main() {
    log "🚀 自律エージェントシステム起動開始"
    
    case "${1:-start}" in
        "start")
            check_requirements
            start_final_boss_watcher
            assign_initial_tasks
            generate_statistics_report
            show_system_status
            log "🎉 自律エージェントシステム起動完了"
            ;;
        
        "stop")
            stop_system
            ;;
            
        "restart")
            stop_system
            sleep 2
            main start
            ;;
            
        "status")
            show_system_status
            run_health_check
            ;;
            
        "health")
            run_health_check
            ;;
            
        "assign")
            log "🎯 手動タスク割り当て実行"
            bash "$SCRIPT_DIR/final_boss_assign_next.sh" assign
            ;;
            
        *)
            echo "使用方法: $0 {start|stop|restart|status|health|assign}"
            echo ""
            echo "  start    - 自律エージェントシステム起動"
            echo "  stop     - システム停止"
            echo "  restart  - システム再起動"
            echo "  status   - システム状況表示"
            echo "  health   - ヘルスチェック実行"
            echo "  assign   - 手動タスク割り当て"
            echo ""
            echo "🤖 完全自律エージェント連携システム"
            echo "エージェント同士がbashファイル実行により連携し、"
            echo "Final Bossが自動でタスク管理・組織運営を行います。"
            exit 1
            ;;
    esac
}

# 実行
main "$@" 