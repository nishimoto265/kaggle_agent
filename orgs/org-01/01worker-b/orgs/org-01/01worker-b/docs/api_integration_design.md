# API統合設計書

**Version**: 0.1  
**Date**: 2025-06-05  
**総API数**: 5つ

## 概要

Kaggle Agent システムで使用する外部APIの統合設計。各APIの認証、レート制限、エラーハンドリング、データモデルを統一的に管理し、高い可用性と信頼性を提供します。

## 共通設計パターン

### 1. 認証システム

```python
class AuthenticationManager:
    """統一認証管理システム"""
    
    SUPPORTED_TYPES = ["api_key", "bearer_token", "basic_auth", "google_cloud_bearer_token"]
    
    def __init__(self):
        self.rotation_period = timedelta(days=30)
        self.storage_backend = "vault"  # HashiCorp Vault
    
    async def get_credentials(self, api_name: str) -> Dict[str, str]:
        """API別認証情報を取得"""
        pass
    
    async def rotate_credentials(self, api_name: str) -> bool:
        """認証情報の自動ローテーション"""
        pass
```

### 2. レート制限管理

```python
class RateLimitManager:
    """トークンバケット式レート制限"""
    
    def __init__(self):
        self.strategy = "token_bucket"
        self.backoff_strategy = "exponential"
        self.max_backoff = 300  # seconds
        self.jitter_enabled = True
    
    async def acquire_token(self, api_name: str, endpoint: str) -> bool:
        """APIトークン取得"""
        pass
    
    async def handle_rate_limit(self, api_name: str, retry_after: int) -> None:
        """レート制限時の待機処理"""
        pass
```

### 3. 統一リトライポリシー

```python
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    retry_conditions: List[str] = field(default_factory=lambda: [
        "network_timeout", "rate_limit_exceeded", "temporary_server_error"
    ])
    no_retry_conditions: List[str] = field(default_factory=lambda: [
        "authentication_failed", "invalid_request", "resource_not_found"
    ])
    
class RetryManager:
    async def execute_with_retry(self, func: Callable, policy: RetryPolicy) -> Any:
        """統一リトライ実行"""
        pass
```

### 4. タイムアウト設定

```python
@dataclass
class TimeoutSettings:
    connection_timeout: int = 10  # seconds
    read_timeout: int = 30
    total_timeout: int = 60
```

### 5. エラーハンドリング

```python
class ErrorHandler:
    def __init__(self):
        self.log_level = "INFO"
        self.alert_on_consecutive_failures = 3
        self.circuit_breaker_threshold = 5
    
    async def handle_error(self, api_name: str, error: Exception) -> None:
        """統一エラー処理"""
        pass
```

## API別詳細設計

### 1. Kaggle API

**目的**: コンペティション発見・データセット取得・提出管理

#### 基本設定
```yaml
base_url: "https://www.kaggle.com/api/v1"
authentication: "basic_auth"
credentials:
  username: "${KAGGLE_USERNAME}"
  password: "${KAGGLE_KEY}"
```

#### レート制限
- **一般API**: 200リクエスト/時間
- **データダウンロード**: 10リクエスト/時間  
- **提出**: 5リクエスト/日

#### エンドポイント設計

##### コンペティション一覧
```python
@dataclass
class CompetitionsListRequest:
    group: Optional[str] = "general"  # general, entered, inClass
    category: Optional[str] = "all"   # all, featured, research, etc.
    sort_by: Optional[str] = "earliestDeadline"
    page: Optional[int] = 1
    search: Optional[str] = None

class KaggleAPI:
    async def list_competitions(self, request: CompetitionsListRequest) -> List[Competition]:
        """コンペティション一覧取得 (キャッシュ: 1時間)"""
        pass
```

##### コンペティション詳細
```python
async def get_competition_detail(self, competition_id: str) -> Competition:
    """コンペティション詳細取得 (キャッシュ: 6時間)"""
    pass
```

##### データセットダウンロード
```python
async def download_dataset(self, competition_id: str, save_path: str) -> bool:
    """
    データセットダウンロード
    - タイムアウト: 300秒
    - プログレスバー表示
    - 部分ダウンロード対応
    """
    pass
```

##### 提出処理
```python
@dataclass
class SubmissionRequest:
    competition_id: str
    file_path: str
    message: Optional[str] = None

async def submit_predictions(self, request: SubmissionRequest) -> SubmissionResult:
    """提出ファイルアップロード"""
    pass

async def get_submission_status(self, competition_id: str) -> List[SubmissionResult]:
    """提出状況確認 (キャッシュ: 5分)"""
    pass
```

#### データモデル
```python
@dataclass
class Competition:
    id: str
    title: str
    url: str
    description: Optional[str]
    category: str
    reward: Optional[int]
    team_count: int
    user_has_entered: bool
    user_rank: Optional[int]
    deadline: datetime
    evaluation_metric: str

@dataclass
class SubmissionResult:
    id: str
    file_name: str
    public_score: Optional[float]
    private_score: Optional[float]
    status: str  # "complete", "error", "pending"
    submitted_at: datetime
```

### 2. Google Agentspace Deep Research

**目的**: 深層リサーチによる競技解法調査

#### 基本設定
```yaml
base_url: "https://discoveryengine.googleapis.com/v1alpha"
authentication: "google_cloud_bearer_token"
project_id: "${GOOGLE_CLOUD_PROJECT_ID}"
app_id: "${GOOGLE_AGENTSPACE_APP_ID}"
```

#### レート制限
- **一般API**: 100リクエスト/時間
- **ストリーミング**: 50リクエスト/時間

#### エンドポイント設計

```python
@dataclass
class ResearchRequest:
    query: str
    context: Optional[str] = None
    max_tokens: int = 8000
    temperature: float = 0.1
    include_citations: bool = True

@dataclass 
class ResearchResponse:
    answer: str
    citations: List[Citation]
    confidence_score: float
    processing_time_ms: int

class GoogleAgentspaceAPI:
    async def stream_research(self, request: ResearchRequest) -> AsyncIterator[ResearchResponse]:
        """ストリーミングリサーチ実行"""
        pass
```

### 3. Claude API (Anthropic)

**目的**: コード生成・解析・改善提案

#### 基本設定
```yaml
base_url: "https://api.anthropic.com/v1"
authentication: "bearer_token"
api_key: "${ANTHROPIC_API_KEY}"
```

#### レート制限
- **Claude Code**: 1000リクエスト/分
- **Claude Sonnet**: 500リクエスト/分

#### エンドポイント設計

```python
@dataclass
class CodeGenerationRequest:
    prompt: str
    language: str = "python"
    max_tokens: int = 4000
    temperature: float = 0.1
    
@dataclass
class CodeGenerationResponse:
    generated_code: str
    explanation: str
    dependencies: List[str]
    estimated_runtime: Optional[str]

class ClaudeAPI:
    async def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """コード生成"""
        pass
    
    async def analyze_code(self, code: str) -> CodeAnalysisResponse:
        """コード解析・改善提案"""
        pass
```

### 4. GPU Provider APIs

#### Salad Cloud API

**目的**: GPU インスタンス管理

```python
@dataclass
class GPUInstanceRequest:
    instance_type: str  # "rtx4090", "a100", "h100"
    region: str = "us-east-1"
    max_price: float = 0.15  # $/hour
    auto_terminate_hours: int = 24

class SaladCloudAPI:
    async def create_instance(self, request: GPUInstanceRequest) -> GPUInstance:
        """GPU インスタンス作成"""
        pass
    
    async def get_instance_status(self, instance_id: str) -> GPUInstanceStatus:
        """インスタンス状況確認"""
        pass
    
    async def terminate_instance(self, instance_id: str) -> bool:
        """インスタンス終了"""
        pass
```

#### Vast.ai API

**目的**: 代替GPUプロバイダー

```python
class VastAIAPI:
    async def search_offers(self, criteria: GPUSearchCriteria) -> List[GPUOffer]:
        """利用可能GPU検索"""
        pass
    
    async def rent_instance(self, offer_id: str) -> GPUInstance:
        """GPUインスタンス借用"""
        pass
```

### 5. Supabase API

**目的**: データベース・ストレージ・リアルタイム機能

#### 基本設定
```yaml
base_url: "${SUPABASE_URL}"
authentication: "bearer_token"
api_key: "${SUPABASE_ANON_KEY}"
service_role_key: "${SUPABASE_SERVICE_ROLE_KEY}"
```

#### エンドポイント設計

```python
class SupabaseAPI:
    async def insert_data(self, table: str, data: Dict) -> Dict:
        """データ挿入"""
        pass
    
    async def update_data(self, table: str, id: str, data: Dict) -> Dict:
        """データ更新"""
        pass
    
    async def subscribe_changes(self, table: str, callback: Callable) -> None:
        """リアルタイム変更監視"""
        pass
    
    async def upload_file(self, bucket: str, path: str, file: bytes) -> str:
        """ファイルアップロード"""
        pass
```

## 統合APIクライアント設計

### 1. APIクライアントファクトリー

```python
class APIClientFactory:
    """統一APIクライアント管理"""
    
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self.rate_limit_manager = RateLimitManager()
        self.auth_manager = AuthenticationManager()
        self.error_handler = ErrorHandler()
    
    def get_client(self, api_name: str) -> Any:
        """API別クライアント取得"""
        if api_name not in self.clients:
            self.clients[api_name] = self._create_client(api_name)
        return self.clients[api_name]
    
    def _create_client(self, api_name: str) -> Any:
        """API別クライアント作成"""
        pass
```

### 2. 統一レスポンス形式

```python
@dataclass
class APIResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict] = None
    execution_time_ms: Optional[int] = None
    from_cache: bool = False
```

### 3. キャッシュ戦略

```python
class CacheManager:
    """Redis ベース統一キャッシュ"""
    
    def __init__(self):
        self.redis_client = redis.Redis()
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """キャッシュ取得"""
        pass
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """キャッシュ設定"""
        pass
    
    def cache_key(self, api_name: str, endpoint: str, params: Dict) -> str:
        """キャッシュキー生成"""
        param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return f"{api_name}:{endpoint}:{param_hash}"
```

## モニタリング & 監視

### 1. メトリクス収集

```python
@dataclass
class APIMetrics:
    api_name: str
    endpoint: str
    method: str
    response_time_ms: int
    status_code: int
    success: bool
    error_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    async def record_api_call(self, metrics: APIMetrics) -> None:
        """API呼び出しメトリクス記録"""
        pass
    
    async def get_api_health(self, api_name: str) -> APIHealthStatus:
        """API健全性レポート"""
        pass
```

### 2. アラート設定

```python
class AlertManager:
    """API監視アラート"""
    
    ALERT_CONDITIONS = [
        "consecutive_failures >= 3",
        "response_time_ms > 10000",
        "error_rate > 0.1",  # 10%
        "rate_limit_exceeded"
    ]
    
    async def check_alerts(self) -> List[Alert]:
        """アラート条件チェック"""
        pass
```

## セキュリティ考慮事項

### 1. 認証情報管理

- **HashiCorp Vault**: 認証情報の暗号化保存
- **自動ローテーション**: 30日サイクル
- **アクセスログ**: 全認証情報アクセスを記録

### 2. ネットワークセキュリティ

```python
class SecurityMiddleware:
    """API セキュリティミドルウェア"""
    
    def __init__(self):
        self.allowed_domains = [
            "kaggle.com",
            "googleapis.com", 
            "anthropic.com",
            "supabase.com"
        ]
        self.request_timeout = 60
        self.max_payload_size = "10MB"
    
    async def validate_request(self, url: str, payload: bytes) -> bool:
        """リクエスト検証"""
        pass
```

### 3. レート制限回避策

```python
class RateLimitMitigation:
    """レート制限対策"""
    
    async def distribute_requests(self, requests: List[APIRequest]) -> None:
        """リクエスト分散実行"""
        pass
    
    async def priority_queue(self, requests: List[APIRequest]) -> List[APIRequest]:
        """優先度ベース実行順序決定"""
        pass
```

## テスト戦略

### 1. 単体テスト

```python
class TestKaggleAPI:
    @pytest.fixture
    def mock_kaggle_response(self):
        """Kaggle API モックレスポンス"""
        pass
    
    async def test_competition_list(self, mock_kaggle_response):
        """コンペティション一覧テスト"""
        pass
```

### 2. 統合テスト

```python
class TestAPIIntegration:
    async def test_full_workflow(self):
        """完全ワークフローテスト"""
        # 1. コンペティション発見
        # 2. 深層リサーチ実行
        # 3. コード生成
        # 4. GPU でトレーニング
        # 5. 結果提出
        pass
```

### 3. 負荷テスト

```python
class LoadTestRunner:
    async def test_concurrent_requests(self, num_requests: int = 100):
        """並行リクエスト負荷テスト"""
        pass
    
    async def test_rate_limit_handling(self):
        """レート制限処理テスト"""
        pass
```

## パフォーマンス最適化

### 1. 接続プール

```python
class ConnectionPoolManager:
    """HTTP接続プール管理"""
    
    def __init__(self):
        self.pools = {}
        self.max_connections_per_host = 10
        self.max_total_connections = 100
    
    def get_pool(self, api_name: str) -> aiohttp.ClientSession:
        """API別接続プール取得"""
        pass
```

### 2. 並列処理

```python
class ParallelAPIExecutor:
    """並列API実行"""
    
    async def execute_batch(self, requests: List[APIRequest]) -> List[APIResponse]:
        """バッチ実行"""
        pass
    
    async def execute_pipeline(self, pipeline: List[APIRequest]) -> APIResponse:
        """パイプライン実行"""
        pass
```

## 運用 & 保守

### 1. ログ設定

```python
import structlog

logger = structlog.get_logger()

class APILogger:
    async def log_request(self, request: APIRequest) -> None:
        logger.info("api_request", 
                   api_name=request.api_name,
                   endpoint=request.endpoint,
                   method=request.method)
    
    async def log_response(self, response: APIResponse) -> None:
        logger.info("api_response",
                   success=response.success,
                   status_code=response.status_code,
                   execution_time_ms=response.execution_time_ms)
```

### 2. 設定管理

```yaml
# config/api_config.yaml
apis:
  kaggle:
    enabled: true
    timeout: 60
    retry_attempts: 3
    cache_ttl: 3600
    
  google_agentspace:
    enabled: true
    timeout: 120
    retry_attempts: 2
    cache_ttl: 1800
    
  claude:
    enabled: true
    timeout: 30
    retry_attempts: 3
    cache_ttl: 0  # No cache for code generation
```

### 3. バージョン管理

```python
class APIVersionManager:
    """API バージョン管理"""
    
    SUPPORTED_VERSIONS = {
        "kaggle": ["v1"],
        "google_agentspace": ["v1alpha"],
        "claude": ["2024-06-01"],
        "supabase": ["v1"]
    }
    
    async def check_version_compatibility(self, api_name: str, version: str) -> bool:
        """バージョン互換性チェック"""
        pass
```

## 拡張性設計

### 1. 新API追加フレームワーク

```python
class BaseAPIClient:
    """新API追加用ベースクラス"""
    
    def __init__(self, api_name: str, config: APIConfig):
        self.api_name = api_name
        self.config = config
        self.rate_limiter = RateLimitManager()
        self.auth_manager = AuthenticationManager()
    
    async def make_request(self, endpoint: str, **kwargs) -> APIResponse:
        """統一リクエスト実行"""
        pass
```

### 2. プラグインシステム

```python
class APIPlugin:
    """API プラグインインターフェース"""
    
    @abstractmethod
    async def initialize(self) -> None:
        pass
    
    @abstractmethod
    async def call(self, request: APIRequest) -> APIResponse:
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        pass
```

この設計により、5つの外部APIを統一的に管理し、高い可用性、パフォーマンス、セキュリティを提供するAPIレイヤーを構築できます。 