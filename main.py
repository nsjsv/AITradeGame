"""AITradeGame - FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.market import router as market_router
from backend.api.models import router as models_router
from backend.api.providers import router as providers_router
from backend.api.system import router as system_router
from backend.api.trades import router as trades_router
from backend.config.constants import (
    DEFAULT_TRADE_FEE_RATE,
    LOG_MSG_APP_STARTING,
    LOG_MSG_AUTO_TRADING_ENABLED,
    LOG_MSG_AUTO_TRADING_DISABLED,
)
from backend.config.settings import Config
from backend.core.service_container import ServiceContainer
from backend.core.trading_loop_manager import TradingLoopManager
from backend.utils.errors import register_error_handlers
from backend.utils.logging_config import LoggingConfigurator

logger = logging.getLogger(__name__)


def _initialize_trading(container: ServiceContainer, config: Config) -> TradingLoopManager:
    """Initialize trading engines and return the loop manager."""
    trading_service = container.trading_service
    db = container.db

    settings = db.get_settings()
    trade_fee_rate = settings.get("trading_fee_rate", DEFAULT_TRADE_FEE_RATE)
    logger.info("Initializing trading engines...")
    trading_service.initialize_engines(trade_fee_rate)
    logger.info("Trading engines initialized")

    return TradingLoopManager(
        trading_service,
        db,
        max_workers=config.TRADING_MAX_CONCURRENCY,
        model_timeout=config.MODEL_CYCLE_TIMEOUT,
    )


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create and configure FastAPI application."""
    config = config or Config()
    log_level = "DEBUG" if getattr(config, "DEBUG", False) else "INFO"
    LoggingConfigurator.setup_logging(log_level=log_level)
    logger = LoggingConfigurator.get_logger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        container = ServiceContainer(config)
        container.initialize()
        app.state.container = container
        app.state.app_config = config

        trading_loop_manager = _initialize_trading(container, config)
        app.state.trading_loop_manager = trading_loop_manager

        if config.AUTO_TRADING:
            trading_loop_manager.start()
            logger.info(LOG_MSG_AUTO_TRADING_ENABLED)
        else:
            logger.info(LOG_MSG_AUTO_TRADING_DISABLED)

        logger.info(LOG_MSG_APP_STARTING)
        try:
            yield
        finally:
            if trading_loop_manager.is_running():
                logger.info("Stopping trading loop...")
                trading_loop_manager.stop()
            container.cleanup()
            logger.info("Application shutdown complete")

    app = FastAPI(title="AITradeGame API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(providers_router)
    app.include_router(models_router)
    app.include_router(trades_router)
    app.include_router(market_router)
    app.include_router(system_router)

    return app


default_config = Config()
app = create_app(default_config)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=default_config.HOST,
        port=default_config.PORT,
        reload=False,
    )
