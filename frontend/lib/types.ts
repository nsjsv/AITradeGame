/**
 * Global Type Definitions
 */

// ============================================================================
// Model Types
// ============================================================================

export interface TradingModel {
  id: number
  name: string
  model_name: string
  provider_id: number
  initial_capital: number
  created_at: string
}

export interface CreateModelRequest {
  name: string
  provider_id: number
  model_name: string
  initial_capital?: number
}

// ============================================================================
// 投资组合相关类型
// ============================================================================

export interface PositionBreakdown {
  long: number
  short: number
}

export interface Portfolio {
  total_value: number
  cash: number
  realized_pnl: number
  unrealized_pnl: number
  positions: Position[]
  model_id?: number
  positions_value?: number
  margin_used?: number
  total_fees?: number
  initial_capital?: number
  net_positions?: Record<string, PositionBreakdown>
}

export interface Position {
  coin: string
  side: 'long' | 'short'
  quantity: number
  avg_price: number
  current_price: number | null
  leverage: number
  pnl: number
}

export interface AccountValueHistory {
  timestamp: string
  total_value: number
  cash?: number
  positions_value?: number
  model_id?: number
}

export interface PortfolioResponse {
  portfolio: Portfolio
  account_value_history: AccountValueHistory[]
}

// ============================================================================
// 交易相关类型
// ============================================================================

export interface Trade {
  id: number
  model_id: number
  timestamp: string
  coin: string
  signal: 'buy_to_enter' | 'sell_to_enter' | 'close_position'
  quantity: number
  price: number
  pnl: number
  fee: number
}

// ============================================================================
// AI 对话相关类型
// ============================================================================

export interface Conversation {
  id: number
  model_id: number
  timestamp: string
  ai_response: string
}

// ============================================================================
// 市场数据相关类型
// ============================================================================

export interface MarketPrice {
  price: number
  change_24h: number
  volume?: number
  source?: string
  timestamp?: number
}

export interface MarketPrices {
  [coin: string]: MarketPrice
}

export interface MarketHistoryRecord {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  source?: string
}

export interface MarketHistoryResponse {
  coin: string
  resolution: number
  limit: number
  records: MarketHistoryRecord[]
}

export interface MarketHistoryQuery {
  coin: string
  resolution?: number
  limit?: number
  start?: string
  end?: string
}

// ============================================================================
// API 提供方相关类型
// ============================================================================

export interface ApiProvider {
  id: number
  name: string
  api_url: string
  api_key: string
  models: string
  created_at: string
}

export interface CreateProviderRequest {
  name: string
  api_url: string
  api_key: string
  models?: string
}

export interface FetchModelsRequest {
  api_url: string
  api_key: string
}

export interface FetchModelsResponse {
  models: string[]
}

// ============================================================================
// 系统设置相关类型
// ============================================================================

export interface SystemSettings {
  trading_frequency_minutes: number
  trading_fee_rate: number
  market_refresh_interval: number
  portfolio_refresh_interval: number
}

export interface FrontendConfig {
  market_refresh_interval: number
  portfolio_refresh_interval: number
  trading_coins: string[]
  trade_fee_rate: number
}

// ============================================================================
// 更新相关类型
// ============================================================================

export interface UpdateInfo {
  update_available: boolean
  current_version: string
  latest_version?: string
  release_url?: string
  release_notes?: string
  repo_url?: string
  error?: string
}

export interface VersionInfo {
  current_version: string
  github_repo: string
  latest_release_url: string
}

// ============================================================================
// 聚合数据相关类型
// ============================================================================

export interface AggregatedPortfolio {
  portfolio: Portfolio
  chart_data: ModelChartData[]
  model_count?: number
}

export interface ModelChartData {
  model_name: string
  data: AccountValueHistory[]
}

// ============================================================================
// 排行榜相关类型
// ============================================================================

export interface LeaderboardEntry {
  model_id: number
  model_name: string
  total_value: number
  initial_capital: number
  return_rate: number
  realized_pnl: number
  unrealized_pnl: number
}

// ============================================================================
// 环境配置类型
// ============================================================================

export interface EnvConfig {
  apiBaseUrl: string
  wsUrl: string
  env: 'development' | 'production' | 'test'
}

// ============================================================================
// 系统状态
// ============================================================================

export interface HealthResponse {
  status: 'ok' | 'error'
  database?: 'ok' | 'error'
  timestamp: string
  message?: string
}
