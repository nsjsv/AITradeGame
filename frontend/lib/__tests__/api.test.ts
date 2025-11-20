/**
 * API Client Tests
 * 
 * Tests for the API client request functions and error handling
 */

import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { apiRequest, apiGet, apiPost, apiPut, apiDelete, ApiError, apiClient } from '../api'

// Mock API server
const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('apiRequestWithBase', () => {
  it('should return response body for successful requests (HTTP 200)', async () => {
    server.use(
      http.get('*/api/test', () => {
        return HttpResponse.json({ data: { message: 'success' }, meta: { page: 1 } })
      })
    )

    const result = await apiGet('/api/test')
    expect(result).toEqual({ data: { message: 'success' }, meta: { page: 1 } })
  })

  it('should return null for HTTP 204 responses', async () => {
    server.use(
      http.delete('*/api/test', () => {
        return new HttpResponse(null, { status: 204 })
      })
    )

    const result = await apiDelete('/api/test')
    expect(result).toBeNull()
  })

  it('should throw ApiError for HTTP 4xx errors', async () => {
    server.use(
      http.post('*/api/test', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'INVALID_REQUEST',
              message: 'Missing required fields',
              details: { fields: ['name'] }
            }
          },
          { status: 400 }
        )
      })
    )

    await expect(apiPost('/api/test', {})).rejects.toThrow(ApiError)
    
    try {
      await apiPost('/api/test', {})
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect((error as ApiError).status).toBe(400)
      expect((error as ApiError).data).toEqual({
        error: {
          code: 'INVALID_REQUEST',
          message: 'Missing required fields',
          details: { fields: ['name'] }
        }
      })
    }
  })

  it('should throw ApiError for HTTP 5xx errors', async () => {
    server.use(
      http.get('*/api/test', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'INTERNAL_SERVER_ERROR',
              message: 'Database connection failed'
            }
          },
          { status: 500 }
        )
      })
    )

    await expect(apiGet('/api/test')).rejects.toThrow(ApiError)
    
    try {
      await apiGet('/api/test')
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect((error as ApiError).status).toBe(500)
    }
  })

  it('should throw ApiError for network errors', async () => {
    server.use(
      http.get('*/api/test', () => {
        return HttpResponse.error()
      })
    )

    await expect(apiGet('/api/test')).rejects.toThrow(ApiError)
    
    try {
      await apiGet('/api/test')
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect((error as ApiError).status).toBe(0)
    }
  })
})

describe('extractErrorMessage', () => {
  it('should extract error.message from standard error format', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'MODEL_NOT_FOUND',
              message: '模型不存在',
              details: { id: 123 }
            }
          },
          { status: 404 }
        )
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBe('模型不存在')
  })

  it('should handle legacy error format (error as string)', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json(
          { error: 'Legacy error message' },
          { status: 400 }
        )
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBe('Legacy error message')
  })

  it('should use fallback message when error format is unexpected', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json(
          { unexpected: 'format' },
          { status: 500 }
        )
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBe('HTTP 500')
  })
})

describe('ApiClient.handleRequest', () => {
  it('should extract data field from response envelope', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json({
          data: [
            { 
              id: 1, 
              name: 'Model 1', 
              provider_id: 1, 
              model_name: 'gpt-4', 
              status: 'active',
              created_at: '2024-01-01T00:00:00Z',
              initial_capital: 10000,
              current_balance: 10000,
              total_pnl: 0,
              total_pnl_percentage: 0,
              trading_enabled: true
            }
          ]
        })
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBeUndefined()
    expect(response.data).toEqual([
      { 
        id: 1, 
        name: 'Model 1', 
        provider_id: 1, 
        provider_name: '',
        model_name: 'gpt-4', 
        initial_capital: 10000,
        created_at: '2024-01-01T00:00:00Z'
      }
    ])
  })

  it('should pass through meta field if present', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json({
          data: [],
          meta: { page: 1, total: 0 }
        })
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBeUndefined()
    expect(response.data).toEqual([])
    expect(response.meta).toEqual({ page: 1, total: 0 })
  })

  it('should handle responses without data envelope', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json([
          { 
            id: 1, 
            name: 'Model 1', 
            provider_id: 1, 
            model_name: 'gpt-4', 
            status: 'active',
            created_at: '2024-01-01T00:00:00Z',
            initial_capital: 10000,
            current_balance: 10000,
            total_pnl: 0,
            total_pnl_percentage: 0,
            trading_enabled: true
          }
        ])
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBeUndefined()
    expect(response.data).toEqual([
      { 
        id: 1, 
        name: 'Model 1', 
        provider_id: 1, 
        provider_name: '',
        model_name: 'gpt-4', 
        initial_capital: 10000,
        created_at: '2024-01-01T00:00:00Z'
      }
    ])
  })

  it('should handle error responses correctly', async () => {
    server.use(
      http.post('*/api/models', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'MISSING_FIELDS',
              message: '缺少必填字段',
              details: { fields: ['name', 'provider_id'] }
            }
          },
          { status: 400 }
        )
      })
    )

    const response = await apiClient.createModel({
      name: '',
      provider_id: 0,
      model_name: '',
      trading_enabled: true
    })
    expect(response.data).toBeUndefined()
    expect(response.error).toBe('缺少必填字段')
  })

  it('should handle null data correctly', async () => {
    server.use(
      http.delete('*/api/models/1', () => {
        return new HttpResponse(null, { status: 204 })
      })
    )

    const response = await apiClient.deleteModel(1)
    expect(response.error).toBeUndefined()
    expect(response.data).toBeNull()
  })

  it('should handle empty data array', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json({ data: [] })
      })
    )

    const response = await apiClient.getModels()
    expect(response.error).toBeUndefined()
    expect(response.data).toEqual([])
  })

  it('should preserve meta information when extracting data', async () => {
    server.use(
      http.get('*/api/models/1/trades', () => {
        return HttpResponse.json({
          data: [
            { 
              id: 1, 
              model_id: 1,
              coin: 'BTC',
              signal: 'buy_signal',
              symbol: 'BTC', 
              side: 'buy', 
              quantity: 1, 
              price: 50000,
              leverage: 1,
              fee: 0,
              timestamp: '2024-01-01T00:00:00Z',
              pnl: 0
            }
          ],
          meta: { page: 1, total: 100, limit: 50 }
        })
      })
    )

    const response = await apiClient.getModelTrades(1, 50)
    expect(response.error).toBeUndefined()
    expect(response.data).toHaveLength(1)
    expect(response.meta).toEqual({ page: 1, total: 100, limit: 50 })
  })

  it('should handle validation errors from validator', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.json({
          data: [
            { id: 1, name: 'Model 1' } // Missing required fields
          ]
        })
      })
    )

    const response = await apiClient.getModels()
    expect(response.data).toBeUndefined()
    expect(response.error).toContain('Invalid TradingModel')
  })

  it('should handle network errors gracefully', async () => {
    server.use(
      http.get('*/api/models', () => {
        return HttpResponse.error()
      })
    )

    const response = await apiClient.getModels()
    expect(response.data).toBeUndefined()
    expect(response.error).toBe('Failed to fetch')
  })
})
