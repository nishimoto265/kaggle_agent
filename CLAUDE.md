# CLAUDE.md

This file provides essential guidance to Claude Code when working with this Kaggle Agent repository.

## Quick Project Overview

Autonomous Kaggle competition system with multi-agent development architecture.
- **Language**: Python 3.12
- **Architecture**: Monolithic-Modular with Git worktree multi-agent development
- **Target Budget**: $0.15/hour, 24h first submission

## Essential Commands

```bash
# Development
make install          # Install dependencies
make dev             # Start dev environment
make test-cov        # Run tests with coverage
make lint            # Code quality checks
make format          # Format code

# Multi-Agent Development
./scripts/create_org01_parallel_session.sh  # Start tmux parallel development
git worktree list    # Check active worktrees
```

## Core Files & Utilities

### Configuration
- `config/default.yaml` - Base configuration
- `config/development.yaml` - Dev overrides
- `.env.example` - Environment template

### Key Utilities
- `scripts/setup/setup_database.py` - Initialize DB
- `scripts/maintenance/health_check.py` - System health
- `scripts/utilities/config_validator.py` - Config validation

### Module Structure Pattern
```
modules/{module_name}/
├── service.py      # Main service class
├── models.py       # Data models
├── tasks.py        # Prefect workflow tasks
└── {specific}.py   # Module implementations
```

## Code Style Guidelines

### Python Standards
- **Formatter**: black (line length 88)
- **Import sorting**: isort
- **Linting**: flake8 + mypy
- **Type hints**: Required for all functions
- **Docstrings**: Google style

### Multi-Agent Development Rules
- **AI出力変動活用**: 全Worker(1,2,3)に同一プロンプト配布
- **自然な多様性**: AIの確率的性質により異なる実装が自動生成
- **Boss統合評価**: 3実装の客観的評価・最適統合
- **品質基準**: 70+ score, 90%+ test coverage

## Testing Procedures

```bash
# Test execution
pytest                           # All tests
pytest tests/unit/              # Unit tests only
pytest --cov=kaggle_agent       # With coverage
pytest -k "test_name"           # Specific test

# Coverage requirements
# Unit tests: >90% coverage
# Integration: API + DB tests
# Multi-agent: Each worker tests independently
```

## Repository Etiquette

### Git Worktree Multi-Agent System
```bash
# Branch naming
main                    # Production branch
orgs/org-01/01boss     # Boss evaluation branch
orgs/org-01/01worker-a # Worker A implementation
orgs/org-01/01worker-b # Worker B implementation
orgs/org-01/01worker-c # Worker C implementation
```

### Merge/Rebase Rules
- **Workers**: Always rebase from boss branch
- **Boss**: Merge best worker solution + improvements
- **Integration**: Final boss merges to main
- **No direct main commits**: Always through multi-agent process

## Development Environment

### Python Setup
```bash
# Use pyenv for Python version management
pyenv install 3.12.0
pyenv local 3.12.0

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

### Required System Dependencies
- **Docker & Docker Compose**: Local infrastructure
- **PostgreSQL**: Database
- **Redis**: Event bus and caching
- **tmux**: Parallel development sessions

### Supported Compilers
- **Python**: 3.12+ (pyenv managed)
- **Rust**: 1.81+ (for cctx tools) - use `rustup update`
- **Node.js**: 18+ (for potential frontend tools)

## Project-Specific Warnings

### Known Issues
- **cctx installation**: Requires Rust 1.81+, use `./scripts/file_context.sh` as alternative
- **GPU costs**: Automatic termination at $0.15/hour threshold
- **API rate limits**: Kaggle (200/h), Claude (1000/h), Research (100/h)
- **tmux session conflicts**: Only one org development session at a time

### Performance Gotchas
- **Large dataset downloads**: Use streaming with progress bars
- **Model training**: Implement early stopping and checkpointing
- **Database queries**: Always use connection pooling
- **Redis pub/sub**: Use connection pools for high-frequency events

## 🤖 全Agent共通指示

### 必須ルール
- **指示厳守**: 指示されたことのみを実行する
- **テスト保護**: 既存テストを削除・破壊してはいけない
- **チェックリスト**: 実装完了後、必ずチェックリストを埋める
- **ドキュメント同期**: 実装変更時は関連ドキュメントも更新する
- **エラー隠蔽禁止**: エラーを握りつぶさず、適切にログ出力・例外処理する
- **設定外部化**: ハードコーディング禁止、config/環境変数を使用する
- **機密情報保護**: APIキー・パスワードをコードに直接書かない
- **提出前自己確認**: 動作確認・静的解析・テストを実行してから提出する
- **アーキテクチャ遵守**: 定義済みのディレクトリ構造・設計パターンに従う
- **モジュール再利用**: 新規作成前に既存モジュール・ユーティリティの活用を検討する

## Claude AI Specific Notes

### Multi-Agent Development Protocol
1. **Always check current Git worktree**: `git worktree list`
2. **📋 MUST READ Role-Specific Instructions**:
   - **Boss Agent**: `docs/boss_instructions.md` - 統括・評価・統合指示書
   - **Worker Agents**: `docs/worker_instructions.md` - 実装専門指示書（A/B/C統合版）
3. **Identify worker role**: Boss evaluates/統合, Workers implement (同一プロンプト・AI変動活用)
4. **Follow unified task checklist**: Check current worktree's `CLAUDE.md` for specific instructions
5. **Boss triggers integration**: Wait for all 3 workers to complete
6. **Final integration to main**: Only through Final Boss process

### Code Generation Preferences
- **Favor composition over inheritance**
- **Use dependency injection patterns**
- **Implement comprehensive error handling**
- **Include type hints and docstrings**
- **Write tests alongside implementation**

### Documentation Requirements
- **README updates**: For new modules
- **API documentation**: FastAPI auto-generated
- **Multi-agent logs**: Track decision rationale
- **Performance metrics**: Include benchmarks

## Emergency Procedures

```bash
# System health check
python scripts/maintenance/health_check.py

# Stop all GPU instances (cost emergency)
python scripts/utilities/emergency_shutdown.py

# Reset multi-agent development
./scripts/reset_multiagent_workspace.sh

# Database recovery
python scripts/maintenance/database_recovery.py
```

## External Dependencies

- **Kaggle API**: Competition data, submissions
- **Claude Code API**: Code generation and review
- **SaladCloud**: GPU provisioning
- **Weights & Biases**: Experiment tracking
- **Slack/Discord**: Human-in-the-loop notifications

---

## 📚 Technical Documentation Reference

### 🏗️ Core System Design
- **[`docs/requirements.md`](docs/requirements.md)** - Functional requirements, user stories, acceptance criteria (45KB, 918 lines)
- **[`docs/architecture_design.md`](docs/architecture_design.md)** - System architecture, component design, data flows (15KB, 584 lines)
- **[`docs/project_structure.md`](docs/project_structure.md)** - Complete directory structure, file organization (56KB, 1368 lines)

### 🤖 Multi-Agent Development System
- **[`docs/worker_instructions.md`](docs/worker_instructions.md)** - Worker実装指示書、チェックリスト駆動ワークフロー
- **[`docs/tmux_parallel_development_spec.md`](docs/tmux_parallel_development_spec.md)** - tmux session management, parallel workspace setup (32KB, 857 lines)
- **[`docs/multi_agent_evaluation_process.md`](docs/multi_agent_evaluation_process.md)** - Boss evaluation criteria, integration workflow (12KB, 478 lines)

### 🛠️ Implementation Guides
- **[`docs/boss_instructions.md`](docs/boss_instructions.md)** - ⚠️ **CRITICAL**: Boss Agent専用指示書 (統括・評価・統合)
- **[`docs/worker_instructions.md`](docs/worker_instructions.md)** - ⚠️ **CRITICAL**: Worker Agent統合指示書 (A/B/C全対応)
- **[`docs/implementation_best_practices.md`](docs/implementation_best_practices.md)** - Development workflows, coding standards, quality guidelines (16KB, 582 lines)
- **[`docs/database_design.md`](docs/database_design.md)** - Database schema, models, migration strategies (22KB, 639 lines)
- **[`docs/api_integration_design.md`](docs/api_integration_design.md)** - External API integrations, rate limiting, error handling (17KB, 686 lines)

### 📖 Quick Navigation Guide
```
For...                          Read...
├─ "📋 I'm Boss Agent"         → boss_instructions.md (⚠️ FIRST!)
├─ "📋 I'm Worker Agent"       → worker_instructions.md (⚠️ FIRST!)
├─ "Where does X file go?"     → project_structure.md
├─ "How does the system work?" → architecture_design.md
├─ "What should I build?"      → requirements.md
├─ "How to develop properly?"  → implementation_best_practices.md
├─ "How to use multi-agent?"   → worker_instructions.md + boss_instructions.md
├─ "How to run parallel dev?"  → tmux_parallel_development_spec.md
├─ "How does evaluation work?" → multi_agent_evaluation_process.md
├─ "How to design database?"   → database_design.md
└─ "How to integrate APIs?"    → api_integration_design.md
```

### 🎯 Document Responsibilities
- **Structure Definition**: Only `project_structure.md` defines directories/files
- **Process Definition**: `worker_instructions.md` と `boss_instructions.md` がワークフローを定義
- **Architecture Definition**: Only `architecture_design.md` defines system design
- **All others**: Reference these 3 core docs and focus on their specialty

