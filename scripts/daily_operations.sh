#!/bin/bash

# Final Boss 日次運用自動化スクリプト
# Usage: ./scripts/daily_operations.sh {morning|noon|evening|weekly}

set -e

OPERATION=$1

if [ -z "$OPERATION" ]; then
    echo "Usage: $0 {morning|noon|evening|weekly}"
    echo ""
    echo "Operations:"
    echo "  morning  - 朝の確認 (09:00)"
    echo "  noon     - 昼の確認 (13:00)"
    echo "  evening  - 夕方の確認 (17:00)"
    echo "  weekly   - 週次確認 (金曜日)"
    exit 1
fi

echo "🏆 Final Boss 日次運用: $OPERATION - $(date)"
echo "================================================================"

case "$OPERATION" in
    "morning")
        echo "🌅 朝の確認開始..."
        
        echo "📋 1. 全組織Boss完了報告確認"
        if ls shared_messages/from_boss_*_completed.md >/dev/null 2>&1; then
            echo "  ✅ 完了報告あり:"
            ls shared_messages/from_boss_*_completed.md | while read file; do
                echo "    - $(basename "$file")"
            done
        else
            echo "  ℹ️ 新規完了報告なし"
        fi
        
        echo ""
        echo "📊 2. 進行中タスクの進捗確認"
        for org in orgs/org-*/*/; do
            if [ -d "$org" ]; then
                org_path=$(echo "$org" | cut -d'/' -f2-3)
                if [ -f "$org/TASK_CHECKLIST.md" ]; then
                    completed=$(grep -c "\[x\]" "$org/TASK_CHECKLIST.md" 2>/dev/null || echo 0)
                    total=$(grep -c "\[\]" "$org/TASK_CHECKLIST.md" 2>/dev/null || echo 0)
                    total=$((total + completed))
                    echo "  📈 $org_path: $completed/$total 完了"
                fi
            fi
        done
        
        echo ""
        echo "🎯 3. 新規タスクの優先度確認"
        if [ -f "PROJECT_CHECKLIST.md" ]; then
            pending_tasks=$(grep "^- \[ \]" PROJECT_CHECKLIST.md | wc -l)
            echo "  📝 保留中タスク: $pending_tasks 件"
            if [ $pending_tasks -gt 0 ]; then
                echo "  次のタスク候補:"
                grep "^- \[ \]" PROJECT_CHECKLIST.md | head -3 | sed 's/^/    /'
            fi
        fi
        
        echo "✅ 朝の確認完了"
        ;;
        
    "noon")
        echo "🌞 昼の確認開始..."
        
        echo "🔍 1. 完了報告された成果物の品質評価"
        for report in shared_messages/from_boss_*_completed.md; do
            if [ -f "$report" ]; then
                # ファイル名から組織名とタスク名を抽出
                basename_report=$(basename "$report" .md)
                org_name=$(echo "$basename_report" | cut -d'_' -f3)
                task_name=$(echo "$basename_report" | cut -d'_' -f4)
                
                echo "  📊 評価実行: $org_name/$task_name"
                if python scripts/quality_evaluation.py "$org_name" "$task_name" >/dev/null 2>&1; then
                    echo "    ✅ 品質評価完了"
                else
                    echo "    ❌ 品質評価エラー"
                fi
            fi
        done
        
        echo ""
        echo "🔄 2. 統合可能な成果物の統合実行"
        for report in shared_messages/from_boss_*_completed.md; do
            if [ -f "$report" ]; then
                basename_report=$(basename "$report" .md)
                org_name=$(echo "$basename_report" | cut -d'_' -f3)
                task_name=$(echo "$basename_report" | cut -d'_' -f4)
                
                echo "  🚀 統合実行: $org_name/$task_name"
                if ./scripts/integrate_to_main.sh "$org_name" "$task_name" >/dev/null 2>&1; then
                    echo "    ✅ 統合成功"
                    mv "$report" "shared_messages/processed_$(basename "$report")"
                else
                    echo "    ❌ 統合失敗または修正必要"
                fi
            fi
        done
        
        echo "✅ 昼の確認完了"
        ;;
        
    "evening")
        echo "🌆 夕方の確認開始..."
        
        echo "📈 1. 本日の統合実績まとめ"
        today=$(date +%Y-%m-%d)
        completed_today=$(grep "$today" PROJECT_CHECKLIST.md 2>/dev/null | wc -l || echo 0)
        echo "  🎯 本日完了タスク: $completed_today 件"
        
        if [ $completed_today -gt 0 ]; then
            echo "  完了したタスク:"
            grep "$today" PROJECT_CHECKLIST.md | sed 's/^/    /'
        fi
        
        echo ""
        echo "🎯 2. 翌日のタスク準備"
        next_tasks=$(grep "^- \[ \]" PROJECT_CHECKLIST.md | head -3)
        if [ ! -z "$next_tasks" ]; then
            echo "  📋 明日の候補タスク:"
            echo "$next_tasks" | sed 's/^/    /'
        fi
        
        echo ""
        echo "📊 3. プロジェクト全体進捗更新"
        total_tasks=$(grep -c "^- " PROJECT_CHECKLIST.md 2>/dev/null || echo 0)
        completed_tasks=$(grep -c "^- \[x\]" PROJECT_CHECKLIST.md 2>/dev/null || echo 0)
        if [ $total_tasks -gt 0 ]; then
            progress=$((completed_tasks * 100 / total_tasks))
            echo "  🚀 全体進捗: $completed_tasks/$total_tasks ($progress%)"
        fi
        
        echo "✅ 夕方の確認完了"
        ;;
        
    "weekly")
        echo "📊 週次確認開始..."
        
        echo "📋 1. 週次統合レポート作成"
        week_start=$(date -d "last monday" +%Y-%m-%d)
        week_end=$(date +%Y-%m-%d)
        
        report_file="reports/weekly_report_$(date +%Y_W%W).md"
        mkdir -p reports
        
        cat > "$report_file" << EOF
# 🏆 Kaggle Agent 週次統合レポート

**Week**: $(date +%Y-W%W)  
**Report Date**: $(date +%Y-%m-%d)  
**Final Boss**: $(whoami)

## 📊 全体進捗サマリー
- **完了タスク**: $(grep -c "^- \[x\]" PROJECT_CHECKLIST.md 2>/dev/null || echo 0)
- **残タスク**: $(grep -c "^- \[ \]" PROJECT_CHECKLIST.md 2>/dev/null || echo 0)
- **今週完了**: $(grep "$week_start\|$week_end" PROJECT_CHECKLIST.md 2>/dev/null | wc -l || echo 0)

## 🏗️ 組織別進捗
EOF

        for org in org-01 org-02 org-03 org-04; do
            echo "### $org" >> "$report_file"
            if ls orgs/$org/*/ >/dev/null 2>&1; then
                task_count=$(ls -d orgs/$org/*/ | wc -l)
                echo "- **タスク数**: $task_count" >> "$report_file"
            else
                echo "- **タスク数**: 0" >> "$report_file"
            fi
            echo "" >> "$report_file"
        done
        
        echo "  📄 週次レポート作成: $report_file"
        
        echo ""
        echo "🎯 2. 来週のタスク計画策定"
        echo "  📋 来週予定タスク:"
        grep "^- \[ \]" PROJECT_CHECKLIST.md | head -5 | sed 's/^/    /'
        
        echo ""
        echo "📈 3. 品質メトリクス分析"
        if ls orgs/*/*/evaluation_*.json >/dev/null 2>&1; then
            avg_score=$(cat orgs/*/*/evaluation_*.json | jq -r '.overall_score' 2>/dev/null | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')
            echo "  📊 平均品質スコア: $avg_score"
        fi
        
        echo "✅ 週次確認完了"
        ;;
        
    *)
        echo "❌ 未知の操作: $OPERATION"
        echo "有効な操作: morning, noon, evening, weekly"
        exit 1
        ;;
esac

echo ""
echo "================================================================"
echo "🏆 Final Boss 日次運用完了: $(date)" 