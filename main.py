"""
Main application module for the microcap trading system.
"""

import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime

from config import STYLE_SUCCESS, STYLE_ERROR, STYLE_WARNING, STYLE_INFO, STYLE_HEADER
from data_manager import DataManager
from stock_data import StockDataManager
from report_generator import ReportGenerator
import pandas as pd


class MicrocapTrader:
    """Main application class for the microcap trading system."""
    
    def __init__(self):
        self.console = Console()
        self.data_manager = DataManager()
        self.stock_data = StockDataManager()
        self.report_generator = ReportGenerator()
    
    def run_daily_update(self):
        """Run the daily update process."""
        self.console.print(Panel.fit("🔄 Running Daily Update", style=STYLE_HEADER))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Load portfolio
            task1 = progress.add_task("Loading portfolio...", total=None)
            portfolio = self.data_manager.load_portfolio()
            progress.update(task1, description="Portfolio loaded")
            
            # Update portfolio prices
            if len(portfolio) > 0:
                task2 = progress.add_task("Updating portfolio prices...", total=None)
                symbols = portfolio['symbol'].tolist()
                price_data = self.stock_data.get_current_prices(symbols)
                self.data_manager.update_portfolio_prices(price_data)
                portfolio = self.data_manager.load_portfolio()  # Reload with updated data
                progress.update(task2, description="Portfolio prices updated")
            
            # Get new candidates
            task3 = progress.add_task("Finding microcap candidates...", total=None)
            candidates = self.stock_data.get_random_candidates()
            self.data_manager.save_candidates(candidates)
            progress.update(task3, description=f"Found {len(candidates)} candidates")
            
            # Generate report
            task4 = progress.add_task("Generating daily report...", total=None)
            self.report_generator.generate_daily_report(portfolio, candidates)
            progress.update(task4, description="Daily report generated")
        
        self.console.print(f"✅ Daily update completed successfully!", style=STYLE_SUCCESS)
        self.show_summary(portfolio, candidates)
    
    def show_summary(self, portfolio, candidates):
        """Show a summary of the current state."""
        # Portfolio summary
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
            
            self.console.print(portfolio_table)
            self.console.print(f"Total Value: ${total_value:,.2f} | P&L: ${total_pnl:,.2f} ({pnl_percentage:+.2f}%)", style=STYLE_INFO)
        
        # Candidates summary
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
            
            self.console.print(candidates_table)
    
    def add_position(self, symbol, shares, buy_price):
        """Add a new position to the portfolio."""
        self.console.print(f"Adding position: {symbol} - {shares} shares at ${buy_price:.2f}", style=STYLE_INFO)
        
        if self.data_manager.add_to_portfolio(symbol, shares, buy_price):
            self.console.print(f"✅ Position added successfully!", style=STYLE_SUCCESS)
        else:
            self.console.print(f"❌ Failed to add position", style=STYLE_ERROR)
    
    def remove_position(self, symbol):
        """Remove a position from the portfolio."""
        self.console.print(f"Removing position: {symbol}", style=STYLE_INFO)
        
        if self.data_manager.remove_from_portfolio(symbol):
            self.console.print(f"✅ Position removed successfully!", style=STYLE_SUCCESS)
        else:
            self.console.print(f"❌ Failed to remove position", style=STYLE_ERROR)
    
    def show_portfolio(self):
        """Show current portfolio."""
        portfolio = self.data_manager.load_portfolio()
        
        if len(portfolio) == 0:
            self.console.print("No positions in portfolio.", style=STYLE_WARNING)
            return
        
        self.show_summary(portfolio, pd.DataFrame())
    
    def show_candidates(self):
        """Show current candidates."""
        candidates = self.data_manager.load_candidates()
        
        if len(candidates) == 0:
            self.console.print("No candidates found. Run daily update first.", style=STYLE_WARNING)
            return
        
        self.show_summary(pd.DataFrame(), candidates)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Microcap Trading System")
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
            print("Error: --symbol, --shares, and --price are required for add command")
            return
        trader.add_position(args.symbol, args.shares, args.price)
    elif args.command == "remove":
        if not args.symbol:
            print("Error: --symbol is required for remove command")
            return
        trader.remove_position(args.symbol)
    elif args.command == "portfolio":
        trader.show_portfolio()
    elif args.command == "candidates":
        trader.show_candidates()


if __name__ == "__main__":
    main() 