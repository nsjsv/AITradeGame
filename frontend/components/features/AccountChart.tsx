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

import React, { useMemo, lazy, Suspense } from 'react'
import { useTheme } from 'next-themes'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatPrice, formatTimestamp } from '@/lib/utils'
import type { AccountValueHistory, ModelChartData } from '@/lib/types'

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

export const AccountChart = React.memo(function AccountChart({ data, type, isLoading }: AccountChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

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

    // 单模型视图
    if (type === 'single') {
      const singleData = data as AccountValueHistory[]
      
      const timestamps = singleData.map((item) => 
        formatTimestamp(item.timestamp, 'datetime')
      )
      const values = singleData.map((item) => item.total_value)

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: tooltipBg,
          borderColor: tooltipBorder,
          borderWidth: 1,
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
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
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
        },
        yAxis: {
          type: 'value',
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
            lineStyle: {
              width: 2,
              color: primaryColor,
            },
            itemStyle: {
              color: primaryColor,
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: isDark ? 'rgba(163, 163, 163, 0.3)' : 'rgba(115, 115, 115, 0.3)',
                  },
                  {
                    offset: 1,
                    color: isDark ? 'rgba(163, 163, 163, 0.05)' : 'rgba(115, 115, 115, 0.05)',
                  },
                ],
              },
            },
          },
        ],
      }
    }

    // 聚合视图
    const aggregatedData = data as ModelChartData[]
    
    // 获取所有时间戳（使用第一个模型的时间戳作为基准）
    const timestamps = aggregatedData[0]?.data.map((item) =>
      formatTimestamp(item.timestamp, 'datetime')
    ) || []

    // 生成每个模型的系列数据
    const series = aggregatedData.map((modelData, index) => ({
      name: modelData.model_name,
      type: 'line',
      data: modelData.data.map((item) => item.total_value),
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
        bottom: '3%',
        top: '15%',
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
      },
      yAxis: {
        type: 'value',
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
      series,
    }
  }, [data, type, isDark])

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
      <CardHeader>
        <CardTitle>账户价值</CardTitle>
      </CardHeader>
      <CardContent>
        <Suspense fallback={
          <div className="h-[400px] flex items-center justify-center">
            <div className="text-sm text-muted-foreground">加载图表中...</div>
          </div>
        }>
          <ReactECharts
            option={chartOption}
            style={{ height: '400px', width: '100%' }}
            opts={{ renderer: 'canvas' }}
            notMerge={true}
            lazyUpdate={true}
          />
        </Suspense>
      </CardContent>
    </Card>
  )
})
