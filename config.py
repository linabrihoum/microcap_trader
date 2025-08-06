"""
Configuration settings for the microcap trading system.

OPTIMIZED STRATEGY BASED ON PERFORMANCE ANALYSIS:
- Current Win Rate: 16.7% (needs improvement)
- Best Performer: ATAI (+18.66% return)
- Focus: Cannabis sector (proven winner), shorter hold periods
- Risk Management: Tighter stops, better entry timing
- Machine Learning: Enhanced pattern recognition for momentum trades
"""

# File paths
PORTFOLIO_FILE = "data/portfolio.csv"
CANDIDATES_FILE = "data/candidates.csv"
DAILY_REPORT_FILE = "data/daily_report.md"

# Market cap threshold (in billions)
MAX_MARKET_CAP = 2.0

# OPTIMIZED candidate selection settings
STRATEGIC_CANDIDATES_COUNT = 3  # Focus on top 3 proven winners
PROVEN_WINNERS_COUNT = 5  # Reduced to focus on best performers
REAL_TIME_CANDIDATES_COUNT = 15  # Reduced for quality over quantity

# ENHANCED filtering criteria based on performance analysis
MIN_VOLUME_THRESHOLD = 500  # Increased for better liquidity
MIN_PRICE_THRESHOLD = 1.0   # Minimum price for microcap focus
MAX_PRICE_THRESHOLD = 20.0  # Reduced max price for better risk control
MIN_MOMENTUM_THRESHOLD = 5   # Only positive momentum (learned from losses)
MIN_AFTERNOON_MOMENTUM = 2   # Increased threshold for afternoon trades

# IMPROVED trading bot configuration
ACCOUNT_SIZE = 200  # Account size in dollars
MAX_POSITION_SIZE = 0.20  # Reduced from 0.25 for better diversification
STOP_LOSS_PERCENTAGE = 0.03  # Tighter 3% stop-loss (learned from losses)
PROFIT_TARGET_PERCENTAGE = 0.15  # 15% profit target for quick wins

# ENHANCED strategy settings
STRATEGIES = ["proven_winners", "momentum_focused", "hybrid"]
DEFAULT_STRATEGY = "momentum_focused"  # Changed to focus on momentum

# OPTIMIZED sector classification based on performance
CANNABIS_SYMBOLS = ['ATAI', 'SNDL', 'CGC', 'HEXO', 'TLRY', 'APHA', 'CRON']  # ATAI first
CLEAN_ENERGY_SYMBOLS = ['PLUG', 'FCEL', 'BLDP', 'BEEM', 'HYSR', 'SUNW']
BIOTECH_SYMBOLS = ['OCGN', 'DRUG', 'STIM']

# PROVEN winners based on actual trading history (ranked by performance)
PROVEN_WINNERS = [
    {'symbol': 'ATAI', 'reason': 'Best performer (+18.66% return)', 'confidence': 'High', 'sector': 'Cannabis'},
    {'symbol': 'SNDL', 'reason': 'Current winner (+0.61% return)', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'CGC', 'reason': 'Cannabis sector, momentum potential', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'HEXO', 'reason': 'Cannabis sector, high volume', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'TLRY', 'reason': 'Cannabis sector, established player', 'confidence': 'Medium', 'sector': 'Cannabis'}
]

# NEW: Performance-based learning settings
MIN_HOLD_DAYS = 1  # Minimum hold period (learned from quick wins)
MAX_HOLD_DAYS = 7  # Maximum hold period (avoid long-term holds)
MOMENTUM_THRESHOLD = 10  # Minimum 1-day momentum for entry
VOLUME_THRESHOLD = 1000  # Minimum volume for entry

# ENHANCED risk management
MAX_DAILY_LOSS = 10  # Maximum daily loss in dollars
MAX_WEEKLY_LOSS = 50  # Maximum weekly loss in dollars
POSITION_SIZING_MULTIPLIER = 0.8  # Conservative position sizing

# Data columns
PORTFOLIO_COLUMNS = ["symbol", "shares", "buy_price", "current_price", "pnl"]
CANDIDATES_COLUMNS = ["symbol", "market_cap", "price", "pct_change_1d", "pct_change_5d", "avg_volume"]

# Date format for reports
DATE_FORMAT = "%Y-%m-%d"

# Rich console styling
STYLE_SUCCESS = "green"
STYLE_ERROR = "red"
STYLE_WARNING = "yellow"
STYLE_INFO = "blue"
STYLE_HEADER = "bold cyan" 