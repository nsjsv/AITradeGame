/**
 * MarketPrices 组件 - 显示市场价格
 * 
 * 功能：
 * - 显示加密货币符号、当前价格和24小时涨跌幅
 * - 使用中文颜色约定（红涨绿跌）
 * - 自动定时刷新
 * - 点击币种查看行情详情弹窗
 */

'use client'

import React, { useMemo, useState, useCallback } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { useMarketPrices } from '@/hooks/useMarketPrices'
import { cn } from '@/lib/utils'
import { MarketHistoryDialog } from './MarketHistoryDialog'

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
  const [selectedCoin, setSelectedCoin] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  const coins = useMemo(() => Object.keys(prices).sort(), [prices])
  const selectedPrice = selectedCoin ? prices[selectedCoin] : undefined

  const handleCoinClick = useCallback((coin: string) => {
    setSelectedCoin(coin)
    setDialogOpen(true)
  }, [])

  const handleDialogOpenChange = useCallback((open: boolean) => {
    setDialogOpen(open)
    if (!open) {
      setSelectedCoin(null)
    }
  }, [])

  if (isLoading && coins.length === 0) {
    return (
      <div className="p-4 text-sm text-muted-foreground">加载中...</div>
    )
  }

  if (error && coins.length === 0) {
    return (
      <div className="p-4 text-sm text-destructive">{error}</div>
    )
  }

  return (
    <>
      <div className="space-y-1">
        {coins.length === 0 ? (
          <div className="p-4 text-sm text-muted-foreground">暂无市场数据</div>
        ) : (
          <div className="space-y-1">
            {coins.map((coin) => {
              const data = prices[coin]
              const isPositive = data.change_24h >= 0

              return (
                <button
                  key={coin}
                  type="button"
                  onClick={() => handleCoinClick(coin)}
                  className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left transition-colors hover:bg-sidebar-accent/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  aria-label={`查看 ${coin} 行情走势`}
                >
                  {/* 币种符号 */}
                  <div className="font-medium text-sm">{coin}</div>

                  {/* 价格和涨跌幅 */}
                  <div className="flex flex-col items-end">
                    {/* 当前价格 */}
                    <div className="text-sm font-medium tabular-nums">
                      ${formatPrice(data.price)}
                    </div>

                    {/* 24小时涨跌幅 - 中文颜色约定：红涨绿跌 */}
                    <div
                      className={cn(
                        'flex items-center gap-1 text-xs',
                        isPositive ? 'text-profit' : 'text-loss'
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
                </button>
              )
            })}
          </div>
        )}
      </div>

      <MarketHistoryDialog
        coin={selectedCoin}
        open={dialogOpen}
        onOpenChange={handleDialogOpenChange}
        marketPrice={selectedPrice}
      />
    </>
  )
})
