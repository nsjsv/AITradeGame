/**
 * useMarketHistory Hook - 根据币种获取历史行情
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient, ApiError } from '@/lib/api'
import type { MarketHistoryResponse } from '@/lib/types'

interface UseMarketHistoryOptions {
  coin: string | null
  resolution?: number
  limit?: number
  enabled?: boolean
}

interface UseMarketHistoryReturn {
  data: MarketHistoryResponse | null
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useMarketHistory({
  coin,
  resolution = 60,
  limit = 120,
  enabled = true,
}: UseMarketHistoryOptions): UseMarketHistoryReturn {
  const [data, setData] = useState<MarketHistoryResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    if (!coin || !enabled) {
      return
    }
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient.getMarketHistory({
        coin,
        resolution,
        limit,
      })
      if (response.error) {
        setError(response.error)
        setData(null)
        return
      }
      setData(response.data ?? null)
    } catch (err) {
      const message =
        err instanceof ApiError && err.status === 0
          ? '无法连接到行情服务'
          : err instanceof Error
            ? err.message
            : '获取行情历史数据失败'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, [coin, enabled, limit, resolution])

  useEffect(() => {
    if (!coin || !enabled) {
      setData(null)
      setError(null)
      setIsLoading(false)
      return
    }
    refresh()
  }, [coin, enabled, refresh])

  return { data, isLoading, error, refresh }
}
