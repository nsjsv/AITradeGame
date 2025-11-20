"""
Market data module - Binance API integration
"""
import heapq
import requests
import time
import logging
import threading
from typing import Dict, List, Optional

from backend.config.constants import (
    BINANCE_BASE_URL,
    COINGECKO_BASE_URL,
    MARKET_DATA_CACHE_TTL,
    ERROR_MSG_API_REQUEST_FAILED,
)
from backend.utils.exceptions import MarketDataException


class MarketDataFetcher:
    """Fetch real-time market data from Binance API"""
    
    def __init__(self, api_url: str = None, cache_duration: int = MARKET_DATA_CACHE_TTL):
        """Initialize market data fetcher
        
        Args:
            api_url: CoinGecko API base URL (optional)
            cache_duration: Cache duration in seconds (default: from constants)
        """
        self.binance_base_url = BINANCE_BASE_URL
        self.coingecko_base_url = api_url or COINGECKO_BASE_URL
        self._logger = logging.getLogger(__name__)
        
        # Binance symbol mapping
        self.binance_symbols = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'SOL': 'SOLUSDT',
            'BNB': 'BNBUSDT',
            'XRP': 'XRPUSDT',
            'DOGE': 'DOGEUSDT'
        }
        
        # CoinGecko mapping for technical indicators
        self.coingecko_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'BNB': 'binancecoin',
            'XRP': 'ripple',
            'DOGE': 'dogecoin'
        }
        
        self._cache: Dict[str, Dict] = {}
        self._cache_expiry: Dict[str, float] = {}
        self._expiry_heap: List[tuple[float, str]] = []
        self._cache_duration = cache_duration  # Configurable cache duration
        self._max_cache_entries = 32  # Prevent unbounded cache growth
        self._lock = threading.Lock()

    def _evict_cache_key(self, key: str) -> None:
        """Remove a cache entry safely."""
        self._cache.pop(key, None)
        self._cache_expiry.pop(key, None)

    def _evict_expired_entries(self, now: Optional[float] = None) -> None:
        """Remove expired entries and enforce cache size limits."""
        if not self._expiry_heap:
            return
        current = now or time.time()
        while self._expiry_heap and self._expiry_heap[0][0] <= current:
            _, key = heapq.heappop(self._expiry_heap)
            expiry = self._cache_expiry.get(key)
            if expiry is None or expiry <= current:
                self._evict_cache_key(key)

        while len(self._cache) > self._max_cache_entries and self._cache_expiry:
            oldest_key = min(self._cache_expiry, key=self._cache_expiry.get)
            self._evict_cache_key(oldest_key)
    
    def get_current_prices(self, coins: List[str]) -> Dict[str, Dict]:
        """Get current prices from Binance API with CoinGecko fallback."""
        cache_key = 'prices_' + '_'.join(sorted(coins))

        # Return cached data if still valid
        with self._lock:
            now = time.time()
            self._evict_expired_entries(now)
            cached = self._cache.get(cache_key)
            expiry = self._cache_expiry.get(cache_key, 0)
            if cached and expiry > now:
                return cached

        prices: Dict[str, Dict] = {}
        snapshot_ts = int(time.time())
        binance_error: Optional[Exception] = None

        try:
            symbols = [self.binance_symbols.get(coin) for coin in coins if coin in self.binance_symbols]

            if symbols:
                symbols_param = '[' + ','.join([f'"{s}"' for s in symbols]) + ']'
                response = requests.get(
                    f"{self.binance_base_url}/ticker/24hr",
                    params={'symbols': symbols_param},
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()

                for item in data:
                    symbol = item['symbol']
                    for coin, binance_symbol in self.binance_symbols.items():
                        if binance_symbol == symbol:
                            prices[coin] = {
                                'price': float(item['lastPrice']),
                                'change_24h': float(item['priceChangePercent']),
                                'volume': float(item.get('volume', 0)),
                                'source': 'binance',
                                'timestamp': snapshot_ts
                            }
                            break
        except Exception as exc:
            binance_error = exc
            self._logger.error(f"Binance API failed: {exc}")

        if prices:
            self._store_cache_entry(cache_key, prices)
            return prices

        if binance_error is None:
            self._logger.warning("Binance API returned empty data set, falling back to CoinGecko")

        fallback_prices = self._get_prices_from_coingecko(coins, binance_error)
        self._store_cache_entry(cache_key, fallback_prices)
        return fallback_prices
    
    def _store_cache_entry(self, cache_key: str, prices: Dict[str, Dict]) -> None:
        """Persist fetched prices in the in-memory cache."""
        with self._lock:
            if prices:
                expiry_ts = time.time() + self._cache_duration
                self._cache[cache_key] = prices
                self._cache_expiry[cache_key] = expiry_ts
                heapq.heappush(self._expiry_heap, (expiry_ts, cache_key))
                self._evict_expired_entries()
            else:
                self._evict_cache_key(cache_key)

    def _get_prices_from_coingecko(
        self,
        coins: List[str],
        previous_error: Optional[Exception] = None,
    ) -> Dict[str, Dict]:
        """Fallback: Fetch prices from CoinGecko or raise if unavailable."""
        try:
            snapshot_ts = int(time.time())
            coin_ids = [self.coingecko_mapping.get(coin, coin.lower()) for coin in coins]

            response = requests.get(
                f"{self.coingecko_base_url}/simple/price",
                params={
                    'ids': ','.join(coin_ids),
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            prices: Dict[str, Dict] = {}
            for coin in coins:
                coin_id = self.coingecko_mapping.get(coin, coin.lower())
                if coin_id in data:
                    prices[coin] = {
                        'price': data[coin_id]['usd'],
                        'change_24h': data[coin_id].get('usd_24h_change', 0),
                        'volume': 0,
                        'source': 'coingecko',
                        'timestamp': snapshot_ts
                    }

            if prices:
                return prices

            detail = "CoinGecko returned an empty result set"
            if previous_error:
                detail = f"Binance error: {previous_error}; {detail}"
            self._logger.error(detail)
            raise MarketDataException(ERROR_MSG_API_REQUEST_FAILED.format(detail=detail))

        except MarketDataException:
            raise
        except Exception as exc:
            detail = f"CoinGecko request failed: {exc}"
            if previous_error:
                detail = f"Binance error: {previous_error}; CoinGecko error: {exc}"
            self._logger.error(detail)
            raise MarketDataException(
                ERROR_MSG_API_REQUEST_FAILED.format(detail=detail)
            ) from exc
    
    def get_market_data(self, coin: str) -> Dict:
        """Get detailed market data from CoinGecko"""
        coin_id = self.coingecko_mapping.get(coin, coin.lower())
        
        try:
            response = requests.get(
                f"{self.coingecko_base_url}/coins/{coin_id}",
                params={'localization': 'false', 'tickers': 'false', 'community_data': 'false'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            
            return {
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'total_volume': market_data.get('total_volume', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'high_24h': market_data.get('high_24h', {}).get('usd', 0),
                'low_24h': market_data.get('low_24h', {}).get('usd', 0),
            }
        except Exception as e:
            self._logger.error(f"Failed to get market data for {coin}: {e}")
            return {}
    
    def get_historical_prices(self, coin: str, days: int = 7) -> List[Dict]:
        """Get historical prices from CoinGecko"""
        coin_id = self.coingecko_mapping.get(coin, coin.lower())
        
        try:
            response = requests.get(
                f"{self.coingecko_base_url}/coins/{coin_id}/market_chart",
                params={'vs_currency': 'usd', 'days': days},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for price_data in data.get('prices', []):
                prices.append({
                    'timestamp': price_data[0],
                    'price': price_data[1]
                })
            
            return prices
        except Exception as e:
            self._logger.error(f"Failed to get historical prices for {coin}: {e}")
            return []
    
    def calculate_technical_indicators(self, coin: str) -> Dict:
        """Calculate technical indicators"""
        historical = self.get_historical_prices(coin, days=14)
        
        if not historical or len(historical) < 14:
            return {}
        
        prices = [p['price'] for p in historical]
        
        # Simple Moving Average
        sma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else prices[-1]
        sma_14 = sum(prices[-14:]) / 14 if len(prices) >= 14 else prices[-1]
        
        # Simple RSI calculation
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [c if c > 0 else 0 for c in changes]
        losses = [-c if c < 0 else 0 for c in changes]
        
        avg_gain = sum(gains[-14:]) / 14 if gains else 0
        avg_loss = sum(losses[-14:]) / 14 if losses else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        return {
            'sma_7': sma_7,
            'sma_14': sma_14,
            'rsi_14': rsi,
            'current_price': prices[-1],
            'price_change_7d': ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] > 0 else 0
        }
