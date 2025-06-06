# 外部API統合設計書

*バージョン 0.1 — 2025-06-05*

---

## 目次
1. [概要](#1-概要)
2. [Kaggle API統合](#2-kaggle-api統合)
3. [Google Deep Research API統合](#3-google-deep-research-api統合)
4. [Claude Code API統合](#4-claude-code-api統合)
5. [SaladCloud API統合](#5-saladcloud-api統合)
6. [通知API統合](#6-通知api統合)
7. [共通設計原則](#7-共通設計原則)
8. [実装計画](#8-実装計画)

---

## 1. 概要

### 1.1 設計方針

```yaml
api_integration_principles:
  reliability:
    - "すべてのAPI呼び出しにリトライ機能"
    - "サーキットブレーカーパターンの実装"
    - "タイムアウト設定の統一"
  
  performance:
    - "非同期処理による並行実行"
    - "レスポンスキャッシュの活用"
    - "バッチ処理の最適化"
  
  security:
    - "API トークンの安全な管理"
    - "リクエスト/レスポンスのログ制御"
    - "レート制限の遵守"
  
  maintainability:
    - "統一されたエラーハンドリング"
    - "構造化されたデータモデル"
    - "テスタブルな設計"
```

### 1.2 共通データ構造

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

class APIStatus(Enum):
    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class APIResponse:
    status: APIStatus
    data: Optional[Any]
    error_message: Optional[str]
    response_time: float
    timestamp: datetime
    retry_count: int = 0
```

## 2. Kaggle API統合

### 2.1 認証・設定

```python
@dataclass
class KaggleConfig:
    username: str
    key: str
    base_url: str = "https://www.kaggle.com/api/v1"
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit: int = 200  # per hour

class KaggleClient:
    def __init__(self, config: KaggleConfig):
        self.config = config
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.rate_limit, window=3600)
    
    def _create_session(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            auth=(self.config.username, self.config.key),
            timeout=self.config.timeout,
            headers={"User-Agent": "kaggle-agent/0.1"}
        )
```

### 2.2 データモデル

```python
@dataclass
class Competition:
    id: str
    title: str
    url: str
    description: str
    category: str
    reward: Optional[int]
    team_count: int
    user_has_entered: bool
    user_rank: Optional[int]
    deadline: datetime
    evaluation_metric: str
    submission_count: int
    max_team_size: int
    
    @property
    def is_active(self) -> bool:
        return datetime.now() < self.deadline

@dataclass
class DatasetInfo:
    competition_id: str
    total_bytes: int
    files: List[Dict[str, Any]]
    download_url: str
    last_modified: datetime

@dataclass
class SubmissionResult:
    id: str
    competition_id: str
    public_score: Optional[float]
    private_score: Optional[float]
    status: str
    submitted_at: datetime
    file_name: str
```

### 2.3 主要メソッド

```python
class KaggleClient:
    async def list_competitions(
        self, 
        category: Optional[str] = None,
        group: str = "general",
        sort_by: str = "deadline"
    ) -> List[Competition]:
        """アクティブなコンペティション一覧を取得"""
        
    async def get_competition_metadata(
        self, 
        competition_id: str
    ) -> Competition:
        """特定のコンペティション詳細を取得"""
        
    async def download_dataset(
        self, 
        competition_id: str,
        download_path: str
    ) -> DatasetInfo:
        """データセットをダウンロード"""
        
    async def submit_predictions(
        self, 
        competition_id: str,
        file_path: str,
        message: str
    ) -> SubmissionResult:
        """予測結果を提出"""
        
    async def get_submission_status(
        self, 
        submission_id: str
    ) -> SubmissionResult:
        """提出状況を確認"""
```

## 3. Google Agentspace Deep Research統合

### 3.1 設定・認証

```python
@dataclass
class AgentspaceConfig:
    project_id: str
    app_id: str
    assistant_id: str = "default_assistant"
    base_url: str = "https://discoveryengine.googleapis.com/v1alpha"
    timeout: float = 60.0
    max_retries: int = 3
    rate_limit: int = 100  # per hour
    max_query_length: int = 1000

class AgentspaceClient:
    def __init__(self, config: AgentspaceConfig):
        self.config = config
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.rate_limit, window=3600)
    
    def _create_session(self) -> httpx.AsyncClient:
        # Google Cloud認証用のセッション作成
        return httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json"}
        )
    
    async def _get_auth_token(self) -> str:
        """Google Cloud認証トークンを取得"""
        # gcloud auth print-access-token の実装
        pass
```

### 3.2 データモデル

```python
@dataclass
class ResearchQuery:
    text: str
    domain: str = "machine_learning"
    time_range: Optional[str] = "2020-2025"
    max_results: int = 10
    include_code: bool = True

@dataclass
class ResearchResult:
    title: str
    summary: str
    url: Optional[str]
    authors: List[str]
    publication_date: Optional[datetime]
    relevance_score: float
    technical_difficulty: str  # "beginner", "intermediate", "advanced"
    implementation_complexity: str  # "low", "medium", "high"
    resource_requirements: Dict[str, Any]

@dataclass
class RankedApproach:
    approach_name: str
    research_results: List[ResearchResult]
    overall_score: float
    feasibility_score: float
    innovation_score: float
    resource_score: float
    synthesis: str
```

### 3.3 主要メソッド

```python
class AgentspaceClient:
    async def stream_research(
        self, 
        query: str
    ) -> AsyncGenerator[ResearchResult, None]:
        """Deep Researchクエリをストリーミング実行"""
        auth_token = await self._get_auth_token()
        url = f"{self.config.base_url}/projects/{self.config.project_id}/locations/global/collections/default_collection/engines/{self.config.app_id}/assistants/{self.config.assistant_id}:streamAssist"
        
        payload = {
            "query": {"text": query},
            "answerGenerationMode": "research"
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "X-Goog-User-Project": self.config.project_id
        }
        
        # ストリーミングレスポンスの処理
        async with self.session.stream("POST", url, json=payload, headers=headers) as response:
            async for chunk in response.aiter_text():
                yield self._parse_research_chunk(chunk)
        
    async def execute_research(
        self, 
        query: ResearchQuery
    ) -> List[ResearchResult]:
        """研究クエリを実行（非ストリーミング）"""
        results = []
        async for result in self.stream_research(query.text):
            results.append(result)
        return results
        
    async def batch_research(
        self, 
        queries: List[ResearchQuery],
        max_concurrent: int = 3
    ) -> Dict[str, List[ResearchResult]]:
        """複数クエリの並行実行"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single_query(query: ResearchQuery):
            async with semaphore:
                return await self.execute_research(query)
        
        tasks = {query.text: execute_single_query(query) for query in queries}
        return await asyncio.gather(*tasks.values(), return_exceptions=True)
```

## 4. Claude Code API統合

### 4.1 設定・認証

```python
@dataclass
class ClaudeConfig:
    api_key: str
    model: str = "claude-3-sonnet-20240229"
    base_url: str = "https://api.anthropic.com/v1"
    timeout: float = 120.0
    max_retries: int = 3
    rate_limit: int = 1000  # per hour
    max_tokens: int = 4000

class ClaudeClient:
    def __init__(self, config: ClaudeConfig):
        self.config = config
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.rate_limit, window=3600)
```

### 4.2 データモデル

```python
@dataclass
class CodeGenerationRequest:
    task_description: str
    requirements: List[str]
    constraints: List[str]
    preferred_libraries: List[str]
    target_framework: str  # "pytorch", "tensorflow", "sklearn"
    complexity_level: str  # "baseline", "intermediate", "advanced"

@dataclass
class CodeBundle:
    main_script: str
    training_script: str
    inference_script: str
    requirements_txt: str
    dockerfile: str
    documentation: str
    estimated_runtime: float  # hours
    estimated_memory: float  # GB

@dataclass
class HyperParameterConfig:
    model_params: Dict[str, Any]
    training_params: Dict[str, Any]
    optimization_strategy: str
    search_space: Dict[str, Any]
```

### 4.3 主要メソッド

```python
class ClaudeClient:
    async def generate_baseline_code(
        self, 
        request: CodeGenerationRequest
    ) -> CodeBundle:
        """ベースラインコードを生成"""
        
    async def optimize_hyperparameters(
        self, 
        code_bundle: CodeBundle,
        performance_target: float
    ) -> HyperParameterConfig:
        """ハイパーパラメータを最適化"""
        
    async def review_and_improve(
        self, 
        code: str,
        feedback: str
    ) -> str:
        """コードレビューと改善"""
```

## 5. SaladCloud API統合

### 5.1 設定・認証

```python
@dataclass
class SaladCloudConfig:
    api_key: str
    organization_name: str
    base_url: str = "https://api.salad.com/api/public"
    timeout: float = 60.0
    max_retries: int = 3
    rate_limit: int = 500  # per hour

class SaladCloudClient:
    def __init__(self, config: SaladCloudConfig):
        self.config = config
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.rate_limit, window=3600)
```

### 5.2 データモデル

```python
@dataclass
class GPUSpec:
    gpu_type: str  # "GTX1650", "RTX3060", "RTX4090"
    vram_gb: int
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    hourly_price: float

@dataclass
class GPUInstance:
    instance_id: str
    spec: GPUSpec
    status: str  # "pending", "running", "stopping", "stopped"
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    total_cost: float

@dataclass
class TrainingJob:
    job_id: str
    instance_id: str
    docker_image: str
    command: str
    environment: Dict[str, str]
    status: str  # "queued", "running", "completed", "failed"
    progress: float  # 0.0 to 1.0
    logs_url: str
    artifacts_url: Optional[str]
```

### 5.3 主要メソッド

```python
class SaladCloudClient:
    async def list_available_gpus(
        self, 
        min_vram: int = 8,
        max_price: float = 0.20
    ) -> List[GPUSpec]:
        """利用可能なGPUをリスト"""
        
    async def create_instance(
        self, 
        spec: GPUSpec,
        container_image: str
    ) -> GPUInstance:
        """GPUインスタンスを作成"""
        
    async def start_training_job(
        self, 
        instance: GPUInstance,
        job_config: TrainingJob
    ) -> TrainingJob:
        """学習ジョブを開始"""
        
    async def monitor_job(
        self, 
        job_id: str
    ) -> TrainingJob:
        """ジョブの進捗を監視"""
        
    async def terminate_instance(
        self, 
        instance_id: str
    ) -> bool:
        """インスタンスを終了"""
```

## 6. 通知API統合

### 6.1 Slack統合

```python
@dataclass
class SlackConfig:
    bot_token: str
    channel_id: str
    base_url: str = "https://slack.com/api"
    timeout: float = 30.0
    rate_limit: int = 50  # per minute

@dataclass
class DecisionOption:
    id: str
    title: str
    description: str
    emoji: str
    consequences: List[str]

class SlackClient:
    async def send_decision_request(
        self, 
        context: str,
        options: List[DecisionOption],
        timeout_minutes: int = 30
    ) -> str:
        """判断要求を送信"""
        
    async def wait_for_reaction(
        self, 
        message_id: str,
        timeout_seconds: int = 1800
    ) -> Optional[str]:
        """リアクション待ち"""
```

## 7. 共通設計原則

### 7.1 エラーハンドリング

```python
class APIException(Exception):
    def __init__(self, api_name: str, error_code: str, message: str):
        self.api_name = api_name
        self.error_code = error_code
        self.message = message
        super().__init__(f"{api_name}: {error_code} - {message}")

class RateLimitExceeded(APIException):
    def __init__(self, api_name: str, retry_after: int):
        self.retry_after = retry_after
        super().__init__(api_name, "RATE_LIMITED", f"Retry after {retry_after}s")

async def with_retry(
    func: callable,
    max_attempts: int = 3,
    backoff_multiplier: float = 2.0
) -> Any:
    """指数バックオフ付きリトライ"""
    for attempt in range(max_attempts):
        try:
            return await func()
        except RateLimitExceeded as e:
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = backoff_multiplier ** attempt
            await asyncio.sleep(delay)
```

### 7.2 レート制限管理

```python
class RateLimiter:
    def __init__(self, max_calls: int, window: int):
        self.max_calls = max_calls
        self.window = window
        self.calls: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        async with self._lock:
            now = time.time()
            # 古い記録を削除
            self.calls = [call for call in self.calls if now - call < self.window]
            
            if len(self.calls) >= self.max_calls:
                return False
            
            self.calls.append(now)
            return True
    
    async def wait_for_capacity(self) -> None:
        while not await self.acquire():
            await asyncio.sleep(1)
```

## 8. 実装計画

### 8.1 開発フェーズ

```yaml
phase_1_foundation:
  duration: "1週間"
  deliverables:
    - "共通APIクライアント基盤"
    - "エラーハンドリング・リトライ機構"
    - "レート制限管理"
    - "基本的なユニットテスト"

phase_2_core_apis:
  duration: "2週間"
  deliverables:
    - "Kaggle API統合完了"
    - "Claude Code API統合完了"
    - "基本的な統合テスト"

phase_3_advanced_apis:
  duration: "2週間"
  deliverables:
    - "Deep Research API統合完了"
    - "SaladCloud API統合完了"
    - "通知API統合完了"

phase_4_optimization:
  duration: "1週間"
  deliverables:
    - "パフォーマンス最適化"
    - "エラー処理の改善"
    - "包括的なテストスイート"
```

### 8.2 次のステップ

1. **データベーススキーマ設計** - API データの永続化
2. **設定管理システム設計** - API 認証情報の管理
3. **モニタリング設計** - API パフォーマンスの監視

---

外部API統合設計が完了しました。次はどの部分を詳細化しますか？ 