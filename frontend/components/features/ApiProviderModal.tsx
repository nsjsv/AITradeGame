/**
 * ApiProviderModal 组件 - API 提供方管理对话框
 * 
 * 功能:
 * - 提供方名称、API URL、API 密钥、可用模型输入
 * - 自动获取模型列表功能
 * - 显示已保存的提供方列表
 * - 提供方删除功能
 * - 左右分栏布局
 * - 智能 URL 处理
 */

'use client'

import React, { useState, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useProviders } from '@/hooks/useProviders'
import { Trash2Icon, RefreshCwIcon, XIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { CreateProviderRequest } from '@/lib/types'

interface ApiProviderModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ApiProviderModal({ open, onOpenChange }: ApiProviderModalProps) {
  const { providers, createProvider, deleteProvider, fetchProviderModels } = useProviders()

  // 表单状态
  const [name, setName] = useState<string>('')
  const [apiUrl, setApiUrl] = useState<string>('')
  const [apiKey, setApiKey] = useState<string>('')
  const [modelsList, setModelsList] = useState<string[]>([])
  
  // UI 状态
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isFetching, setIsFetching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fetchError, setFetchError] = useState<string | null>(null)

  // 重置表单
  const resetForm = useCallback(() => {
    setName('')
    setApiUrl('')
    setApiKey('')
    setModelsList([])
    setError(null)
    setFetchError(null)
  }, [])
  
  // 移除模型
  const removeModel = useCallback((modelToRemove: string) => {
    setModelsList(prev => prev.filter(m => m !== modelToRemove))
  }, [])

  // 表单验证
  const validateForm = useCallback((): string | null => {
    if (!name.trim()) {
      return '请输入提供方名称'
    }
    if (!apiUrl.trim()) {
      return '请输入 API URL'
    }
    if (!apiKey.trim()) {
      return '请输入 API 密钥'
    }
    if (modelsList.length === 0) {
      return '请先获取模型列表'
    }
    return null
  }, [name, apiUrl, apiKey, modelsList])

  // 自动获取模型列表
  const handleFetchModels = useCallback(async () => {
    if (!apiUrl.trim() || !apiKey.trim()) {
      setFetchError('请先填写 API URL 和 API 密钥')
      return
    }

    setIsFetching(true)
    setFetchError(null)

    try {
      const fetchedModels = await fetchProviderModels({
        api_url: apiUrl.trim(),
        api_key: apiKey.trim(),
      })

      if (fetchedModels && fetchedModels.length > 0) {
        setModelsList(fetchedModels)
        setFetchError(null)
      } else {
        setFetchError('未能获取到模型列表，请检查 API URL 和密钥是否正确')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取模型列表失败'
      setFetchError(errorMessage)
    } finally {
      setIsFetching(false)
    }
  }, [apiUrl, apiKey, fetchProviderModels])

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
      const data: CreateProviderRequest = {
        name: name.trim(),
        api_url: apiUrl.trim(),
        api_key: apiKey.trim(),
        models: JSON.stringify(modelsList),
      }

      const success = await createProvider(data)

      if (success) {
        resetForm()
      } else {
        setError('创建提供方失败，请重试')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建提供方失败')
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, name, apiUrl, apiKey, modelsList, createProvider, resetForm])

  // 删除提供方
  const handleDelete = useCallback(async (id: number) => {
    if (!confirm('确定要删除此提供方吗？')) {
      return
    }

    const success = await deleteProvider(id)
    if (!success) {
      setError('删除提供方失败')
    }
  }, [deleteProvider])

  // 对话框关闭时重置表单
  const handleOpenChange = useCallback((newOpen: boolean) => {
    if (!newOpen) {
      resetForm()
    }
    onOpenChange(newOpen)
  }, [resetForm, onOpenChange])

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-[95vw] sm:max-w-[900px] max-h-[90vh] overflow-hidden p-4 sm:p-6">
        <DialogHeader>
          <DialogTitle>API 提供方管理</DialogTitle>
          <DialogDescription>
            添加和管理 LLM API 提供方配置
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col lg:flex-row gap-6 overflow-hidden">
          {/* 左侧/上方：添加提供方表单 */}
          <div className="flex-1 space-y-4 overflow-y-auto lg:pr-2">
            <h3 className="text-sm font-semibold">添加新提供方</h3>
            
            {/* 提供方名称 */}
            <div className="grid gap-2.5">
              <label htmlFor="name" className="text-sm font-medium ml-2">
                提供方名称
              </label>
              <div className="ml-2">
                <Input
                  id="name"
                  placeholder="例如: OpenAI"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-10"
                />
              </div>
            </div>

            {/* API URL */}
            <div className="grid gap-2.5">
              <label htmlFor="apiUrl" className="text-sm font-medium ml-2">
                API URL
              </label>
              <div className="ml-2">
                <Input
                  id="apiUrl"
                  placeholder="https://api.openai.com"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="h-10"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  后端会自动添加 /v1（如需要）
                </p>
              </div>
            </div>

            {/* API 密钥 */}
            <div className="grid gap-2.5">
              <label htmlFor="apiKey" className="text-sm font-medium ml-2">
                API 密钥
              </label>
              <div className="ml-2">
                <Input
                  id="apiKey"
                  type="password"
                  placeholder="sk-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="h-10"
                />
              </div>
            </div>

            {/* 获取模型按钮 */}
            <div className="grid gap-2.5">
              <div className="flex items-center justify-between mb-1">
                <label className="text-sm font-medium">
                  可用模型
                </label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleFetchModels}
                  disabled={isFetching || !apiUrl || !apiKey}
                >
                  <RefreshCwIcon className={cn('size-4 mr-2', isFetching && 'animate-spin')} />
                  {isFetching ? '获取中...' : '获取模型列表'}
                </Button>
              </div>
              
              {/* 模型列表显示 */}
              {modelsList.length > 0 && (
                <div className="flex flex-wrap gap-2 p-4 rounded-md border bg-muted/50 max-h-[200px] overflow-y-auto">
                  {modelsList.map((model) => (
                    <Badge
                      key={model}
                      variant="secondary"
                      className="gap-1 pr-1 py-1"
                    >
                      <span className="text-xs">{model}</span>
                      <button
                        type="button"
                        onClick={() => removeModel(model)}
                        className="ml-1 rounded-sm hover:bg-muted-foreground/20 p-0.5"
                      >
                        <XIcon className="size-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
              
              {fetchError && (
                <p className="text-sm text-destructive mt-1">{fetchError}</p>
              )}
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            {/* 提交按钮 */}
            <div className="flex justify-end gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isSubmitting}
                className="h-10 px-4"
              >
                关闭
              </Button>
              <Button 
                onClick={handleSubmit} 
                disabled={isSubmitting || modelsList.length === 0}
                className="h-10 px-4"
              >
                {isSubmitting ? '添加中...' : '添加提供方'}
              </Button>
            </div>
          </div>

          {/* 右侧/下方：已有提供方列表 */}
          <div className="w-full lg:w-[380px] lg:border-l lg:pl-6 border-t lg:border-t-0 pt-6 lg:pt-0 mt-4 lg:mt-0 flex flex-col max-h-[300px] lg:max-h-none">
            <h3 className="text-sm font-semibold mb-4">已有提供方</h3>
            
            <div className="flex-1 overflow-y-auto space-y-3">
              {providers.length === 0 ? (
                <div className="py-8 text-center text-sm text-muted-foreground">
                  暂无提供方
                </div>
              ) : (
                providers.map((provider) => {
                  let providerModels: string[] = []
                  try {
                    providerModels = JSON.parse(provider.models || '[]')
                  } catch {
                    providerModels = []
                  }
                  
                  return (
                    <div
                      key={provider.id}
                      className="rounded-lg border p-4 space-y-2.5 hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm truncate mb-1">{provider.name}</h4>
                          <p className="text-xs text-muted-foreground truncate">
                            {provider.api_url}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          onClick={() => handleDelete(provider.id)}
                          className="text-destructive hover:text-destructive flex-shrink-0"
                        >
                          <Trash2Icon className="size-4" />
                        </Button>
                      </div>
                      
                      {providerModels.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {providerModels.slice(0, 3).map((model) => (
                            <Badge
                              key={model}
                              variant="outline"
                              className="text-xs py-0.5"
                            >
                              {model}
                            </Badge>
                          ))}
                          {providerModels.length > 3 && (
                            <Badge variant="outline" className="text-xs py-0.5">
                              +{providerModels.length - 3}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default ApiProviderModal
