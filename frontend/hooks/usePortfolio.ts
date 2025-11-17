/**
 * usePortfolio Hook - 投资组合数据管理
 * 
 * 用于获取单个模型或聚合的投资组合数据
 */

import { useState, useEffect, useCallback } from 'react'
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
  const { selectedModelId, isAggregatedView, config } = useAppStore()
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [chartData, setChartData] = useState<AccountValueHistory[] | ModelChartData[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * 加载投资组合数据
   */
  const loadPortfolio = useCallback(async () => {
    // 如果没有选中模型且不是聚合视图，不加载
    if (!selectedModelId && !isAggregatedView) {
      setPortfolio(null)
      setChartData([])
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      if (isAggregatedView) {
        // 聚合视图
        const response = await apiClient.getAggregatedPortfolio()
        
        if (response.success && response.data) {
          setPortfolio(response.data.portfolio)
          setChartData(response.data.chart_data)
        } else {
          setError(response.error || '获取聚合投资组合失败')
        }
      } else if (selectedModelId) {
        // 单个模型视图
        const response = await apiClient.getModelPortfolio(selectedModelId)
        
        if (response.success && response.data) {
          setPortfolio(response.data.portfolio)
          setChartData(response.data.account_value_history)
        } else {
          setError(response.error || '获取投资组合失败')
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取投资组合失败')
    } finally {
      setIsLoading(false)
    }
  }, [selectedModelId, isAggregatedView])

  // 当选中模型或视图模式变化时重新加载
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
