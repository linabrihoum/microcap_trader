# Enhanced Microcap Trading System

A production-ready microcap stock trading system with intelligent scoring, position sizing, and risk management. Inspired by [
LuckyOne7777 ChatGPT Micro Cap Experiment](https://github.com/LuckyOne7777/ChatGPT-Micro-Cap-Experiment).

## 🚀 Features

- **Intelligent Stock Scoring** (0-100): Multi-factor analysis including momentum, volume, market cap, and volatility
- **Position Sizing**: Risk-adjusted position sizing based on stock score and volatility
- **Multiple Data Sources**: Polygon.io, Finnhub, and yfinance fallback
- **Enhanced Reporting**: Daily reports with actionable insights and recommendations
- **Risk Management**: Built-in volatility filters and market cap optimization
- **Production Security**: Secure API key handling with environment variables

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

The system works without API keys using yfinance fallback, but for enhanced data quality:

### Polygon.io (Recommended)
- Sign up at: https://polygon.io/
- Free tier: 5 API calls per minute
- Add to `.env`: `POLYGON_API_KEY=your_key_here`

### Finnhub
- Sign up at: https://finnhub.io/
- Free tier: 60 API calls per minute
- Add to `.env`: `FINNHUB_API_KEY=your_key_here`

## 🎯 Usage

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
├── config.py                    # Configuration settings
├── portfolio.csv                 # Portfolio data
├── candidates.csv                # Candidate stocks
├── daily_report.md              # Daily reports
├── requirements.txt              # Dependencies
├── env_template.txt             # Environment template
├── PRODUCTION_CHECKLIST.md      # Production guidelines
├── weekly_research/             # Weekly research reports
│   ├── weekly_research_generator.py  # Report generator
│   ├── run_weekly_report.bat    # Windows batch script
│   ├── run_weekly_report.ps1    # PowerShell script
│   ├── report_generator.py      # Daily report generator
│   └── README.md                # Research documentation
├── machine_learning/            # ML trading bots & analysis
│   ├── advanced_trading_bot.py # Advanced trading bot with multiple strategies
│   ├── trading_recommendations.py # Simple recommendations
│   ├── trading_analysis.py     # P&L analysis
│   ├── trading_history_manager.py # History management
│   ├── trading_history.csv     # Trading data
│   └── README.md               # ML documentation
└── README.md                    # This file
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

---

**Disclaimer**: This system is for educational purposes. Always do your own research and consider consulting with a financial advisor before making investment decisions.
