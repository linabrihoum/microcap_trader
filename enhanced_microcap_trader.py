#!/usr/bin/env python3
"""
Enhanced Microcap Trading System
Uses Polygon.io and Finnhub APIs when available, with yfinance fallback
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

# Import our enhanced data manager
from enhanced_data_manager import EnhancedDataManager

console = Console()

class EnhancedMicrocapTrader:
    """Enhanced microcap trading system with multiple data sources."""
    
    def __init__(self):
        self.data_manager = EnhancedDataManager()
        self.portfolio_file = "portfolio.csv"
        self.candidates_file = "candidates.csv"
        self.report_file = "daily_report.md"
        
        # Ensure portfolio file exists
        self._ensure_portfolio_file()
    
    def _ensure_portfolio_file(self):
        """Ensure portfolio CSV file exists with proper columns."""
        try:
            df = pd.read_csv(self.portfolio_file)
        except FileNotFoundError:
            # Create new portfolio file
            df = pd.DataFrame(columns=['symbol', 'shares', 'buy_price', 'current_price', 'pnl'])
            df.to_csv(self.portfolio_file, index=False)
            console.print(f"✅ Created new portfolio file: {self.portfolio_file}", style="green")
    
    def run_daily_update(self):
        """Run the daily update process with enhanced data sources."""
        console.print("🚀 Starting Enhanced Daily Update", style="bold cyan")
        console.print("=" * 50)
        
        # Step 1: Load current portfolio
        with Progress(SpinnerColumn(), TextColumn("Loading portfolio..."), console=console) as progress:
            portfolio_df = pd.read_csv(self.portfolio_file)
            progress.update(progress.add_task("Portfolio loaded", total=1), completed=1)
        
        console.print(f"📊 Portfolio loaded: {len(portfolio_df)} positions", style="blue")
        
        # Step 2: Update portfolio prices
        if not portfolio_df.empty:
            console.print("\n💰 Updating portfolio prices...")
            symbols = portfolio_df['symbol'].tolist()
            prices = self.data_manager.get_current_prices(symbols)
            
            # Update current prices and calculate PnL
            for idx, row in portfolio_df.iterrows():
                symbol = row['symbol']
                if symbol in prices:
                    current_price = prices[symbol]
                    buy_price = row['buy_price']
                    shares = row['shares']
                    pnl = (current_price - buy_price) * shares
                    
                    portfolio_df.at[idx, 'current_price'] = current_price
                    portfolio_df.at[idx, 'pnl'] = pnl
            
            # Save updated portfolio
            portfolio_df.to_csv(self.portfolio_file, index=False)
            console.print("✅ Portfolio prices updated", style="green")
        
        # Step 3: Get microcap candidates
        console.print("\n🔍 Finding microcap candidates...")
        candidates_df = self.data_manager.get_microcap_stocks(count=30)
        
        if not candidates_df.empty:
            # Save candidates
            candidates_df.to_csv(self.candidates_file, index=False)
            console.print(f"✅ Found {len(candidates_df)} microcap candidates", style="green")
        else:
            console.print("⚠️  No candidates found", style="yellow")
        
        # Step 4: Generate report
        console.print("\n📝 Generating daily report...")
        self._generate_daily_report(portfolio_df, candidates_df)
        console.print("✅ Daily report generated", style="green")
        
        # Step 5: Show summary
        self._show_summary(portfolio_df, candidates_df)
        
        console.print("\n🎉 Daily update completed!", style="bold green")
    
    def _generate_daily_report(self, portfolio_df, candidates_df):
        """Generate the daily report with enhanced formatting."""
        report = []
        report.append("# Daily Microcap Trading Report")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Portfolio Summary
        report.append("## 📊 Portfolio Summary")
        if not portfolio_df.empty:
            total_value = (portfolio_df['current_price'] * portfolio_df['shares']).sum()
            total_pnl = portfolio_df['pnl'].sum()
            total_invested = (portfolio_df['buy_price'] * portfolio_df['shares']).sum()
            pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            report.append(f"- **Total Portfolio Value:** ${total_value:,.2f}")
            report.append(f"- **Total P&L:** ${total_pnl:,.2f} ({pnl_percentage:+.2f}%)")
            report.append(f"- **Total Invested:** ${total_invested:,.2f}")
            report.append("")
            
            # Top gainers and losers
            if not portfolio_df.empty:
                top_gainers = portfolio_df.nlargest(3, 'pnl')
                top_losers = portfolio_df.nsmallest(3, 'pnl')
                
                report.append("### 🚀 Top Gainers")
                for _, row in top_gainers.iterrows():
                    pnl_pct = (row['pnl'] / (row['buy_price'] * row['shares']) * 100)
                    report.append(f"- **{row['symbol']}:** ${row['pnl']:,.2f} ({pnl_pct:+.2f}%)")
                
                report.append("")
                report.append("### 📉 Top Losers")
                for _, row in top_losers.iterrows():
                    pnl_pct = (row['pnl'] / (row['buy_price'] * row['shares']) * 100)
                    report.append(f"- **{row['symbol']}:** ${row['pnl']:,.2f} ({pnl_pct:+.2f}%)")
        else:
            report.append("No positions in portfolio.")
        
        report.append("")
        
        # Candidates Analysis with Enhanced Insights
        report.append("## 🔍 Microcap Candidates Analysis")
        if not candidates_df.empty:
            report.append(f"- **Total Candidates:** {len(candidates_df)}")
            report.append(f"- **Average Market Cap:** ${candidates_df['market_cap'].mean():.2f}B")
            report.append("")
            
            # Top candidates by score
            top_scored = candidates_df.nlargest(5, 'score')
            report.append("### 🎯 Top Scored Candidates (Best Opportunities)")
            for _, row in top_scored.iterrows():
                score = row.get('score', 0)
                report.append(f"- **{row['symbol']}:** ${row['price']:.2f} | Score: {score:.1f}/100 | {row['pct_change_1d']:+.2f}%")
            
            report.append("")
            
            # High momentum candidates
            high_momentum = candidates_df.nlargest(5, 'pct_change_1d')
            report.append("### 📈 High Momentum Candidates")
            for _, row in high_momentum.iterrows():
                report.append(f"- **{row['symbol']}:** ${row['price']:.2f} | {row['pct_change_1d']:+.2f}% | Vol: {row['avg_volume']:,}")
            
            report.append("")
            
            # Trading Recommendations
            report.append("### 💡 Trading Recommendations")
            
            # Find best opportunities
            best_opportunities = candidates_df[
                (candidates_df['score'] >= 70) & 
                (candidates_df['pct_change_1d'] > 0) & 
                (candidates_df['avg_volume'] > 100000)
            ].head(3)
            
            if not best_opportunities.empty:
                report.append("**Strong Buy Candidates:**")
                for _, row in best_opportunities.iterrows():
                    score = row.get('score', 0)
                    report.append(f"- **{row['symbol']}** (Score: {score:.1f}) - Strong momentum + volume")
            else:
                report.append("**No strong buy signals today** - Consider waiting for better opportunities")
            
            report.append("")
            report.append("**Risk Management:**")
            report.append("- Set stop losses at 5-8% below entry")
            report.append("- Take profits at 15-20% gains")
            report.append("- Diversify across 3-5 positions")
            
        else:
            report.append("No candidates available.")
        
        report.append("")
        report.append("---")
        report.append("*Report generated by Enhanced Microcap Trading System*")
        
        # Write report
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
    
    def _show_summary(self, portfolio_df, candidates_df):
        """Show a summary using Rich tables."""
        console.print("\n📊 Portfolio Summary", style="bold cyan")
        
        if not portfolio_df.empty:
            # Portfolio table
            portfolio_table = Table(title="Current Portfolio")
            portfolio_table.add_column("Symbol", style="cyan")
            portfolio_table.add_column("Shares", justify="right")
            portfolio_table.add_column("Buy Price", justify="right")
            portfolio_table.add_column("Current Price", justify="right")
            portfolio_table.add_column("P&L", justify="right")
            portfolio_table.add_column("P&L %", justify="right")
            
            for _, row in portfolio_df.iterrows():
                pnl_pct = (row['pnl'] / (row['buy_price'] * row['shares']) * 100)
                pnl_style = "green" if row['pnl'] >= 0 else "red"
                
                portfolio_table.add_row(
                    row['symbol'],
                    str(int(row['shares'])),
                    f"${row['buy_price']:.2f}",
                    f"${row['current_price']:.2f}",
                    f"${row['pnl']:,.2f}",
                    f"{pnl_pct:+.2f}%",
                    style=pnl_style
                )
            
            console.print(portfolio_table)
        else:
            console.print("No positions in portfolio.", style="yellow")
        
        # Candidates summary
        if not candidates_df.empty:
            console.print("\n🎯 Top Candidates", style="bold cyan")
            candidates_table = Table(title="Top 5 Candidates")
            candidates_table.add_column("Symbol", style="cyan")
            candidates_table.add_column("Price", justify="right")
            candidates_table.add_column("Market Cap", justify="right")
            candidates_table.add_column("1D %", justify="right")
            candidates_table.add_column("5D %", justify="right")
            candidates_table.add_column("Volume", justify="right")
            
            top_candidates = candidates_df.head(5)
            for _, row in top_candidates.iterrows():
                candidates_table.add_row(
                    row['symbol'],
                    f"${row['price']:.2f}",
                    f"${row['market_cap']:.2f}B",
                    f"{row['pct_change_1d']:+.2f}%",
                    f"{row['pct_change_5d']:+.2f}%",
                    f"{row['avg_volume']:,}"
                )
            
            console.print(candidates_table)
    
    def calculate_position_size(self, symbol: str, available_capital: float = 10000) -> Dict:
        """Calculate optimal position size based on volatility and score."""
        data = self.data_manager.get_stock_data(symbol)
        if not data:
            return {'shares': 0, 'investment': 0, 'risk_level': 'high'}
        
        score = data.get('score', 0)
        price = data.get('price', 0)
        volatility = abs(data.get('pct_change_1d', 0))
        
        # Base position size (1-5% of capital based on score)
        if score >= 80:
            base_percentage = 0.05  # 5% for high-scoring stocks
        elif score >= 60:
            base_percentage = 0.03  # 3% for medium-high scoring
        elif score >= 40:
            base_percentage = 0.02  # 2% for medium scoring
        else:
            base_percentage = 0.01  # 1% for low scoring
        
        # Adjust for volatility (reduce size for high volatility)
        if volatility > 10:
            base_percentage *= 0.5
        elif volatility > 5:
            base_percentage *= 0.7
        
        # Calculate investment amount
        investment = available_capital * base_percentage
        shares = int(investment / price) if price > 0 else 0
        
        # Determine risk level
        if score >= 70 and volatility < 5:
            risk_level = 'low'
        elif score >= 50 and volatility < 8:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'shares': shares,
            'investment': investment,
            'risk_level': risk_level,
            'score': score,
            'volatility': volatility
        }
    
    def add_position(self, symbol: str, shares: int, buy_price: float):
        """Add a new position to the portfolio."""
        try:
            # Get current data for the symbol
            data = self.data_manager.get_stock_data(symbol)
            if not data:
                console.print(f"❌ Could not fetch data for {symbol}", style="red")
                return
            
            # Check if it's a microcap stock
            if not self.data_manager.is_microcap_stock(symbol):
                console.print(f"❌ {symbol} is not a microcap stock (market cap >= $2B)", style="red")
                console.print(f"   Market cap: ${data.get('market_cap', 0):.2f}B", style="yellow")
                return
            
            # Calculate optimal position size
            position_analysis = self.calculate_position_size(symbol)
            score = position_analysis['score']
            risk_level = position_analysis['risk_level']
            
            # Load current portfolio
            portfolio_df = pd.read_csv(self.portfolio_file)
            
            # Check if position already exists
            if symbol in portfolio_df['symbol'].values:
                console.print(f"⚠️  Position for {symbol} already exists", style="yellow")
                return
            
            # Add new position
            new_row = {
                'symbol': symbol,
                'shares': shares,
                'buy_price': buy_price,
                'current_price': data['price'],
                'pnl': (data['price'] - buy_price) * shares
            }
            
            portfolio_df = pd.concat([portfolio_df, pd.DataFrame([new_row])], ignore_index=True)
            portfolio_df.to_csv(self.portfolio_file, index=False)
            
            console.print(f"✅ Added {shares} shares of {symbol} at ${buy_price:.2f}", style="green")
            console.print(f"   Current price: ${data['price']:.2f} (P&L: ${new_row['pnl']:,.2f})")
            console.print(f"   Market cap: ${data.get('market_cap', 0):.2f}B")
            console.print(f"   Score: {score:.1f}/100 | Risk: {risk_level.upper()}")
            
        except Exception as e:
            console.print(f"❌ Error adding position: {e}", style="red")
    
    def remove_position(self, symbol: str):
        """Remove a position from the portfolio."""
        try:
            portfolio_df = pd.read_csv(self.portfolio_file)
            
            if symbol not in portfolio_df['symbol'].values:
                console.print(f"❌ No position found for {symbol}", style="red")
                return
            
            # Remove the position
            portfolio_df = portfolio_df[portfolio_df['symbol'] != symbol]
            portfolio_df.to_csv(self.portfolio_file, index=False)
            
            console.print(f"✅ Removed position for {symbol}", style="green")
            
        except Exception as e:
            console.print(f"❌ Error removing position: {e}", style="red")
    
    def show_portfolio(self):
        """Show current portfolio."""
        try:
            portfolio_df = pd.read_csv(self.portfolio_file)
            self._show_summary(portfolio_df, pd.DataFrame())
        except Exception as e:
            console.print(f"❌ Error loading portfolio: {e}", style="red")
    
    def analyze_position_size(self, symbol: str):
        """Analyze optimal position size for a symbol."""
        try:
            data = self.data_manager.get_stock_data(symbol)
            if not data:
                console.print(f"❌ Could not fetch data for {symbol}", style="red")
                return
            
            position_analysis = self.calculate_position_size(symbol)
            
            console.print(f"\n📊 Position Analysis for {symbol}", style="bold cyan")
            console.print("=" * 50)
            
            # Stock info
            console.print(f"Current Price: ${data['price']:.2f}")
            console.print(f"Market Cap: ${data.get('market_cap', 0):.2f}B")
            console.print(f"1-Day Change: {data.get('pct_change_1d', 0):+.2f}%")
            console.print(f"5-Day Change: {data.get('pct_change_5d', 0):+.2f}%")
            console.print(f"Average Volume: {data.get('avg_volume', 0):,}")
            console.print(f"Score: {position_analysis['score']:.1f}/100")
            
            console.print("\n💰 Position Sizing Recommendations:")
            console.print(f"Risk Level: {position_analysis['risk_level'].upper()}")
            console.print(f"Recommended Shares: {position_analysis['shares']}")
            console.print(f"Investment Amount: ${position_analysis['investment']:,.2f}")
            
            # Risk assessment
            if position_analysis['risk_level'] == 'low':
                console.print("✅ Low risk - Good for larger positions", style="green")
            elif position_analysis['risk_level'] == 'medium':
                console.print("⚠️  Medium risk - Moderate position size", style="yellow")
            else:
                console.print("🔴 High risk - Consider smaller position", style="red")
                
        except Exception as e:
            console.print(f"❌ Error analyzing position: {e}", style="red")

    def show_candidates(self):
        """Show current candidates."""
        try:
            candidates_df = pd.read_csv(self.candidates_file)
            if not candidates_df.empty:
                self._show_summary(pd.DataFrame(), candidates_df)
            else:
                console.print("No candidates available. Run daily update first.", style="yellow")
        except Exception as e:
            console.print(f"❌ Error loading candidates: {e}", style="red")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Enhanced Microcap Trading System")
    parser.add_argument('command', choices=['update', 'add', 'remove', 'portfolio', 'candidates', 'analyze'],
                       help='Command to execute')
    parser.add_argument('--symbol', '-s', help='Stock symbol (for add/remove/analyze commands)')
    parser.add_argument('--shares', '-n', type=int, help='Number of shares (for add command)')
    parser.add_argument('--price', '-p', type=float, help='Buy price (for add command)')
    
    args = parser.parse_args()
    
    trader = EnhancedMicrocapTrader()
    
    if args.command == 'update':
        trader.run_daily_update()
    elif args.command == 'add':
        if not all([args.symbol, args.shares, args.price]):
            console.print("❌ Please provide symbol, shares, and price for add command", style="red")
            return
        trader.add_position(args.symbol.upper(), args.shares, args.price)
    elif args.command == 'remove':
        if not args.symbol:
            console.print("❌ Please provide symbol for remove command", style="red")
            return
        trader.remove_position(args.symbol.upper())
    elif args.command == 'portfolio':
        trader.show_portfolio()
    elif args.command == 'candidates':
        trader.show_candidates()
    elif args.command == 'analyze':
        if not args.symbol:
            console.print("❌ Please provide symbol for analyze command", style="red")
            return
        trader.analyze_position_size(args.symbol.upper())


if __name__ == "__main__":
    main() 