"""PostgreSQL database implementation composed from focused mixins."""

from __future__ import annotations

from backend.data.postgres import (
    AccountValueRepositoryMixin,
    ConversationRepositoryMixin,
    MarketHistoryRepositoryMixin,
    ModelRepositoryMixin,
    PortfolioRepositoryMixin,
    PostgresBase,
    ProviderRepositoryMixin,
    SettingsRepositoryMixin,
    TradeRepositoryMixin,
)


class PostgreSQLDatabase(PostgresBase):
    """Concrete PostgreSQL database used across the backend."""

    # Provider management
    add_provider = ProviderRepositoryMixin.add_provider
    get_provider = ProviderRepositoryMixin.get_provider
    get_all_providers = ProviderRepositoryMixin.get_all_providers
    delete_provider = ProviderRepositoryMixin.delete_provider
    update_provider = ProviderRepositoryMixin.update_provider

    # Model management
    add_model = ModelRepositoryMixin.add_model
    get_model = ModelRepositoryMixin.get_model
    get_all_models = ModelRepositoryMixin.get_all_models
    delete_model = ModelRepositoryMixin.delete_model

    # Portfolio + positions
    update_position = PortfolioRepositoryMixin.update_position
    get_portfolio = PortfolioRepositoryMixin.get_portfolio
    close_position = PortfolioRepositoryMixin.close_position

    # Trades
    add_trade = TradeRepositoryMixin.add_trade
    get_trades = TradeRepositoryMixin.get_trades

    # Conversations
    add_conversation = ConversationRepositoryMixin.add_conversation
    get_conversations = ConversationRepositoryMixin.get_conversations

    # Account value analytics
    record_account_value = AccountValueRepositoryMixin.record_account_value
    get_account_value_history = AccountValueRepositoryMixin.get_account_value_history
    get_aggregated_account_value_history = (
        AccountValueRepositoryMixin.get_aggregated_account_value_history
    )
    get_multi_model_chart_data = AccountValueRepositoryMixin.get_multi_model_chart_data

    # Market history
    record_market_prices = MarketHistoryRepositoryMixin.record_market_prices
    get_market_history = MarketHistoryRepositoryMixin.get_market_history

    # Settings
    get_settings = SettingsRepositoryMixin.get_settings
    update_settings = SettingsRepositoryMixin.update_settings
