/**
 * ModelList 组件 - 显示交易模型列表
 * 
 * 功能：
 * - 显示所有交易模型
 * - 支持选择单个模型或聚合视图
 * - 高亮当前选中的模型
 * - 支持删除模型
 */

'use client'

import React, { useState, useCallback } from 'react'
import { Trash2, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { useModels } from '@/hooks/useModels'
import { cn } from '@/lib/utils'

export const ModelList = React.memo(function ModelList() {
  const { models, isLoading, deleteModel } = useModels()
  const { selectedModelId, isAggregatedView, setSelectedModel, setAggregatedView } = useAppStore()
  const [deletingId, setDeletingId] = useState<number | null>(null)

  /**
   * 处理模型选择
   */
  const handleSelectModel = useCallback((id: number) => {
    if (selectedModelId === id) {
      return // 已经选中，不做处理
    }
    setSelectedModel(id)
  }, [selectedModelId, setSelectedModel])

  /**
   * 处理聚合视图选择
   */
  const handleSelectAggregated = useCallback(() => {
    if (isAggregatedView) {
      return // 已经是聚合视图，不做处理
    }
    setAggregatedView(true)
  }, [isAggregatedView, setAggregatedView])

  /**
   * 处理删除模型
   */
  const handleDeleteModel = useCallback(async (id: number, e: React.MouseEvent) => {
    e.stopPropagation() // 阻止事件冒泡到父元素
    
    if (!confirm('确定要删除这个模型吗？')) {
      return
    }

    setDeletingId(id)
    const success = await deleteModel(id)
    setDeletingId(null)

    if (success && selectedModelId === id) {
      // 如果删除的是当前选中的模型，切换到聚合视图
      setAggregatedView(true)
    }
  }, [deleteModel, selectedModelId, setAggregatedView])

  if (isLoading && models.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>交易模型</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">加载中...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>交易模型</CardTitle>
      </CardHeader>
      <CardContent>
        {models.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            暂无模型，请添加新模型
          </div>
        ) : (
          <div className="space-y-2">
            {/* 聚合视图选项 */}
            <button
              onClick={handleSelectAggregated}
              className={cn(
                'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
                'hover:bg-accent',
                isAggregatedView
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'bg-background'
              )}
            >
              <div className="flex items-center gap-2">
                <TrendingUp className="size-4" />
                <span className="font-medium">聚合视图</span>
              </div>
              <span className="text-xs opacity-75">
                {models.length} 个模型
              </span>
            </button>

            {/* 模型列表 */}
            {
            models.map((model) => (
              <div
                key={model.id}
                onClick={() => handleSelectModel(model.id)}
                className={cn(
                  'group relative flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer',
                  'hover:bg-accent',
                  selectedModelId === model.id
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'bg-background'
                )}
              >
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{model.name}</div>
                  <div
                    className={cn(
                      'text-xs truncate',
                      selectedModelId === model.id
                        ? 'opacity-75'
                        : 'text-muted-foreground'
                    )}
                  >
                    {model.model_name}
                  </div>
                </div>

                {/* 删除按钮 */}
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={(e) => handleDeleteModel(model.id, e)}
                  disabled={deletingId === model.id}
                  className={cn(
                    'opacity-0 group-hover:opacity-100 transition-opacity',
                    selectedModelId === model.id && 'text-primary-foreground hover:text-primary-foreground',
                    deletingId === model.id && 'opacity-50'
                  )}
                  title="删除模型"
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
})
