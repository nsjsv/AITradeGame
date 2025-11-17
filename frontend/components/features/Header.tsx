/**
 * Header 组件 - 顶部导航栏
 * 
 * 功能：
 * - 显示应用标题和运行状态
 * - 提供刷新、设置、添加模型等操作按钮
 * - 显示更新通知指示器
 * - 提供 GitHub 链接
 */

'use client'

import React, { useState, useCallback, useMemo } from 'react'
import { useTheme } from 'next-themes'
import { 
  RefreshCw, 
  Settings, 
  Plus, 
  Github, 
  Bell,
  Menu,
  X,
  Moon,
  Sun
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { useUpdate } from '@/hooks/useUpdate'

interface HeaderProps {
  onRefresh?: () => void
  onOpenSettings?: () => void
  onOpenAddModel?: () => void
  onOpenApiProvider?: () => void
  onOpenUpdate?: () => void
}

export const Header = React.memo(function Header({
  onRefresh,
  onOpenSettings,
  onOpenAddModel,
  onOpenApiProvider,
  onOpenUpdate,
}: HeaderProps) {
  const { isRefreshing, toggleSidebar } = useAppStore()
  const { updateInfo } = useUpdate()
  const { theme, setTheme } = useTheme()
  const [isRunning] = useState(true) // TODO: 从 API 获取实际运行状态

  const hasUpdate = useMemo(
    () => updateInfo?.update_available && !updateInfo.error,
    [updateInfo]
  )

  const toggleTheme = useCallback(() => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }, [theme, setTheme])

  const handleRefresh = useCallback(() => {
    if (onRefresh && !isRefreshing) {
      onRefresh()
    }
  }, [onRefresh, isRefreshing])

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        {/* 左侧：菜单按钮 + 标题 + 状态 */}
        <div className="flex items-center gap-3">
          {/* 移动端菜单按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleSidebar}
            className="lg:hidden"
            aria-label="切换侧边栏"
          >
            <Menu className="size-5" />
          </Button>

          {/* 应用标题 */}
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100 sm:text-xl">
              AI Trade Game
            </h1>
            
            {/* 运行状态指示器 */}
            <div className="flex items-center gap-1.5">
              <div
                className={`size-2 rounded-full ${
                  isRunning
                    ? 'bg-green-500 animate-pulse'
                    : 'bg-gray-400'
                }`}
                aria-label={isRunning ? '运行中' : '已停止'}
              />
              <span className="hidden text-sm text-gray-600 dark:text-gray-400 sm:inline">
                {isRunning ? '运行中' : '已停止'}
              </span>
            </div>
          </div>
        </div>

        {/* 右侧：操作按钮 */}
        <div className="flex items-center gap-2">
          {/* 刷新按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            aria-label="刷新数据"
            title="刷新数据"
          >
            <RefreshCw
              className={`size-4 ${isRefreshing ? 'animate-spin' : ''}`}
            />
          </Button>

          {/* 更新通知按钮 */}
          {hasUpdate && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={onOpenUpdate}
              className="relative"
              aria-label="有可用更新"
              title="有可用更新"
            >
              <Bell className="size-4" />
              <span className="absolute right-1 top-1 size-2 rounded-full bg-red-500" />
            </Button>
          )}

          {/* 添加模型按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onOpenAddModel}
            className="hidden sm:inline-flex"
          >
            <Plus className="size-4" />
            <span>添加模型</span>
          </Button>

          {/* 移动端添加模型按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onOpenAddModel}
            className="sm:hidden"
            aria-label="添加模型"
            title="添加模型"
          >
            <Plus className="size-4" />
          </Button>

          {/* API 提供方按钮 - 仅桌面端显示文字 */}
          <Button
            variant="outline"
            size="sm"
            onClick={onOpenApiProvider}
            className="hidden md:inline-flex"
          >
            API 提供方
          </Button>

          {/* 暗黑模式切换按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? '切换到浅色模式' : '切换到暗黑模式'}
            title={theme === 'dark' ? '切换到浅色模式' : '切换到暗黑模式'}
          >
            {theme === 'dark' ? (
              <Sun className="size-4" />
            ) : (
              <Moon className="size-4" />
            )}
          </Button>

          {/* 设置按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onOpenSettings}
            aria-label="设置"
            title="设置"
          >
            <Settings className="size-4" />
          </Button>

          {/* GitHub 链接 */}
          <Button
            variant="ghost"
            size="icon-sm"
            asChild
            aria-label="访问 GitHub"
            title="访问 GitHub"
          >
            <a
              href="https://github.com/yourusername/aitradegame"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="size-4" />
            </a>
          </Button>
        </div>
      </div>
    </header>
  )
})
