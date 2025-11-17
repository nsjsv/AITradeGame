/**
 * StatsGrid 组件 - 显示投资组合统计信息
 * 
 * 功能：
 * - 显示账户总值、可用现金、已实现盈亏、未实现盈亏
 * - 使用适当的颜色编码格式化盈亏值（中文约定：红涨绿跌）
 * - 实现响应式网格布局
 */

'use client'

import React, { useMemo } from 'react'
import { Wallet, DollarSign, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { formatPrice, getPnlColorClass } from '@/lib/utils'
import type { Portfolio } from '@/lib/types'
import { cn } from '@/lib/utils'

interface StatsGridProps {
  portfolio: Portfolio | null
  isLoading?: boolean
}

interface StatCardProps {
  title: string
  value: string
  icon: React.ReactNode
  colorClass?: string
  description?: string
}

/**
 * 单个统计卡片组件
 */
const StatCard = React.memo(function StatCard({ title, value, icon, colorClass, description }: StatCardProps) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 py-4">
        {/* 图标 */}
        <div className="flex size-12 items-center justify-center rounded-lg bg-muted">
          {icon}
        </div>

        {/* 内容 */}
        <div className="flex-1 min-w-0">
          <div className="text-sm text-muted-foreground">{title}</div>
          <div className={cn('text-2xl font-bold font-mono truncate', colorClass)}>
            {value}
          </div>
          {description && (
            <div className="text-xs text-muted-foreground mt-0.5">{description}</div>
          )}
        </div>
      </CardContent>
    </Card>
  )
})

export const StatsGrid = React.memo(function StatsGrid({ portfolio, isLoading }: StatsGridProps) {
  // 加载状态
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="flex items-center gap-4 py-4">
              <div className="size-12 rounded-lg bg-muted animate-pulse" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-20 bg-muted animate-pulse rounded" />
                <div className="h-6 w-32 bg-muted animate-pulse rounded" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  // 无数据状态
  if (!portfolio) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="账户总值"
          value="$0.00"
          icon={<Wallet className="size-6 text-muted-foreground" />}
        />
        <StatCard
          title="可用现金"
          value="$0.00"
          icon={<DollarSign className="size-6 text-muted-foreground" />}
        />
        <StatCard
          title="已实现盈亏"
          value="$0.00"
          icon={<TrendingUp className="size-6 text-muted-foreground" />}
        />
        <StatCard
          title="未实现盈亏"
          value="$0.00"
          icon={<TrendingDown className="size-6 text-muted-foreground" />}
        />
      </div>
    )
  }

  // 计算盈亏颜色类名（中文约定：红色表示盈利，绿色表示亏损）
  const realizedPnlColor = useMemo(() => getPnlColorClass(portfolio.realized_pnl), [portfolio.realized_pnl])
  const unrealizedPnlColor = useMemo(() => getPnlColorClass(portfolio.unrealized_pnl), [portfolio.unrealized_pnl])

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* 账户总值 */}
      <StatCard
        title="账户总值"
        value={formatPrice(portfolio.total_value)}
        icon={<Wallet className="size-6 text-primary" />}
        description="总资产价值"
      />

      {/* 可用现金 */}
      <StatCard
        title="可用现金"
        value={formatPrice(portfolio.cash)}
        icon={<DollarSign className="size-6 text-blue-600 dark:text-blue-500" />}
        description="可用于交易"
      />

      {/* 已实现盈亏 */}
      <StatCard
        title="已实现盈亏"
        value={formatPrice(portfolio.realized_pnl)}
        icon={
          <TrendingUp
            className={cn(
              'size-6',
              realizedPnlColor
            )}
          />
        }
        colorClass={realizedPnlColor}
        description="已平仓收益"
      />

      {/* 未实现盈亏 */}
      <StatCard
        title="未实现盈亏"
        value={formatPrice(portfolio.unrealized_pnl)}
        icon={
          <TrendingDown
            className={cn(
              'size-6',
              unrealizedPnlColor
            )}
          />
        }
        colorClass={unrealizedPnlColor}
        description="持仓浮动盈亏"
      />
    </div>
  )
})
