/**
 * AddModelModal 组件 - 添加交易模型对话框
 * 
 * 功能:
 * - API 提供方选择下拉框
 * - 模型选择下拉框（根据提供方动态更新）
 * - 显示名称和初始资金输入
 * - 表单验证和提交
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useProviders } from '@/hooks/useProviders'
import { useModels } from '@/hooks/useModels'
import type { CreateModelRequest } from '@/lib/types'
import { Bot, Database, DollarSign, Cpu, Sparkles } from 'lucide-react'

interface AddModelModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AddModelModal({ open, onOpenChange }: AddModelModalProps) {
  const { providers } = useProviders()
  const { createModel } = useModels()

  // 表单状态
  const [providerId, setProviderId] = useState<string>('')
  const [modelName, setModelName] = useState<string>('')
  const [displayName, setDisplayName] = useState<string>('')
  const [initialCapital, setInitialCapital] = useState<string>('10000')
  
  // UI 状态
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [availableModels, setAvailableModels] = useState<string[]>([])

  // 当提供方改变时，更新可用模型列表
  useEffect(() => {
    if (providerId) {
      const provider = providers.find(p => p.id === Number(providerId))
      if (provider && provider.models) {
        try {
          // models 字段是 JSON 字符串，需要解析
          const models = JSON.parse(provider.models)
          setAvailableModels(Array.isArray(models) ? models : [])
        } catch {
          setAvailableModels([])
        }
      } else {
        setAvailableModels([])
      }
      // 重置模型选择
      setModelName('')
    }
  }, [providerId, providers])

  // 重置表单
  const resetForm = useCallback(() => {
    setProviderId('')
    setModelName('')
    setDisplayName('')
    setInitialCapital('10000')
    setError(null)
  }, [])

  // 表单验证
  const validateForm = useCallback((): string | null => {
    if (!providerId) {
      return '请选择 API 提供方'
    }
    if (!modelName) {
      return '请选择模型'
    }
    if (!displayName.trim()) {
      return '请输入显示名称'
    }
    const capital = Number(initialCapital)
    if (isNaN(capital) || capital <= 0) {
      return '初始资金必须大于 0'
    }
    return null
  }, [providerId, modelName, displayName, initialCapital])

  // 提交表单
  const handleSubmit = useCallback(async () => {
    // 验证表单
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const data: CreateModelRequest = {
        name: displayName.trim(),
        provider_id: Number(providerId),
        model_name: modelName,
        initial_capital: Number(initialCapital),
      }

      const success = await createModel(data)

      if (success) {
        resetForm()
        onOpenChange(false)
      } else {
        setError('创建模型失败，请重试')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建模型失败')
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, displayName, providerId, modelName, initialCapital, createModel, resetForm, onOpenChange])

  // 对话框关闭时重置表单
  const handleOpenChange = useCallback((newOpen: boolean) => {
    if (!newOpen) {
      resetForm()
    }
    onOpenChange(newOpen)
  }, [resetForm, onOpenChange])

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[460px] p-0 gap-0 overflow-hidden bg-background/95 backdrop-blur-sm" showCloseButton={false}>
        <DialogHeader className="px-6 py-4 border-b border-border/40 bg-muted/30 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-primary/10 text-primary">
              <Bot className="size-4" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold">添加交易模型</DialogTitle>
              <DialogDescription className="text-xs mt-0.5">
                配置新的 AI 交易策略实例
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

        <div className="p-6 space-y-4">
          {/* API 提供方选择 */}
          <div className="space-y-2">
            <label htmlFor="provider" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
              <Database className="size-3.5" />
              API 提供方
            </label>
            <Select value={providerId} onValueChange={setProviderId}>
              <SelectTrigger id="provider" className="w-full h-9 bg-secondary/30 focus:bg-background transition-all">
                <SelectValue placeholder="选择 API 提供方" />
              </SelectTrigger>
              <SelectContent>
                {providers.length === 0 ? (
                  <div className="px-2 py-1.5 text-sm text-muted-foreground">
                    暂无可用提供方
                  </div>
                ) : (
                  providers.map((provider) => (
                    <SelectItem key={provider.id} value={String(provider.id)}>
                      {provider.name}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          {/* 模型选择 */}
          <div className="space-y-2">
            <label htmlFor="model" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
              <Cpu className="size-3.5" />
              基础模型
            </label>
            <Select
              value={modelName}
              onValueChange={setModelName}
              disabled={!providerId || availableModels.length === 0}
            >
              <SelectTrigger id="model" className="w-full h-9 bg-secondary/30 focus:bg-background transition-all">
                <SelectValue placeholder="选择模型" />
              </SelectTrigger>
              <SelectContent>
                {availableModels.length === 0 ? (
                  <div className="px-2 py-1.5 text-sm text-muted-foreground">
                    {providerId ? '该提供方暂无可用模型' : '请先选择提供方'}
                  </div>
                ) : (
                  availableModels.map((model) => (
                    <SelectItem key={model} value={model}>
                      {model}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          {/* 显示名称 */}
          <div className="space-y-2">
            <label htmlFor="displayName" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
              <Sparkles className="size-3.5" />
              显示名称
            </label>
            <Input
              id="displayName"
              placeholder="例如: GPT-4 激进策略"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="h-9 bg-secondary/30 focus:bg-background transition-all"
            />
          </div>

          {/* 初始资金 */}
          <div className="space-y-2">
            <label htmlFor="initialCapital" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
              <DollarSign className="size-3.5" />
              初始资金 (USDT)
            </label>
            <Input
              id="initialCapital"
              type="number"
              placeholder="10000"
              value={initialCapital}
              onChange={(e) => setInitialCapital(e.target.value)}
              min="0"
              step="100"
              className="h-9 bg-secondary/30 focus:bg-background transition-all"
            />
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive flex items-center gap-2">
              <div className="size-1.5 rounded-full bg-destructive" />
              {error}
            </div>
          )}
        </div>

        <DialogFooter className="px-6 py-4 border-t border-border/40 bg-muted/10">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleOpenChange(false)}
            disabled={isSubmitting}
            className="text-muted-foreground hover:text-foreground"
          >
            取消
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            size="sm"
            className="min-w-[80px]"
          >
            {isSubmitting ? '创建中...' : '确认创建'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default AddModelModal
