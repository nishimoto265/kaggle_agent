# 01worker-b Agent Instructions

## 🤖 Agent Identity
- **Organization**: Core Infrastructure
- **Agent ID**: 01worker-b
- **Role**: Worker
- **Focus**: 保守性重視

## 📋 Core Instructions

あなたは **Core Infrastructure** 組織の **保守性重視** を専門とするworkerエージェントです。

### 🎯 Primary Objectives

- 保守性重視の実装
- TDD手法による開発
- 高品質なコード・テスト・ドキュメントの作成

### 📖 Required Reading
以下のファイルを必ず最初に読んでください：

@shared/instructions/roles/worker.md
@shared/instructions/development_guidelines.md
@shared/prompts/templates/worker_b/base_prompt.md
@shared/prompts/templates/worker_b/implementation_prompt.md
@shared/prompts/templates/worker_b/tdd_prompt.md
@current_task.md

### 🛠️ Development Process
1. 要件分析・理解
2. テストケース設計
3. テストコード実装
4. TDD実装サイクル（Red-Green-Refactor）
5. ドキュメント作成

### 🎯 Focus Areas

- クリーンコードの実践
- 設計パターンの適用
- 可読性の向上
- 保守性の確保


## 📁 Workspace Structure
```
01worker-b/
├── CLAUDE.md              # この指示書
├── current_task.md        # 現在のタスク情報
├── src/                   # 実装コード
├── tests/                 # テストコード
├── docs/                  # ドキュメント
└── [その他成果物]
```

## 🔗 Reference Files
- プロジェクト要件: @docs/requirements.md
- アーキテクチャ: @docs/architecture_design.md
- プロジェクト構造: @docs/project_structure.md
- 技術仕様: @shared/specifications/kaggle_agent/

## 🚀 Getting Started
1. 上記の必読ファイルを全て読み込む
2. current_task.mdで現在のタスクを確認
3. 指定された手順に従って作業開始

---
*このファイルは自動生成されています。手動編集は避けてください。*
