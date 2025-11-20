/**
 * useUpdate Hook - 更新检查管理
 * 
 * 用于检查软件更新，支持 24 小时内不重复显示已关闭的更新通知
 */

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import type { UpdateInfo } from '@/lib/types'

interface UseUpdateReturn {
  updateInfo: UpdateInfo | null
  isLoading: boolean
  error: string | null
  checkUpdate: () => Promise<void>
  dismissUpdate: () => void
}

const DISMISS_STORAGE_KEY = 'updateDismissedUntil'

/**
 * 检查更新通知是否在抑制期内
 */
function isUpdateDismissed(): boolean {
  if (typeof window === 'undefined') return false
  
  try {
    const dismissedUntil = localStorage.getItem(DISMISS_STORAGE_KEY)
    if (!dismissedUntil) return false
    
    const dismissedTime = parseInt(dismissedUntil, 10)
    return Date.now() < dismissedTime
  } catch (error) {
    console.error('读取更新通知状态失败:', error)
    return false
  }
}

/**
 * 设置更新通知抑制期（24 小时）
 */
function setUpdateDismissed(): void {
  if (typeof window === 'undefined') return
  
  try {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    localStorage.setItem(DISMISS_STORAGE_KEY, tomorrow.getTime().toString())
  } catch (error) {
    console.error('保存更新通知状态失败:', error)
  }
}

export function useUpdate(): UseUpdateReturn {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDismissed, setIsDismissed] = useState(false)

  /**
   * 检查更新
   */
  const checkUpdate = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.checkUpdate()
      
      if (!response.error && response.data) {
        setUpdateInfo(response.data)
        // 检查是否在抑制期内
        const dismissed = isUpdateDismissed()
        setIsDismissed(dismissed)
      } else {
        setError(response.error || '检查更新失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '检查更新失败')
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * 关闭更新通知
   * 设置 24 小时抑制期
   */
  const dismissUpdate = useCallback(() => {
    setIsDismissed(true)
    setUpdateDismissed()
  }, [])

  // 初始检查更新
  useEffect(() => {
    checkUpdate()
  }, [checkUpdate])

  // 如果用户关闭了通知，返回 null
  const visibleUpdateInfo = isDismissed ? null : updateInfo

  return {
    updateInfo: visibleUpdateInfo,
    isLoading,
    error,
    checkUpdate,
    dismissUpdate,
  }
}
