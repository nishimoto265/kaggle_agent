#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Task Management System
タスクの作成、割り当て、進捗管理、TDD開発サイクルの統制
"""

import os
import json
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid


class TaskManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.orgs_dir = self.project_root / "orgs"
        self.shared_dir = self.project_root / "shared"
        self.state_file = self.project_root / ".multi_agent_state.json"
        
        # Load current state
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """現在の状態を読み込み"""
        if not self.state_file.exists():
            raise FileNotFoundError(
                "Multi-agent environment not initialized. Run 'python scripts/setup_multi_agent_env.py setup' first."
            )
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """状態を保存"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def create_task(self, 
                   module_name: str, 
                   description: str, 
                   priority: str = "medium",
                   organization_id: str = None,
                   requirements_file: str = None) -> str:
        """新しいタスクを作成"""
        
        # Determine organization if not specified
        if not organization_id:
            organization_id = self._determine_organization(module_name)
        
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        task = {
            "id": task_id,
            "module_name": module_name,
            "description": description,
            "priority": priority,
            "organization_id": organization_id,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "assigned_agents": [],
            "requirements_file": requirements_file,
            "deliverables": {
                "test_cases": None,
                "test_code": None,
                "implementation": {
                    "worker_a": None,
                    "worker_b": None, 
                    "worker_c": None
                },
                "evaluation": None,
                "selected_implementation": None
            },
            "metrics": {
                "start_time": None,
                "end_time": None,
                "total_duration": None,
                "test_coverage": {},
                "performance_metrics": {},
                "quality_scores": {}
            }
        }
        
        self.state["active_tasks"].append(task)
        self._save_state()
        
        print(f"✅ タスク {task_id} を作成しました")
        print(f"   モジュール: {module_name}")
        print(f"   組織: {organization_id}")
        print(f"   説明: {description}")
        
        # Create task specification file
        self._create_task_specification(task)
        
        return task_id

    def _determine_organization(self, module_name: str) -> str:
        """モジュール名から適切な組織を決定"""
        org_mapping = {
            # Core Infrastructure
            "workflow": "01", "database": "01", "cache": "01", "storage": "01",
            "messaging": "01", "monitoring": "01", "security": "01",
            
            # Application Modules  
            "competition_discovery": "02", "research": "02", "code_generation": "02",
            "gpu_management": "02", "training": "02", "submission": "02", "human_loop": "02",
            
            # Interfaces
            "api": "03", "cli": "03", "ui": "03", "webhooks": "03",
            
            # Quality Assurance
            "testing": "04", "monitoring": "04", "security_audit": "04", "performance": "04"
        }
        
        return org_mapping.get(module_name, "02")  # Default to application modules

    def _create_task_specification(self, task: Dict[str, Any]):
        """タスク仕様書を作成"""
        task_id = task["id"]
        module_name = task["module_name"]
        org_id = task["organization_id"]
        
        # Task specification directory
        task_spec_dir = self.shared_dir / "specifications" / "tasks" / task_id
        task_spec_dir.mkdir(parents=True, exist_ok=True)
        
        # Main specification file
        spec_content = f"""# Task Specification: {module_name}

## Task Information
- **Task ID**: {task_id}
- **Module**: {module_name}
- **Organization**: {org_id}
- **Priority**: {task['priority']}
- **Created**: {task['created_at']}

## Description
{task['description']}

## Requirements
{self._generate_requirements_section(task)}

## Test Requirements
{self._generate_test_requirements(task)}

## Implementation Guidelines
{self._generate_implementation_guidelines(task)}

## Acceptance Criteria
{self._generate_acceptance_criteria(task)}

## Reference Files
- Project Requirements: @docs/requirements.md
- Architecture Design: @docs/architecture_design.md
- Module Specification: @shared/specifications/kaggle_agent/{module_name}_spec.md
- Organization Guidelines: @shared/instructions/org-{org_id}/guidelines.md

---
*Auto-generated task specification*
"""
        
        spec_file = task_spec_dir / "specification.md"
        spec_file.write_text(spec_content, encoding='utf-8')
        
        # Test case template
        test_template = f"""# Test Cases for {module_name}

## Unit Test Cases

### Basic Functionality
- [ ] Test case 1: [Description]
- [ ] Test case 2: [Description]
- [ ] Test case 3: [Description]

### Error Handling
- [ ] Test invalid input handling
- [ ] Test exception propagation
- [ ] Test resource cleanup

### Integration Tests
- [ ] Test module integration
- [ ] Test API endpoints
- [ ] Test database operations

### Performance Tests
- [ ] Test response time requirements
- [ ] Test memory usage
- [ ] Test concurrent operations

## Implementation-Specific Tests

### Worker-A (Performance Focus)
- [ ] Benchmark test suites
- [ ] Memory profiling tests
- [ ] Concurrent execution tests

### Worker-B (Maintainability Focus)
- [ ] Code readability tests
- [ ] Documentation completeness tests
- [ ] Refactoring safety tests

### Worker-C (Extensibility Focus)
- [ ] Plugin interface tests
- [ ] Configuration flexibility tests
- [ ] Future feature compatibility tests

---
*Complete these test cases before implementation*
"""
        
        test_cases_file = task_spec_dir / "test_cases.md"
        test_cases_file.write_text(test_template, encoding='utf-8')

    def assign_task(self, task_id: str, force: bool = False) -> bool:
        """タスクをエージェントに割り当て"""
        task = self._find_task(task_id)
        if not task:
            print(f"❌ タスク {task_id} が見つかりません")
            return False
        
        if task["status"] != "created" and not force:
            print(f"❌ タスク {task_id} は既に割り当て済みです（status: {task['status']}）")
            return False
        
        org_id = task["organization_id"]
        org_dir = self.orgs_dir / f"org-{org_id}"
        
        if not org_dir.exists():
            print(f"❌ 組織 {org_id} のディレクトリが存在しません")
            return False
        
        # Find agents in the organization
        agents = []
        for agent_dir in org_dir.iterdir():
            if agent_dir.is_dir():
                info_file = agent_dir / ".agent_info.json"
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        agent_info = json.load(f)
                        agents.append(agent_info)
        
        if len(agents) != 4:  # Should have 1 boss + 3 workers
            print(f"❌ 組織 {org_id} に適切な数のエージェントがいません (found: {len(agents)})")
            return False
        
        # Assign task to all agents in the organization
        assigned_agents = []
        for agent in agents:
            agent_id = agent["agent_id"]
            agent_path = Path(agent["worktree_path"])
            
            # Update current_task.md
            self._update_agent_task(agent_path, task)
            
            # Update agent info
            agent["current_task"] = task_id
            agent["status"] = "active"
            
            info_file = agent_path / ".agent_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(agent, f, indent=2, ensure_ascii=False)
            
            assigned_agents.append(agent_id)
        
        # Update task status
        task["assigned_agents"] = assigned_agents
        task["status"] = "assigned"
        task["metrics"]["start_time"] = datetime.now(timezone.utc).isoformat()
        
        self._save_state()
        
        print(f"✅ タスク {task_id} を組織 {org_id} の全エージェントに割り当てました")
        for agent_id in assigned_agents:
            print(f"   🤖 {agent_id}")
        
        return True

    def _update_agent_task(self, agent_path: Path, task: Dict[str, Any]):
        """エージェントのcurrent_task.mdを更新"""
        task_content = f"""# Current Task - {task['id']}

## 📋 Task Information
- **Task ID**: {task['id']}
- **Module**: {task['module_name']}
- **Status**: {task['status']}
- **Priority**: {task['priority']}
- **Created**: {task['created_at']}

## 🎯 Task Description
{task['description']}

## 📊 Progress Tracking
- [ ] 要件分析・理解
- [ ] テストケース設計
- [ ] テストコード実装
- [ ] 実装（TDD Red-Green-Refactor）
- [ ] ドキュメント作成
- [ ] 品質確認・提出

## 🔗 Reference Files
- Task Specification: @shared/specifications/tasks/{task['id']}/specification.md
- Test Cases: @shared/specifications/tasks/{task['id']}/test_cases.md
- Module Spec: @shared/specifications/kaggle_agent/{task['module_name']}_spec.md

## 📝 Development Notes
開発過程での重要な決定事項や注意点をここに記録してください。

## 🚀 Getting Started
1. まず上記の参照ファイルを全て読み込んでください
2. 要件を理解し、質問があれば明確にしてください
3. TDD手法で段階的に実装を進めてください

---
*Last updated: {datetime.now().isoformat()}*
"""
        
        task_file = agent_path / "current_task.md"
        task_file.write_text(task_content, encoding='utf-8')

    def monitor(self, task_id: str = None):
        """タスクの進捗を監視"""
        if task_id:
            self._monitor_specific_task(task_id)
        else:
            self._monitor_all_active_tasks()

    def _monitor_specific_task(self, task_id: str):
        """特定タスクの詳細監視"""
        task = self._find_task(task_id)
        if not task:
            print(f"❌ タスク {task_id} が見つかりません")
            return
        
        print(f"📊 タスク {task_id} の詳細状況:")
        print(f"   モジュール: {task['module_name']}")
        print(f"   状態: {task['status']}")
        print(f"   組織: {task['organization_id']}")
        print(f"   優先度: {task['priority']}")
        
        if task["assigned_agents"]:
            print(f"   割り当てエージェント:")
            for agent_id in task["assigned_agents"]:
                agent_info = self._get_agent_info(agent_id)
                if agent_info:
                    print(f"     🤖 {agent_id} ({agent_info['focus']}) - {agent_info['status']}")
                    
                    # Check file status in agent workspace
                    agent_path = Path(agent_info["worktree_path"])
                    self._check_agent_progress(agent_path, agent_id)

    def _monitor_all_active_tasks(self):
        """全アクティブタスクの監視"""
        active_tasks = [t for t in self.state["active_tasks"] if t["status"] in ["assigned", "in_progress"]]
        
        if not active_tasks:
            print("📭 アクティブなタスクはありません")
            return
        
        print(f"📊 アクティブタスク監視 ({len(active_tasks)} 件):")
        
        for task in active_tasks:
            print(f"\n🔸 {task['id']} - {task['module_name']}")
            print(f"   状態: {task['status']}")
            print(f"   組織: {task['organization_id']}")
            
            if task["assigned_agents"]:
                for agent_id in task["assigned_agents"]:
                    agent_info = self._get_agent_info(agent_id)
                    if agent_info:
                        status_emoji = "🟢" if agent_info["status"] == "active" else "🟡"
                        print(f"   {status_emoji} {agent_id} ({agent_info['focus']})")

    def _check_agent_progress(self, agent_path: Path, agent_id: str):
        """エージェントの進捗をチェック"""
        progress_indicators = {
            "src/": "実装コード",
            "tests/": "テストコード", 
            "docs/": "ドキュメント",
            "implementation_report.md": "実装報告書"
        }
        
        for indicator, description in progress_indicators.items():
            path = agent_path / indicator
            if path.exists():
                if path.is_dir():
                    file_count = len(list(path.glob("**/*.py")))
                    print(f"       ✓ {description}: {file_count} files")
                else:
                    print(f"       ✓ {description}: exists")
            else:
                print(f"       ⏳ {description}: pending")

    def run_cycle(self, task_id: str):
        """開発サイクルを実行（Boss評価 → Worker実装 → 統合）"""
        task = self._find_task(task_id)
        if not task:
            print(f"❌ タスク {task_id} が見つかりません")
            return False
        
        org_id = task["organization_id"]
        print(f"🔄 開発サイクルを開始: {task_id} (組織 {org_id})")
        
        # Phase 1: Test Case Design (Boss coordination)
        print("\n📋 Phase 1: テストケース設計フェーズ")
        boss_agent = self._get_boss_agent(org_id)
        if boss_agent:
            print(f"   🤖 Boss {boss_agent['agent_id']} がテストケース統制を開始...")
            self._update_task_phase(task, "test_design")
        
        # Phase 2: Parallel Implementation (Workers)
        print("\n🏗️ Phase 2: 並列実装フェーズ")
        worker_agents = self._get_worker_agents(org_id)
        for worker in worker_agents:
            print(f"   🤖 Worker {worker['agent_id']} ({worker['focus']}) が実装を開始...")
        self._update_task_phase(task, "implementation")
        
        # Phase 3: Evaluation & Integration (Boss)
        print("\n🔍 Phase 3: 評価・統合フェーズ")
        if boss_agent:
            print(f"   🤖 Boss {boss_agent['agent_id']} が評価・統合を開始...")
            self._update_task_phase(task, "evaluation")
        
        print("✅ 開発サイクルが開始されました。エージェントが作業を開始してください。")
        return True

    def _update_task_phase(self, task: Dict[str, Any], phase: str):
        """タスクフェーズを更新"""
        task["current_phase"] = phase
        task["phase_updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state()

    def status(self, verbose: bool = False):
        """システム全体の状況を表示"""
        print("📊 Multi-Agent Task Manager Status")
        print("=" * 50)
        
        # Overall statistics
        total_tasks = len(self.state.get("active_tasks", [])) + len(self.state.get("completed_tasks", []))
        active_tasks = len([t for t in self.state.get("active_tasks", []) if t["status"] in ["assigned", "in_progress"]])
        completed_tasks = len(self.state.get("completed_tasks", []))
        
        print(f"📈 Total Tasks: {total_tasks}")
        print(f"🔥 Active Tasks: {active_tasks}")
        print(f"✅ Completed Tasks: {completed_tasks}")
        
        # Organization status
        print(f"\n🏢 Organization Status:")
        for org in self.state.get("organizations", []):
            org_id = org["id"]
            org_tasks = [t for t in self.state.get("active_tasks", []) if t["organization_id"] == org_id]
            print(f"   Org-{org_id} ({org['description']}): {len(org_tasks)} active tasks")
        
        # Agent status
        print(f"\n🤖 Agent Status:")
        for agent in self.state.get("agents", []):
            status_emoji = "🟢" if agent["status"] == "active" else "🟡"
            current_task = agent.get("current_task", "None")
            print(f"   {status_emoji} {agent['agent_id']} ({agent['focus']}) - Task: {current_task}")
        
        if verbose:
            print(f"\n📋 Active Tasks Details:")
            for task in self.state.get("active_tasks", []):
                if task["status"] in ["assigned", "in_progress"]:
                    print(f"   🔸 {task['id']}: {task['module_name']} ({task['status']})")
                    print(f"      Org: {task['organization_id']}, Priority: {task['priority']}")

    def _find_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスクIDでタスクを検索"""
        for task in self.state.get("active_tasks", []):
            if task["id"] == task_id:
                return task
        for task in self.state.get("completed_tasks", []):
            if task["id"] == task_id:
                return task
        return None

    def _get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """エージェント情報を取得"""
        for agent in self.state.get("agents", []):
            if agent["agent_id"] == agent_id:
                return agent
        return None

    def _get_boss_agent(self, org_id: str) -> Optional[Dict[str, Any]]:
        """指定組織のBossエージェントを取得"""
        for agent in self.state.get("agents", []):
            if agent["agent_id"].startswith(org_id) and "boss" in agent["agent_id"]:
                return agent
        return None

    def _get_worker_agents(self, org_id: str) -> List[Dict[str, Any]]:
        """指定組織のWorkerエージェントを取得"""
        workers = []
        for agent in self.state.get("agents", []):
            if agent["agent_id"].startswith(org_id) and "worker" in agent["agent_id"]:
                workers.append(agent)
        return workers

    def _generate_requirements_section(self, task: Dict[str, Any]) -> str:
        """要件セクションを生成"""
        return f"""### Functional Requirements
- Implement {task['module_name']} module according to architecture specification
- Follow TDD methodology with comprehensive test coverage
- Ensure compatibility with existing system components

### Non-Functional Requirements  
- Performance: Response time < 100ms for typical operations
- Scalability: Support concurrent operations
- Maintainability: Follow clean code principles
- Security: Implement proper input validation and error handling

### Technical Requirements
- Python 3.12+
- Follow project coding standards
- Use type hints throughout
- Comprehensive documentation
"""

    def _generate_test_requirements(self, task: Dict[str, Any]) -> str:
        """テスト要件を生成"""
        return """### Test Coverage Requirements
- Unit test coverage: 90%+
- Integration test coverage: 80%+
- All public APIs must have tests
- Error conditions must be tested

### Test Types Required
- Unit tests (pytest)
- Integration tests
- Performance tests (if applicable)
- Security tests (if applicable)

### Test Quality Standards
- Clear test names and descriptions
- Proper setup/teardown
- Mock external dependencies
- Assert meaningful outcomes
"""

    def _generate_implementation_guidelines(self, task: Dict[str, Any]) -> str:
        """実装ガイドラインを生成"""
        return """### TDD Process
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass test
3. **Refactor**: Improve code while keeping tests green

### Code Quality Standards
- Follow PEP 8 style guide
- Use meaningful variable/function names
- Add comprehensive docstrings
- Implement proper error handling
- Use type hints consistently

### Architecture Compliance
- Follow defined module interfaces
- Respect dependency injection patterns
- Implement proper logging
- Use configuration management
"""

    def _generate_acceptance_criteria(self, task: Dict[str, Any]) -> str:
        """受け入れ基準を生成"""
        return """### Quality Gates
- [ ] All tests pass (100%)
- [ ] Test coverage ≥ 90%
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Documentation complete
- [ ] Performance requirements met
- [ ] Security requirements met

### Deliverables Checklist
- [ ] Implementation code in src/
- [ ] Comprehensive test suite in tests/
- [ ] Documentation in docs/
- [ ] Implementation report
- [ ] Performance benchmark results (if applicable)

### Boss Evaluation Criteria
- Code Quality (25%)
- Test Coverage (25%)  
- Performance (25%)
- Maintainability (15%)
- Documentation (10%)
"""


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Task Manager")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create task command
    create_parser = subparsers.add_parser("create-task", help="Create a new task")
    create_parser.add_argument("module_name", help="Module name to implement")
    create_parser.add_argument("description", help="Task description")
    create_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    create_parser.add_argument("--org", help="Organization ID (01-04)")
    create_parser.add_argument("--requirements", help="Requirements file path")
    
    # Assign task command
    assign_parser = subparsers.add_parser("assign-task", help="Assign task to agents")
    assign_parser.add_argument("task_id", help="Task ID to assign")
    assign_parser.add_argument("--force", action="store_true", help="Force reassignment")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor task progress")
    monitor_parser.add_argument("--task-id", help="Specific task ID to monitor")
    
    # Run cycle command
    cycle_parser = subparsers.add_parser("run-cycle", help="Run development cycle")
    cycle_parser.add_argument("task_id", help="Task ID to run cycle for")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = TaskManager()
        
        if args.command == "create-task":
            task_id = manager.create_task(
                args.module_name,
                args.description,
                args.priority,
                args.org,
                args.requirements
            )
            print(f"\n次のステップ: python scripts/task_manager.py assign-task {task_id}")
            
        elif args.command == "assign-task":
            success = manager.assign_task(args.task_id, args.force)
            if success:
                print(f"\n次のステップ: python scripts/task_manager.py run-cycle {args.task_id}")
                
        elif args.command == "monitor":
            manager.monitor(args.task_id)
            
        elif args.command == "run-cycle":
            manager.run_cycle(args.task_id)
            
        elif args.command == "status":
            manager.status(args.verbose)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Hint: Run 'python scripts/setup_multi_agent_env.py setup' first")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main() 