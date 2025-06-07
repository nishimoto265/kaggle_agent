#!/bin/bash

# 📡 エージェント間自動通信システム
# Boss/Worker間の指示送信・受信・処理

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SHARED_MESSAGES="$PROJECT_ROOT/shared_messages"

echo "📡 エージェント間自動通信システム - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
COMM_LOG="$LOG_DIR/communication_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$COMM_LOG"
}

# メッセージディレクトリ初期化
init_message_system() {
    log "📋 メッセージシステムを初期化中..."
    
    mkdir -p "$SHARED_MESSAGES"/{inbox,outbox,processed,archive}
    mkdir -p "$SHARED_MESSAGES"/{to_boss,from_boss,to_worker,from_worker}
    
    log "✅ メッセージシステム初期化完了"
}

# Final Boss -> Boss メッセージ送信
send_message_to_boss() {
    local org_name=$1
    local message_type=$2
    local content="$3"
    
    log "📤 Bossにメッセージ送信: $org_name ($message_type)"
    
    local timestamp=$(date -Iseconds)
    local message_file="$SHARED_MESSAGES/to_boss_${org_name}_${message_type}_${timestamp}.md"
    
    cat > "$message_file" << EOF
# 📋 Final Boss からの指示

## メッセージ情報
- **送信者**: Final Boss
- **宛先**: Boss ($org_name)
- **種類**: $message_type
- **送信時刻**: $timestamp
- **優先度**: 高

## 内容
$content

## 対応要求
1. この指示を確認したら確認報告を送信
2. 指示内容を実行
3. 実行結果を報告
4. 問題があれば速やかに報告

## 報告先
\`shared_messages/from_boss_${org_name}_response_${message_type}.md\`

---
*このメッセージは自動生成されました*
EOF

    log "✅ Bossメッセージ送信完了: $message_file"
    echo "$message_file"
}

# Boss -> Final Boss メッセージ受信処理
process_boss_messages() {
    log "📥 Bossメッセージを処理中..."
    
    local processed_count=0
    
    for message_file in "$SHARED_MESSAGES"/from_boss_*.md; do
        if [ -f "$message_file" ]; then
            local basename_msg=$(basename "$message_file" .md)
            
            # メッセージタイプ判定
            if [[ "$basename_msg" == *"_completed"* ]]; then
                process_completion_report "$message_file"
            elif [[ "$basename_msg" == *"_progress"* ]]; then
                process_progress_report "$message_file"
            elif [[ "$basename_msg" == *"_issue"* ]]; then
                process_issue_report "$message_file"
            elif [[ "$basename_msg" == *"_request"* ]]; then
                process_help_request "$message_file"
            else
                log "⚠️ メッセージタイプが不明: $basename_msg"
            fi
            
            ((processed_count++))
        fi
    done
    
    log "📊 Bossメッセージ処理完了: $processed_count 件"
}

# 完了報告の処理
process_completion_report() {
    local message_file=$1
    local basename_msg=$(basename "$message_file" .md)
    
    log "🎉 完了報告を処理中: $basename_msg"
    
    # 組織名とタスク名を抽出
    local org_name=$(echo "$basename_msg" | grep -o 'org-[0-9][0-9]' || echo "unknown")
    local task_name=$(echo "$basename_msg" | cut -d'_' -f4 || echo "unknown")
    
    # 品質評価をトリガー
    if [ "$org_name" != "unknown" ] && [ "$task_name" != "unknown" ]; then
        log "🔍 品質評価を開始: $org_name/$task_name"
        
        # 品質評価スクリプトを実行
        if python3 scripts/quality_evaluation.py "$org_name" "$task_name"; then
            log "✅ 品質評価完了: $org_name/$task_name"
            
            # 統合スクリプトを実行
            if bash scripts/integrate_to_main.sh "$org_name" "$task_name"; then
                log "✅ 統合処理完了: $org_name/$task_name"
                
                # 成功応答メッセージ
                send_message_to_boss "$org_name" "completion_accepted" "
あなたのタスク完了報告を受理しました。

## 処理結果
- ✅ 品質評価: 合格
- ✅ 統合処理: 完了
- ✅ Final Boss承認: 完了

## 次のアクション
新しいタスクの割り当てを待機してください。
優秀な成果をありがとうございました！"
                
            else
                log "❌ 統合処理失敗: $org_name/$task_name"
                
                # 修正要求メッセージ
                send_message_to_boss "$org_name" "correction_required" "
品質評価は合格しましたが、統合処理で問題が発生しました。

## 修正要求
以下の点を確認して修正してください：
- ファイル構造の確認
- 依存関係の確認  
- テストの実行確認

修正完了後、再度完了報告してください。"
            fi
        else
            log "❌ 品質評価失敗: $org_name/$task_name"
            
            # 再作業要求メッセージ
            send_message_to_boss "$org_name" "rework_required" "
品質評価で基準未達のため、再作業が必要です。

## 品質基準
- テストカバレッジ95%以上
- 静的解析エラー0件
- パフォーマンス基準満足
- ドキュメント完備

詳細は品質レポートを確認してください。"
        fi
    fi
    
    # 処理済みに移動
    mv "$message_file" "$SHARED_MESSAGES/processed/"
    log "📄 完了報告を処理済みに移動"
}

# 進捗報告の処理
process_progress_report() {
    local message_file=$1
    local basename_msg=$(basename "$message_file" .md)
    
    log "📊 進捗報告を処理中: $basename_msg"
    
    # 進捗データを抽出して統計に追加
    local org_name=$(echo "$basename_msg" | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    # 応答メッセージ
    send_message_to_boss "$org_name" "progress_acknowledged" "
進捗報告を確認しました。

## 指示
- 順調に進行しています
- 品質基準を維持してください
- 問題があれば速やかに報告してください

継続して頑張ってください！"
    
    # 処理済みに移動
    mv "$message_file" "$SHARED_MESSAGES/processed/"
    log "📈 進捗報告を処理済みに移動"
}

# 問題報告の処理
process_issue_report() {
    local message_file=$1
    local basename_msg=$(basename "$message_file" .md)
    
    log "🚨 問題報告を処理中: $basename_msg"
    
    local org_name=$(echo "$basename_msg" | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    # 問題の内容を解析（簡易版）
    local issue_content=$(cat "$message_file")
    
    # 適切な対応指示を送信
    send_message_to_boss "$org_name" "issue_resolution" "
問題報告を確認しました。

## 対応指示
1. 詳細な問題分析を実行
2. 可能な解決策を検討
3. 必要に応じてWorker再配置を検討
4. 進捗への影響を最小化

## 支援可能な内容
- 技術的なアドバイス
- 追加リソースの提供
- タスクの再分割

解決策が見つからない場合は、詳細情報と共に再度報告してください。"
    
    # 処理済みに移動
    mv "$message_file" "$SHARED_MESSAGES/processed/"
    log "🔧 問題報告を処理済みに移動"
}

# 支援要求の処理
process_help_request() {
    local message_file=$1
    local basename_msg=$(basename "$message_file" .md)
    
    log "🤝 支援要求を処理中: $basename_msg"
    
    local org_name=$(echo "$basename_msg" | grep -o 'org-[0-9][0-9]' || echo "unknown")
    
    # 支援応答
    send_message_to_boss "$org_name" "support_response" "
支援要求を確認しました。

## 提供可能な支援
1. 技術的なガイダンス
2. リソースの追加割り当て
3. 他組織との連携調整
4. タスクの優先度調整

## 次のステップ
具体的な支援内容を明確にして再度要求してください。
可能な限り迅速に対応します。"
    
    # 処理済みに移動
    mv "$message_file" "$SHARED_MESSAGES/processed/"
    log "🆘 支援要求を処理済みに移動"
}

# Worker -> Boss メッセージ中継
relay_worker_messages() {
    log "🔄 Workerメッセージを中継中..."
    
    for message_file in "$SHARED_MESSAGES"/from_worker_*.md; do
        if [ -f "$message_file" ]; then
            local basename_msg=$(basename "$message_file" .md)
            local org_name=$(echo "$basename_msg" | grep -o 'org-[0-9][0-9]' || echo "unknown")
            
            if [ "$org_name" != "unknown" ]; then
                # Boss宛に中継
                local relay_file="$SHARED_MESSAGES/to_boss_${org_name}_worker_relay_$(date +%s).md"
                
                cat > "$relay_file" << EOF
# 🔄 Worker メッセージ中継

## 元のメッセージ
$(cat "$message_file")

## 中継情報
- 中継者: Final Boss Auto Relay
- 中継時刻: $(date)
- 元ファイル: $basename_msg

## Boss への指示
このWorkerメッセージを確認し、適切に対応してください。
EOF
                
                log "🔄 Workerメッセージを中継: $basename_msg -> $org_name"
                
                # 元メッセージを処理済みに移動
                mv "$message_file" "$SHARED_MESSAGES/processed/"
            fi
        fi
    done
}

# 自動応答システム
auto_response_system() {
    log "🤖 自動応答システムを実行中..."
    
    # 長時間応答がないBossをチェック
    for org_dir in "$PROJECT_ROOT"/orgs/org-*/; do
        if [ -d "$org_dir" ]; then
            local org_name=$(basename "$org_dir")
            
            # 最後の応答時刻をチェック
            local last_response=$(find "$SHARED_MESSAGES" -name "from_boss_${org_name}_*" -newermt "1 hour ago" | wc -l)
            
            if [ "$last_response" -eq 0 ]; then
                # 1時間以上応答がない場合は状況確認
                send_message_to_boss "$org_name" "status_check" "
1時間以上応答がありません。現在の状況を確認してください。

## 確認事項
- 現在の作業状況
- Worker の進捗状況
- 発生している問題
- 支援が必要な事項

30分以内に応答してください。"
                
                log "⏰ 無応答チェック: $org_name に状況確認を送信"
            fi
        fi
    done
}

# メッセージクリーンアップ
cleanup_old_messages() {
    log "🧹 古いメッセージをクリーンアップ中..."
    
    # 7日以上前の処理済みメッセージをアーカイブ
    find "$SHARED_MESSAGES/processed" -name "*.md" -mtime +7 -exec mv {} "$SHARED_MESSAGES/archive/" \; 2>/dev/null || true
    
    # 30日以上前のアーカイブを削除
    find "$SHARED_MESSAGES/archive" -name "*.md" -mtime +30 -delete 2>/dev/null || true
    
    log "✅ メッセージクリーンアップ完了"
}

# 通信統計の生成
generate_communication_stats() {
    log "📊 通信統計を生成中..."
    
    local stats_file="$PROJECT_ROOT/statistics/communication_$(date +%Y%m%d).json"
    mkdir -p "$PROJECT_ROOT/statistics"
    
    local total_messages=$(find "$SHARED_MESSAGES" -name "*.md" | wc -l)
    local processed_messages=$(find "$SHARED_MESSAGES/processed" -name "*.md" | wc -l)
    local pending_messages=$(find "$SHARED_MESSAGES" -maxdepth 1 -name "*.md" | wc -l)
    
    cat > "$stats_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "communication_stats": {
        "total_messages": $total_messages,
        "processed_messages": $processed_messages,
        "pending_messages": $pending_messages,
        "active_organizations": $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)
    },
    "message_types": {
        "completion_reports": $(find "$SHARED_MESSAGES" -name "*completed*.md" | wc -l),
        "progress_reports": $(find "$SHARED_MESSAGES" -name "*progress*.md" | wc -l),
        "issue_reports": $(find "$SHARED_MESSAGES" -name "*issue*.md" | wc -l),
        "help_requests": $(find "$SHARED_MESSAGES" -name "*request*.md" | wc -l)
    }
}
EOF
    
    log "📈 通信統計生成完了: $stats_file"
}

# メイン処理
main() {
    log "🚀 エージェント間通信システム開始"
    
    # システム初期化
    init_message_system
    
    # Bossメッセージ処理
    process_boss_messages
    
    # Workerメッセージ中継
    relay_worker_messages
    
    # 自動応答システム
    auto_response_system
    
    # 古いメッセージクリーンアップ
    cleanup_old_messages
    
    # 統計生成
    generate_communication_stats
    
    log "✅ エージェント間通信システム完了"
    
    # サマリー表示
    echo ""
    echo "📊 通信サマリー"
    echo "================"
    echo "保留メッセージ: $(find "$SHARED_MESSAGES" -maxdepth 1 -name "*.md" | wc -l)"
    echo "処理済メッセージ: $(find "$SHARED_MESSAGES/processed" -name "*.md" | wc -l)"
    echo "アクティブ組織: $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)"
    echo "ログファイル: $COMM_LOG"
}

# 使用方法
show_usage() {
    echo "使用方法: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  process     メッセージ処理を実行"
    echo "  status      システム状況を表示"
    echo "  cleanup     古いメッセージをクリーンアップ"
    echo "  help        この使用方法を表示"
    echo ""
}

# 引数処理
case "${1:-process}" in
    "process")
        main
        ;;
    "status")
        echo "📊 通信システム状況"
        echo "=================="
        echo "保留メッセージ: $(find "$SHARED_MESSAGES" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)"
        echo "処理済メッセージ: $(find "$SHARED_MESSAGES/processed" -name "*.md" 2>/dev/null | wc -l)"
        echo "アクティブ組織: $(ls -1d "$PROJECT_ROOT"/orgs/org-*/ 2>/dev/null | wc -l)"
        ;;
    "cleanup")
        init_message_system
        cleanup_old_messages
        ;;
    "help")
        show_usage
        ;;
    *)
        echo "❌ 不明なコマンド: $1"
        show_usage
        exit 1
        ;;
esac 