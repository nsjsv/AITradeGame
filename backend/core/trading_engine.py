"""
Trading Engine module - Core trading logic and execution
"""
from datetime import datetime
from typing import Dict
import json
import logging

from backend.data.database import DatabaseInterface
from backend.data.market_data import MarketDataFetcher
from backend.core.ai_trader import AITrader
from backend.config.constants import (
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_CLOSE,
    SIGNAL_HOLD,
    ERROR_MSG_TRADING_LOOP_ERROR,
)


class TradingEngine:
    """Trading engine for executing AI-driven trades"""
    
    def __init__(
        self, 
        model_id: int, 
        db: DatabaseInterface, 
        market_fetcher: MarketDataFetcher, 
        ai_trader: AITrader, 
        trade_fee_rate: float = 0.001
    ):
        """
        Initialize trading engine
        
        Args:
            model_id: ID of the trading model
            db: Database interface for data operations
            market_fetcher: Market data fetcher
            ai_trader: AI trader for decision making
            trade_fee_rate: Trading fee rate (default 0.1%)
        """
        self.model_id = model_id
        self.db = db
        self.market_fetcher = market_fetcher
        self.ai_trader = ai_trader
        self.coins = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']
        self.trade_fee_rate = trade_fee_rate
        self._logger = logging.getLogger(__name__)
    
    def execute_trading_cycle(self) -> Dict:
        """
        Execute one complete trading cycle
        
        Returns:
            Dictionary with execution results
            
        Raises:
            Exception: Re-raises any exception after logging for proper error handling
        """
        try:
            self._logger.info(
                f"Starting trading cycle for model_id={self.model_id}"
            )
            
            market_state = self._get_market_state()
            formatted_prices = [
                f"{coin}:${market_state[coin]['price']:.2f}"
                for coin in market_state
            ]
            self._logger.debug(
                f"Market state retrieved: {len(market_state)} coins, "
                f"prices={formatted_prices}"
            )
            
            current_prices = {coin: market_state[coin]['price'] for coin in market_state}
            
            portfolio = self.db.get_portfolio(self.model_id, current_prices)
            self._logger.debug(
                f"Portfolio: cash=${portfolio['cash']:.2f}, "
                f"total_value=${portfolio['total_value']:.2f}, "
                f"positions={len(portfolio['positions'])}, "
                f"total_fees=${portfolio.get('total_fees', 0):.2f}"
            )
            
            account_info = self._build_account_info(portfolio)
            
            decisions = self.ai_trader.make_decision(
                market_state, portfolio, account_info
            )
            self._logger.info(
                f"AI decisions for model_id={self.model_id}: "
                f"{len(decisions)} signals generated"
            )
            
            self.db.add_conversation(
                self.model_id,
                user_prompt=self._format_prompt(market_state, portfolio, account_info),
                ai_response=json.dumps(decisions, ensure_ascii=False),
                cot_trace=''
            )
            
            execution_results = self._execute_decisions(decisions, market_state, portfolio)
            
            # Log execution results
            for result in execution_results:
                if 'error' in result:
                    self._logger.warning(
                        f"Trade execution failed for {result.get('coin', 'unknown')}: "
                        f"{result['error']}"
                    )
                elif 'message' in result:
                    self._logger.info(
                        f"Trade executed: {result['message']}"
                    )
            
            updated_portfolio = self.db.get_portfolio(self.model_id, current_prices)
            self.db.record_account_value(
                self.model_id,
                updated_portfolio['total_value'],
                updated_portfolio['cash'],
                updated_portfolio['positions_value']
            )
            
            self._logger.info(
                f"Trading cycle completed for model_id={self.model_id}, "
                f"new_total_value=${updated_portfolio['total_value']:.2f}"
            )
            
            return {
                'success': True,
                'decisions': decisions,
                'executions': execution_results,
                'portfolio': updated_portfolio
            }
            
        except ValueError as e:
            self._logger.error(
                f"Validation error in trading cycle for model_id={self.model_id}: {e}",
                exc_info=True
            )
            raise
        except KeyError as e:
            self._logger.error(
                f"Missing required data in trading cycle for model_id={self.model_id}: {e}",
                exc_info=True
            )
            raise
        except Exception as e:
            self._logger.error(
                f"Unexpected error in trading cycle for model_id={self.model_id}: {e}",
                exc_info=True
            )
            raise
    
    def _get_market_state(self) -> Dict:
        """Get current market state with prices and indicators"""
        market_state = {}
        prices = self.market_fetcher.get_current_prices(self.coins)
        
        for coin in self.coins:
            if coin in prices:
                market_state[coin] = prices[coin].copy()
                indicators = self.market_fetcher.calculate_technical_indicators(coin)
                market_state[coin]['indicators'] = indicators
        
        return market_state
    
    def _build_account_info(self, portfolio: Dict) -> Dict:
        """Build account information for AI decision making"""
        model = self.db.get_model(self.model_id)
        initial_capital = model['initial_capital']
        total_value = portfolio['total_value']
        total_return = ((total_value - initial_capital) / initial_capital) * 100
        
        return {
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_return': total_return,
            'initial_capital': initial_capital
        }
    
    def _format_prompt(self, market_state: Dict, portfolio: Dict, 
                      account_info: Dict) -> str:
        """Format prompt summary for conversation history"""
        return f"Market State: {len(market_state)} coins, Portfolio: {len(portfolio['positions'])} positions"
    
    def _execute_decisions(self, decisions: Dict, market_state: Dict, 
                          portfolio: Dict) -> list:
        """Execute trading decisions
        
        Args:
            decisions: AI trading decisions per coin
            market_state: Current market data
            portfolio: Current portfolio state
            
        Returns:
            List of execution results
        """
        results = []
        
        for coin, decision in decisions.items():
            if coin not in self.coins:
                self._logger.warning(
                    f"Skipping unknown coin: {coin}, "
                    f"valid_coins={self.coins}"
                )
                continue
            
            signal = decision.get('signal', '').lower()
            
            try:
                if signal == SIGNAL_BUY:
                    result = self._execute_buy(coin, decision, market_state, portfolio)
                elif signal == SIGNAL_SELL:
                    result = self._execute_sell(coin, decision, market_state, portfolio)
                elif signal == SIGNAL_CLOSE:
                    result = self._execute_close(coin, decision, market_state, portfolio)
                elif signal == SIGNAL_HOLD:
                    result = {'coin': coin, 'signal': SIGNAL_HOLD, 'message': 'Hold position'}
                else:
                    self._logger.warning(
                        f"Unknown signal for {coin}: {signal}, "
                        f"valid_signals=[{SIGNAL_BUY}, {SIGNAL_SELL}, {SIGNAL_CLOSE}, {SIGNAL_HOLD}]"
                    )
                    result = {'coin': coin, 'error': f'Unknown signal: {signal}'}
                
                results.append(result)
                
            except ValueError as e:
                self._logger.error(
                    f"Validation error executing {signal} for {coin}: {e}"
                )
                results.append({'coin': coin, 'error': f'Validation error: {str(e)}'})
            except KeyError as e:
                self._logger.error(
                    f"Missing required field executing {signal} for {coin}: {e}"
                )
                results.append({'coin': coin, 'error': f'Missing field: {str(e)}'})
            except Exception as e:
                self._logger.error(
                    f"Unexpected error executing {signal} for {coin}: {e}",
                    exc_info=True
                )
                results.append({'coin': coin, 'error': f'Execution failed: {str(e)}'})
        
        return results
    
    def _execute_buy(self, coin: str, decision: Dict, market_state: Dict, 
                    portfolio: Dict) -> Dict:
        """Execute buy (long) order
        
        Args:
            coin: Coin symbol
            decision: AI decision with quantity and leverage
            market_state: Current market prices
            portfolio: Current portfolio state
            
        Returns:
            Execution result dictionary
            
        Raises:
            ValueError: If quantity or leverage is invalid
            KeyError: If required market data is missing
        """
        try:
            quantity = float(decision.get('quantity', 0))
            leverage = int(decision.get('leverage', 1))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid quantity or leverage: {e}") from e
        
        if coin not in market_state:
            raise KeyError(f"Market data not available for {coin}")
        
        price = market_state[coin]['price']
        
        if quantity <= 0:
            return {'coin': coin, 'error': 'Invalid quantity: must be positive'}
        
        if leverage < 1 or leverage > 20:
            return {'coin': coin, 'error': f'Invalid leverage: must be 1-20, got {leverage}'}
        
        # Calculate trade amount and fee
        trade_amount = quantity * price
        trade_fee = trade_amount * self.trade_fee_rate
        required_margin = (quantity * price) / leverage
        
        # Total required = margin + fee
        total_required = required_margin + trade_fee
        if total_required > portfolio['cash']:
            return {
                'coin': coin,
                'error': f'Insufficient cash: need ${total_required:.2f}, have ${portfolio["cash"]:.2f}'
            }
        
        # Update position
        self.db.update_position(
            self.model_id, coin, quantity, price, leverage, 'long'
        )
        
        # Record trade with fee (pnl=0 for opening trade, fee is negative)
        self.db.add_trade(
            self.model_id, coin, SIGNAL_BUY, quantity, 
            price, leverage, 'long', pnl=-trade_fee, fee=trade_fee
        )
        
        return {
            'coin': coin,
            'signal': SIGNAL_BUY,
            'quantity': quantity,
            'price': price,
            'leverage': leverage,
            'fee': trade_fee,
            'message': f'Long {quantity:.4f} {coin} @ ${price:.2f} (Fee: ${trade_fee:.2f})'
        }
    
    def _execute_sell(self, coin: str, decision: Dict, market_state: Dict, 
                     portfolio: Dict) -> Dict:
        """Execute sell (short) order
        
        Args:
            coin: Coin symbol
            decision: AI decision with quantity and leverage
            market_state: Current market prices
            portfolio: Current portfolio state
            
        Returns:
            Execution result dictionary
            
        Raises:
            ValueError: If quantity or leverage is invalid
            KeyError: If required market data is missing
        """
        try:
            quantity = float(decision.get('quantity', 0))
            leverage = int(decision.get('leverage', 1))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid quantity or leverage: {e}") from e
        
        if coin not in market_state:
            raise KeyError(f"Market data not available for {coin}")
        
        price = market_state[coin]['price']
        
        if quantity <= 0:
            return {'coin': coin, 'error': 'Invalid quantity: must be positive'}
        
        if leverage < 1 or leverage > 20:
            return {'coin': coin, 'error': f'Invalid leverage: must be 1-20, got {leverage}'}
        
        # Calculate trade amount and fee
        trade_amount = quantity * price
        trade_fee = trade_amount * self.trade_fee_rate
        required_margin = (quantity * price) / leverage
        
        # Total required = margin + fee
        total_required = required_margin + trade_fee
        if total_required > portfolio['cash']:
            return {
                'coin': coin,
                'error': f'Insufficient cash: need ${total_required:.2f}, have ${portfolio["cash"]:.2f}'
            }
        
        # Update position
        self.db.update_position(
            self.model_id, coin, quantity, price, leverage, 'short'
        )
        
        # Record trade with fee (pnl=0 for opening trade, fee is negative)
        self.db.add_trade(
            self.model_id, coin, SIGNAL_SELL, quantity, 
            price, leverage, 'short', pnl=-trade_fee, fee=trade_fee
        )
        
        return {
            'coin': coin,
            'signal': SIGNAL_SELL,
            'quantity': quantity,
            'price': price,
            'leverage': leverage,
            'fee': trade_fee,
            'message': f'Short {quantity:.4f} {coin} @ ${price:.2f} (Fee: ${trade_fee:.2f})'
        }
    
    def _execute_close(self, coin: str, decision: Dict, market_state: Dict, 
                      portfolio: Dict) -> Dict:
        """Execute close position order
        
        Args:
            coin: Coin symbol
            decision: AI decision (not used for close)
            market_state: Current market prices
            portfolio: Current portfolio state
            
        Returns:
            Execution result dictionary
            
        Raises:
            KeyError: If required market data is missing
        """
        position = None
        for pos in portfolio['positions']:
            if pos['coin'] == coin:
                position = pos
                break
        
        if not position:
            return {'coin': coin, 'error': 'No position to close'}
        
        if coin not in market_state:
            raise KeyError(f"Market data not available for {coin}")
        
        current_price = market_state[coin]['price']
        entry_price = position['avg_price']
        quantity = position['quantity']
        side = position['side']
        
        # Calculate gross P&L
        if side == 'long':
            gross_pnl = (current_price - entry_price) * quantity
        else:  # short
            gross_pnl = (entry_price - current_price) * quantity
        
        # Calculate closing fee
        trade_amount = quantity * current_price
        trade_fee = trade_amount * self.trade_fee_rate
        net_pnl = gross_pnl - trade_fee
        
        # Close position
        self.db.close_position(self.model_id, coin, side)
        
        # Record closing trade with fee and net P&L
        self.db.add_trade(
            self.model_id, coin, SIGNAL_CLOSE, quantity,
            current_price, position['leverage'], side, pnl=net_pnl, fee=trade_fee
        )
        
        self._logger.info(
            f"Closed {side} position: {coin}, "
            f"entry=${entry_price:.2f}, exit=${current_price:.2f}, "
            f"quantity={quantity:.4f}, gross_pnl=${gross_pnl:.2f}, "
            f"fee=${trade_fee:.2f}, net_pnl=${net_pnl:.2f}"
        )
        
        return {
            'coin': coin,
            'signal': SIGNAL_CLOSE,
            'quantity': quantity,
            'price': current_price,
            'pnl': net_pnl,
            'fee': trade_fee,
            'message': f'Close {side} {coin}: Gross P&L ${gross_pnl:.2f}, Fee ${trade_fee:.2f}, Net P&L ${net_pnl:.2f}'
        }
