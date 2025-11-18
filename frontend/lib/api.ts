/**
 * API Client
 * 
 * Encapsulates all backend API calls with unified error handling and runtime type validation
 */

import type {
  TradingModel,
  CreateModelRequest,
  PortfolioResponse,
  Trade,
  Conversation,
  MarketPrices,
  ApiProvider,
  CreateProviderRequest,
  FetchModelsRequest,
  FetchModelsResponse,
  SystemSettings,
  FrontendConfig,
  UpdateInfo,
  VersionInfo,
  AggregatedPortfolio,
  ModelChartData,
  LeaderboardEntry,
  HealthResponse,
} from './types'

import {
  validateTradingModels,
  validatePortfolioResponse,
  validateTrades,
  validateApiProviders,
  validateSystemSettings,
  validateMarketPrices,
  validateApiResponse,
  ValidationError,
} from './validators'

// ============================================================================
// 配置和工具函数
// ============================================================================

/**
 * 获取 API 基础 URL
 */
const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    if (process.env.NEXT_PUBLIC_BROWSER_API_BASE_URL) {
      return process.env.NEXT_PUBLIC_BROWSER_API_BASE_URL
    }
    if (process.env.NEXT_PUBLIC_API_BASE_URL?.includes('backend')) {
      // Allow docker-compose internal hostnames to fall back to browser origin
      const url = new URL(process.env.NEXT_PUBLIC_API_BASE_URL)
      return `${window.location.protocol}//${window.location.hostname}${url.port ? `:${url.port}` : ''}`
    }
  }

  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL
  }
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return 'http://localhost:5000'
}

/**
 * 专用于市场数据的 API 基础 URL（可指向独立行情服务）
 */
const getMarketApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_MARKET_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_MARKET_API_BASE_URL
  }
  return getApiBaseUrl()
}

/**
 * Request configuration type
 */
interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>
}

/**
 * Standard API response shape used by frontend hooks
 */
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

/**
 * API Error class
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public data: any,
    message?: string
  ) {
    super(message || `HTTP ${status}`)
    this.name = 'ApiError'
  }
}

const successResponse = <T>(data: T): ApiResponse<T> => ({
  success: true,
  data,
})

const extractErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof ValidationError) {
    return error.message
  }
  if (error instanceof ApiError) {
    const data = error.data
    if (data && typeof data === 'object') {
      if ('error' in data && typeof data.error === 'string') {
        return data.error
      }
      if ('message' in data && typeof data.message === 'string') {
        return data.message
      }
    }
    return error.message || fallback
  }
  if (error instanceof Error) {
    return error.message
  }
  return fallback
}

const errorResponse = (error: unknown, fallback: string): ApiResponse<never> => {
  const message = extractErrorMessage(error, fallback)
  if (process.env.NODE_ENV === 'development') {
    const isNetworkError = error instanceof ApiError && error.status === 0
    const logger = isNetworkError ? console.warn : console.error
    logger('[API Client Error]', message, error)
  }
  return { success: false, error: message }
}

// ============================================================================
// 核心请求函数
// ============================================================================

/**
 * Generic API request function
 * 
 * @param endpoint - API endpoint path
 * @param config - Request configuration
 * @returns Promise<T>
 * @throws ApiError on HTTP errors
 */
export async function apiRequest<T = any>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> {
  return apiRequestWithBase(endpoint, config, getApiBaseUrl())
}

async function apiRequestWithBase<T = any>(
  endpoint: string,
  config: RequestConfig = {},
  baseUrl?: string
): Promise<T> {
  const { params, ...fetchConfig } = config
  const resolvedBaseUrl = baseUrl || getApiBaseUrl()
  
  // Build URL
  let url = `${resolvedBaseUrl}${endpoint}`
  if (params) {
    const searchParams = new URLSearchParams(
      Object.entries(params).map(([key, value]) => [key, String(value)])
    )
    url += `?${searchParams.toString()}`
  }

  if (process.env.NODE_ENV === 'development') {
    console.log(`[API] ${config.method || 'GET'} ${url}`)
  }

  try {
    const response = await fetch(url, {
      ...fetchConfig,
      headers: {
        'Content-Type': 'application/json',
        ...fetchConfig.headers,
      },
    })
    
    // Parse JSON response
    let data: any
    try {
      data = await response.json()
    } catch {
      data = {}
    }

    if (!response.ok) {
      const errorMessage = data.error || `HTTP ${response.status}: ${response.statusText}`
      if (process.env.NODE_ENV === 'development') {
        console.error(`[API Error] ${errorMessage}`, data)
      }
      throw new ApiError(response.status, data, errorMessage)
    }

    return data as T
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    const message = error instanceof Error ? error.message : 'Network request failed'
    throw new ApiError(0, {}, message)
  }
}

/**
 * GET request
 */
export async function apiGet<T = any>(
  endpoint: string,
  params?: Record<string, string | number | boolean>,
  baseUrl?: string
): Promise<T> {
  return apiRequestWithBase<T>(endpoint, { method: 'GET', params }, baseUrl)
}

/**
 * POST request
 */
export async function apiPost<T = any>(
  endpoint: string,
  body?: any
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

/**
 * PUT request
 */
export async function apiPut<T = any>(
  endpoint: string,
  body?: any
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

/**
 * DELETE request
 */
export async function apiDelete<T = any>(
  endpoint: string
): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE' })
}

// ============================================================================
// API 客户端类
// ============================================================================

/**
 * API 客户端类
 * 封装所有后端 API 调用
 */
class ApiClient {
  private async handleRequest<T>(
    operation: () => Promise<unknown>,
    options: {
      fallbackMessage: string
      validator?: (data: unknown) => T
      context?: string
    }
  ): Promise<ApiResponse<T>> {
    try {
      const raw = await operation()
      const data = options.validator
        ? validateApiResponse(raw, options.validator, options.context)
        : (raw as T)
      return successResponse(data)
    } catch (error) {
      return errorResponse(error, options.fallbackMessage)
    }
  }

  // --------------------------------------------------------------------------
  // 模型相关 API
  // --------------------------------------------------------------------------

  async getModels(): Promise<ApiResponse<TradingModel[]>> {
    return this.handleRequest(
      () => apiGet('/api/models'),
      {
        fallbackMessage: '获取模型列表失败',
        validator: validateTradingModels,
        context: 'getModels',
      }
    )
  }

  async createModel(data: CreateModelRequest): Promise<ApiResponse<{ id: number; message: string }>> {
    return this.handleRequest(
      () => apiPost('/api/models', data),
      { fallbackMessage: '创建模型失败' }
    )
  }

  async deleteModel(id: number): Promise<ApiResponse<{ message: string }>> {
    return this.handleRequest(
      () => apiDelete(`/api/models/${id}`),
      { fallbackMessage: '删除模型失败' }
    )
  }

  async executeTrading(id: number): Promise<ApiResponse<any>> {
    return this.handleRequest(
      () => apiPost(`/api/models/${id}/execute`),
      { fallbackMessage: '执行交易失败' }
    )
  }

  async getModelPortfolio(id: number): Promise<ApiResponse<PortfolioResponse>> {
    return this.handleRequest(
      () => apiGet(`/api/models/${id}/portfolio`),
      {
        fallbackMessage: '获取投资组合失败',
        validator: validatePortfolioResponse,
        context: `getModelPortfolio(${id})`,
      }
    )
  }

  async getModelTrades(id: number, limit: number = 50): Promise<ApiResponse<Trade[]>> {
    return this.handleRequest(
      () => apiGet(`/api/models/${id}/trades`, { limit }),
      {
        fallbackMessage: '获取交易记录失败',
        validator: validateTrades,
        context: `getModelTrades(${id})`,
      }
    )
  }

  async getModelConversations(id: number, limit: number = 20): Promise<ApiResponse<Conversation[]>> {
    return this.handleRequest(
      () => apiGet(`/api/models/${id}/conversations`, { limit }),
      { fallbackMessage: '获取对话记录失败' }
    )
  }

  // --------------------------------------------------------------------------
  // 聚合数据 API
  // --------------------------------------------------------------------------

  async getAggregatedPortfolio(): Promise<ApiResponse<AggregatedPortfolio>> {
    return this.handleRequest(
      () => apiGet('/api/aggregated/portfolio'),
      { fallbackMessage: '获取聚合投资组合失败' }
    )
  }

  async getModelsChartData(limit: number = 100): Promise<ApiResponse<ModelChartData[]>> {
    return this.handleRequest(
      () => apiGet('/api/models/chart-data', { limit }),
      { fallbackMessage: '获取图表数据失败' }
    )
  }

  async getLeaderboard(): Promise<ApiResponse<LeaderboardEntry[]>> {
    return this.handleRequest(
      () => apiGet('/api/leaderboard'),
      { fallbackMessage: '获取排行榜失败' }
    )
  }

  // --------------------------------------------------------------------------
  // 市场数据 API
  // --------------------------------------------------------------------------

  async getMarketPrices(): Promise<ApiResponse<MarketPrices>> {
    return this.handleRequest(
      () => apiGet('/api/market/prices', undefined, getMarketApiBaseUrl()),
      {
        fallbackMessage: '获取市场价格失败',
        validator: validateMarketPrices,
        context: 'getMarketPrices',
      }
    )
  }

  // --------------------------------------------------------------------------
  // API 提供方 API
  // --------------------------------------------------------------------------

  async getProviders(): Promise<ApiResponse<ApiProvider[]>> {
    return this.handleRequest(
      () => apiGet('/api/providers'),
      {
        fallbackMessage: '获取提供方列表失败',
        validator: validateApiProviders,
        context: 'getProviders',
      }
    )
  }

  async createProvider(data: CreateProviderRequest): Promise<ApiResponse<{ id: number; message: string }>> {
    return this.handleRequest(
      () => apiPost('/api/providers', data),
      { fallbackMessage: '创建提供方失败' }
    )
  }

  async deleteProvider(id: number): Promise<ApiResponse<{ message: string }>> {
    return this.handleRequest(
      () => apiDelete(`/api/providers/${id}`),
      { fallbackMessage: '删除提供方失败' }
    )
  }

  async fetchProviderModels(data: FetchModelsRequest): Promise<ApiResponse<FetchModelsResponse>> {
    return this.handleRequest(
      () => apiPost('/api/providers/models', data),
      { fallbackMessage: '获取模型列表失败' }
    )
  }

  // --------------------------------------------------------------------------
  // 系统设置 API
  // --------------------------------------------------------------------------

  async getSettings(): Promise<ApiResponse<SystemSettings>> {
    return this.handleRequest(
      () => apiGet('/api/settings'),
      {
        fallbackMessage: '获取系统设置失败',
        validator: validateSystemSettings,
        context: 'getSettings',
      }
    )
  }

  async updateSettings(data: SystemSettings): Promise<ApiResponse<{ message: string }>> {
    return this.handleRequest(
      () => apiPut('/api/settings', data),
      { fallbackMessage: '更新系统设置失败' }
    )
  }

  async getConfig(): Promise<ApiResponse<FrontendConfig>> {
    return this.handleRequest(
      () => apiGet('/api/config'),
      { fallbackMessage: '获取前端配置失败' }
    )
  }

  // --------------------------------------------------------------------------
  // 版本和更新 API
  // --------------------------------------------------------------------------

  async getVersion(): Promise<ApiResponse<VersionInfo>> {
    return this.handleRequest(
      () => apiGet('/api/version'),
      { fallbackMessage: '获取版本信息失败' }
    )
  }

  async checkUpdate(): Promise<ApiResponse<UpdateInfo>> {
    return this.handleRequest(
      () => apiGet('/api/check-update'),
      { fallbackMessage: '检查更新失败' }
    )
  }

  async getHealth(): Promise<ApiResponse<HealthResponse>> {
    return this.handleRequest(
      () => apiGet('/api/health'),
      { fallbackMessage: '健康检查失败' }
    )
  }

  async getMarketHealth(): Promise<ApiResponse<HealthResponse>> {
    return this.handleRequest(
      () => apiGet('/api/health', undefined, getMarketApiBaseUrl()),
      { fallbackMessage: '行情服务健康检查失败' }
    )
  }
}

// ============================================================================
// 导出单例实例
// ============================================================================

/**
 * API 客户端单例实例
 * 
 * 使用示例:
 * ```typescript
 * import { apiClient } from '@/lib/api'
 * 
 * const response = await apiClient.getModels()
 * if (response.success) {
 *   console.log(response.data)
 * } else {
 *   console.error(response.error)
 * }
 * ```
 */
export const apiClient = new ApiClient()

/**
 * 默认导出 API 客户端实例
 */
export default apiClient
