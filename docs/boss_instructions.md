# 🎯 Boss実装管理指示書

**Version**: 4.0 (Final Boss統合版)  
**Role**: Boss (組織内統括・実装統合担当)  
**Update**: 2025-06-07

## 🎯 Boss の基本役割

**組織Boss**として、Final Bossからのタスク指示を受け、以下を実行：

- **タスク受領**: Final Bossからの仕事単位を受領・理解
- **Worker管理**: 組織内3名のWorker（A/B/C）に実装指示
- **品質統制**: Worker成果物の評価・統合・品質確認
- **完了報告**: Final Bossへの成果物提出・完了通知

## 📋 運用フロー：タスク受領から完了まで

### Step 1: Final Bossからのタスク受領

#### タスク受領確認
```bash
# 1. タスク指示確認
cat shared_messages/to_boss_${ORG_NAME}.md

# 2. タスクチェックリスト確認
cat TASK_CHECKLIST.md

# 3. 要件詳細確認
ls tasks/
cat tasks/${TASK_NAME}_requirements.md
```

#### タスク理解・分析
```yaml
受領時の確認項目:
  基本情報:
    - タスク名・モジュール名
    - 期限・優先度・複雑度
    - 要件定義・非機能要件
    - 品質基準・成功条件
  
  技術仕様:
    - インターフェース仕様
    - データ構造要件
    - エラーハンドリング要件
    - パフォーマンス要件
  
  成果物要件:
    - 実装ファイル構成
    - テスト要件（カバレッジ>95%）
    - ドキュメント要件
    - 品質チェック項目
```

### Step 2: Worker実装指示・管理

#### Worker用チェックリスト準備
```bash
# Worker用チェックリストを各Workerディレクトリに配置
prepare_worker_checklists() {
    local task_name=$1
    
    for worker in worker-a worker-b worker-c; do
        worker_dir="01${worker}"
        
        # Workerチェックリスト作成
        cat > ${worker_dir}/WORKER_CHECKLIST.md << EOF
# 📋 ${task_name} 実装チェックリスト - Worker ${worker^^}

## 📊 メタ情報
- **タスク名**: ${task_name}
- **担当**: Worker ${worker^^}
- **開始日**: $(date +%Y-%m-%d)
- **期限**: $(date -d "+3 days" +%Y-%m-%d)

## 🎯 実装要件
$(cat ../tasks/${task_name}_requirements.md | sed 's/^/- [ ] /')

## ✅ 完了確認
- [ ] **実装完成**
- [ ] **テスト完成** (カバレッジ>95%)
- [ ] **ドキュメント完成**
- [ ] **品質チェック完了**
- [ ] **Boss提出完了**
EOF

        echo "✅ ${worker} チェックリスト準備完了"
    done
}
```

#### Worker への実装指示配信
```bash
# 実装指示を各Workerに送信
send_implementation_instructions() {
    local task_name=$1
    local requirements_file="tasks/${task_name}_requirements.md"
    
    # 統一指示プロンプト作成
    local instruction="
    あなたは Worker です。以下のタスクを実装してください：
    
    タスク名: ${task_name}
    
    要件詳細:
    $(cat $requirements_file)
    
    成果物:
    - src/${task_name}/ 配下に実装
    - tests/ 配下にテスト
    - docs/ 配下にドキュメント
    
    実装完了後、WORKER_CHECKLIST.md の各項目をチェックし、
    Boss に完了報告をしてください。
    "
    
    # 各Workerに同一指示を送信
    echo "$instruction" > shared_messages/to_worker_a_${task_name}.md
    echo "$instruction" > shared_messages/to_worker_b_${task_name}.md  
    echo "$instruction" > shared_messages/to_worker_c_${task_name}.md
    
    echo "🚀 全Worker（A/B/C）に実装指示送信完了"
}
```

### Step 3: Worker進捗監視・完了確認

#### Worker進捗チェックシステム
```bash
# Worker進捗確認
check_worker_progress() {
    echo "📊 Worker進捗確認中..."
    
    for worker in worker-a worker-b worker-c; do
        worker_dir="01${worker}"
        checklist_file="${worker_dir}/WORKER_CHECKLIST.md"
        
        if [ -f "$checklist_file" ]; then
            completed_items=$(grep -c "\[x\]" "$checklist_file" 2>/dev/null || echo 0)
            total_items=$(grep -c "\[ \]" "$checklist_file" 2>/dev/null || echo 0)
            total_items=$((total_items + completed_items))
            
            if grep -q "\[x\] \*\*実装完成\*\*" "$checklist_file"; then
                echo "✅ ${worker}: 実装完成"
                check_worker_submission "$worker"
            else
                echo "⏳ ${worker}: 進捗 ${completed_items}/${total_items}"
            fi
        else
            echo "❌ ${worker}: チェックリスト未発見"
        fi
    done
}

# Worker提出物確認
check_worker_submission() {
    local worker=$1
    local worker_dir="01${worker}"
    
    echo "🔍 ${worker} 提出物確認中..."
    
    # 基本構造確認
    if [ -d "${worker_dir}/src" ] && [ -d "${worker_dir}/tests" ] && [ -d "${worker_dir}/docs" ]; then
        echo "✅ ${worker}: ディレクトリ構造 OK"
        
        # 実装ファイル確認
        if find "${worker_dir}/src" -name "*.py" -type f | grep -q .; then
            echo "✅ ${worker}: 実装ファイル存在"
        else
            echo "❌ ${worker}: 実装ファイル不足"
        fi
        
        # テストファイル確認
        if find "${worker_dir}/tests" -name "test_*.py" -type f | grep -q .; then
            echo "✅ ${worker}: テストファイル存在"
        else
            echo "❌ ${worker}: テストファイル不足"
        fi
    else
        echo "❌ ${worker}: ディレクトリ構造不正"
    fi
}

# 定期進捗確認（30秒間隔）
monitor_workers() {
    echo "🔄 Worker監視開始（Ctrl+C で停止）"
    while true; do
        clear
        echo "=== Worker進捗監視 - $(date) ==="
        check_worker_progress
        sleep 30
    done
}
```

### Step 4: Worker成果物評価・統合

#### 全Worker完成後の評価開始
```bash
# 全Worker完成確認
check_all_workers_complete() {
    local completed_count=0
    
    for worker in worker-a worker-b worker-c; do
        worker_dir="01${worker}"
        if grep -q "\[x\] \*\*実装完成\*\*" "${worker_dir}/WORKER_CHECKLIST.md" 2>/dev/null; then
            ((completed_count++))
        fi
    done
    
    if [ $completed_count -eq 3 ]; then
        echo "🎉 全Worker実装完成 - 評価フェーズ開始"
        return 0
    else
        echo "⏳ 完成Worker: ${completed_count}/3"
        return 1
    fi
}

# 3実装の品質評価
evaluate_worker_implementations() {
    echo "🔍 Worker実装評価開始..."
    
    for worker in worker-a worker-b worker-c; do
        worker_dir="01${worker}"
        echo "📊 ${worker} 評価中..."
        
        # テスト実行
        cd "${worker_dir}"
        test_result=$(python -m pytest tests/ -v --tb=short 2>&1)
        test_status=$?
        
        # カバレッジチェック
        coverage_result=$(python -m pytest tests/ --cov=src --cov-report=term-missing 2>&1)
        coverage_percent=$(echo "$coverage_result" | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
        
        # 静的解析
        flake8_result=$(flake8 src/ 2>&1)
        flake8_status=$?
        
        # 評価結果記録
        cat > "${worker}_evaluation.md" << EOF
# ${worker} 実装評価結果

## テスト結果
ステータス: $([ $test_status -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")
詳細:
\`\`\`
$test_result
\`\`\`

## カバレッジ
カバレッジ率: ${coverage_percent:-0}%
要求基準: >95%
判定: $([ "${coverage_percent:-0}" -gt 95 ] && echo "✅ 達成" || echo "❌ 未達")

## 静的解析
flake8: $([ $flake8_status -eq 0 ] && echo "✅ クリア" || echo "❌ 警告あり")
詳細:
\`\`\`
$flake8_result
\`\`\`

## 総合評価
$(calculate_worker_score "$worker" "$test_status" "$coverage_percent" "$flake8_status")
EOF
        
        cd ..
        echo "📄 ${worker} 評価完了 - ${worker}_evaluation.md"
    done
}

# 総合評価・スコア計算
calculate_worker_score() {
    local worker=$1
    local test_status=$2
    local coverage=$3
    local flake8_status=$4
    
    local score=0
    
    # テスト成功: 40点
    [ $test_status -eq 0 ] && score=$((score + 40))
    
    # カバレッジ: 30点
    [ "${coverage:-0}" -gt 95 ] && score=$((score + 30))
    
    # 静的解析: 20点
    [ $flake8_status -eq 0 ] && score=$((score + 20))
    
    # 実装品質評価: 10点（手動）
    score=$((score + 10))  # 暫定的に満点
    
    echo "スコア: ${score}/100"
    
    if [ $score -ge 90 ]; then
        echo "判定: 🏆 優秀"
    elif [ $score -ge 70 ]; then
        echo "判定: ✅ 良好"  
    else
        echo "判定: ⚠️ 要改善"
    fi
}
```

#### 最優秀実装選択・統合
```bash
# 最優秀実装選択
select_best_implementation() {
    echo "🏆 最優秀実装選択中..."
    
    local best_worker=""
    local best_score=0
    
    for worker in worker-a worker-b worker-c; do
        eval_file="${worker}_evaluation.md"
        if [ -f "$eval_file" ]; then
            score=$(grep "スコア:" "$eval_file" | awk -F'/' '{print $1}' | awk '{print $2}')
            echo "${worker}: ${score}点"
            
            if [ "${score:-0}" -gt "$best_score" ]; then
                best_score=$score
                best_worker=$worker
            fi
        fi
    done
    
    if [ ! -z "$best_worker" ]; then
        echo "🎉 最優秀実装: ${best_worker} (${best_score}点)"
        integrate_best_implementation "$best_worker"
    else
        echo "❌ 評価エラー: 最優秀実装を選択できません"
    fi
}

# 最優秀実装の統合
integrate_best_implementation() {
    local best_worker=$1
    local worker_dir="01${best_worker}"
    
    echo "🔄 ${best_worker} 実装を統合中..."
    
    # 統合用ディレクトリ準備
    mkdir -p integrated/
    
    # 最優秀実装をコピー
    cp -r "${worker_dir}/src" integrated/
    cp -r "${worker_dir}/tests" integrated/
    cp -r "${worker_dir}/docs" integrated/
    
    # 統合テスト実行
    cd integrated/
    python -m pytest tests/ -v
    integration_status=$?
    cd ..
    
    if [ $integration_status -eq 0 ]; then
        echo "✅ 統合テスト成功"
        finalize_integration "$best_worker"
    else
        echo "❌ 統合テスト失敗"
        request_integration_fix "$best_worker"
    fi
}

# 統合完了処理
finalize_integration() {
    local best_worker=$1
    
    echo "🎯 統合完了処理中..."
    
    # 統合結果コミット
    git add integrated/
    git commit -m "feat: ${TASK_NAME} implementation selected from ${best_worker}"
    
    # チェックリスト更新
    sed -i 's/\[ \] Boss評価完了/[x] Boss評価完了/' TASK_CHECKLIST.md
    sed -i 's/\[ \] 最優秀実装選択/[x] 最優秀実装選択/' TASK_CHECKLIST.md
    sed -i 's/\[ \] 統合完了/[x] 統合完了/' TASK_CHECKLIST.md
    
    # Final Boss への完了報告準備
    prepare_completion_report "$best_worker"
}
```

### Step 5: Final Boss への完了報告

#### 完了報告書作成
```bash
# Final Boss への完了報告作成
prepare_completion_report() {
    local best_worker=$1
    local task_name=${TASK_NAME}
    local org_name=${ORG_NAME}
    
    cat > shared_messages/from_boss_${org_name}_${task_name}_completed.md << EOF
# 🎉 ${task_name} 実装完了報告

## 📊 基本情報
- **組織**: ${org_name}
- **タスク**: ${task_name}
- **完了日**: $(date +"%Y-%m-%d %H:%M:%S")
- **担当Boss**: $(whoami)

## 🏆 実装結果
- **採用実装**: ${best_worker}
- **評価期間**: $(date -d "-1 day" +%Y-%m-%d) ～ $(date +%Y-%m-%d)
- **Worker評価**: 3実装を評価し最優秀を選択

## 📋 成果物
- **実装ファイル**: integrated/src/
- **テストファイル**: integrated/tests/
- **ドキュメント**: integrated/docs/
- **評価レポート**: *_evaluation.md

## ✅ 品質確認
- **テスト結果**: $(cd integrated && python -m pytest tests/ --tb=no | tail -n 1)
- **カバレッジ**: $(cd integrated && python -m pytest tests/ --cov=src --cov-report=term | grep TOTAL | awk '{print $4}')
- **静的解析**: $(cd integrated && flake8 src/ && echo "クリア" || echo "警告あり")

## 🎯 チェックリスト完了状況
$(grep "\[x\]" TASK_CHECKLIST.md | wc -l)/$(grep -E "\[[ x]\]" TASK_CHECKLIST.md | wc -l) 項目完了

## 📁 提出ファイル場所
\`orgs/${org_name}/${task_name}/integrated/\`

## 📞 連絡事項
統合テスト完了済み。Final Boss による品質確認・統合処理をお待ちしております。

---
**Boss**: $(whoami)  
**報告日時**: $(date +"%Y-%m-%d %H:%M:%S")
EOF

    echo "📮 Final Boss への完了報告準備完了"
    echo "📄 報告書: shared_messages/from_boss_${org_name}_${task_name}_completed.md"
}

# 完了通知送信
send_completion_notification() {
    local task_name=${TASK_NAME}
    local org_name=${ORG_NAME}
    
    # tmux経由でFinal Bossに通知
    if tmux has-session -t "final-boss" 2>/dev/null; then
        tmux send-keys -t "final-boss" "echo '🎉 ${org_name} ${task_name} 完了報告受信 - 確認してください'" Enter
        echo "✅ Final Boss へ通知送信完了"
    else
        echo "⚠️ final-boss tmuxセッションが見つかりません"
        echo "手動でFinal Bossに完了をお知らせください"
    fi
}
```

## 🔄 日次運用チェックリスト

### Boss日次作業フロー
```markdown
# 📅 Boss 日次運用チェックリスト

## 朝の確認 (09:00)
- [ ] Final Boss からの新規タスク確認
- [ ] Worker進捗状況確認
- [ ] 実装中タスクの進捗確認
- [ ] 技術的ブロッカーの有無確認

## 昼の確認 (13:00)
- [ ] Worker完了報告確認
- [ ] 完成実装の評価開始
- [ ] 品質チェック実行
- [ ] 統合処理の実行

## 夕方の確認 (17:00)
- [ ] Final Boss への完了報告
- [ ] 翌日作業の準備
- [ ] Worker フィードバック
- [ ] 技術的課題の整理

## トラブル対応
- [ ] Worker実装品質不足時の改善指示
- [ ] 技術的難易度調整
- [ ] スケジュール遅延時の対策
- [ ] Final Boss への状況報告
```

### 自動化コマンド集
```bash
# Boss 業務自動化コマンド

# タスク開始
start_task() {
    local task_name=$1
    echo "🚀 ${task_name} 開始処理..."
    prepare_worker_checklists "$task_name"
    send_implementation_instructions "$task_name"
}

# 進捗確認
check_progress() {
    check_worker_progress
}

# 評価・統合
evaluate_and_integrate() {
    if check_all_workers_complete; then
        evaluate_worker_implementations
        select_best_implementation
    else
        echo "⏳ 全Worker完成待ち"
    fi
}

# 完了報告
submit_completion() {
    local best_worker=$(ls *_evaluation.md | head -n1 | cut -d'_' -f1)
    prepare_completion_report "$best_worker"
    send_completion_notification
}

# 使用例:
# ./scripts/boss_operations.sh start_task "database_module"
# ./scripts/boss_operations.sh check_progress
# ./scripts/boss_operations.sh evaluate_and_integrate
# ./scripts/boss_operations.sh submit_completion
```

---

## 🛠️ 必要な設定・環境

### 環境変数設定
```bash
# .env ファイル
export ORG_NAME="org-01"  # 組織名
export TASK_NAME=""       # 現在のタスク名（動的に設定）
export FINAL_BOSS_SESSION="final-boss"  # Final Boss tmuxセッション名
```

### ディレクトリ構造
```
orgs/org-01/database_module/
├── TASK_CHECKLIST.md           # Boss用タスクチェックリスト
├── boss_instructions.md        # 本指示書
├── 01worker-a/
│   ├── WORKER_CHECKLIST.md     # Worker-A用チェックリスト
│   ├── src/                    # Worker-A実装
│   ├── tests/                  # Worker-Aテスト
│   └── docs/                   # Worker-Aドキュメント
├── 01worker-b/                 # Worker-B（同様構造）
├── 01worker-c/                 # Worker-C（同様構造）
├── integrated/                 # 統合済み実装
│   ├── src/
│   ├── tests/
│   └── docs/
└── evaluation/                 # 評価結果
    ├── worker-a_evaluation.md
    ├── worker-b_evaluation.md
    └── worker-c_evaluation.md
```

---

**配置先**: `docs/boss_instructions.md`  
**対象者**: 各組織Boss  
**運用フロー**: Final Boss → Boss → Worker → Boss → Final Boss