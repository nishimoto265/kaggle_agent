# tmux並列開発システム技術仕様書

## 概要

Kaggle Agent開発における**tmux並列開発システム**の技術仕様。Boss+3名Workerによる同時並列開発環境を提供し、リアルタイム監視・指示・評価を実現。

## システム設計原則

### 基本コンセプト
```yaml
並列性原則:
  - 4つのペインでの同時作業
  - 独立ディレクトリによる衝突回避
  - Git worktreeによる物理分離

リアルタイム性原則:
  - 即座の指示配布・進捗共有
  - 30分間隔での自動進捗更新
  - 完了時の即座通知

可視性原則:
  - Boss画面での全体進捗一覧表示
  - Worker画面での個別チェックリスト
  - ペインタイトルでの役割明示
```

## tmuxセッション設計仕様

### セッション構造詳細

> **📁 ディレクトリ構造**: 詳細は [`project_structure.md`](project_structure.md) を参照

```
tmux session: org01-parallel-dev
Window 0: Main Development (2x2 Layout)

┌─────────────────────────┬─────────────────────────┐
│ Pane 0: Boss Control    │ Pane 1: Worker-A        │
│ - Title: "👑 Boss"      │ - Title: "⚡ Worker-A"  │
│ - Focus: 指示・監視      │ - Focus: パフォーマンス  │
├─────────────────────────┼─────────────────────────┤
│ Pane 2: Worker-B        │ Pane 3: Worker-C        │
│ - Title: "📚 Worker-B"  │ - Title: "🔧 Worker-C"  │
│ - Focus: 保守性         │ - Focus: 拡張性         │
└─────────────────────────┴─────────────────────────┘

共通設定:
- 総サイズ: 120x40
- レイアウト: tiled (2x2均等分割)
- スクロールバック: 10000行
- マウスサポート: 有効
- ステータスバー: 常時表示
```

### セッション自動構築スクリプト
```bash
#!/bin/bash
# scripts/create_org01_parallel_session.sh

SESSION="org01-parallel-dev"
ORG_PATH="orgs/org-01"
BASE_PATH="/media/thithilab/volume/kaggle_agent"

echo "🚀 Creating org01 parallel development session..."

# 既存セッション確認・削除
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "🔄 Killing existing session: $SESSION"
    tmux kill-session -t $SESSION
fi

# 基本設定
tmux set-option -g default-shell /usr/bin/bash
tmux set-option -g history-limit 10000
tmux set-option -g mouse on
tmux set-option -g status on
tmux set-option -g status-position bottom

# 新セッション作成
echo "📱 Creating new session: $SESSION"
tmux new-session -d -s $SESSION -c "$BASE_PATH" -x 120 -y 40

# ウィンドウ名設定
tmux rename-window -t $SESSION:0 "Parallel-Dev"

# ペイン分割 (2x2レイアウト)
echo "🔧 Setting up 2x2 pane layout..."
tmux split-window -h -t $SESSION:0
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.1

# ペイン設定関数
setup_pane() {
    local pane=$1
    local directory=$2
    local title=$3
    local role=$4
    local emoji=$5
    
    echo "⚙️ Setting up pane $pane: $title"
    
    # ディレクトリ移動
    tmux send-keys -t $SESSION:0.$pane "cd $BASE_PATH/$ORG_PATH/$directory" C-m
    
    # ペインタイトル設定
    tmux select-pane -t $SESSION:0.$pane -T "$emoji $title"
    
    # 初期表示
    tmux send-keys -t $SESSION:0.$pane "clear" C-m
    tmux send-keys -t $SESSION:0.$pane "echo '╔══════════════════════════════════════════════════════════╗'" C-m
    tmux send-keys -t $SESSION:0.$pane "echo '║  $emoji $title - $role ║'" C-m  
    tmux send-keys -t $SESSION:0.$pane "echo '╚══════════════════════════════════════════════════════════╝'" C-m
    tmux send-keys -t $SESSION:0.$pane "echo ''" C-m
    
    # 役割別初期化
    case $directory in
        "01boss")
            tmux send-keys -t $SESSION:0.$pane "echo '🎯 Ready to distribute tasks and monitor progress'" C-m
            tmux send-keys -t $SESSION:0.$pane "echo '📋 Commands: distribute_task, monitor_progress, evaluate_implementations'" C-m
            ;;
        "01worker-a")
            tmux send-keys -t $SESSION:0.$pane "echo '⚡ Specialization: Performance Optimization'" C-m
            tmux send-keys -t $SESSION:0.$pane "echo '🎯 Focus: Speed, Memory Efficiency, Algorithmic Optimization'" C-m
            ;;
        "01worker-b") 
            tmux send-keys -t $SESSION:0.$pane "echo '📚 Specialization: Maintainability & Readability'" C-m
            tmux send-keys -t $SESSION:0.$pane "echo '🎯 Focus: Clean Code, Documentation, Error Handling'" C-m
            ;;
        "01worker-c")
            tmux send-keys -t $SESSION:0.$pane "echo '🔧 Specialization: Extensibility & Scalability'" C-m
            tmux send-keys -t $SESSION:0.$pane "echo '🎯 Focus: Pluggable Design, Configuration, Future-proofing'" C-m
            ;;
    esac
    
    tmux send-keys -t $SESSION:0.$pane "echo ''" C-m
    tmux send-keys -t $SESSION:0.$pane "echo '⏳ Waiting for task assignment...'" C-m
}

# 各ペイン初期化
setup_pane 0 "01boss" "Boss Control" "Task Distribution & Monitoring" "👑"
setup_pane 1 "01worker-a" "Worker-A" "Performance Focus" "⚡"
setup_pane 2 "01worker-b" "Worker-B" "Maintainability Focus" "📚" 
setup_pane 3 "01worker-c" "Worker-C" "Extensibility Focus" "🔧"

# ステータスバー設定
tmux set-option -t $SESSION status-left-length 50
tmux set-option -t $SESSION status-right-length 100
tmux set-option -t $SESSION status-left "#[fg=green]Session: #S #[fg=yellow]| Win: #I #[fg=cyan]| "
tmux set-option -t $SESSION status-right "#[fg=cyan]%Y-%m-%d %H:%M #[fg=yellow]| #[fg=green]org01-dev"

# キーバインド設定
tmux bind-key -t $SESSION r source-file ~/.tmux.conf \; display-message "Config reloaded!"
tmux bind-key -t $SESSION h select-pane -L
tmux bind-key -t $SESSION j select-pane -D  
tmux bind-key -t $SESSION k select-pane -U
tmux bind-key -t $SESSION l select-pane -R

# デフォルトペインフォーカス（Boss）
tmux select-pane -t $SESSION:0.0

echo "✅ Session created successfully!"
echo "🔗 Attach with: tmux attach-session -t $SESSION"
echo "📋 Quick commands:"
echo "   - Ctrl+b + h/j/k/l : Navigate panes"  
echo "   - Ctrl+b + r       : Reload config"
echo "   - Ctrl+b + d       : Detach session"
```

## Boss指示配布システム

### 統一タスク配布メカニズム
```python
# scripts/boss_task_distributor.py

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List

class BossTaskDistributor:
    """Boss指示配布・監視システム"""
    
    def __init__(self, session_name: str = "org01-parallel-dev"):
        self.session_name = session_name
        self.org_path = "orgs/org-01"
        self.workers = {
                'worker-a': {'pane': 1, 'approach': 'AI変動実装1', 'emoji': '⚡'},
    'worker-b': {'pane': 2, 'approach': 'AI変動実装2', 'emoji': '📚'},
    'worker-c': {'pane': 3, 'approach': 'AI変動実装3', 'emoji': '🔧'}
        }
        
    def distribute_unified_task(self, module_name: str, requirements: Dict):
        """統一タスクを全Workerに同時配布"""
        
        print(f"🎯 Distributing task: {module_name}")
        
        # 1. 統一チェックリスト作成
        checklist_content = self.create_unified_checklist(module_name, requirements)
        
        # 2. 共有リソースに配置
        self.save_shared_checklist(checklist_content, module_name)
        
        # 3. 各Worker環境準備
        for worker_name, config in self.workers.items():
            self.prepare_worker_environment(worker_name, module_name)
        
        # 4. tmuxペインに指示送信
        for worker_name, config in self.workers.items():
            self.send_worker_instructions(worker_name, config, module_name)
        
        # 5. Boss監視画面準備
        self.setup_boss_monitoring()
        
        print(f"✅ Task distributed to all workers: {module_name}")
    
    def create_unified_checklist(self, module_name: str, requirements: Dict) -> str:
        """統一チェックリスト生成"""
        
        checklist = f"""# 📋 {module_name} 統一実装チェックリスト

## 📊 メタ情報
- **モジュール**: {module_name}
- **開始日**: {datetime.now().strftime('%Y-%m-%d')}
- **期限**: {requirements.get('deadline', 'TBD')}
- **優先度**: {requirements.get('priority', 'Medium')}
- **複雑度**: {requirements.get('complexity', 'Medium')}

## 🎯 要件定義 (共通)"""
        
        # 要件セクション追加
        for req_category, req_items in requirements.get('requirements', {}).items():
            checklist += f"\n### {req_category}\n"
            for item in req_items:
                checklist += f"- [ ] {item}\n"
        
        # 専門性セクション追加
        checklist += """
## ⚡ 専門性実装 (Worker別分化)
### Worker-A (パフォーマンス重視)
- [ ] アルゴリズム最適化実装
- [ ] メモリ効率最適化
- [ ] 実行速度最適化
- [ ] リソース使用量最適化
- [ ] パフォーマンス分析レポート作成

### Worker-B (保守性重視)
- [ ] 可読性向上実装
- [ ] 設計パターン適用
- [ ] 包括的エラーメッセージ
- [ ] 保守性向上ドキュメント
- [ ] コードレビューガイド作成

### Worker-C (拡張性重視)
- [ ] プラガブル設計実装
- [ ] 設定外部化実装
- [ ] インターフェース抽象化
- [ ] 将来拡張ポイント設計
- [ ] 拡張方法ガイド作成

## ✅ 完了確認システム
- [ ] **🎯 全タスク完了確認**
- [ ] 他Worker進捗確認実行
- [ ] 品質基準達成確認
- [ ] 最後完了者のBoss通知送信

## 📊 進捗状況 (自動更新)
- Worker-A Progress: 0/25 (0%)
- Worker-B Progress: 0/25 (0%)
- Worker-C Progress: 0/25 (0%)
- Estimated Completion: TBD
"""
        
        return checklist
    
    def send_worker_instructions(self, worker_name: str, config: Dict, module_name: str):
        """Worker個別指示送信"""
        
        pane = config['pane']
        specialty = config['specialty']
        emoji = config['emoji']
        
        # ペインクリア
        self.send_to_pane(pane, "clear")
        
        # ヘッダー表示
        self.send_to_pane(pane, "echo '╔══════════════════════════════════════════════════════════╗'")
        self.send_to_pane(pane, f"echo '║  {emoji} {worker_name.upper()} - {module_name} TASK START ║'")
        self.send_to_pane(pane, "echo '╚══════════════════════════════════════════════════════════╝'")
        self.send_to_pane(pane, "echo ''")
        
        # 指示内容
        instructions = [
            f"🎯 **作業ディレクトリ**: {self.org_path}/01{worker_name}/",
            f"🎪 **専門性**: {specialty}でタスクを実装",
            f"📋 **チェックリスト**: shared_org01/task_checklist.md",
            f"📈 **進捗管理**: ./progress.md でチェックマーク更新",
            "🔄 **自動監視**: 30分毎に進捗自動確認",
            "✅ **完了通知**: 全タスク完了時、自動でBoss通知",
            "",
            "📋 **開始コマンド**:",
            "  cat ../shared_org01/task_checklist.md | head -50",
            "  cp ../shared_org01/task_checklist.md ./progress.md",
            "",
            f"🎯 **{specialty}での実装要点**:"
        ]
        
        # 専門性別の詳細指示
        specialty_guidance = {
            'パフォーマンス重視': [
                "- アルゴリズム計算量を最小化",
                "- メモリ使用量を最適化", 
                "- 実行時間短縮を優先",
                "- プロファイリングでボトルネック特定",
                "- ベンチマークテストで性能測定"
            ],
            '保守性重視': [
                "- コードの可読性を最優先",
                "- 豊富なコメントと文書化",
                "- 明確なエラーメッセージ",
                "- 設計パターンの適切な適用",
                "- 包括的なテストケース作成"
            ],
            '拡張性重視': [
                "- プラガブルなアーキテクチャ",
                "- 設定の外部化・柔軟化",
                "- インターフェースの抽象化",
                "- 将来の拡張ポイント設計",
                "- 依存関係の最小化"
            ]
        }
        
        for guidance in specialty_guidance.get(specialty, []):
            instructions.append(guidance)
        
        instructions.extend([
            "",
            "🚀 **実装開始**: Ready for implementation!",
            f"⏰ **開始時刻**: {datetime.now().strftime('%H:%M:%S')}"
        ])
        
        # 指示送信
        for instruction in instructions:
            self.send_to_pane(pane, f"echo '{instruction}'")
        
        # チェックリスト初期表示
        self.send_to_pane(pane, "echo ''")
        self.send_to_pane(pane, "echo '📋 統一チェックリスト (最初の20項目):'")
        self.send_to_pane(pane, "head -20 ../shared_org01/task_checklist.md")
    
    def setup_boss_monitoring(self):
        """Boss監視画面セットアップ"""
        
        boss_pane = 0
        
        # ペインクリア
        self.send_to_pane(boss_pane, "clear")
        
        # Boss監視インターフェース
        self.send_to_pane(boss_pane, "echo '╔══════════════════════════════════════════════════════════╗'")
        self.send_to_pane(boss_pane, "echo '║  👑 BOSS CONTROL PANEL - PARALLEL DEVELOPMENT MONITOR  ║'")
        self.send_to_pane(boss_pane, "echo '╚══════════════════════════════════════════════════════════╝'")
        self.send_to_pane(boss_pane, "echo ''")
        
        monitoring_display = [
            "📊 **実行中タスク**: Database Module Implementation",
            f"⏰ **開始時刻**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "🎯 **Worker状況**:",
            "  ⚡ Worker-A (Performance): ⏳ 準備完了 (0/25 tasks)",
            "  📚 Worker-B (Maintainability): ⏳ 準備完了 (0/25 tasks)",
            "  🔧 Worker-C (Extensibility): ⏳ 準備完了 (0/25 tasks)",
            "",
            "📋 **監視コマンド**:",
            "  python ../shared_org01/progress_tracking/progress_tracker.py",
            "  watch -n 1800 'python progress_monitor.py'",
            "",
            "🔄 **自動更新**: 30分間隔で進捗確認中...",
            "",
            "📈 **完了予測**: 全Worker完了後、Boss評価開始",
            "⚡ **評価準備**: evaluation_tools/ で比較分析準備中"
        ]
        
        for display_item in monitoring_display:
            self.send_to_pane(boss_pane, f"echo '{display_item}'")
        
        # 自動監視スクリプト開始
        self.send_to_pane(boss_pane, "echo ''")
        self.send_to_pane(boss_pane, "echo '🚀 Starting automatic progress monitoring...'")
        self.send_to_pane(boss_pane, "python ../shared_org01/progress_tracking/auto_monitor.py &")
    
    def send_to_pane(self, pane: int, command: str):
        """tmuxペインにコマンド送信"""
        cmd = f"tmux send-keys -t {self.session_name}:0.{pane} '{command}' C-m"
        subprocess.run(cmd, shell=True)
        time.sleep(0.1)  # 表示間隔調整
```

## リアルタイム進捗監視システム

### 自動進捗更新エンジン
```python
# shared_org01/progress_tracking/auto_monitor.py

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List

class RealtimeProgressMonitor:
    """リアルタイム進捗監視システム"""
    
    def __init__(self):
        self.workers = ['worker-a', 'worker-b', 'worker-c']
        self.monitor_interval = 1800  # 30分
        self.session_name = "org01-parallel-dev"
        self.status_file = "shared_org01/progress_tracking/realtime_status.json"
        
    def start_monitoring(self):
        """監視開始"""
        print("🔄 Starting realtime progress monitoring...")
        
        while True:
            try:
                # 進捗データ更新
                progress_data = self.collect_all_progress()
                
                # 表示更新
                self.update_displays(progress_data)
                
                # 完了チェック
                if self.check_completion(progress_data):
                    self.trigger_completion_process()
                    break
                
                # 30分待機
                time.sleep(self.monitor_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(60)  # エラー時は1分待機
    
    def collect_all_progress(self) -> Dict:
        """全Worker進捗収集"""
        progress_data = {
            'timestamp': datetime.now().isoformat(),
            'workers': {},
            'overall': {}
        }
        
        total_tasks = 0
        completed_tasks = 0
        
        for worker in self.workers:
            worker_progress = self.analyze_worker_progress(worker)
            progress_data['workers'][worker] = worker_progress
            
            total_tasks += worker_progress.get('total_tasks', 0)
            completed_tasks += worker_progress.get('completed_tasks', 0)
        
        # 全体進捗計算
        progress_data['overall'] = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'estimated_completion': self.estimate_completion_time(progress_data['workers'])
        }
        
        # ステータスファイル保存
        self.save_status(progress_data)
        
        return progress_data
    
    def analyze_worker_progress(self, worker_name: str) -> Dict:
        """Worker個別進捗解析"""
        progress_file = f"orgs/org-01/01{worker_name}/progress.md"
        
        if not os.path.exists(progress_file):
            return {
                'status': 'not_started',
                'total_tasks': 0,
                'completed_tasks': 0,
                'completion_rate': 0,
                'last_activity': None
            }
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # チェックマーク解析
        total_checkboxes = content.count('- [ ]') + content.count('- [x]')
        completed_checkboxes = content.count('- [x]')
        completion_rate = (completed_checkboxes / total_checkboxes * 100) if total_checkboxes > 0 else 0
        
        # ファイル最終更新時刻
        stat = os.stat(progress_file)
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        
        return {
            'status': 'completed' if completion_rate >= 100 else 'in_progress',
            'total_tasks': total_checkboxes,
            'completed_tasks': completed_checkboxes,
            'completion_rate': completion_rate,
            'last_activity': last_modified.isoformat(),
            'file_size': stat.st_size
        }
    
    def update_displays(self, progress_data: Dict):
        """全ペイン表示更新"""
        
        # Boss画面更新
        self.update_boss_display(progress_data)
        
        # Worker画面更新
        for worker in self.workers:
            self.update_worker_display(worker, progress_data['workers'][worker])
    
    def update_boss_display(self, progress_data: Dict):
        """Boss画面進捗表示更新"""
        
        boss_pane = 0
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # 画面下部に進捗情報追加
        self.send_to_pane(boss_pane, "echo ''")
        self.send_to_pane(boss_pane, f"echo '🕒 {current_time} - Progress Update:'")
        
        for worker_name, worker_data in progress_data['workers'].items():
            status_emoji = "✅" if worker_data['status'] == 'completed' else "⏳"
            rate = worker_data['completion_rate']
            completed = worker_data['completed_tasks']
            total = worker_data['total_tasks']
            
            progress_bar = self.create_progress_bar(rate)
            
            worker_display = {
                'worker-a': '⚡ Worker-A (Performance)',
                'worker-b': '📚 Worker-B (Maintainability)', 
                'worker-c': '🔧 Worker-C (Extensibility)'
            }
            
            display_text = f"  {status_emoji} {worker_display[worker_name]}: {progress_bar} {rate:.1f}% ({completed}/{total})"
            self.send_to_pane(boss_pane, f"echo '{display_text}'")
        
        # 全体進捗
        overall = progress_data['overall']
        overall_rate = overall['completion_rate']
        overall_bar = self.create_progress_bar(overall_rate)
        
        self.send_to_pane(boss_pane, "echo ''")
        self.send_to_pane(boss_pane, f"echo '📊 Overall Progress: {overall_bar} {overall_rate:.1f}%'")
        
        if overall['estimated_completion']:
            self.send_to_pane(boss_pane, f"echo '🕒 Estimated Completion: {overall[\"estimated_completion\"]}'")
    
    def create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """プログレスバー生成"""
        filled = int(percentage / 100 * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"
    
    def send_to_pane(self, pane: int, command: str):
        """tmuxペインにコマンド送信"""
        cmd = f"tmux send-keys -t {self.session_name}:0.{pane} '{command}' C-m"
        subprocess.run(cmd, shell=True, capture_output=True)

if __name__ == "__main__":
    monitor = RealtimeProgressMonitor()
    monitor.start_monitoring()
```

## Worker専用環境設定

### Worker個別初期化システム
```python
# scripts/worker_environment_setup.py

class WorkerEnvironmentSetup:
    """Worker作業環境自動設定"""
    
    def __init__(self, worker_name: str):
        self.worker_name = worker_name
        self.worker_dir = f"orgs/org-01/01{worker_name}"
        self.specialty_config = {
            'worker-a': {
                'focus': 'performance',
                'tools': ['pytest-benchmark', 'memory-profiler', 'py-spy'],
                'configs': ['performance_test_config.py', 'benchmark_settings.yaml']
            },
            'worker-b': {
                'focus': 'maintainability', 
                'tools': ['pylint', 'black', 'mypy', 'sphinx'],
                'configs': ['code_quality_config.py', 'documentation_template.md']
            },
            'worker-c': {
                'focus': 'extensibility',
                'tools': ['pluggy', 'pydantic', 'dynaconf'],
                'configs': ['plugin_architecture.py', 'config_schema.yaml']
            }
        }
    
    def setup_worker_environment(self, module_name: str):
        """Worker環境完全セットアップ"""
        
        print(f"🔧 Setting up {self.worker_name} environment for {module_name}")
        
        # 基本ディレクトリ構造作成
        self.create_directory_structure()
        
        # 専門性特化ツール設定
        self.setup_specialty_tools()
        
        # 初期ファイル配置
        self.deploy_initial_files(module_name)
        
        # 環境変数設定
        self.setup_environment_variables()
        
        # Worker専用スクリプト配置
        self.deploy_worker_scripts()
        
        print(f"✅ {self.worker_name} environment ready")
    
    def create_directory_structure(self):
        """基本ディレクトリ構造作成"""
        
        dirs = [
            f"{self.worker_dir}/src/kaggle_agent",
            f"{self.worker_dir}/tests",
            f"{self.worker_dir}/docs", 
            f"{self.worker_dir}/config",
            f"{self.worker_dir}/tools",
            f"{self.worker_dir}/reports"
        ]
        
        # 専門性別追加ディレクトリ
        specialty_dir = self.specialty_config[self.worker_name]['focus']
        dirs.append(f"{self.worker_dir}/{specialty_dir}")
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
    
    def setup_specialty_tools(self):
        """専門性特化ツール設定"""
        
        config = self.specialty_config[self.worker_name]
        tools = config['tools']
        
        # 専門性別ツール設定ファイル作成
        if config['focus'] == 'performance':
            self.create_performance_tools()
        elif config['focus'] == 'maintainability':
            self.create_maintainability_tools()
        elif config['focus'] == 'extensibility':
            self.create_extensibility_tools()
    
    def create_performance_tools(self):
        """パフォーマンス特化ツール設定"""
        
        # ベンチマーク設定
        benchmark_config = """
# performance/benchmark_config.py

import pytest

# ベンチマーク設定
BENCHMARK_SETTINGS = {
    'min_rounds': 10,
    'max_time': 30.0,
    'warmup': True,
    'warmup_iterations': 5
}

def pytest_benchmark_generate_machine_info():
    return {
        'worker': 'worker-a',
        'focus': 'performance_optimization'
    }
"""
        
        with open(f"{self.worker_dir}/performance/benchmark_config.py", 'w') as f:
            f.write(benchmark_config)
        
        # プロファイリングスクリプト
        profiling_script = """#!/bin/bash
# performance/profile_runner.sh

echo "🔍 Running performance profiling..."

# メモリプロファイリング
python -m memory_profiler src/kaggle_agent/core/database.py > reports/memory_profile.txt

# CPU プロファイリング  
py-spy record -o reports/cpu_profile.svg -- python -m pytest tests/

# ベンチマーク実行
python -m pytest tests/ --benchmark-only --benchmark-json=reports/benchmark_results.json

echo "📊 Profiling complete. Check reports/ directory."
"""
        
        with open(f"{self.worker_dir}/performance/profile_runner.sh", 'w') as f:
            f.write(profiling_script)
        
        os.chmod(f"{self.worker_dir}/performance/profile_runner.sh", 0o755)
```

## 完了検知・通知システム

### 自動完了通知エンジン
```python
# shared_org01/progress_tracking/completion_notifier.py

class CompletionNotifier:
    """完了検知・通知システム"""
    
    def __init__(self):
        self.session_name = "org01-parallel-dev"
        self.notification_log = "shared_org01/progress_tracking/notifications.log"
        
    def check_and_notify_completion(self, progress_data: Dict) -> bool:
        """完了チェック・通知"""
        
        all_completed = all(
            worker_data['status'] == 'completed' 
            for worker_data in progress_data['workers'].values()
        )
        
        if all_completed:
            self.trigger_completion_celebration()
            self.notify_boss_evaluation_ready()
            self.prepare_evaluation_environment()
            return True
        
        return False
    
    def trigger_completion_celebration(self):
        """完了祝賀表示"""
        
        celebration_message = """
╔══════════════════════════════════════════════════════════╗
║  🎉 ALL WORKERS COMPLETED! PARALLEL DEVELOPMENT SUCCESS! ║
╚══════════════════════════════════════════════════════════╝

🏆 ACHIEVEMENTS:
  ⚡ Worker-A: Performance optimization implementation complete
  📚 Worker-B: Maintainable & readable implementation complete  
  🔧 Worker-C: Extensible & scalable implementation complete

📊 STATISTICS:
  ⏱️ Total Development Time: [Auto-calculated]
  📈 Average Progress Rate: [Auto-calculated]
  🎯 Quality Metrics: Ready for evaluation

🔄 NEXT PHASE:
  👑 Boss evaluation starting automatically...
  📋 Comparison matrix generation in progress...
  🏅 Best implementation selection pending...

✨ Transitioning to evaluation phase in 10 seconds...
"""
        
        # 全ペインに祝賀メッセージ表示
        for pane in range(4):
            self.send_celebration_to_pane(pane, celebration_message)
        
        # 10秒待機
        time.sleep(10)
    
    def notify_boss_evaluation_ready(self):
        """Boss評価準備通知"""
        
        boss_pane = 0
        
        self.send_to_pane(boss_pane, "clear")
        
        evaluation_instructions = [
            "╔══════════════════════════════════════════════════════════╗",
            "║  👑 BOSS EVALUATION PHASE - ALL IMPLEMENTATIONS READY   ║", 
            "╚══════════════════════════════════════════════════════════╝",
            "",
            "🎯 **評価開始指示**:",
            "  1. 自動評価実行: python evaluation_tools/auto_evaluator.py",
            "  2. 手動評価実行: python evaluation_tools/manual_evaluator.py",
            "  3. 比較レポート確認: cat comparison_reports/matrix.md",
            "  4. 最終判断記録: python evaluation_tools/final_decision.py",
            "",
            "📊 **評価対象**:",
            "  ⚡ Worker-A Implementation (Performance Focus)",
            "  📚 Worker-B Implementation (Maintainability Focus)",
            "  🔧 Worker-C Implementation (Extensibility Focus)",
            "",
            "📋 **評価基準**:",
            "  - Code Quality (25 points)",
            "  - Performance (20 points)",
            "  - Maintainability (20 points)", 
            "  - Extensibility (15 points)",
            "  - Testing (10 points)",
            "  - Security (10 points)",
            "",
            "🚀 **評価開始**: Ready for Boss evaluation!"
        ]
        
        for instruction in evaluation_instructions:
            self.send_to_pane(boss_pane, f"echo '{instruction}'")
    
    def send_to_pane(self, pane: int, command: str):
        """tmuxペインにコマンド送信"""
        cmd = f"tmux send-keys -t {self.session_name}:0.{pane} '{command}' C-m"
        subprocess.run(cmd, shell=True)
```

## システム統合・運用仕様

### ワンコマンド起動システム
```bash
# scripts/start_org01_parallel_dev.sh
#!/bin/bash

echo "🚀 Starting org01 parallel development system..."

# 1. tmuxセッション作成
echo "📱 Creating tmux session..."
./scripts/create_org01_parallel_session.sh

# 2. Git worktree準備
echo "🌿 Setting up Git worktree..."
git worktree add orgs/org-01 org-01-development

# 3. 共有リソース初期化  
echo "📋 Initializing shared resources..."
mkdir -p orgs/org-01/shared_org01/{progress_tracking,boss_evaluation,reference_materials}

# 4. Worker環境準備
echo "⚙️ Setting up worker environments..."
for worker in worker-a worker-b worker-c; do
    python scripts/worker_environment_setup.py --worker $worker
done

# 5. 監視システム開始
echo "👁️ Starting monitoring system..."
python shared_org01/progress_tracking/auto_monitor.py &

# 6. セッションにアタッチ
echo "🔗 Attaching to session..."
tmux attach-session -t org01-parallel-dev

echo "✅ org01 parallel development system started!"
```

この**tmux並列開発システム**により、効率的で協調的な並列開発環境が実現されます。 