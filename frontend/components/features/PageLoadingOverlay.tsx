'use client'

import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PageLoadingOverlayProps {
  show: boolean
  message?: string
}

/**
 * PageLoadingOverlay - 显示页面级别的加载提示
 * 
 * 每当数据刷新时，覆盖当前界面，提供明确的加载状态反馈
 */
export function PageLoadingOverlay({ show, message = '正在载入界面，请稍候…' }: PageLoadingOverlayProps) {
  return (
    <div
      className={cn(
        'fixed inset-0 z-40 flex items-center justify-center transition-opacity duration-300',
        show ? 'opacity-100' : 'pointer-events-none opacity-0'
      )}
      aria-live="polite"
      aria-busy={show}
    >
      <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" />
      <div className="relative flex min-w-[220px] flex-col items-center gap-3 rounded-2xl border border-border bg-card/90 px-8 py-6 text-center shadow-large">
        <Loader2 className="h-6 w-6 animate-spin text-foreground" />
        <p className="text-sm text-foreground/80">{message}</p>
      </div>
    </div>
  )
}
