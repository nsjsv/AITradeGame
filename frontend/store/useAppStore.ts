/**
 * 全局应用状态管理 - 使用 Zustand
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type {
  TradingModel,
  MarketPrices,
  FrontendConfig,
  ApiProvider,
} from '@/lib/types'

// ============================================================================
// 状态接口定义
// ============================================================================

interface AppState {
  // 模型相关
  selectedModelId: number | null
  isAggregatedView: boolean
  models: TradingModel[]
  providers: ApiProvider[]

  // 市场数据
  marketPrices: MarketPrices

  // 配置
  config: FrontendConfig | null

  // UI 状态
  isRefreshing: boolean
  isSidebarOpen: boolean

  // 暗黑模式（由 next-themes 管理，这里仅作为备份）
  isDarkMode: boolean

  // 后端状态
  backendOnline: boolean
  backendLastChecked: number | null
  backendError: string | null

  // Actions
  setSelectedModel: (id: number | null) => void
  setAggregatedView: (isAggregated: boolean) => void
  setModels: (models: TradingModel[]) => void
  setProviders: (providers: ApiProvider[]) => void
  setMarketPrices: (prices: MarketPrices) => void
  setConfig: (config: FrontendConfig) => void
  setRefreshing: (isRefreshing: boolean) => void
  setSidebarOpen: (isOpen: boolean) => void
  toggleSidebar: () => void
  setDarkMode: (isDark: boolean) => void
  setBackendStatus: (online: boolean, error?: string | null) => void
  reset: () => void
}

// ============================================================================
// 初始状态
// ============================================================================

const initialState = {
  selectedModelId: null,
  isAggregatedView: false,
  models: [],
  providers: [],
  marketPrices: {},
  config: null,
  isRefreshing: false,
  isSidebarOpen: true,
  isDarkMode: false,
  backendOnline: true,
  backendLastChecked: null,
  backendError: null,
}

// ============================================================================
// Store 创建
// ============================================================================

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        // 设置选中的模型
        setSelectedModel: (id) =>
          set(
            { selectedModelId: id, isAggregatedView: false },
            false,
            'setSelectedModel'
          ),

        // 设置聚合视图
        setAggregatedView: (isAggregated) =>
          set(
            { isAggregatedView: isAggregated, selectedModelId: null },
            false,
            'setAggregatedView'
          ),

        // 设置模型列表
        setModels: (models) => set({ models }, false, 'setModels'),
        // 设置提供方列表
        setProviders: (providers) => set({ providers }, false, 'setProviders'),

        // 设置市场价格
        setMarketPrices: (prices) =>
          set({ marketPrices: prices }, false, 'setMarketPrices'),

        // 设置配置
        setConfig: (config) => set({ config }, false, 'setConfig'),

        // 设置刷新状态
        setRefreshing: (isRefreshing) =>
          set({ isRefreshing }, false, 'setRefreshing'),

        // 设置侧边栏状态
        setSidebarOpen: (isOpen) =>
          set({ isSidebarOpen: isOpen }, false, 'setSidebarOpen'),

        // 切换侧边栏
        toggleSidebar: () =>
          set(
            (state) => ({ isSidebarOpen: !state.isSidebarOpen }),
            false,
            'toggleSidebar'
          ),

        // 设置暗黑模式
        setDarkMode: (isDark) =>
          set({ isDarkMode: isDark }, false, 'setDarkMode'),

        // 设置后端状态
        setBackendStatus: (online, error = null) =>
          set(
            {
              backendOnline: online,
              backendError: error ?? null,
              backendLastChecked: Date.now(),
            },
            false,
            'setBackendStatus'
          ),

        // 重置状态
        reset: () => set(initialState, false, 'reset'),
      }),
      {
        name: 'aitradegame-storage',
        // 只持久化部分状态
        partialize: (state) => ({
          selectedModelId: state.selectedModelId,
          isAggregatedView: state.isAggregatedView,
          isSidebarOpen: state.isSidebarOpen,
          isDarkMode: state.isDarkMode,
        }),
      }
    ),
    {
      name: 'AppStore',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
)

// ============================================================================
// 选择器 Hooks（用于性能优化）
// ============================================================================

export const useSelectedModelId = () =>
  useAppStore((state) => state.selectedModelId)

export const useIsAggregatedView = () =>
  useAppStore((state) => state.isAggregatedView)

export const useModels = () => useAppStore((state) => state.models)

export const useMarketPrices = () => useAppStore((state) => state.marketPrices)

export const useConfig = () => useAppStore((state) => state.config)

export const useIsRefreshing = () => useAppStore((state) => state.isRefreshing)

export const useIsSidebarOpen = () =>
  useAppStore((state) => state.isSidebarOpen)

export const useIsDarkMode = () => useAppStore((state) => state.isDarkMode)
