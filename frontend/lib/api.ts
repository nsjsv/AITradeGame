/**
 * API Client
 *
 * Encapsulates all backend API calls with unified error handling and runtime type validation
 */

import type {
  AggregatedPortfolio,
  ApiProvider,
  Conversation,
  CreateModelRequest,
  CreateProviderRequest,
  FetchModelsRequest,
  FetchModelsResponse,
  FrontendConfig,
  HealthResponse,
  LeaderboardEntry,
  MarketPrices,
  ModelChartData,
  PortfolioResponse,
  SystemSettings,
  Trade,
  TradingModel,
  UpdateInfo,
  VersionInfo,
} from './types'

import {
  validateApiProviders,
  validateApiResponse,
  validateMarketPrices,
  validatePortfolioResponse,
  validateSystemSettings,
  validateTrades,
  validateTradingModels,
} from './validators'
import type { ApiResponse } from './http'
import {
  apiDelete,
  apiGet,
  apiPost,
  apiPut,
  errorResponse,
  getMarketApiBaseUrl,
  successResponse,
} from './http'

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
      
      // 直接从响应中提取 data 字段
      let payload: unknown
      let meta: Record<string, unknown> | undefined
      
      if (raw && typeof raw === 'object' && !Array.isArray(raw) && 'data' in raw) {
        const envelope = raw as { data: unknown; meta?: Record<string, unknown> }
        payload = envelope.data
        meta = envelope.meta
      } else {
        payload = raw ?? null
      }
      
      const data = options.validator
        ? validateApiResponse(payload, options.validator, options.context)
        : (payload as T)
      return successResponse(data, meta)
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

  async createModel(data: CreateModelRequest): Promise<ApiResponse<{ id: number }>> {
    return this.handleRequest(
      () => apiPost('/api/models', data),
      { fallbackMessage: '创建模型失败' }
    )
  }

  async deleteModel(id: number): Promise<ApiResponse<null>> {
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

  async createProvider(data: CreateProviderRequest): Promise<ApiResponse<{ id: number }>> {
    return this.handleRequest(
      () => apiPost('/api/providers', data),
      { fallbackMessage: '创建提供方失败' }
    )
  }

  async deleteProvider(id: number): Promise<ApiResponse<null>> {
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

  async updateSettings(data: SystemSettings): Promise<ApiResponse<null>> {
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
 * if (!response.error && response.data) {
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

export {
  ApiError,
  type ApiResponse,
  apiRequest,
  apiRequestWithBase,
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
} from './http'
