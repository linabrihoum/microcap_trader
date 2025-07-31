"""
Stock data fetching module using yfinance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import MAX_MARKET_CAP, CANDIDATES_COUNT, MIN_VOLUME_THRESHOLD


class StockDataManager:
    """Manages stock data fetching and processing."""
    
    def __init__(self):
        self.max_market_cap = MAX_MARKET_CAP
        self.candidates_count = CANDIDATES_COUNT
        self.min_volume = MIN_VOLUME_THRESHOLD
    
    def get_microcap_stocks(self):
        """Get a list of microcap stocks using yfinance."""
        # This is a simplified approach - in practice you'd want a more comprehensive list
        # For now, we'll use some known microcap ETFs and their holdings as a starting point
        
        # Common microcap stocks (you can expand this list)
        microcap_symbols = [
            'IWM', 'VTWO', 'IJR', 'IWC',  # Microcap ETFs
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',  # Large caps for testing
            # Add more microcap symbols here
        ]
        
        candidates = []
        
        for symbol in microcap_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get market cap
                market_cap = info.get('marketCap', 0)
                if market_cap == 0:
                    continue
                
                # Convert to billions
                market_cap_billions = market_cap / 1e9
                
                if market_cap_billions <= self.max_market_cap:
                    # Get historical data
                    hist = ticker.history(period='5d')
                    if len(hist) >= 5:
                        current_price = hist['Close'].iloc[-1]
                        price_1d_ago = hist['Close'].iloc[-2]
                        price_5d_ago = hist['Close'].iloc[0]
                        
                        pct_change_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100
                        pct_change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
                        avg_volume = hist['Volume'].mean() / 1000  # Convert to thousands
                        
                        if avg_volume >= self.min_volume:
                            candidates.append({
                                'symbol': symbol,
                                'market_cap': market_cap_billions,
                                'price': current_price,
                                'pct_change_1d': pct_change_1d,
                                'pct_change_5d': pct_change_5d,
                                'avg_volume': avg_volume
                            })
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
        
        return pd.DataFrame(candidates)
    
    def get_random_candidates(self):
        """Get random microcap candidates for evaluation."""
        candidates = self.get_microcap_stocks()
        
        if len(candidates) == 0:
            return pd.DataFrame()
        
        # Randomly select candidates
        if len(candidates) > self.candidates_count:
            candidates = candidates.sample(n=self.candidates_count, random_state=42)
        
        return candidates.sort_values('pct_change_5d', ascending=False)
    
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
                print(f"Error getting price for {symbol}: {e}")
                continue
        
        return price_data
    
    def get_stock_info(self, symbol):
        """Get detailed information for a specific stock."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', 'Unknown'),
                'market_cap': info.get('marketCap', 0) / 1e9,
                'price': info.get('currentPrice', 0),
                'volume': info.get('volume', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'sector': info.get('sector', 'Unknown')
            }
        except Exception as e:
            print(f"Error getting info for {symbol}: {e}")
            return None 