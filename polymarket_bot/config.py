"""
Configuration for Polymarket Trading Bot
"""

# Trading Parameters
PAPER_TRADING = True  # Start with paper trading!

# Arbitrage Settings
MIN_ARBITRAGE_PROFIT = 0.02  # Minimum 2¢ profit to execute
MAX_POSITION_SIZE = 500  # Max shares per position
STANDARD_POSITION_SIZE = 151  # FirstOrder's standard size

# Market Making Settings
MARKET_MAKING_ENABLED = True
SPREAD_LEVELS = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
MARKET_MAKING_SIZE = 11  # Small size for limit orders

# Risk Management
MAX_TOTAL_EXPOSURE = 10000  # Max $10k total exposure
MAX_PER_MARKET = 3000  # Max $3k per single market
STOP_LOSS_ENABLED = False  # No stop loss for arbitrage

# Target Markets
TARGET_TOKENS = ['Bitcoin', 'Ethereum', 'Solana', 'XRP']
MARKET_TYPES = ['Up or Down']
TIME_WINDOWS = ['hourly']  # Focus on hourly markets

# API Settings
CLOB_API_URL = "https://clob.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"
STRAPI_API_URL = "https://strapi-matic.poly.market"

# Update frequency
SCAN_INTERVAL = 5  # Scan for opportunities every 5 seconds
POSITION_CHECK_INTERVAL = 30  # Check positions every 30 seconds

# Paper Trading Settings
PAPER_STARTING_BALANCE = 10000  # Start with $10k virtual money
PAPER_SLIPPAGE = 0.005  # Assume 0.5% slippage

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "polymarket_bot.log"
ENABLE_DISCORD_ALERTS = False  # Can add Discord webhook for alerts

# Wallet (for real trading - NOT USED in paper mode)
WALLET_ADDRESS = None  # Add your wallet address when ready
PRIVATE_KEY = None  # NEVER commit this!

# Performance tracking
TRACK_PERFORMANCE = True
PERFORMANCE_LOG = "performance.json"
