#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Git Worktree Environment Setup
各エージェント用のgit worktreeワークスペースをセットアップ
"""

import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json


class MultiAgentWorktreeSetup:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.orgs_dir = self.project_root / "orgs"
        
        self.organizations = [
            {
                "id": "01",
                "name": "core-infrastructure", 
                "description": "Core Infrastructure",
                "modules": ["workflow", "database", "cache", "storage", "messaging", "monitoring", "security"]
            },
            {
                "id": "02", 
                "name": "application-modules",
                "description": "Application Modules", 
                "modules": ["competition_discovery", "research", "code_generation", "gpu_management", "training", "submission", "human_loop"]
            },
            {
                "id": "03",
                "name": "interfaces",
                "description": "Interfaces",
                "modules": ["api", "cli", "ui", "webhooks"]
            },
            {
                "id": "04",
                "name": "quality-assurance", 
                "description": "Quality Assurance",
                "modules": ["testing", "monitoring", "security_audit", "performance"]
            }
        ]

    def setup_all(self):
        """全マルチエージェント環境をセットアップ"""
        print("🚀 マルチエージェント Git Worktree 環境をセットアップ中...")
        
        # 1. Git初期化確認
        self._ensure_git_repo()
        
        # 2. メインブランチの準備
        self._setup_main_branch()
        
        # 3. 各組織のブランチとworktreeを作成
        for org in self.organizations:
            self._setup_organization_worktrees(org)
        
        # 4. 共有リソースの初期化
        self._initialize_shared_resources()
        
        # 5. 状態ファイルの作成
        self._create_state_file()
        
        print("✅ マルチエージェント環境のセットアップが完了しました！")
        print("\n📋 作成されたworktree:")
        self._list_worktrees()

    def _ensure_git_repo(self):
        """Gitリポジトリの初期化を確認"""
        if not (self.project_root / ".git").exists():
            print("📁 Gitリポジトリを初期化中...")
            subprocess.run(["git", "init"], cwd=self.project_root, check=True)
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.project_root, check=True)

    def _setup_main_branch(self):
        """メインブランチの準備"""
        print("🌳 メインブランチを準備中...")
        
        # 現在のブランチ名を取得
        result = subprocess.run(
            ["git", "branch", "--show-current"], 
            cwd=self.project_root, 
            capture_output=True, 
            text=True
        )
        current_branch = result.stdout.strip()
        
        if current_branch != "main":
            # mainブランチに切り替え（作成）
            subprocess.run(["git", "checkout", "-b", "main"], cwd=self.project_root, check=True)

    def _setup_organization_worktrees(self, org: Dict[str, Any]):
        """組織のworktreeをセットアップ"""
        org_id = org["id"]
        org_name = org["name"]
        
        print(f"🏢 組織 {org_id} ({org_name}) のworktreeを作成中...")
        
        agents = [
            {"suffix": "boss", "role": "boss", "focus": "評価・統合"},
            {"suffix": "worker-a", "role": "worker", "focus": "パフォーマンス重視"},
            {"suffix": "worker-b", "role": "worker", "focus": "保守性重視"},
            {"suffix": "worker-c", "role": "worker", "focus": "拡張性重視"}
        ]
        
        for agent in agents:
            self._create_agent_worktree(org, agent)

    def _create_agent_worktree(self, org: Dict[str, Any], agent: Dict[str, str]):
        """個別エージェントのworktreeを作成"""
        org_id = org["id"]
        agent_suffix = agent["suffix"]
        agent_id = f"{org_id}{agent_suffix}"
        
        # ブランチ名とworktreeパス
        branch_name = f"agent/{agent_id}"
        worktree_path = self.orgs_dir / f"org-{org_id}" / agent_id
        
        print(f"  🤖 エージェント {agent_id} のworktreeを作成...")
        
        try:
            # ブランチが存在しない場合は作成
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
                cwd=self.project_root,
                check=False
            )
            
            if subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
                cwd=self.project_root
            ).returncode != 0:
                # ブランチを作成
                subprocess.run(
                    ["git", "branch", branch_name, "main"],
                    cwd=self.project_root,
                    check=True
                )
            
            # worktreeが既に存在する場合は削除
            if worktree_path.exists():
                subprocess.run(
                    ["git", "worktree", "remove", str(worktree_path)],
                    cwd=self.project_root,
                    check=False
                )
            
            # worktreeを作成
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch_name],
                cwd=self.project_root,
                check=True
            )
            
            # エージェント固有の初期化
            self._initialize_agent_workspace(worktree_path, org, agent)
            
            print(f"    ✓ {agent_id} worktree created at {worktree_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Failed to create worktree for {agent_id}: {e}")

    def _initialize_agent_workspace(self, worktree_path: Path, org: Dict[str, Any], agent: Dict[str, str]):
        """エージェントワークスペースの初期化"""
        agent_id = f"{org['id']}{agent['suffix']}"
        
        # .gitignoreを作成
        gitignore_content = """# Agent workspace specific
.agent_cache/
.temp/
*.log
.DS_Store

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        
        gitignore_file = worktree_path / ".gitignore"
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        
        # エージェント情報ファイル
        agent_info = {
            "agent_id": agent_id,
            "organization": org,
            "role": agent["role"],
            "focus": agent["focus"],
            "created_at": str(Path(__file__).stat().st_mtime),
            "status": "initialized",
            "current_task": None,
            "worktree_path": str(worktree_path),
            "branch_name": f"agent/{agent_id}"
        }
        
        info_file = worktree_path / ".agent_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(agent_info, f, indent=2, ensure_ascii=False)

    def _initialize_shared_resources(self):
        """共有リソースの初期化"""
        print("📚 共有リソースを初期化中...")
        
        shared_dir = self.project_root / "shared"
        
        # 技術仕様ファイルの作成
        specs_dir = shared_dir / "specifications" / "kaggle_agent"
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        # 基本仕様ファイル
        basic_specs = [
            "workflow_spec.md",
            "database_spec.md", 
            "api_spec.md",
            "security_spec.md"
        ]
        
        for spec_file in basic_specs:
            spec_path = specs_dir / spec_file
            if not spec_path.exists():
                spec_content = f"""# {spec_file.replace('_', ' ').replace('.md', '').title()}

## Overview
This is the specification for {spec_file.replace('_spec.md', '').replace('_', ' ')}.

## TODO
- Define detailed specifications
- Add technical requirements
- Include API definitions
- Add examples

---
*Auto-generated specification file*
"""
                spec_path.write_text(spec_content, encoding='utf-8')
        
        # 役割定義ファイル
        roles_dir = shared_dir / "instructions" / "roles"
        roles_dir.mkdir(parents=True, exist_ok=True)
        
        # Boss役割定義
        boss_role_content = """# Boss Agent Role Definition

## 🎯 Primary Responsibilities
- Worker実装の品質評価
- 最適実装の選択判断
- メインブランチへの統合管理
- 品質基準の維持

## 📊 Evaluation Framework
### Multi-Axis Evaluation
- **Code Quality (25%)**: 複雑度、保守性、可読性、標準準拠
- **Test Coverage (25%)**: 行・分岐・関数カバレッジ
- **Performance (25%)**: 実行時間、メモリ使用量、スケーラビリティ
- **Maintainability (15%)**: モジュール性、文書化、エラーハンドリング
- **Documentation (10%)**: 完全性、明確性、例示

### Quality Gates
- 総合スコア70点以上で統合可能
- テストカバレッジ90%以上必須
- パフォーマンス要件達成必須
- セキュリティ要件遵守必須

## 🔄 Evaluation Process
1. 3つのWorker実装を並列評価
2. 各評価軸でのスコアリング
3. 統合判断レポートの作成
4. 最適実装の選択・統合実行

## 📋 Evaluation Report Template
```markdown
# Evaluation Report - [Task Name]

## Summary
- Best Implementation: Worker-X
- Overall Score: XX/100
- Integration Decision: [APPROVE/REJECT/REVISE]

## Worker Comparison
| Criteria | Worker-A | Worker-B | Worker-C |
|----------|----------|----------|----------|
| Code Quality | XX/25 | XX/25 | XX/25 |
| Test Coverage | XX/25 | XX/25 | XX/25 |
| Performance | XX/25 | XX/25 | XX/25 |
| Maintainability | XX/15 | XX/15 | XX/15 |
| Documentation | XX/10 | XX/10 | XX/10 |
| **Total** | **XX/100** | **XX/100** | **XX/100** |

## Detailed Analysis
[詳細な分析・コメント]

## Integration Decision
[統合判断の理由]
```
"""
        
        (roles_dir / "boss.md").write_text(boss_role_content, encoding='utf-8')
        
        # Worker役割定義
        worker_role_content = """# Worker Agent Role Definition

## 🎯 Primary Responsibilities  
- 割り当てられたモジュールの実装
- TDD手法による開発
- 高品質なコード・テスト・ドキュメントの作成
- 継続的な改善・最適化

## 🛠️ Development Process
1. **要件分析・理解**: タスクの詳細分析
2. **テストケース設計**: 包括的なテストケースの設計
3. **テストコード実装**: pytest形式でのテスト実装
4. **TDD実装サイクル**: Red-Green-Refactor サイクル
5. **ドキュメント作成**: 実装詳細・使用例の文書化

## 🎯 Focus Area Specialization

### Worker-A: Performance Focus
- アルゴリズムの最適化
- 並列処理・非同期処理の活用
- メモリ効率の改善
- 実行速度の向上
- プロファイリング・ベンチマーク

### Worker-B: Maintainability Focus  
- クリーンコードの実践
- 設計パターンの適用
- 可読性の向上
- 保守性の確保
- リファクタリング技術

### Worker-C: Extensibility Focus
- モジュール設計
- インターフェース定義
- プラグイン機構
- 将来拡張への対応
- アーキテクチャ設計

## 📋 Deliverables
- 実装コード (src/)
- テストコード (tests/)
- ドキュメント (docs/)
- 実装報告書 (implementation_report.md)

## ✅ Quality Standards
- テストカバレッジ90%以上
- Lint警告0件
- 型ヒント完備
- ドキュメント文字列完備
- セキュリティ要件遵守
"""
        
        (roles_dir / "worker.md").write_text(worker_role_content, encoding='utf-8')

    def _create_state_file(self):
        """マルチエージェント環境の状態ファイルを作成"""
        state = {
            "version": "1.0.0",
            "created_at": str(Path(__file__).stat().st_mtime),
            "organizations": self.organizations,
            "agents": [],
            "active_tasks": [],
            "completed_tasks": []
        }
        
        # 各エージェントの情報を収集
        for org in self.organizations:
            org_id = org["id"]
            org_dir = self.orgs_dir / f"org-{org_id}"
            
            if org_dir.exists():
                for agent_dir in org_dir.iterdir():
                    if agent_dir.is_dir():
                        info_file = agent_dir / ".agent_info.json"
                        if info_file.exists():
                            with open(info_file, 'r', encoding='utf-8') as f:
                                agent_info = json.load(f)
                                state["agents"].append(agent_info)
        
        state_file = self.project_root / ".multi_agent_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def _list_worktrees(self):
        """作成されたworktreeの一覧を表示"""
        result = subprocess.run(
            ["git", "worktree", "list"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if 'orgs/' in line:
                    print(f"  📁 {line}")

    def cleanup_worktrees(self):
        """全worktreeをクリーンアップ"""
        print("🧹 Worktreeをクリーンアップ中...")
        
        # 全worktreeを取得
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            worktrees = []
            current_worktree = {}
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('worktree '):
                    if current_worktree:
                        worktrees.append(current_worktree)
                    current_worktree = {'path': line.split(' ', 1)[1]}
                elif line.startswith('branch '):
                    current_worktree['branch'] = line.split(' ', 1)[1]
            
            if current_worktree:
                worktrees.append(current_worktree)
            
            # orgs/配下のworktreeを削除
            for worktree in worktrees:
                path = worktree['path']
                if '/orgs/' in path:
                    print(f"  🗑️ Removing worktree: {path}")
                    subprocess.run(
                        ["git", "worktree", "remove", path],
                        cwd=self.project_root,
                        check=False
                    )
        
        # ブランチもクリーンアップ
        self._cleanup_agent_branches()
        
        print("✅ Worktreeクリーンアップ完了")

    def _cleanup_agent_branches(self):
        """エージェントブランチをクリーンアップ"""
        result = subprocess.run(
            ["git", "branch"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                branch = line.strip().lstrip('* ')
                if branch.startswith('agent/'):
                    print(f"  🗑️ Deleting branch: {branch}")
                    subprocess.run(
                        ["git", "branch", "-D", branch],
                        cwd=self.project_root,
                        check=False
                    )

    def status(self):
        """マルチエージェント環境の状態を表示"""
        print("📊 マルチエージェント環境の状態:")
        
        state_file = self.project_root / ".multi_agent_state.json"
        if not state_file.exists():
            print("❌ 環境が初期化されていません。先に setup を実行してください。")
            return
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        print(f"📅 作成日時: {state['created_at']}")
        print(f"🏢 組織数: {len(state['organizations'])}")
        print(f"🤖 エージェント数: {len(state['agents'])}")
        print(f"📋 アクティブタスク: {len(state['active_tasks'])}")
        print(f"✅ 完了タスク: {len(state['completed_tasks'])}")
        
        print("\n🤖 エージェント一覧:")
        for agent in state['agents']:
            status_emoji = "🟢" if agent['status'] == 'active' else "🟡"
            print(f"  {status_emoji} {agent['agent_id']} ({agent['focus']})")
        
        # Worktree状態
        print("\n📁 Worktree状態:")
        self._list_worktrees()


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Git Worktree Setup")
    parser.add_argument(
        "command",
        choices=["setup", "cleanup", "status"],
        help="Command to execute"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory"
    )
    
    args = parser.parse_args()
    
    setup = MultiAgentWorktreeSetup(args.project_root)
    
    if args.command == "setup":
        setup.setup_all()
    elif args.command == "cleanup":
        setup.cleanup_worktrees()
    elif args.command == "status":
        setup.status()


if __name__ == "__main__":
    main() 