#!/usr/bin/env python3
"""
Microcap Trading System - Single File Version
A comprehensive system for tracking microcap stocks and portfolio management.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import argparse
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configuration
PORTFOLIO_FILE = "portfolio.csv"
CANDIDATES_FILE = "candidates.csv"
DAILY_REPORT_FILE = "daily_report.md"
MAX_MARKET_CAP = 2.0  # $2B
CANDIDATES_COUNT = 30
MIN_VOLUME_THRESHOLD = 100  # 100K shares

# Rich console styling
STYLE_SUCCESS = "green"
STYLE_ERROR = "red"
STYLE_WARNING = "yellow"
STYLE_INFO = "blue"
STYLE_HEADER = "bold cyan"

console = Console()


class MicrocapTrader:
    """Single-file microcap trading system."""
    
    def __init__(self):
        self.portfolio_file = PORTFOLIO_FILE
        self.candidates_file = CANDIDATES_FILE
        self.report_file = DAILY_REPORT_FILE
    
    def load_portfolio(self):
        """Load portfolio data from CSV file."""
        if not os.path.exists(self.portfolio_file):
            df = pd.DataFrame(columns=["symbol", "shares", "buy_price", "current_price", "pnl"])
            df.to_csv(self.portfolio_file, index=False)
            return df
        
        try:
            df = pd.read_csv(self.portfolio_file)
            for col in ["symbol", "shares", "buy_price", "current_price", "pnl"]:
                if col not in df.columns:
                    df[col] = 0.0
            return df
        except Exception as e:
            console.print(f"Error loading portfolio: {e}", style=STYLE_ERROR)
            return pd.DataFrame(columns=["symbol", "shares", "buy_price", "current_price", "pnl"])
    
    def save_portfolio(self, df):
        """Save portfolio data to CSV file."""
        try:
            df.to_csv(self.portfolio_file, index=False)
            return True
        except Exception as e:
            console.print(f"Error saving portfolio: {e}", style=STYLE_ERROR)
            return False
    
    def load_candidates(self):
        """Load candidates data from CSV file."""
        if not os.path.exists(self.candidates_file):
            return pd.DataFrame(columns=["symbol", "market_cap", "price", "pct_change_1d", "pct_change_5d", "avg_volume"])
        
        try:
            return pd.read_csv(self.candidates_file)
        except Exception as e:
            console.print(f"Error loading candidates: {e}", style=STYLE_ERROR)
            return pd.DataFrame(columns=["symbol", "market_cap", "price", "pct_change_1d", "pct_change_5d", "avg_volume"])
    
    def save_candidates(self, df):
        """Save candidates data to CSV file."""
        try:
            df.to_csv(self.candidates_file, index=False)
            return True
        except Exception as e:
            console.print(f"Error saving candidates: {e}", style=STYLE_ERROR)
            return False
    
    def add_to_portfolio(self, symbol, shares, buy_price):
        """Add a new position to the portfolio."""
        portfolio = self.load_portfolio()
        
        if symbol in portfolio['symbol'].values:
            console.print(f"Symbol {symbol} already exists in portfolio", style=STYLE_WARNING)
            return False
        
        new_row = {
            'symbol': symbol,
            'shares': shares,
            'buy_price': buy_price,
            'current_price': buy_price,
            'pnl': 0.0
        }
        
        portfolio = pd.concat([portfolio, pd.DataFrame([new_row])], ignore_index=True)
        return self.save_portfolio(portfolio)
    
    def remove_from_portfolio(self, symbol):
        """Remove a position from the portfolio."""
        portfolio = self.load_portfolio()
        portfolio = portfolio[portfolio['symbol'] != symbol]
        return self.save_portfolio(portfolio)
    
    def update_portfolio_prices(self, price_data):
        """Update current prices and PnL for portfolio holdings."""
        portfolio = self.load_portfolio()
        
        for index, row in portfolio.iterrows():
            symbol = row['symbol']
            if symbol in price_data:
                current_price = price_data[symbol]
                shares = row['shares']
                buy_price = row['buy_price']
                pnl = (current_price - buy_price) * shares
                
                portfolio.at[index, 'current_price'] = current_price
                portfolio.at[index, 'pnl'] = pnl
        
        return self.save_portfolio(portfolio)
    
    def get_microcap_candidates(self):
        """Get microcap stock candidates."""
        # Sample microcap stocks (expand this list)
        microcap_symbols = [
            'IWM', 'VTWO', 'IJR', 'IWC',  # Microcap ETFs
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',  # For testing
            'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
            'CRM', 'ADBE', 'PYPL', 'NKE', 'DIS'
        ]
        
        candidates = []
        
        for symbol in microcap_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                market_cap = info.get('marketCap', 0)
                if market_cap == 0:
                    continue
                
                market_cap_billions = market_cap / 1e9
                
                if market_cap_billions <= MAX_MARKET_CAP:
                    hist = ticker.history(period='5d')
                    if len(hist) >= 5:
                        current_price = hist['Close'].iloc[-1]
                        price_1d_ago = hist['Close'].iloc[-2]
                        price_5d_ago = hist['Close'].iloc[0]
                        
                        pct_change_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100
                        pct_change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
                        avg_volume = hist['Volume'].mean() / 1000
                        
                        if avg_volume >= MIN_VOLUME_THRESHOLD:
                            candidates.append({
                                'symbol': symbol,
                                'market_cap': market_cap_billions,
                                'price': current_price,
                                'pct_change_1d': pct_change_1d,
                                'pct_change_5d': pct_change_5d,
                                'avg_volume': avg_volume
                            })
            except Exception as e:
                console.print(f"Error processing {symbol}: {e}", style=STYLE_ERROR)
                continue
        
        df = pd.DataFrame(candidates)
        if len(df) > CANDIDATES_COUNT:
            df = df.sample(n=CANDIDATES_COUNT, random_state=42)
        
        return df.sort_values('pct_change_5d', ascending=False)
    
    def get_current_prices(self, symbols):
        """Get current prices for a list of symbols."""
        price_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if len(hist) > 0:
                    price_data[symbol] = hist['Close'].iloc[-1]
            except Exception as e:
                console.print(f"Error getting price for {symbol}: {e}", style=STYLE_ERROR)
                continue
        
        return price_data
    
    def generate_daily_report(self, portfolio_df, candidates_df):
        """Generate daily report in Markdown format."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""# Microcap Trading Daily Report
**Date:** {today}

## Portfolio Summary

"""
        
        if len(portfolio_df) > 0:
            total_value = (portfolio_df['shares'] * portfolio_df['current_price']).sum()
            total_pnl = portfolio_df['pnl'].sum()
            total_invested = (portfolio_df['shares'] * portfolio_df['buy_price']).sum()
            pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            report += f"""
- **Total Portfolio Value:** ${total_value:,.2f}
- **Total P&L:** ${total_pnl:,.2f} ({pnl_percentage:+.2f}%)
- **Total Invested:** ${total_invested:,.2f}
- **Number of Positions:** {len(portfolio_df)}

### Portfolio Holdings

| Symbol | Shares | Buy Price | Current Price | P&L | P&L % |
|--------|--------|-----------|---------------|-----|-------|
"""
            
            for _, row in portfolio_df.iterrows():
                pnl_pct = ((row['current_price'] - row['buy_price']) / row['buy_price'] * 100)
                report += f"| {row['symbol']} | {row['shares']:,.0f} | ${row['buy_price']:.2f} | ${row['current_price']:.2f} | ${row['pnl']:,.2f} | {pnl_pct:+.2f}% |\n"
            
            portfolio_df_sorted = portfolio_df.sort_values('pnl', ascending=False)
            
            report += f"""

### Top Gainers
"""
            for _, row in portfolio_df_sorted.head(3).iterrows():
                pnl_pct = ((row['current_price'] - row['buy_price']) / row['buy_price'] * 100)
                report += f"- **{row['symbol']}**: ${row['pnl']:,.2f} ({pnl_pct:+.2f}%)\n"
            
            report += f"""

### Top Losers
"""
            for _, row in portfolio_df_sorted.tail(3).iterrows():
                pnl_pct = ((row['current_price'] - row['buy_price']) / row['buy_price'] * 100)
                report += f"- **{row['symbol']}**: ${row['pnl']:,.2f} ({pnl_pct:+.2f}%)\n"
        else:
            report += "No positions in portfolio.\n"
        
        report += f"""

## Microcap Candidates Analysis

"""
        
        if len(candidates_df) > 0:
            report += f"**Total Candidates Analyzed:** {len(candidates_df)}\n\n"
            
            top_candidates = candidates_df.head(10)
            
            report += f"""

### Top Candidates (5-Day Performance)

| Symbol | Market Cap (B) | Price | 1D Change | 5D Change | Avg Volume (K) |
|--------|----------------|-------|-----------|-----------|----------------|
"""
            
            for _, row in top_candidates.iterrows():
                report += f"| {row['symbol']} | ${row['market_cap']:.2f}B | ${row['price']:.2f} | {row['pct_change_1d']:+.2f}% | {row['pct_change_5d']:+.2f}% | {row['avg_volume']:,.0f} |\n"
            
            volume_leaders = candidates_df.nlargest(5, 'avg_volume')
            
            report += f"""

### High Volume Candidates

| Symbol | Market Cap (B) | Price | Avg Volume (K) |
|--------|----------------|-------|----------------|
"""
            
            for _, row in volume_leaders.iterrows():
                report += f"| {row['symbol']} | ${row['market_cap']:.2f}B | ${row['price']:.2f} | {row['avg_volume']:,.0f} |\n"
        else:
            report += "No candidates found.\n"
        
        report += f"""

## Market Insights

- **Analysis Date:** {today}
- **Market Cap Threshold:** $2B
- **Minimum Volume:** 100K shares
- **Candidates Analyzed:** {len(candidates_df)}

### Recommendations

1. **High Momentum:** Focus on stocks with strong 5-day performance
2. **Volume Analysis:** Consider stocks with increasing volume
3. **Risk Management:** Diversify across different sectors
4. **Entry Timing:** Consider buying on pullbacks for strong performers

---
*Report generated by Microcap Trader System*
"""
        
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except Exception as e:
            console.print(f"Error saving report: {e}", style=STYLE_ERROR)
            return False
    
    def run_daily_update(self):
        """Run the daily update process."""
        console.print(Panel.fit("🔄 Running Daily Update", style=STYLE_HEADER))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task1 = progress.add_task("Loading portfolio...", total=None)
            portfolio = self.load_portfolio()
            progress.update(task1, description="Portfolio loaded")
            
            if len(portfolio) > 0:
                task2 = progress.add_task("Updating portfolio prices...", total=None)
                symbols = portfolio['symbol'].tolist()
                price_data = self.get_current_prices(symbols)
                self.update_portfolio_prices(price_data)
                portfolio = self.load_portfolio()
                progress.update(task2, description="Portfolio prices updated")
            
            task3 = progress.add_task("Finding microcap candidates...", total=None)
            candidates = self.get_microcap_candidates()
            self.save_candidates(candidates)
            progress.update(task3, description=f"Found {len(candidates)} candidates")
            
            task4 = progress.add_task("Generating daily report...", total=None)
            self.generate_daily_report(portfolio, candidates)
            progress.update(task4, description="Daily report generated")
        
        console.print(f"✅ Daily update completed successfully!", style=STYLE_SUCCESS)
        self.show_summary(portfolio, candidates)
    
    def show_summary(self, portfolio, candidates):
        """Show a summary of the current state."""
        if len(portfolio) > 0:
            total_value = (portfolio['shares'] * portfolio['current_price']).sum()
            total_pnl = portfolio['pnl'].sum()
            total_invested = (portfolio['shares'] * portfolio['buy_price']).sum()
            pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            portfolio_table = Table(title="Portfolio Summary")
            portfolio_table.add_column("Symbol", style="cyan")
            portfolio_table.add_column("Shares", justify="right")
            portfolio_table.add_column("Buy Price", justify="right")
            portfolio_table.add_column("Current Price", justify="right")
            portfolio_table.add_column("P&L", justify="right")
            portfolio_table.add_column("P&L %", justify="right")
            
            for _, row in portfolio.iterrows():
                pnl_pct = ((row['current_price'] - row['buy_price']) / row['buy_price'] * 100)
                pnl_color = "green" if row['pnl'] >= 0 else "red"
                portfolio_table.add_row(
                    row['symbol'],
                    f"{row['shares']:,.0f}",
                    f"${row['buy_price']:.2f}",
                    f"${row['current_price']:.2f}",
                    f"${row['pnl']:,.2f}",
                    f"{pnl_pct:+.2f}%",
                    style=pnl_color
                )
            
            console.print(portfolio_table)
            console.print(f"Total Value: ${total_value:,.2f} | P&L: ${total_pnl:,.2f} ({pnl_percentage:+.2f}%)", style=STYLE_INFO)
        
        if len(candidates) > 0:
            candidates_table = Table(title="Top Candidates")
            candidates_table.add_column("Symbol", style="cyan")
            candidates_table.add_column("Market Cap", justify="right")
            candidates_table.add_column("Price", justify="right")
            candidates_table.add_column("5D Change", justify="right")
            candidates_table.add_column("Volume (K)", justify="right")
            
            for _, row in candidates.head(5).iterrows():
                change_color = "green" if row['pct_change_5d'] >= 0 else "red"
                candidates_table.add_row(
                    row['symbol'],
                    f"${row['market_cap']:.2f}B",
                    f"${row['price']:.2f}",
                    f"{row['pct_change_5d']:+.2f}%",
                    f"{row['avg_volume']:,.0f}",
                    style=change_color
                )
            
            console.print(candidates_table)
    
    def add_position(self, symbol, shares, buy_price):
        """Add a new position to the portfolio."""
        console.print(f"Adding position: {symbol} - {shares} shares at ${buy_price:.2f}", style=STYLE_INFO)
        
        if self.add_to_portfolio(symbol, shares, buy_price):
            console.print(f"✅ Position added successfully!", style=STYLE_SUCCESS)
        else:
            console.print(f"❌ Failed to add position", style=STYLE_ERROR)
    
    def remove_position(self, symbol):
        """Remove a position from the portfolio."""
        console.print(f"Removing position: {symbol}", style=STYLE_INFO)
        
        if self.remove_from_portfolio(symbol):
            console.print(f"✅ Position removed successfully!", style=STYLE_SUCCESS)
        else:
            console.print(f"❌ Failed to remove position", style=STYLE_ERROR)
    
    def show_portfolio(self):
        """Show current portfolio."""
        portfolio = self.load_portfolio()
        
        if len(portfolio) == 0:
            console.print("No positions in portfolio.", style=STYLE_WARNING)
            return
        
        self.show_summary(portfolio, pd.DataFrame())
    
    def show_candidates(self):
        """Show current candidates."""
        candidates = self.load_candidates()
        
        if len(candidates) == 0:
            console.print("No candidates found. Run daily update first.", style=STYLE_WARNING)
            return
        
        self.show_summary(pd.DataFrame(), candidates)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Microcap Trading System - Single File Version")
    parser.add_argument("command", choices=["update", "add", "remove", "portfolio", "candidates"], 
                       help="Command to execute")
    parser.add_argument("--symbol", help="Stock symbol")
    parser.add_argument("--shares", type=float, help="Number of shares")
    parser.add_argument("--price", type=float, help="Buy price")
    
    args = parser.parse_args()
    
    trader = MicrocapTrader()
    
    if args.command == "update":
        trader.run_daily_update()
    elif args.command == "add":
        if not all([args.symbol, args.shares, args.price]):
            console.print("Error: --symbol, --shares, and --price are required for add command", style=STYLE_ERROR)
            return
        trader.add_position(args.symbol, args.shares, args.price)
    elif args.command == "remove":
        if not args.symbol:
            console.print("Error: --symbol is required for remove command", style=STYLE_ERROR)
            return
        trader.remove_position(args.symbol)
    elif args.command == "portfolio":
        trader.show_portfolio()
    elif args.command == "candidates":
        trader.show_candidates()


if __name__ == "__main__":
    main() 