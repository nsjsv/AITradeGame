'use client'

/**
 * ConversationsList 组件 - AI 对话列表
 * 
 * 显示 AI 对话历史，包括时间戳和响应内容
 * 实现可滚动列表和空状态处理
 * 在聚合视图中隐藏
 */

import React from 'react'
import { useConversations } from '@/hooks'
import { useAppStore } from '@/store/useAppStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { formatTimestamp } from '@/lib/utils'
import type { Conversation } from '@/lib/types'

export const ConversationsList = React.memo(function ConversationsList() {
  const { conversations, isLoading } = useConversations(20)
  const isAggregatedView = useAppStore((state) => state.isAggregatedView)

  // 聚合视图中隐藏
  if (isAggregatedView) {
    return null
  }

  // 空状态
  if (!isLoading && conversations.length === 0) {
    return (
      <div className="rounded-md border bg-card p-8 text-center text-sm text-muted-foreground shadow-sm">
        暂无对话记录
      </div>
    )
  }

  // 加载状态
  if (isLoading) {
    return (
      <div className="rounded-md border bg-card p-8 text-center text-sm text-muted-foreground shadow-sm">
        加载中...
      </div>
    )
  }

  return (
    <div className="rounded-md border bg-card shadow-sm">
      <div className="p-4 border-b">
        <h3 className="font-semibold leading-none tracking-tight">AI 决策日志</h3>
      </div>
      <div className="max-h-[600px] overflow-y-auto p-4 space-y-4">
        {conversations.map((conversation: Conversation) => (
          <div
            key={conversation.id}
            className="group relative rounded-md border bg-muted/30 p-4 transition-colors hover:bg-muted/50"
          >
            <div className="mb-2 flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-primary/50" />
              <span className="text-xs font-medium text-muted-foreground font-mono">
                {formatTimestamp(conversation.timestamp, 'datetime')}
              </span>
            </div>
            <div className="text-sm leading-relaxed whitespace-pre-wrap break-words text-foreground/90">
              {conversation.ai_response}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})
