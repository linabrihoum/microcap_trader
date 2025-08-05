#!/usr/bin/env python3
"""
Trading Analysis - Comprehensive P&L Analysis
Calculates realized and unrealized gains/losses from trading history.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns

console = Console()

class TradingAnalysis:
    def __init__(self, history_file="trading_history.csv"):
        self.history_file = history_file
        self.df = self.load_history()
    
    def load_history(self):
        """Load trading history from CSV."""
        try:
            return pd.read_csv(self.history_file)
        except FileNotFoundError:
            console.print(f"❌ {self.history_file} not found")
            return pd.DataFrame()
    
    def calculate_realized_pnl(self):
        """Calculate realized P&L from closed positions."""
        closed_positions = self.df[self.df['status'] == 'CLOSED']
        
        if closed_positions.empty:
            return {
                'total_realized_pnl': 0.0,
                'total_realized_percentage': 0.0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'total_invested': 0.0,
                'roi': 0.0
            }
        
        # Basic statistics
        total_realized_pnl = closed_positions['pnl'].sum()
        total_realized_percentage = closed_positions['pnl_percentage'].mean()
        
        # Trade counts
        winning_trades = len(closed_positions[closed_positions['pnl'] > 0])
        losing_trades = len(closed_positions[closed_positions['pnl'] < 0])
        total_trades = len(closed_positions)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Average wins/losses
        wins = closed_positions[closed_positions['pnl'] > 0]['pnl']
        losses = closed_positions[closed_positions['pnl'] < 0]['pnl']
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        largest_win = wins.max() if len(wins) > 0 else 0
        largest_loss = losses.min() if len(losses) > 0 else 0
        
        # Total invested and ROI
        total_invested = (closed_positions['shares'] * closed_positions['buy_price']).sum()
        roi = (total_realized_pnl / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'total_realized_pnl': total_realized_pnl,
            'total_realized_percentage': total_realized_percentage,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'total_invested': total_invested,
            'roi': roi
        }
    
    def calculate_unrealized_pnl(self):
        """Calculate unrealized P&L from open positions."""
        open_positions = self.df[self.df['status'] == 'OPEN']
        
        if open_positions.empty:
            return {
                'total_unrealized_pnl': 0.0,
                'total_unrealized_percentage': 0.0,
                'open_positions_count': 0,
                'winning_positions': 0,
                'losing_positions': 0,
                'total_invested_open': 0.0
            }
        
        total_unrealized_pnl = open_positions['pnl'].sum()
        total_unrealized_percentage = open_positions['pnl_percentage'].mean()
        open_positions_count = len(open_positions)
        
        winning_positions = len(open_positions[open_positions['pnl'] > 0])
        losing_positions = len(open_positions[open_positions['pnl'] < 0])
        
        total_invested_open = (open_positions['shares'] * open_positions['buy_price']).sum()
        
        return {
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_unrealized_percentage': total_unrealized_percentage,
            'open_positions_count': open_positions_count,
            'winning_positions': winning_positions,
            'losing_positions': losing_positions,
            'total_invested_open': total_invested_open
        }
    
    def show_comprehensive_analysis(self):
        """Display comprehensive trading analysis."""
        realized = self.calculate_realized_pnl()
        unrealized = self.calculate_unrealized_pnl()
        
        # Total P&L
        total_pnl = realized['total_realized_pnl'] + unrealized['total_unrealized_pnl']
        total_invested = realized['total_invested'] + unrealized['total_invested_open']
        total_roi = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        console.print("\n" + "="*80)
        console.print("📊 COMPREHENSIVE TRADING ANALYSIS", style="bold blue")
        console.print("="*80)
        
        # Overall Summary
        overall_table = Table(title="🎯 Overall Performance")
        overall_table.add_column("Metric", style="cyan")
        overall_table.add_column("Value", style="green")
        
        overall_table.add_row("Total P&L (Realized + Unrealized)", f"${total_pnl:.2f}")
        overall_table.add_row("Total ROI", f"{total_roi:.2f}%")
        overall_table.add_row("Total Invested", f"${total_invested:.2f}")
        overall_table.add_row("Total Closed Trades", str(realized['total_trades']))
        overall_table.add_row("Open Positions", str(unrealized['open_positions_count']))
        
        console.print(overall_table)
        
        # Realized Gains/Losses
        realized_table = Table(title="💰 Realized Gains/Losses")
        realized_table.add_column("Metric", style="cyan")
        realized_table.add_column("Value", style="green")
        
        realized_table.add_row("Total Realized P&L", f"${realized['total_realized_pnl']:.2f}")
        realized_table.add_row("Average Realized Return", f"{realized['total_realized_percentage']:.2f}%")
        realized_table.add_row("Win Rate", f"{realized['win_rate']:.1f}%")
        realized_table.add_row("Winning Trades", f"{realized['winning_trades']} / {realized['total_trades']}")
        realized_table.add_row("Losing Trades", f"{realized['losing_trades']} / {realized['total_trades']}")
        realized_table.add_row("Average Win", f"${realized['avg_win']:.2f}")
        realized_table.add_row("Average Loss", f"${realized['avg_loss']:.2f}")
        realized_table.add_row("Largest Win", f"${realized['largest_win']:.2f}")
        realized_table.add_row("Largest Loss", f"${realized['largest_loss']:.2f}")
        realized_table.add_row("Total Invested (Closed)", f"${realized['total_invested']:.2f}")
        realized_table.add_row("ROI (Closed)", f"{realized['roi']:.2f}%")
        
        console.print(realized_table)
        
        # Unrealized Gains/Losses
        unrealized_table = Table(title="📈 Unrealized Gains/Losses")
        unrealized_table.add_column("Metric", style="cyan")
        unrealized_table.add_column("Value", style="green")
        
        unrealized_table.add_row("Total Unrealized P&L", f"${unrealized['total_unrealized_pnl']:.2f}")
        unrealized_table.add_row("Average Unrealized Return", f"{unrealized['total_unrealized_percentage']:.2f}%")
        unrealized_table.add_row("Winning Positions", f"{unrealized['winning_positions']} / {unrealized['open_positions_count']}")
        unrealized_table.add_row("Losing Positions", f"{unrealized['losing_positions']} / {unrealized['open_positions_count']}")
        unrealized_table.add_row("Total Invested (Open)", f"${unrealized['total_invested_open']:.2f}")
        
        console.print(unrealized_table)
        
        # Detailed Trade Analysis
        self.show_detailed_trades()
    
    def show_detailed_trades(self):
        """Show detailed breakdown of all trades."""
        console.print("\n" + "="*80)
        console.print("📋 DETAILED TRADE BREAKDOWN", style="bold blue")
        console.print("="*80)
        
        # Closed Trades
        closed_positions = self.df[self.df['status'] == 'CLOSED']
        if not closed_positions.empty:
            closed_table = Table(title="✅ Closed Trades")
            closed_table.add_column("Symbol", style="cyan")
            closed_table.add_column("Shares", style="blue")
            closed_table.add_column("Buy Price", style="green")
            closed_table.add_column("Sell Price", style="green")
            closed_table.add_column("P&L", style="yellow")
            closed_table.add_column("P&L %", style="yellow")
            closed_table.add_column("Hold Days", style="magenta")
            closed_table.add_column("Notes", style="white")
            
            for _, trade in closed_positions.iterrows():
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                closed_table.add_row(
                    trade['symbol'],
                    f"{trade['shares']:.2f}",
                    f"${trade['buy_price']:.2f}",
                    f"${trade['sell_price']:.2f}",
                    f"${trade['pnl']:.2f}",
                    f"{trade['pnl_percentage']:.2f}%",
                    str(trade['hold_days']),
                    trade['notes']
                )
            
            console.print(closed_table)
        
        # Open Positions
        open_positions = self.df[self.df['status'] == 'OPEN']
        if not open_positions.empty:
            open_table = Table(title="📈 Open Positions")
            open_table.add_column("Symbol", style="cyan")
            open_table.add_column("Shares", style="blue")
            open_table.add_column("Buy Price", style="green")
            open_table.add_column("Buy Date", style="blue")
            open_table.add_column("Current P&L", style="yellow")
            open_table.add_column("P&L %", style="yellow")
            open_table.add_column("Notes", style="white")
            
            for _, position in open_positions.iterrows():
                pnl_color = "green" if position['pnl'] > 0 else "red"
                open_table.add_row(
                    position['symbol'],
                    str(position['shares']),
                    f"${position['buy_price']:.2f}",
                    position['buy_date'],
                    f"${position['pnl']:.2f}",
                    f"{position['pnl_percentage']:.2f}%",
                    position['notes']
                )
            
            console.print(open_table)
    
    def show_performance_insights(self):
        """Show performance insights and recommendations."""
        realized = self.calculate_realized_pnl()
        unrealized = self.calculate_unrealized_pnl()
        
        console.print("\n" + "="*80)
        console.print("💡 PERFORMANCE INSIGHTS", style="bold blue")
        console.print("="*80)
        
        insights = []
        
        # Win rate analysis
        if realized['total_trades'] > 0:
            if realized['win_rate'] >= 60:
                insights.append("🎯 Excellent win rate! You're consistently profitable.")
            elif realized['win_rate'] >= 50:
                insights.append("✅ Good win rate. Focus on improving average win size.")
            else:
                insights.append("⚠️  Win rate below 50%. Consider reviewing entry/exit strategies.")
        
        # Risk analysis
        if realized['avg_win'] > 0 and realized['avg_loss'] < 0:
            risk_reward = abs(realized['avg_win'] / realized['avg_loss'])
            if risk_reward >= 2:
                insights.append("🚀 Great risk/reward ratio! Your wins significantly outweigh losses.")
            elif risk_reward >= 1.5:
                insights.append("✅ Good risk/reward ratio. Consider optimizing for larger wins.")
            else:
                insights.append("⚠️  Risk/reward ratio could be improved. Focus on larger wins or smaller losses.")
        
        # Current position analysis
        if unrealized['open_positions_count'] > 0:
            winning_ratio = unrealized['winning_positions'] / unrealized['open_positions_count']
            if winning_ratio >= 0.7:
                insights.append("📈 Strong current positions! Most positions are profitable.")
            elif winning_ratio >= 0.5:
                insights.append("📊 Mixed current positions. Monitor closely for exit opportunities.")
            else:
                insights.append("📉 Most current positions are underwater. Review stop-loss strategies.")
        
        # Overall performance
        total_pnl = realized['total_realized_pnl'] + unrealized['total_unrealized_pnl']
        if total_pnl > 0:
            insights.append("💰 Overall profitable trading! Keep up the good work.")
        else:
            insights.append("📉 Overall negative P&L. Consider reviewing your trading strategy.")
        
        # Display insights
        for i, insight in enumerate(insights, 1):
            console.print(f"{i}. {insight}")

def main():
    """Main function."""
    analyzer = TradingAnalysis()
    
    if analyzer.df.empty:
        console.print("❌ No trading history found")
        return
    
    analyzer.show_comprehensive_analysis()
    analyzer.show_performance_insights()

if __name__ == "__main__":
    main() 