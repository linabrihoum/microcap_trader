"""
Configuration settings for the microcap trading system.
"""

# File paths
PORTFOLIO_FILE = "portfolio.csv"
CANDIDATES_FILE = "candidates.csv"
DAILY_REPORT_FILE = "daily_report.md"

# Market cap threshold (in billions)
MAX_MARKET_CAP = 2.0

# Number of random microcap stocks to evaluate daily
CANDIDATES_COUNT = 30

# Minimum volume threshold for candidates (in thousands)
MIN_VOLUME_THRESHOLD = 100

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