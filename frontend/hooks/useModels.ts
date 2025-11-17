/**
 * useModels Hook - 模型数据管理
 * 
 * 用于获取、创建和删除交易模型
 */

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import type { TradingModel, CreateModelRequest } from '@/lib/types'

interface UseModelsReturn {
  models: TradingModel[]
  isLoading: boolean
  error: string | null
  loadModels: () => Promise<void>
  createModel: (data: CreateModelRequest) => Promise<boolean>
  deleteModel: (id: number) => Promise<boolean>
  executeTrading: (id: number) => Promise<boolean>
}

export function useModels(): UseModelsReturn {
  const { models, setModels } = useAppStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * 加载模型列表
   */
  const loadModels = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getModels()
      
      if (response.success && response.data) {
        setModels(response.data)
      } else {
        setError(response.error || '获取模型列表失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取模型列表失败')
    } finally {
      setIsLoading(false)
    }
  }, [setModels])

  /**
   * 创建新模型
   */
  const createModel = useCallback(async (data: CreateModelRequest): Promise<boolean> => {
    setError(null)
    
    try {
      const response = await apiClient.createModel(data)
      
      if (response.success) {
        await loadModels()
        return true
      } else {
        setError(response.error || '创建模型失败')
        return false
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建模型失败')
      return false
    }
  }, [loadModels])

  /**
   * 删除模型
   */
  const deleteModel = useCallback(async (id: number): Promise<boolean> => {
    setError(null)
    
    try {
      const response = await apiClient.deleteModel(id)
      
      if (response.success) {
        await loadModels()
        return true
      } else {
        setError(response.error || '删除模型失败')
        return false
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除模型失败')
      return false
    }
  }, [loadModels])

  /**
   * 执行交易周期
   */
  const executeTrading = useCallback(async (id: number): Promise<boolean> => {
    setError(null)
    
    try {
      const response = await apiClient.executeTrading(id)
      
      if (response.success) {
        return true
      } else {
        setError(response.error || '执行交易失败')
        return false
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '执行交易失败')
      return false
    }
  }, [])

  // 初始加载
  useEffect(() => {
    loadModels()
  }, [loadModels])

  return {
    models,
    isLoading,
    error,
    loadModels,
    createModel,
    deleteModel,
    executeTrading,
  }
}
