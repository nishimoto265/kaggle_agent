#!/bin/bash

# 📤 Boss → Final Boss メッセージ送信スクリプト
# Boss が Final Boss に各種メッセージを送信するために使用

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
mkdir -p "$SHARED_MESSAGES"

# メッセージタイプ
MESSAGE_TYPE="$1"
ADDITIONAL_INFO="$2"

# 使用方法表示
show_usage() {
    echo "使用方法: $0 <MESSAGE_TYPE> [ADDITIONAL_INFO]"
    echo ""
    echo "MESSAGE_TYPE:"
    echo "  completed    - タスク完了報告"
    echo "  progress     - 進捗報告"
    echo "  issue        - 問題報告"  
    echo "  request      - 支援要求"
    echo "  status       - 状況報告"
    echo ""
    echo "例:"
    echo "  $0 completed \"data_processing_foundation\""
    echo "  $0 progress \"60% workers completed\""
    echo "  $0 issue \"Worker-A stuck on dependency error\""
    echo ""
}

# 引数チェック
if [ -z "$MESSAGE_TYPE" ]; then
    show_usage
    exit 1
fi

# タイムスタンプ
TIMESTAMP=$(date -Iseconds)
MESSAGE_ID="${ORG_NAME}_${MESSAGE_TYPE}_$(date +%s)"

# メッセージファイル作成
MESSAGE_FILE="$SHARED_MESSAGES/from_boss_${MESSAGE_ID}.md"

echo "📤 Boss ($ORG_NAME) → Final Boss メッセージ送信..."

case "$MESSAGE_TYPE" in
    "completed")
        TASK_NAME="${ADDITIONAL_INFO:-unknown_task}"
        cat > "$MESSAGE_FILE" << EOF
# 🎉 タスク完了報告

## メッセージ情報
- **送信者**: Boss ($ORG_NAME)
- **メッセージタイプ**: 完了報告
- **タスク名**: $TASK_NAME
- **送信時刻**: $TIMESTAMP
- **緊急度**: 高

## 完了内容
すべてのWorker作業が完了し、タスクの実装が完成しました。

### 完了確認項目
- ✅ Worker-A 実装完了
- ✅ Worker-B 実装完了  
- ✅ Worker-C 実装完了
- ✅ 統合テスト実行済み
- ✅ 品質基準チェック済み

## 提出物
- **実装ディレクトリ**: \`orgs/$ORG_NAME/\`
- **テストファイル**: 全Worker提出済み
- **ドキュメント**: 作成済み

## 次のアクション要求
Final Boss による品質評価と統合処理をお願いします。

---
**Boss ($ORG_NAME) - 自動送信**
EOF
        echo "✅ 完了報告を送信しました: $TASK_NAME"
        ;;
        
    "progress")
        PROGRESS_INFO="${ADDITIONAL_INFO:-progress update}"
        cat > "$MESSAGE_FILE" << EOF
# 📊 進捗報告

## メッセージ情報
- **送信者**: Boss ($ORG_NAME)
- **メッセージタイプ**: 進捗報告
- **送信時刻**: $TIMESTAMP

## 進捗状況
$PROGRESS_INFO

### Worker状況
$(cd "$CURRENT_DIR" && find . -name "WORKER_CHECKLIST.md" -exec echo "- {}: $(grep -c '\[x\]' {} || echo 0)/$(grep -c '\[ \]\|\[x\]' {} || echo 0) 完了" \; 2>/dev/null || echo "- チェックリスト情報取得中...")

## 予定
- 継続して作業を進行中
- 問題があれば追って報告します

---
**Boss ($ORG_NAME) - 進捗自動報告**
EOF
        echo "✅ 進捗報告を送信しました"
        ;;
        
    "issue")
        ISSUE_DESCRIPTION="${ADDITIONAL_INFO:-issue occurred}"
        cat > "$MESSAGE_FILE" << EOF
# 🚨 問題報告

## メッセージ情報
- **送信者**: Boss ($ORG_NAME)
- **メッセージタイプ**: 問題報告
- **送信時刻**: $TIMESTAMP
- **緊急度**: 高

## 問題内容
$ISSUE_DESCRIPTION

## 影響
- 作業進捗に影響あり
- 解決策の検討が必要

## 支援要求
- 技術的なアドバイス
- 代替案の提案
- リソースの追加支援

緊急対応をお願いします。

---
**Boss ($ORG_NAME) - 問題自動報告**
EOF
        echo "🚨 問題報告を送信しました: $ISSUE_DESCRIPTION"
        ;;
        
    "request")
        REQUEST_CONTENT="${ADDITIONAL_INFO:-support needed}"
        cat > "$MESSAGE_FILE" << EOF
# 🤝 支援要求

## メッセージ情報
- **送信者**: Boss ($ORG_NAME)
- **メッセージタイプ**: 支援要求
- **送信時刻**: $TIMESTAMP

## 要求内容
$REQUEST_CONTENT

## 背景
現在の作業において支援が必要な状況が発生しました。

## 期待する支援
- 技術的ガイダンス
- リソースの提供
- 作業方針の調整

よろしくお願いします。

---
**Boss ($ORG_NAME) - 支援要求**
EOF
        echo "🤝 支援要求を送信しました: $REQUEST_CONTENT"
        ;;
        
    "status")
        cat > "$MESSAGE_FILE" << EOF
# 📋 状況報告

## メッセージ情報
- **送信者**: Boss ($ORG_NAME)
- **メッセージタイプ**: 状況報告
- **送信時刻**: $TIMESTAMP

## 現在の状況
${ADDITIONAL_INFO:-"定期状況報告"}

### システム状態
- Boss稼働中
- Worker監視継続中
- 通信システム正常

## 次回報告予定
1時間後

---
**Boss ($ORG_NAME) - 定期状況報告**
EOF
        echo "📋 状況報告を送信しました"
        ;;
        
    *)
        echo "❌ 不明なメッセージタイプ: $MESSAGE_TYPE"
        show_usage
        exit 1
        ;;
esac

# Final Boss 起動トリガーファイル作成
TRIGGER_FILE="$SHARED_MESSAGES/.trigger_final_boss"
echo "$MESSAGE_ID" >> "$TRIGGER_FILE"

echo "🔔 Final Boss 起動トリガーを送信"
echo "📄 メッセージファイル: $MESSAGE_FILE"
echo "⏳ Final Boss の応答を待機中..." 