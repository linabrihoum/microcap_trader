#!/usr/bin/env python3
"""
Portfolio Value Chart Generator
Tracks portfolio value starting from $200 investment over time.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
from rich.console import Console
import numpy as np

console = Console()

class PortfolioValueChart:
    def __init__(self):
        self.trading_history_file = "trading_history.csv"
        self.chart_file = "portfolio_value_chart.png"
        self.console = Console()
        self.initial_investment = 200  # Starting with $200
        
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
    
    def calculate_portfolio_value(self, df):
        """Calculate portfolio value over time starting from $200."""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Convert dates to datetime
        df['buy_date'] = pd.to_datetime(df['buy_date'])
        df['sell_date'] = pd.to_datetime(df['sell_date'])
        
        # Get all unique dates from buy and sell dates
        all_dates = []
        for _, row in df.iterrows():
            all_dates.append(row['buy_date'])
            if pd.notna(row['sell_date']):
                all_dates.append(row['sell_date'])
        
        # Add current date
        all_dates.append(datetime.now())
        
        # Remove duplicates and sort
        unique_dates = sorted(list(set(all_dates)))
        
        # Calculate portfolio value for each date
        portfolio_values = []
        current_value = self.initial_investment
        
        for date in unique_dates:
            # Calculate PnL for all trades up to this date
            daily_pnl = 0
            
            for _, trade in df.iterrows():
                # If trade was bought before or on this date
                if trade['buy_date'] <= date:
                    # If trade is closed and sold before or on this date
                    if trade['status'] == 'CLOSED' and pd.notna(trade['sell_date']) and trade['sell_date'] <= date:
                        daily_pnl += trade['pnl']
                    # If trade is still open on this date
                    elif trade['status'] == 'OPEN':
                        daily_pnl += trade['pnl']
            
            # Calculate current portfolio value
            portfolio_value = self.initial_investment + daily_pnl
            portfolio_values.append(portfolio_value)
        
        # Create DataFrame with dates and values
        portfolio_data = pd.DataFrame({
            'date': unique_dates,
            'value': portfolio_values
        })
        
        return portfolio_data
    
    def create_portfolio_chart(self, portfolio_data):
        """Create and save the portfolio value chart."""
        if portfolio_data.empty:
            console.print("❌ No portfolio data to chart", style="red")
            return
        
        # Set up the plot
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        fig.suptitle('Portfolio Value: $200 Investment Performance', fontsize=16, fontweight='bold')
        
        # Format dates for x-axis
        dates = [d.strftime('%Y-%m-%d') for d in portfolio_data['date']]
        
        # Plot portfolio value
        ax.plot(dates, portfolio_data['value'], 
                marker='o', linewidth=3, markersize=6, color='blue', alpha=0.8,
                label='Trading Bot ($200 invested)')
        
        # Add value label at the last point
        last_value = portfolio_data['value'].iloc[-1]
        ax.annotate(f'${last_value:.2f}', 
                    xy=(len(dates)-1, last_value),
                    xytext=(5, 0), textcoords='offset points',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Add -7% drawdown line
        drawdown_value = self.initial_investment * 0.93
        ax.axhline(y=drawdown_value, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
        ax.annotate(f'-7% Drawdown (${drawdown_value:.2f})', 
                    xy=(0, drawdown_value), 
                    xytext=(10, 10), textcoords='offset points',
                    color='red', fontsize=10)
        
        # Set title and labels
        ax.set_title('Portfolio Value Over Time', fontweight='bold', fontsize=14)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        
        # Format x-axis
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([d.split('-')[1] + '/' + d.split('-')[2] for d in dates], rotation=45)
        
        # Add grid and legend
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        plt.tight_layout()
        plt.savefig(self.chart_file, dpi=300, bbox_inches='tight')
        console.print(f"✅ Chart saved as: {self.chart_file}", style="green")
        
        return fig
    
    def run(self):
        """Main execution method."""
        console.print("📊 Generating Portfolio Value Chart...", style="bold blue")
        
        # Load trading data
        df = self.load_trading_data()
        if df is None:
            return
        
        # Calculate portfolio value over time
        portfolio_data = self.calculate_portfolio_value(df)
        if portfolio_data.empty:
            console.print("❌ No portfolio data calculated", style="red")
            return
        
        # Create and save chart
        self.create_portfolio_chart(portfolio_data)

def main():
    """Main function."""
    chart_generator = PortfolioValueChart()
    chart_generator.run()

if __name__ == "__main__":
    main()