/**
 * useInterval Hook - 定时刷新工具
 * 
 * 用于定时执行回调函数
 */

import { useEffect, useRef } from 'react'

/**
 * useInterval Hook
 * 
 * @param callback - 要定时执行的回调函数
 * @param delay - 延迟时间（毫秒），null 表示停止定时器
 * 
 * @example
 * ```typescript
 * useInterval(() => {
 *   console.log('每秒执行一次')
 * }, 1000)
 * ```
 */
export function useInterval(callback: () => void, delay: number | null) {
  const savedCallback = useRef(callback)

  // 记住最新的回调函数
  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  // 设置定时器
  useEffect(() => {
    // 如果 delay 为 null，不启动定时器
    if (delay === null) {
      return
    }

    const id = setInterval(() => {
      savedCallback.current()
    }, delay)

    // 清理定时器
    return () => clearInterval(id)
  }, [delay])
}
