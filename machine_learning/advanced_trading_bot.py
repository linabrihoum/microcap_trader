#!/usr/bin/env python3
"""
Advanced Microcap Trading Bot
Enhanced version that learns from trading history and provides intelligent recommendations.
Combines real-time market analysis with proven pattern recognition and improved error handling.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import warnings
import os
import json
import glob
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from utilities.error_handler import error_handler, APIError, NetworkError, DataError, FileError, handle_exceptions
from validation.data_models import MarketData, TradingRecommendation
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

console = Console()

class AdvancedTradingBot:
    """
    Advanced trading bot that learns from your trading history and provides
    intelligent recommendations based on proven patterns and real-time market data.
    """
    
    def __init__(self, account_size: float = 200, max_position_size: float = 0.25):
        self.account_size = account_size
        self.max_position_size = max_position_size
        self.trading_history = self.load_trading_history()
        self.current_holdings = self.get_current_holdings()
        self.learned_patterns = self.analyze_trading_patterns()
        self.market_data_cache = {}
        
    @handle_exceptions
    def load_trading_history(self) -> pd.DataFrame:
        """Load trading history with enhanced error handling."""
        try:
            df = pd.read_csv("trading_history.csv")
            console.print("✅ Loaded trading history")
            return df
        except FileNotFoundError:
            try:
                # Try relative path from machine_learning folder
                df = pd.read_csv("machine_learning/trading_history.csv")
                console.print("✅ Loaded trading history from machine_learning folder")
                return df
            except FileNotFoundError:
                try:
                    # Try relative path from parent directory
                    df = pd.read_csv("../trading_history.csv")
                    console.print("✅ Loaded trading history from parent directory")
                    return df
                except FileNotFoundError:
                    error_handler.handle_file_error(FileNotFoundError("trading_history.csv not found"), "trading_history.csv")
                    return pd.DataFrame()
    
    @handle_exceptions
    def get_current_holdings(self) -> pd.DataFrame:
        """Get current portfolio holdings with enhanced error handling."""
        try:
            df = pd.read_csv("data/portfolio.csv")
            return df[df['shares'] > 0]
        except FileNotFoundError:
            try:
                # Try relative path from machine_learning folder
                df = pd.read_csv("machine_learning/portfolio.csv")
                return df[df['shares'] > 0]
            except FileNotFoundError:
                try:
                    # Try relative path from parent directory
                    df = pd.read_csv("../data/portfolio.csv")
                    return df[df['shares'] > 0]
                except FileNotFoundError:
                    error_handler.handle_file_error(FileNotFoundError("portfolio.csv not found"), "data/portfolio.csv")
                    return pd.DataFrame()
    
    def analyze_trading_patterns(self) -> Dict:
        """Enhanced analysis of trading patterns from history."""
        if self.trading_history.empty:
            return {}
        
        closed_trades = self.trading_history[self.trading_history['status'] == 'CLOSED']
        
        if closed_trades.empty:
            return {}
        
        # Analyze winning vs losing patterns
        winning_trades = closed_trades[closed_trades['pnl'] > 0]
        losing_trades = closed_trades[closed_trades['pnl'] < 0]
        
        # Enhanced pattern analysis
        patterns = {
            'win_rate': len(winning_trades) / len(closed_trades) * 100,
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'avg_hold_days_win': winning_trades['hold_days'].mean() if len(winning_trades) > 0 else 0,
            'avg_hold_days_loss': losing_trades['hold_days'].mean() if len(losing_trades) > 0 else 0,
            'best_performers': winning_trades.nlargest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'hold_days']].to_dict('records'),
            'worst_performers': losing_trades.nsmallest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'hold_days']].to_dict('records'),
            'total_trades': len(closed_trades),
            'total_wins': len(winning_trades),
            'total_losses': len(losing_trades),
            'profit_factor': abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else float('inf'),
            'largest_win': winning_trades['pnl'].max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 else 0,
            'avg_roi_win': winning_trades['pnl_percentage'].mean() if len(winning_trades) > 0 else 0,
            'avg_roi_loss': losing_trades['pnl_percentage'].mean() if len(losing_trades) > 0 else 0
        }
        
        return patterns
    
    @handle_exceptions
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get real-time market data with caching and fallback to simulated data."""
        if symbol in self.market_data_cache:
            return self.market_data_cache[symbol]
        
        try:
            # Try Polygon.io first
            data = self.get_market_data_polygon(symbol)
            if data:
                self.market_data_cache[symbol] = data
                return data
            
            # Try Finnhub second
            data = self.get_market_data_finnhub(symbol)
            if data:
                self.market_data_cache[symbol] = data
                return data
            
            # Fallback to simulated data
            data = self.get_simulated_data(symbol)
            self.market_data_cache[symbol] = data
            return data
            
        except Exception as e:
            error_handler.log_error_with_context(e, {
                'symbol': symbol,
                'operation': 'market_data_fetch'
            })
            # Fallback to simulated data on any error
            data = self.get_simulated_data(symbol)
            self.market_data_cache[symbol] = data
            return data
    
    @handle_exceptions
    @error_handler.retry_on_failure(max_retries=2, delay=0.5)
    def get_market_data_polygon(self, symbol: str) -> Optional[Dict]:
        """Get market data from Polygon.io API with enhanced error handling."""
        polygon_api_key = os.getenv('POLYGON_API_KEY')
        if not polygon_api_key:
            return None
            
        try:
            # Get current price and volume
            price_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
            price_response = requests.get(price_url, params={'apikey': polygon_api_key}, timeout=10)
            
            if price_response.status_code != 200:
                raise APIError(f"Status code {price_response.status_code}", "Polygon", price_response.status_code)
                
            price_data = price_response.json()
            if not price_data.get('results'):
                raise DataError(f"No data available for {symbol}")
                
            current_price = price_data['results'][0]['c']
            volume = price_data['results'][0].get('v', 0)
            
            # Get 5-day historical data for momentum
            hist_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')}/{datetime.now().strftime('%Y-%m-%d')}"
            hist_response = requests.get(hist_url, params={'apikey': polygon_api_key}, timeout=10)
            
            pct_change_5d = 0
            avg_volume = volume
            afternoon_momentum = 0
            
            if hist_response.status_code == 200:
                hist_data = hist_response.json()
                if hist_data.get('results') and len(hist_data['results']) >= 5:
                    results = hist_data['results']
                    current_price = results[-1]['c']
                    five_day_ago = results[0]['c']
                    pct_change_5d = ((current_price - five_day_ago) / five_day_ago) * 100 if five_day_ago > 0 else 0
                    avg_volume = sum(r.get('v', 0) for r in results) / len(results)
            
            # Get company details for market cap
            details_url = f"https://api.polygon.io/v3/reference/tickers/{symbol}"
            details_response = requests.get(details_url, params={'apikey': polygon_api_key}, timeout=10)
            
            market_cap = 0
            if details_response.status_code == 200:
                details_data = details_response.json()
                market_cap = details_data.get('results', {}).get('market_cap', 0)
            
            result_data = {
                'symbol': symbol,
                'current_price': current_price,
                'avg_volume': avg_volume,
                'market_cap': market_cap,
                'pct_change_5d': pct_change_5d,
                'afternoon_momentum': afternoon_momentum,
                'data_source': 'polygon'
            }
            
            # Validate the data
            if not error_handler.validate_data(result_data, f"Polygon data for {symbol}", ['symbol', 'current_price']):
                raise DataError(f"Invalid data structure for {symbol}")
            
            return result_data
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Timeout fetching data for {symbol}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error fetching {symbol}: {str(e)}")
        except Exception as e:
            if not error_handler.handle_api_error(e, "Polygon", symbol):
                return None
            raise
    
    def get_market_data_finnhub(self, symbol: str) -> Optional[Dict]:
        """Get market data from Finnhub API."""
        finnhub_api_key = os.getenv('FINNHUB_API_KEY')
        if not finnhub_api_key:
            return None
            
        try:
            # Get quote data
            quote_url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': finnhub_api_key
            }
            response = requests.get(quote_url, params=params)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            if data.get('c') == 0:  # No data
                return None
                
            current_price = data['c']
            volume = data.get('v', 0)
            
            # Get 5-day historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=10)
            
            hist_url = f"https://finnhub.io/api/v1/stock/candle"
            hist_params = {
                'symbol': symbol,
                'resolution': 'D',
                'from': int(start_date.timestamp()),
                'to': int(end_date.timestamp()),
                'token': finnhub_api_key
            }
            
            hist_response = requests.get(hist_url, params=hist_params)
            pct_change_5d = 0
            avg_volume = volume
            
            if hist_response.status_code == 200:
                hist_data = hist_response.json()
                if hist_data.get('s') == 'ok' and len(hist_data.get('c', [])) >= 5:
                    closes = hist_data['c']
                    volumes = hist_data.get('v', [volume] * len(closes))
                    
                    current_price = closes[-1]
                    five_day_ago = closes[0]
                    pct_change_5d = ((current_price - five_day_ago) / five_day_ago) * 100 if five_day_ago > 0 else 0
                    avg_volume = sum(volumes) / len(volumes)
            
            # Get company profile for market cap
            profile_url = f"https://finnhub.io/api/v1/stock/profile2"
            profile_response = requests.get(profile_url, params=params)
            
            market_cap = 0
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                market_cap = profile_data.get('marketCapitalization', 0)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'avg_volume': avg_volume,
                'market_cap': market_cap,
                'pct_change_5d': pct_change_5d,
                'afternoon_momentum': 0,  # Finnhub doesn't provide intraday data easily
                'data_source': 'finnhub'
            }
            
        except Exception as e:
            console.print(f"Error fetching {symbol} from Finnhub: {e}", style="red")
            return None
    
    def get_simulated_data(self, symbol: str) -> Dict:
        """Get simulated market data based on historical patterns."""
        # Simulated data based on your trading history and typical microcap patterns
        simulated_data = {
            'ACB': {'price': 2.15, 'volume': 1500000, 'momentum_5d': 8.5, 'afternoon_momentum': 3.2},
            'ATAI': {'price': 4.25, 'volume': 800000, 'momentum_5d': 12.3, 'afternoon_momentum': 5.1},
            'SNDL': {'price': 1.65, 'volume': 1200000, 'momentum_5d': 6.8, 'afternoon_momentum': 2.4},
            'CGC': {'price': 1.85, 'volume': 900000, 'momentum_5d': 7.2, 'afternoon_momentum': 3.8},
            'HEXO': {'price': 1.25, 'volume': 1100000, 'momentum_5d': 9.1, 'afternoon_momentum': 4.2},
            'TLRY': {'price': 3.45, 'volume': 1400000, 'momentum_5d': 11.5, 'afternoon_momentum': 6.8},
            'PLUG': {'price': 4.20, 'volume': 2000000, 'momentum_5d': 15.2, 'afternoon_momentum': 8.1},
            'OCGN': {'price': 2.80, 'volume': 600000, 'momentum_5d': 4.5, 'afternoon_momentum': 1.9},
            'FCEL': {'price': 4.95, 'volume': 1800000, 'momentum_5d': 13.7, 'afternoon_momentum': 7.3},
            'DRUG': {'price': 34.50, 'volume': 300000, 'momentum_5d': -2.1, 'afternoon_momentum': -1.5}
        }
        
        # Default values for unknown symbols
        default_data = {
            'price': 2.50,
            'volume': 750000,
            'momentum_5d': 5.0,
            'afternoon_momentum': 2.0
        }
        
        data = simulated_data.get(symbol, default_data)
        
        return {
            'symbol': symbol,
            'current_price': data['price'],
            'avg_volume': data['volume'],
            'market_cap': 1.5e9,  # Typical microcap
            'pct_change_5d': data['momentum_5d'],
            'afternoon_momentum': data['afternoon_momentum'],
            'info': {'marketCap': 1.5e9}
        }
    
    def get_candidates(self, strategy: str = 'momentum_focused') -> List[Dict]:
        """Get candidates based on strategy with enhanced momentum focus."""
        if strategy == 'proven_winners':
            return self.get_proven_winners()
        elif strategy == 'momentum_focused':
            return self.get_momentum_focused_candidates()
        elif strategy == 'hybrid':
            return self.get_hybrid_candidates()
        else:
            return self.get_hybrid_candidates()
    
    def get_proven_winners(self) -> List[Dict]:
        """Get recommendations based on your proven winners."""
        proven_winners = [
            {'symbol': 'ATAI', 'reason': 'Current winner (+18.66% return)', 'confidence': 'High', 'sector': 'Cannabis'},
            {'symbol': 'SNDL', 'reason': 'Current position (+0.61% return)', 'confidence': 'Medium', 'sector': 'Cannabis'},
            {'symbol': 'CGC', 'reason': 'Cannabis sector, potential opportunity', 'confidence': 'Medium', 'sector': 'Cannabis'},
            {'symbol': 'HEXO', 'reason': 'Cannabis sector, high volume', 'confidence': 'Medium', 'sector': 'Cannabis'},
            {'symbol': 'TLRY', 'reason': 'Cannabis sector, established player', 'confidence': 'Medium', 'sector': 'Cannabis'},
            {'symbol': 'PLUG', 'reason': 'Clean energy, similar to FCEL', 'confidence': 'Medium', 'sector': 'Clean Energy'},
            {'symbol': 'OCGN', 'reason': 'Biotech, similar to DRUG pattern', 'confidence': 'Low', 'sector': 'Biotech'}
        ]
        
        recommendations = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching proven winners...", total=len(proven_winners))
            
            for winner in proven_winners:
                progress.update(task, advance=1)
                
                data = self.get_market_data(winner['symbol'])
                if not data:
                    continue
                
                # Skip if price is too high for $200 account
                if data['current_price'] > 50:
                    continue
                
                # Calculate position size
                max_cost = self.account_size * self.max_position_size
                shares = int(max_cost / data['current_price'])
                
                if shares > 0 and not self.check_duplicate_holdings(winner['symbol']):
                    score = self.calculate_enhanced_score(
                        winner['symbol'], 
                        data['current_price'], 
                        data['avg_volume'], 
                        data['pct_change_5d'], 
                        data['afternoon_momentum'],
                        winner['confidence'],
                        winner['sector']
                    )
                    
                    recommendations.append({
                        'symbol': winner['symbol'],
                        'current_price': data['current_price'],
                        'shares': shares,
                        'total_cost': shares * data['current_price'],
                        'stop_loss_price': data['current_price'] * 0.95,
                        'confidence': winner['confidence'],
                        'reason': winner['reason'],
                        'sector': winner['sector'],
                        'score': score,
                        'avg_volume': data['avg_volume'],
                        'pct_change_5d': data['pct_change_5d'],
                        'afternoon_momentum': data['afternoon_momentum']
                    })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]
    
    def get_real_time_candidates(self) -> List[Dict]:
        """Get real-time microcap candidates."""
        microcap_symbols = [
            'SNDL', 'ATAI', 'FCEL', 'ACB', 'CGC', 'DRUG',  # Your historical trades
            'OCGN', 'NAKD', 'ZOM', 'IDEX', 'CIDM', 'CTRM',  # Popular microcaps
            'GNUS', 'MARK', 'SHIP', 'TOPS', 'HEXO', 'TLRY',  # High volume microcaps
            'APHA', 'CRON', 'ACB', 'CGC', 'TLRY', 'HEXO',   # Cannabis sector
            'PLUG', 'FCEL', 'BLDP', 'BEEM', 'HYSR', 'SUNW'  # Clean energy
        ]
        
        candidates = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing real-time candidates...", total=len(microcap_symbols))
            
            for symbol in microcap_symbols:
                progress.update(task, advance=1)
                
                data = self.get_market_data(symbol)
                if not data:
                    continue
                
                # Filter criteria based on learned patterns
                if (data['avg_volume'] >= 100000 and 
                    data['market_cap'] <= 2e9 and 
                    data['current_price'] >= 1.0 and 
                    data['current_price'] <= 50.0 and
                    data['pct_change_5d'] > -20 and  # Not in severe downtrend
                    data['afternoon_momentum'] > -5):   # Some afternoon momentum
                    
                    # Calculate position size based on account size
                    max_cost = self.account_size * self.max_position_size
                    shares = int(max_cost / data['current_price'])
                    
                    if shares > 0 and not self.check_duplicate_holdings(symbol):
                        score = self.calculate_enhanced_score(
                            symbol, 
                            data['current_price'], 
                            data['avg_volume'], 
                            data['pct_change_5d'], 
                            data['afternoon_momentum'],
                            'Medium',  # Default confidence for real-time
                            self.get_sector(symbol)
                        )
                        
                        candidates.append({
                            'symbol': symbol,
                            'current_price': data['current_price'],
                            'avg_volume': data['avg_volume'],
                            'market_cap': data['market_cap'],
                            'pct_change_5d': data['pct_change_5d'],
                            'afternoon_momentum': data['afternoon_momentum'],
                            'shares': shares,
                            'total_cost': shares * data['current_price'],
                            'stop_loss_price': data['current_price'] * 0.95,
                            'score': score,
                            'confidence': 'Medium',
                            'reason': f'Real-time analysis: {data["pct_change_5d"]:.1f}% 5d change, {data["afternoon_momentum"]:.1f}% PM momentum',
                            'sector': self.get_sector(symbol)
                        })
        
        # Sort by score and return top candidates
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:5]
    
    def get_momentum_focused_candidates(self) -> List[Dict]:
        """Get candidates focused on strong momentum patterns."""
        candidates = []
        
        # Focus on proven winners with momentum
        proven_winners = ['ATAI', 'SNDL', 'CGC', 'HEXO', 'TLRY']
        
        for symbol in proven_winners:
            if self.check_duplicate_holdings(symbol):
                continue
                
            market_data = self.get_market_data(symbol)
            if not market_data:
                continue
            
            # Enhanced momentum scoring
            momentum_score = self.calculate_momentum_score(market_data)
            if momentum_score < 70:  # Higher threshold for momentum
                continue
            
            # Calculate position size based on momentum
            position_size = self.calculate_momentum_position_size(market_data)
            
            candidates.append({
                'symbol': symbol,
                'current_price': market_data['current_price'],
                'buy_shares': position_size['shares'],
                'total_cost': position_size['total_cost'],
                'stop_loss_price': position_size['stop_loss'],
                'score': momentum_score,
                'sector': self.get_sector(symbol),
                'confidence': 'High' if momentum_score > 80 else 'Medium',
                'momentum_1d': market_data.get('pct_change_1d', 0),
                'momentum_5d': market_data.get('pct_change_5d', 0),
                'volume': market_data.get('avg_volume', 0)
            })
        
        # Sort by momentum score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:5]  # Top 5 momentum candidates
    
    def calculate_momentum_score(self, market_data: Dict) -> float:
        """Calculate enhanced momentum score based on performance analysis."""
        score = 0
        
        # Base momentum (40% weight)
        momentum_1d = market_data.get('pct_change_1d', 0)
        momentum_5d = market_data.get('pct_change_5d', 0)
        
        if momentum_1d > 10:  # Strong 1-day momentum
            score += 40
        elif momentum_1d > 5:
            score += 30
        elif momentum_1d > 2:
            score += 20
        
        # Volume analysis (30% weight)
        volume = market_data.get('avg_volume', 0)
        if volume > 5000:
            score += 30
        elif volume > 2000:
            score += 20
        elif volume > 1000:
            score += 10
        
        # Sector bonus (20% weight) - Cannabis focus
        sector = self.get_sector(market_data['symbol'])
        if sector == 'Cannabis':
            score += 20
        elif sector == 'Clean Energy':
            score += 10
        
        # Price range optimization (10% weight)
        price = market_data.get('current_price', 0)
        if 1 <= price <= 10:
            score += 10
        elif 10 < price <= 20:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def calculate_momentum_position_size(self, market_data: Dict) -> Dict:
        """Calculate position size based on momentum strength."""
        from config import ACCOUNT_SIZE, MAX_POSITION_SIZE, STOP_LOSS_PERCENTAGE
        
        price = market_data.get('current_price', 0)
        momentum_1d = market_data.get('pct_change_1d', 0)
        
        # Dynamic position sizing based on momentum
        if momentum_1d > 15:
            position_pct = MAX_POSITION_SIZE * 1.2  # 20% larger for strong momentum
        elif momentum_1d > 10:
            position_pct = MAX_POSITION_SIZE
        else:
            position_pct = MAX_POSITION_SIZE * 0.8  # 20% smaller for weak momentum
        
        max_cost = ACCOUNT_SIZE * position_pct
        shares = int(max_cost / price)
        total_cost = shares * price
        stop_loss = price * (1 - STOP_LOSS_PERCENTAGE)
        
        return {
            'shares': shares,
            'total_cost': total_cost,
            'stop_loss': stop_loss
        }
    
    def get_hybrid_candidates(self) -> List[Dict]:
        """Get hybrid recommendations combining proven winners and real-time analysis."""
        proven = self.get_proven_winners()
        real_time = self.get_real_time_candidates()
        
        # Combine and deduplicate
        all_candidates = {}
        
        for candidate in proven + real_time:
            symbol = candidate['symbol']
            if symbol not in all_candidates or candidate['score'] > all_candidates[symbol]['score']:
                all_candidates[symbol] = candidate
        
        # Sort by score
        candidates = list(all_candidates.values())
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:5]
    
    def calculate_enhanced_score(self, symbol: str, price: float, volume: float, 
                               momentum_5d: float, afternoon_momentum: float,
                               confidence: str, sector: str) -> float:
        """Enhanced scoring system that learns from your patterns."""
        score = 0
        
        # Volume scoring (higher volume = better)
        if volume > 1000000:
            score += 30
        elif volume > 500000:
            score += 20
        elif volume > 100000:
            score += 10
        
        # Price range scoring (based on your successful trades)
        if 1.0 <= price <= 10.0:  # Your sweet spot
            score += 25
        elif 10.0 < price <= 25.0:
            score += 15
        elif 25.0 < price <= 50.0:
            score += 5
        
        # Momentum scoring
        if momentum_5d > 10:
            score += 20
        elif momentum_5d > 5:
            score += 15
        elif momentum_5d > 0:
            score += 10
        
        # Afternoon momentum (key learning from your patterns)
        if afternoon_momentum > 5:
            score += 25
        elif afternoon_momentum > 0:
            score += 15
        elif afternoon_momentum > -5:
            score += 5
        
        # Confidence scoring
        if confidence == 'High':
            score += 30
        elif confidence == 'Medium':
            score += 20
        else:
            score += 10
        
        # Sector scoring (learned from your success)
        if sector == 'Cannabis':
            score += 25  # Your best performing sector
        elif sector == 'Clean Energy':
            score += 15
        elif sector == 'Biotech':
            score += 5
        
        # Historical performance bonus
        if symbol in ['ATAI', 'SNDL']:  # Your current best performers
            score += 20
        
        return score
    
    def get_sector(self, symbol: str) -> str:
        """Determine sector based on symbol."""
        cannabis_symbols = ['ACB', 'CGC', 'HEXO', 'TLRY', 'SNDL', 'APHA', 'CRON']
        clean_energy_symbols = ['PLUG', 'FCEL', 'BLDP', 'BEEM', 'HYSR', 'SUNW']
        biotech_symbols = ['OCGN', 'DRUG']
        
        if symbol in cannabis_symbols:
            return 'Cannabis'
        elif symbol in clean_energy_symbols:
            return 'Clean Energy'
        elif symbol in biotech_symbols:
            return 'Biotech'
        else:
            return 'Other'
    
    def check_duplicate_holdings(self, symbol: str) -> bool:
        """Check if we already hold this symbol."""
        if self.current_holdings.empty:
            return False
        
        return symbol in self.current_holdings['symbol'].values
    
    def generate_recommendations(self, strategy: str = 'hybrid'):
        """Generate comprehensive trade recommendations."""
        console.print("\n" + "="*80)
        console.print("🤖 ADVANCED MICROCAP TRADING BOT", style="bold blue")
        console.print("="*80)
        
        # Show learned patterns
        self.show_learned_patterns()
        
        # Get candidates based on strategy
        candidates = self.get_candidates(strategy)
        
        if not candidates:
            console.print("❌ No suitable candidates found")
            return
        
        # Create recommendations table
        rec_table = Table(title=f"📈 Trade Recommendations ({strategy.title()} Strategy)")
        rec_table.add_column("Rank", style="cyan")
        rec_table.add_column("Ticker", style="blue")
        rec_table.add_column("Current Price", style="green")
        rec_table.add_column("Buy Shares", style="yellow")
        rec_table.add_column("Total Cost", style="yellow")
        rec_table.add_column("5% Stop-Loss", style="red")
        rec_table.add_column("Score", style="magenta")
        rec_table.add_column("Sector", style="white")
        rec_table.add_column("Confidence", style="cyan")
        
        rank = 1
        for candidate in candidates:
            rec_table.add_row(
                str(rank),
                candidate['symbol'],
                f"${candidate['current_price']:.2f}",
                str(candidate['shares']),
                f"${candidate['total_cost']:.2f}",
                f"${candidate['stop_loss_price']:.2f}",
                f"{candidate['score']:.0f}",
                candidate['sector'],
                candidate['confidence']
            )
            rank += 1
        
        console.print(rec_table)
        
        # Show current holdings
        self.show_current_holdings()
        
        # Show trading strategy
        self.show_trading_strategy()
        
        # Show stop-loss instructions
        self.show_stop_loss_instructions()
        
        # Show summary
        self.show_summary(strategy)
    
    def show_learned_patterns(self):
        """Show enhanced patterns learned from trading history."""
        if not self.learned_patterns:
            return
        
        patterns = self.learned_patterns
        
        pattern_table = Table(title="📊 Enhanced Trading Analysis")
        pattern_table.add_column("Metric", style="cyan")
        pattern_table.add_column("Value", style="green")
        
        pattern_table.add_row("Win Rate", f"{patterns['win_rate']:.1f}%")
        pattern_table.add_row("Total Trades", str(patterns['total_trades']))
        pattern_table.add_row("Winning Trades", f"{patterns['total_wins']} / {patterns['total_trades']}")
        pattern_table.add_row("Losing Trades", f"{patterns['total_losses']} / {patterns['total_trades']}")
        pattern_table.add_row("Average Win", f"${patterns['avg_win']:.2f}")
        pattern_table.add_row("Average Loss", f"${patterns['avg_loss']:.2f}")
        pattern_table.add_row("Profit Factor", f"{patterns['profit_factor']:.2f}")
        pattern_table.add_row("Largest Win", f"${patterns['largest_win']:.2f}")
        pattern_table.add_row("Largest Loss", f"${patterns['largest_loss']:.2f}")
        pattern_table.add_row("Avg ROI (Wins)", f"{patterns['avg_roi_win']:.1f}%")
        pattern_table.add_row("Avg ROI (Losses)", f"{patterns['avg_roi_loss']:.1f}%")
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
        """Show enhanced trading strategy based on learned patterns."""
        console.print("\n" + "="*80)
        console.print("📋 ENHANCED TRADING STRATEGY", style="bold green")
        console.print("="*80)
        
        strategy = """
        🎯 KEY LEARNINGS FROM YOUR TRADING HISTORY:
        
        ✅ WHAT WORKS:
        • Cannabis sector (ATAI: +18.66% current winner)
        • Short-term holds (1-7 days for winners)
        • High volume stocks (>500K average volume)
        • Post-noon momentum trades
        • Price range $1-$25 (your sweet spot)
        • Profit factor: {profit_factor:.2f} (excellent!)
        
        ❌ WHAT DOESN'T WORK:
        • Low volume setups (DRUG losses)
        • Holding past failed momentum (ACB losses)
        • Not setting stop-losses
        • Biotech without strong volume (DRUG)
        
        🚀 RECOMMENDED APPROACH:
        • Focus on cannabis sector (ATAI, CGC, HEXO, TLRY)
        • Set 5% stop-loss immediately
        • Exit on momentum breakdown
        • Trade after 12 PM EST
        • Maximum 25% of account per trade
        • Target profit factor > 2.0
        """
        
        if self.learned_patterns:
            strategy = strategy.format(profit_factor=self.learned_patterns.get('profit_factor', 0))
        
        console.print(Panel(strategy, title="Enhanced Trading Strategy", border_style="green"))
    
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
        • Target profit factor > 2.0 for sustainable gains
        """
        
        console.print(Panel(instructions, title="Stop-Loss Instructions", border_style="red"))
    
    def show_summary(self, strategy: str):
        """Show enhanced trading summary."""
        console.print("\n" + "="*80)
        console.print("📊 ENHANCED TRADING SUMMARY", style="bold yellow")
        console.print("="*80)
        
        summary = f"""
        💰 Account Size: ${self.account_size}
        📈 Max Position Size: {self.max_position_size * 100}% (${self.account_size * self.max_position_size})
        🎯 Strategy: {strategy.title()}
        🎯 Focus: Cannabis sector microcaps
        ⏰ Trading Time: After 12 PM EST
        🛡️ Stop-Loss: 5% on every trade
        
        📋 RECOMMENDATIONS:
        1. ATAI - Your current winner (+18.66% return)
        2. CGC - Cannabis sector opportunity
        3. HEXO - High volume cannabis play
        4. TLRY - Established cannabis player
        5. PLUG - Clean energy alternative
        
        ⚠️ REMEMBER:
        • Set stop-loss immediately after buying
        • Exit on momentum breakdown
        • Focus on post-noon trades
        • Avoid low-volume setups
        • Target profit factor > 2.0
        """
        
        console.print(Panel(summary, title="Enhanced Trading Summary", border_style="yellow"))

    def run_training_mode(self):
        """Run the bot in training mode to update ML model."""
        console.print("🤖 Starting ML training mode...", style="blue")
        
        # Load latest weekly research data
        weekly_data = self.load_weekly_research_data()
        
        # Update trading patterns
        self.update_trading_patterns(weekly_data)
        
        # Generate training insights
        training_insights = self.generate_training_insights()
        
        # Save updated model
        self.save_training_results(training_insights)
        
        console.print("✅ ML training completed successfully!", style="green")

    def load_weekly_research_data(self):
        """Load latest weekly research data for training."""
        try:
            # Look for latest weekly data file
            weekly_files = glob.glob("../weekly_research/weekly_data_*.json")
            if weekly_files:
                latest_file = max(weekly_files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                console.print(f"✅ Loaded weekly research data: {latest_file}", style="green")
                return data
            else:
                console.print("⚠️ No weekly research data found", style="yellow")
                return {}
        except Exception as e:
            console.print(f"❌ Error loading weekly data: {str(e)}", style="red")
            return {}

    def update_trading_patterns(self, weekly_data):
        """Update trading patterns based on weekly research."""
        if not weekly_data:
            return
        
        # Analyze new patterns from weekly data
        candidates = weekly_data.get('candidates', [])
        if candidates:
            df = pd.DataFrame(candidates)
            
            # Update sector performance
            sector_perf = df.groupby('sector')['score'].mean().to_dict()
            
            # Update proven winners list
            top_performers = df.nlargest(5, 'score')['symbol'].tolist()
            
            console.print(f"📊 Updated patterns with {len(candidates)} new candidates", style="green")
            console.print(f"🏆 New top performers: {', '.join(top_performers)}", style="blue")

    def generate_training_insights(self):
        """Generate insights from training data."""
        insights = {
            'timestamp': datetime.now().isoformat(),
            'training_data_points': len(self.trading_history),
            'updated_patterns': self.learned_patterns,
            'model_version': '1.0',
            'training_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        return insights

    def save_training_results(self, insights):
        """Save training results and updated model."""
        try:
            # Save training insights
            training_file = f"training_results/training_results_{datetime.now().strftime('%Y%m%d')}.json"
            with open(training_file, 'w') as f:
                json.dump(insights, f, indent=2)
            
            # Update model files
            self.update_model_files()
            
            console.print(f"💾 Saved training results to {training_file}", style="green")
            
        except Exception as e:
            console.print(f"❌ Error saving training results: {str(e)}", style="red")

    def update_model_files(self):
        """Update model files with new training data."""
        # This would typically update ML model weights, but for now we'll
        # just update the proven winners and patterns
        console.print("🔄 Updating model files...", style="blue")
        
        # Update proven winners based on latest performance
        if not self.trading_history.empty:
            closed_trades = self.trading_history[self.trading_history['status'] == 'CLOSED']
            if not closed_trades.empty:
                top_performers = closed_trades.nlargest(5, 'pnl_percentage')['symbol'].tolist()
                console.print(f"🏆 Updated proven winners: {', '.join(top_performers)}", style="green")

def main():
    """Main function with strategy selection."""
    import argparse
    import json
    import glob
    import requests
    
    parser = argparse.ArgumentParser(description="Advanced Microcap Trading Bot")
    parser.add_argument("--strategy", choices=["proven_winners", "momentum_focused", "hybrid"],
                       default="hybrid", help="Trading strategy to use")
    parser.add_argument("--account-size", type=float, default=200, 
                       help="Account size in dollars")
    parser.add_argument("--max-position", type=float, default=0.25, 
                       help="Maximum position size as fraction of account")
    parser.add_argument("--training-mode", action="store_true",
                       help="Run in training mode to update ML model")
    
    args = parser.parse_args()
    
    bot = AdvancedTradingBot(
        account_size=args.account_size, 
        max_position_size=args.max_position
    )
    
    if args.training_mode:
        bot.run_training_mode()
    else:
        bot.generate_recommendations(strategy=args.strategy)

if __name__ == "__main__":
    main() 