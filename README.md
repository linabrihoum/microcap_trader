# Microcap Trading System

A production-ready microcap stock trading system with intelligent scoring, position sizing, and risk management. Inspired by [
LuckyOne7777 ChatGPT Micro Cap Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment).

## 🚀 Features

- **Intelligent Stock Scoring** (0-100): Multi-factor analysis including momentum, volume, market cap, and volatility
- **Position Sizing**: Risk-adjusted position sizing based on stock score and volatility
- **Robust Data Sources**: Polygon.io (primary) → Finnhub (secondary) → yfinance (fallback) → simulated data (emergency)
- **Real-Time Caching System**: Smart TTL management with 60-80% API call reduction
- **Batch Processing**: High-performance parallel processing for large datasets (2-5x faster)
- **Enhanced Reporting**: Daily reports with actionable insights and recommendations
- **Risk Management**: Built-in volatility filters and market cap optimization
- **Production Security**: Secure API key handling with environment variables
- **Automated Workflows**: GitHub Actions for daily/weekly research and ML training
- **Comprehensive Error Handling**: Robust error management with retry logic and fallbacks
- **Data Validation**: Pydantic models for type safety and data integrity
- **Modular Architecture**: Organized codebase with utilities, validation, caching, and ML components

## 📋 Requirements

- Python 3.8+
- Required packages (see `requirements.txt`)

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd microcap_trader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the template
   cp env_template.txt .env
   
   # Edit .env with your API keys (optional)
   nano .env
   ```

## 🔐 API Keys (Optional)

The system uses a robust fallback chain for data fetching, ensuring reliability even when APIs are unavailable:

### Data Source Priority
1. **Polygon.io** (Primary) - Most reliable and comprehensive
2. **Finnhub** (Secondary) - Good alternative with different rate limits
3. **yfinance** (Fallback) - Always available, no API key required
4. **Simulated Data** (Emergency) - Generated when all APIs fail

### Polygon.io (Recommended)
- Sign up at: https://polygon.io/
- Free tier: 5 API calls per minute
- **Best for**: Real-time data, comprehensive market cap info
- Add to `.env`: `POLYGON_API_KEY=your_key_here`

### Finnhub
- Sign up at: https://finnhub.io/
- Free tier: 60 API calls per minute
- **Best for**: Alternative data source, different rate limits
- Add to `.env`: `FINNHUB_API_KEY=your_key_here`

### yfinance (Fallback)
- **No API key required** - Always available
- **Best for**: Backup when other APIs hit rate limits
- **Limitations**: Rate limits, less comprehensive data
- **Automatic**: Used automatically when primary APIs fail

## 🤖 GitHub Actions Automation

The system includes automated workflows that run daily and weekly research, ML training, and chart updates.

### Setting Up GitHub Actions

**Add Repository Secrets**
   Navigate to **Settings** → **Secrets and variables** → **Actions** and add:

   **Required Secrets:**
   ```
   POLYGON_API_KEY=your_polygon_api_key_here
   FINNHUB_API_KEY=your_finnhub_api_key_here
   ```

4. **Configure Workflow Permissions**
   - Go to **Settings** → **Actions** → **General**
   - Under "Workflow permissions", select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

### Automated Workflows

The system includes three automated workflows:

#### 1. Daily Research (Runs at 11 AM EST)
- **Purpose**: Finds potential microcap candidates daily
- **Schedule**: `0 16 * * 1-5` (Monday-Friday at 4 PM UTC = 11 AM EST)
- **Actions**:
  - Scans microcap stocks across sectors
  - Saves candidates to `daily_research/` folder
  - Updates main `data/candidates.csv`
  - Generates daily summary reports

#### 2. Weekly Research (Runs every Friday at 4 PM EST)
- **Purpose**: Comprehensive weekly analysis and ML training
- **Schedule**: `0 21 * * 5` (Friday at 9 PM UTC = 4 PM EST)
- **Actions**:
  - Aggregates daily research data
  - Generates comprehensive weekly report
  - Runs ML training on historical data
  - Updates portfolio value chart
  - Commits results to repository

#### 3. ML Training (Runs at assistant's discretion)
- **Purpose**: Continuous improvement of trading bot
- **Schedule**: Manual trigger or weekly
- **Actions**:
  - Analyzes trading patterns
  - Updates ML models
  - Generates training insights
  - Saves results to `machine_learning/training_results/`



**Debugging Steps:**
1. Go to **Actions** → **Select workflow** → **View logs**
2. Check the specific step that failed
3. Review error messages and context
4. Test locally with same inputs
5. Update secrets or configuration as needed

### Data Source Troubleshooting

**API Rate Limits:**
- The system automatically switches to fallback sources
- Check logs to see which data source was used
- Consider upgrading API plans for better reliability

**Fallback Chain:**
- Polygon.io → Finnhub → yfinance → Simulated data
- Each source has different rate limits and data quality
- System logs show which source provided the data

### Local vs. GitHub Actions

**Local Development:**
```bash
# Run daily research locally
python daily_research_generator.py

# Run weekly research locally
python weekly_research/weekly_research_generator.py

# Run ML training locally
python machine_learning/advanced_trading_bot.py --training-mode
```

**GitHub Actions:**
- Automatic scheduling
- No local resources required
- Consistent environment
- Version control integration
- Email notifications on completion/failure

## 🎯 Usage

### Data Source Fallback System

The system automatically handles API failures and rate limits:

1. **Tries Polygon.io first** - Best data quality
2. **Falls back to Finnhub** - Different rate limits
3. **Uses yfinance** - Always available, no API key needed
4. **Generates simulated data** - Emergency fallback

**No configuration needed** - The system automatically detects failures and switches sources.

### Daily Update
```bash
python enhanced_microcap_trader.py update
```

### Add Position
```bash
python enhanced_microcap_trader.py add --symbol OCGN --shares 100 --price 1.08
```

### Analyze Position Size
```bash
python enhanced_microcap_trader.py analyze --symbol OCGN
```

### View Portfolio
```bash
python enhanced_microcap_trader.py portfolio
```

### View Candidates
```bash
python enhanced_microcap_trader.py candidates
```

### Generate Weekly Research Report
```bash
python weekly_research/weekly_research_generator.py
```

## 📊 Scoring System

The system uses a comprehensive 0-100 scoring algorithm:

- **Momentum (30%)**: 1-day and 5-day price changes
- **Volume (25%)**: Trading volume for liquidity assessment
- **Market Cap (20%)**: Optimization for $100M-$500M range
- **Price Range (15%)**: Ideal $1-$10 microcap range
- **Volatility (10%)**: Bonus for high positive volatility

## 💰 Position Sizing

Automatic position sizing based on:
- **Score ≥ 80**: 5% of capital
- **Score ≥ 60**: 3% of capital
- **Score ≥ 40**: 2% of capital
- **Score < 40**: 1% of capital

Volatility adjustments reduce position size for high volatility stocks.

## 🛡️ Risk Management

- **Stop Losses**: 5-8% below entry
- **Profit Targets**: 15-20% gains
- **Diversification**: 3-5 positions recommended
- **Market Cap Filter**: < $2B microcap focus
- **Volume Requirements**: Minimum liquidity thresholds

## 📁 File Structure

```
microcap_trader/
├── enhanced_microcap_trader.py  # Main trading system
├── enhanced_data_manager.py      # Data management
├── daily_research_generator.py   # Daily research automation
├── weekly_aggregator.py         # Weekly data aggregation
├── config.py                    # Configuration settings
├── requirements.txt              # Dependencies
├── env_template.txt             # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── data/                        # Core data files
│   ├── portfolio.csv            # Portfolio data
│   ├── candidates.csv           # Candidate stocks
│   └── daily_report.md         # Daily reports
├── utilities/                   # Utility modules
│   ├── error_handler.py        # Error handling system
│   └── README.md               # Utilities documentation
├── validation/                  # Data validation system
│   ├── data_models.py          # Pydantic data models
│   ├── data_validator.py       # Validation manager
│   └── README.md               # Validation documentation
├── caching/                    # Real-time caching system
│   ├── cache_manager.py        # High-level cache interface
│   ├── real_time_cache.py      # Core caching engine
│   ├── background_refresh.py   # Background refresh system
│   ├── cache_config.py         # Cache configuration
│   └── README.md               # Caching documentation
├── machine_learning/            # ML trading bots & analysis
│   ├── advanced_trading_bot.py # Advanced trading bot
│   ├── trading_recommendations.py # Trading recommendations
│   ├── trading_analysis.py     # P&L analysis
│   ├── trading_history_manager.py # History management
│   ├── trading_history.csv     # Trading data
│   ├── portfolio_value_chart.py # Portfolio value chart
│   ├── training_results/       # ML training results
│   └── README.md               # ML documentation
├── daily_research/             # Daily research data
│   ├── daily_candidates_*.csv  # Daily candidate files
│   ├── daily_candidates_*.json # Daily candidate JSON
│   └── daily_summary_*.md     # Daily summary reports
├── weekly_research/            # Weekly research reports
│   ├── weekly_research_generator.py # Report generator
│   ├── ml_insights_generator.py # ML insights
│   ├── summaries/              # Weekly summaries
│   └── README.md               # Research documentation
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       └── trading_automation.yml # Automation workflows
└── trading_system.log          # System logs
```

## ⚡ Real-Time Caching System

The system includes a sophisticated real-time caching system that balances data freshness with API efficiency:

### Smart TTL Strategy
| **Use Case** | **TTL** | **Priority** | **Real-Time** |
|--------------|---------|--------------|---------------|
| Active Positions | 30 seconds | High | ✅ |
| Watchlist | 2 minutes | Medium | ✅ |
| High Volume | 1 minute | High | ✅ |
| Research | 5 minutes | Low | ❌ |
| Historical | 15 minutes | Low | ❌ |

### Key Features
- **Dynamic Invalidation**: Cache invalidated on >2% price changes or >50% volume spikes
- **Background Refresh**: Non-blocking updates with priority queuing
- **60-80% API Reduction**: Significant cost savings while maintaining accuracy
- **Real-Time for Trading**: Active positions get fresh data for P&L calculations
- **Cached for Analysis**: Research and ML training use cached data

### Usage
```python
from enhanced_data_manager import EnhancedDataManager

# Initialize with caching enabled
data_manager = EnhancedDataManager(enable_caching=True)

# Get real-time data for active trading
trading_data = data_manager.get_stock_data_for_trading('AAPL')

# Get cached data for analysis
analysis_data = data_manager.get_stock_data('TSLA')

# Set active positions for real-time updates
data_manager.set_active_positions(['AAPL', 'TSLA'])

# View cache statistics
data_manager.display_cache_stats()
```

## 🔍 Daily Report Features

- **Portfolio Summary**: Total value, P&L, top gainers/losers
- **Top Scored Candidates**: Best opportunities by score
- **High Momentum**: Top performers by 1-day change
- **Trading Recommendations**: Strong buy signals
- **Risk Management Tips**: Stop losses and profit targets

## 📊 Weekly Research Reports

Comprehensive weekly analysis available in the `weekly_research/` folder:

- **Portfolio Performance**: Detailed analysis of all positions
- **Individual Stock Analysis**: Technical and fundamental analysis
- **Sector Analysis**: Market sentiment and sector rotation
- **Trading Recommendations**: Actionable advice for each position
- **Risk Management**: Stop loss and take profit targets
- **Next Week's Focus**: Strategic planning and priorities

**Generate weekly report:**
```bash
python weekly_research/weekly_research_generator.py
```

## 🤖 Machine Learning Trading Bots

Advanced trading bots that learn from your trading history and provide intelligent recommendations:

- **Pattern Recognition**: Analyzes your successful trades to identify winning patterns
- **Risk Management**: Implements 5% stop-loss on every trade
- **Position Sizing**: Optimized for $200 account with 25% max position size
- **Sector Focus**: Cannabis sector has been your best performer (ACB: +402%)

**Run advanced trading bot:**
```bash
# Default hybrid strategy
python machine_learning/advanced_trading_bot.py

# Specific strategies
python machine_learning/advanced_trading_bot.py --strategy proven_winners
python machine_learning/advanced_trading_bot.py --strategy real_time
python machine_learning/advanced_trading_bot.py --strategy hybrid

# Custom account settings
python machine_learning/advanced_trading_bot.py --account-size 300 --max-position 0.20
```

**Get recommendations:**
```bash
python machine_learning/trading_recommendations.py
```

**Analyze trading history:**
```bash
python machine_learning/trading_analysis.py
```

## ⚠️ Important Notes

1. **Not Financial Advice**: This system is for educational purposes only
2. **Risk Warning**: Microcap stocks are highly volatile and risky
3. **Paper Trading**: Consider testing with paper trading first
4. **API Limits**: Be aware of API rate limits for production use
5. **Data Accuracy**: Verify all data before making trading decisions

## 🚀 Getting Started

1. **First Run:**
   ```bash
   python enhanced_microcap_trader.py update
   ```

2. **Review Candidates:**
   ```bash
   python enhanced_microcap_trader.py candidates
   ```

3. **Analyze a Stock:**
   ```bash
   python enhanced_microcap_trader.py analyze --symbol OCGN
   ```

4. **Add a Position:**
   ```bash
   python enhanced_microcap_trader.py add --symbol OCGN --shares 100 --price 1.08
   ```

## 🔧 System Components

### Core Modules
- **`enhanced_microcap_trader.py`**: Main trading system with portfolio management
- **`enhanced_data_manager.py`**: Robust data fetching with fallback chain (Polygon → Finnhub → yfinance → simulated)
- **`daily_research_generator.py`**: Automated daily candidate research with error handling
- **`weekly_aggregator.py`**: Weekly data aggregation and analysis

### Utilities
- **`utilities/error_handler.py`**: Comprehensive error handling and logging
- **`validation/`**: Data validation with Pydantic models
- **`config.py`**: Centralized configuration management

### Machine Learning
- **`machine_learning/advanced_trading_bot.py`**: ML-powered trading recommendations
- **`machine_learning/trading_analysis.py`**: Performance analysis and insights
- **`machine_learning/portfolio_value_chart.py`**: Portfolio visualization

### Automation
- **`.github/workflows/trading_automation.yml`**: GitHub Actions automation
- **`weekly_research/`**: Weekly research and analysis
- **`daily_research/`**: Daily candidate tracking

---

**Disclaimer**: This system is for educational purposes. Always do your own research and consider consulting with a financial advisor before making investment decisions.
