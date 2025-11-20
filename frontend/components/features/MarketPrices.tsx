/**
 * MarketPrices 组件 - 显示市场价格
 * 
 * 功能：
 * - 显示加密货币符号、当前价格和24小时涨跌幅
 * - 使用中文颜色约定（红涨绿跌）
 * - 自动定时刷新
 */

'use client'

import React, { useMemo } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useMarketPrices } from '@/hooks/useMarketPrices'
import { cn } from '@/lib/utils'

/**
 * 格式化价格
 */
function formatPrice(price: number): string {
  if (price >= 1000) {
    return price.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  } else if (price >= 1) {
    return price.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    })
  } else {
    return price.toLocaleString('zh-CN', {
      minimumFractionDigits: 4,
      maximumFractionDigits: 8,
    })
  }
}

/**
 * 格式化涨跌幅
 */
function formatChange(change: number): string {
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

export const MarketPrices = React.memo(function MarketPrices() {
  const { prices, isLoading, error } = useMarketPrices()

  const coins = useMemo(() => Object.keys(prices).sort(), [prices])

  if (isLoading && coins.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>市场价格</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">加载中...</div>
        </CardContent>
      </Card>
    )
  }

  if (error && coins.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>市场价格</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-destructive">{error}</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>市场价格</CardTitle>
      </CardHeader>
      <CardContent>
        {coins.length === 0 ? (
          <div className="text-sm text-muted-foreground">暂无市场数据</div>
        ) : (
          <div className="space-y-3">
            {coins.map((coin) => {
              const data = prices[coin]
              const isPositive = data.change_24h >= 0

              return (
                <div
                  key={coin}
                  className="flex items-center justify-between py-2 border-b last:border-b-0"
                >
                  {/* 币种符号 */}
                  <div className="flex items-center gap-2">
                    <div className="font-medium text-sm">{coin}</div>
                  </div>

                  {/* 价格和涨跌幅 */}
                  <div className="flex flex-col items-end gap-0.5">
                    {/* 当前价格 */}
                    <div className="font-mono text-sm font-medium">
                      ${formatPrice(data.price)}
                    </div>

                    {/* 24小时涨跌幅 - 中文颜色约定：红涨绿跌 */}
                    <div
                      className={cn(
                        'flex items-center gap-1 text-xs font-medium',
                        isPositive
                          ? 'text-red-600 dark:text-red-500' // 红色表示上涨
                          : 'text-green-600 dark:text-green-500' // 绿色表示下跌
                      )}
                    >
                      {isPositive ? (
                        <TrendingUp className="size-3" />
                      ) : (
                        <TrendingDown className="size-3" />
                      )}
                      <span>{formatChange(data.change_24h)}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
})
