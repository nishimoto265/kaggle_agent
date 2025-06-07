#!/bin/bash

# 🕒 Final Boss 自動スケジューラー
# 定期的に自律組織管理を実行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🕒 Final Boss 自動スケジューラー起動 - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
SCHEDULER_LOG="$LOG_DIR/scheduler_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$SCHEDULER_LOG"
}

# 設定
CHECK_INTERVAL=300  # 5分間隔で実行
MAX_ITERATIONS=288  # 24時間分 (5分×288 = 24時間)

# 自律組織管理の実行
run_autonomous_management() {
    log "🤖 自律組織管理を実行中..."
    
    cd "$PROJECT_ROOT"
    if bash scripts/autonomous_org_manager.sh; then
        log "✅ 自律組織管理完了"
        return 0
    else
        log "❌ 自律組織管理でエラーが発生"
        return 1
    fi
}

# 日次運用の実行
run_daily_operations() {
    local operation_type=$1
    log "📅 日次運用を実行中: $operation_type"
    
    cd "$PROJECT_ROOT"
    if bash scripts/daily_operations.sh "$operation_type"; then
        log "✅ 日次運用完了: $operation_type"
        return 0
    else
        log "❌ 日次運用でエラーが発生: $operation_type"
        return 1
    fi
}

# 時刻に基づく日次運用チェック
check_daily_operations() {
    local current_hour=$(date +%H)
    local current_minute=$(date +%M)
    
    # 09:00 朝の確認
    if [ "$current_hour" = "09" ] && [ "$current_minute" -lt "05" ]; then
        if [ ! -f "$LOG_DIR/morning_$(date +%Y%m%d).done" ]; then
            log "🌅 朝の日次運用を実行"
            if run_daily_operations "morning"; then
                touch "$LOG_DIR/morning_$(date +%Y%m%d).done"
            fi
        fi
    fi
    
    # 13:00 昼の確認
    if [ "$current_hour" = "13" ] && [ "$current_minute" -lt "05" ]; then
        if [ ! -f "$LOG_DIR/noon_$(date +%Y%m%d).done" ]; then
            log "🌞 昼の日次運用を実行"
            if run_daily_operations "noon"; then
                touch "$LOG_DIR/noon_$(date +%Y%m%d).done"
            fi
        fi
    fi
    
    # 17:00 夕方の確認
    if [ "$current_hour" = "17" ] && [ "$current_minute" -lt "05" ]; then
        if [ ! -f "$LOG_DIR/evening_$(date +%Y%m%d).done" ]; then
            log "🌅 夕方の日次運用を実行"
            if run_daily_operations "evening"; then
                touch "$LOG_DIR/evening_$(date +%Y%m%d).done"
            fi
        fi
    fi
    
    # 金曜日の18:00 週次確認
    if [ "$(date +%u)" = "5" ] && [ "$current_hour" = "18" ] && [ "$current_minute" -lt "05" ]; then
        if [ ! -f "$LOG_DIR/weekly_$(date +%Y%m%d).done" ]; then
            log "📊 週次運用を実行"
            if run_daily_operations "weekly"; then
                touch "$LOG_DIR/weekly_$(date +%Y%m%d).done"
            fi
        fi
    fi
}

# 緊急停止条件の確認
check_emergency_stop() {
    # 緊急停止ファイルの確認
    if [ -f "$PROJECT_ROOT/EMERGENCY_STOP" ]; then
        log "🚨 緊急停止ファイルを検出。スケジューラーを停止します。"
        exit 0
    fi
    
    # ディスク容量確認 (90%以上で停止)
    disk_usage=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log "🚨 ディスク容量不足 (${disk_usage}%)。スケジューラーを停止します。"
        exit 1
    fi
    
    # メモリ使用量確認 (95%以上で一時停止)
    mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$mem_usage" -gt 95 ]; then
        log "⚠️ メモリ使用量が高い (${mem_usage}%)。しばらく待機します。"
        sleep 60
        return 1
    fi
    
    return 0
}

# ヘルスチェック
health_check() {
    local errors=0
    
    # 必要なディレクトリの確認
    for dir in "orgs" "scripts" "tasks" "shared_messages"; do
        if [ ! -d "$PROJECT_ROOT/$dir" ]; then
            log "❌ 必要なディレクトリが見つかりません: $dir"
            ((errors++))
        fi
    done
    
    # 必要なスクリプトの確認
    for script in "autonomous_org_manager.sh" "daily_operations.sh" "create_task_unit.sh" "assign_task_to_boss.sh"; do
        if [ ! -f "$PROJECT_ROOT/scripts/$script" ]; then
            log "❌ 必要なスクリプトが見つかりません: $script"
            ((errors++))
        fi
    done
    
    # PROJECT_CHECKLIST.mdの確認
    if [ ! -f "$PROJECT_ROOT/PROJECT_CHECKLIST.md" ]; then
        log "❌ PROJECT_CHECKLIST.md が見つかりません"
        ((errors++))
    fi
    
    if [ $errors -gt 0 ]; then
        log "🚨 ヘルスチェックで $errors 個のエラーを発見。修復が必要です。"
        return 1
    else
        log "✅ ヘルスチェック完了"
        return 0
    fi
}

# メインループ
main_loop() {
    local iteration=0
    
    log "🚀 スケジューラーメインループ開始"
    log "📊 設定: チェック間隔=${CHECK_INTERVAL}秒, 最大実行回数=${MAX_ITERATIONS}"
    
    while [ $iteration -lt $MAX_ITERATIONS ]; do
        iteration=$((iteration + 1))
        log "🔄 実行回数: $iteration/$MAX_ITERATIONS"
        
        # 緊急停止確認
        if ! check_emergency_stop; then
            continue
        fi
        
        # ヘルスチェック (1時間に1回)
        if [ $((iteration % 12)) -eq 0 ]; then
            if ! health_check; then
                log "⚠️ ヘルスチェック失敗。次回に延期します。"
                sleep $CHECK_INTERVAL
                continue
            fi
        fi
        
        # 日次運用チェック
        check_daily_operations
        
        # 自律組織管理実行
        run_autonomous_management
        
        # 次の実行まで待機
        log "⏳ 次回実行まで ${CHECK_INTERVAL} 秒待機..."
        sleep $CHECK_INTERVAL
    done
    
    log "🏁 スケジューラー完了: $MAX_ITERATIONS 回実行"
}

# シグナルハンドラー
cleanup_and_exit() {
    log "🛑 スケジューラーが停止要求を受信しました"
    log "📊 最終統計を記録中..."
    
    # 最終統計記録
    cat >> "$SCHEDULER_LOG" << EOF

📊 最終実行サマリー
==================
停止時刻: $(date)
ログファイル: $SCHEDULER_LOG
実行モード: continuous_scheduler
EOF
    
    log "✅ スケジューラー正常終了"
    exit 0
}

# シグナルハンドラー設定
trap cleanup_and_exit SIGTERM SIGINT

# 使用方法
show_usage() {
    echo "使用方法: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --daemon    バックグラウンドで実行"
    echo "  --once      一回だけ実行"
    echo "  --test      テストモード (5回だけ実行)"
    echo "  --help      この使用方法を表示"
    echo ""
    echo "例:"
    echo "  $0                # フォアグラウンドで24時間実行"
    echo "  $0 --daemon       # バックグラウンドで24時間実行"
    echo "  $0 --once         # 一回だけ実行"
    echo "  $0 --test         # テストモード"
    echo ""
}

# 引数処理
case "${1:-}" in
    "--daemon")
        log "🔄 バックグラウンドモードで開始"
        nohup "$0" > "$LOG_DIR/scheduler_daemon_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
        echo "PID: $!" > "$LOG_DIR/scheduler.pid"
        echo "🚀 バックグラウンドでスケジューラーを開始しました"
        echo "📄 ログ: $LOG_DIR/scheduler_daemon_$(date +%Y%m%d_%H%M%S).log"
        echo "📋 PID: $(cat "$LOG_DIR/scheduler.pid")"
        echo "🛑 停止方法: kill $(cat "$LOG_DIR/scheduler.pid")"
        exit 0
        ;;
    "--once")
        log "🎯 一回実行モード"
        check_daily_operations
        run_autonomous_management
        log "✅ 一回実行完了"
        exit 0
        ;;
    "--test")
        log "🧪 テストモード (5回実行)"
        MAX_ITERATIONS=5
        CHECK_INTERVAL=10
        main_loop
        exit 0
        ;;
    "--help")
        show_usage
        exit 0
        ;;
    "")
        log "📅 通常モード (24時間実行)"
        main_loop
        ;;
    *)
        echo "❌ 不明なオプション: $1"
        show_usage
        exit 1
        ;;
esac 