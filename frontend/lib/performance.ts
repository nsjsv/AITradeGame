/**
 * 性能监控工具
 * 
 * 用于监控和报告 Core Web Vitals 指标
 */

import { onCLS, onINP, onLCP, onFCP, onTTFB, type Metric } from 'web-vitals'

/**
 * 性能指标类型
 */
export interface PerformanceMetrics {
  // Core Web Vitals
  CLS?: number  // Cumulative Layout Shift
  INP?: number  // Interaction to Next Paint (替代 FID)
  LCP?: number  // Largest Contentful Paint
  
  // 其他重要指标
  FCP?: number  // First Contentful Paint
  TTFB?: number // Time to First Byte
}

/**
 * 性能指标回调函数类型
 */
type MetricCallback = (metric: Metric) => void

/**
 * 报告性能指标
 */
function reportMetric(metric: Metric) {
  // 在开发环境输出到控制台
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${metric.name}:`, {
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
    })
  }

  // 在生产环境可以发送到分析服务
  // 例如: Google Analytics, Sentry, 自定义分析服务等
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', metric.name, {
      value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      event_category: 'Web Vitals',
      event_label: metric.id,
      non_interaction: true,
    })
  }
}

/**
 * 初始化性能监控
 * 
 * 监控 Core Web Vitals 和其他重要性能指标
 */
export function initPerformanceMonitoring() {
  if (typeof window === 'undefined') {
    return
  }

  try {
    // Core Web Vitals
    onCLS(reportMetric)  // 累积布局偏移
    onINP(reportMetric)  // 交互到下次绘制（替代 FID）
    onLCP(reportMetric)  // 最大内容绘制

    // 其他指标
    onFCP(reportMetric)  // 首次内容绘制
    onTTFB(reportMetric) // 首字节时间
  } catch (error) {
    console.error('[Performance] Failed to initialize monitoring:', error)
  }
}

/**
 * 获取当前性能指标
 */
export function getPerformanceMetrics(): PerformanceMetrics {
  if (typeof window === 'undefined' || !window.performance) {
    return {}
  }

  const metrics: PerformanceMetrics = {}

  try {
    // 获取 Navigation Timing 数据
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    
    if (navigation) {
      // TTFB (Time to First Byte)
      metrics.TTFB = navigation.responseStart - navigation.requestStart

      // FCP (First Contentful Paint)
      const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0]
      if (fcpEntry) {
        metrics.FCP = fcpEntry.startTime
      }
    }

    // LCP (Largest Contentful Paint)
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint')
    if (lcpEntries.length > 0) {
      const lastEntry = lcpEntries[lcpEntries.length - 1] as PerformancePaintTiming
      metrics.LCP = lastEntry.startTime
    }

    // CLS (Cumulative Layout Shift)
    const clsEntries = performance.getEntriesByType('layout-shift')
    if (clsEntries.length > 0) {
      metrics.CLS = clsEntries.reduce((sum, entry: any) => {
        // 只计算非用户输入导致的布局偏移
        if (!entry.hadRecentInput) {
          return sum + entry.value
        }
        return sum
      }, 0)
    }
  } catch (error) {
    console.error('[Performance] Failed to get metrics:', error)
  }

  return metrics
}

/**
 * 性能指标评级
 */
export function getRating(metric: keyof PerformanceMetrics, value: number): 'good' | 'needs-improvement' | 'poor' {
  const thresholds = {
    CLS: { good: 0.1, poor: 0.25 },
    INP: { good: 200, poor: 500 },  // INP 阈值（毫秒）
    LCP: { good: 2500, poor: 4000 },
    FCP: { good: 1800, poor: 3000 },
    TTFB: { good: 800, poor: 1800 },
  }

  const threshold = thresholds[metric]
  if (!threshold) return 'good'

  if (value <= threshold.good) return 'good'
  if (value <= threshold.poor) return 'needs-improvement'
  return 'poor'
}

/**
 * 格式化性能指标值
 */
export function formatMetricValue(metric: keyof PerformanceMetrics, value: number): string {
  if (metric === 'CLS') {
    return value.toFixed(3)
  }
  return `${Math.round(value)}ms`
}

/**
 * 打印性能报告到控制台
 */
export function logPerformanceReport() {
  const metrics = getPerformanceMetrics()
  
  console.group('📊 Performance Report')
  
  Object.entries(metrics).forEach(([key, value]) => {
    if (value !== undefined) {
      const rating = getRating(key as keyof PerformanceMetrics, value)
      const emoji = rating === 'good' ? '✅' : rating === 'needs-improvement' ? '⚠️' : '❌'
      console.log(
        `${emoji} ${key}: ${formatMetricValue(key as keyof PerformanceMetrics, value)} (${rating})`
      )
    }
  })
  
  console.groupEnd()
}

// 类型声明
declare global {
  interface Window {
    gtag?: (...args: any[]) => void
  }
}
