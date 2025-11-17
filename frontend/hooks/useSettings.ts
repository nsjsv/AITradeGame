/**
 * useSettings Hook - 系统设置管理
 * 
 * 用于获取和更新系统设置
 */

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'
import type { SystemSettings, FrontendConfig } from '@/lib/types'

interface UseSettingsReturn {
  settings: SystemSettings | null
  config: FrontendConfig | null
  isLoading: boolean
  error: string | null
  loadSettings: () => Promise<void>
  loadConfig: () => Promise<void>
  updateSettings: (data: SystemSettings) => Promise<boolean>
}

export function useSettings(): UseSettingsReturn {
  const { config, setConfig } = useAppStore()
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * 加载系统设置
   */
  const loadSettings = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getSettings()
      
      if (response.success && response.data) {
        setSettings(response.data)
      } else {
        setError(response.error || '获取系统设置失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取系统设置失败')
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * 加载前端配置
   */
  const loadConfig = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getConfig()
      
      if (response.success && response.data) {
        setConfig(response.data)
      } else {
        setError(response.error || '获取前端配置失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取前端配置失败')
    } finally {
      setIsLoading(false)
    }
  }, [setConfig])

  /**
   * 更新系统设置
   */
  const updateSettings = useCallback(async (data: SystemSettings): Promise<boolean> => {
    setError(null)
    
    try {
      const response = await apiClient.updateSettings(data)
      
      if (response.success) {
        await loadSettings()
        await loadConfig()
        return true
      } else {
        setError(response.error || '更新系统设置失败')
        return false
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新系统设置失败')
      return false
    }
  }, [loadSettings, loadConfig])

  // 初始加载
  useEffect(() => {
    loadSettings()
    loadConfig()
  }, [loadSettings, loadConfig])

  return {
    settings,
    config,
    isLoading,
    error,
    loadSettings,
    loadConfig,
    updateSettings,
  }
}
