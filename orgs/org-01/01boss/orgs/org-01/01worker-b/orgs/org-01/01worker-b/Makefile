.PHONY: help install dev test lint format clean build run setup-structure setup-agents

help:           ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Project Setup Commands ===
setup-structure: ## プロジェクト構造を自動生成
	@echo "🏗️ Kaggle Agent プロジェクト構造を生成中..."
	python scripts/setup_project_structure.py
	@echo "✅ プロジェクト構造の生成が完了しました"

setup-agents:   ## マルチエージェント環境をセットアップ
	@echo "🤖 マルチエージェント Git Worktree 環境をセットアップ中..."
	python scripts/setup_multi_agent_env.py setup
	@echo "✅ マルチエージェント環境のセットアップが完了しました"

setup-all: setup-structure setup-agents ## 完全セットアップ（構造 + エージェント）
	@echo "🎉 Kaggle Agent システムのセットアップが完了しました！"
	@echo ""
	@echo "📋 次のステップ:"
	@echo "1. make install     # 依存関係をインストール"
	@echo "2. make create-task MODULE=competition_discovery DESCRIPTION='コンペ発見モジュールの実装'"
	@echo "3. エージェントのworktreeで開発を開始"

install:        ## 依存関係をインストール
	pip install -e .[dev]

dev:            ## 開発環境を起動
	docker-compose up -d
	python -m kaggle_agent.cli start --development

# === Multi-Agent Development Commands ===
create-task:    ## 新しい開発タスクを作成 (MODULE=module_name DESCRIPTION="説明" [PRIORITY=medium] [ORG=01])
	@if [ -z "$(MODULE)" ]; then echo "❌ MODULE parameter is required. Example: make create-task MODULE=workflow DESCRIPTION='Workflow engine implementation'"; exit 1; fi
	@if [ -z "$(DESCRIPTION)" ]; then echo "❌ DESCRIPTION parameter is required"; exit 1; fi
	python scripts/task_manager.py create-task "$(MODULE)" "$(DESCRIPTION)" \
		$(if $(PRIORITY),--priority $(PRIORITY)) \
		$(if $(ORG),--org $(ORG))

assign-task:    ## タスクをWorkerに割り当て (TASK_ID=task-xxx [FORCE=true])
	@if [ -z "$(TASK_ID)" ]; then echo "❌ TASK_ID parameter is required. Example: make assign-task TASK_ID=task-abc123def"; exit 1; fi
	python scripts/task_manager.py assign-task $(TASK_ID) $(if $(FORCE),--force)

run-cycle:      ## 開発サイクルを実行 (TASK_ID=task-xxx)
	@if [ -z "$(TASK_ID)" ]; then echo "❌ TASK_ID parameter is required"; exit 1; fi
	python scripts/task_manager.py run-cycle $(TASK_ID)

monitor:        ## Worker進捗を監視 ([TASK_ID=task-xxx])
	python scripts/task_manager.py monitor $(if $(TASK_ID),--task-id $(TASK_ID))

agent-status:   ## エージェント状況を表示 ([VERBOSE=true])
	python scripts/task_manager.py status $(if $(VERBOSE),-v)

worktree-list:  ## Git worktree一覧を表示
	git worktree list

worktree-clean: ## 不要なworktreeを削除
	python scripts/setup_multi_agent_env.py cleanup
	git worktree prune

agents-clean:   ## マルチエージェント環境をクリーンアップ
	python scripts/setup_multi_agent_env.py cleanup
	@echo "✅ マルチエージェント環境をクリーンアップしました"

agents-status:  ## マルチエージェント環境の状態表示
	python scripts/setup_multi_agent_env.py status

# === Development Commands ===
test:           ## テストを実行
	pytest

test-cov:       ## カバレッジ付きテスト実行
	pytest --cov=kaggle_agent --cov-report=html --cov-report=term

lint:           ## コード品質チェック
	black --check src tests
	isort --check-only src tests
	flake8 src tests
	mypy src

format:         ## コードフォーマット
	black src tests
	isort src tests

clean:          ## クリーンアップ
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf build/ dist/ *.egg-info/

# === Build & Deployment Commands ===
build:          ## Dockerイメージをビルド
	docker build -t kaggle-agent:latest .

run:            ## アプリケーションを実行
	python -m kaggle_agent.main

migrate:        ## データベース移行
	alembic upgrade head

seed:           ## サンプルデータを投入
	python scripts/development/load_sample_data.py

deploy-staging: ## ステージング環境にデプロイ
	./scripts/deployment/deploy_staging.sh

deploy-prod:    ## 本番環境にデプロイ
	./scripts/deployment/deploy_production.sh

# === Quick Start Examples ===
quick-example:  ## クイックスタート例を実行
	@echo "🚀 Kaggle Agent クイックスタート例"
	@echo ""
	@echo "1. プロジェクトセットアップ:"
	@echo "   make setup-all"
	@echo ""
	@echo "2. タスク作成例:"
	@echo "   make create-task MODULE=competition_discovery DESCRIPTION='コンペ発見機能の実装'"
	@echo ""
	@echo "3. タスク割り当て例（作成後のtask-idを使用）:"
	@echo "   make assign-task TASK_ID=task-abc123def"
	@echo ""
	@echo "4. 開発サイクル開始:"
	@echo "   make run-cycle TASK_ID=task-abc123def"
	@echo ""
	@echo "5. 進捗監視:"
	@echo "   make monitor TASK_ID=task-abc123def"

demo-workflow:  ## デモワークフローを実行
	@echo "🎬 デモワークフローを開始..."
	@echo "Step 1: プロジェクト構造生成"
	make setup-structure
	@echo "Step 2: マルチエージェント環境セットアップ"  
	make setup-agents
	@echo "Step 3: サンプルタスク作成"
	make create-task MODULE=workflow DESCRIPTION="Workflow engine demo implementation" PRIORITY=high
	@echo "✅ デモワークフロー完了！"
	@echo "次のステップ: 上記で作成されたタスクIDを使用してassign-taskを実行"

# === Documentation Commands ===
docs-serve:     ## ドキュメントサーバーを起動
	@echo "📚 ドキュメントサーバーを起動中..."
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs serve; \
	else \
		echo "mkdocs not found. Installing..."; \
		pip install mkdocs mkdocs-material; \
		mkdocs serve; \
	fi

docs-build:     ## ドキュメントをビルド
	mkdocs build

# === Utility Commands ===
check-deps:     ## 依存関係をチェック
	@echo "🔍 依存関係チェック:"
	@echo "Python version:" && python --version
	@echo "Git version:" && git --version
	@echo "Docker version:" && docker --version 2>/dev/null || echo "Docker not installed"

env-check:      ## 環境設定をチェック
	@echo "🔧 環境設定チェック:"
	@echo "Project root: $(PWD)"
	@echo "Git status:" && git status --porcelain | wc -l | xargs echo "modified files:"
	@echo "Virtual env:" && echo $${VIRTUAL_ENV:-"Not in virtual environment"}

project-info:   ## プロジェクト情報を表示
	@echo "📊 Kaggle Agent Project Information"
	@echo "=================================="
	@echo "Project Name: Kaggle Agent"
	@echo "Version: 1.0.0"
	@echo "Description: Autonomous Kaggle Competition Agent"
	@echo "Architecture: Monolithic-Modular with Multi-Agent Development"
	@echo ""
	@echo "📁 Structure:"
	@echo "├── src/kaggle_agent/    # Main application code"
	@echo "├── tests/               # Test suites"
	@echo "├── docs/                # Documentation"
	@echo "├── orgs/                # Multi-agent workspaces"
	@echo "├── shared/              # Shared resources"
	@echo "└── scripts/             # Development scripts"
	@echo ""
	@echo "🤖 Multi-Agent Organizations:"
	@echo "├── org-01: Core Infrastructure"
	@echo "├── org-02: Application Modules"  
	@echo "├── org-03: Interfaces"
	@echo "└── org-04: Quality Assurance"

# === Organization-specific Commands ===
org-01-status:  ## Core Infrastructure組織の状態
	@echo "🏗️ Core Infrastructure (org-01) Status:"
	@find orgs/org-01 -name ".agent_info.json" -exec echo "Agent: {}" \; -exec cat {} \; 2>/dev/null || echo "org-01 not initialized"

org-02-status:  ## Application Modules組織の状態
	@echo "⚙️ Application Modules (org-02) Status:"
	@find orgs/org-02 -name ".agent_info.json" -exec echo "Agent: {}" \; -exec cat {} \; 2>/dev/null || echo "org-02 not initialized"

org-03-status:  ## Interfaces組織の状態
	@echo "🔌 Interfaces (org-03) Status:"
	@find orgs/org-03 -name ".agent_info.json" -exec echo "Agent: {}" \; -exec cat {} \; 2>/dev/null || echo "org-03 not initialized"

org-04-status:  ## Quality Assurance組織の状態
	@echo "🔍 Quality Assurance (org-04) Status:"
	@find orgs/org-04 -name ".agent_info.json" -exec echo "Agent: {}" \; -exec cat {} \; 2>/dev/null || echo "org-04 not initialized"

all-org-status: ## 全組織の状態を表示
	make org-01-status
	@echo ""
	make org-02-status
	@echo ""
	make org-03-status  
	@echo ""
	make org-04-status

# === Reset Commands ===
reset-hard:     ## ハードリセット（全削除・再生成）
	@echo "⚠️  WARNING: This will delete all agent workspaces and reset the project"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	make worktree-clean
	rm -rf orgs/ shared/ src/ tests/ config/ scripts/ migrations/ deployment/
	rm -f .multi_agent_state.json pyproject.toml
	make setup-all
	@echo "✅ ハードリセット完了"

reset-agents:   ## エージェント環境のみリセット
	@echo "🔄 エージェント環境をリセット中..."
	make worktree-clean
	rm -rf orgs/ shared/ .multi_agent_state.json
	make setup-agents
	@echo "✅ エージェント環境リセット完了" 