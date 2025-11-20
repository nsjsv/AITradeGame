/**
 * Sidebar 组件 - 侧边栏
 * 
 * 功能：
 * - 集成 ModelList 和 MarketPrices 子组件
 * - 实现响应式设计（移动端隐藏）
 */

'use client'

import React, { useCallback } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'
import { ModelList } from './ModelList'
import { MarketPrices } from './MarketPrices'

interface SidebarProps {
  className?: string
}

export const Sidebar = React.memo(function Sidebar({ className }: SidebarProps) {
  const isSidebarOpen = useAppStore((state) => state.isSidebarOpen)
  const toggleSidebar = useAppStore((state) => state.toggleSidebar)
  
  const handleOverlayClick = useCallback(() => {
    toggleSidebar()
  }, [toggleSidebar])

  return (
    <>
      {/* 移动端遮罩层 */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
          onClick={handleOverlayClick}
          aria-hidden="true"
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={cn(
          // 基础样式
          'fixed left-0 top-0 z-40 h-screen w-64 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground',
          // 移动端：可滑动显示/隐藏
          'transition-transform duration-300 lg:translate-x-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
          // 桌面端：始终显示
          'lg:sticky lg:flex',
          className
        )}
      >
        <div className="flex h-full flex-col overflow-hidden">
          {/* 顶部标题区域 - 仅在移动端显示，桌面端在 Header 中 */}
          <div className="flex h-14 items-center border-b border-sidebar-border px-4 lg:hidden">
             <span className="font-semibold">AI Trade Game</span>
          </div>

          {/* 模型列表区域 */}
          <div className="flex-1 overflow-y-auto p-2">
            <div className="mb-2 px-2 py-1 text-xs font-medium text-muted-foreground">
              模型列表
            </div>
            <ModelList />
          </div>

          {/* 市场价格区域 */}
          <div className="flex-shrink-0 border-t border-sidebar-border bg-sidebar-accent/50 p-2">
             <div className="mb-2 px-2 text-xs font-medium text-muted-foreground">
              市场概览
            </div>
            <MarketPrices />
          </div>
        </div>
      </aside>
    </>
  )
})
