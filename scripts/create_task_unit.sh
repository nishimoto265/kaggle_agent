#!/bin/bash

# 新規タスク単位作成スクリプト
# Usage: ./scripts/create_task_unit.sh "task_name" "org_name" "priority" "complexity"

set -e

TASK_NAME=$1
ORG_NAME=$2
PRIORITY=${3:-"Medium"}
COMPLEXITY=${4:-"Medium"}

if [ -z "$TASK_NAME" ] || [ -z "$ORG_NAME" ]; then
    echo "Usage: $0 <task_name> <org_name> [priority] [complexity]"
    echo "Example: $0 'database_module' 'org-01' 'High' 'Complex'"
    exit 1
fi

echo "🚀 新規タスク作成開始: $TASK_NAME (組織: $ORG_NAME)"

# タスクディレクトリ作成
TASK_DIR="tasks"
mkdir -p "$TASK_DIR"

# タスク要件ファイル作成
cat > "$TASK_DIR/${TASK_NAME}_requirements.md" << EOF
# ${TASK_NAME} 実装要件

## 基本情報
- **タスク名**: ${TASK_NAME}
- **担当組織**: ${ORG_NAME}
- **優先度**: ${PRIORITY}
- **複雑度**: ${COMPLEXITY}
- **作成日**: $(date +%Y-%m-%d)

## 機能要件
- [ ] 基本機能の実装
- [ ] エラーハンドリングの実装
- [ ] ログ機能の実装
- [ ] 設定管理の実装

## 非機能要件
- [ ] パフォーマンス要件の満足
- [ ] セキュリティ要件の遵守
- [ ] 可用性要件の確保

## 技術仕様
- **言語**: Python 3.9+
- **フレームワーク**: 要件に応じて選択
- **テストフレームワーク**: pytest
- **品質ツール**: black, flake8, mypy

## 成果物
- \`src/${TASK_NAME}/\` - 実装コード
- \`tests/\` - テストコード
- \`docs/\` - ドキュメント

## 品質基準
- テストカバレッジ > 95%
- 静的解析エラー 0件
- パフォーマンス基準達成
EOF

# タスクチェックリスト作成
cat > "$TASK_DIR/${TASK_NAME}_checklist.md" << EOF
# 📋 ${TASK_NAME} 開発チェックリスト

## 📊 メタ情報
- **モジュール名**: ${TASK_NAME}
- **担当組織**: ${ORG_NAME}
- **開始日**: $(date +%Y-%m-%d)
- **期限**: $(date -d "+7 days" +%Y-%m-%d)
- **優先度**: ${PRIORITY}
- **複雑度**: ${COMPLEXITY}

## 🎯 要件定義
- [ ] 機能要件明確化
- [ ] 非機能要件定義
- [ ] インターフェース仕様確定
- [ ] データ構造設計
- [ ] エラーハンドリング戦略
- [ ] 他モジュールとの連携仕様

## 💻 実装要件
- [ ] コア機能実装
- [ ] エラーハンドリング実装
- [ ] ログ機能実装
- [ ] 設定管理実装
- [ ] パフォーマンス最適化

## 🧪 テスト要件
- [ ] 単体テスト (カバレッジ>95%)
- [ ] 統合テスト
- [ ] エラーケーステスト
- [ ] パフォーマンステスト

## 📚 ドキュメント要件
- [ ] API文書
- [ ] 使用例・サンプル
- [ ] 設定ガイド
- [ ] トラブルシューティング

## ✅ 品質基準
- [ ] 静的解析クリア
- [ ] セキュリティスキャンクリア
- [ ] パフォーマンス基準満足
- [ ] Final Boss品質確認完了
EOF

# プロジェクトチェックリストに追加
if [ -f "PROJECT_CHECKLIST.md" ]; then
    echo "- [ ] ${TASK_NAME} (${ORG_NAME}) - $(date +%Y-%m-%d)" >> PROJECT_CHECKLIST.md
    echo "✅ PROJECT_CHECKLIST.md に追加"
fi

echo "🎯 タスク作成完了:"
echo "📄 要件書: $TASK_DIR/${TASK_NAME}_requirements.md"
echo "📋 チェックリスト: $TASK_DIR/${TASK_NAME}_checklist.md"
echo "📂 次のステップ: ./scripts/quick_send.sh boss0X \"新タスク: $TASK_NAME を開始してください\"" 