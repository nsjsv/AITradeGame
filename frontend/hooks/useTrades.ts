/**
 * useTrades Hook - 交易记录管理
 * 
 * 用于获取交易记录数据
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import { useInterval } from './useInterval'
import type { Trade } from '@/lib/types'

interface UseTradesReturn {
  trades: Trade[]
  isLoading: boolean
  error: string | null
  loadTrades: () => Promise<void>
}

export function useTrades(limit: number = 50): UseTradesReturn {
  const { selectedModelId, isAggregatedView, config } = useAppStore()
  const [trades, setTrades] = useState<Trade[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshInterval = useMemo(
    () => (config?.portfolio_refresh_interval ? config.portfolio_refresh_interval * 1000 : 10000),
    [config?.portfolio_refresh_interval]
  )

  /**
   * 加载交易记录
   */
  const loadTrades = useCallback(async () => {
    // 聚合视图不显示交易记录
    if (isAggregatedView || !selectedModelId) {
      setTrades([])
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getModelTrades(selectedModelId, limit)
      
      if (response.success && response.data) {
        setTrades(response.data)
      } else {
        setError(response.error || '获取交易记录失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取交易记录失败')
    } finally {
      setIsLoading(false)
    }
  }, [selectedModelId, isAggregatedView, limit])

  // 当选中模型变化时重新加载
  useEffect(() => {
    loadTrades()
  }, [loadTrades])

  // 定时刷新（仅在单模型视图下）
  useInterval(
    loadTrades,
    !isAggregatedView && selectedModelId ? refreshInterval : null
  )

  return {
    trades,
    isLoading,
    error,
    loadTrades,
  }
}
