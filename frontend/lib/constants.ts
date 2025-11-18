/**
 * 全局常量定义
 */

// ============================================================================
// API 配置
// ============================================================================

/**
 * API 基础 URL
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:5000'

/**
 * WebSocket URL
 */
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:5000/ws'

// ============================================================================
// 刷新间隔（毫秒）
// ============================================================================

/**
 * 默认市场价格刷新间隔（30秒）
 */
export const DEFAULT_MARKET_REFRESH_INTERVAL = 30 * 1000

/**
 * 默认投资组合刷新间隔（10秒）
 */
export const DEFAULT_PORTFOLIO_REFRESH_INTERVAL = 10 * 1000

/**
 * 默认交易记录刷新间隔（15秒）
 */
export const DEFAULT_TRADES_REFRESH_INTERVAL = 15 * 1000

/**
 * 默认对话刷新间隔（20秒）
 */
export const DEFAULT_CONVERSATIONS_REFRESH_INTERVAL = 20 * 1000

// ============================================================================
// 数据限制
// ============================================================================

/**
 * 默认交易记录获取数量
 */
export const DEFAULT_TRADES_LIMIT = 50

/**
 * 默认对话获取数量
 */
export const DEFAULT_CONVERSATIONS_LIMIT = 20

/**
 * 图表最大数据点数
 */
export const MAX_CHART_DATA_POINTS = 1000

// ============================================================================
// 交易相关常量
// ============================================================================

/**
 * 交易信号类型映射（用于显示）
 */
export const TRADE_SIGNAL_LABELS: Record<string, string> = {
  buy_to_enter: '开多',
  sell_to_enter: '开空',
  close_position: '平仓',
}

/**
 * 交易信号颜色映射
 */
export const TRADE_SIGNAL_COLORS: Record<string, string> = {
  buy_to_enter: 'bg-profit/10 text-profit border-profit/20',
  sell_to_enter: 'bg-loss/10 text-loss border-loss/20',
  close_position: 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700',
}

/**
 * 持仓方向映射
 */
export const POSITION_SIDE_LABELS: Record<string, string> = {
  long: '多',
  short: '空',
}

/**
 * 持仓方向颜色映射
 */
export const POSITION_SIDE_COLORS: Record<string, string> = {
  long: 'text-profit',
  short: 'text-loss',
}

// ============================================================================
// 格式化配置
// ============================================================================

/**
 * 价格小数位数
 */
export const PRICE_DECIMALS = 2

/**
 * 数量小数位数
 */
export const QUANTITY_DECIMALS = 4

/**
 * 百分比小数位数
 */
export const PERCENT_DECIMALS = 2

/**
 * 费率小数位数
 */
export const FEE_RATE_DECIMALS = 4

// ============================================================================
// 默认值
// ============================================================================

/**
 * 默认初始资金
 */
export const DEFAULT_INITIAL_CAPITAL = 10000

/**
 * 默认交易频率（分钟）
 */
export const DEFAULT_TRADING_FREQUENCY = 60

/**
 * 默认交易费率
 */
export const DEFAULT_TRADING_FEE_RATE = 0.001

/**
 * 默认杠杆倍数
 */
export const DEFAULT_LEVERAGE = 1

// ============================================================================
// UI 配置
// ============================================================================

/**
 * 侧边栏宽度（像素）
 */
export const SIDEBAR_WIDTH = 280

/**
 * 移动端断点（像素）
 */
export const MOBILE_BREAKPOINT = 768

/**
 * 平板断点（像素）
 */
export const TABLET_BREAKPOINT = 1024

/**
 * 桌面断点（像素）
 */
export const DESKTOP_BREAKPOINT = 1280

/**
 * Toast 显示时长（毫秒）
 */
export const TOAST_DURATION = 3000

/**
 * 模态框动画时长（毫秒）
 */
export const MODAL_ANIMATION_DURATION = 200

// ============================================================================
// 图表配置
// ============================================================================

/**
 * 图表默认高度（像素）
 */
export const CHART_DEFAULT_HEIGHT = 400

/**
 * 图表颜色调色板（用于多模型对比）
 */
export const CHART_COLOR_PALETTE = [
  '#ef4444', // 红色
  '#3b82f6', // 蓝色
  '#10b981', // 绿色
  '#f59e0b', // 橙色
  '#8b5cf6', // 紫色
  '#ec4899', // 粉色
  '#14b8a6', // 青色
  '#f97316', // 深橙色
  '#6366f1', // 靛蓝色
  '#84cc16', // 黄绿色
]

/**
 * 图表网格配置
 */
export const CHART_GRID_CONFIG = {
  left: '3%',
  right: '4%',
  bottom: '3%',
  top: '10%',
  containLabel: true,
}

/**
 * 图表工具提示配置
 */
export const CHART_TOOLTIP_CONFIG = {
  trigger: 'axis' as const,
  axisPointer: {
    type: 'cross' as const,
    label: {
      backgroundColor: '#6a7985',
    },
  },
}

// ============================================================================
// 验证规则
// ============================================================================

/**
 * 模型名称最小长度
 */
export const MODEL_NAME_MIN_LENGTH = 1

/**
 * 模型名称最大长度
 */
export const MODEL_NAME_MAX_LENGTH = 50

/**
 * API 密钥最小长度
 */
export const API_KEY_MIN_LENGTH = 10

/**
 * 初始资金最小值
 */
export const INITIAL_CAPITAL_MIN = 100

/**
 * 初始资金最大值
 */
export const INITIAL_CAPITAL_MAX = 1000000

/**
 * 交易频率最小值（分钟）
 */
export const TRADING_FREQUENCY_MIN = 1

/**
 * 交易频率最大值（分钟）
 */
export const TRADING_FREQUENCY_MAX = 1440

/**
 * 交易费率最小值
 */
export const TRADING_FEE_RATE_MIN = 0

/**
 * 交易费率最大值
 */
export const TRADING_FEE_RATE_MAX = 0.1

// ============================================================================
// 错误消息
// ============================================================================

/**
 * 通用错误消息
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  SERVER_ERROR: '服务器错误，请稍后重试',
  INVALID_INPUT: '输入数据无效，请检查后重试',
  UNAUTHORIZED: '未授权访问，请登录',
  NOT_FOUND: '请求的资源不存在',
  TIMEOUT: '请求超时，请重试',
  UNKNOWN: '未知错误，请联系管理员',
}

/**
 * API 错误消息
 */
export const API_ERROR_MESSAGES = {
  FETCH_MODELS_FAILED: '获取模型列表失败',
  CREATE_MODEL_FAILED: '创建模型失败',
  DELETE_MODEL_FAILED: '删除模型失败',
  FETCH_PORTFOLIO_FAILED: '获取投资组合失败',
  FETCH_TRADES_FAILED: '获取交易记录失败',
  FETCH_CONVERSATIONS_FAILED: '获取对话记录失败',
  FETCH_MARKET_PRICES_FAILED: '获取市场价格失败',
  FETCH_PROVIDERS_FAILED: '获取API提供方失败',
  CREATE_PROVIDER_FAILED: '创建API提供方失败',
  DELETE_PROVIDER_FAILED: '删除API提供方失败',
  FETCH_SETTINGS_FAILED: '获取系统设置失败',
  UPDATE_SETTINGS_FAILED: '更新系统设置失败',
  CHECK_UPDATE_FAILED: '检查更新失败',
}

// ============================================================================
// 成功消息
// ============================================================================

/**
 * 成功消息
 */
export const SUCCESS_MESSAGES = {
  MODEL_CREATED: '模型创建成功',
  MODEL_DELETED: '模型删除成功',
  PROVIDER_CREATED: 'API提供方创建成功',
  PROVIDER_DELETED: 'API提供方删除成功',
  SETTINGS_UPDATED: '设置更新成功',
  DATA_REFRESHED: '数据刷新成功',
}

// ============================================================================
// 本地存储键
// ============================================================================

/**
 * 本地存储键前缀
 */
export const STORAGE_PREFIX = 'aitradegame'

/**
 * 本地存储键
 */
export const STORAGE_KEYS = {
  THEME: `${STORAGE_PREFIX}_theme`,
  SELECTED_MODEL: `${STORAGE_PREFIX}_selected_model`,
  SIDEBAR_STATE: `${STORAGE_PREFIX}_sidebar_state`,
  LAST_UPDATE_CHECK: `${STORAGE_PREFIX}_last_update_check`,
}

// ============================================================================
// 外部链接
// ============================================================================

/**
 * GitHub 仓库 URL
 */
export const GITHUB_REPO_URL = 'https://github.com/yourusername/aitradegame'

/**
 * 文档 URL
 */
export const DOCS_URL = 'https://github.com/yourusername/aitradegame#readme'

/**
 * 问题反馈 URL
 */
export const ISSUES_URL = 'https://github.com/yourusername/aitradegame/issues'

// ============================================================================
// 应用信息
// ============================================================================

/**
 * 应用名称
 */
export const APP_NAME = 'AITradeGame'

/**
 * 应用描述
 */
export const APP_DESCRIPTION = 'AI 驱动的加密货币交易模拟游戏'

/**
 * 应用版本（从环境变量读取，或使用默认值）
 */
export const APP_VERSION = process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'
