# Machine Learning Trading System

This folder contains all machine learning and trading bot components that learn from your trading history and provide intelligent recommendations.

## 📁 Files Overview

### 🤖 Trading Bots
- **`advanced_trading_bot.py`** - Advanced trading bot with multiple strategies and enhanced learning
- **`trading_recommendations.py`** - Simple recommendations based on proven trading patterns

### 📊 Analysis Tools
- **`trading_analysis.py`** - Comprehensive P&L analysis with realized/unrealized gains
- **`trading_history_manager.py`** - Trading history management and portfolio tracking

### 📈 Data Files
- **`trading_history.csv`** - Complete trading history with wins/losses tracking

## 🎯 Key Features

### Learning from Trading History
- Analyzes your past trades to identify successful patterns
- Calculates win rates, average gains/losses, and hold periods
- Identifies best and worst performing stocks

### Pattern Recognition
- **Cannabis Sector Success**: ACB (+402%), ATAI (+18.66%)
- **Price Range Optimization**: $1-$25 sweet spot
- **Timing Analysis**: Post-noon momentum trades
- **Risk Management**: 5% stop-loss on every trade

### Trading Recommendations
- Focuses on proven winners from your history
- Avoids duplicate holdings
- Provides position sizing for $200 account
- Includes stop-loss calculations

## 🚀 Usage

### Run Advanced Trading Bot
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

### Get Recommendations
```bash
python machine_learning/trading_recommendations.py
```

### Analyze Trading History
```bash
python machine_learning/trading_analysis.py
```

### Manage Trading History
```bash
python machine_learning/trading_history_manager.py summary
python machine_learning/trading_history_manager.py open
python machine_learning/trading_history_manager.py add --symbol AAPL --shares 10 --price 150.00
python machine_learning/trading_history_manager.py close --symbol AAPL --price 155.00
```

## 📊 Learned Patterns

### ✅ What Works
- Cannabis sector (ACB: +402%, ATAI: +18.66%)
- Short-term holds (1-7 days for winners)
- High volume stocks
- Post-noon momentum trades
- Price range $1-$25 (your sweet spot)

### ❌ What Doesn't Work
- Low volume setups (DRUG losses)
- Holding past failed momentum
- Not setting stop-losses
- Biotech without strong volume (DRUG)

## 🎯 Trading Strategy

### Recommended Approach
- Focus on cannabis sector (ACB, CGC, HEXO, TLRY)
- Set 5% stop-loss immediately
- Exit on momentum breakdown
- Trade after 12 PM EST
- Maximum 25% of account per trade

### Account Management
- **Account Size**: $200
- **Max Position Size**: 25% ($50 per trade)
- **Stop-Loss**: 5% on every trade
- **Trading Time**: After 12 PM EST

## 📈 Performance Metrics

### Current Statistics
- **Win Rate**: 40% (2 wins, 3 losses)
- **Average Win**: +$88.83
- **Average Loss**: -$1.08
- **Risk/Reward Ratio**: 82:1 (exceptional!)
- **Best Performer**: ACB (+402% return in 12 days)

### Historical Analysis
- **Total Realized P&L**: +$174.41
- **Total Unrealized P&L**: +$8.10
- **Overall ROI**: +76.33%
- **Total Invested**: $239.11

## 🔧 Technical Details

### Dependencies
- `pandas` - Data analysis
- `yfinance` - Market data
- `rich` - Terminal output
- `numpy` - Numerical computations

### Data Sources
- **Trading History**: `trading_history.csv`
- **Current Portfolio**: `portfolio.csv`
- **Market Data**: Yahoo Finance API

### File Structure
```
machine_learning/
├── README.md                    # This documentation
├── advanced_trading_bot.py     # Advanced trading bot with multiple strategies
├── trading_recommendations.py  # Simple recommendations
├── trading_analysis.py         # P&L analysis
├── trading_history_manager.py  # History management
└── trading_history.csv         # Trading data
```

## ⚠️ Important Notes

### Risk Management
- Always set stop-loss immediately after buying
- Never hold past failed momentum
- Exit on breakdowns (learned from your losses)
- Focus on post-noon momentum trades
- Avoid low-volume setups

### Trading Rules
- Only trade U.S. microcap stocks (<$2B market cap)
- Trade after 12 PM EST
- Focus on intraday momentum
- Use whole-share trades (no fractional shares)
- Set strict 5% stop-loss on every trade

### Performance Tracking
- Track all wins and losses in `trading_history.csv`
- Monitor realized vs unrealized gains
- Analyze patterns for continuous improvement
- Update recommendations based on new data

---

**Disclaimer**: This system is for educational purposes. Always do your own research and consider consulting with a financial advisor before making investment decisions. 