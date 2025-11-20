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

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
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
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>添加交易模型</DialogTitle>
          <DialogDescription>
            创建一个新的 AI 交易模型，选择提供方和模型配置
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* API 提供方选择 */}
          <div className="grid gap-2">
            <label htmlFor="provider" className="text-sm font-medium">
              API 提供方
            </label>
            <Select value={providerId} onValueChange={setProviderId}>
              <SelectTrigger id="provider" className="w-full">
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
          <div className="grid gap-2">
            <label htmlFor="model" className="text-sm font-medium">
              模型
            </label>
            <Select
              value={modelName}
              onValueChange={setModelName}
              disabled={!providerId || availableModels.length === 0}
            >
              <SelectTrigger id="model" className="w-full">
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
          <div className="grid gap-2">
            <label htmlFor="displayName" className="text-sm font-medium">
              显示名称
            </label>
            <Input
              id="displayName"
              placeholder="例如: GPT-4 交易员"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>

          {/* 初始资金 */}
          <div className="grid gap-2">
            <label htmlFor="initialCapital" className="text-sm font-medium">
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
            />
          </div>

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
            onClick={() => handleOpenChange(false)}
            disabled={isSubmitting}
          >
            取消
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? '创建中...' : '创建模型'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default AddModelModal
