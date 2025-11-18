"""AITradeGame - Main Application Entry Point

This module serves as the main entry point for the AITradeGame application.
It initializes the Flask application, sets up all services, registers blueprints,
and starts the trading loop.
"""

import atexit
import logging

from flask import Flask, g, current_app
from flask_cors import CORS

from backend.config.settings import Config
from backend.config.constants import (
    DEFAULT_TRADE_FEE_RATE,
    LOG_MSG_APP_STARTING,
    LOG_MSG_AUTO_TRADING_ENABLED,
    LOG_MSG_AUTO_TRADING_DISABLED,
)
from backend.utils.logging_config import LoggingConfigurator
from backend.utils.errors import register_error_handlers
from backend.core.service_container import ServiceContainer
from backend.core.trading_loop_manager import TradingLoopManager

# Import all blueprints
from backend.api.providers import providers_bp
from backend.api.models import models_bp
from backend.api.trades import trades_bp
from backend.api.market import market_bp
from backend.api.system import system_bp

# Initialize logger
logger = logging.getLogger(__name__)


def create_app(config: Config = None) -> Flask:
    """Create and configure Flask application
    
    This factory function creates the Flask app, initializes all services,
    and registers all API blueprints.
    
    Args:
        config: Configuration object. If None, uses default Config()
        
    Returns:
        Configured Flask application instance
    """
    if config is None:
        config = Config()
    
    # Create Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Create and initialize service container
    container = ServiceContainer(config)
    container.initialize()
    
    # Store container reference in app.config
    app.config['container'] = container
    app.config['app_config'] = config
    
    # Ensure services are cleaned up on application shutdown
    atexit.register(container.cleanup)
    
    # Inject services into request context
    @app.before_request
    def inject_services():
        """Inject service container into Flask g object for blueprint access"""
        g.container = current_app.config['container']
    
    # Register blueprints
    app.register_blueprint(providers_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(trades_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(system_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    # Load configuration
    config = Config()
    
    # Setup logging
    log_level = 'DEBUG' if config.DEBUG else 'INFO'
    LoggingConfigurator.setup_logging(log_level=log_level)
    logger = LoggingConfigurator.get_logger(__name__)
    
    # Log application startup
    logger.info("=" * 60)
    logger.info("AITradeGame - Starting...")
    logger.info("=" * 60)
    logger.info(LOG_MSG_APP_STARTING)
    
    # Create application
    app = create_app(config)
    
    # Get services from container
    container = app.config['container']
    trading_service = container.trading_service
    db = container.db
    
    # Initialize trading engines
    logger.info("Initializing trading engines...")
    settings = db.get_settings()
    trade_fee_rate = settings.get('trading_fee_rate', DEFAULT_TRADE_FEE_RATE)
    trading_service.initialize_engines(trade_fee_rate)
    logger.info("Trading engines initialized")
    
    # Create trading loop manager
    trading_loop_manager = TradingLoopManager(trading_service, db)
    
    # Start auto-trading if enabled
    if config.AUTO_TRADING:
        trading_loop_manager.start()
        logger.info(LOG_MSG_AUTO_TRADING_ENABLED)
    else:
        logger.info(LOG_MSG_AUTO_TRADING_DISABLED)
    
    # Log ready message
    logger.info("=" * 60)
    logger.info("AITradeGame is running!")
    logger.info(f"Server: http://{config.HOST}:{config.PORT}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Start Flask application
    try:
        app.run(
            debug=config.DEBUG,
            host=config.HOST,
            port=config.PORT,
            use_reloader=False  # Disable reloader to prevent duplicate threads
        )
    finally:
        # Graceful shutdown
        if trading_loop_manager.is_running():
            logger.info("Stopping trading loop...")
            trading_loop_manager.stop()
        container.cleanup()
        logger.info("Application shutdown complete")
