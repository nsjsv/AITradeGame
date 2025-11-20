/**
 * useConversations Hook - AI 对话管理
 * 
 * 用于获取 AI 对话记录
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import { useInterval } from './useInterval'
import type { Conversation } from '@/lib/types'

interface UseConversationsReturn {
  conversations: Conversation[]
  isLoading: boolean
  error: string | null
  loadConversations: () => Promise<void>
}

export function useConversations(limit: number = 20): UseConversationsReturn {
  const selectedModelId = useAppStore((state) => state.selectedModelId)
  const isAggregatedView = useAppStore((state) => state.isAggregatedView)
  const config = useAppStore((state) => state.config)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshInterval = useMemo(
    () => (config?.portfolio_refresh_interval ? config.portfolio_refresh_interval * 1000 : 10000),
    [config?.portfolio_refresh_interval]
  )

  /**
   * 加载对话记录
   */
  const loadConversations = useCallback(async () => {
    // 聚合视图不显示对话记录
    if (isAggregatedView || !selectedModelId) {
      setConversations([])
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getModelConversations(selectedModelId, limit)
      
      if (!response.error && response.data) {
        setConversations(response.data)
      } else {
        setError(response.error || '获取对话记录失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取对话记录失败')
    } finally {
      setIsLoading(false)
    }
  }, [selectedModelId, isAggregatedView, limit])

  // 当选中模型变化时重新加载
  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  // 定时刷新（仅在单模型视图下）
  useInterval(
    loadConversations,
    !isAggregatedView && selectedModelId ? refreshInterval : null
  )

  return {
    conversations,
    isLoading,
    error,
    loadConversations,
  }
}
