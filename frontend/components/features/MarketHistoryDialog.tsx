/**
 * MarketHistoryDialog - 币种行情详情弹窗
 */

'use client'

import React, { lazy, Suspense, useMemo } from 'react'
import { useTheme } from 'next-themes'
import { RefreshCw, X, TrendingUp, TrendingDown, Clock, BarChart3, Calendar } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogClose,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { useMarketHistory } from '@/hooks/useMarketHistory'
import { formatLargeNumber, formatPercent, formatPrice, formatTimestamp } from '@/lib/utils'
import type { MarketPrice } from '@/lib/types'

const ReactECharts = lazy(() => import('echarts-for-react'))

interface MarketHistoryDialogProps {
  coin: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
  marketPrice?: MarketPrice
}

export function MarketHistoryDialog({
  coin,
  open,
  onOpenChange,
  marketPrice,
}: MarketHistoryDialogProps) {
  const { data, isLoading, error, refresh } = useMarketHistory({
    coin,
    enabled: open,
    resolution: 60,
    limit: 120,
  })
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const records = data?.records ?? []

  const metrics = useMemo(() => {
    if (!records.length) {
      return null
    }

    const latest = records[records.length - 1]
    const highs = records.map((item) => item.high ?? item.close)
    const lows = records.map((item) => item.low ?? item.close)
    const totalVolume = records.reduce((sum, item) => sum + (item.volume ?? 0), 0)
    const highest = Math.max(...highs)
    const lowest = Math.min(...lows)

    return {
      latestClose: latest.close,
      latestTimestamp: latest.timestamp,
      highest,
      lowest,
      rangeText: `${formatPrice(lowest)} ~ ${formatPrice(highest)}`,
      totalVolume,
      source: latest.source || marketPrice?.source || '未知',
      startTimestamp: records[0]?.timestamp,
    }
  }, [marketPrice?.source, records])

  const chartOption = useMemo(() => {
    if (!records.length) {
      return null
    }

    const timestamps = records.map((item) =>
      formatTimestamp(item.timestamp, 'datetime')
    )
    const closes = records.map((item) => item.close || item.open)
    const lineColor = isDark ? '#ef4444' : '#b91c1c'
    const areaColor = isDark ? 'rgba(239,68,68,0.08)' : 'rgba(185,28,28,0.08)'
    const axisColor = isDark ? '#a3a3a3' : '#525252'
    const splitLineColor = isDark ? '#262626' : '#e5e5e5'

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: isDark ? 'rgba(23,23,23,0.95)' : 'rgba(255,255,255,0.95)',
        borderColor: splitLineColor,
        borderWidth: 1,
        textStyle: {
          color: isDark ? '#f5f5f5' : '#262626',
        },
        valueFormatter: (value: number) => formatPrice(Number(value)),
      },
      grid: {
        left: 10,
        right: 10,
        top: 20,
        bottom: 10,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: timestamps,
        boundaryGap: false,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: axisColor,
          fontSize: 10,
          margin: 10
        },
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: axisColor,
          fontSize: 10,
          formatter: (value: number) => formatPrice(value, 0, '$').replace('$', ''),
        },
        splitLine: {
          lineStyle: {
            color: splitLineColor,
            type: 'dashed'
          }
        },
      },
      series: [
        {
          type: 'line',
          name: '收盘价',
          data: closes,
          smooth: true,
          showSymbol: false,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            width: 2,
            color: lineColor
          },
          itemStyle: {
            color: lineColor,
            borderWidth: 2,
            borderColor: isDark ? '#191919' : '#ffffff'
          },
          areaStyle: {
            color: areaColor,
          },
        },
      ],
    }
  }, [isDark, records])

  const changeClass =
    (marketPrice?.change_24h ?? 0) >= 0 ? 'text-profit' : 'text-loss'
  const ChangeIcon = (marketPrice?.change_24h ?? 0) >= 0 ? TrendingUp : TrendingDown

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl p-0 gap-0 overflow-hidden bg-background/95 backdrop-blur-sm" showCloseButton={false}>
        {/* Header Section */}
        <div className="px-6 py-5 border-b border-border/40 flex items-start justify-between bg-muted/10">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <DialogTitle className="text-xl font-semibold tracking-tight">
                {coin || '行情走势'}
              </DialogTitle>
              {marketPrice && (
                <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-background border border-border/50 ${changeClass}`}>
                  <ChangeIcon className="size-3" />
                  {formatPercent(marketPrice.change_24h)}
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{metrics?.source || marketPrice?.source || '数据源加载中...'}</span>
              <span>•</span>
              <span>{data ? `每 ${data.resolution} 分钟更新` : '加载中...'}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={refresh}
              disabled={!coin || isLoading}
              className="h-8 text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className={`size-3.5 mr-1.5 ${isLoading ? 'animate-spin' : ''}`} />
              刷新
            </Button>
            <DialogClose asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 rounded-full hover:bg-secondary"
              >
                <X className="size-4" />
              </Button>
            </DialogClose>
          </div>
        </div>

        {error && (
          <div className="m-4 rounded-md border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive flex items-center gap-2">
            <div className="size-1.5 rounded-full bg-destructive" />
            {error}
          </div>
        )}

        {/* Main Content */}
        <div className="p-6 space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-1 p-3 rounded-lg hover:bg-secondary/30 transition-colors">
              <div className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <TrendingUp className="size-3.5" />
                最新收盘
              </div>
              <div className="text-xl font-semibold tracking-tight">
                {metrics ? formatPrice(metrics.latestClose) : '-'}
              </div>
            </div>
            
            <div className="space-y-1 p-3 rounded-lg hover:bg-secondary/30 transition-colors">
              <div className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <BarChart3 className="size-3.5" />
                区间高低
              </div>
              <div className="text-sm font-medium pt-1">
                {metrics ? metrics.rangeText : '-'}
              </div>
            </div>

            <div className="space-y-1 p-3 rounded-lg hover:bg-secondary/30 transition-colors">
              <div className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Activity className="size-3.5" />
                成交量
              </div>
              <div className="text-lg font-medium">
                {metrics ? formatLargeNumber(metrics.totalVolume) : '-'}
              </div>
            </div>

            <div className="space-y-1 p-3 rounded-lg hover:bg-secondary/30 transition-colors">
              <div className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Calendar className="size-3.5" />
                更新时间
              </div>
              <div className="text-sm font-medium pt-1">
                {metrics ? formatTimestamp(metrics.latestTimestamp, 'time') : '-'}
              </div>
            </div>
          </div>

          {/* Chart Section */}
          <div className="rounded-xl border border-border/40 bg-card/50 p-1 shadow-sm">
            {isLoading && (
              <div className="flex h-[300px] items-center justify-center text-sm text-muted-foreground">
                <div className="flex flex-col items-center gap-2">
                  <RefreshCw className="size-5 animate-spin opacity-50" />
                  <span>图表加载中...</span>
                </div>
              </div>
            )}

            {!isLoading && chartOption && (
              <Suspense
                fallback={
                  <div className="flex h-[300px] items-center justify-center text-sm text-muted-foreground">
                    正在渲染图表...
                  </div>
                }
              >
                <ReactECharts
                  option={chartOption}
                  style={{ height: '300px', width: '100%' }}
                  notMerge
                  lazyUpdate
                  theme={isDark ? 'dark' : undefined}
                />
              </Suspense>
            )}

            {!isLoading && !chartOption && (
              <div className="flex h-[300px] items-center justify-center text-sm text-muted-foreground">
                暂无历史数据
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

function Activity(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  )
}
