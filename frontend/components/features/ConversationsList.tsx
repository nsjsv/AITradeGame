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
      <Card>
        <CardHeader>
          <CardTitle>AI 对话</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-muted-foreground text-sm">暂无对话记录</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // 加载状态
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>AI 对话</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <p className="text-muted-foreground text-sm">加载中...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI 对话</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="max-h-[600px] space-y-4 overflow-y-auto">
          {conversations.map((conversation: Conversation) => (
            <div
              key={conversation.id}
              className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-muted-foreground text-xs">
                  {formatTimestamp(conversation.timestamp, 'datetime')}
                </span>
              </div>
              <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                {conversation.ai_response}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
})
