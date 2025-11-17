"""Application constants"""

# API endpoints
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Trading signals
SIGNAL_BUY = 'buy_to_enter'
SIGNAL_SELL = 'sell_to_enter'
SIGNAL_CLOSE = 'close_position'
SIGNAL_HOLD = 'hold'

# Position sides
SIDE_LONG = 'long'
SIDE_SHORT = 'short'

# Leverage limits
MIN_LEVERAGE = 1
MAX_LEVERAGE = 20

# Default values
DEFAULT_INITIAL_CAPITAL = 10000.0
DEFAULT_TRADE_FEE_RATE = 0.001

# Cache settings
MARKET_DATA_CACHE_TTL = 5  # seconds

# API response codes
SUCCESS_CODE = 'SUCCESS'
ERROR_CODE = 'ERROR'
