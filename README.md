# AITradeGame - Open Source AI Trading Simulator

[English](README.md) | [中文](README_ZH.md)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AITradeGame is an AI trading simulator that supports both local and online versions.

Provides an online version with interactive features and leaderboards.

Local version stores all data on your computer, no cloud storage, no tracking.

Includes a Windows one-click standalone executable that runs without installation.

## Features

### Desktop Version (Local)

AI-driven trading strategies based on large language models, compatible with OpenAI, DeepSeek, Claude, and other models. Leveraged portfolio management with ECharts visualizations. 100% privacy with all data stored in local database. Trading fee configuration supported to simulate real trading environment.

**Modern Frontend (Migrated):**
The application now features a modern Next.js 15 + React 19 frontend with TypeScript, Tailwind CSS 4, and Shadcn UI components. The new frontend provides enhanced user experience with responsive design, dark mode support, and improved performance.

**Latest Features:**
- API Provider Management: Unified management of multiple AI service provider API configurations
- Smart Model Selection: Automatically fetch available model lists for each provider
- Aggregated View: View aggregated assets and performance comparison across all models
- System Settings: Configurable trading frequency and fee rates
- Responsive Design: Full mobile and tablet support
- Dark Mode: System-aware theme switching

### Online Version (Public)

Leaderboard functionality to compete with AI enthusiasts worldwide. Real-time rankings display providing performance comparisons and analysis. Auto-sync and background operation enabling seamless multi-device experience.

## Quick Start

### Try Online Version

Launch the online version at https://aitradegame.com without any installation.

### Desktop Version

Download AITradeGame.exe from GitHub releases. Double-click the executable to run. The interface will open automatically. Start adding AI models and begin trading.

Alternatively, clone the repository from GitHub. Install dependencies with pip install -r requirements.txt. Run the application with python main.py and visit http://localhost:5000.

### Docker Deployment

You can also run AITradeGame using Docker:

**Using docker-compose (recommended):**
```bash
# Build and start the container
docker-compose up -d

# Access the application at http://localhost:5000
```

**Using docker directly:**
```bash
# Build the image
docker build -t aitradegame .

# Run the container
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data aitradegame

# Access the application at http://localhost:5000
```

The docker-compose stack provisions PostgreSQL automatically and stores data in the `postgres_data` volume. If you run the backend container manually, make sure `POSTGRES_URI` points to a reachable PostgreSQL instance before starting the app. To stop the compose stack, run `docker-compose down`.

## Project Structure

The project follows a modular architecture with clear separation of concerns:

```
project/
├── main.py                      # Backend entry point
├── backend/
│   ├── core/                    # Core trading logic (engine, AI trader)
│   ├── data/                    # Data layer (database, market data)
│   ├── api/                     # API routes (providers, models, trades, market, system)
│   ├── models/                  # Data models (provider, trading_model, portfolio, trade)
│   ├── services/                # Business services (trading, portfolio, market)
│   ├── utils/                   # Utility functions (formatters, validators, version)
│   └── config/                  # Configuration (settings, constants)
├── frontend/                    # Next.js 15 + React 19 frontend
│   ├── app/                     # Next.js App Router pages
│   ├── components/              # React components (UI + features)
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utilities and API client
│   └── store/                   # Zustand state management
└── requirements.txt             # Python dependencies
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Key configuration options:
- `DEBUG`: Enable debug mode (default: False)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `POSTGRES_URI`: PostgreSQL connection URI (default: `postgresql://aitrade:aitrade@localhost:5432/aitrade`)
- `AUTO_TRADING`: Enable automatic trading (default: True)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MARKET_CACHE_DURATION`: Market data cache duration in seconds (default: 5)
- `MARKET_API_URL`: External market data API base URL (default: CoinGecko)
- `MARKET_HISTORY_ENABLED`: Toggle background market snapshot persistence (default: True)
- `MARKET_HISTORY_INTERVAL`: Snapshot interval in seconds (default: 60)
- `MARKET_HISTORY_RESOLUTION`: Resolution bucket in seconds for stored candles (default: 60)
- `MARKET_HISTORY_MAX_POINTS`: Maximum records returned from history API (default: 500, capped at 2000)
- `MARKET_HISTORY_CACHE_TTL`: Cache TTL for history responses (default: 60; placeholder for future Redis integration)
- `TRADING_COINS`: Comma-separated list of tradable coins (default: BTC,ETH,SOL,BNB,XRP,DOGE)
- `NEXT_PUBLIC_MARKET_API_BASE_URL`: Frontend override for the market collector service (default: falls back to backend API URL)

Trading frequency, fee rate, and refresh intervals are now configured inside the in-app **Settings** dialog instead of environment variables.

### API Provider Setup
First, add AI service providers:
1. Click the "API Provider" button
2. Enter provider name, API URL, and API key
3. Manually input available models or click "Fetch Models" to auto-fetch
4. Click save to complete configuration

### Adding Trading Models
After configuring providers, add trading models:
1. Click the "Add Model" button
2. Select a configured API provider
3. Choose a specific model from the dropdown
4. Enter display name and initial capital
5. Click submit to start trading

### System Settings
Click the "Settings" button to configure:
- Trading Frequency: Control AI decision interval (1-1440 minutes)
- Trading Fee Rate: Commission rate per trade (default 0.1%)
- Market Refresh Interval: How often market data updates (seconds)
- Portfolio Refresh Interval: How often portfolio data refreshes (seconds)

### Market Data APIs
- `GET /api/market/prices`: Returns the latest price and 24h change for the configured trading universe.
- `GET /api/market/history`: Returns persisted OHLC snapshots. Query params:
  - `coin` (required): Symbol such as `BTC`
  - `resolution` (optional): Bucket size in seconds (default from config)
  - `limit` (optional): Number of points (max 2000, default 500)
  - `start` / `end` (optional): ISO8601 timestamps to bound the query
- **Standalone Collector**: When running via docker-compose, a dedicated `market-collector` service (port 5100) handles price persistence and exposes `/api/health`, `/api/market/prices`, `/api/market/history` so price tracking continues even if the main backend restarts.

## Supported AI Models

Supports all OpenAI-compatible APIs. This includes OpenAI models like gpt-4 and gpt-3.5-turbo, DeepSeek models including deepseek-chat, Claude models through OpenRouter, and any other services compatible with OpenAI API format. More protocols are being added.

## Usage

### Desktop Version (Standalone Executable)
Run AITradeGame.exe and the interface will open automatically at http://localhost:5000.

### Development Mode
1. Start the backend server:
```bash
python main.py
```
The backend API will be available at http://localhost:5000

2. Start the frontend development server:
```bash
cd frontend
pnpm dev
```
The frontend will be available at http://localhost:3000

Add AI model configuration through the web interface. The system automatically begins trading simulation based on your configuration. Trading fees are charged for each open and close position according to the set rate, ensuring AI strategies operate under realistic cost conditions.

## Privacy and Security

All data is stored in PostgreSQL (using the database defined by `POSTGRES_URI`). When running under docker-compose, the `postgres_data` volume keeps the data on your machine. No external servers are contacted except your specified AI API endpoints. No user accounts or login required - everything runs locally.

## Development

### Backend Development

Development requires Python 3.9 or later. Internet connection is needed for market data and AI API calls.

Install all dependencies with:
```bash
pip install -r requirements.txt
```

Start the backend server:
```bash
python main.py
```

The backend API will be available at http://localhost:5000

### Running Tests

Run all tests with coverage:
```bash
pytest
```

Or use the test script:
```bash
./scripts/run_tests.sh
```

See `DEVELOPMENT.md` for detailed development guide.

### Security Features

- **API Key Encryption**: All API keys are encrypted at rest using Fernet symmetric encryption
- **Error Handling**: Comprehensive error handling with custom exception classes
- **Schema Bootstrap**: Database tables are created automatically when the app starts
- **Input Validation**: Strict validation on all API endpoints

### Frontend Development

The frontend is built with Next.js 15, React 19, TypeScript, Tailwind CSS 4, and Shadcn UI.

**Prerequisites:**
- Node.js 18+ 
- pnpm (recommended) or npm

**Setup:**

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
pnpm install
# or
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` and set the API base URL:
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

4. Start the development server:
```bash
pnpm dev
# or
npm run dev
```

The frontend will be available at http://localhost:3000

**Build for production:**
```bash
pnpm build
pnpm start
```

**Frontend Structure:**
```
frontend/
├── app/                    # Next.js App Router pages
├── components/
│   ├── ui/                # Shadcn UI base components
│   └── features/          # Business components
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities and API client
└── store/                 # Zustand state management
```

**Key Technologies:**
- Next.js 15 with App Router
- React 19 with Server Components
- TypeScript for type safety
- Tailwind CSS 4 for styling
- Shadcn UI for component library
- Zustand for state management
- ECharts for data visualization

## Contributing

Community contributions are welcome.

## Disclaimer

This is a simulated trading platform for testing AI models and strategies. It is not real trading and no actual money is involved. Always conduct your own research and analysis before making investment decisions. No warranties are provided regarding trading outcomes or AI performance.

## Links

Online version with leaderboard and social features: https://aitradegame.com

Desktop builds and releases: https://github.com/chadyi/AITradeGame/releases/tag/main

Source code repository: https://github.com/chadyi/AITradeGame
