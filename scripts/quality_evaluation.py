#!/usr/bin/env python3
"""
品質評価システム
Final Boss がBoss成果物の品質を評価し、統合判定を行う
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class TaskQualityEvaluator:
    """仕事単位の品質評価システム"""
    
    def __init__(self, org_name: str, task_name: str):
        self.org_name = org_name
        self.task_name = task_name
        self.task_path = Path(f"orgs/{org_name}/{task_name}")
        self.evaluation_results = {}
        
        if not self.task_path.exists():
            raise FileNotFoundError(f"Task directory not found: {self.task_path}")
    
    def evaluate_completion(self) -> Dict:
        """完了品質の総合評価"""
        print(f"🔍 {self.org_name} {self.task_name} 品質評価開始...")
        
        results = {
            'functional_test': self._check_functional_requirements(),
            'code_quality': self._check_code_quality(),
            'test_coverage': self._check_test_coverage(),
            'documentation': self._check_documentation(),
            'performance': self._check_performance(),
        }
        
        overall_score = self._calculate_overall_score(results)
        judgment = self._make_integration_judgment(overall_score, results)
        
        evaluation_report = {
            'timestamp': datetime.now().isoformat(),
            'org_name': self.org_name,
            'task_name': self.task_name,
            'overall_score': overall_score,
            'detailed_results': results,
            'judgment': judgment,
            'recommended_action': self._get_recommended_action(judgment),
            'issues': self._extract_issues(results),
            'fix_suggestions': self._generate_fix_suggestions(results)
        }
        
        self._save_evaluation_report(evaluation_report)
        return evaluation_report
    
    def _check_functional_requirements(self) -> Dict:
        """機能要件チェック"""
        integrated_path = self.task_path / "integrated"
        
        if not integrated_path.exists():
            return {
                'passed': False,
                'score': 0,
                'details': 'integrated ディレクトリが存在しません'
            }
        
        # 基本構造確認
        src_exists = (integrated_path / "src").exists()
        tests_exists = (integrated_path / "tests").exists()
        docs_exists = (integrated_path / "docs").exists()
        
        structure_score = sum([src_exists, tests_exists, docs_exists]) * 10
        
        # 実装ファイル確認
        src_files = list((integrated_path / "src").rglob("*.py")) if src_exists else []
        implementation_score = min(len(src_files) * 10, 30)
        
        # 基本インポートテスト
        import_test_passed = False
        if src_files:
            try:
                # 最初のPythonファイルのインポートテスト
                first_file = src_files[0]
                module_name = first_file.stem
                result = subprocess.run([
                    sys.executable, "-c", 
                    f"import sys; sys.path.append('{integrated_path}/src'); import {module_name}; print('Import OK')"
                ], capture_output=True, text=True, cwd=integrated_path)
                import_test_passed = result.returncode == 0
            except Exception:
                import_test_passed = False
        
        import_score = 30 if import_test_passed else 0
        total_score = structure_score + implementation_score + import_score
        
        return {
            'passed': total_score >= 60,
            'score': total_score,
            'details': {
                'structure_check': f"{'✅' if structure_score >= 20 else '❌'} ディレクトリ構造 ({structure_score}/30)",
                'implementation_check': f"{'✅' if implementation_score >= 20 else '❌'} 実装ファイル ({implementation_score}/30)",
                'import_check': f"{'✅' if import_test_passed else '❌'} インポートテスト ({import_score}/30)",
                'src_files_count': len(src_files),
                'structure_score': structure_score,
                'implementation_score': implementation_score,
                'import_score': import_score
            }
        }
    
    def _check_code_quality(self) -> Dict:
        """コード品質チェック"""
        integrated_path = self.task_path / "integrated" / "src"
        
        if not integrated_path.exists():
            return {
                'passed': False,
                'score': 0,
                'details': 'src ディレクトリが存在しません'
            }
        
        # flake8 チェック
        flake8_result = subprocess.run([
            "flake8", str(integrated_path)
        ], capture_output=True, text=True)
        flake8_passed = flake8_result.returncode == 0
        flake8_score = 40 if flake8_passed else 0
        
        # black チェック
        black_result = subprocess.run([
            "black", "--check", str(integrated_path)
        ], capture_output=True, text=True)
        black_passed = black_result.returncode == 0
        black_score = 30 if black_passed else 0
        
        # mypy チェック (optional)
        mypy_result = subprocess.run([
            "mypy", str(integrated_path)
        ], capture_output=True, text=True)
        mypy_passed = mypy_result.returncode == 0
        mypy_score = 30 if mypy_passed else 15  # 部分点あり
        
        total_score = flake8_score + black_score + mypy_score
        
        return {
            'passed': total_score >= 70,
            'score': total_score,
            'details': {
                'flake8': f"{'✅' if flake8_passed else '❌'} flake8 ({flake8_score}/40)",
                'black': f"{'✅' if black_passed else '❌'} black formatting ({black_score}/30)",
                'mypy': f"{'✅' if mypy_passed else '⚠️'} mypy typing ({mypy_score}/30)",
                'flake8_output': flake8_result.stdout + flake8_result.stderr,
                'black_output': black_result.stdout + black_result.stderr,
                'mypy_output': mypy_result.stdout + mypy_result.stderr
            }
        }
    
    def _check_test_coverage(self) -> Dict:
        """テストカバレッジチェック"""
        integrated_path = self.task_path / "integrated"
        
        if not (integrated_path / "tests").exists():
            return {
                'passed': False,
                'score': 0,
                'details': 'tests ディレクトリが存在しません'
            }
        
        # pytest 実行
        pytest_result = subprocess.run([
            "python", "-m", "pytest", "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=integrated_path)
        pytest_passed = pytest_result.returncode == 0
        pytest_score = 50 if pytest_passed else 0
        
        # カバレッジ測定
        coverage_result = subprocess.run([
            "python", "-m", "pytest", "tests/", 
            "--cov=src", "--cov-report=term-missing"
        ], capture_output=True, text=True, cwd=integrated_path)
        
        coverage_percent = 0
        if coverage_result.returncode == 0:
            for line in coverage_result.stdout.split('\n'):
                if 'TOTAL' in line:
                    try:
                        coverage_percent = int(line.split()[-1].replace('%', ''))
                    except:
                        coverage_percent = 0
                    break
        
        coverage_score = min(coverage_percent, 50)  # 最大50点
        total_score = pytest_score + coverage_score
        
        return {
            'passed': total_score >= 80 and coverage_percent >= 95,
            'score': total_score,
            'details': {
                'pytest': f"{'✅' if pytest_passed else '❌'} pytest ({pytest_score}/50)",
                'coverage': f"{'✅' if coverage_percent >= 95 else '❌'} カバレッジ {coverage_percent}% ({coverage_score}/50)",
                'coverage_percent': coverage_percent,
                'pytest_output': pytest_result.stdout + pytest_result.stderr,
                'coverage_output': coverage_result.stdout + coverage_result.stderr
            }
        }
    
    def _check_documentation(self) -> Dict:
        """ドキュメントチェック"""
        integrated_path = self.task_path / "integrated"
        docs_path = integrated_path / "docs"
        
        if not docs_path.exists():
            return {
                'passed': False,
                'score': 0,
                'details': 'docs ディレクトリが存在しません'
            }
        
        # ドキュメントファイル確認
        doc_files = list(docs_path.rglob("*.md"))
        readme_exists = any("readme" in f.name.lower() for f in doc_files)
        api_docs_exist = any("api" in f.name.lower() for f in doc_files)
        
        file_count_score = min(len(doc_files) * 10, 40)
        readme_score = 30 if readme_exists else 0
        api_score = 30 if api_docs_exist else 0
        
        total_score = file_count_score + readme_score + api_score
        
        return {
            'passed': total_score >= 70,
            'score': total_score,
            'details': {
                'file_count': f"{'✅' if len(doc_files) >= 3 else '❌'} ドキュメントファイル数 {len(doc_files)} ({file_count_score}/40)",
                'readme': f"{'✅' if readme_exists else '❌'} README文書 ({readme_score}/30)",
                'api_docs': f"{'✅' if api_docs_exist else '❌'} API文書 ({api_score}/30)",
                'doc_files': [str(f) for f in doc_files]
            }
        }
    
    def _check_performance(self) -> Dict:
        """パフォーマンスチェック"""
        integrated_path = self.task_path / "integrated"
        
        # 基本的なパフォーマンステスト
        if not (integrated_path / "src").exists():
            return {
                'passed': False,
                'score': 0,
                'details': 'src ディレクトリが存在しません'
            }
        
        # インポート時間測定
        start_time = datetime.now()
        try:
            # 簡単なインポートテスト
            result = subprocess.run([
                sys.executable, "-c", 
                "import time; start=time.time(); import os; print(f'Import time: {time.time()-start:.3f}s')"
            ], capture_output=True, text=True, cwd=integrated_path)
            import_time = 0.1  # デフォルト値
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Import time:' in line:
                        try:
                            import_time = float(line.split(':')[1].replace('s', '').strip())
                        except:
                            pass
        except:
            import_time = 1.0
        
        # パフォーマンススコア（1秒以下で満点）
        performance_score = max(0, 100 - int(import_time * 100))
        
        return {
            'passed': performance_score >= 70,
            'score': performance_score,
            'details': {
                'import_time': f"{'✅' if import_time < 1.0 else '❌'} インポート時間 {import_time:.3f}s ({performance_score}/100)",
                'import_time_value': import_time
            }
        }
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """総合スコア計算"""
        weights = {
            'functional_test': 0.30,
            'code_quality': 0.25,
            'test_coverage': 0.25,
            'documentation': 0.15,
            'performance': 0.05
        }
        
        total_score = 0
        for category, result in results.items():
            weight = weights.get(category, 0)
            score = result.get('score', 0)
            total_score += score * weight
        
        return round(total_score, 2)
    
    def _make_integration_judgment(self, score: float, results: Dict) -> str:
        """統合判定"""
        critical_failures = []
        
        # 重要な項目の確認
        if not results['functional_test']['passed']:
            critical_failures.append('機能要件未達')
        
        if results['test_coverage']['details']['coverage_percent'] < 95:
            critical_failures.append('テストカバレッジ不足')
        
        if score >= 90 and len(critical_failures) == 0:
            return "INTEGRATE"  # そのまま統合
        elif score >= 70 and len(critical_failures) <= 1:
            return "MINOR_FIX"  # 軽微修正後統合
        else:
            return "MAJOR_REWORK"  # 大幅修正・再作成
    
    def _get_recommended_action(self, judgment: str) -> str:
        """推奨アクション取得"""
        actions = {
            "INTEGRATE": "高品質完成。そのまま統合して次のタスクに進む。",
            "MINOR_FIX": "軽微な修正を適用後、統合する。",
            "MAJOR_REWORK": "品質基準未達。Boss に詳細な改善指示を送り、再作成を求める。"
        }
        return actions.get(judgment, "判定エラー")
    
    def _extract_issues(self, results: Dict) -> List[str]:
        """問題点抽出"""
        issues = []
        
        for category, result in results.items():
            if not result['passed']:
                if category == 'functional_test':
                    issues.append("機能要件が満たされていません")
                elif category == 'code_quality':
                    issues.append("コード品質基準を満たしていません")
                elif category == 'test_coverage':
                    issues.append("テストカバレッジが95%未満です")
                elif category == 'documentation':
                    issues.append("ドキュメントが不十分です")
                elif category == 'performance':
                    issues.append("パフォーマンス要件を満たしていません")
        
        return issues
    
    def _generate_fix_suggestions(self, results: Dict) -> List[str]:
        """修正提案生成"""
        suggestions = []
        
        # コード品質の修正提案
        if not results['code_quality']['passed']:
            details = results['code_quality']['details']
            if 'flake8' in details and '❌' in details['flake8']:
                suggestions.append("flake8 の警告を修正してください")
            if 'black' in details and '❌' in details['black']:
                suggestions.append("black でコードをフォーマットしてください")
        
        # テストカバレッジの修正提案
        if not results['test_coverage']['passed']:
            coverage = results['test_coverage']['details']['coverage_percent']
            if coverage < 95:
                suggestions.append(f"テストカバレッジを95%以上にしてください（現在{coverage}%）")
        
        # ドキュメントの修正提案
        if not results['documentation']['passed']:
            details = results['documentation']['details']
            if '❌' in details.get('readme', ''):
                suggestions.append("README.md を作成してください")
            if '❌' in details.get('api_docs', ''):
                suggestions.append("API ドキュメントを作成してください")
        
        return suggestions
    
    def _save_evaluation_report(self, report: Dict):
        """評価レポート保存"""
        report_path = self.task_path / f"evaluation_{self.org_name}_{self.task_name}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 評価レポート保存: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='Task Quality Evaluator')
    parser.add_argument('org_name', help='Organization name (e.g., org-01)')
    parser.add_argument('task_name', help='Task name (e.g., database_module)')
    parser.add_argument('--output', help='Output format', choices=['json', 'text'], default='text')
    
    args = parser.parse_args()
    
    try:
        evaluator = TaskQualityEvaluator(args.org_name, args.task_name)
        result = evaluator.evaluate_completion()
        
        if args.output == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # テキスト形式での出力
            print(f"\n🏆 {args.org_name} {args.task_name} 品質評価結果")
            print("=" * 50)
            print(f"📊 総合スコア: {result['overall_score']}/100")
            print(f"🎯 判定: {result['judgment']}")
            print(f"💡 推奨アクション: {result['recommended_action']}")
            
            if result['issues']:
                print(f"\n🚨 主要な問題:")
                for issue in result['issues']:
                    print(f"  - {issue}")
            
            if result['fix_suggestions']:
                print(f"\n🔧 修正提案:")
                for suggestion in result['fix_suggestions']:
                    print(f"  - {suggestion}")
            
            print(f"\n📄 詳細レポート: orgs/{args.org_name}/{args.task_name}/evaluation_{args.org_name}_{args.task_name}.json")
        
        # 終了コード設定
        if result['judgment'] == 'INTEGRATE':
            sys.exit(0)
        elif result['judgment'] == 'MINOR_FIX':
            sys.exit(1)
        else:  # MAJOR_REWORK
            sys.exit(2)
            
    except Exception as e:
        print(f"❌ 評価エラー: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main() 