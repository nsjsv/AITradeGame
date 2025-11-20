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

import React, { useState, useCallback, useMemo, useEffect } from 'react'
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
import { Button } from '@/components/ui/Button'
import { useAppStore } from '@/store/useAppStore'
import { useUpdate } from '@/hooks/useUpdate'
import { useBackendStatus } from '@/hooks/useBackendStatus'

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
  const isRefreshing = useAppStore((state) => state.isRefreshing)
  const toggleSidebar = useAppStore((state) => state.toggleSidebar)
  const backendOnline = useAppStore((state) => state.backendOnline)
  const backendError = useAppStore((state) => state.backendError)
  const backendLastChecked = useAppStore((state) => state.backendLastChecked)
  const { updateInfo } = useUpdate()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useBackendStatus()

  useEffect(() => {
    setMounted(true)
  }, [])

  const hasUpdate = useMemo(
    () => updateInfo?.update_available && !updateInfo.error,
    [updateInfo]
  )

  const toggleTheme = useCallback(() => {
    if (!mounted) {
      return
    }
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }, [theme, setTheme, mounted])

  const handleRefresh = useCallback(() => {
    if (onRefresh && !isRefreshing) {
      onRefresh()
    }
  }, [onRefresh, isRefreshing])

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center justify-between px-4">
        {/* 左侧：菜单按钮 + 标题 + 状态 */}
        <div className="flex items-center gap-2">
          {/* 移动端菜单按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleSidebar}
            className="lg:hidden -ml-2"
            aria-label="切换侧边栏"
          >
            <Menu className="size-4" />
          </Button>

          {/* 面包屑导航风格的标题 */}
          <div className="flex items-center gap-2 text-sm">
            <span className="font-medium text-foreground">AI Trade Game</span>
            <span className="text-muted-foreground">/</span>
            <div className="flex items-center gap-2">
               <div
                className={`size-1.5 rounded-full ${
                  backendOnline ? 'bg-green-500' : 'bg-red-500'
                }`}
                title={backendOnline ? '系统正常' : '系统离线'}
              />
              <span className="text-muted-foreground">
                {backendOnline ? 'Dashboard' : 'Offline'}
              </span>
            </div>
          </div>
        </div>

        {/* 右侧：操作按钮 */}
        <div className="flex items-center gap-1">
          {/* 刷新按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="h-8 px-2 text-muted-foreground hover:text-foreground"
          >
            <RefreshCw
              className={`mr-1 size-3.5 ${isRefreshing ? 'animate-spin' : ''}`}
            />
            <span className="hidden sm:inline text-xs">刷新</span>
          </Button>

          <div className="mx-2 h-4 w-[1px] bg-border" />

          {/* 添加模型按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onOpenAddModel}
            className="h-8 px-2 text-muted-foreground hover:text-foreground"
          >
            <Plus className="mr-1 size-3.5" />
            <span className="hidden sm:inline text-xs">新建模型</span>
          </Button>

          {/* API 提供方按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onOpenApiProvider}
            className="hidden md:inline-flex h-8 px-2 text-muted-foreground hover:text-foreground"
          >
            <span className="text-xs">API 设置</span>
          </Button>

          <div className="mx-2 h-4 w-[1px] bg-border" />

          {/* 暗黑模式切换按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleTheme}
            className="text-muted-foreground hover:text-foreground"
          >
            {mounted ? (
              theme === 'dark' ? (
                <Sun className="size-4" />
              ) : (
                <Moon className="size-4" />
              )
            ) : (
              <Sun className="size-4 opacity-0" />
            )}
          </Button>

          {/* 设置按钮 */}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onOpenSettings}
            className="text-muted-foreground hover:text-foreground"
          >
            <Settings className="size-4" />
          </Button>
          
          {/* GitHub 链接 */}
          <Button
            variant="ghost"
            size="icon-sm"
            asChild
            className="text-muted-foreground hover:text-foreground"
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
