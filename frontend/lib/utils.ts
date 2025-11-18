/**
 * 工具函数库
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

// ============================================================================
// 样式工具
// ============================================================================

/**
 * 合并 Tailwind CSS 类名
 * 用于组件样式组合，避免类名冲突
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ============================================================================
// 数字格式化
// ============================================================================

/**
 * 格式化价格
 * @param value - 价格数值
 * @param decimals - 小数位数，默认 2
 * @param prefix - 前缀符号，默认 '$'
 */
export function formatPrice(
  value: number | null | undefined,
  decimals: number = 2,
  prefix: string = '$'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return `${prefix}0.00`
  }
  return `${prefix}${value.toFixed(decimals)}`
}

/**
 * 格式化百分比
 * @param value - 数值
 * @param decimals - 小数位数，默认 2
 * @param showSign - 是否显示正负号，默认 true
 */
export function formatPercent(
  value: number | null | undefined,
  decimals: number = 2,
  showSign: boolean = true
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.00%'
  }
  const sign = showSign && value > 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

/**
 * 格式化数量
 * @param value - 数量数值
 * @param decimals - 小数位数，默认 4
 */
export function formatQuantity(
  value: number | null | undefined,
  decimals: number = 4
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.0000'
  }
  return value.toFixed(decimals)
}

/**
 * 格式化大数字（使用 K, M, B 等单位）
 * @param value - 数值
 * @param decimals - 小数位数，默认 2
 */
export function formatLargeNumber(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '0'
  }

  const absValue = Math.abs(value)
  const sign = value < 0 ? '-' : ''

  if (absValue >= 1e9) {
    return `${sign}${(absValue / 1e9).toFixed(decimals)}B`
  }
  if (absValue >= 1e6) {
    return `${sign}${(absValue / 1e6).toFixed(decimals)}M`
  }
  if (absValue >= 1e3) {
    return `${sign}${(absValue / 1e3).toFixed(decimals)}K`
  }
  return `${sign}${absValue.toFixed(decimals)}`
}

// ============================================================================
// 颜色工具（中文约定：红涨绿跌）
// ============================================================================

/**
 * 获取盈亏颜色类名（中文约定：红色表示盈利，绿色表示亏损）
 * @param value - 盈亏数值
 * @param neutral - 零值时的颜色，默认 'text-gray-500'
 */
export function getPnlColorClass(
  value: number | null | undefined,
  neutral: string = 'text-gray-500'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return neutral
  }
  if (value > 0) {
    return 'text-profit' // 红色表示盈利
  }
  if (value < 0) {
    return 'text-loss' // 绿色表示亏损
  }
  return neutral
}

/**
 * 获取变化颜色类名（中文约定：红色表示上涨，绿色表示下跌）
 * @param value - 变化数值
 * @param neutral - 零值时的颜色，默认 'text-gray-500'
 */
export function getChangeColorClass(
  value: number | null | undefined,
  neutral: string = 'text-gray-500'
): string {
  return getPnlColorClass(value, neutral)
}

/**
 * 获取盈亏背景颜色类名
 * @param value - 盈亏数值
 * @param neutral - 零值时的颜色，默认 'bg-gray-100 dark:bg-gray-800'
 */
export function getPnlBgColorClass(
  value: number | null | undefined,
  neutral: string = 'bg-gray-100 dark:bg-gray-800'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return neutral
  }
  if (value > 0) {
    return 'bg-profit/10 dark:bg-profit/20' // 红色背景表示盈利
  }
  if (value < 0) {
    return 'bg-loss/10 dark:bg-loss/20' // 绿色背景表示亏损
  }
  return neutral
}

// ============================================================================
// 时间格式化
// ============================================================================

/**
 * 格式化时间戳为本地时间字符串（Asia/Shanghai 时区）
 * @param timestamp - ISO 时间戳字符串
 * @param format - 格式类型：'full' | 'date' | 'time' | 'datetime'
 */
export function formatTimestamp(
  timestamp: string | null | undefined,
  format: 'full' | 'date' | 'time' | 'datetime' = 'datetime'
): string {
  if (!timestamp) {
    return '-'
  }

  const normalizeCandidates = (value: string): string[] => {
    const trimmed = value.trim()
    const candidates = new Set<string>()
    const timezonePattern = /([+-]\d{2}:?\d{2})$/i

    const maybeVariants = [trimmed]
    if (!trimmed.includes('T') && trimmed.includes(' ')) {
      maybeVariants.push(trimmed.replace(' ', 'T'))
    }

    for (const variant of maybeVariants) {
      candidates.add(variant)
      const hasTimezoneOffset =
        timezonePattern.test(variant) || /z$/i.test(variant)
      if (!hasTimezoneOffset) {
        candidates.add(`${variant}Z`)
      } else {
        candidates.add(variant)
      }
    }

    return Array.from(candidates)
  }

  const parseTimestampString = (value: string): Date | null => {
    const variants = normalizeCandidates(value)
    for (const variant of variants) {
      const date = new Date(variant)
      if (!Number.isNaN(date.getTime())) {
        return date
      }
    }
    return null
  }

  try {
    const date = parseTimestampString(timestamp)
    if (!date) {
      return timestamp
    }
    const options: Intl.DateTimeFormatOptions = {
      timeZone: 'Asia/Shanghai',
    }

    switch (format) {
      case 'full':
        options.year = 'numeric'
        options.month = '2-digit'
        options.day = '2-digit'
        options.hour = '2-digit'
        options.minute = '2-digit'
        options.second = '2-digit'
        options.hour12 = false
        break
      case 'date':
        options.year = 'numeric'
        options.month = '2-digit'
        options.day = '2-digit'
        break
      case 'time':
        options.hour = '2-digit'
        options.minute = '2-digit'
        options.second = '2-digit'
        options.hour12 = false
        break
      case 'datetime':
      default:
        options.year = 'numeric'
        options.month = '2-digit'
        options.day = '2-digit'
        options.hour = '2-digit'
        options.minute = '2-digit'
        options.hour12 = false
        break
    }

    return new Intl.DateTimeFormat('zh-CN', options).format(date)
  } catch (error) {
    console.error('Failed to format timestamp:', error)
    return timestamp
  }
}

/**
 * 格式化相对时间（例如：2小时前）
 * @param timestamp - ISO 时间戳字符串
 */
export function formatRelativeTime(
  timestamp: string | null | undefined
): string {
  if (!timestamp) {
    return '-'
  }

  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)

    if (diffSec < 60) {
      return '刚刚'
    }
    if (diffMin < 60) {
      return `${diffMin}分钟前`
    }
    if (diffHour < 24) {
      return `${diffHour}小时前`
    }
    if (diffDay < 7) {
      return `${diffDay}天前`
    }
    return formatTimestamp(timestamp, 'date')
  } catch (error) {
    console.error('Failed to format relative time:', error)
    return timestamp
  }
}

// ============================================================================
// 数据验证
// ============================================================================

/**
 * 验证是否为有效数字
 */
export function isValidNumber(value: any): value is number {
  return typeof value === 'number' && !isNaN(value) && isFinite(value)
}

/**
 * 验证是否为正数
 */
export function isPositiveNumber(value: any): boolean {
  return isValidNumber(value) && value > 0
}

/**
 * 验证是否为非负数
 */
export function isNonNegativeNumber(value: any): boolean {
  return isValidNumber(value) && value >= 0
}

// ============================================================================
// 字符串工具
// ============================================================================

/**
 * 截断字符串
 * @param str - 字符串
 * @param maxLength - 最大长度
 * @param suffix - 后缀，默认 '...'
 */
export function truncate(
  str: string | null | undefined,
  maxLength: number,
  suffix: string = '...'
): string {
  if (!str) {
    return ''
  }
  if (str.length <= maxLength) {
    return str
  }
  return str.slice(0, maxLength - suffix.length) + suffix
}

/**
 * 首字母大写
 */
export function capitalize(str: string | null | undefined): string {
  if (!str) {
    return ''
  }
  return str.charAt(0).toUpperCase() + str.slice(1)
}

// ============================================================================
// 数组工具
// ============================================================================

/**
 * 安全地获取数组的最后一个元素
 */
export function last<T>(arr: T[] | null | undefined): T | undefined {
  if (!arr || arr.length === 0) {
    return undefined
  }
  return arr[arr.length - 1]
}

/**
 * 安全地获取数组的第一个元素
 */
export function first<T>(arr: T[] | null | undefined): T | undefined {
  if (!arr || arr.length === 0) {
    return undefined
  }
  return arr[0]
}

// ============================================================================
// 延迟工具
// ============================================================================

/**
 * 延迟执行（用于异步操作）
 * @param ms - 延迟毫秒数
 */
export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// ============================================================================
// 防抖和节流
// ============================================================================

/**
 * 防抖函数
 * @param fn - 要防抖的函数
 * @param wait - 等待时间（毫秒）
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function (this: any, ...args: Parameters<T>) {
    const context = this

    if (timeout) {
      clearTimeout(timeout)
    }

    timeout = setTimeout(() => {
      fn.apply(context, args)
    }, wait)
  }
}

/**
 * 节流函数
 * @param fn - 要节流的函数
 * @param wait - 等待时间（毫秒）
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  wait: number
): (...args: Parameters<T>) => void {
  let lastTime = 0

  return function (this: any, ...args: Parameters<T>) {
    const context = this
    const now = Date.now()

    if (now - lastTime >= wait) {
      lastTime = now
      fn.apply(context, args)
    }
  }
}

// ============================================================================
// 别名函数（为了兼容性）
// ============================================================================

/**
 * formatPercentage - formatPercent 的别名
 * @param value - 数值
 * @param decimals - 小数位数，默认 2
 * @param showSign - 是否显示正负号，默认 true
 */
export const formatPercentage = formatPercent
