#!/bin/bash

# 👁️ Final Boss ファイル監視・自動起動システム
# Boss からのメッセージを監視し、自動でFinal Boss処理を実行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SHARED_MESSAGES="$PROJECT_ROOT/shared_messages"

echo "👁️ Final Boss ファイル監視システム起動 - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
WATCHER_LOG="$LOG_DIR/final_boss_watcher_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$WATCHER_LOG"
}

# 必要なディレクトリ作成
init_directories() {
    mkdir -p "$SHARED_MESSAGES"/{processed,archive}
    mkdir -p "$PROJECT_ROOT"/{archives,statistics,quality_reports}
    log "📁 ディレクトリ初期化完了"
}

# メッセージ処理
process_message() {
    local message_file="$1"
    local message_basename=$(basename "$message_file" .md)
    
    log "📨 メッセージ処理開始: $message_basename"
    
    # メッセージタイプ判定
    if [[ "$message_basename" == *"_completed_"* ]]; then
        process_completion_message "$message_file"
    elif [[ "$message_basename" == *"_progress_"* ]]; then
        process_progress_message "$message_file"
    elif [[ "$message_basename" == *"_issue_"* ]]; then
        process_issue_message "$message_file"
    elif [[ "$message_basename" == *"_request_"* ]]; then
        process_request_message "$message_file"
    else
        log "ℹ️ 通常メッセージとして処理: $message_basename"
        send_acknowledgment "$message_file"
    fi
    
    # 処理済みに移動
    mv "$message_file" "$SHARED_MESSAGES/processed/"
    log "✅ メッセージ処理完了: $message_basename"
}

# 完了報告の処理
process_completion_message() {
    local message_file="$1"
    local message_basename=$(basename "$message_file" .md)
    
    log "🎉 完了報告を処理中: $message_basename"
    
    # 組織名とタスク名を抽出
    local org_name=$(echo "$message_basename" | grep -o 'org-[0-9][0-9]' || echo "unknown")
    local task_name=$(grep "タスク名" "$message_file" | sed 's/.*: *//' | head -1 || echo "unknown")
    
    if [ "$org_name" != "unknown" ]; then
        log "🔍 品質評価を開始: $org_name"
        
        # 品質評価実行
        cd "$PROJECT_ROOT"
        if python3 scripts/quality_evaluation.py "$org_name" "$task_name" 2>&1 | tee -a "$WATCHER_LOG"; then
            log "✅ 品質評価完了: $org_name"
            
            # 統合実行
            if bash scripts/integrate_to_main.sh "$org_name" "$task_name" 2>&1 | tee -a "$WATCHER_LOG"; then
                log "✅ 統合完了: $org_name"
                
                # 組織削除とクリーンアップ実行
                bash scripts/final_boss_cleanup.sh "$org_name" "$task_name"
                
                # 新しいタスク割り当て実行
                bash scripts/final_boss_assign_next.sh
                
                # 成功通知送信
                send_success_notification "$org_name" "$task_name"
                
            else
                log "❌ 統合失敗: $org_name"
                send_correction_request "$org_name" "$task_name"
            fi
        else
            log "❌ 品質評価失敗: $org_name"
            send_rework_request "$org_name" "$task_name"
        fi
    else
        log "⚠️ 組織名が特定できません: $message_basename"
    fi
}

# 進捗報告の処理
process_progress_message() {
    local message_file="$1"
    local org_name=$(basename "$message_file" .md | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    log "📊 進捗報告確認: $org_name"
    send_progress_acknowledgment "$org_name"
}

# 問題報告の処理  
process_issue_message() {
    local message_file="$1"
    local org_name=$(basename "$message_file" .md | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    log "🚨 問題報告対応: $org_name"
    send_issue_support "$org_name"
}

# 支援要求の処理
process_request_message() {
    local message_file="$1"
    local org_name=$(basename "$message_file" .md | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    log "🤝 支援要求対応: $org_name"
    send_support_response "$org_name"
}

# 成功通知送信
send_success_notification() {
    local org_name="$1"
    local task_name="$2"
    
    cat > "$SHARED_MESSAGES/to_boss_${org_name}_success_$(date +%s).md" << EOF
# ✅ タスク完了承認通知

## 処理結果
- **組織**: $org_name
- **タスク**: $task_name
- **処理時刻**: $(date)
- **結果**: 成功

## 実行された処理
1. ✅ 品質評価: 合格
2. ✅ 統合処理: 完了
3. ✅ 組織クリーンアップ: 完了
4. ✅ 次タスク準備: 完了

## 次のアクション
新しいタスクの割り当てを準備中です。
優秀な成果をありがとうございました！

---
**Final Boss - 自動処理システム**
EOF
    
    log "📤 成功通知送信: $org_name"
}

# 修正要求送信
send_correction_request() {
    local org_name="$1"
    local task_name="$2"
    
    cat > "$SHARED_MESSAGES/to_boss_${org_name}_correction_$(date +%s).md" << EOF
# 🔧 修正要求通知

## 処理結果
- **組織**: $org_name
- **タスク**: $task_name
- **結果**: 修正が必要

## 問題点
品質評価は合格しましたが、統合処理で問題が発生しました。

## 修正要求事項
1. ファイル構造の確認
2. 依存関係の確認
3. テストの実行確認
4. ドキュメントの補完

修正完了後、再度完了報告してください。

---
**Final Boss - 自動処理システム**
EOF
    
    log "📤 修正要求送信: $org_name"
}

# 再作業要求送信
send_rework_request() {
    local org_name="$1"
    local task_name="$2"
    
    cat > "$SHARED_MESSAGES/to_boss_${org_name}_rework_$(date +%s).md" << EOF
# 🔄 再作業要求通知

## 処理結果
- **組織**: $org_name
- **タスク**: $task_name
- **結果**: 品質基準未達

## 品質基準
- テストカバレッジ95%以上
- 静的解析エラー0件
- パフォーマンス基準満足
- ドキュメント完備

詳細は品質レポートを確認してください。
再作業完了後、再度完了報告してください。

---
**Final Boss - 自動処理システム**
EOF
    
    log "📤 再作業要求送信: $org_name"
}

# 進捗確認応答
send_progress_acknowledgment() {
    local org_name="$1"
    
    cat > "$SHARED_MESSAGES/to_boss_${org_name}_ack_$(date +%s).md" << EOF
# 📊 進捗確認済み

進捗報告を確認しました。

## 指示
- 順調に進行しています
- 品質基準を維持してください
- 問題があれば即座に報告してください

継続して頑張ってください！

---
**Final Boss - 自動応答**
EOF
    
    log "📤 進捗確認応答: $org_name"
}

# 問題対応支援
send_issue_support() {
    local org_name="$1"
    
    cat > "$SHARED_MESSAGES/to_boss_${org_name}_support_$(date +%s).md" << EOF
# 🚨 問題対応支援

問題報告を確認しました。

## 対応指示
1. 詳細な問題分析を実行
2. 可能な解決策を検討
3. 必要に応じてWorker再配置
4. 進捗への影響を最小化

## 利用可能な支援
- 技術的アドバイス
- 追加リソース提供
- タスク再分割

解決しない場合は詳細と共に再報告してください。

---
**Final Boss - 自動対応**
EOF
    
    log "📤 問題対応支援: $org_name"
}

# 支援応答
send_support_response() {
    local org_name="$1"
    
    cat > "$SHARED_MESSAGES/to_boss_${org_name}_help_$(date +%s).md" << EOF
# 🤝 支援応答

支援要求を確認しました。

## 提供可能な支援
1. 技術的ガイダンス
2. リソース追加割り当て
3. 他組織との連携調整
4. タスク優先度調整

具体的な支援内容を明確にして再度要求してください。

---
**Final Boss - 自動応答**
EOF
    
    log "📤 支援応答: $org_name"
}

# 通常確認応答
send_acknowledgment() {
    local message_file="$1"
    local org_name=$(basename "$message_file" .md | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    if [ "$org_name" != "unknown" ]; then
        cat > "$SHARED_MESSAGES/to_boss_${org_name}_ack_$(date +%s).md" << EOF
# 📋 メッセージ確認

メッセージを確認しました。

---
**Final Boss - 自動確認**
EOF
        log "📤 確認応答: $org_name"
    fi
}

# ファイル監視メインループ
watch_messages() {
    log "👁️ メッセージ監視開始..."
    
    # inotify が利用可能か確認
    if command -v inotifywait >/dev/null 2>&1; then
        log "📡 inotify監視モードで開始"
        
        # inotifyでファイル作成を監視
        inotifywait -m -e create -e moved_to --format '%w%f' "$SHARED_MESSAGES" 2>/dev/null | while read new_file; do
            if [[ "$new_file" == *.md ]] && [[ "$(basename "$new_file")" == from_boss_* ]]; then
                log "🔔 新しいメッセージ検出: $(basename "$new_file")"
                sleep 1  # ファイル書き込み完了を待機
                process_message "$new_file"
            fi
        done
    else
        log "📡 ポーリング監視モードで開始（inotify-tools未インストール）"
        
        # ポーリングでファイルを監視
        while true; do
            for message_file in "$SHARED_MESSAGES"/from_boss_*.md; do
                if [ -f "$message_file" ]; then
                    log "🔔 新しいメッセージ検出: $(basename "$message_file")"
                    process_message "$message_file"
                fi
            done
            sleep 5  # 5秒間隔でチェック
        done
    fi
}

# 統計更新
update_statistics() {
    local stats_file="$PROJECT_ROOT/statistics/final_boss_activity_$(date +%Y%m%d).json"
    
    cat > "$stats_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "watcher_status": "active",
    "processed_messages_today": $(find "$SHARED_MESSAGES/processed" -name "*.md" -newermt "today" | wc -l),
    "pending_messages": $(find "$SHARED_MESSAGES" -maxdepth 1 -name "from_boss_*.md" | wc -l),
    "active_organizations": $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)
}
EOF
    
    log "📊 統計更新完了"
}

# シグナルハンドラー
cleanup_and_exit() {
    log "🛑 Final Boss監視システムを停止中..."
    update_statistics
    log "✅ Final Boss監視システム正常終了"
    exit 0
}

trap cleanup_and_exit SIGTERM SIGINT

# メイン処理
main() {
    log "🚀 Final Boss ファイル監視システム開始"
    
    # 初期化
    init_directories
    
    # 既存のメッセージがあれば処理
    for message_file in "$SHARED_MESSAGES"/from_boss_*.md; do
        if [ -f "$message_file" ]; then
            log "📥 既存メッセージを処理: $(basename "$message_file")"
            process_message "$message_file"
        fi
    done
    
    # 統計更新
    update_statistics
    
    # ファイル監視開始
    watch_messages
}

# 引数チェック
case "${1:-watch}" in
    "watch")
        main
        ;;
    "process-once")
        log "🎯 一回処理モード"
        init_directories
        for message_file in "$SHARED_MESSAGES"/from_boss_*.md; do
            if [ -f "$message_file" ]; then
                process_message "$message_file"
            fi
        done
        update_statistics
        ;;
    "status")
        echo "📊 Final Boss 監視システム状況"
        echo "================================"
        echo "保留メッセージ: $(find "$SHARED_MESSAGES" -maxdepth 1 -name "from_boss_*.md" 2>/dev/null | wc -l)"
        echo "処理済みメッセージ: $(find "$SHARED_MESSAGES/processed" -name "*.md" 2>/dev/null | wc -l)"
        echo "アクティブ組織: $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)"
        ;;
    *)
        echo "使用方法: $0 {watch|process-once|status}"
        exit 1
        ;;
esac 