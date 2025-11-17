"""AITradeGame - Main Application Entry Point

This module serves as the main entry point for the AITradeGame application.
It initializes the Flask application, sets up all services, registers blueprints,
and starts the trading loop.
"""

from flask import Flask, render_template
from flask_cors import CORS
import threading
import time
import webbrowser
from datetime import datetime

from backend.config.settings import Config
from backend.data.sqlite_db import SQLiteDatabase
from backend.data.market_data import MarketDataFetcher
from backend.services.trading_service import TradingService
from backend.services.portfolio_service import PortfolioService
from backend.services.market_service import MarketService

# Import all blueprints
from backend.api.providers import providers_bp
from backend.api.models import models_bp
from backend.api.trades import trades_bp
from backend.api.market import market_bp
from backend.api.system import system_bp


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
    
    # Initialize database
    print("[INFO] Initializing database...")
    db = SQLiteDatabase(config.SQLITE_PATH)
    db.init_db()
    print("[INFO] Database initialized")
    
    # Initialize market data fetcher with config
    market_fetcher = MarketDataFetcher(
        api_url=config.MARKET_API_URL,
        cache_duration=config.MARKET_CACHE_DURATION
    )
    
    # Initialize services
    print("[INFO] Initializing services...")
    trading_service = TradingService(db, market_fetcher)
    portfolio_service = PortfolioService(db)
    market_service = MarketService(market_fetcher, default_coins=config.DEFAULT_COINS)
    print("[INFO] Services initialized")
    
    # Store services in app.config for blueprint access
    app.config['db'] = db
    app.config['trading_service'] = trading_service
    app.config['portfolio_service'] = portfolio_service
    app.config['market_service'] = market_service
    app.config['app_config'] = config
    
    # Register blueprints
    app.register_blueprint(providers_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(trades_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(system_bp)
    
    # Register index route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app


def start_trading_loop(trading_service: TradingService, config: Config):
    """Start the automated trading loop
    
    This function runs in a separate thread and executes trading cycles
    for all active models at regular intervals.
    
    Args:
        trading_service: TradingService instance to execute trades
        config: Configuration object containing trading settings
    """
    print("[INFO] Trading loop started")
    
    while True:
        try:
            # Check if there are any engines to trade
            if not trading_service.engines:
                time.sleep(30)
                continue
            
            # Print cycle header
            print(f"\n{'='*60}")
            print(f"[CYCLE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[INFO] Active models: {len(trading_service.engines)}")
            print(f"{'='*60}")
            
            # Execute trading cycle for each model
            for model_id, engine in list(trading_service.engines.items()):
                try:
                    print(f"\n[EXEC] Model {model_id}")
                    result = engine.execute_trading_cycle()
                    
                    if result.get('success'):
                        print(f"[OK] Model {model_id} completed")
                        if result.get('executions'):
                            for exec_result in result['executions']:
                                signal = exec_result.get('signal', 'unknown')
                                coin = exec_result.get('coin', 'unknown')
                                msg = exec_result.get('message', '')
                                if signal != 'hold':
                                    print(f"  [TRADE] {coin}: {msg}")
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"[WARN] Model {model_id} failed: {error}")
                        
                except Exception as e:
                    print(f"[ERROR] Model {model_id} exception: {e}")
                    import traceback
                    print(traceback.format_exc())
                    continue
            
            # Print cycle footer
            print(f"\n{'='*60}")
            print(f"[SLEEP] Waiting {config.DEFAULT_TRADING_FREQUENCY} seconds for next cycle")
            print(f"{'='*60}\n")
            
            # Sleep until next cycle
            time.sleep(config.DEFAULT_TRADING_FREQUENCY)
            
        except Exception as e:
            print(f"\n[CRITICAL] Trading loop error: {e}")
            import traceback
            print(traceback.format_exc())
            print("[RETRY] Retrying in 60 seconds\n")
            time.sleep(60)
    
    print("[INFO] Trading loop stopped")


if __name__ == '__main__':
    # Load configuration
    config = Config()
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("AITradeGame - Starting...")
    print("=" * 60)
    
    # Create application
    app = create_app(config)
    
    # Get services from app config
    trading_service = app.config['trading_service']
    
    # Initialize trading engines
    print("[INFO] Initializing trading engines...")
    trading_service.initialize_engines(config.DEFAULT_TRADE_FEE_RATE)
    
    # Start auto-trading thread if enabled
    if config.AUTO_TRADING:
        trading_thread = threading.Thread(
            target=start_trading_loop,
            args=(trading_service, config),
            daemon=True
        )
        trading_thread.start()
        print("[INFO] Auto-trading enabled")
    else:
        print("[INFO] Auto-trading disabled")
    
    # Print ready message
    print("\n" + "=" * 60)
    print("AITradeGame is running!")
    print(f"Server: http://{config.HOST}:{config.PORT}")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    # Auto-open browser
    def open_browser():
        time.sleep(1.5)  # Wait for server to start
        url = f"http://localhost:{config.PORT}"
        try:
            webbrowser.open(url)
            print(f"[INFO] Browser opened: {url}")
        except Exception as e:
            print(f"[WARN] Could not open browser: {e}")
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start Flask application
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT,
        use_reloader=False  # Disable reloader to prevent duplicate threads
    )
