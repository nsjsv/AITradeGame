/**
 * usePortfolio Hook - 投资组合数据管理
 * 
 * 用于获取单个模型或聚合的投资组合数据
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import { useInterval } from './useInterval'
import type { Portfolio, AccountValueHistory, ModelChartData } from '@/lib/types'

interface UsePortfolioReturn {
  portfolio: Portfolio | null
  chartData: AccountValueHistory[] | ModelChartData[]
  isLoading: boolean
  error: string | null
  loadPortfolio: () => Promise<void>
}

export function usePortfolio(): UsePortfolioReturn {
  const selectedModelId = useAppStore((state) => state.selectedModelId)
  const isAggregatedView = useAppStore((state) => state.isAggregatedView)
  const config = useAppStore((state) => state.config)
  const setRefreshing = useAppStore((state) => state.setRefreshing)
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [chartData, setChartData] = useState<AccountValueHistory[] | ModelChartData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const initialLoadRef = useRef(true)

  /**
   * 加载投资组合数据
   */
  const loadPortfolio = useCallback(async () => {
    // 如果没有选中模型且不是聚合视图，不加载
    if (!selectedModelId && !isAggregatedView) {
      setPortfolio(null)
      setChartData([])
      setIsLoading(false)
      initialLoadRef.current = true
      setRefreshing(false)
      return
    }

    setError(null)
    const blockUI = initialLoadRef.current
    if (blockUI) {
      setIsLoading(true)
    } else {
      setRefreshing(true)
    }
    
    try {
      if (isAggregatedView) {
        // 聚合视图
        const response = await apiClient.getAggregatedPortfolio()
        
        if (!response.error && response.data) {
          setPortfolio(response.data.portfolio)
          setChartData(response.data.chart_data)
        } else {
          setError(response.error || '获取聚合投资组合失败')
        }
      } else if (selectedModelId) {
        // 单个模型视图
        const response = await apiClient.getModelPortfolio(selectedModelId)
        
        if (!response.error && response.data) {
          setPortfolio(response.data.portfolio)
          setChartData(response.data.account_value_history)
        } else {
          setError(response.error || '获取投资组合失败')
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取投资组合失败')
    } finally {
      if (blockUI) {
        setIsLoading(false)
        initialLoadRef.current = false
      }
      setRefreshing(false)
    }
  }, [selectedModelId, isAggregatedView, setRefreshing])

  // 当选中模型或视图模式变化时重新加载
  useEffect(() => {
    initialLoadRef.current = true
    setIsLoading(true)
  }, [selectedModelId, isAggregatedView])

  useEffect(() => {
    loadPortfolio()
  }, [loadPortfolio])

  // 定时刷新
  useInterval(
    loadPortfolio,
    config?.portfolio_refresh_interval ? config.portfolio_refresh_interval * 1000 : 10000
  )

  return {
    portfolio,
    chartData,
    isLoading,
    error,
    loadPortfolio,
  }
}
