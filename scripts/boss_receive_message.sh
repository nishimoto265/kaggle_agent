#!/bin/bash

# 📨 Boss メッセージ受信・処理システム
# Final Boss からのメッセージを受信し、適切に処理

set -e

# 現在のディレクトリから組織名を自動検出
CURRENT_DIR=$(pwd)
ORG_NAME=$(echo "$CURRENT_DIR" | grep -o 'org-[0-9][0-9]' | head -1)

if [ -z "$ORG_NAME" ]; then
    echo "❌ 組織ディレクトリ内で実行してください (orgs/org-XX/)"
    exit 1
fi

# プロジェクトルートを検出
PROJECT_ROOT=""
temp_dir="$CURRENT_DIR"
while [ "$temp_dir" != "/" ]; do
    if [ -f "$temp_dir/PROJECT_CHECKLIST.md" ]; then
        PROJECT_ROOT="$temp_dir"
        break
    fi
    temp_dir=$(dirname "$temp_dir")
done

if [ -z "$PROJECT_ROOT" ]; then
    echo "❌ プロジェクトルートが見つかりません"
    exit 1
fi

SHARED_MESSAGES="$PROJECT_ROOT/shared_messages"

echo "📨 Boss ($ORG_NAME) メッセージ受信・処理システム - $(date)"
echo "================================================================"

# ログ設定
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
RECEIVE_LOG="$LOG_DIR/boss_${ORG_NAME}_receive_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$RECEIVE_LOG"
}

# 受信メッセージを確認
check_messages() {
    log "📬 Boss ($ORG_NAME) へのメッセージを確認中..."
    
    # メッセージファイルのパターン
    local message_files=("$SHARED_MESSAGES/to_boss_${ORG_NAME}_"*.md)
    local message_count=0
    
    for message_file in "${message_files[@]}"; do
        if [ -f "$message_file" ]; then
            message_count=$((message_count + 1))
            log "📋 メッセージ発見: $(basename "$message_file")"
            process_message "$message_file"
        fi
    done
    
    if [ $message_count -eq 0 ]; then
        log "📭 新しいメッセージはありません"
        echo "📭 現在、新しいメッセージはありません"
    else
        log "✅ $message_count 個のメッセージを処理しました"
        echo "✅ $message_count 個のメッセージを処理完了"
    fi
}

# メッセージ処理
process_message() {
    local message_file="$1"
    local message_basename=$(basename "$message_file" .md)
    
    log "📖 メッセージ読み込み: $message_basename"
    
    # メッセージタイプを判定
    if [[ "$message_basename" == *"_new_task_"* ]]; then
        process_new_task_message "$message_file"
    elif [[ "$message_basename" == *"_success_"* ]]; then
        process_success_message "$message_file"
    elif [[ "$message_basename" == *"_correction_"* ]]; then
        process_correction_message "$message_file"
    elif [[ "$message_basename" == *"_rework_"* ]]; then
        process_rework_message "$message_file"
    elif [[ "$message_basename" == *"_ack_"* ]]; then
        process_acknowledgment_message "$message_file"
    elif [[ "$message_basename" == *"_support_"* ]]; then
        process_support_message "$message_file"
    elif [[ "$message_basename" == *"_help_"* ]]; then
        process_help_message "$message_file"
    else
        process_general_message "$message_file"
    fi
    
    # 処理済みに移動
    local processed_dir="$SHARED_MESSAGES/processed"
    mkdir -p "$processed_dir"
    mv "$message_file" "$processed_dir/"
    log "📦 メッセージを処理済みに移動: $message_basename"
}

# 新しいタスク割り当てメッセージの処理
process_new_task_message() {
    local message_file="$1"
    
    log "🎯 新しいタスク割り当てを処理中"
    
    # タスク名を抽出
    local task_name=$(grep "タスク名" "$message_file" | sed 's/.*: *//' | head -1)
    
    echo ""
    echo "🎯 新しいタスクが割り当てられました！"
    echo "============================================"
    echo "タスク名: $task_name"
    echo "組織: $ORG_NAME"
    echo "割り当て日時: $(date)"
    echo ""
    
    # メッセージ内容を表示
    echo "📋 詳細なタスク指示:"
    echo "==================="
    cat "$message_file"
    echo ""
    
    # タスクディレクトリの確認
    if [ -d "$PROJECT_ROOT/tasks" ]; then
        echo "📁 利用可能なタスクファイル:"
        ls -la "$PROJECT_ROOT/tasks" | grep "$task_name" || echo "タスクファイルを確認中..."
    fi
    
    # Boss作業開始の指示
    echo "🚀 作業開始指示"
    echo "==============="
    echo "1. Worker-A, Worker-B, Worker-C に作業分担を指示"
    echo "2. 各Workerのチェックリストを定期確認"
    echo "3. 24時間毎に進捗報告を実行"
    echo "4. 完了時にFinal Bossに報告"
    echo ""
    
    # 自動応答を送信
    send_task_received_confirmation "$task_name"
    
    log "✅ 新しいタスク割り当て処理完了: $task_name"
}

# 成功通知メッセージの処理
process_success_message() {
    local message_file="$1"
    
    log "🎉 成功通知を処理中"
    
    echo ""
    echo "🎉 タスク完了が承認されました！"
    echo "================================"
    cat "$message_file"
    echo ""
    echo "✅ 組織 $ORG_NAME の作業が正常に完了し、統合されました"
    echo "🏆 優秀な成果をありがとうございました！"
    
    log "✅ 成功通知処理完了"
}

# 修正要求メッセージの処理
process_correction_message() {
    local message_file="$1"
    
    log "🔧 修正要求を処理中"
    
    echo ""
    echo "🔧 修正要求を受信しました"
    echo "========================"
    cat "$message_file"
    echo ""
    echo "⚠️ 修正作業を開始してください"
    echo "📝 修正完了後、再度完了報告を送信してください"
    
    # Worker通知ファイル作成
    create_worker_correction_notice
    
    log "✅ 修正要求処理完了"
}

# 再作業要求メッセージの処理
process_rework_message() {
    local message_file="$1"
    
    log "🔄 再作業要求を処理中"
    
    echo ""
    echo "🔄 再作業要求を受信しました"
    echo "============================"
    cat "$message_file"
    echo ""
    echo "⚠️ 品質基準を満たすために再作業が必要です"
    echo "📊 詳細な品質レポートを確認してください"
    
    # Worker通知ファイル作成
    create_worker_rework_notice
    
    log "✅ 再作業要求処理完了"
}

# 確認応答メッセージの処理
process_acknowledgment_message() {
    local message_file="$1"
    
    log "📋 確認応答を処理中"
    
    echo ""
    echo "📋 Final Boss からの確認応答"
    echo "============================"
    cat "$message_file"
    echo ""
    
    log "✅ 確認応答処理完了"
}

# 支援メッセージの処理
process_support_message() {
    local message_file="$1"
    
    log "🤝 支援メッセージを処理中"
    
    echo ""
    echo "🤝 Final Boss からの支援"
    echo "========================"
    cat "$message_file"
    echo ""
    echo "🙏 支援ありがとうございます"
    
    log "✅ 支援メッセージ処理完了"
}

# ヘルプメッセージの処理
process_help_message() {
    local message_file="$1"
    
    log "🆘 ヘルプメッセージを処理中"
    
    echo ""
    echo "🆘 Final Boss からのヘルプ"
    echo "=========================="
    cat "$message_file"
    echo ""
    
    log "✅ ヘルプメッセージ処理完了"
}

# 一般メッセージの処理
process_general_message() {
    local message_file="$1"
    
    log "📄 一般メッセージを処理中"
    
    echo ""
    echo "📄 Final Boss からのメッセージ"
    echo "============================"
    cat "$message_file"
    echo ""
    
    log "✅ 一般メッセージ処理完了"
}

# タスク受信確認の送信
send_task_received_confirmation() {
    local task_name="$1"
    
    local confirmation_file="$SHARED_MESSAGES/from_boss_${ORG_NAME}_task_received_$(date +%s).md"
    
    cat > "$confirmation_file" << EOF
# 📩 タスク受信確認

## メッセージ情報
- **送信者**: Boss ($ORG_NAME)
- **メッセージタイプ**: タスク受信確認
- **タスク名**: $task_name
- **受信時刻**: $(date -Iseconds)

## 確認事項
✅ タスク割り当てを受信しました
✅ タスク要件を確認中
✅ Worker配置を準備中
✅ 作業計画を策定中

## 次のアクション
1. Worker-A, B, C への作業分担指示
2. 作業スケジュール策定
3. 定期進捗報告の開始
4. 品質基準の確認・周知

## 予定報告
- 第1回進捗報告: 24時間後
- 完了予定: 7日以内

効率的に進めて早期完了を目指します！

---
**Boss ($ORG_NAME) - 自動確認**
EOF
    
    # Final Boss起動トリガー
    echo "task_received_${ORG_NAME}" >> "$SHARED_MESSAGES/.trigger_final_boss"
    
    log "📤 タスク受信確認を送信: $task_name"
}

# Worker修正通知作成
create_worker_correction_notice() {
    local notice_file="$CURRENT_DIR/CORRECTION_NOTICE.md"
    
    cat > "$notice_file" << EOF
# 🔧 修正作業通知

**緊急**: Final Boss より修正要求を受信しました

## 修正が必要な項目
1. ファイル構造の確認
2. 依存関係の確認  
3. テストの実行確認
4. ドキュメントの補完

## 各Worker対応指示
### Worker-A
- 実装コードの見直し
- テストケースの補強

### Worker-B  
- 統合テストの実行
- 依存関係の確認

### Worker-C
- ドキュメントの更新
- 品質チェックの再実行

## 完了報告
修正完了後、Boss にて以下を実行:
\`\`\`bash
bash scripts/boss_send_message.sh completed "修正完了"
\`\`\`

---
**Boss ($ORG_NAME) - 修正指示**
EOF
    
    log "📝 Worker修正通知作成: $notice_file"
}

# Worker再作業通知作成  
create_worker_rework_notice() {
    local notice_file="$CURRENT_DIR/REWORK_NOTICE.md"
    
    cat > "$notice_file" << EOF
# 🔄 再作業通知

**重要**: 品質基準未達により再作業が必要です

## 品質基準
- テストカバレッジ95%以上
- 静的解析エラー0件
- パフォーマンス基準満足
- ドキュメント完備

## 各Worker再作業指示
### Worker-A
- コード品質の向上
- テストカバレッジの改善

### Worker-B
- パフォーマンス最適化
- 静的解析エラーの修正

### Worker-C  
- ドキュメント品質向上
- 総合的な品質チェック

## 完了報告
再作業完了後、Boss にて以下を実行:
\`\`\`bash
bash scripts/boss_send_message.sh completed "再作業完了"
\`\`\`

---
**Boss ($ORG_NAME) - 再作業指示**
EOF
    
    log "📝 Worker再作業通知作成: $notice_file"
}

# メイン処理
main() {
    log "🚀 Boss ($ORG_NAME) メッセージ受信システム開始"
    
    # メッセージディレクトリ確認
    if [ ! -d "$SHARED_MESSAGES" ]; then
        log "⚠️ 共有メッセージディレクトリが存在しません: $SHARED_MESSAGES"
        echo "⚠️ 共有メッセージシステムが初期化されていません"
        return 1
    fi
    
    # メッセージ受信・処理
    check_messages
    
    log "✅ Boss ($ORG_NAME) メッセージ受信システム完了"
}

# 引数処理
case "${1:-check}" in
    "check")
        main
        ;;
    "watch")
        echo "👁️ Boss ($ORG_NAME) メッセージ監視モード"
        echo "Ctrl+C で停止"
        while true; do
            main
            sleep 30  # 30秒間隔で確認
        done
        ;;
    "status")
        echo "📊 Boss ($ORG_NAME) メッセージシステム状況"
        echo "========================================="
        echo "受信待ちメッセージ: $(find "$SHARED_MESSAGES" -maxdepth 1 -name "to_boss_${ORG_NAME}_*.md" 2>/dev/null | wc -l)"
        echo "処理済みメッセージ: $(find "$SHARED_MESSAGES/processed" -name "to_boss_${ORG_NAME}_*.md" 2>/dev/null | wc -l)"
        echo "送信済みメッセージ: $(find "$SHARED_MESSAGES/processed" -name "from_boss_${ORG_NAME}_*.md" 2>/dev/null | wc -l)"
        ;;
    *)
        echo "使用方法: $0 {check|watch|status}"
        echo ""
        echo "  check   - 新しいメッセージを確認・処理"
        echo "  watch   - 継続的にメッセージを監視"
        echo "  status  - メッセージシステムの状況表示"
        exit 1
        ;;
esac 