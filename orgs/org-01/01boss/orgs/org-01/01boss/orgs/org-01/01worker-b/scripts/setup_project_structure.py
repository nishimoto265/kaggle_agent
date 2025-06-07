#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kaggle Agent Project Structure Generator
自動的にプロジェクト構造を生成し、マルチエージェント開発環境をセットアップする
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import shutil


class ProjectStructureGenerator:
    def __init__(self, spec_file: str = "docs/project_structure_spec.yaml"):
        self.spec_file = spec_file
        self.project_root = Path.cwd()
        self.spec = self._load_spec()

    def _load_spec(self) -> Dict[str, Any]:
        """仕様ファイルを読み込み"""
        spec_path = self.project_root / self.spec_file
        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_full_structure(self):
        """完全なプロジェクト構造を生成"""
        print("🚀 Kaggle Agent プロジェクト構造を生成中...")
        
        # 1. ルートディレクトリ構造
        self._create_root_structure()
        
        # 2. ソースコード構造  
        self._create_src_structure()
        
        # 3. テスト構造
        self._create_test_structure()
        
        # 4. 設定ファイル構造
        self._create_config_structure()
        
        # 5. スクリプト構造
        self._create_scripts_structure()
        
        # 6. マイグレーション構造
        self._create_migrations_structure()
        
        # 7. デプロイメント構造
        self._create_deployment_structure()
        
        # 8. マルチエージェント構造
        self._create_multi_agent_structure()
        
        # 9. 共有リソース構造
        self._create_shared_resources_structure()
        
        # 10. 基本ファイル生成
        self._create_basic_files()
        
        print("✅ プロジェクト構造の生成が完了しました！")

    def _create_root_structure(self):
        """ルートディレクトリ構造を作成"""
        print("📁 ルートディレクトリ構造を作成中...")
        
        # ディレクトリ作成
        root_dirs = self.spec['root_structure']['directories']
        for dir_info in root_dirs:
            dir_path = self.project_root / dir_info['name']
            dir_path.mkdir(exist_ok=True)
            print(f"  ✓ {dir_info['name']}/")

    def _create_src_structure(self):
        """ソースコード構造を作成"""
        print("🐍 ソースコード構造を作成中...")
        
        src_spec = self.spec['src_structure']
        package_name = src_spec['package_name']
        
        # メインパッケージディレクトリ
        src_dir = self.project_root / "src" / package_name
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # __init__.py作成
        (src_dir / "__init__.py").touch()
        
        # コアモジュール
        core_dir = src_dir / "core"
        core_dir.mkdir(exist_ok=True)
        (core_dir / "__init__.py").touch()
        
        for module in src_spec['core_modules']:
            module_dir = core_dir / module['name']
            module_dir.mkdir(exist_ok=True)
            (module_dir / "__init__.py").touch()
            
            for file_name in module['files']:
                self._create_python_file(
                    module_dir / file_name,
                    module['description']
                )
        
        # アプリケーションモジュール
        modules_dir = src_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        (modules_dir / "__init__.py").touch()
        
        for module in src_spec['application_modules']:
            module_dir = modules_dir / module['name']
            module_dir.mkdir(exist_ok=True)
            (module_dir / "__init__.py").touch()
            
            # サブディレクトリ作成
            if 'subdirectories' in module:
                for subdir in module['subdirectories']:
                    subdir_path = module_dir / subdir['name']
                    subdir_path.mkdir(exist_ok=True)
                    (subdir_path / "__init__.py").touch()
                    
                    for file_name in subdir['files']:
                        self._create_python_file(
                            subdir_path / file_name,
                            f"{module['description']} - {subdir['name']}"
                        )
            
            # メインファイル作成
            for file_name in module['files']:
                self._create_python_file(
                    module_dir / file_name,
                    module['description']
                )
        
        # API層
        api_spec = src_spec['api_layer']
        api_dir = src_dir / "api"
        api_dir.mkdir(exist_ok=True)
        (api_dir / "__init__.py").touch()
        
        for file_name in api_spec['files']:
            self._create_python_file(
                api_dir / file_name,
                f"FastAPI {file_name}"
            )
        
        # API サブディレクトリ
        for subdir in api_spec['subdirectories']:
            subdir_path = api_dir / subdir['name']
            subdir_path.mkdir(exist_ok=True)
            (subdir_path / "__init__.py").touch()
            
            for file_name in subdir['files']:
                self._create_python_file(
                    subdir_path / file_name,
                    f"API {subdir['name']} - {file_name}"
                )
        
        # CLI層
        cli_spec = src_spec['cli_layer']
        cli_dir = src_dir / "cli"
        cli_dir.mkdir(exist_ok=True)
        (cli_dir / "__init__.py").touch()
        
        for file_name in cli_spec['files']:
            self._create_python_file(
                cli_dir / file_name,
                f"CLI {file_name}"
            )
        
        # CLI サブディレクトリ
        for subdir in cli_spec['subdirectories']:
            subdir_path = cli_dir / subdir['name']
            subdir_path.mkdir(exist_ok=True)
            (subdir_path / "__init__.py").touch()
            
            for file_name in subdir['files']:
                self._create_python_file(
                    subdir_path / file_name,
                    f"CLI {subdir['name']} - {file_name}"
                )
        
        # ユーティリティ
        utils_dir = src_dir / "utils"
        utils_dir.mkdir(exist_ok=True)
        (utils_dir / "__init__.py").touch()
        
        for file_name in src_spec['utilities']['files']:
            self._create_python_file(
                utils_dir / file_name,
                f"Utility - {file_name}"
            )

    def _create_test_structure(self):
        """テスト構造を作成"""
        print("🧪 テスト構造を作成中...")
        
        test_spec = self.spec['test_structure']
        tests_dir = self.project_root / "tests"
        
        # conftest.py作成
        conftest_content = '''# -*- coding: utf-8 -*-
"""
pytest設定ファイル
"""
import pytest
import asyncio
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def project_root():
    """プロジェクトルートディレクトリ"""
    return Path(__file__).parent.parent
'''
        (tests_dir / "conftest.py").write_text(conftest_content, encoding='utf-8')
        
        # フィクスチャディレクトリ
        fixtures_dir = tests_dir / "fixtures"
        fixtures_dir.mkdir(exist_ok=True)
        (fixtures_dir / "__init__.py").touch()
        
        fixture_files = ["database.py", "api_responses.py", "sample_data.py"]
        for file_name in fixture_files:
            self._create_python_file(
                fixtures_dir / file_name,
                f"Test fixture - {file_name}"
            )
        
        # テストカテゴリ
        for category in test_spec['categories']:
            category_dir = tests_dir / category['name']
            category_dir.mkdir(exist_ok=True)
            (category_dir / "__init__.py").touch()
            
            if 'subdirectories' in category:
                for subdir in category['subdirectories']:
                    subdir_path = category_dir / subdir
                    subdir_path.mkdir(exist_ok=True)
                    (subdir_path / "__init__.py").touch()
            
            if 'files' in category:
                for file_name in category['files']:
                    self._create_test_file(
                        category_dir / file_name,
                        category['description']
                    )

    def _create_multi_agent_structure(self):
        """マルチエージェント構造を作成"""
        print("🤖 マルチエージェント構造を作成中...")
        
        orgs_dir = self.project_root / "orgs"
        orgs_dir.mkdir(exist_ok=True)
        
        # 4つの組織を作成
        organizations = [
            {"id": "01", "name": "core-infrastructure", "description": "Core Infrastructure"},
            {"id": "02", "name": "application-modules", "description": "Application Modules"},
            {"id": "03", "name": "interfaces", "description": "Interfaces"},
            {"id": "04", "name": "quality-assurance", "description": "Quality Assurance"}
        ]
        
        for org in organizations:
            org_dir = orgs_dir / f"org-{org['id']}"
            org_dir.mkdir(exist_ok=True)
            
            # Boss + 3 Workers
            agents = [
                {"role": "boss", "suffix": "boss", "focus": "評価・統合"},
                {"role": "worker", "suffix": "worker-a", "focus": "パフォーマンス重視"},
                {"role": "worker", "suffix": "worker-b", "focus": "保守性重視"},
                {"role": "worker", "suffix": "worker-c", "focus": "拡張性重視"}
            ]
            
            for agent in agents:
                agent_dir = org_dir / f"{org['id']}{agent['suffix']}"
                agent_dir.mkdir(exist_ok=True)
                
                # CLAUDE.md作成
                self._create_claude_md(agent_dir, org, agent)
                
                # current_task.md作成
                self._create_current_task_md(agent_dir, org, agent)
                
                # ワークスペース構造
                if agent['role'] == 'boss':
                    # Bossは評価用ディレクトリ
                    (agent_dir / "evaluation").mkdir(exist_ok=True)
                    (agent_dir / "reports").mkdir(exist_ok=True)
                else:
                    # Workerは実装用ディレクトリ
                    (agent_dir / "src").mkdir(exist_ok=True)
                    (agent_dir / "tests").mkdir(exist_ok=True)
                    (agent_dir / "docs").mkdir(exist_ok=True)

    def _create_shared_resources_structure(self):
        """共有リソース構造を作成"""
        print("📚 共有リソース構造を作成中...")
        
        shared_dir = self.project_root / "shared"
        shared_dir.mkdir(exist_ok=True)
        
        # プロンプト管理システム
        prompts_dir = shared_dir / "prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        # テンプレートディレクトリ
        templates_dir = prompts_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # 役割別プロンプトテンプレート
        roles = ["boss", "worker_a", "worker_b", "worker_c"]
        for role in roles:
            role_dir = templates_dir / role
            role_dir.mkdir(exist_ok=True)
            
            # 基本プロンプトファイル
            self._create_prompt_template(role_dir / "base_prompt.md", role)
            
            if role == "boss":
                self._create_prompt_template(role_dir / "evaluation_prompt.md", role)
                self._create_prompt_template(role_dir / "integration_prompt.md", role)
            else:
                self._create_prompt_template(role_dir / "implementation_prompt.md", role)
                self._create_prompt_template(role_dir / "tdd_prompt.md", role)
            
            # コンテキスト変数定義
            context_vars = {
                'task_info': 'string',
                'progress_status': 'object',
                'evaluation_criteria': 'list',
                'constraints': 'object',
                'reference_files': 'list'
            }
            
            context_file = role_dir / "context_variables.yaml"
            with open(context_file, 'w', encoding='utf-8') as f:
                yaml.dump(context_vars, f, default_flow_style=False, allow_unicode=True)
        
        # プロンプト生成器
        generators_dir = prompts_dir / "generators"
        generators_dir.mkdir(exist_ok=True)
        
        generator_files = [
            "prompt_builder.py",
            "context_injector.py", 
            "template_processor.py"
        ]
        
        for file_name in generator_files:
            self._create_python_file(
                generators_dir / file_name,
                f"Prompt generator - {file_name}"
            )
        
        # その他共有リソース
        shared_subdirs = [
            "instructions", "evaluation_criteria", "templates", 
            "specifications", "tech_stack"
        ]
        
        for subdir in shared_subdirs:
            (shared_dir / subdir).mkdir(exist_ok=True)

    def _create_claude_md(self, agent_dir: Path, org: Dict, agent: Dict):
        """CLAUDE.mdファイルを作成"""
        org_id = org['id']
        agent_suffix = agent['suffix']
        role = agent['role']
        focus = agent['focus']
        
        claude_content = f"""# {org_id}{agent_suffix} Agent Instructions

## 🤖 Agent Identity
- **Organization**: {org['description']}
- **Agent ID**: {org_id}{agent_suffix}
- **Role**: {role.title()}
- **Focus**: {focus}

## 📋 Core Instructions

あなたは **{org['description']}** 組織の **{focus}** を専門とする{role}エージェントです。

### 🎯 Primary Objectives
"""

        if role == 'boss':
            claude_content += """
- Worker実装の品質評価
- 最適実装の選択判断
- メインブランチへの統合管理
- 品質基準の維持

### 📖 Required Reading
以下のファイルを必ず最初に読んでください：

@shared/instructions/roles/boss.md
@shared/evaluation_criteria/code_quality.md
@shared/evaluation_criteria/test_coverage.md
@shared/evaluation_criteria/performance.md
@shared/evaluation_criteria/maintainability.md
@shared/evaluation_criteria/documentation.md
@shared/prompts/templates/boss/base_prompt.md
@shared/prompts/templates/boss/evaluation_prompt.md
@shared/prompts/templates/boss/integration_prompt.md

### 🔍 Evaluation Process
1. 3つのWorker実装を並列評価
2. 多軸評価基準の適用
3. 最適実装の選択・統合判断
4. 品質ゲートの確認

### 📊 Evaluation Criteria
- コード品質: 25%
- テストカバレッジ: 25% 
- パフォーマンス: 25%
- 保守性: 15%
- ドキュメント: 10%

### ✅ Quality Gates
- 総合スコア70点以上
- テストカバレッジ90%以上
- パフォーマンス要件達成
- セキュリティ要件遵守
"""
        else:
            claude_content += f"""
- {focus}の実装
- TDD手法による開発
- 高品質なコード・テスト・ドキュメントの作成

### 📖 Required Reading
以下のファイルを必ず最初に読んでください：

@shared/instructions/roles/worker.md
@shared/instructions/development_guidelines.md
@shared/prompts/templates/{agent['suffix'].replace('-', '_')}/base_prompt.md
@shared/prompts/templates/{agent['suffix'].replace('-', '_')}/implementation_prompt.md
@shared/prompts/templates/{agent['suffix'].replace('-', '_')}/tdd_prompt.md
@current_task.md

### 🛠️ Development Process
1. 要件分析・理解
2. テストケース設計
3. テストコード実装
4. TDD実装サイクル（Red-Green-Refactor）
5. ドキュメント作成

### 🎯 Focus Areas
"""
            
            if 'worker-a' in agent_suffix:
                claude_content += """
- アルゴリズムの最適化
- 並列処理・非同期処理の活用
- メモリ効率の改善
- 実行速度の向上
"""
            elif 'worker-b' in agent_suffix:
                claude_content += """
- クリーンコードの実践
- 設計パターンの適用
- 可読性の向上
- 保守性の確保
"""
            elif 'worker-c' in agent_suffix:
                claude_content += """
- モジュール設計
- インターフェース定義
- プラグイン機構
- 将来拡張への対応
"""

        claude_content += f"""

## 📁 Workspace Structure
```
{agent_dir.name}/
├── CLAUDE.md              # この指示書
├── current_task.md        # 現在のタスク情報
"""

        if role == 'boss':
            claude_content += """├── evaluation/            # 評価レポート
├── reports/               # 統合判断レポート
"""
        else:
            claude_content += """├── src/                   # 実装コード
├── tests/                 # テストコード
├── docs/                  # ドキュメント
"""

        claude_content += """└── [その他成果物]
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
"""
        
        claude_file = agent_dir / "CLAUDE.md"
        claude_file.write_text(claude_content, encoding='utf-8')

    def _create_current_task_md(self, agent_dir: Path, org: Dict, agent: Dict):
        """current_task.mdファイルを作成"""
        task_content = f"""# Current Task - {org['id']}{agent['suffix']}

## 📋 Task Information
- **Status**: Waiting for assignment
- **Priority**: Medium
- **Estimated Time**: TBD
- **Dependencies**: None

## 🎯 Task Description
現在、タスクは割り当てられていません。
新しいタスクが割り当てられると、この文書が更新されます。

## 📊 Progress Tracking
- [ ] 要件分析・理解
- [ ] テストケース設計  
- [ ] テストコード実装
- [ ] 実装（TDD）
- [ ] ドキュメント作成
- [ ] 品質確認

## 🔗 Related Files
- Task specification: TBD
- Reference implementation: TBD
- Test requirements: TBD

## 📝 Notes
タスク開始前に必要な情報やファイルを確認してください。

---
*Last updated: {os.path.basename(__file__)} - Auto-generated*
"""
        
        task_file = agent_dir / "current_task.md"
        task_file.write_text(task_content, encoding='utf-8')

    def _create_prompt_template(self, file_path: Path, role: str):
        """プロンプトテンプレートファイルを作成"""
        file_name = file_path.name
        
        content = f"""# {role.title()} {file_name.replace('_', ' ').replace('.md', '').title()}

## Template Variables
- {{task_info}} - 現在のタスク情報
- {{progress_status}} - 進捗状況
- {{evaluation_criteria}} - 評価基準
- {{constraints}} - 制約条件
- {{reference_files}} - 参照ファイル

## Template Content
このファイルは{role}エージェント用の{file_name}テンプレートです。
具体的なプロンプト内容は後で実装されます。

---
*Template file - Auto-generated*
"""
        
        file_path.write_text(content, encoding='utf-8')

    def _create_python_file(self, file_path: Path, description: str):
        """Pythonファイルを作成"""
        content = f'''# -*- coding: utf-8 -*-
"""
{description}
"""

# TODO: Implement {file_path.stem}
'''
        file_path.write_text(content, encoding='utf-8')

    def _create_test_file(self, file_path: Path, description: str):
        """テストファイルを作成"""
        module_name = file_path.stem.replace('test_', '')
        content = f'''# -*- coding: utf-8 -*-
"""
Tests for {module_name}
{description}
"""

import pytest


class Test{module_name.title().replace('_', '')}:
    """Test class for {module_name}"""
    
    def test_placeholder(self):
        """Placeholder test"""
        # TODO: Implement actual tests
        assert True
'''
        file_path.write_text(content, encoding='utf-8')

    def _create_config_structure(self):
        """設定ファイル構造を作成"""
        print("⚙️ 設定ファイル構造を作成中...")
        
        config_dir = self.project_root / "config"
        
        # 環境別設定ファイル
        environments = ["default", "development", "staging", "production", "testing"]
        for env in environments:
            config_file = config_dir / f"{env}.yaml"
            config_content = {
                'environment': env,
                'debug': env in ['development', 'testing'],
                'database': {
                    'url': f'postgresql://localhost/kaggle_agent_{env}'
                },
                'redis': {
                    'url': 'redis://localhost:6379/0'
                }
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_content, f, default_flow_style=False)

    def _create_scripts_structure(self):
        """スクリプト構造を作成"""
        print("📜 スクリプト構造を作成中...")
        
        scripts_spec = self.spec['scripts_structure']
        scripts_dir = self.project_root / "scripts"
        
        for category in scripts_spec['categories']:
            category_dir = scripts_dir / category['name']
            category_dir.mkdir(exist_ok=True)
            
            for file_info in category['files']:
                file_path = category_dir / file_info['name']
                
                if file_info.get('executable', False):
                    # Shell script
                    content = f"""#!/bin/bash
# {category['description']} - {file_info['name']}

echo "TODO: Implement {file_info['name']}"
"""
                    file_path.write_text(content, encoding='utf-8')
                    file_path.chmod(0o755)
                else:
                    # Python script
                    self._create_python_file(file_path, f"{category['description']} - {file_info['name']}")

    def _create_migrations_structure(self):
        """マイグレーション構造を作成"""
        print("🗄️ マイグレーション構造を作成中...")
        
        migrations_dir = self.project_root / "migrations"
        
        # Alembic設定
        alembic_dir = migrations_dir / "alembic"
        alembic_dir.mkdir(exist_ok=True)
        
        versions_dir = alembic_dir / "versions"
        versions_dir.mkdir(exist_ok=True)

    def _create_deployment_structure(self):
        """デプロイメント構造を作成"""
        print("🚀 デプロイメント構造を作成中...")
        
        deployment_dir = self.project_root / "deployment"
        
        # Docker設定
        docker_dir = deployment_dir / "docker"
        docker_dir.mkdir(exist_ok=True)

    def _create_basic_files(self):
        """基本ファイルを作成"""
        print("📄 基本ファイルを作成中...")
        
        # pyproject.toml
        pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kaggle-agent"
version = "1.0.0"
description = "Autonomous Kaggle Competition Agent"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.104.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "redis>=5.0.0",
    "boto3>=1.29.0",
    "prefect>=2.14.0",
    "anthropic>=0.7.0",
    "kaggle>=1.5.0",
    "pydantic>=2.5.0",
    "click>=8.1.0",
    "uvicorn>=0.24.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
]

[project.scripts]
kaggle-agent = "kaggle_agent.cli.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ['py312']

[tool.isort]
profile = "black"
src_paths = ["src", "tests"]
'''
        
        (self.project_root / "pyproject.toml").write_text(pyproject_content, encoding='utf-8')
        
        # .env.example
        env_example = '''# Kaggle Agent Environment Variables

# API Keys
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
ANTHROPIC_API_KEY=your_claude_api_key
GOOGLE_DEEP_RESEARCH_API_KEY=your_deep_research_key

# Database
DATABASE_URL=postgresql://localhost/kaggle_agent
REDIS_URL=redis://localhost:6379/0

# GPU Management
SALAD_CLOUD_API_KEY=your_salad_api_key

# Notifications
SLACK_BOT_TOKEN=your_slack_token
DISCORD_BOT_TOKEN=your_discord_token

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# Monitoring
PROMETHEUS_GATEWAY=http://localhost:9091
'''
        
        (self.project_root / ".env.example").write_text(env_example, encoding='utf-8')

    def move_existing_docs(self):
        """既存のドキュメントを適切な位置に移動"""
        print("📚 既存ドキュメントを整理中...")
        
        docs_dir = self.project_root / "docs"
        
        # requirements.mdを適切な位置に保持
        requirements_file = docs_dir / "requirements.md"
        if requirements_file.exists():
            print("  ✓ requirements.md は既に適切な位置にあります")
        
        # その他のファイルも docs/ 内に保持
        existing_docs = [
            "project_structure.md",
            "project_structure_spec.yaml"
        ]
        
        for doc_file in existing_docs:
            doc_path = docs_dir / doc_file
            if doc_path.exists():
                print(f"  ✓ {doc_file} は既に適切な位置にあります")


def main():
    parser = argparse.ArgumentParser(description="Kaggle Agent Project Structure Generator")
    parser.add_argument(
        "--spec-file", 
        default="docs/project_structure_spec.yaml",
        help="Project structure specification file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating"
    )
    
    args = parser.parse_args()
    
    generator = ProjectStructureGenerator(args.spec_file)
    
    if args.dry_run:
        print("🔍 Dry run mode - showing what would be created:")
        # TODO: Implement dry run logic
        return
    
    try:
        generator.generate_full_structure()
        generator.move_existing_docs()
        
        print("\n🎉 セットアップ完了！")
        print("\n次のステップ:")
        print("1. cd src/kaggle_agent && python -m pip install -e .[dev]")
        print("2. git worktree を使用してマルチエージェント環境をセットアップ")
        print("3. shared/prompts/ でプロンプトテンプレートを充実")
        print("4. 最初のタスクをエージェントに割り当て")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main() 