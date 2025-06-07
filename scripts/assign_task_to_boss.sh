#!/bin/bash

# Boss にタスク割り当てスクリプト
# Usage: ./scripts/assign_task_to_boss.sh "org_name" "task_name"

set -e

ORG_NAME=$1
TASK_NAME=$2

if [ -z "$ORG_NAME" ] || [ -z "$TASK_NAME" ]; then
    echo "Usage: $0 <org_name> <task_name>"
    echo "Example: $0 'org-01' 'database_module'"
    exit 1
fi

echo "📋 タスク割り当て開始: $TASK_NAME → $ORG_NAME"

# ワークツリー作成
WORKTREE_PATH="orgs/$ORG_NAME/$TASK_NAME"
if [ ! -d "$WORKTREE_PATH" ]; then
    echo "🌿 ワークツリー作成中: $WORKTREE_PATH"
    git worktree add "$WORKTREE_PATH" 2>/dev/null || {
        echo "ワークツリー作成スキップ（既存または作成不可）"
        mkdir -p "$WORKTREE_PATH"
    }
else
    echo "📁 既存ワークツリー利用: $WORKTREE_PATH"
fi

# 作業ディレクトリに移動
cd "$WORKTREE_PATH"

# 基本ディレクトリ構造作成
mkdir -p 01worker-a 01worker-b 01worker-c integrated evaluation shared_messages

# Boss用指示書とチェックリストをコピー
cp "../../../docs/boss_instructions.md" .
cp "../../../tasks/${TASK_NAME}_checklist.md" "./TASK_CHECKLIST.md"

# 環境設定ファイル作成
cat > .env << EOF
# タスク環境設定
export ORG_NAME="$ORG_NAME"
export TASK_NAME="$TASK_NAME"
export FINAL_BOSS_SESSION="final-boss"
export TASK_START_DATE="$(date +%Y-%m-%d)"
EOF

# Boss用メッセージ作成
cat > shared_messages/to_boss_${ORG_NAME}.md << EOF
# 🎯 新規タスク割り当て通知

## 📊 タスク情報
- **タスク名**: ${TASK_NAME}
- **組織**: ${ORG_NAME}
- **割り当て日**: $(date +"%Y-%m-%d %H:%M:%S")
- **期限**: $(date -d "+7 days" +%Y-%m-%d)

## 📋 作業内容
1. **TASK_CHECKLIST.md** を確認してタスク要件を理解
2. **Worker A/B/C** に実装指示を配布
3. **Worker実装監視** を実行
4. **品質評価・統合** を実行
5. **Final Boss** への完了報告

## 📂 ファイル構成
- \`TASK_CHECKLIST.md\` - タスクチェックリスト
- \`boss_instructions.md\` - Boss運用指示書
- \`01worker-{a,b,c}/\` - 各Worker作業ディレクトリ
- \`integrated/\` - 統合結果格納ディレクトリ

## 🚀 開始手順
\`\`\`bash
cd $WORKTREE_PATH
source .env
./scripts/start_task.sh "$TASK_NAME"
\`\`\`

## 📞 サポート
質問や技術的問題は Final Boss までご連絡ください。

---
**From**: Final Boss  
**Date**: $(date +"%Y-%m-%d %H:%M:%S")
EOF

# Boss用実行スクリプト作成
cat > scripts/start_task.sh << 'EOF'
#!/bin/bash
# Boss タスク開始スクリプト

source .env

echo "🚀 タスク開始: $TASK_NAME"

# Worker用チェックリスト準備
prepare_worker_checklists() {
    for worker in worker-a worker-b worker-c; do
        worker_dir="01${worker}"
        
        cat > ${worker_dir}/WORKER_CHECKLIST.md << EOW
# 📋 ${TASK_NAME} 実装チェックリスト - Worker ${worker^^}

## 📊 メタ情報
- **タスク名**: ${TASK_NAME}
- **担当**: Worker ${worker^^}
- **開始日**: $(date +%Y-%m-%d)
- **期限**: $(date -d "+3 days" +%Y-%m-%d)

## 🎯 実装要件
$(cat ../../../tasks/${TASK_NAME}_requirements.md | grep "^- \[ \]" || echo "- [ ] 要件ファイルから取得")

## ✅ 完了確認
- [ ] **実装完成**
- [ ] **テスト完成** (カバレッジ>95%)
- [ ] **ドキュメント完成**
- [ ] **品質チェック完了**
- [ ] **Boss提出完了**
EOW

        echo "✅ ${worker} チェックリスト準備完了"
    done
}

# Worker指示配布
send_worker_instructions() {
    local requirements_file="../../../tasks/${TASK_NAME}_requirements.md"
    
    local instruction="
あなたは Worker です。以下のタスクを実装してください：

タスク名: ${TASK_NAME}

要件詳細:
$(cat $requirements_file 2>/dev/null || echo "要件ファイルを確認してください")

成果物:
- src/${TASK_NAME}/ 配下に実装
- tests/ 配下にテスト  
- docs/ 配下にドキュメント

実装完了後、WORKER_CHECKLIST.md の各項目をチェックし、
Boss に完了報告をしてください。
"
    
    echo "$instruction" > shared_messages/to_worker_a_${TASK_NAME}.md
    echo "$instruction" > shared_messages/to_worker_b_${TASK_NAME}.md
    echo "$instruction" > shared_messages/to_worker_c_${TASK_NAME}.md
    
    echo "🚀 全Worker（A/B/C）に実装指示送信完了"
}

echo "📋 Worker準備中..."
prepare_worker_checklists

echo "📤 Worker指示配布中..."
send_worker_instructions

echo "✅ タスク開始完了"
echo "📊 進捗確認: ./scripts/check_progress.sh"
echo "🔍 評価実行: ./scripts/evaluate_and_integrate.sh"
EOF

chmod +x scripts/start_task.sh

# 進捗確認スクリプト作成
mkdir -p scripts
cat > scripts/check_progress.sh << 'EOF'
#!/bin/bash
# Worker進捗確認スクリプト

source .env

echo "📊 Worker進捗確認 - $(date)"
echo "=================================="

for worker in worker-a worker-b worker-c; do
    worker_dir="01${worker}"
    checklist_file="${worker_dir}/WORKER_CHECKLIST.md"
    
    if [ -f "$checklist_file" ]; then
        completed_items=$(grep -c "\[x\]" "$checklist_file" 2>/dev/null || echo 0)
        total_items=$(grep -c "\[x\]\|\[ \]" "$checklist_file" 2>/dev/null || echo 0)
        
        if grep -q "\[x\] \*\*実装完成\*\*" "$checklist_file" 2>/dev/null; then
            echo "✅ ${worker}: 実装完成"
        else
            echo "⏳ ${worker}: 進捗 ${completed_items}/${total_items}"
        fi
    else
        echo "❌ ${worker}: チェックリスト未発見"
    fi
done

echo "=================================="
EOF

chmod +x scripts/check_progress.sh

# tmux セッション作成（Boss用）
BOSS_SESSION="${ORG_NAME}-boss"
if ! tmux has-session -t "$BOSS_SESSION" 2>/dev/null; then
    tmux new-session -d -s "$BOSS_SESSION" -c "$(pwd)"
    echo "🖥️  Boss用tmuxセッション作成: $BOSS_SESSION"
else
    echo "🖥️  既存Boss用tmuxセッション利用: $BOSS_SESSION"
fi

cd ../../..

echo "🎯 タスク割り当て完了:"
echo "📂 作業ディレクトリ: $WORKTREE_PATH"
echo "💬 Boss用メッセージ: $WORKTREE_PATH/shared_messages/to_boss_${ORG_NAME}.md"
echo "🖥️  tmuxセッション: $BOSS_SESSION"
echo ""
echo "🚀 Boss開始手順:"
echo "  tmux attach -t $BOSS_SESSION"
echo "  cd $WORKTREE_PATH"
echo "  ./scripts/start_task.sh" 