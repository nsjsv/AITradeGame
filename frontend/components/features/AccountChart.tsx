/**
 * AccountChart 组件 - 显示账户价值图表
 * 
 * 功能：
 * - 集成 ECharts 库
 * - 实现单模型视图的账户价值折线图
 * - 实现聚合视图的多模型对比图
 * - 格式化时间戳为 Asia/Shanghai 时区
 * - 实现交互式工具提示
 */

'use client'

import React, { useMemo, lazy, Suspense, useEffect, useRef } from 'react'
import { useTheme } from 'next-themes'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { formatPrice, formatTimestamp } from '@/lib/utils'
import type { AccountValueHistory, ModelChartData } from '@/lib/types'
import type { ECharts } from 'echarts'

// 懒加载 ECharts 组件
const ReactECharts = lazy(() => import('echarts-for-react'))

interface AccountChartProps {
  data: AccountValueHistory[] | ModelChartData[]
  type: 'single' | 'aggregated'
  isLoading?: boolean
}

/**
 * 生成图表颜色（使用中性灰色系统）
 */
const CHART_COLORS_LIGHT = [
  '#737373', // gray-500
  '#a3a3a3', // gray-400
  '#525252', // gray-600
  '#d4d4d4', // gray-300
  '#404040', // gray-700
  '#e5e5e5', // gray-200
  '#262626', // gray-800
]

const CHART_COLORS_DARK = [
  '#a3a3a3', // gray-400
  '#737373', // gray-500
  '#d4d4d4', // gray-300
  '#525252', // gray-600
  '#e5e5e5', // gray-200
  '#404040', // gray-700
  '#f5f5f5', // gray-100
]

const sortByTimestampAscending = <T extends { timestamp: string }>(items: T[]): T[] =>
  [...items].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )

export const AccountChart = React.memo(function AccountChart({ data, type, isLoading }: AccountChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const chartInstanceRef = useRef<ECharts | null>(null)

  /**
   * 计算最新快照信息（用于图表顶部展示）
   */
  const latestSnapshot = useMemo(() => {
    if (!data || data.length === 0) {
      return null
    }

    if (type === 'single') {
      const singleData = sortByTimestampAscending(data as AccountValueHistory[])
      const latestPoint = singleData[singleData.length - 1]
      if (!latestPoint) {
        return null
      }
      return {
        value: formatPrice(latestPoint.total_value),
        timestamp: formatTimestamp(latestPoint.timestamp, 'datetime'),
      }
    }

    const aggregatedData = (data as ModelChartData[])
      .filter(
        (model): model is ModelChartData & { data: AccountValueHistory[] } =>
          Array.isArray(model.data) && model.data.length > 0
      )
      .map((model) => ({
        ...model,
        data: sortByTimestampAscending(model.data),
      }))

    if (aggregatedData.length === 0) {
      return null
    }

    const lastTimestamps = aggregatedData
      .map((model) => model.data[model.data.length - 1]?.timestamp)
      .filter(Boolean) as string[]
    const latestTimestamp = lastTimestamps[lastTimestamps.length - 1]

    const latestTotal = aggregatedData.reduce((sum, model) => {
      const latestPoint = model.data[model.data.length - 1]
      if (!latestPoint) {
        return sum
      }
      return sum + latestPoint.total_value
    }, 0)

    if (!latestTimestamp) {
      return null
    }

    return {
      value: formatPrice(latestTotal),
      timestamp: formatTimestamp(latestTimestamp, 'datetime'),
    }
  }, [data, type])

  /**
   * 生成 ECharts 配置
   */
  const chartOption = useMemo(() => {
    if (!data || data.length === 0) {
      return null
    }

    const CHART_COLORS = isDark ? CHART_COLORS_DARK : CHART_COLORS_LIGHT
    const tooltipBg = isDark ? 'rgba(23, 23, 23, 0.95)' : 'rgba(255, 255, 255, 0.95)'
    const tooltipBorder = isDark ? '#404040' : '#e5e5e5'
    const tooltipText = isDark ? '#f5f5f5' : '#262626'
    const axisLineColor = isDark ? '#404040' : '#d4d4d4'
    const axisLabelColor = isDark ? '#a3a3a3' : '#737373'
    const splitLineColor = isDark ? '#262626' : '#e5e5e5'
    const primaryColor = isDark ? '#a3a3a3' : '#737373'
    const blurArea = isDark ? 'rgba(216, 215, 213, 0.08)' : 'rgba(0, 0, 0, 0.04)'
    const animationProps = {
      animationDuration: 480,
      animationDurationUpdate: 320,
      animationEasing: 'cubicOut',
      animationEasingUpdate: 'cubicOut',
    }

    // 单模型视图
    if (type === 'single') {
      const singleData = sortByTimestampAscending(data as AccountValueHistory[])
      
      const timestamps = singleData.map((item) => 
        formatTimestamp(item.timestamp, 'datetime')
      )
      const values = singleData.map((item) => item.total_value)

      const latestCoordinate = [
        timestamps[timestamps.length - 1],
        values[values.length - 1],
      ]
      const hasLatestPoint =
        latestCoordinate[0] !== undefined && latestCoordinate[1] !== undefined

      return {
        ...animationProps,
        tooltip: {
          trigger: 'axis',
          backgroundColor: tooltipBg,
          borderColor: tooltipBorder,
          borderWidth: 1,
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: tooltipBg,
              color: tooltipText,
            },
          },
          textStyle: {
            color: tooltipText,
          },
          formatter: (params: any) => {
            const param = params[0]
            return `
              <div style="padding: 4px 8px;">
                <div style="font-weight: 600; margin-bottom: 4px;">${param.name}</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${param.color};"></span>
                  <span>账户总值: ${formatPrice(param.value)}</span>
                </div>
              </div>
            `
          },
        },
        dataZoom: [
          {
            type: 'inside',
            zoomOnMouseWheel: true,
            moveOnMouseMove: true,
            moveOnMouseWheel: true,
          },
          {
            type: 'slider',
            show: true,
            height: 8,
            right: 10,
            bottom: 6,
            brushSelect: false,
            borderColor: 'transparent',
            handleSize: 14,
            handleStyle: {
              color: primaryColor,
            },
            labelFormatter: '',
          },
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '10%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: timestamps,
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: axisLineColor,
            },
          },
          axisLabel: {
            color: axisLabelColor,
            fontSize: 11,
          },
          axisPointer: {
            show: true,
            lineStyle: {
              color: axisLineColor,
              width: 1,
            },
          },
        },
        yAxis: {
          type: 'value',
          scale: true,
          axisLine: {
            show: false,
          },
          axisTick: {
            show: false,
          },
          axisLabel: {
            color: axisLabelColor,
            fontSize: 11,
            formatter: (value: number) => formatPrice(value, 0, '$'),
          },
          splitLine: {
            lineStyle: {
              color: splitLineColor,
              type: 'dashed',
            },
          },
        },
        series: [
          {
            name: '账户总值',
            type: 'line',
            data: values,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            showSymbol: false,
            lineStyle: {
              width: 3,
              color: primaryColor,
            },
            itemStyle: {
              color: primaryColor,
            },
            areaStyle: {
              color: blurArea,
            },
            emphasis: {
              focus: 'series',
              lineStyle: { width: 4 },
            },
            universalTransition: true,
            markPoint: hasLatestPoint
              ? {
                symbol: 'circle',
                symbolSize: 12,
                data: [
                {
                  coord: latestCoordinate,
                  value: latestCoordinate[1],
                  label: {
                    formatter: (param: any) => formatPrice(param.value),
                    color: tooltipText,
                    fontWeight: 600,
                    backgroundColor: tooltipBg,
                    borderColor: tooltipBorder,
                    borderWidth: 1,
                    borderRadius: 999,
                    padding: [4, 8],
                  },
                },
              ],
              animationDuration: 200,
            }
              : undefined,
          },
        ],
      }
    }

    // 聚合视图
    const aggregatedData = (data as ModelChartData[])
      .filter(
        (item): item is ModelChartData & { data: AccountValueHistory[] } =>
          Array.isArray(item.data) && item.data.length > 0
      )
      .map((item) => ({
        ...item,
        data: sortByTimestampAscending(item.data),
      }))

    if (aggregatedData.length === 0) {
      return null
    }
    
    const getTotalValue = (entry: AccountValueHistory | { value?: number }) => {
      if ('total_value' in entry) {
        return entry.total_value
      }
      return entry.value ?? 0
    }

    // 获取所有时间戳（使用第一个模型的时间戳作为基准）
    const timestamps = aggregatedData[0].data.map((item) =>
      formatTimestamp(item.timestamp, 'datetime')
    )

    // 生成每个模型的系列数据
    const series = aggregatedData.map((modelData, index) => ({
      name: modelData.model_name,
      type: 'line',
      data: modelData.data.map((item) => getTotalValue(item)),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2,
        color: CHART_COLORS[index % CHART_COLORS.length],
      },
      itemStyle: {
        color: CHART_COLORS[index % CHART_COLORS.length],
      },
    }))

    return {
      ...animationProps,
      tooltip: {
        trigger: 'axis',
        backgroundColor: tooltipBg,
        borderColor: tooltipBorder,
        borderWidth: 1,
        textStyle: {
          color: tooltipText,
        },
        formatter: (params: any) => {
          let result = `<div style="padding: 4px 8px;">
            <div style="font-weight: 600; margin-bottom: 8px;">${params[0].name}</div>`
          
          params.forEach((param: any) => {
            result += `
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${param.color};"></span>
                <span>${param.seriesName}: ${formatPrice(param.value)}</span>
              </div>
            `
          })
          
          result += '</div>'
          return result
        },
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: tooltipBg,
            color: tooltipText,
          },
        },
      },
      legend: {
        data: aggregatedData.map((item) => item.model_name),
        top: 0,
        textStyle: {
          color: axisLabelColor,
          fontSize: 12,
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '15%',
        containLabel: true,
      },
      dataZoom: [
        {
          type: 'inside',
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: true,
        },
        {
          type: 'slider',
          show: true,
          height: 8,
          right: 10,
          bottom: 6,
          brushSelect: false,
          borderColor: 'transparent',
          handleSize: 14,
          handleStyle: {
            color: axisLabelColor,
          },
          labelFormatter: '',
        },
      ],
      xAxis: {
        type: 'category',
        data: timestamps,
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: axisLineColor,
          },
        },
        axisLabel: {
          color: axisLabelColor,
          fontSize: 11,
        },
      },
      yAxis: {
        type: 'value',
        scale: true,
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        axisLabel: {
          color: axisLabelColor,
          fontSize: 11,
          formatter: (value: number) => formatPrice(value, 0, '$'),
        },
        splitLine: {
          lineStyle: {
            color: splitLineColor,
            type: 'dashed',
          },
        },
      },
      series: series.map((item, index) => ({
        ...item,
        showSymbol: false,
        areaStyle: {
          color: isDark ? 'rgba(216, 215, 213, 0.04)' : 'rgba(0, 0, 0, 0.02)',
        },
        emphasis: {
          focus: 'series',
        },
        universalTransition: true,
        lineStyle: {
          ...item.lineStyle,
          width: 2.5,
        },
        animationDuration: 420 + index * 20,
      })),
    }
  }, [data, type, isDark])

  useEffect(() => {
    if (chartOption && chartInstanceRef.current) {
      chartInstanceRef.current.setOption(chartOption, false, true)
    }
  }, [chartOption])

  // 加载状态
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>账户价值</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <div className="text-sm text-muted-foreground">加载中...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // 无数据状态
  if (!chartOption) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>账户价值</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <div className="text-sm text-muted-foreground">
              {type === 'single' ? '暂无账户数据' : '暂无模型数据'}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <CardTitle>账户价值</CardTitle>
        {latestSnapshot && (
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <span className="font-medium text-foreground">
              最新：{latestSnapshot.value}
            </span>
            <span className="text-xs text-muted-foreground">
              更新时间：{latestSnapshot.timestamp}
            </span>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <Suspense fallback={
          <div className="h-[400px] flex items-center justify-center">
            <div className="text-sm text-muted-foreground">加载图表中...</div>
          </div>
        }>
          <ReactECharts
            option={chartOption ?? undefined}
            style={{ height: '400px', width: '100%' }}
            opts={{ renderer: 'canvas' }}
            notMerge={false}
            lazyUpdate={true}
            onChartReady={(instance) => {
              chartInstanceRef.current = instance
              if (chartOption) {
                instance.setOption(chartOption, false, true)
              }
            }}
          />
        </Suspense>
      </CardContent>
    </Card>
  )
})
