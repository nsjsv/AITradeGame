/**
 * Shared HTTP helpers for API client
 */

import { ValidationError } from './validators'

export const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    if (process.env.NEXT_PUBLIC_BROWSER_API_BASE_URL) {
      return process.env.NEXT_PUBLIC_BROWSER_API_BASE_URL
    }
    if (process.env.NEXT_PUBLIC_API_BASE_URL?.includes('backend')) {
      const url = new URL(process.env.NEXT_PUBLIC_API_BASE_URL)
      return `${window.location.protocol}//${window.location.hostname}${url.port ? `:${url.port}` : ''}`
    }
  }

  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL
  }
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return 'http://localhost:5000'
}

export const getMarketApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_MARKET_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_MARKET_API_BASE_URL
  }
  return getApiBaseUrl()
}

export interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>
}

export interface ApiResponse<T> {
  data?: T
  meta?: Record<string, unknown>
  error?: string
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public data: any,
    message?: string
  ) {
    super(message || `HTTP ${status}`)
    this.name = 'ApiError'
  }
}

export const successResponse = <T>(data: T, meta?: Record<string, unknown>): ApiResponse<T> => ({
  data,
  meta,
})

const extractErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof ValidationError) {
    return error.message
  }
  if (error instanceof ApiError) {
    const data = error.data
    if (data && typeof data === 'object' && 'error' in data) {
      const errorObj = (data as any).error
      if (errorObj && typeof errorObj === 'object' && 'message' in errorObj && typeof errorObj.message === 'string') {
        return errorObj.message
      }
      if (typeof errorObj === 'string') {
        return errorObj
      }
    }
    return error.message || fallback
  }
  if (error instanceof Error) {
    return error.message
  }
  return fallback
}

export const errorResponse = (error: unknown, fallback: string): ApiResponse<never> => {
  const message = extractErrorMessage(error, fallback)
  if (process.env.NODE_ENV === 'development') {
    const shouldWarn = error instanceof ApiError || error instanceof ValidationError
    const logger = shouldWarn ? console.warn : console.error
    logger('[API Client Error]', message, error)
  }
  return { error: message }
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> {
  return apiRequestWithBase(endpoint, config, getApiBaseUrl())
}

export async function apiRequestWithBase<T = unknown>(
  endpoint: string,
  config: RequestConfig = {},
  baseUrl?: string
): Promise<T> {
  const { params, ...fetchConfig } = config
  const resolvedBaseUrl = baseUrl || getApiBaseUrl()

  let url = `${resolvedBaseUrl}${endpoint}`
  if (params) {
    const searchParams = new URLSearchParams(
      Object.entries(params).map(([key, value]) => [key, String(value)])
    )
    url += `?${searchParams.toString()}`
  }

  if (process.env.NODE_ENV === 'development') {
    console.log(`[API] ${config.method || 'GET'} ${url}`)
  }

  try {
    const response = await fetch(url, {
      ...fetchConfig,
      headers: {
        'Content-Type': 'application/json',
        ...fetchConfig.headers,
      },
    })

    if (response.status === 204 || response.status === 205) {
      return null as T
    }

    let data: any
    try {
      data = await response.json()
    } catch {
      data = {}
    }

    if (!response.ok) {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`[API Error] HTTP ${response.status}`, data)
      }
      throw new ApiError(response.status, data)
    }

    return data as T
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    const message = error instanceof Error ? error.message : 'Network request failed'
    throw new ApiError(0, {}, message)
  }
}

export async function apiGet<T = unknown>(
  endpoint: string,
  params?: Record<string, string | number | boolean>,
  baseUrl?: string
): Promise<T> {
  return apiRequestWithBase<T>(endpoint, { method: 'GET', params }, baseUrl)
}

export async function apiPost<T = unknown>(
  endpoint: string,
  body?: any
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function apiPut<T = unknown>(
  endpoint: string,
  body?: any
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

export async function apiDelete<T = unknown>(
  endpoint: string
): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE' })
}
