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
  DialogClose,
} from '@/components/ui/Dialog'
import { X } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useSettings } from '@/hooks/useSettings'
import type { SystemSettings } from '@/lib/types'
import { Clock, Percent, Activity, RefreshCw, Settings2 } from 'lucide-react'

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
      <DialogContent className="sm:max-w-[600px] p-0 gap-0 overflow-hidden bg-background/95 backdrop-blur-sm" showCloseButton={false}>
        <DialogHeader className="px-6 py-4 border-b border-border/40 bg-muted/30 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-primary/10 text-primary">
              <Settings2 className="size-4" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold">系统设置</DialogTitle>
              <DialogDescription className="text-xs mt-0.5">
                配置交易系统的全局参数与运行频率
              </DialogDescription>
            </div>
          </div>
          <DialogClose asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full hover:bg-secondary -mr-2"
            >
              <X className="size-4" />
            </Button>
          </DialogClose>
        </DialogHeader>

        <div className="p-6 space-y-1">
          {/* 交易频率 */}
          <div className="group flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors border border-transparent hover:border-border/50">
            <div className="space-y-1">
              <label htmlFor="tradingFrequency" className="text-sm font-medium flex items-center gap-2 text-foreground/90">
                <Clock className="size-3.5 text-muted-foreground" />
                交易频率
              </label>
              <p className="text-xs text-muted-foreground pl-5.5">
                AI 模型执行交易决策的时间间隔 (分钟)
              </p>
            </div>
            <div className="w-full sm:w-[140px]">
              <Input
                id="tradingFrequency"
                type="number"
                placeholder="60"
                value={tradingFrequency}
                onChange={(e) => setTradingFrequency(e.target.value)}
                min="1"
                step="1"
                className="h-8 bg-background/50 focus:bg-background transition-all"
              />
            </div>
          </div>

          {/* 交易费率 */}
          <div className="group flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors border border-transparent hover:border-border/50">
            <div className="space-y-1">
              <label htmlFor="tradingFeeRate" className="text-sm font-medium flex items-center gap-2 text-foreground/90">
                <Percent className="size-3.5 text-muted-foreground" />
                交易费率
              </label>
              <p className="text-xs text-muted-foreground pl-5.5">
                每笔交易的手续费率 (例如: 0.001 = 0.1%)
              </p>
            </div>
            <div className="w-full sm:w-[140px]">
              <Input
                id="tradingFeeRate"
                type="number"
                placeholder="0.001"
                value={tradingFeeRate}
                onChange={(e) => setTradingFeeRate(e.target.value)}
                min="0"
                max="1"
                step="0.0001"
                className="h-8 bg-background/50 focus:bg-background transition-all"
              />
            </div>
          </div>

          {/* 市场刷新间隔 */}
          <div className="group flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors border border-transparent hover:border-border/50">
            <div className="space-y-1">
              <label htmlFor="marketRefreshInterval" className="text-sm font-medium flex items-center gap-2 text-foreground/90">
                <Activity className="size-3.5 text-muted-foreground" />
                市场数据刷新
              </label>
              <p className="text-xs text-muted-foreground pl-5.5">
                刷新市场价格的时间间隔 (秒)
              </p>
            </div>
            <div className="w-full sm:w-[140px]">
              <Input
                id="marketRefreshInterval"
                type="number"
                placeholder="5"
                value={marketRefreshInterval}
                onChange={(e) => setMarketRefreshInterval(e.target.value)}
                min="1"
                step="1"
                className="h-8 bg-background/50 focus:bg-background transition-all"
              />
            </div>
          </div>

          {/* 投资组合刷新间隔 */}
          <div className="group flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors border border-transparent hover:border-border/50">
            <div className="space-y-1">
              <label htmlFor="portfolioRefreshInterval" className="text-sm font-medium flex items-center gap-2 text-foreground/90">
                <RefreshCw className="size-3.5 text-muted-foreground" />
                投资组合刷新
              </label>
              <p className="text-xs text-muted-foreground pl-5.5">
                刷新投资组合和图表的时间间隔 (秒)
              </p>
            </div>
            <div className="w-full sm:w-[140px]">
              <Input
                id="portfolioRefreshInterval"
                type="number"
                placeholder="10"
                value={portfolioRefreshInterval}
                onChange={(e) => setPortfolioRefreshInterval(e.target.value)}
                min="1"
                step="1"
                className="h-8 bg-background/50 focus:bg-background transition-all"
              />
            </div>
          </div>

          {/* 成功提示 */}
          {successMessage && (
            <div className="mx-3 rounded-md bg-green-500/10 border border-green-500/20 px-3 py-2 text-xs text-green-600 dark:text-green-400 flex items-center gap-2">
              <div className="size-1.5 rounded-full bg-green-500 animate-pulse" />
              {successMessage}
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <div className="mx-3 rounded-md bg-destructive/10 border border-destructive/20 px-3 py-2 text-xs text-destructive flex items-center gap-2">
              <div className="size-1.5 rounded-full bg-destructive" />
              {error}
            </div>
          )}
        </div>

        <DialogFooter className="px-6 py-4 border-t border-border/40 bg-muted/10">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            disabled={isSubmitting}
            className="text-muted-foreground hover:text-foreground"
          >
            重置默认
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            size="sm"
            className="min-w-[80px]"
          >
            {isSubmitting ? '保存中...' : '保存更改'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default SettingsModal
