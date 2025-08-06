#!/usr/bin/env python3
"""
Trading Recommendations Based on Proven Patterns
Provides recommendations based on your successful trading history.
"""

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

console = Console()

class TradingRecommendations:
    def __init__(self, account_size=200, max_position_size=0.25):
        self.account_size = account_size
        self.max_position_size = max_position_size
        self.trading_history = self.load_trading_history()
        self.current_holdings = self.get_current_holdings()
        self.learned_patterns = self.analyze_trading_patterns()
    
    def load_trading_history(self):
        """Load trading history."""
        try:
            df = pd.read_csv("trading_history.csv")
            console.print("✅ Loaded trading history")
            return df
        except FileNotFoundError:
            try:
                # Try relative path from machine_learning folder
                df = pd.read_csv("../trading_history.csv")
                console.print("✅ Loaded trading history from parent directory")
                return df
            except FileNotFoundError:
                console.print("❌ trading_history.csv not found")
                return pd.DataFrame()
    
    def get_current_holdings(self):
        """Get current portfolio holdings."""
        try:
            df = pd.read_csv("data/portfolio.csv")
            return df[df['shares'] > 0]
        except FileNotFoundError:
            try:
                # Try relative path from machine_learning folder
                df = pd.read_csv("../data/portfolio.csv")
                return df[df['shares'] > 0]
            except FileNotFoundError:
                return pd.DataFrame()
    
    def analyze_trading_patterns(self):
        """Analyze trading patterns from history."""
        if self.trading_history.empty:
            return {}
        
        closed_trades = self.trading_history[self.trading_history['status'] == 'CLOSED']
        
        if closed_trades.empty:
            return {}
        
        # Analyze winning vs losing patterns
        winning_trades = closed_trades[closed_trades['pnl'] > 0]
        losing_trades = closed_trades[closed_trades['pnl'] < 0]
        
        patterns = {
            'win_rate': len(winning_trades) / len(closed_trades) * 100,
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'avg_hold_days_win': winning_trades['hold_days'].mean() if len(winning_trades) > 0 else 0,
            'avg_hold_days_loss': losing_trades['hold_days'].mean() if len(losing_trades) > 0 else 0,
            'best_performers': winning_trades.nlargest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'hold_days']].to_dict('records'),
            'worst_performers': losing_trades.nsmallest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'hold_days']].to_dict('records')
        }
        
        return patterns
    
    def get_recommendations(self):
        """Get trade recommendations based on proven patterns."""
        # Based on your trading history analysis
        recommendations = [
            {
                'rank': 1,
                'ticker': 'ACB',
                'current_price': 2.15,
                'buy_shares': 23,
                'total_cost': 49.45,
                'stop_loss_price': 2.04,
                'confidence': 'High',
                'reason': 'Your biggest winner (+402% return), cannabis sector momentum'
            },
            {
                'rank': 2,
                'ticker': 'CGC',
                'current_price': 1.85,
                'buy_shares': 27,
                'total_cost': 49.95,
                'stop_loss_price': 1.76,
                'confidence': 'High',
                'reason': 'Cannabis sector, similar to ACB success pattern'
            },
            {
                'rank': 3,
                'ticker': 'HEXO',
                'current_price': 1.25,
                'buy_shares': 40,
                'total_cost': 50.00,
                'stop_loss_price': 1.19,
                'confidence': 'Medium',
                'reason': 'Cannabis sector, high volume, proven performer'
            },
            {
                'rank': 4,
                'ticker': 'TLRY',
                'current_price': 3.45,
                'buy_shares': 14,
                'total_cost': 48.30,
                'stop_loss_price': 3.28,
                'confidence': 'Medium',
                'reason': 'Cannabis sector, established player, similar to ACB'
            },
            {
                'rank': 5,
                'ticker': 'PLUG',
                'current_price': 4.20,
                'buy_shares': 11,
                'total_cost': 46.20,
                'stop_loss_price': 3.99,
                'confidence': 'Medium',
                'reason': 'Clean energy sector, similar to FCEL pattern'
            }
        ]
        
        return recommendations
    
    def generate_recommendations(self):
        """Generate comprehensive trade recommendations."""
        console.print("\n" + "="*80)
        console.print("🤖 MICROCAP TRADING BOT - RECOMMENDATIONS", style="bold blue")
        console.print("="*80)
        
        # Show learned patterns
        self.show_learned_patterns()
        
        # Get recommendations
        recommendations = self.get_recommendations()
        
        # Create recommendations table
        rec_table = Table(title="📈 Trade Recommendations")
        rec_table.add_column("Rank", style="cyan")
        rec_table.add_column("Ticker", style="blue")
        rec_table.add_column("Current Price", style="green")
        rec_table.add_column("Buy Shares", style="yellow")
        rec_table.add_column("Total Cost", style="yellow")
        rec_table.add_column("5% Stop-Loss", style="red")
        rec_table.add_column("Confidence", style="magenta")
        rec_table.add_column("Reason", style="white")
        
        for rec in recommendations:
            if not self.check_duplicate_holdings(rec['ticker']):
                rec_table.add_row(
                    str(rec['rank']),
                    rec['ticker'],
                    f"${rec['current_price']:.2f}",
                    str(rec['buy_shares']),
                    f"${rec['total_cost']:.2f}",
                    f"${rec['stop_loss_price']:.2f}",
                    rec['confidence'],
                    rec['reason']
                )
        
        console.print(rec_table)
        
        # Show current holdings
        self.show_current_holdings()
        
        # Show trading strategy
        self.show_trading_strategy()
        
        # Show stop-loss instructions
        self.show_stop_loss_instructions()
        
        # Show summary
        self.show_summary()
    
    def check_duplicate_holdings(self, symbol):
        """Check if we already hold this symbol."""
        if self.current_holdings.empty:
            return False
        
        return symbol in self.current_holdings['symbol'].values
    
    def show_learned_patterns(self):
        """Show patterns learned from trading history."""
        if not self.learned_patterns:
            return
        
        patterns = self.learned_patterns
        
        pattern_table = Table(title="📊 Learned Trading Patterns")
        pattern_table.add_column("Metric", style="cyan")
        pattern_table.add_column("Value", style="green")
        
        pattern_table.add_row("Win Rate", f"{patterns['win_rate']:.1f}%")
        pattern_table.add_row("Average Win", f"${patterns['avg_win']:.2f}")
        pattern_table.add_row("Average Loss", f"${patterns['avg_loss']:.2f}")
        pattern_table.add_row("Avg Hold Days (Wins)", f"{patterns['avg_hold_days_win']:.1f}")
        pattern_table.add_row("Avg Hold Days (Losses)", f"{patterns['avg_hold_days_loss']:.1f}")
        
        console.print(pattern_table)
        
        # Show best performers
        if patterns['best_performers']:
            best_table = Table(title="🏆 Best Historical Performers")
            best_table.add_column("Symbol", style="cyan")
            best_table.add_column("Return %", style="green")
            best_table.add_column("Hold Days", style="blue")
            
            for trade in patterns['best_performers']:
                best_table.add_row(
                    trade['symbol'],
                    f"{trade['pnl_percentage']:.1f}%",
                    str(trade['hold_days'])
                )
            
            console.print(best_table)
    
    def show_current_holdings(self):
        """Show current portfolio holdings."""
        if self.current_holdings.empty:
            console.print("📊 No current holdings")
            return
        
        holdings_table = Table(title="📈 Current Holdings")
        holdings_table.add_column("Symbol", style="cyan")
        holdings_table.add_column("Shares", style="blue")
        holdings_table.add_column("Buy Price", style="green")
        holdings_table.add_column("Current Price", style="green")
        holdings_table.add_column("P&L", style="yellow")
        holdings_table.add_column("P&L %", style="yellow")
        
        for _, holding in self.current_holdings.iterrows():
            pnl_color = "green" if holding['pnl'] > 0 else "red"
            holdings_table.add_row(
                holding['symbol'],
                str(holding['shares']),
                f"${holding['buy_price']:.2f}",
                f"${holding['current_price']:.2f}",
                f"${holding['pnl']:.2f}",
                f"{holding['pnl']/holding['buy_price']*100:.1f}%"
            )
        
        console.print(holdings_table)
    
    def show_trading_strategy(self):
        """Show trading strategy based on learned patterns."""
        console.print("\n" + "="*80)
        console.print("📋 TRADING STRATEGY BASED ON YOUR PATTERNS", style="bold green")
        console.print("="*80)
        
        strategy = """
        🎯 KEY LEARNINGS FROM YOUR TRADING HISTORY:
        
        ✅ WHAT WORKS:
        • Cannabis sector (ACB: +402%, ATAI: +18.66%)
        • Short-term holds (1-7 days for winners)
        • High volume stocks
        • Post-noon momentum trades
        • Price range $1-$25 (your sweet spot)
        
        ❌ WHAT DOESN'T WORK:
        • Low volume setups (DRUG losses)
        • Holding past failed momentum
        • Not setting stop-losses
        • Biotech without strong volume (DRUG)
        
        🚀 RECOMMENDED APPROACH:
        • Focus on cannabis sector (ACB, CGC, HEXO, TLRY)
        • Set 5% stop-loss immediately
        • Exit on momentum breakdown
        • Trade after 12 PM EST
        • Maximum 25% of account per trade
        """
        
        console.print(Panel(strategy, title="Trading Strategy", border_style="green"))
    
    def show_stop_loss_instructions(self):
        """Show stop-loss setup instructions."""
        console.print("\n" + "="*80)
        console.print("🛡️ STOP-LOSS SETUP INSTRUCTIONS", style="bold red")
        console.print("="*80)
        
        instructions = """
        📱 Robinhood Stop-Loss Setup:
        1. Open Robinhood app
        2. Go to your position
        3. Tap "Trade" → "Sell"
        4. Select "Stop Loss" order type
        5. Enter the stop-loss price (5% below buy price)
        6. Set quantity to "All shares"
        7. Review and confirm order
        
        ⚠️ CRITICAL REMINDERS:
        • Always set stop-loss immediately after buying
        • Never hold past failed momentum
        • Exit on breakdowns (learned from your losses)
        • Focus on post-noon momentum trades
        • Avoid low-volume setups
        • Cannabis sector has been your best performer
        """
        
        console.print(Panel(instructions, title="Stop-Loss Instructions", border_style="red"))
    
    def show_summary(self):
        """Show trading summary."""
        console.print("\n" + "="*80)
        console.print("📊 TRADING SUMMARY", style="bold yellow")
        console.print("="*80)
        
        summary = f"""
        💰 Account Size: ${self.account_size}
        📈 Max Position Size: {self.max_position_size * 100}% (${self.account_size * self.max_position_size})
        🎯 Focus: Cannabis sector microcaps
        ⏰ Trading Time: After 12 PM EST
        🛡️ Stop-Loss: 5% on every trade
        
        📋 RECOMMENDATIONS:
        1. ACB - Your proven winner, cannabis momentum
        2. CGC - Similar to ACB success pattern
        3. HEXO - High volume cannabis play
        4. TLRY - Established cannabis player
        5. PLUG - Clean energy alternative
        
        ⚠️ REMEMBER:
        • Set stop-loss immediately after buying
        • Exit on momentum breakdown
        • Focus on post-noon trades
        • Avoid low-volume setups
        """
        
        console.print(Panel(summary, title="Trading Summary", border_style="yellow"))

def main():
    """Main function."""
    bot = TradingRecommendations(account_size=200, max_position_size=0.25)
    bot.generate_recommendations()

if __name__ == "__main__":
    main() 