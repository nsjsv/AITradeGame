'use client'

/**
 * TradesTable 组件 - 交易记录表格
 * 
 * 显示交易历史，包括时间、币种、操作、数量、价格、盈亏和费用
 * 使用徽章显示交易信号（开多、开空、平仓）
 * 在聚合视图中隐藏
 */

import React from 'react'
import { useTrades } from '@/hooks'
import { useAppStore } from '@/store/useAppStore'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/Table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import {
  formatPrice,
  formatQuantity,
  formatTimestamp,
  getPnlColorClass,
} from '@/lib/utils'
import type { Trade } from '@/lib/types'

/**
 * 获取交易信号的徽章配置
 */
function getSignalBadge(signal: Trade['signal']) {
  switch (signal) {
    case 'buy_to_enter':
      return {
        label: '开多',
        variant: 'success' as const,
      }
    case 'sell_to_enter':
      return {
        label: '开空',
        variant: 'warning' as const,
      }
    case 'close_position':
      return {
        label: '平仓',
        variant: 'info' as const,
      }
    default:
      return {
        label: signal,
        variant: 'outline' as const,
      }
  }
}

export const TradesTable = React.memo(function TradesTable() {
  const { trades, isLoading } = useTrades(50)
  const isAggregatedView = useAppStore((state) => state.isAggregatedView)

  // 聚合视图中隐藏
  if (isAggregatedView) {
    return null
  }

  // 空状态
  if (!isLoading && trades.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>交易记录</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-muted-foreground text-sm">暂无交易记录</p>
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
          <CardTitle>交易记录</CardTitle>
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
        <CardTitle>交易记录</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>时间</TableHead>
              <TableHead>币种</TableHead>
              <TableHead>操作</TableHead>
              <TableHead className="text-right">数量</TableHead>
              <TableHead className="text-right">价格</TableHead>
              <TableHead className="text-right">盈亏</TableHead>
              <TableHead className="text-right">费用</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((trade: Trade) => {
              const signalBadge = getSignalBadge(trade.signal)
              return (
                <TableRow key={trade.id}>
                  <TableCell className="text-muted-foreground text-xs">
                    {formatTimestamp(trade.timestamp, 'datetime')}
                  </TableCell>
                  <TableCell className="font-medium">{trade.coin}</TableCell>
                  <TableCell>
                    <Badge variant={signalBadge.variant}>
                      {signalBadge.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    {formatQuantity(trade.quantity)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatPrice(trade.price)}
                  </TableCell>
                  <TableCell className={`text-right font-medium ${getPnlColorClass(trade.pnl)}`}>
                    {formatPrice(trade.pnl)}
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {formatPrice(trade.fee)}
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
})
