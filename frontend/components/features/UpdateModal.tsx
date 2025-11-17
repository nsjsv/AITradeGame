/**
 * UpdateModal 组件 - 更新通知对话框
 * 
 * 功能:
 * - 显示当前版本、最新版本和发布说明
 * - 实现 Markdown 格式化显示发布说明
 * - 提供 GitHub 发布页面链接
 * - 实现更新通知关闭功能
 */

'use client'

import React, { useMemo, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { ExternalLinkIcon } from 'lucide-react'
import type { UpdateInfo } from '@/lib/types'

interface UpdateModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  updateInfo: UpdateInfo | null
}

export function UpdateModal({ open, onOpenChange, updateInfo }: UpdateModalProps) {
  if (!updateInfo) {
    return null
  }

  // 格式化 Markdown 文本为简单的 HTML
  const formattedReleaseNotes = useMemo(() => {
    const markdown = updateInfo?.release_notes
    if (!markdown) {
      return '暂无发布说明'
    }

    // 简单的 Markdown 格式化
    let formatted = markdown
      // 标题
      .replace(/^### (.*$)/gim, '<h3 class="text-base font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-lg font-semibold mt-4 mb-2">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-xl font-bold mt-4 mb-2">$1</h1>')
      // 粗体
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      // 斜体
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // 代码块
      .replace(/`([^`]+)`/g, '<code class="bg-muted px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
      // 链接
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline">$1</a>')
      // 无序列表
      .replace(/^\* (.*$)/gim, '<li class="ml-4">• $1</li>')
      .replace(/^- (.*$)/gim, '<li class="ml-4">• $1</li>')
      // 换行
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>')

    return formatted
  }, [updateInfo?.release_notes])

  const handleOpenRelease = useCallback(() => {
    if (updateInfo?.release_url) {
      window.open(updateInfo.release_url, '_blank', 'noopener,noreferrer')
    }
  }, [updateInfo?.release_url])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>发现新版本</DialogTitle>
          <DialogDescription>
            有新版本可用，建议更新以获得最新功能和修复
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 版本信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">当前版本</p>
              <p className="text-lg font-semibold">{updateInfo.current_version}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">最新版本</p>
              <p className="text-lg font-semibold text-primary">
                {updateInfo.latest_version}
              </p>
            </div>
          </div>

          {/* 发布说明 */}
          {updateInfo.release_notes && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium">发布说明</h3>
              <div className="rounded-lg border bg-muted/30 p-4 max-h-[300px] overflow-y-auto">
                <div
                  className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: formattedReleaseNotes,
                  }}
                />
              </div>
            </div>
          )}

          {/* GitHub 仓库链接 */}
          {updateInfo.repo_url && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>GitHub 仓库:</span>
              <a
                href={updateInfo.repo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline inline-flex items-center gap-1"
              >
                {updateInfo.repo_url.replace('https://github.com/', '')}
                <ExternalLinkIcon className="size-3" />
              </a>
            </div>
          )}

          {/* 错误信息 */}
          {updateInfo.error && (
            <div className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {updateInfo.error}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            稍后提醒
          </Button>
          {updateInfo.release_url && (
            <Button onClick={handleOpenRelease}>
              <ExternalLinkIcon />
              查看发布页面
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default UpdateModal
