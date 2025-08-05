"""
Configuration settings for the microcap trading system.

STRATEGIC APPROACH:
- Proven Winners Strategy: Focus on historically successful stocks (ATAI: +18.66% return)
- Real-Time Analysis: Screen for current momentum and volume patterns
- Hybrid Strategy: Combine proven winners with real-time market analysis
- Sector-Based Scoring: Cannabis sector gets bonus points (your best performer)
- Machine Learning: Learns from your trading history to identify patterns
- Risk Management: 5% stop-loss, position sizing, duplicate avoidance
"""

# File paths
PORTFOLIO_FILE = "portfolio.csv"
CANDIDATES_FILE = "candidates.csv"
DAILY_REPORT_FILE = "daily_report.md"

# Market cap threshold (in billions)
MAX_MARKET_CAP = 2.0

# Strategic candidate selection settings
STRATEGIC_CANDIDATES_COUNT = 5  # Top 5 strategic candidates based on ML analysis
PROVEN_WINNERS_COUNT = 8  # Number of proven winners to analyze
REAL_TIME_CANDIDATES_COUNT = 25  # Number of real-time candidates to screen

# Advanced filtering criteria
MIN_VOLUME_THRESHOLD = 100  # Minimum volume in thousands
MIN_PRICE_THRESHOLD = 1.0   # Minimum price for microcap focus
MAX_PRICE_THRESHOLD = 50.0  # Maximum price for $200 account
MIN_MOMENTUM_THRESHOLD = -20  # Minimum 5-day momentum (avoid severe downtrends)
MIN_AFTERNOON_MOMENTUM = -5   # Minimum afternoon momentum threshold

# Data columns
PORTFOLIO_COLUMNS = ["symbol", "shares", "buy_price", "current_price", "pnl"]
CANDIDATES_COLUMNS = ["symbol", "market_cap", "price", "pct_change_1d", "pct_change_5d", "avg_volume"]

# Trading bot configuration
ACCOUNT_SIZE = 200  # Account size in dollars
MAX_POSITION_SIZE = 0.25  # Maximum position size as fraction of account
STOP_LOSS_PERCENTAGE = 0.05  # 5% stop-loss on every trade

# Strategy settings
STRATEGIES = ["proven_winners", "real_time", "hybrid"]
DEFAULT_STRATEGY = "hybrid"

# Sector classification for scoring
CANNABIS_SYMBOLS = ['ACB', 'CGC', 'HEXO', 'TLRY', 'SNDL', 'APHA', 'CRON']
CLEAN_ENERGY_SYMBOLS = ['PLUG', 'FCEL', 'BLDP', 'BEEM', 'HYSR', 'SUNW']
BIOTECH_SYMBOLS = ['OCGN', 'DRUG']

# Proven winners based on actual trading history
PROVEN_WINNERS = [
    {'symbol': 'ATAI', 'reason': 'Current winner (+18.66% return)', 'confidence': 'High', 'sector': 'Cannabis'},
    {'symbol': 'SNDL', 'reason': 'Current position (+0.61% return)', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'CGC', 'reason': 'Cannabis sector, potential opportunity', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'HEXO', 'reason': 'Cannabis sector, high volume', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'TLRY', 'reason': 'Cannabis sector, established player', 'confidence': 'Medium', 'sector': 'Cannabis'},
    {'symbol': 'PLUG', 'reason': 'Clean energy, similar to FCEL', 'confidence': 'Medium', 'sector': 'Clean Energy'},
    {'symbol': 'OCGN', 'reason': 'Biotech, similar to DRUG pattern', 'confidence': 'Low', 'sector': 'Biotech'}
]

# Date format for reports
DATE_FORMAT = "%Y-%m-%d"

# Rich console styling
STYLE_SUCCESS = "green"
STYLE_ERROR = "red"
STYLE_WARNING = "yellow"
STYLE_INFO = "blue"
STYLE_HEADER = "bold cyan" 