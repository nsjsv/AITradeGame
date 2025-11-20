'use client'

/**
 * PositionsTable 组件 - 持仓表格
 * 
 * 显示当前持仓信息，包括币种、方向、数量、价格、杠杆和盈亏
 * 在聚合视图中隐藏
 */

import React, { useMemo } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/Table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import {
  formatPrice,
  formatQuantity,
  getPnlColorClass,
} from '@/lib/utils'
import type { Portfolio, Position } from '@/lib/types'

interface PositionsTableProps {
  portfolio: Portfolio | null
  isLoading?: boolean
}

export const PositionsTable = React.memo(function PositionsTable({
  portfolio,
  isLoading,
}: PositionsTableProps) {
  const positions = useMemo(
    () => portfolio?.positions ?? [],
    [portfolio?.positions]
  )

  // 空状态
  if (!isLoading && positions.length === 0) {
    return (
      <div className="rounded-md border bg-card p-8 text-center text-sm text-muted-foreground shadow-sm">
        暂无持仓
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
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead className="w-[100px]">币种</TableHead>
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
              <TableCell className="text-right font-mono text-xs">
                {formatQuantity(position.quantity)}
              </TableCell>
              <TableCell className="text-right font-mono text-xs">
                {formatPrice(position.avg_price)}
              </TableCell>
              <TableCell className="text-right font-mono text-xs">
                {position.current_price !== null
                  ? formatPrice(position.current_price)
                  : '-'}
              </TableCell>
              <TableCell className="text-right text-xs text-muted-foreground">
                {position.leverage}x
              </TableCell>
              <TableCell className={`text-right font-mono text-xs font-medium ${getPnlColorClass(position.pnl)}`}>
                {formatPrice(position.pnl)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
})
