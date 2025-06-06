# プロジェクト構造設計

## 概要

Kaggle Agent システムの実装における包括的なディレクトリ構造とファイル組織の定義。アーキテクチャで定義されたモノリシック-モジュラー設計に基づく構造化。

## ルートディレクトリ構造

```
kaggle_agent/
├── README.md                           # プロジェクト概要
├── pyproject.toml                      # Python プロジェクト設定
├── requirements.txt                    # 依存関係（互換性用）
├── .env.example                        # 環境変数テンプレート
├── .gitignore                          # Git 除外設定
├── .dockerignore                       # Docker 除外設定
├── Dockerfile                          # メインアプリケーション用
├── docker-compose.yml                  # 開発環境用
├── docker-compose.prod.yml             # 本番環境用
├── Makefile                            # 開発タスク自動化
├── multi_agent_config.yaml             # マルチエージェント設定
│
├── docs/                               # ドキュメント
├── src/                                # ソースコード
├── tests/                              # テストコード  
├── scripts/                            # ユーティリティスクリプト
├── config/                             # 設定ファイル
├── data/                               # データディレクトリ
├── logs/                               # ログファイル
├── artifacts/                          # 成果物（モデル、レポート等）
├── migrations/                         # データベース移行
├── deployment/                         # デプロイメント設定
│
├── orgs/                               # マルチエージェント開発ワークスペース
│   ├── org-01/                         # Core Infrastructure 組織
│   │   ├── 01boss/                     # Boss Agent ワークスペース
│   │   │   ├── CLAUDE.md               # Boss Agent 専用指示書
│   │   │   ├── evaluation/             # 評価レポート・統合判断
│   │   │   └── [評価対象ファイル]
│   │   ├── 01worker-a/                 # Worker A ワークスペース
│   │   │   ├── CLAUDE.md               # Worker A 専用指示書
│   │   │   ├── current_task.md         # 現在のタスク情報
│   │   │   ├── src/                    # パフォーマンス重視実装
│   │   │   ├── tests/                  # テストコード
│   │   │   └── docs/                   # 実装ドキュメント
│   │   ├── 01worker-b/                 # Worker B ワークスペース
│   │   │   ├── CLAUDE.md               # Worker B 専用指示書
│   │   │   ├── current_task.md         # 現在のタスク情報
│   │   │   ├── src/                    # 保守性重視実装
│   │   │   ├── tests/                  # テストコード
│   │   │   └── docs/                   # 実装ドキュメント
│   │   └── 01worker-c/                 # Worker C ワークスペース
│   │       ├── CLAUDE.md               # Worker C 専用指示書
│   │       ├── current_task.md         # 現在のタスク情報
│   │       ├── src/                    # 拡張性重視実装
│   │       ├── tests/                  # テストコード
│   │       └── docs/                   # 実装ドキュメント
│   │
│   ├── org-02/                         # Application Modules 組織
│   │   ├── 02boss/                     # Boss Agent ワークスペース
│   │   ├── 02worker-a/                 # パフォーマンス重視 Worker
│   │   ├── 02worker-b/                 # 保守性重視 Worker
│   │   └── 02worker-c/                 # 拡張性重視 Worker
│   │
│   ├── org-03/                         # Interfaces 組織
│   │   ├── 03boss/                     # Boss Agent ワークスペース
│   │   ├── 03worker-a/                 # パフォーマンス重視 Worker
│   │   ├── 03worker-b/                 # 保守性重視 Worker
│   │   └── 03worker-c/                 # 拡張性重視 Worker
│   │
│   └── org-04/                         # Quality Assurance 組織
│       ├── 04boss/                     # Boss Agent ワークスペース
│       ├── 04worker-a/                 # パフォーマンス重視 Worker
│       ├── 04worker-b/                 # 保守性重視 Worker
│       └── 04worker-c/                 # 拡張性重視 Worker
│
└── shared/                             # マルチエージェント共通リソース
    ├── prompts/                        # プロンプト管理システム
    │   ├── templates/                  # プロンプトテンプレート
    │   │   ├── boss/                   # Boss Agent用プロンプト
    │   │   │   ├── base_prompt.md      # 基本役割プロンプト
    │   │   │   ├── evaluation_prompt.md # 評価専用プロンプト
    │   │   │   ├── integration_prompt.md # 統合判断プロンプト
    │   │   │   └── context_variables.yaml # コンテキスト変数定義
    │   │   ├── worker_a/               # Worker A用プロンプト（パフォーマンス重視）
    │   │   │   ├── base_prompt.md      # 基本役割プロンプト
    │   │   │   ├── implementation_prompt.md # 実装専用プロンプト
    │   │   │   ├── tdd_prompt.md       # TDD専用プロンプト
    │   │   │   └── context_variables.yaml # コンテキスト変数定義
    │   │   ├── worker_b/               # Worker B用プロンプト（保守性重視）
    │   │   │   ├── base_prompt.md
    │   │   │   ├── implementation_prompt.md
    │   │   │   ├── tdd_prompt.md
    │   │   │   └── context_variables.yaml
    │   │   └── worker_c/               # Worker C用プロンプト（拡張性重視）
    │   │       ├── base_prompt.md
    │   │       ├── implementation_prompt.md
    │   │       ├── tdd_prompt.md
    │   │       └── context_variables.yaml
    │   ├── generators/                 # プロンプト生成器
    │   │   ├── prompt_builder.py       # 動的プロンプト構築
    │   │   ├── context_injector.py     # コンテキスト情報注入
    │   │   └── template_processor.py   # テンプレート処理
    │   ├── versions/                   # プロンプトバージョン管理
    │   │   ├── v1.0/                   # バージョン1.0
    │   │   ├── v1.1/                   # バージョン1.1
    │   │   └── current -> v1.1         # 現在バージョンのシンボリックリンク
    │   └── config/                     # プロンプト設定
    │       ├── prompt_config.yaml      # 全体設定
    │       ├── role_mappings.yaml      # ロール別マッピング
    │       └── context_sources.yaml    # コンテキスト情報源定義
    │
    ├── instructions/                   # 共通指示書・ガイドライン
    │   ├── roles/                      # ロール別定義
    │   │   ├── boss.md                 # Boss Agent 役割定義
    │   │   └── worker.md               # Worker Agent 役割定義
    │   ├── current_tasks/              # 現在のタスク情報
    │   └── development_guidelines.md   # 開発ガイドライン
    ├── evaluation_criteria/            # 評価基準
    │   ├── code_quality.md             # コード品質基準
    │   ├── test_coverage.md            # テストカバレッジ基準
    │   ├── performance.md              # パフォーマンス基準
    │   ├── maintainability.md          # 保守性基準
    │   └── documentation.md            # ドキュメント基準
    ├── templates/                      # テンプレート
    │   ├── claude/                     # CLAUDE.md テンプレート
    │   │   ├── boss_template.md        # Boss用テンプレート
    │   │   └── worker_template.md      # Worker用テンプレート
    │   └── evaluation/                 # 評価レポートテンプレート
    │       └── evaluation_report.md    # 評価レポート形式
    ├── specifications/                 # 技術仕様書
    │   └── kaggle_agent/               # Kaggle Agent 仕様
    │       ├── workflow_spec.md
    │       ├── database_spec.md
    │       ├── api_spec.md
    │       └── [モジュール別仕様]
    └── tech_stack/                     # 技術スタック定義
        └── kaggle_agent/
            ├── common_stack.md         # 共通技術スタック
            └── [モジュール別スタック]
```

## src/ ディレクトリ詳細

```
src/
├── kaggle_agent/                       # メインパッケージ
│   ├── __init__.py
│   ├── main.py                         # アプリケーションエントリーポイント
│   ├── settings.py                     # 設定管理
│   ├── exceptions.py                   # カスタム例外定義
│   ├── constants.py                    # 定数定義
│   │
│   ├── core/                           # コア機能
│   │   ├── __init__.py
│   │   ├── workflow/                   # ワークフロー管理
│   │   │   ├── __init__.py
│   │   │   ├── engine.py               # Prefect/LangGraphエンジン
│   │   │   ├── state_machine.py        # ステートマシン
│   │   │   ├── orchestrator.py         # オーケストレーション
│   │   │   └── tasks.py                # タスク定義
│   │   │
│   │   ├── database/                   # データベース層
│   │   │   ├── __init__.py
│   │   │   ├── connection.py           # 接続管理
│   │   │   ├── models.py               # SQLAlchemy モデル
│   │   │   ├── repositories.py         # リポジトリパターン
│   │   │   ├── migrations.py           # 移行ヘルパー
│   │   │   └── queries.py              # 複雑なクエリ
│   │   │
│   │   ├── cache/                      # キャッシュ層
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py         # Redis クライアント
│   │   │   ├── cache_manager.py        # キャッシュ管理
│   │   │   └── decorators.py           # キャッシュデコレータ
│   │   │
│   │   ├── storage/                    # ストレージ層
│   │   │   ├── __init__.py
│   │   │   ├── s3_client.py            # S3/MinIO クライアント
│   │   │   ├── file_manager.py         # ファイル管理
│   │   │   └── artifacts.py            # 成果物管理
│   │   │
│   │   ├── messaging/                  # メッセージング
│   │   │   ├── __init__.py
│   │   │   ├── queue_manager.py        # キュー管理
│   │   │   ├── event_bus.py            # イベントバス
│   │   │   └── notifications.py        # 通知システム
│   │   │
│   │   ├── monitoring/                 # 監視・メトリクス
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py              # メトリクス収集
│   │   │   ├── logging.py              # ログ設定
│   │   │   ├── health_check.py         # ヘルスチェック
│   │   │   └── profiler.py             # パフォーマンス分析
│   │   │
│   │   └── security/                   # セキュリティ
│   │       ├── __init__.py
│   │       ├── auth.py                 # 認証管理
│   │       ├── encryption.py           # 暗号化
│   │       ├── vault_client.py         # Vault 連携
│   │       └── rate_limiter.py         # レート制限
│   │
│   ├── modules/                        # アプリケーションモジュール
│   │   ├── __init__.py
│   │   │
│   │   ├── competition_discovery/      # コンペティション発見
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # メインサービス
│   │   │   ├── kaggle_client.py        # Kaggle API クライアント
│   │   │   ├── recommender.py          # 推薦システム
│   │   │   ├── filter.py               # フィルタリング
│   │   │   ├── scorer.py               # 難易度スコアリング
│   │   │   ├── models.py               # データモデル
│   │   │   └── tasks.py                # Workflow タスク
│   │   │
│   │   ├── research/                   # 調査モジュール
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # メインサービス
│   │   │   ├── apis/                   # 外部API統合
│   │   │   │   ├── __init__.py
│   │   │   │   ├── google_deep_research.py
│   │   │   │   ├── arxiv.py
│   │   │   │   ├── kaggle_datasets.py
│   │   │   │   └── base_client.py
│   │   │   ├── processors/             # データ処理
│   │   │   │   ├── __init__.py
│   │   │   │   ├── paper_processor.py
│   │   │   │   ├── solution_processor.py
│   │   │   │   └── insight_extractor.py
│   │   │   ├── query_builder.py        # クエリ構築
│   │   │   ├── relevance_scorer.py     # 関連性評価
│   │   │   ├── models.py               # データモデル
│   │   │   └── tasks.py                # Workflow タスク
│   │   │
│   │   ├── code_generation/            # コード生成
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # メインサービス
│   │   │   ├── claude_client.py        # Claude Code API
│   │   │   ├── generators/             # コードジェネレータ
│   │   │   │   ├── __init__.py
│   │   │   │   ├── eda_generator.py
│   │   │   │   ├── preprocessing_generator.py
│   │   │   │   ├── model_generator.py
│   │   │   │   ├── training_generator.py
│   │   │   │   └── submission_generator.py
│   │   │   ├── validators/             # コードバリデータ
│   │   │   │   ├── __init__.py
│   │   │   │   ├── syntax_validator.py
│   │   │   │   ├── dependency_validator.py
│   │   │   │   └── security_validator.py
│   │   │   ├── templates/              # コードテンプレート
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_template.py
│   │   │   │   └── problem_specific/
│   │   │   ├── models.py               # データモデル
│   │   │   └── tasks.py                # Workflow タスク
│   │   │
│   │   ├── gpu_management/             # GPU管理
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # メインサービス
│   │   │   ├── providers/              # GPUプロバイダー
│   │   │   │   ├── __init__.py
│   │   │   │   ├── salad_cloud.py
│   │   │   │   ├── vast_ai.py
│   │   │   │   ├── lambda_labs.py
│   │   │   │   └── base_provider.py
│   │   │   ├── provisioner.py          # プロビジョニング
│   │   │   ├── monitor.py              # 使用量監視
│   │   │   ├── cost_optimizer.py       # コスト最適化
│   │   │   ├── session_manager.py      # セッション管理
│   │   │   ├── models.py               # データモデル
│   │   │   └── tasks.py                # Workflow タスク
│   │   │
│   │   ├── training/                   # 訓練実行（GPU管理から分離）
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # メインサービス
│   │   │   ├── job_manager.py          # ジョブ管理
│   │   │   ├── executor.py             # 実行エンジン
│   │   │   ├── monitor.py              # 進捗監視
│   │   │   ├── hyperparameter_tuner.py # ハイパーパラメータ調整
│   │   │   ├── model_registry.py       # モデル登録
│   │   │   ├── models.py               # データモデル
│   │   │   └── tasks.py                # Workflow タスク
│   │   │
│   │   ├── submission/                 # 提出管理
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # メインサービス
│   │   │   ├── kaggle_submitter.py     # Kaggle 提出クライアント
│   │   │   ├── file_validator.py       # ファイルバリデーション
│   │   │   ├── score_tracker.py        # スコア追跡
│   │   │   ├── ranking_analyzer.py     # 順位分析
│   │   │   ├── models.py               # データモデル
│   │   │   └── tasks.py                # Workflow タスク
│   │   │
│   │   └── human_loop/                 # 人的介入
│   │       ├── __init__.py
│   │       ├── service.py              # メインサービス
│   │       ├── intervention_manager.py # 介入管理
│   │       ├── notification_sender.py  # 通知送信
│   │       ├── approval_handler.py     # 承認処理
│   │       ├── escalation_manager.py   # エスカレーション
│   │       ├── dashboard_api.py        # ダッシュボードAPI
│   │       ├── models.py               # データモデル
│   │       └── tasks.py                # Workflow タスク
│   │
│   ├── api/                            # Web API
│   │   ├── __init__.py
│   │   ├── app.py                      # FastAPI アプリケーション
│   │   ├── dependencies.py             # 依存性注入
│   │   ├── middleware.py               # ミドルウェア
│   │   ├── routers/                    # APIルーター
│   │   │   ├── __init__.py
│   │   │   ├── competitions.py
│   │   │   ├── executions.py
│   │   │   ├── submissions.py
│   │   │   ├── interventions.py
│   │   │   ├── metrics.py
│   │   │   └── health.py
│   │   ├── schemas/                    # Pydantic スキーマ
│   │   │   ├── __init__.py
│   │   │   ├── competitions.py
│   │   │   ├── executions.py
│   │   │   ├── submissions.py
│   │   │   └── common.py
│   │   └── responses.py                # 共通レスポンス
│   │
│   ├── cli/                            # CLI インターフェース
│   │   ├── __init__.py
│   │   ├── main.py                     # Click CLI メイン
│   │   ├── commands/                   # CLI コマンド
│   │   │   ├── __init__.py
│   │   │   ├── start.py
│   │   │   ├── stop.py
│   │   │   ├── status.py
│   │   │   ├── deploy.py
│   │   │   └── migrate.py
│   │   └── utils.py                    # CLI ユーティリティ
│   │
│   └── utils/                          # 共通ユーティリティ
│       ├── __init__.py
│       ├── datetime_utils.py           # 日時処理
│       ├── file_utils.py               # ファイル操作
│       ├── json_utils.py               # JSON処理
│       ├── string_utils.py             # 文字列処理
│       ├── validation.py               # バリデーション
│       ├── decorators.py               # デコレータ
│       └── async_utils.py              # 非同期ユーティリティ
```

## tests/ ディレクトリ詳細

```
tests/
├── __init__.py
├── conftest.py                         # pytest 設定
├── fixtures/                           # テストフィクスチャ
│   ├── __init__.py
│   ├── database.py                     # DB フィクスチャ
│   ├── api_responses.py                # API レスポンス
│   └── sample_data.py                  # サンプルデータ
│
├── unit/                               # 単体テスト
│   ├── __init__.py
│   ├── core/                           # コア機能テスト
│   │   ├── __init__.py
│   │   ├── test_workflow.py
│   │   ├── test_database.py
│   │   ├── test_cache.py
│   │   └── test_storage.py
│   │
│   ├── modules/                        # モジュールテスト
│   │   ├── __init__.py
│   │   ├── test_competition_discovery.py
│   │   ├── test_research.py
│   │   ├── test_code_generation.py
│   │   ├── test_gpu_management.py
│   │   ├── test_training.py
│   │   ├── test_submission.py
│   │   └── test_human_loop.py
│   │
│   └── utils/                          # ユーティリティテスト
│       ├── __init__.py
│       └── test_validators.py
│
├── integration/                        # 統合テスト
│   ├── __init__.py
│   ├── test_api_endpoints.py           # API エンドポイント
│   ├── test_workflow_integration.py    # ワークフロー統合
│   ├── test_database_integration.py    # DB 統合
│   └── test_external_apis.py           # 外部API統合
│
├── e2e/                                # E2Eテスト
│   ├── __init__.py
│   ├── test_full_workflow.py           # 完全ワークフロー
│   ├── test_gpu_training.py            # GPU訓練E2E
│   └── test_submission_flow.py         # 提出フローE2E
│
└── performance/                        # パフォーマンステスト
    ├── __init__.py
    ├── test_load.py                    # 負荷テスト
    ├── test_stress.py                  # ストレステスト
    └── test_gpu_utilization.py         # GPU使用率テスト
```

## config/ ディレクトリ詳細

```
config/
├── default.yaml                       # デフォルト設定
├── development.yaml                   # 開発環境設定
├── staging.yaml                       # ステージング環境設定
├── production.yaml                    # 本番環境設定
├── testing.yaml                       # テスト環境設定
│
├── modules/                           # モジュール別設定
│   ├── competition_discovery.yaml
│   ├── research.yaml
│   ├── code_generation.yaml
│   ├── gpu_management.yaml
│   ├── training.yaml
│   ├── submission.yaml
│   └── human_loop.yaml
│
├── apis/                              # 外部API設定
│   ├── kaggle.yaml
│   ├── google_deep_research.yaml
│   ├── claude_code.yaml
│   ├── salad_cloud.yaml
│   └── slack.yaml
│
└── infrastructure/                    # インフラ設定
    ├── database.yaml
    ├── cache.yaml
    ├── storage.yaml
    ├── monitoring.yaml
    └── security.yaml
```

## scripts/ ディレクトリ詳細

```
scripts/
├── setup/                             # セットアップスクリプト
│   ├── install_dependencies.sh
│   ├── setup_database.py
│   ├── create_admin_user.py
│   └── initialize_config.py
│
├── development/                       # 開発用スクリプト
│   ├── start_dev_environment.sh
│   ├── reset_database.py
│   ├── load_sample_data.py
│   └── generate_test_data.py
│
├── deployment/                        # デプロイメント用
│   ├── build_docker.sh
│   ├── deploy_staging.sh
│   ├── deploy_production.sh
│   └── backup_database.py
│
├── maintenance/                       # 保守用スクリプト
│   ├── cleanup_old_data.py
│   ├── optimize_database.py
│   ├── health_check.py
│   └── metrics_reporter.py
│
└── utilities/                         # ユーティリティ
    ├── data_migration.py
    ├── config_validator.py
    ├── log_analyzer.py
    └── performance_profiler.py
```

## migrations/ ディレクトリ詳細

```
migrations/
├── alembic/                           # Alembic 移行ファイル
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_gpu_management.py
│   │   ├── 003_add_human_interventions.py
│   │   └── 004_add_metrics_partitioning.py
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
│
├── data/                              # データ移行
│   ├── seed_competitions.py
│   ├── seed_configurations.py
│   └── update_schema_v2.py
│
└── rollback/                          # ロールバック用
    ├── rollback_v1_to_v0.py
    └── emergency_rollback.py
```

## deployment/ ディレクトリ詳細

```
deployment/
├── docker/                           # Docker設定
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.scheduler
│   └── docker-compose.override.yml
│
├── kubernetes/                       # Kubernetes設定
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── deployments/
│   │   ├── api-deployment.yaml
│   │   ├── worker-deployment.yaml
│   │   └── scheduler-deployment.yaml
│   ├── services/
│   │   ├── api-service.yaml
│   │   └── worker-service.yaml
│   └── ingress/
│       └── api-ingress.yaml
│
├── terraform/                        # インフラコード
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── vpc/
│   │   ├── database/
│   │   ├── cache/
│   │   └── storage/
│   └── environments/
│       ├── development/
│       ├── staging/
│       └── production/
│
├── ansible/                          # 設定管理
│   ├── playbooks/
│   │   ├── setup-servers.yml
│   │   ├── deploy-app.yml
│   │   └── configure-monitoring.yml
│   ├── inventory/
│   │   ├── development
│   │   ├── staging
│   │   └── production
│   └── roles/
│       ├── common/
│       ├── database/
│       └── monitoring/
│
└── helm/                             # Helm チャート
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── configmap.yaml
    │   └── secret.yaml
    └── charts/
        └── postgresql/
```

## 設定ファイル例

### pyproject.toml
```toml
[build-system]
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
    "langchain>=0.0.340",
    "anthropic>=0.7.0",
    "kaggle>=1.5.0",
    "pydantic>=2.5.0",
    "click>=8.1.0",
    "uvicorn>=0.24.0",
    "python-multipart>=0.0.6",
    "httpx>=0.25.0",
    "cryptography>=41.0.0",
    "prometheus-client>=0.19.0",
    "structlog>=23.2.0",
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
    "pre-commit>=3.5.0",
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

[tool.mypy]
python_version = "3.12"
packages = ["kaggle_agent"]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=kaggle_agent --cov-report=html --cov-report=term"
```

### Makefile
```makefile
.PHONY: help install dev test lint format clean build run

help:           ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:        ## 依存関係をインストール
	pip install -e .[dev]

dev:            ## 開発環境を起動
	docker-compose up -d
	python -m kaggle_agent.cli start --development

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

# マルチエージェント開発環境コマンド
setup-multi-agent: ## マルチエージェント開発環境をセットアップ
	python scripts/setup_multi_agent_env.py

create-task:    ## 新しい開発タスクを作成
	python scripts/task_manager.py create-task

assign-task:    ## タスクをWorkerに割り当て
	python scripts/task_manager.py assign-task

monitor:        ## Worker進捗を監視
	python scripts/task_manager.py monitor

run-cycle:      ## 開発サイクルを実行
	python scripts/task_manager.py run-cycle

agent-status:   ## エージェント状況を表示
	python scripts/task_manager.py status

worktree-list:  ## Git worktree一覧を表示
	git worktree list

worktree-clean: ## 不要なworktreeを削除
	git worktree prune

# プロンプト管理コマンド
update-prompts: ## 全エージェントのプロンプトを更新
	python scripts/prompt_manager.py update-all

generate-claude-md: ## CLAUDE.mdファイルを生成
	python scripts/prompt_manager.py generate-claude-md

validate-prompts: ## プロンプトテンプレートを検証
	python scripts/prompt_manager.py validate

version-prompts: ## プロンプトのバージョンを作成
	python scripts/prompt_manager.py create-version

rollback-prompts: ## プロンプトを前バージョンに戻す
	python scripts/prompt_manager.py rollback

prompt-diff:    ## プロンプトバージョン間の差分表示
	python scripts/prompt_manager.py diff
```

## マルチエージェント開発システム設計

### 概要
Claude Codeエージェントを活用した革新的な並列開発環境。4つの専門組織がgit worktreeベースの独立ワークスペースで競争的開発を行う。

### 組織体制
- **org-01**: Core Infrastructure（ワークフロー、データベース、キャッシュ、ストレージ）
- **org-02**: Application Modules（各機能モジュール）
- **org-03**: Interfaces（API、CLI、UI）
- **org-04**: Quality Assurance（テスト、品質管理、セキュリティ）

### Agent役割分担
- **Boss Agent**: 評価・統合・品質管理を担当
- **Worker A**: パフォーマンス重視の実装
- **Worker B**: 保守性・可読性重視の実装  
- **Worker C**: 拡張性・モジュール性重視の実装

### 開発フロー
1. **タスク生成**: Boss Agentが要件を分析し、3種類の実装アプローチを定義
2. **並列開発**: 3名のWorkerがTDD手法で異なるアプローチを並列実装
3. **品質評価**: Boss Agentが多軸評価（品質・性能・保守性・文書化）を実施
4. **最適選択**: 総合評価に基づき最適実装を選択・統合

### 技術基盤
- **Git Worktree**: 物理的分離による安全な並列開発
- **プロンプト管理**: 階層化・バージョン管理された動的プロンプトシステム
- **CLAUDE.md自動生成**: テンプレート+コンテキストからの指示書自動構築
- **@参照システム**: ファイルパス参照による情報共有
- **自動評価**: メトリクス収集・分析による客観的判断
- **品質ゲート**: 70点以上、テストカバレッジ90%以上で統合可能

### プロンプト管理システム詳細

#### プロンプトフロー
```
1. プロンプトテンプレート（静的）
   ↓ (テンプレート処理)
2. コンテキスト情報注入（動的）
   ↓ (CLAUDE.md生成)
3. エージェントワークスペース配布
   ↓ (Claude Code実行)
4. 成果物生成・評価
   ↓ (フィードバックループ)
5. プロンプト最適化
```

#### エージェント別プロンプト構成

**Boss Agent**
- `base_prompt.md`: 品質評価者としての基本役割
- `evaluation_prompt.md`: 多軸評価（品質・性能・保守性・文書化）手順
- `integration_prompt.md`: 最適実装選択・統合判断ロジック

**Worker A（パフォーマンス重視）**
- `base_prompt.md`: 高性能実装に特化した役割定義
- `implementation_prompt.md`: アルゴリズム最適化・並列化手法
- `tdd_prompt.md`: パフォーマンステスト駆動開発手法

**Worker B（保守性重視）**
- `base_prompt.md`: 可読性・保守性重視の役割定義
- `implementation_prompt.md`: クリーンコード・設計パターン適用
- `tdd_prompt.md`: 可読性重視のテスト設計手法

**Worker C（拡張性重視）**
- `base_prompt.md`: モジュール性・拡張性重視の役割定義
- `implementation_prompt.md`: アーキテクチャ設計・インターフェース定義
- `tdd_prompt.md`: 拡張性を考慮したテスト設計手法

#### 動的コンテキスト情報
- **タスク情報**: 現在の実装対象モジュール・要件
- **進捗状況**: 他Workerの進捗・完了状況
- **評価基準**: 現在のタスクに適用される具体的評価項目
- **制約条件**: 技術スタック・パフォーマンス要件
- **参照情報**: 関連仕様書・API定義・既存実装例

---

この構造は以下の特徴を持ちます：

1. **モジュラー設計**: 各機能モジュールが独立して開発・テスト可能
2. **スケーラビリティ**: 将来的な機能追加に対応しやすい構造
3. **保守性**: 設定、ドキュメント、テストが適切に整理
4. **デプロイメント対応**: Docker、K8s、Terraformでの本格運用を想定
5. **開発効率**: 開発、テスト、デプロイの自動化ツールを完備
6. **マルチエージェント**: 競争的開発による品質向上とイノベーション創出
7. **拡張可能**: 他プロジェクトへの適用可能な汎用的設計
