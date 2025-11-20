/**
 * useProviders Hook - API 提供方管理
 * 
 * 用于获取、创建和删除 API 提供方
 */

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import type { ApiProvider, CreateProviderRequest, FetchModelsRequest } from '@/lib/types'

interface UseProvidersReturn {
  providers: ApiProvider[]
  isLoading: boolean
  error: string | null
  loadProviders: () => Promise<void>
  createProvider: (data: CreateProviderRequest) => Promise<boolean>
  deleteProvider: (id: number) => Promise<boolean>
  fetchProviderModels: (data: FetchModelsRequest) => Promise<string[] | null>
}

export function useProviders(): UseProvidersReturn {
  const providers = useAppStore((state) => state.providers)
  const setProviders = useAppStore((state) => state.setProviders)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * 加载提供方列表
   */
  const loadProviders = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getProviders()
      
      if (!response.error && response.data) {
        setProviders(response.data)
      } else {
        setError(response.error || '获取提供方列表失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取提供方列表失败')
    } finally {
      setIsLoading(false)
    }
  }, [setProviders])

  /**
   * 创建新提供方
   */
  const createProvider = useCallback(async (data: CreateProviderRequest): Promise<boolean> => {
    setError(null)
    
    try {
      const response = await apiClient.createProvider(data)
      
      const isSuccess = !response.error
      if (isSuccess) {
        await loadProviders()
        return true
      } else {
        setError(response.error || '创建提供方失败')
        return false
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建提供方失败')
      return false
    }
  }, [loadProviders])

  /**
   * 删除提供方
   */
  const deleteProvider = useCallback(async (id: number): Promise<boolean> => {
    setError(null)
    
    try {
      const response = await apiClient.deleteProvider(id)
      
      const isSuccess = !response.error
      if (isSuccess) {
        await loadProviders()
        return true
      } else {
        setError(response.error || '删除提供方失败')
        return false
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除提供方失败')
      return false
    }
  }, [loadProviders])

  /**
   * 从提供方 API 获取可用模型列表
   */
  const fetchProviderModels = useCallback(async (data: FetchModelsRequest): Promise<string[] | null> => {
    setError(null)
    
    try {
      const response = await apiClient.fetchProviderModels(data)
      
      if (!response.error && response.data) {
        return response.data.models
      } else {
        const errorMsg = response.error || '获取模型列表失败'
        setError(errorMsg)
        // 抛出错误以便组件能够捕获并显示
        throw new Error(errorMsg)
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取模型列表失败'
      setError(errorMsg)
      throw err
    }
  }, [])

  // 初始加载
  useEffect(() => {
    loadProviders()
  }, [loadProviders])

  return {
    providers,
    isLoading,
    error,
    loadProviders,
    createProvider,
    deleteProvider,
    fetchProviderModels,
  }
}
