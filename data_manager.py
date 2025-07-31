"""
Data management module for handling portfolio and candidates CSV files.
"""

import pandas as pd
import os
from datetime import datetime
from config import (
    PORTFOLIO_FILE, CANDIDATES_FILE, 
    PORTFOLIO_COLUMNS, CANDIDATES_COLUMNS
)


class DataManager:
    """Manages portfolio and candidates data files."""
    
    def __init__(self):
        self.portfolio_file = PORTFOLIO_FILE
        self.candidates_file = CANDIDATES_FILE
    
    def load_portfolio(self):
        """Load portfolio data from CSV file."""
        if not os.path.exists(self.portfolio_file):
            # Create empty portfolio file with headers
            df = pd.DataFrame(columns=PORTFOLIO_COLUMNS)
            df.to_csv(self.portfolio_file, index=False)
            return df
        
        try:
            df = pd.read_csv(self.portfolio_file)
            # Ensure all required columns exist
            for col in PORTFOLIO_COLUMNS:
                if col not in df.columns:
                    df[col] = 0.0
            return df
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return pd.DataFrame(columns=PORTFOLIO_COLUMNS)
    
    def save_portfolio(self, df):
        """Save portfolio data to CSV file."""
        try:
            df.to_csv(self.portfolio_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            return False
    
    def load_candidates(self):
        """Load candidates data from CSV file."""
        if not os.path.exists(self.candidates_file):
            return pd.DataFrame(columns=CANDIDATES_COLUMNS)
        
        try:
            return pd.read_csv(self.candidates_file)
        except Exception as e:
            print(f"Error loading candidates: {e}")
            return pd.DataFrame(columns=CANDIDATES_COLUMNS)
    
    def save_candidates(self, df):
        """Save candidates data to CSV file."""
        try:
            df.to_csv(self.candidates_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving candidates: {e}")
            return False
    
    def add_to_portfolio(self, symbol, shares, buy_price):
        """Add a new position to the portfolio."""
        portfolio = self.load_portfolio()
        
        # Check if symbol already exists
        if symbol in portfolio['symbol'].values:
            print(f"Symbol {symbol} already exists in portfolio")
            return False
        
        # Add new position
        new_row = {
            'symbol': symbol,
            'shares': shares,
            'buy_price': buy_price,
            'current_price': buy_price,  # Initially same as buy price
            'pnl': 0.0  # Initially 0
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
                
                # Calculate PnL
                pnl = (current_price - buy_price) * shares
                
                # Update values
                portfolio.at[index, 'current_price'] = current_price
                portfolio.at[index, 'pnl'] = pnl
        
        return self.save_portfolio(portfolio) 