"""
AI Trader module - LLM-based trading decision system
"""
import json
import logging
from typing import Dict
from openai import OpenAI, APIConnectionError, APIError

from backend.config.constants import (
    ERROR_MSG_API_REQUEST_FAILED,
    ERROR_MSG_CONNECTION_ERROR,
)
from backend.utils.errors import ExternalServiceError


class AITrader:
    """AI trading decision maker using LLM"""
    
    def __init__(self, api_key: str, api_url: str, model_name: str):
        """
        Initialize AI trader
        
        Args:
            api_key: API key for LLM provider
            api_url: Base URL for LLM API
            model_name: Name of the LLM model to use
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model_name = model_name
        self._logger = logging.getLogger(__name__)
    
    def make_decision(self, market_state: Dict, portfolio: Dict, 
                     account_info: Dict) -> Dict:
        """
        Make trading decisions based on market state and portfolio
        
        Args:
            market_state: Current market data with prices and indicators
            portfolio: Current portfolio positions and cash
            account_info: Account information including returns
            
        Returns:
            Dictionary of trading decisions per coin
        """
        prompt = self._build_prompt(market_state, portfolio, account_info)
        
        response = self._call_llm(prompt)
        
        decisions = self._parse_response(response)
        
        return decisions
    
    def _build_prompt(self, market_state: Dict, portfolio: Dict, 
                     account_info: Dict) -> str:
        """Build trading prompt for LLM"""
        prompt = f"""You are a professional cryptocurrency trader. Analyze the market and make trading decisions.

MARKET DATA:
"""
        for coin, data in market_state.items():
            prompt += f"{coin}: ${data['price']:.2f} ({data['change_24h']:+.2f}%)\n"
            if 'indicators' in data and data['indicators']:
                indicators = data['indicators']
                prompt += f"  SMA7: ${indicators.get('sma_7', 0):.2f}, SMA14: ${indicators.get('sma_14', 0):.2f}, RSI: {indicators.get('rsi_14', 0):.1f}\n"
        
        prompt += f"""
ACCOUNT STATUS:
- Initial Capital: ${account_info['initial_capital']:.2f}
- Total Value: ${portfolio['total_value']:.2f}
- Cash: ${portfolio['cash']:.2f}
- Total Return: {account_info['total_return']:.2f}%

CURRENT POSITIONS:
"""
        if portfolio['positions']:
            for pos in portfolio['positions']:
                prompt += f"- {pos['coin']} {pos['side']}: {pos['quantity']:.4f} @ ${pos['avg_price']:.2f} ({pos['leverage']}x)\n"
        else:
            prompt += "None\n"
        
        prompt += """
TRADING RULES:
1. Signals: buy_to_enter (long), sell_to_enter (short), close_position, hold
2. Risk Management:
   - Max 3 positions
   - Risk 1-5% per trade
   - Use appropriate leverage (1-20x)
3. Position Sizing:
   - Conservative: 1-2% risk
   - Moderate: 2-4% risk
   - Aggressive: 4-5% risk
4. Exit Strategy:
   - Close losing positions quickly
   - Let winners run
   - Use technical indicators

OUTPUT FORMAT (JSON only):
```json
{
  "COIN": {
    "signal": "buy_to_enter|sell_to_enter|hold|close_position",
    "quantity": 0.5,
    "leverage": 10,
    "profit_target": 45000.0,
    "stop_loss": 42000.0,
    "confidence": 0.75,
    "justification": "Brief reason"
  }
}
```

Analyze and output JSON only.
"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API with error handling"""
        try:
            base_url = self.api_url.rstrip('/')
            if not base_url.endswith('/v1'):
                if '/v1' in base_url:
                    base_url = base_url.split('/v1')[0] + '/v1'
                else:
                    base_url = base_url + '/v1'
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency trader. Output JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except APIConnectionError as e:
            error_msg = ERROR_MSG_CONNECTION_ERROR
            self._logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ExternalServiceError(
                error_msg,
                status_code=503,
                details={
                    "provider": self.api_url,
                    "model": self.model_name,
                    "error": str(e),
                },
            ) from e
        except APIError as e:
            status = getattr(e, "status_code", 502) or 502
            message = getattr(e, "message", str(e)) or str(e)
            error_msg = ERROR_MSG_API_REQUEST_FAILED.format(detail=f"{status}: {message}")
            self._logger.error(error_msg, exc_info=True)
            raise ExternalServiceError(
                error_msg,
                status_code=status if isinstance(status, int) else 502,
                details={
                    "provider": self.api_url,
                    "model": self.model_name,
                    "status": status,
                    "error": message,
                },
            ) from e
        except Exception as e:
            error_msg = f"LLM call failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            raise ExternalServiceError(
                error_msg,
                status_code=500,
                details={
                    "provider": self.api_url,
                    "model": self.model_name,
                    "error": str(e),
                },
            ) from e
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response to extract trading decisions
        
        Raises:
            ValueError: If response cannot be parsed as valid JSON
        """
        response = response.strip()
        
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]
        
        try:
            decisions = json.loads(response.strip())
            if not isinstance(decisions, dict):
                raise ValueError(f"Expected dict, got {type(decisions).__name__}")
            return decisions
        except json.JSONDecodeError as e:
            self._logger.error(
                f"Failed to parse LLM response as JSON: {e}, "
                f"response_length={len(response)}, "
                f"response_preview={response[:200]}"
            )
            raise ValueError(f"Invalid JSON response from LLM: {e}") from e
        except ValueError as e:
            self._logger.error(f"Invalid response format: {e}")
            raise
