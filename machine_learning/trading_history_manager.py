#!/usr/bin/env python3
"""
Trading History Manager
Manages wins and losses tracking for the microcap trading system.
"""

import pandas as pd
import os
from datetime import datetime, date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

class TradingHistoryManager:
    def __init__(self, history_file="trading_history.csv"):
        self.history_file = history_file
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Create the trading history file if it doesn't exist."""
        if not os.path.exists(self.history_file):
            columns = [
                'symbol', 'shares', 'buy_price', 'sell_price', 
                'buy_date', 'sell_date', 'status', 'pnl', 
                'pnl_percentage', 'hold_days', 'notes'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.history_file, index=False)
            console.print(f"✅ Created new trading history file: {self.history_file}")
    
    def load_history(self):
        """Load the trading history from CSV."""
        try:
            return pd.read_csv(self.history_file)
        except FileNotFoundError:
            self._ensure_history_file()
            return pd.read_csv(self.history_file)
    
    def save_history(self, df):
        """Save the trading history to CSV."""
        df.to_csv(self.history_file, index=False)
    
    def add_trade(self, symbol, shares, buy_price, buy_date=None, notes=""):
        """Add a new trade to the history."""
        if buy_date is None:
            buy_date = datetime.now().strftime('%Y-%m-%d')
        
        df = self.load_history()
        
        # Check if symbol already exists as OPEN position
        existing_open = df[(df['symbol'] == symbol) & (df['status'] == 'OPEN')]
        if not existing_open.empty:
            console.print(f"⚠️  Warning: {symbol} already has an OPEN position")
            return False
        
        new_trade = {
            'symbol': symbol,
            'shares': shares,
            'buy_price': buy_price,
            'sell_price': None,
            'buy_date': buy_date,
            'sell_date': None,
            'status': 'OPEN',
            'pnl': 0.0,
            'pnl_percentage': 0.0,
            'hold_days': 0,
            'notes': notes
        }
        
        df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
        self.save_history(df)
        console.print(f"✅ Added new trade: {symbol} - {shares} shares at ${buy_price}")
        return True
    
    def close_position(self, symbol, sell_price, sell_date=None, notes=""):
        """Close an open position."""
        if sell_date is None:
            sell_date = datetime.now().strftime('%Y-%m-%d')
        
        df = self.load_history()
        open_positions = df[(df['symbol'] == symbol) & (df['status'] == 'OPEN')]
        
        if open_positions.empty:
            console.print(f"❌ No open position found for {symbol}")
            return False
        
        # Get the open position
        position = open_positions.iloc[0]
        buy_price = position['buy_price']
        shares = position['shares']
        buy_date = position['buy_date']
        
        # Calculate P&L
        pnl = (sell_price - buy_price) * shares
        pnl_percentage = ((sell_price - buy_price) / buy_price) * 100
        
        # Calculate hold days
        buy_dt = datetime.strptime(buy_date, '%Y-%m-%d')
        sell_dt = datetime.strptime(sell_date, '%Y-%m-%d')
        hold_days = (sell_dt - buy_dt).days
        
        # Update the position
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'OPEN'), 'sell_price'] = sell_price
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'OPEN'), 'sell_date'] = sell_date
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'OPEN'), 'status'] = 'CLOSED'
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'CLOSED'), 'pnl'] = pnl
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'CLOSED'), 'pnl_percentage'] = pnl_percentage
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'CLOSED'), 'hold_days'] = hold_days
        df.loc[(df['symbol'] == symbol) & (df['status'] == 'CLOSED'), 'notes'] = notes
        
        self.save_history(df)
        
        status = "WIN" if pnl > 0 else "LOSS"
        console.print(f"✅ Closed position: {symbol} - {status} ${pnl:.2f} ({pnl_percentage:.2f}%)")
        return True
    
    def update_open_positions(self, portfolio_df):
        """Update P&L for open positions based on current portfolio data."""
        df = self.load_history()
        open_positions = df[df['status'] == 'OPEN']
        
        for _, position in open_positions.iterrows():
            symbol = position['symbol']
            portfolio_row = portfolio_df[portfolio_df['symbol'] == symbol]
            
            if not portfolio_row.empty:
                current_price = portfolio_row.iloc[0]['current_price']
                buy_price = position['buy_price']
                shares = position['shares']
                
                pnl = (current_price - buy_price) * shares
                pnl_percentage = ((current_price - buy_price) / buy_price) * 100
                
                df.loc[(df['symbol'] == symbol) & (df['status'] == 'OPEN'), 'pnl'] = pnl
                df.loc[(df['symbol'] == symbol) & (df['status'] == 'OPEN'), 'pnl_percentage'] = pnl_percentage
        
        self.save_history(df)
    
    def show_summary(self):
        """Display trading summary statistics."""
        df = self.load_history()
        
        if df.empty:
            console.print("📊 No trading history found")
            return
        
        # Closed positions
        closed_positions = df[df['status'] == 'CLOSED']
        open_positions = df[df['status'] == 'OPEN']
        
        # Calculate statistics
        total_trades = len(closed_positions)
        winning_trades = len(closed_positions[closed_positions['pnl'] > 0])
        losing_trades = len(closed_positions[closed_positions['pnl'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = closed_positions['pnl'].sum()
        total_pnl_percentage = closed_positions['pnl_percentage'].mean()
        
        # Open positions
        open_pnl = open_positions['pnl'].sum()
        open_pnl_percentage = open_positions['pnl_percentage'].mean()
        
        # Create summary table
        summary_table = Table(title="📊 Trading Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Closed Trades", str(total_trades))
        summary_table.add_row("Winning Trades", f"{winning_trades} ({win_rate:.1f}%)")
        summary_table.add_row("Losing Trades", str(losing_trades))
        summary_table.add_row("Total P&L (Closed)", f"${total_pnl:.2f}")
        summary_table.add_row("Avg P&L % (Closed)", f"{total_pnl_percentage:.2f}%")
        summary_table.add_row("Open Positions P&L", f"${open_pnl:.2f}")
        summary_table.add_row("Open Positions Avg %", f"{open_pnl_percentage:.2f}%")
        
        console.print(summary_table)
        
        # Show recent trades
        if not closed_positions.empty:
            recent_trades = closed_positions.tail(5)
            trades_table = Table(title="📈 Recent Closed Trades")
            trades_table.add_column("Symbol", style="cyan")
            trades_table.add_column("Shares", style="blue")
            trades_table.add_column("Buy Price", style="green")
            trades_table.add_column("Sell Price", style="green")
            trades_table.add_column("P&L", style="yellow")
            trades_table.add_column("P&L %", style="yellow")
            trades_table.add_column("Hold Days", style="magenta")
            
            for _, trade in recent_trades.iterrows():
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                trades_table.add_row(
                    trade['symbol'],
                    str(trade['shares']),
                    f"${trade['buy_price']:.2f}",
                    f"${trade['sell_price']:.2f}",
                    f"${trade['pnl']:.2f}",
                    f"{trade['pnl_percentage']:.2f}%",
                    str(trade['hold_days'])
                )
            
            console.print(trades_table)
    
    def show_open_positions(self):
        """Display current open positions."""
        df = self.load_history()
        open_positions = df[df['status'] == 'OPEN']
        
        if open_positions.empty:
            console.print("📊 No open positions found")
            return
        
        positions_table = Table(title="📈 Open Positions")
        positions_table.add_column("Symbol", style="cyan")
        positions_table.add_column("Shares", style="blue")
        positions_table.add_column("Buy Price", style="green")
        positions_table.add_column("Buy Date", style="blue")
        positions_table.add_column("Current P&L", style="yellow")
        positions_table.add_column("P&L %", style="yellow")
        positions_table.add_column("Notes", style="white")
        
        for _, position in open_positions.iterrows():
            pnl_color = "green" if position['pnl'] > 0 else "red"
            positions_table.add_row(
                position['symbol'],
                str(position['shares']),
                f"${position['buy_price']:.2f}",
                position['buy_date'],
                f"${position['pnl']:.2f}",
                f"{position['pnl_percentage']:.2f}%",
                position['notes']
            )
        
        console.print(positions_table)

def main():
    """Main function for command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trading History Manager")
    parser.add_argument("command", choices=["summary", "open", "add", "close", "update"])
    parser.add_argument("--symbol", help="Stock symbol")
    parser.add_argument("--shares", type=int, help="Number of shares")
    parser.add_argument("--price", type=float, help="Price per share")
    parser.add_argument("--notes", help="Trade notes")
    
    args = parser.parse_args()
    
    manager = TradingHistoryManager()
    
    if args.command == "summary":
        manager.show_summary()
    elif args.command == "open":
        manager.show_open_positions()
    elif args.command == "add":
        if not all([args.symbol, args.shares, args.price]):
            console.print("❌ Please provide --symbol, --shares, and --price")
            return
        manager.add_trade(args.symbol, args.shares, args.price, notes=args.notes or "")
    elif args.command == "close":
        if not all([args.symbol, args.price]):
            console.print("❌ Please provide --symbol and --price")
            return
        manager.close_position(args.symbol, args.price, notes=args.notes or "")
    elif args.command == "update":
        # Update from current portfolio
        try:
            portfolio_df = pd.read_csv("data/portfolio.csv")
            manager.update_open_positions(portfolio_df)
            console.print("✅ Updated open positions from data/portfolio.csv")
        except FileNotFoundError:
            console.print("❌ data/portfolio.csv not found")

if __name__ == "__main__":
    main() 