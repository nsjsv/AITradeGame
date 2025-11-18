"""Application constants"""

# API endpoints
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Trading signals
SIGNAL_BUY = 'buy_to_enter'
SIGNAL_SELL = 'sell_to_enter'
SIGNAL_CLOSE = 'close_position'
SIGNAL_HOLD = 'hold'

# Position sides
SIDE_LONG = 'long'
SIDE_SHORT = 'short'

# Leverage limits
MIN_LEVERAGE = 1
MAX_LEVERAGE = 20

# Default values
DEFAULT_INITIAL_CAPITAL = 10000.0
DEFAULT_TRADE_FEE_RATE = 0.001
DEFAULT_TRADING_FREQUENCY_MINUTES = 180
DEFAULT_MARKET_REFRESH_INTERVAL = 5  # seconds
DEFAULT_PORTFOLIO_REFRESH_INTERVAL = 10  # seconds
DEFAULT_HISTORY_COLLECTION_INTERVAL = 60  # seconds
DEFAULT_HISTORY_RESOLUTION = 60  # seconds
DEFAULT_HISTORY_RETENTION_MONTHS = 12
HISTORY_DEFAULT_LIMIT = 500
HISTORY_MAX_LIMIT = 2000
HISTORY_CACHE_TTL = 60  # seconds

# Cache settings
MARKET_DATA_CACHE_TTL = 5  # seconds

# API response codes
SUCCESS_CODE = 'SUCCESS'
ERROR_CODE = 'ERROR'

# ============================================================================
# 日志消息模板
# ============================================================================
LOG_MSG_APP_STARTING = "AITradeGame 正在启动..."
LOG_MSG_APP_READY = "AITradeGame 已就绪"
LOG_MSG_DB_INIT = "正在初始化数据库..."
LOG_MSG_DB_READY = "数据库初始化完成，使用 {db_type}"
LOG_MSG_SERVICES_INIT = "正在初始化服务..."
LOG_MSG_SERVICES_READY = "服务初始化完成"
LOG_MSG_TRADING_LOOP_START = "交易循环已启动"
LOG_MSG_TRADING_LOOP_STOP = "交易循环已停止"
LOG_MSG_CYCLE_START = "交易周期开始"
LOG_MSG_CYCLE_COMPLETE = "交易周期完成"
LOG_MSG_MODEL_EXEC = "执行模型 {model_id}"
LOG_MSG_MODEL_SUCCESS = "模型 {model_id} 完成"
LOG_MSG_MODEL_FAILED = "模型 {model_id} 失败: {error}"
LOG_MSG_TRADE_EXECUTED = "{coin}: {message}"
LOG_MSG_AUTO_TRADING_ENABLED = "自动交易已启用"
LOG_MSG_AUTO_TRADING_DISABLED = "自动交易已禁用"

# ============================================================================
# 错误消息
# ============================================================================
ERROR_MSG_PROVIDER_NOT_FOUND = "未找到提供商"
ERROR_MSG_MODEL_NOT_FOUND = "未找到模型"
ERROR_MSG_INVALID_CONFIG = "配置无效: {detail}"
ERROR_MSG_DB_CONNECTION_FAILED = "数据库连接失败"
ERROR_MSG_TRADING_LOOP_ERROR = "交易循环错误"
ERROR_MSG_API_REQUEST_FAILED = "API 请求失败: {detail}"
ERROR_MSG_MISSING_REQUIRED_FIELDS = "API URL 和密钥是必需的"
ERROR_MSG_INVALID_API_KEY = "API 密钥无效，请检查后重试"
ERROR_MSG_API_ACCESS_DENIED = "API 访问被拒绝 (403)，可能原因：\n1. API 密钥权限不足\n2. API 密钥已过期\n3. 该 API 不支持列出模型"
ERROR_MSG_API_ENDPOINT_NOT_FOUND = "API 端点不存在，请检查 URL 是否正确 (可能需要添加或移除 /v1)"
ERROR_MSG_NO_MODELS_FOUND = "未找到可用模型"
ERROR_MSG_UNKNOWN_RESPONSE_FORMAT = "无法解析模型列表响应格式"
ERROR_MSG_REQUEST_TIMEOUT = "请求超时，请检查网络连接或 API 地址"
ERROR_MSG_CONNECTION_ERROR = "无法连接到 API，请检查 URL 是否正确"
ERROR_MSG_REQUEST_FAILED = "请求失败: {detail}"
ERROR_MSG_FETCH_MODELS_FAILED = "获取模型列表失败: {detail}"
ERROR_MSG_ADD_MODEL_FAILED = "添加模型失败"
ERROR_MSG_DELETE_MODEL_FAILED = "删除模型失败"
ERROR_MSG_UPDATE_SETTINGS_FAILED = "更新设置失败"
ERROR_MSG_CHECK_UPDATE_FAILED = "检查更新失败"

# ============================================================================
# 成功消息
# ============================================================================
SUCCESS_MSG_PROVIDER_ADDED = "提供商添加成功"
SUCCESS_MSG_PROVIDER_DELETED = "提供商删除成功"
SUCCESS_MSG_MODEL_ADDED = "模型添加成功"
SUCCESS_MSG_MODEL_DELETED = "模型删除成功"
SUCCESS_MSG_SETTINGS_UPDATED = "设置更新成功"

# ============================================================================
# 信息消息
# ============================================================================
INFO_MSG_FETCHING_MODELS = "正在从 {endpoint} 获取模型"
INFO_MSG_RESPONSE_STATUS = "响应状态: {status}"
INFO_MSG_MODELS_FOUND = "找到 {count} 个模型"
INFO_MSG_MODEL_INITIALIZED = "模型 {model_id} ({name}) 已初始化"
INFO_MSG_MODEL_DELETED = "模型 {model_id} ({name}) 已删除"
INFO_MSG_GITHUB_API_ERROR = "GitHub API 错误: {error}"

# ============================================================================
# 警告消息
# ============================================================================
WARN_MSG_UPDATE_CHECK_FAILED = "无法检查更新"
WARN_MSG_NETWORK_ERROR = "网络错误检查更新"

# ============================================================================
# 时间和重试配置
# ============================================================================
TIMEOUT_API_REQUEST = 15  # 秒
TIMEOUT_GRACEFUL_SHUTDOWN = 30  # 秒
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1  # 秒
RETRY_MAX_DELAY = 300  # 秒 (5 分钟)
RETRY_BACKOFF_FACTOR = 2  # 指数退避因子

# ============================================================================
# 日志配置
# ============================================================================
LOG_FILE_PATH = "logs/app.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# 线程和循环配置
# ============================================================================
TRADING_LOOP_IDLE_SLEEP = 30  # 秒，无活动模型时的睡眠时间
TRADING_LOOP_MIN_INTERVAL = 60  # 秒，最小交易间隔
