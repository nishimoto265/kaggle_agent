#!/bin/bash

# 🔍 全Worker完了チェック＆Boss報告スクリプト
# 使用方法: ./check_all_workers_done.sh [org-番号]

# 組織番号取得（引数 or 現在のディレクトリから）
if [ -n "$1" ]; then
    ORG_NUM="$1"
else
    ORG_NUM=$(pwd | grep -o 'org-[0-9][0-9]' | tail -1)
fi

if [ -z "$ORG_NUM" ]; then
    echo "❌ 組織番号が特定できません。引数で指定してください: ./check_all_workers_done.sh org-01"
    exit 1
fi

echo "🔍 $ORG_NUM の全Worker完了状況をチェック中..."

# ベースディレクトリ設定
BASE_DIR="orgs/$ORG_NUM"

# 各Workerの完成状況確認
check_worker_done() {
    local worker_dir="$1"
    local checklist_file="$BASE_DIR/$worker_dir/WORKER_CHECKLIST.md"
    
    if [ -f "$checklist_file" ]; then
        if grep -q "\[x\] \*\*実装完成\*\*" "$checklist_file" 2>/dev/null; then
            echo "1"
        else
            echo "0"
        fi
    else
        echo "0"
    fi
}

WORKER_A_DONE=$(check_worker_done "01worker-a")
WORKER_B_DONE=$(check_worker_done "01worker-b")  
WORKER_C_DONE=$(check_worker_done "01worker-c")

echo "📊 完了状況:"
echo "  Worker-A: $([ $WORKER_A_DONE -eq 1 ] && echo '✅完了' || echo '⏳作業中')"
echo "  Worker-B: $([ $WORKER_B_DONE -eq 1 ] && echo '✅完了' || echo '⏳作業中')"
echo "  Worker-C: $([ $WORKER_C_DONE -eq 1 ] && echo '✅完了' || echo '⏳作業中')"

# 全Worker完成判定
TOTAL_DONE=$((WORKER_A_DONE + WORKER_B_DONE + WORKER_C_DONE))

echo "🎯 完了総数: $TOTAL_DONE/3"

if [ $TOTAL_DONE -eq 3 ]; then
    echo "🎉 全Worker完成！Boss に報告します"
    
    # Boss target決定
    case $ORG_NUM in
        "org-01") BOSS_TARGET="boss01" ;;
        "org-02") BOSS_TARGET="boss02" ;;
        "org-03") BOSS_TARGET="boss03" ;;
        "org-04") BOSS_TARGET="boss04" ;;
        *) 
            echo "❌ 不明な組織番号: $ORG_NUM"
            exit 1
            ;;
    esac
    
    echo "📤 Boss報告先: $BOSS_TARGET"
    
    # Boss報告実行
    if ./scripts/quick_send.sh "$BOSS_TARGET" "実装が完了しました。"; then
        echo "✅ Boss報告完了"
        
        # 全Workerのチェックリスト更新
        for worker_dir in "01worker-a" "01worker-b" "01worker-c"; do
            checklist_file="$BASE_DIR/$worker_dir/WORKER_CHECKLIST.md"
            if [ -f "$checklist_file" ]; then
                sed -i 's/\[ \] \*\*Boss報告完了\*\*/[x] **Boss報告完了**/' "$checklist_file" 2>/dev/null || true
            fi
        done
        
        echo "✅ 全Workerのチェックリスト更新完了"
    else
        echo "❌ Boss報告に失敗しました"
        exit 1
    fi
else
    echo "⏳ 他のWorkerの完了を待機中 ($TOTAL_DONE/3)"
    echo "💡 完了したWorkerから再実行してください"
fi 