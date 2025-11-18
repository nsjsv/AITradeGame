"""
Test fee accounting to verify the fix for the accounting bug

This test verifies that:
1. Fees are properly deducted from cash
2. Total account value correctly reflects fees paid
3. Opening and closing trades properly account for fees
"""

import pytest


class TestFeeAccounting:
    """Test fee accounting correctness"""
    
    def test_fee_deduction_from_cash(self, db):
        """Test that fees are properly deducted from available cash"""
        # Add provider and model
        provider_id = db.add_provider("Test Provider", "http://test.com", "test_key")
        model_id = db.add_model("Test Model", provider_id, "test-model", initial_capital=10000)
        
        # Open a position (should deduct fee from cash)
        db.update_position(model_id, "BTC", 0.1, 50000, 1, 'long')
        
        # Record opening trade with fee
        opening_fee = 0.1 * 50000 * 0.001  # quantity * price * fee_rate = $5
        db.add_trade(
            model_id, "BTC", "buy_to_enter", 0.1,
            50000, 1, 'long', pnl=-opening_fee, fee=opening_fee
        )
        
        # Get portfolio
        portfolio = db.get_portfolio(model_id, {"BTC": 50000})
        
        # Verify cash calculation
        # Cash = initial_capital + realized_pnl - margin_used
        # realized_pnl = -5 (opening fee recorded as negative pnl)
        # Cash = 10000 + (-5) - 5000 = 4995
        expected_cash = 10000 - opening_fee - 5000  # initial - fee - margin
        assert abs(portfolio['cash'] - expected_cash) < 0.01, \
            f"Expected cash ${expected_cash:.2f}, got ${portfolio['cash']:.2f}"
        
        # Verify total fees
        assert portfolio['total_fees'] == opening_fee, \
            f"Expected total_fees ${opening_fee:.2f}, got ${portfolio['total_fees']:.2f}"
        
        # Verify total value (should be initial capital - fees since no P&L yet)
        expected_total = 10000 - opening_fee
        assert abs(portfolio['total_value'] - expected_total) < 0.01, \
            f"Expected total_value ${expected_total:.2f}, got ${portfolio['total_value']:.2f}"
    
    def test_closing_trade_fee_accounting(self, db):
        """Test that closing trade fees are properly accounted"""
        # Add provider and model
        provider_id = db.add_provider("Test Provider", "http://test.com", "test_key")
        model_id = db.add_model("Test Model", provider_id, "test-model", initial_capital=10000)
        
        # Open position
        db.update_position(model_id, "BTC", 0.1, 50000, 1, 'long')
        opening_fee = 0.1 * 50000 * 0.001  # $5
        db.add_trade(
            model_id, "BTC", "buy_to_enter", 0.1,
            50000, 1, 'long', pnl=-opening_fee, fee=opening_fee
        )
        
        # Close position with profit
        closing_price = 55000
        gross_pnl = (closing_price - 50000) * 0.1  # $500
        closing_fee = 0.1 * closing_price * 0.001  # $5.5
        net_pnl = gross_pnl - closing_fee  # $494.5
        
        db.close_position(model_id, "BTC", 'long')
        db.add_trade(
            model_id, "BTC", "close_position", 0.1,
            closing_price, 1, 'long', pnl=net_pnl, fee=closing_fee
        )
        
        # Get portfolio
        portfolio = db.get_portfolio(model_id, {})
        
        # Verify total fees
        total_fees = opening_fee + closing_fee  # $10.5
        assert abs(portfolio['total_fees'] - total_fees) < 0.01, \
            f"Expected total_fees ${total_fees:.2f}, got ${portfolio['total_fees']:.2f}"
        
        # Verify realized P&L (should include both opening and closing)
        expected_realized_pnl = -opening_fee + net_pnl  # -5 + 494.5 = 489.5
        assert abs(portfolio['realized_pnl'] - expected_realized_pnl) < 0.01, \
            f"Expected realized_pnl ${expected_realized_pnl:.2f}, got ${portfolio['realized_pnl']:.2f}"
        
        # Verify cash (no positions, so cash = initial + realized_pnl)
        # realized_pnl = sum of all trade pnl = -5 + 494.5 = 489.5
        # Cash = 10000 + 489.5 - 0 = 10489.5
        expected_cash = 10000 + expected_realized_pnl
        assert abs(portfolio['cash'] - expected_cash) < 0.01, \
            f"Expected cash ${expected_cash:.2f}, got ${portfolio['cash']:.2f}"
        
        # Verify total value
        expected_total = 10000 + expected_realized_pnl
        assert abs(portfolio['total_value'] - expected_total) < 0.01, \
            f"Expected total_value ${expected_total:.2f}, got ${portfolio['total_value']:.2f}"
    
    def test_multiple_trades_fee_accumulation(self, db):
        """Test that fees accumulate correctly across multiple trades"""
        # Add provider and model
        provider_id = db.add_provider("Test Provider", "http://test.com", "test_key")
        model_id = db.add_model("Test Model", provider_id, "test-model", initial_capital=10000)
        
        total_fees_paid = 0
        
        # Trade 1: Open BTC long
        db.update_position(model_id, "BTC", 0.1, 50000, 1, 'long')
        fee1 = 0.1 * 50000 * 0.001
        total_fees_paid += fee1
        db.add_trade(model_id, "BTC", "buy_to_enter", 0.1, 50000, 1, 'long', pnl=-fee1, fee=fee1)
        
        # Trade 2: Open ETH long
        db.update_position(model_id, "ETH", 1.0, 3000, 1, 'long')
        fee2 = 1.0 * 3000 * 0.001
        total_fees_paid += fee2
        db.add_trade(model_id, "ETH", "buy_to_enter", 1.0, 3000, 1, 'long', pnl=-fee2, fee=fee2)
        
        # Trade 3: Close BTC
        db.close_position(model_id, "BTC", 'long')
        gross_pnl_btc = (51000 - 50000) * 0.1
        fee3 = 0.1 * 51000 * 0.001
        total_fees_paid += fee3
        net_pnl_btc = gross_pnl_btc - fee3
        db.add_trade(model_id, "BTC", "close_position", 0.1, 51000, 1, 'long', pnl=net_pnl_btc, fee=fee3)
        
        # Get portfolio
        portfolio = db.get_portfolio(model_id, {"ETH": 3000})
        
        # Verify total fees
        assert abs(portfolio['total_fees'] - total_fees_paid) < 0.01, \
            f"Expected total_fees ${total_fees_paid:.2f}, got ${portfolio['total_fees']:.2f}"
        
        # Verify cash calculation
        # realized_pnl = -fee1 + -fee2 + net_pnl_btc
        # margin_used = 3000 (ETH position)
        # cash = 10000 + realized_pnl - margin_used
        realized_pnl = -fee1 - fee2 + net_pnl_btc
        margin_used = 3000
        expected_cash = 10000 + realized_pnl - margin_used
        
        assert abs(portfolio['cash'] - expected_cash) < 0.01, \
            f"Expected cash ${expected_cash:.2f}, got ${portfolio['cash']:.2f}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
