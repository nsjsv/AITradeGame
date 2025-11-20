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
  DialogClose,
} from '@/components/ui/Dialog'
import { X } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useProviders } from '@/hooks/useProviders'
import { Trash2Icon, RefreshCwIcon, XIcon, Server, Key, Globe, Plus, Database } from 'lucide-react'
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
      <DialogContent className="max-w-[95vw] sm:max-w-[900px] max-h-[90vh] overflow-hidden p-0 gap-0 bg-background/95 backdrop-blur-sm" showCloseButton={false}>
        <DialogHeader className="px-6 py-4 border-b border-border/40 bg-muted/30 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-primary/10 text-primary">
              <Server className="size-4" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold">API 提供方管理</DialogTitle>
              <DialogDescription className="text-xs mt-0.5">
                配置 LLM API 连接与模型映射
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

        <div className="flex flex-col lg:flex-row h-[600px] lg:h-[500px] overflow-hidden">
          {/* 左侧：添加提供方表单 */}
          <div className="flex-1 flex flex-col overflow-hidden border-b lg:border-b-0 lg:border-r border-border/40">
            <div className="p-4 border-b border-border/40 bg-muted/10 flex items-center gap-2">
              <Plus className="size-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">添加新连接</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-5">
              {/* 提供方名称 */}
              <div className="space-y-2">
                <label htmlFor="name" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <Database className="size-3.5" />
                  提供方名称
                </label>
                <Input
                  id="name"
                  placeholder="例如: OpenAI, Anthropic"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-9 bg-secondary/30 focus:bg-background transition-all"
                />
              </div>

              {/* API URL */}
              <div className="space-y-2">
                <label htmlFor="apiUrl" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <Globe className="size-3.5" />
                  API URL
                </label>
                <Input
                  id="apiUrl"
                  placeholder="https://api.openai.com"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="h-9 bg-secondary/30 focus:bg-background transition-all"
                />
                <p className="text-[10px] text-muted-foreground/70 pl-1">
                  * 后端会自动适配 /v1 路径
                </p>
              </div>

              {/* API 密钥 */}
              <div className="space-y-2">
                <label htmlFor="apiKey" className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <Key className="size-3.5" />
                  API 密钥
                </label>
                <Input
                  id="apiKey"
                  type="password"
                  placeholder="sk-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="h-9 bg-secondary/30 focus:bg-background transition-all"
                />
              </div>

              {/* 获取模型 */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-muted-foreground">
                    可用模型列表
                  </label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleFetchModels}
                    disabled={isFetching || !apiUrl || !apiKey}
                    className="h-7 text-xs hover:bg-secondary"
                  >
                    <RefreshCwIcon className={cn('size-3 mr-1.5', isFetching && 'animate-spin')} />
                    {isFetching ? '同步中...' : '同步模型'}
                  </Button>
                </div>
                
                {/* 模型列表显示 */}
                <div className="min-h-[80px] p-3 rounded-lg border border-border/50 bg-secondary/20 text-sm">
                  {modelsList.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {modelsList.map((model) => (
                        <Badge
                          key={model}
                          variant="secondary"
                          className="gap-1 pr-1 py-0.5 text-[10px] font-normal bg-background border-border/50"
                        >
                          {model}
                          <button
                            type="button"
                            onClick={() => removeModel(model)}
                            className="ml-1 rounded-full hover:bg-muted-foreground/20 p-0.5 transition-colors"
                          >
                            <XIcon className="size-2.5" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-muted-foreground/50 text-xs gap-1 py-4">
                      <Server className="size-8 opacity-20" />
                      <span>暂无模型数据，请先同步</span>
                    </div>
                  )}
                </div>
                
                {fetchError && (
                  <p className="text-xs text-destructive flex items-center gap-1.5">
                    <span className="size-1.5 rounded-full bg-destructive" />
                    {fetchError}
                  </p>
                )}
              </div>

              {/* 错误提示 */}
              {error && (
                <div className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">
                  {error}
                </div>
              )}
            </div>

            <div className="p-4 border-t border-border/40 bg-muted/10 flex justify-end gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleOpenChange(false)}
                disabled={isSubmitting}
              >
                取消
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting || modelsList.length === 0}
                size="sm"
              >
                {isSubmitting ? '添加中...' : '确认添加'}
              </Button>
            </div>
          </div>

          {/* 右侧：已有提供方列表 */}
          <div className="w-full lg:w-[320px] flex flex-col bg-muted/5">
            <div className="p-4 border-b border-border/40 bg-muted/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="size-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">已连接服务</h3>
              </div>
              <Badge variant="outline" className="text-[10px] h-5 px-1.5 bg-background">
                {providers.length}
              </Badge>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {providers.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-muted-foreground/40 text-xs gap-2">
                  <div className="p-3 rounded-full bg-secondary/50">
                    <Server className="size-6" />
                  </div>
                  <p>暂无已配置的服务商</p>
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
                      className="group relative rounded-lg border border-border/60 bg-card p-3 hover:shadow-sm hover:border-border transition-all duration-200"
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="min-w-0">
                          <h4 className="font-medium text-sm truncate text-foreground/90">{provider.name}</h4>
                          <div className="flex items-center gap-1 text-[10px] text-muted-foreground mt-0.5">
                            <Globe className="size-2.5" />
                            <span className="truncate max-w-[140px]">{provider.api_url}</span>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(provider.id)}
                          className="h-6 w-6 text-muted-foreground hover:text-destructive hover:bg-destructive/10 -mr-1 -mt-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Trash2Icon className="size-3.5" />
                        </Button>
                      </div>
                      
                      <div className="pt-2 border-t border-border/30 flex items-center justify-between text-[10px] text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Database className="size-2.5" />
                          {providerModels.length} 个模型
                        </span>
                        <div className="flex gap-1">
                          {providerModels.slice(0, 2).map(m => (
                            <span key={m} className="bg-secondary px-1 rounded text-[9px] max-w-[60px] truncate">
                              {m}
                            </span>
                          ))}
                          {providerModels.length > 2 && (
                            <span className="bg-secondary px-1 rounded text-[9px]">+{providerModels.length - 2}</span>
                          )}
                        </div>
                      </div>
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
