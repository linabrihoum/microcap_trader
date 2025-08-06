#!/usr/bin/env python3
"""
Weekly PnL Chart Generator
Tracks and visualizes weekly profit/loss performance over time.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
from rich.console import Console
from rich.panel import Panel
import numpy as np

console = Console()

class WeeklyPnLChart:
    def __init__(self):
        self.trading_history_file = "trading_history.csv"
        self.chart_file = "weekly_pnl_chart.png"
        self.console = Console()
        
    def load_trading_data(self):
        """Load trading history data."""
        try:
            df = pd.read_csv(self.trading_history_file)
            console.print(f"✅ Loaded {len(df)} trading records", style="green")
            return df
        except FileNotFoundError:
            console.print(f"❌ Trading history file not found: {self.trading_history_file}", style="red")
            return None
        except Exception as e:
            console.print(f"❌ Error loading trading data: {e}", style="red")
            return None
    
    def calculate_weekly_pnl(self, df):
        """Calculate weekly PnL from trading history."""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Convert dates to datetime
        df['buy_date'] = pd.to_datetime(df['buy_date'])
        df['sell_date'] = pd.to_datetime(df['sell_date'])
        
        # Calculate realized PnL for closed trades
        closed_trades = df[df['status'] == 'CLOSED'].copy()
        closed_trades['realized_pnl'] = closed_trades['pnl']
        
        # Calculate unrealized PnL for open trades (current positions)
        open_trades = df[df['status'] == 'OPEN'].copy()
        open_trades['unrealized_pnl'] = open_trades['pnl']
        
        # Combine all trades
        all_trades = pd.concat([closed_trades, open_trades], ignore_index=True)
        
        # Group by week and calculate weekly totals
        weekly_pnl = []
        
        # Get date range - start from July 30, 2025
        min_date = datetime(2025, 7, 30)  # Start from July 30th
        max_date = max(all_trades['sell_date'].max() if not all_trades['sell_date'].isna().all() else all_trades['buy_date'].max(), 
                      datetime.now())
        
        current_date = min_date
        cumulative_pnl = 0
        
        while current_date <= max_date:
            week_start = current_date - timedelta(days=current_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Get trades that closed this week
            week_closed = closed_trades[
                (closed_trades['sell_date'] >= week_start) & 
                (closed_trades['sell_date'] <= week_end)
            ]
            
            # Get unrealized PnL for positions opened this week
            week_unrealized = open_trades[
                (open_trades['buy_date'] >= week_start) & 
                (open_trades['buy_date'] <= week_end)
            ]
            
            # Calculate weekly PnL
            realized_pnl = week_closed['realized_pnl'].sum()
            unrealized_pnl = week_unrealized['unrealized_pnl'].sum()
            weekly_total = realized_pnl + unrealized_pnl
            
            cumulative_pnl += weekly_total
            
            weekly_pnl.append({
                'week_start': week_start,
                'week_end': week_end,
                'realized_pnl': realized_pnl,
                'unrealized_pnl': unrealized_pnl,
                'weekly_total': weekly_total,
                'cumulative_pnl': cumulative_pnl,
                'trades_count': len(week_closed) + len(week_unrealized)
            })
            
            current_date += timedelta(days=7)
        
        return pd.DataFrame(weekly_pnl)
    
    def create_pnl_chart(self, weekly_data):
        """Create and save the weekly PnL chart."""
        if weekly_data.empty:
            console.print("❌ No weekly data to chart", style="red")
            return
        
        # Set up the plot - single chart for cumulative PnL
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        fig.suptitle('📈 Cumulative Trading Performance (July 30 - Present)', fontsize=16, fontweight='bold')
        
        # Weekly PnL Chart
        weeks = [f"{row['week_start'].strftime('%m/%d')} - {row['week_end'].strftime('%m/%d')}" 
                for _, row in weekly_data.iterrows()]
        
        # Cumulative PnL Chart - main focus
        line = ax.plot(weeks, weekly_data['cumulative_pnl'], 
                marker='o', linewidth=3, markersize=8, color='blue', alpha=0.8)
        
        # Add value labels on points
        for i, (week, value) in enumerate(zip(weeks, weekly_data['cumulative_pnl'])):
            ax.text(i, value + (0.5 if value >= 0 else -0.5), 
                    f'${value:.2f}', ha='center', va='bottom' if value >= 0 else 'top',
                    fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', 
                    facecolor='white', alpha=0.8))
        
        ax.set_title('Cumulative P&L Over Time', fontweight='bold', fontsize=14)
        ax.set_ylabel('Cumulative P&L ($)', fontsize=12)
        ax.set_xlabel('Week Period', fontsize=12)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        ax.grid(True, alpha=0.3)
        
        # Color the line based on performance
        for i in range(len(weekly_data['cumulative_pnl']) - 1):
            if weekly_data['cumulative_pnl'].iloc[i+1] >= weekly_data['cumulative_pnl'].iloc[i]:
                ax.plot([i, i+1], [weekly_data['cumulative_pnl'].iloc[i], weekly_data['cumulative_pnl'].iloc[i+1]], 
                       color='green', linewidth=3, alpha=0.8)
            else:
                ax.plot([i, i+1], [weekly_data['cumulative_pnl'].iloc[i], weekly_data['cumulative_pnl'].iloc[i+1]], 
                       color='red', linewidth=3, alpha=0.8)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add summary statistics
        total_pnl = weekly_data['cumulative_pnl'].iloc[-1]
        total_weeks = len(weekly_data)
        avg_weekly_pnl = weekly_data['weekly_total'].mean()
        winning_weeks = len(weekly_data[weekly_data['weekly_total'] > 0])
        win_rate = (winning_weeks / total_weeks) * 100 if total_weeks > 0 else 0
        
        # Calculate performance metrics
        starting_value = weekly_data['cumulative_pnl'].iloc[0] if len(weekly_data) > 0 else 0
        total_return = ((total_pnl - starting_value) / abs(starting_value)) * 100 if starting_value != 0 else 0
        
        summary_text = f"""
        📊 PERFORMANCE SUMMARY:
        • Total P&L: ${total_pnl:.2f}
        • Total Return: {total_return:.1f}%
        • Weeks Tracked: {total_weeks}
        • Average Weekly P&L: ${avg_weekly_pnl:.2f}
        • Winning Weeks: {winning_weeks}/{total_weeks} ({win_rate:.1f}%)
        • Starting Date: July 30, 2025
        """
        
        # Add summary as text box
        ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
                fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.chart_file, dpi=300, bbox_inches='tight')
        console.print(f"✅ Chart saved as: {self.chart_file}", style="green")
        
        return fig
    
    def display_summary(self, weekly_data):
        """Display a summary of the weekly PnL data."""
        if weekly_data.empty:
            return
        
        total_pnl = weekly_data['cumulative_pnl'].iloc[-1]
        total_weeks = len(weekly_data)
        avg_weekly_pnl = weekly_data['weekly_total'].mean()
        winning_weeks = len(weekly_data[weekly_data['weekly_total'] > 0])
        win_rate = (winning_weeks / total_weeks) * 100 if total_weeks > 0 else 0
        
        # Find best and worst weeks
        best_week = weekly_data.loc[weekly_data['weekly_total'].idxmax()]
        worst_week = weekly_data.loc[weekly_data['weekly_total'].idxmin()]
        
        summary_panel = Panel(
            f"""
            📈 WEEKLY P&L SUMMARY
            
            💰 Total P&L: ${total_pnl:.2f}
            📅 Weeks Tracked: {total_weeks}
            📊 Average Weekly P&L: ${avg_weekly_pnl:.2f}
            🎯 Win Rate: {win_rate:.1f}% ({winning_weeks}/{total_weeks} weeks)
            
            🏆 Best Week: {best_week['week_start'].strftime('%m/%d')} - {best_week['week_end'].strftime('%m/%d')} (${best_week['weekly_total']:.2f})
            📉 Worst Week: {worst_week['week_start'].strftime('%m/%d')} - {worst_week['week_end'].strftime('%m/%d')} (${worst_week['weekly_total']:.2f})
            
            📊 Chart saved as: {self.chart_file}
            """,
            title="📊 Weekly Performance Analysis",
            border_style="blue"
        )
        
        console.print(summary_panel)
    
    def run(self):
        """Main execution method."""
        console.print("📊 Generating Weekly P&L Chart...", style="bold blue")
        
        # Load trading data
        df = self.load_trading_data()
        if df is None:
            return
        
        # Calculate weekly PnL
        weekly_data = self.calculate_weekly_pnl(df)
        if weekly_data.empty:
            console.print("❌ No weekly data calculated", style="red")
            return
        
        # Create and save chart
        self.create_pnl_chart(weekly_data)
        
        # Display summary
        self.display_summary(weekly_data)

def main():
    """Main function."""
    chart_generator = WeeklyPnLChart()
    chart_generator.run()

if __name__ == "__main__":
    main() 