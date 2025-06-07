#!/bin/bash

# メイン統合スクリプト
# Usage: ./scripts/integrate_to_main.sh "org_name" "task_name"

set -e

ORG_NAME=$1
TASK_NAME=$2

if [ -z "$ORG_NAME" ] || [ -z "$TASK_NAME" ]; then
    echo "Usage: $0 <org_name> <task_name>"
    echo "Example: $0 'org-01' 'database_module'"
    exit 1
fi

TASK_PATH="orgs/$ORG_NAME/$TASK_NAME"
INTEGRATED_PATH="$TASK_PATH/integrated"

echo "🔄 メイン統合開始: $ORG_NAME/$TASK_NAME"

# 事前確認
if [ ! -d "$TASK_PATH" ]; then
    echo "❌ タスクディレクトリが存在しません: $TASK_PATH"
    exit 1
fi

if [ ! -d "$INTEGRATED_PATH" ]; then
    echo "❌ 統合済みディレクトリが存在しません: $INTEGRATED_PATH"
    exit 1
fi

# 品質評価実行
echo "🔍 品質評価実行中..."
python scripts/quality_evaluation.py "$ORG_NAME" "$TASK_NAME"
evaluation_result=$?

case $evaluation_result in
    0)
        echo "✅ 品質評価: INTEGRATE (そのまま統合)"
        INTEGRATION_TYPE="INTEGRATE"
        ;;
    1)
        echo "🔧 品質評価: MINOR_FIX (軽微修正後統合)"
        INTEGRATION_TYPE="MINOR_FIX"
        ;;
    2)
        echo "🚨 品質評価: MAJOR_REWORK (再作成必要)"
        echo "統合を中止し、Boss に再作成指示を送信します"
        ./scripts/request_major_rework.sh "$ORG_NAME" "$TASK_NAME"
        exit 2
        ;;
    *)
        echo "❌ 品質評価エラー"
        exit 3
        ;;
esac

# 軽微修正の適用（必要な場合）
if [ "$INTEGRATION_TYPE" = "MINOR_FIX" ]; then
    echo "🔧 軽微修正適用中..."
    ./scripts/apply_minor_fixes.sh "$ORG_NAME" "$TASK_NAME"
    
    # 修正後再評価
    echo "🔍 修正後再評価..."
    python scripts/quality_evaluation.py "$ORG_NAME" "$TASK_NAME"
    if [ $? -ne 0 ]; then
        echo "❌ 修正後も品質基準未達"
        ./scripts/request_major_rework.sh "$ORG_NAME" "$TASK_NAME"
        exit 2
    fi
fi

# メインブランチに統合
echo "🚀 メインブランチ統合開始..."

# 現在のブランチ確認
current_branch=$(git branch --show-current)
echo "現在のブランチ: $current_branch"

# 統合用のコミット作成
cd "$TASK_PATH"

# 統合ファイルをステージング
git add integrated/
git add evaluation/
git add *_evaluation.json 2>/dev/null || true

# コミット作成
commit_message="feat: ${TASK_NAME} implementation by ${ORG_NAME}

- Task: ${TASK_NAME}
- Organization: ${ORG_NAME}
- Quality Score: $(python ../../../scripts/quality_evaluation.py "$ORG_NAME" "$TASK_NAME" --output json | jq -r '.overall_score' 2>/dev/null || echo 'N/A')
- Integration Type: ${INTEGRATION_TYPE}
- Date: $(date +%Y-%m-%d)
"

git commit -m "$commit_message" || {
    echo "⚠️ コミット作成スキップ（変更なしまたはエラー）"
}

# メインブランチに戻る
cd ../../..

# メインブランチとマージ
echo "🔄 メインブランチとマージ中..."

# ワークツリーの内容をメインにマージ
if [ -d "$TASK_PATH/.git" ]; then
    # ワークツリーの場合
    git subtree pull --prefix="shared_main/modules/$TASK_NAME" "$TASK_PATH" HEAD --squash 2>/dev/null || {
        # 初回の場合はsubtree add
        mkdir -p "shared_main/modules"
        git subtree add --prefix="shared_main/modules/$TASK_NAME" "$TASK_PATH" HEAD --squash
    }
else
    # 通常ディレクトリの場合
    mkdir -p "shared_main/modules/$TASK_NAME"
    cp -r "$INTEGRATED_PATH"/* "shared_main/modules/$TASK_NAME/"
    
    git add "shared_main/modules/$TASK_NAME"
    git commit -m "integrate: ${TASK_NAME} from ${ORG_NAME}" || echo "コミットスキップ"
fi

# 統合テスト実行
echo "🧪 統合テスト実行中..."
integration_test_result=0

if [ -d "shared_main/modules/$TASK_NAME/tests" ]; then
    cd "shared_main/modules/$TASK_NAME"
    python -m pytest tests/ -v || integration_test_result=$?
    cd ../../..
fi

if [ $integration_test_result -eq 0 ]; then
    echo "✅ 統合テスト成功"
else
    echo "❌ 統合テスト失敗"
    # ロールバック処理
    echo "🔄 ロールバック実行中..."
    git reset --hard HEAD~1
    exit 4
fi

# プロジェクトチェックリスト更新
echo "📋 プロジェクトチェックリスト更新中..."
if [ -f "PROJECT_CHECKLIST.md" ]; then
    # チェックリストにマーク
    sed -i "s/- \[ \] ${TASK_NAME}/- [x] ${TASK_NAME} ✅ $(date +%Y-%m-%d)/" PROJECT_CHECKLIST.md
    git add PROJECT_CHECKLIST.md
    git commit -m "update: mark ${TASK_NAME} as completed" || echo "チェックリスト更新スキップ"
fi

# 統合完了通知
echo "📮 統合完了通知作成中..."
cat > "shared_messages/integration_completed_${ORG_NAME}_${TASK_NAME}.md" << EOF
# 🎉 統合完了通知

## 📊 統合情報
- **タスク**: ${TASK_NAME}
- **組織**: ${ORG_NAME}
- **統合日時**: $(date +"%Y-%m-%d %H:%M:%S")
- **統合タイプ**: ${INTEGRATION_TYPE}

## ✅ 統合結果
- **品質スコア**: $(python scripts/quality_evaluation.py "$ORG_NAME" "$TASK_NAME" --output json | jq -r '.overall_score' 2>/dev/null || echo 'N/A')/100
- **統合テスト**: ✅ 成功
- **統合場所**: shared_main/modules/${TASK_NAME}/

## 🎯 次のステップ
1. 他のモジュールとの連携テスト
2. 全体システム統合テスト
3. 次のタスクの準備

---
**Final Boss**: $(whoami)  
**統合完了時刻**: $(date +"%Y-%m-%d %H:%M:%S")
EOF

# Boss への統合完了通知
if tmux has-session -t "${ORG_NAME}-boss" 2>/dev/null; then
    tmux send-keys -t "${ORG_NAME}-boss" "echo '🎉 ${TASK_NAME} 統合完了! 次のタスクをお待ちください'" Enter
fi

echo ""
echo "🎯 統合完了サマリー:"
echo "  タスク: $TASK_NAME"
echo "  組織: $ORG_NAME"
echo "  統合場所: shared_main/modules/$TASK_NAME/"
echo "  プロジェクト進捗: PROJECT_CHECKLIST.md 更新済み"
echo "  通知: shared_messages/integration_completed_${ORG_NAME}_${TASK_NAME}.md"
echo ""
echo "🚀 次のアクション:"
echo "  1. 他のタスクの進捗確認"
echo "  2. 新しいタスクの割り当て"
echo "  3. 全体システムテストの実行"
echo ""
echo "✅ 統合処理完了!" 