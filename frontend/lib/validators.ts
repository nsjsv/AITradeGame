/**
 * Runtime Type Validators
 * 
 * Provides runtime type validation for API responses to ensure type safety
 */

import type {
  TradingModel,
  PortfolioResponse,
  AccountValueHistory,
  Trade,
  Conversation,
  MarketPrices,
  MarketPrice,
  ApiProvider,
  SystemSettings,
  FrontendConfig,
  VersionInfo,
  UpdateInfo,
  AggregatedPortfolio,
  ModelChartData,
} from './types'

/**
 * Validation error class
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public expected?: string,
    public received?: any
  ) {
    super(message)
    this.name = 'ValidationError'
  }
}

/**
 * Type guard utilities
 */
const isString = (value: unknown): value is string => typeof value === 'string'
const isNumber = (value: unknown): value is number => typeof value === 'number' && !isNaN(value)
const isBoolean = (value: unknown): value is boolean => typeof value === 'boolean'
const isArray = (value: unknown): value is unknown[] => Array.isArray(value)
const isObject = (value: unknown): value is Record<string, unknown> => 
  typeof value === 'object' && value !== null && !Array.isArray(value)

/**
 * Validate required field
 */
function validateRequired<T>(
  obj: Record<string, unknown>,
  field: string,
  validator: (value: unknown) => value is T,
  typeName: string
): T {
  if (!(field in obj)) {
    throw new ValidationError(
      `Missing required field: ${field}`,
      field,
      typeName,
      undefined
    )
  }
  
  const value = obj[field]
  if (!validator(value)) {
    throw new ValidationError(
      `Invalid type for field: ${field}`,
      field,
      typeName,
      typeof value
    )
  }
  
  return value
}

/**
 * Validate optional field
 */
function validateOptional<T>(
  obj: Record<string, unknown>,
  field: string,
  validator: (value: unknown) => value is T,
  defaultValue: T
): T {
  if (!(field in obj) || obj[field] === null || obj[field] === undefined) {
    return defaultValue
  }
  
  const value = obj[field]
  if (!validator(value)) {
    return defaultValue
  }
  
  return value
}

/**
 * Validate TradingModel
 */
export function validateTradingModel(data: unknown): TradingModel {
  if (!isObject(data)) {
    throw new ValidationError('TradingModel must be an object', undefined, 'object', typeof data)
  }
  
  return {
    id: validateRequired(data, 'id', isNumber, 'number'),
    name: validateRequired(data, 'name', isString, 'string'),
    provider_id: validateRequired(data, 'provider_id', isNumber, 'number'),
    provider_name: validateOptional(data, 'provider_name', isString, ''),
    model_name: validateRequired(data, 'model_name', isString, 'string'),
    initial_capital: validateRequired(data, 'initial_capital', isNumber, 'number'),
    created_at: validateRequired(data, 'created_at', isString, 'string'),
  }
}

/**
 * Validate array of TradingModels
 */
export function validateTradingModels(data: unknown): TradingModel[] {
  if (!isArray(data)) {
    throw new ValidationError('Expected array of TradingModels', undefined, 'array', typeof data)
  }
  
  return data.map((item, index) => {
    try {
      return validateTradingModel(item)
    } catch (error) {
      if (error instanceof ValidationError) {
        throw new ValidationError(
          `Invalid TradingModel at index ${index}: ${error.message}`,
          `[${index}].${error.field}`,
          error.expected,
          error.received
        )
      }
      throw error
    }
  })
}

/**
 * Validate PortfolioResponse
 */
export function validatePortfolioResponse(data: unknown): PortfolioResponse {
  if (!isObject(data)) {
    throw new ValidationError('PortfolioResponse must be an object', undefined, 'object', typeof data)
  }

  const portfolioData = validateRequired(data, 'portfolio', isObject, 'object')
  const positionsData = validateRequired(portfolioData, 'positions', isArray, 'array')
  const historyData = validateRequired(data, 'account_value_history', isArray, 'array')

  const positions = positionsData.map((pos, index) => {
    if (!isObject(pos)) {
      throw new ValidationError(
        `Position at index ${index} must be an object`,
        `portfolio.positions[${index}]`,
        'object',
        typeof pos
      )
    }

    return {
      coin: validateRequired(pos, 'coin', isString, 'string'),
      quantity: validateRequired(pos, 'quantity', isNumber, 'number'),
      avg_price: validateRequired(pos, 'avg_price', isNumber, 'number'),
      leverage: validateRequired(pos, 'leverage', isNumber, 'number'),
      side: validateRequired(pos, 'side', isString, 'string'),
      current_price: validateOptional(pos, 'current_price', isNumber, 0),
      pnl: validateOptional(pos, 'pnl', isNumber, 0),
    }
  })

  let netPositions: Record<string, { long: number; short: number }> = {}
  if ('net_positions' in portfolioData) {
    const rawNet = portfolioData['net_positions']
    if (!isObject(rawNet)) {
      throw new ValidationError(
        'net_positions must be an object',
        'portfolio.net_positions',
        'object',
        typeof rawNet
      )
    }

    netPositions = Object.entries(rawNet).reduce((acc, [coin, breakdown]) => {
      if (!isObject(breakdown)) {
        throw new ValidationError(
          `Net position for ${coin} must be an object`,
          `portfolio.net_positions.${coin}`,
          'object',
          typeof breakdown
        )
      }

      const breakdownObj = breakdown as Record<string, unknown>
      acc[coin] = {
        long: validateRequired(breakdownObj, 'long', isNumber, 'number'),
        short: validateRequired(breakdownObj, 'short', isNumber, 'number'),
      }
      return acc
    }, {} as Record<string, { long: number; short: number }>)
  }

  const accountValueHistory: AccountValueHistory[] = historyData.map((entry, index) => {
    if (!isObject(entry)) {
      throw new ValidationError(
        `Account value history at index ${index} must be an object`,
        `account_value_history[${index}]`,
        'object',
        typeof entry
      )
    }

    const entryObj = entry as Record<string, unknown>
    const historyEntry: AccountValueHistory = {
      timestamp: validateRequired(entryObj, 'timestamp', isString, 'string'),
      total_value: validateRequired(entryObj, 'total_value', isNumber, 'number'),
    }

    const cashValue = entryObj['cash']
    if (isNumber(cashValue)) {
      historyEntry.cash = cashValue
    }

    const positionsValue = entryObj['positions_value']
    if (isNumber(positionsValue)) {
      historyEntry.positions_value = positionsValue
    }

    const modelIdValue = entryObj['model_id']
    if (isNumber(modelIdValue)) {
      historyEntry.model_id = modelIdValue
    }

    return historyEntry
  })

  const initialCapital = portfolioData['initial_capital']

  return {
    portfolio: {
      model_id: validateRequired(portfolioData, 'model_id', isNumber, 'number'),
      cash: validateRequired(portfolioData, 'cash', isNumber, 'number'),
      positions,
      positions_value: validateRequired(portfolioData, 'positions_value', isNumber, 'number'),
      margin_used: validateRequired(portfolioData, 'margin_used', isNumber, 'number'),
      total_value: validateRequired(portfolioData, 'total_value', isNumber, 'number'),
      realized_pnl: validateRequired(portfolioData, 'realized_pnl', isNumber, 'number'),
      unrealized_pnl: validateRequired(portfolioData, 'unrealized_pnl', isNumber, 'number'),
      total_fees: validateOptional(portfolioData, 'total_fees', isNumber, 0),
      net_positions: netPositions,
      ...(isNumber(initialCapital) ? { initial_capital: initialCapital } : {}),
    },
    account_value_history: accountValueHistory,
  }
}

/**
 * Validate Trade
 */
export function validateTrade(data: unknown): Trade {
  if (!isObject(data)) {
    throw new ValidationError('Trade must be an object', undefined, 'object', typeof data)
  }
  
  return {
    id: validateRequired(data, 'id', isNumber, 'number'),
    model_id: validateRequired(data, 'model_id', isNumber, 'number'),
    coin: validateRequired(data, 'coin', isString, 'string'),
    signal: validateRequired(data, 'signal', isString, 'string'),
    quantity: validateRequired(data, 'quantity', isNumber, 'number'),
    price: validateRequired(data, 'price', isNumber, 'number'),
    leverage: validateRequired(data, 'leverage', isNumber, 'number'),
    side: validateRequired(data, 'side', isString, 'string'),
    pnl: validateRequired(data, 'pnl', isNumber, 'number'),
    fee: validateRequired(data, 'fee', isNumber, 'number'),
    timestamp: validateRequired(data, 'timestamp', isString, 'string'),
  }
}

/**
 * Validate array of Trades
 */
export function validateTrades(data: unknown): Trade[] {
  if (!isArray(data)) {
    throw new ValidationError('Expected array of Trades', undefined, 'array', typeof data)
  }
  
  return data.map((item, index) => {
    try {
      return validateTrade(item)
    } catch (error) {
      if (error instanceof ValidationError) {
        throw new ValidationError(
          `Invalid Trade at index ${index}: ${error.message}`,
          `[${index}].${error.field}`,
          error.expected,
          error.received
        )
      }
      throw error
    }
  })
}

/**
 * Validate ApiProvider
 */
export function validateApiProvider(data: unknown): ApiProvider {
  if (!isObject(data)) {
    throw new ValidationError('ApiProvider must be an object', undefined, 'object', typeof data)
  }
  
  return {
    id: validateRequired(data, 'id', isNumber, 'number'),
    name: validateRequired(data, 'name', isString, 'string'),
    api_url: validateRequired(data, 'api_url', isString, 'string'),
    api_key: validateRequired(data, 'api_key', isString, 'string'),
    models: validateOptional(data, 'models', isString, ''),
    created_at: validateRequired(data, 'created_at', isString, 'string'),
  }
}

/**
 * Validate array of ApiProviders
 */
export function validateApiProviders(data: unknown): ApiProvider[] {
  if (!isArray(data)) {
    throw new ValidationError('Expected array of ApiProviders', undefined, 'array', typeof data)
  }
  
  return data.map((item, index) => {
    try {
      return validateApiProvider(item)
    } catch (error) {
      if (error instanceof ValidationError) {
        throw new ValidationError(
          `Invalid ApiProvider at index ${index}: ${error.message}`,
          `[${index}].${error.field}`,
          error.expected,
          error.received
        )
      }
      throw error
    }
  })
}

/**
 * Validate SystemSettings
 */
export function validateSystemSettings(data: unknown): SystemSettings {
  if (!isObject(data)) {
    throw new ValidationError('SystemSettings must be an object', undefined, 'object', typeof data)
  }
  
  return {
    trading_frequency_minutes: validateRequired(data, 'trading_frequency_minutes', isNumber, 'number'),
    trading_fee_rate: validateRequired(data, 'trading_fee_rate', isNumber, 'number'),
    market_refresh_interval: validateRequired(data, 'market_refresh_interval', isNumber, 'number'),
    portfolio_refresh_interval: validateRequired(data, 'portfolio_refresh_interval', isNumber, 'number'),
  }
}

/**
 * Validate MarketPrices
 */
export function validateMarketPrices(data: unknown): MarketPrices {
  if (!isObject(data)) {
    throw new ValidationError('MarketPrices must be an object', undefined, 'object', typeof data)
  }
  
  // Validate that all values are objects with price and change_24h
  const validated: MarketPrices = {}
  
  for (const [coin, priceData] of Object.entries(data)) {
    if (!isObject(priceData)) {
      throw new ValidationError(
        `Price data for ${coin} must be an object`,
        coin,
        'object',
        typeof priceData
      )
    }
    
    const entry: MarketPrice = {
      price: validateRequired(priceData, 'price', isNumber, 'number'),
      change_24h: validateRequired(priceData, 'change_24h', isNumber, 'number'),
    }

    if ('volume' in priceData && typeof priceData.volume === 'number') {
      entry.volume = priceData.volume
    }
    if ('source' in priceData && typeof priceData.source === 'string') {
      entry.source = priceData.source
    }
    if ('timestamp' in priceData && typeof priceData.timestamp === 'number') {
      entry.timestamp = priceData.timestamp
    }
    
    validated[coin] = entry
  }
  
  return validated
}

/**
 * Generic validator wrapper for API responses
 */
export function validateApiResponse<T>(
  data: unknown,
  validator: (data: unknown) => T,
  context?: string
): T {
  try {
    return validator(data)
  } catch (error) {
    if (error instanceof ValidationError) {
      const contextMsg = context ? ` in ${context}` : ''
      console.error(
        `[Validation Error${contextMsg}] ${error.message}`,
        {
          field: error.field,
          expected: error.expected,
          received: error.received,
          data
        }
      )
    }
    throw error
  }
}
