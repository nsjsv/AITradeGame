/**
 * Backend status polling hook
 *
 * 定期调用 /api/health 并同步状态到全局 store，
 * 供 Header 等组件显示后端在线/离线信息。
 */

'use client'

import { useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { useAppStore } from '@/store/useAppStore'

export function useBackendStatus(interval: number = 15000): void {
  const setBackendStatus = useAppStore((state) => state.setBackendStatus)

  useEffect(() => {
    let cancelled = false

    const checkHealth = async () => {
      const response = await apiClient.getHealth()
      if (cancelled) {
        return
      }

      if (!response.error && response.data?.status === 'ok') {
        setBackendStatus(true, null)
      } else {
        setBackendStatus(
          false,
          response.error || '后端服务不可用'
        )
      }
    }

    const handleError = (err: unknown, message: string) => {
      if (cancelled) {
        return
      }
      const detail = err instanceof Error ? err.message : message
      setBackendStatus(false, detail)
    }

    checkHealth().catch((error) => handleError(error, '无法连接到后端服务'))
    const checkMarket = async () => {
      const response = await apiClient.getMarketHealth()
      if (cancelled) {
        return
      }

      if (response.error || !response.data || response.data.status !== 'ok') {
        setBackendStatus(
          false,
          response.error || '行情服务不可用'
        )
      }
    }
    checkMarket().catch((error) => handleError(error, '行情服务不可用'))

    const timer = window.setInterval(() => {
      checkHealth().catch((error) => handleError(error, '无法连接到后端服务'))
      checkMarket().catch((error) => handleError(error, '行情服务不可用'))
    }, interval)

    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [interval, setBackendStatus])
}
