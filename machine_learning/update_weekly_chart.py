#!/usr/bin/env python3
"""
Weekly Chart Update Script
Simple script to update the weekly PnL chart with latest trading data.
"""

import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

# Import the chart generator
from weekly_pnl_chart import WeeklyPnLChart

console = Console()

def main():
    """Update the weekly PnL chart with latest data."""
    console.print("🔄 Updating Weekly P&L Chart...", style="bold blue")
    
    # Check if trading history exists
    if not os.path.exists("trading_history.csv"):
        console.print("❌ trading_history.csv not found", style="red")
        return
    
    # Generate updated chart
    chart_generator = WeeklyPnLChart()
    chart_generator.run()
    
    # Display update confirmation
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_panel = Panel(
        f"""
        ✅ Weekly P&L Chart Updated Successfully!
        
        📅 Last Updated: {current_time}
        📊 Chart File: weekly_pnl_chart.png
        📈 Data Source: trading_history.csv
        
        💡 Tip: Run this script weekly to keep your chart updated
        """,
        title="📊 Chart Update Complete",
        border_style="green"
    )
    
    console.print(update_panel)

if __name__ == "__main__":
    main() 