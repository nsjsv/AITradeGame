/**
 * useMarketPrices Hook - 市场价格数据管理
 * 
 * 用于获取和定时刷新市场价格数据
 */

import { useState, useEffect, useCallback } from 'react'
import { apiClient, ApiError } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import { useInterval } from './useInterval'
import type { MarketPrices } from '@/lib/types'

interface UseMarketPricesReturn {
  prices: MarketPrices
  isLoading: boolean
  error: string | null
  loadPrices: () => Promise<void>
}

export function useMarketPrices(): UseMarketPricesReturn {
  const marketPrices = useAppStore((state) => state.marketPrices)
  const config = useAppStore((state) => state.config)
  const setMarketPrices = useAppStore((state) => state.setMarketPrices)
  const setBackendStatus = useAppStore((state) => state.setBackendStatus)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * 加载市场价格
   */
  const loadPrices = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getMarketPrices()
      
      if (response.success && response.data) {
        setMarketPrices(response.data)
        setBackendStatus(true, null)
      } else {
        setError(response.error || '获取市场价格失败')
      }
    } catch (err) {
      const message =
        err instanceof ApiError && err.status === 0
          ? '无法连接到后端服务'
          : err instanceof Error
            ? err.message
            : '获取市场价格失败'
      setError(message)
      if (err instanceof ApiError && err.status === 0) {
        setBackendStatus(false, message)
      }
    } finally {
      setIsLoading(false)
    }
  }, [setMarketPrices, setBackendStatus])

  // 初始加载
  useEffect(() => {
    loadPrices()
  }, [loadPrices])

  // 定时刷新
  useInterval(
    loadPrices,
    config?.market_refresh_interval ? config.market_refresh_interval * 1000 : 30000
  )

  return {
    prices: marketPrices,
    isLoading,
    error,
    loadPrices,
  }
}
