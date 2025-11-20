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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useAppStore } from '@/store/useAppStore'
import { useModels } from '@/hooks/useModels'
import { cn } from '@/lib/utils'

export const ModelList = React.memo(function ModelList() {
  const { models, isLoading, deleteModel } = useModels()
  const selectedModelId = useAppStore((state) => state.selectedModelId)
  const isAggregatedView = useAppStore((state) => state.isAggregatedView)
  const setSelectedModel = useAppStore((state) => state.setSelectedModel)
  const setAggregatedView = useAppStore((state) => state.setAggregatedView)
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
      <div className="p-4 text-sm text-muted-foreground">加载中...</div>
    )
  }

  return (
    <div className="space-y-1">
      {models.length === 0 ? (
        <div className="py-8 text-center text-sm text-muted-foreground">
          暂无模型，请添加新模型
        </div>
      ) : (
        <>
          {/* 聚合视图选项 */}
          <button
            onClick={handleSelectAggregated}
            className={cn(
              'w-full flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors',
              'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
              isAggregatedView
                ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                : 'text-sidebar-foreground'
            )}
          >
            <div className="flex items-center gap-2">
              <TrendingUp className="size-4" />
              <span>聚合视图</span>
            </div>
            <span className="text-xs text-muted-foreground">
              {models.length}
            </span>
          </button>

          {/* 模型列表 */}
          {models.map((model) => (
            <div
              key={model.id}
              onClick={() => handleSelectModel(model.id)}
              className={cn(
                'group relative flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors cursor-pointer',
                'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                selectedModelId === model.id
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                  : 'text-sidebar-foreground'
              )}
            >
              <div className="flex-1 min-w-0">
                <div className="truncate">{model.name}</div>
                <div className="text-xs text-muted-foreground truncate">
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
                  'h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity',
                  deletingId === model.id && 'opacity-50'
                )}
                title="删除模型"
              >
                <Trash2 className="size-3" />
              </Button>
            </div>
          ))}
        </>
      )}
    </div>
  )
})
