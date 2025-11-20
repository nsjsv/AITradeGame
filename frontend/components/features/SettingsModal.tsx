/**
 * SettingsModal 组件 - 系统设置对话框
 * 
 * 功能:
 * - 交易频率和交易费率配置输入
 * - 输入验证
 * - 设置保存功能
 */

'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useSettings } from '@/hooks/useSettings'
import type { SystemSettings } from '@/lib/types'

interface SettingsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SettingsModal({ open, onOpenChange }: SettingsModalProps) {
  const { settings, loadSettings, updateSettings } = useSettings()

  // 表单状态
  const [tradingFrequency, setTradingFrequency] = useState<string>('')
  const [tradingFeeRate, setTradingFeeRate] = useState<string>('')
  const [marketRefreshInterval, setMarketRefreshInterval] = useState<string>('')
  const [portfolioRefreshInterval, setPortfolioRefreshInterval] = useState<string>('')
  
  // UI 状态
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // 当设置加载时，更新表单
  useEffect(() => {
    if (settings) {
      setTradingFrequency(String(settings.trading_frequency_minutes))
      setTradingFeeRate(String(settings.trading_fee_rate))
      setMarketRefreshInterval(String(settings.market_refresh_interval))
      setPortfolioRefreshInterval(String(settings.portfolio_refresh_interval))
    }
  }, [settings])

  // 表单验证
  const validateForm = useCallback((): string | null => {
    const frequency = Number(tradingFrequency)
    if (isNaN(frequency) || frequency <= 0) {
      return '交易频率必须大于 0'
    }
    if (frequency < 1) {
      return '交易频率不能小于 1 分钟'
    }

    const feeRate = Number(tradingFeeRate)
    if (isNaN(feeRate) || feeRate < 0) {
      return '交易费率不能为负数'
    }
    if (feeRate > 1) {
      return '交易费率不能大于 1 (100%)'
    }

    const marketInterval = Number(marketRefreshInterval)
    if (isNaN(marketInterval) || marketInterval < 1) {
      return '市场刷新间隔必须大于等于 1 秒'
    }

    const portfolioInterval = Number(portfolioRefreshInterval)
    if (isNaN(portfolioInterval) || portfolioInterval < 1) {
      return '投资组合刷新间隔必须大于等于 1 秒'
    }

    return null
  }, [tradingFrequency, tradingFeeRate, marketRefreshInterval, portfolioRefreshInterval])

  // 提交表单
  const handleSubmit = useCallback(async () => {
    // 验证表单
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      setSuccessMessage(null)
      return
    }

    setIsSubmitting(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const data: SystemSettings = {
        trading_frequency_minutes: Number(tradingFrequency),
        trading_fee_rate: Number(tradingFeeRate),
        market_refresh_interval: Number(marketRefreshInterval),
        portfolio_refresh_interval: Number(portfolioRefreshInterval),
      }

      const success = await updateSettings(data)

      if (success) {
        setSuccessMessage('设置已保存')
        // 3 秒后清除成功消息
        setTimeout(() => {
          setSuccessMessage(null)
        }, 3000)
      } else {
        setError('保存设置失败，请重试')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存设置失败')
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, tradingFrequency, tradingFeeRate, marketRefreshInterval, portfolioRefreshInterval, updateSettings])

  // 重置表单到当前设置
  const handleReset = useCallback(() => {
    if (settings) {
      setTradingFrequency(String(settings.trading_frequency_minutes))
      setTradingFeeRate(String(settings.trading_fee_rate))
      setMarketRefreshInterval(String(settings.market_refresh_interval))
      setPortfolioRefreshInterval(String(settings.portfolio_refresh_interval))
      setError(null)
      setSuccessMessage(null)
    }
  }, [settings])

  // 对话框打开时重新加载设置
  useEffect(() => {
    if (open) {
      loadSettings()
      setError(null)
      setSuccessMessage(null)
    }
  }, [open, loadSettings])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>系统设置</DialogTitle>
          <DialogDescription>
            配置交易系统的全局参数
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* 交易频率 */}
          <div className="grid gap-2">
            <label htmlFor="tradingFrequency" className="text-sm font-medium">
              交易频率 (分钟)
            </label>
            <Input
              id="tradingFrequency"
              type="number"
              placeholder="60"
              value={tradingFrequency}
              onChange={(e) => setTradingFrequency(e.target.value)}
              min="1"
              step="1"
            />
            <p className="text-xs text-muted-foreground">
              AI 模型执行交易决策的时间间隔
            </p>
          </div>

          {/* 交易费率 */}
          <div className="grid gap-2">
            <label htmlFor="tradingFeeRate" className="text-sm font-medium">
              交易费率
            </label>
            <Input
              id="tradingFeeRate"
              type="number"
              placeholder="0.001"
              value={tradingFeeRate}
              onChange={(e) => setTradingFeeRate(e.target.value)}
              min="0"
              max="1"
              step="0.0001"
            />
            <p className="text-xs text-muted-foreground">
              每笔交易的手续费率 (例如: 0.001 = 0.1%)
            </p>
          </div>

          {/* 市场刷新间隔 */}
          <div className="grid gap-2">
            <label htmlFor="marketRefreshInterval" className="text-sm font-medium">
              市场数据刷新间隔 (秒)
            </label>
            <Input
              id="marketRefreshInterval"
              type="number"
              placeholder="5"
              value={marketRefreshInterval}
              onChange={(e) => setMarketRefreshInterval(e.target.value)}
              min="1"
              step="1"
            />
            <p className="text-xs text-muted-foreground">
              刷新市场价格的时间间隔，单位为秒
            </p>
          </div>
          {/* 投资组合刷新间隔 */}
          <div className="grid gap-2">
            <label htmlFor="portfolioRefreshInterval" className="text-sm font-medium">
              投资组合刷新间隔 (秒)
            </label>
            <Input
              id="portfolioRefreshInterval"
              type="number"
              placeholder="10"
              value={portfolioRefreshInterval}
              onChange={(e) => setPortfolioRefreshInterval(e.target.value)}
              min="1"
              step="1"
            />
            <p className="text-xs text-muted-foreground">
              刷新投资组合和图表的时间间隔，单位为秒
            </p>
          </div>

          {/* 成功提示 */}
          {successMessage && (
            <div className="rounded-md bg-success/10 px-3 py-2 text-sm text-success">
              {successMessage}
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <div className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleReset}
            disabled={isSubmitting}
          >
            重置
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? '保存中...' : '保存设置'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default SettingsModal
