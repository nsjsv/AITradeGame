'use client'

/**
 * PositionsTable 组件 - 持仓表格
 * 
 * 显示当前持仓信息，包括币种、方向、数量、价格、杠杆和盈亏
 * 在聚合视图中隐藏
 */

import React from 'react'
import { usePortfolio } from '@/hooks'
import { useAppStore } from '@/store/useAppStore'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  formatPrice,
  formatQuantity,
  getPnlColorClass,
} from '@/lib/utils'
import type { Position } from '@/lib/types'

export const PositionsTable = React.memo(function PositionsTable() {
  const { portfolio, isLoading } = usePortfolio()
  const { isAggregatedView } = useAppStore()

  // 聚合视图中隐藏
  if (isAggregatedView) {
    return null
  }

  // 空状态
  if (!isLoading && (!portfolio || !portfolio.positions || portfolio.positions.length === 0)) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>当前持仓</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-muted-foreground text-sm">暂无持仓</p>
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
          <CardTitle>当前持仓</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <p className="text-muted-foreground text-sm">加载中...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const positions = portfolio?.positions || []

  return (
    <Card>
      <CardHeader>
        <CardTitle>当前持仓</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>币种</TableHead>
              <TableHead>方向</TableHead>
              <TableHead className="text-right">数量</TableHead>
              <TableHead className="text-right">均价</TableHead>
              <TableHead className="text-right">当前价</TableHead>
              <TableHead className="text-right">杠杆</TableHead>
              <TableHead className="text-right">盈亏</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {positions.map((position: Position, index: number) => (
              <TableRow key={`${position.coin}-${position.side}-${index}`}>
                <TableCell className="font-medium">{position.coin}</TableCell>
                <TableCell>
                  <span
                    className={
                      position.side === 'long'
                        ? 'text-profit font-medium'
                        : 'text-loss font-medium'
                    }
                  >
                    {position.side === 'long' ? '多' : '空'}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  {formatQuantity(position.quantity)}
                </TableCell>
                <TableCell className="text-right">
                  {formatPrice(position.avg_price)}
                </TableCell>
                <TableCell className="text-right">
                  {position.current_price !== null
                    ? formatPrice(position.current_price)
                    : '-'}
                </TableCell>
                <TableCell className="text-right">
                  {position.leverage}x
                </TableCell>
                <TableCell className={`text-right font-medium ${getPnlColorClass(position.pnl)}`}>
                  {formatPrice(position.pnl)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
})
