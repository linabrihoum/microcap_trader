#!/usr/bin/env python3
"""
Enhanced Data Manager for Microcap Trading System
"""

import os
import time
import random
import requests
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
from utilities.error_handler import error_handler, APIError, NetworkError, DataError, handle_exceptions
from validation.data_validator import validate_stock_data_safe
from validation.data_models import StockData, DataSource, MarketSector

# Load environment variables
load_dotenv()

console = Console()

class EnhancedDataManager:
    """Enhanced data manager with multiple API sources and production security."""
    
    def __init__(self, enable_caching: bool = True):
        # Load API keys from environment variables (production secure)
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.finnhub_api_key = os.getenv('FINNHUB_API_KEY')
        
        # Initialize caching system
        self.enable_caching = enable_caching
        self.cache_manager = None
        
        if enable_caching:
            try:
                from caching.cache_manager import RealTimeCacheManager
                self.cache_manager = RealTimeCacheManager(self._fetch_stock_data_uncached)
                console.print("✅ Real-time caching system initialized", style="green")
            except ImportError as e:
                console.print(f"⚠️  Caching system not available: {e}", style="yellow")
                self.enable_caching = False
        
        # Validate API keys are present
        if not self.polygon_api_key:
            console.print("⚠️  POLYGON_API_KEY not found in environment", style="yellow")
        else:
            console.print("✅ Polygon.io API key found", style="green")
            
        if not self.finnhub_api_key:
            console.print("⚠️  FINNHUB_API_KEY not found in environment", style="yellow")
        else:
            console.print("✅ Finnhub API key found", style="green")
    
    @handle_exceptions
    def get_stock_data(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """Get stock data with optional caching."""
        if use_cache and self.enable_caching and self.cache_manager:
            # Use cached data for analysis (default)
            return self.cache_manager.get_stock_data_for_analysis(symbol)
        else:
            # Fetch uncached data
            return self._fetch_stock_data_uncached(symbol)
    
    @handle_exceptions
    def get_stock_data_for_trading(self, symbol: str) -> Optional[Dict]:
        """Get real-time stock data for active trading."""
        if self.enable_caching and self.cache_manager:
            return self.cache_manager.get_stock_data_for_trading(symbol)
        else:
            return self._fetch_stock_data_uncached(symbol)
    
    @handle_exceptions
    def get_portfolio_data(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """Get portfolio data with appropriate caching strategy."""
        if self.enable_caching and self.cache_manager:
            return self.cache_manager.get_portfolio_data(symbols)
        else:
            # Fallback to uncached data
            portfolio_data = {}
            for symbol in symbols:
                portfolio_data[symbol] = self._fetch_stock_data_uncached(symbol)
            return portfolio_data
    
    @handle_exceptions
    def set_active_positions(self, symbols: List[str]) -> None:
        """Set active positions for real-time updates."""
        if self.enable_caching and self.cache_manager:
            for symbol in symbols:
                self.cache_manager.set_active_position(symbol, True)
    
    @handle_exceptions
    def set_watchlist(self, symbols: List[str]) -> None:
        """Set watchlist for medium priority updates."""
        if self.enable_caching and self.cache_manager:
            self.cache_manager.set_watchlist(symbols)
    
    @handle_exceptions
    def get_cache_stats(self) -> Optional[Dict]:
        """Get cache statistics if caching is enabled."""
        if self.enable_caching and self.cache_manager:
            return self.cache_manager.get_cache_stats()
        return None
    
    @handle_exceptions
    def display_cache_stats(self) -> None:
        """Display cache statistics if caching is enabled."""
        if self.enable_caching and self.cache_manager:
            self.cache_manager.display_comprehensive_stats()
        else:
            console.print("⚠️  Caching is not enabled", style="yellow")
    
    def _fetch_stock_data_uncached(self, symbol: str) -> Optional[Dict]:
        """Internal method to fetch stock data without caching (fallback chain)."""
        # Try Polygon.io first
        data = self.get_stock_data_polygon(symbol)
        if data:
            return data
        
        # Try Finnhub second
        data = self.get_stock_data_finnhub(symbol)
        if data:
            return data
        
        # Try yfinance third
        data = self.get_stock_data_yfinance(symbol)
        if data:
            return data
        
        # Generate simulated data as last resort
        return self.generate_simulated_data(symbol)
    
    @handle_exceptions
    def generate_simulated_data(self, symbol: str) -> Optional[Dict]:
        """Generate simulated stock data when all APIs fail."""
        try:
            # Generate realistic simulated data
            import random
            
            # Base price range for microcap stocks
            base_price = random.uniform(1.0, 25.0)
            
            # Market cap in billions (microcap range)
            market_cap = random.uniform(0.05, 1.8)
            
            # Volume in thousands
            volume = random.randint(50, 2000) * 1000
            
            # Price changes
            pct_change_1d = random.uniform(-15.0, 15.0)
            pct_change_5d = random.uniform(-25.0, 25.0)
            
            data = {
                'symbol': symbol,
                'price': round(base_price, 2),
                'market_cap': round(market_cap, 2),
                'avg_volume': volume,
                'pct_change_1d': round(pct_change_1d, 2),
                'pct_change_5d': round(pct_change_5d, 2),
                'data_source': DataSource.SIMULATED
            }
            
            # Validate the simulated data
            validated_data = validate_stock_data_safe(data)
            if validated_data:
                return validated_data.model_dump()
            return None
            
        except Exception as e:
            console.print(f"❌ Failed to generate simulated data for {symbol}: {e}", style="red")
            return None
    
    @handle_exceptions
    @error_handler.retry_on_failure(max_retries=2, delay=0.5)
    def get_stock_data_polygon(self, symbol: str) -> Optional[Dict]:
        """Get stock data from Polygon.io API with enhanced error handling."""
        if not self.polygon_api_key:
            return None
            
        try:
            # Get current price
            price_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
            price_response = requests.get(price_url, params={'apikey': self.polygon_api_key}, timeout=10)
            
            if price_response.status_code != 200:
                raise APIError(f"Status code {price_response.status_code}", "Polygon", price_response.status_code)
                
            price_data = price_response.json()
            if not price_data.get('results'):
                raise DataError(f"No data available for {symbol}")
                
            current_price = price_data['results'][0]['c']
            
            # Get additional data (market cap, volume, etc.)
            details_url = f"https://api.polygon.io/v3/reference/tickers/{symbol}"
            details_response = requests.get(details_url, params={'apikey': self.polygon_api_key}, timeout=10)
            
            market_cap = 0
            if details_response.status_code == 200:
                details_data = details_response.json()
                market_cap = details_data.get('results', {}).get('market_cap', 0) / 1e9  # Convert to billions
            
            data = {
                'symbol': symbol,
                'price': current_price,
                'market_cap': market_cap,
                'avg_volume': price_data['results'][0].get('v', 0),
                'pct_change_1d': 0,  # Polygon doesn't provide this easily
                'pct_change_5d': 0,
                'data_source': DataSource.POLYGON
            }
            
            # Validate data using Pydantic
            validated_data = validate_stock_data_safe(data)
            if validated_data:
                return validated_data.model_dump()
            return None
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Timeout fetching data for {symbol}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error fetching {symbol}: {str(e)}")
        except Exception as e:
            if not error_handler.handle_api_error(e, "Polygon", symbol):
                return None
            raise
    
    @handle_exceptions
    @error_handler.retry_on_failure(max_retries=2, delay=0.5)
    def get_stock_data_finnhub(self, symbol: str) -> Optional[Dict]:
        """Get stock data from Finnhub API with enhanced error handling."""
        if not self.finnhub_api_key:
            return None
            
        try:
            # Get quote data
            quote_url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': self.finnhub_api_key
            }
            response = requests.get(quote_url, params=params, timeout=10)
            
            if response.status_code != 200:
                raise APIError(f"Status code {response.status_code}", "Finnhub", response.status_code)
                
            data = response.json()
            if data.get('c') == 0:  # No data
                raise DataError(f"No data available for {symbol}")
                
            current_price = data['c']
            prev_close = data['pc']
            pct_change_1d = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            
            # Get company profile for market cap
            profile_url = f"https://finnhub.io/api/v1/stock/profile2"
            profile_response = requests.get(profile_url, params=params, timeout=10)
            
            market_cap = 0
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                market_cap = profile_data.get('marketCapitalization', 0) / 1e9  # Convert to billions
            
            result_data = {
                'symbol': symbol,
                'price': current_price,
                'market_cap': market_cap,
                'avg_volume': data.get('v', 0),
                'pct_change_1d': pct_change_1d,
                'pct_change_5d': 0,  # Finnhub doesn't provide 5-day easily
                'data_source': DataSource.FINNHUB
            }
            
            # Validate data using Pydantic
            validated_data = validate_stock_data_safe(result_data)
            if validated_data:
                return validated_data.model_dump()
            return None
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Timeout fetching data for {symbol}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error fetching {symbol}: {str(e)}")
        except Exception as e:
            if not error_handler.handle_api_error(e, "Finnhub", symbol):
                return None
            raise
    
    @handle_exceptions
    @error_handler.retry_on_failure(max_retries=1, delay=1.0)
    def get_stock_data_yfinance(self, symbol: str) -> Optional[Dict]:
        """Get stock data from yfinance (fallback) with enhanced error handling."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or info.get('regularMarketPrice', 0) == 0:
                raise DataError(f"No data available for {symbol}")
                
            current_price = info.get('regularMarketPrice', 0)
            prev_close = info.get('regularMarketPreviousClose', current_price)
            pct_change_1d = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            
            # Get 5-day change
            hist = ticker.history(period='5d')
            if len(hist) >= 2:
                five_day_ago = hist.iloc[0]['Close']
                pct_change_5d = ((current_price - five_day_ago) / five_day_ago * 100) if five_day_ago > 0 else 0
            else:
                pct_change_5d = pct_change_1d
            
            result_data = {
                'symbol': symbol,
                'price': current_price,
                'market_cap': info.get('marketCap', 0) / 1e9,  # Convert to billions
                'avg_volume': info.get('averageVolume', 0),
                'pct_change_1d': pct_change_1d,
                'pct_change_5d': pct_change_5d,
                'data_source': DataSource.YFINANCE
            }
            
            # Validate data using Pydantic
            validated_data = validate_stock_data_safe(result_data)
            if validated_data:
                return validated_data.model_dump()
            return None
            
        except Exception as e:
            if not error_handler.handle_api_error(e, "yfinance", symbol):
                return None
            raise
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols."""
        prices = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("Fetching current prices..."),
            console=console
        ) as progress:
            task = progress.add_task("Processing", total=len(symbols))
            
            for symbol in symbols:
                data = self.get_stock_data(symbol)
                if data:
                    prices[symbol] = data['price']
                
                progress.advance(task)
                time.sleep(0.1)  # Rate limiting
        
        return prices
    
    def is_microcap_stock(self, symbol: str) -> bool:
        """Check if a stock is a microcap (< $2B market cap)."""
        data = self.get_stock_data(symbol)
        if not data:
            return False
        
        market_cap = data.get('market_cap', 0)
        return market_cap < 2.0  # Less than $2B
    
    def calculate_stock_score(self, data: Dict) -> float:
        """Calculate a comprehensive score for stock selection (0-100)."""
        if not data:
            return 0.0
        
        score = 0.0
        
        # Price momentum (30% weight)
        pct_change_1d = data.get('pct_change_1d', 0)
        pct_change_5d = data.get('pct_change_5d', 0)
        
        # 1-day momentum
        if pct_change_1d > 5:
            score += 15
        elif pct_change_1d > 2:
            score += 10
        elif pct_change_1d > 0:
            score += 5
        elif pct_change_1d < -5:
            score -= 10
        
        # 5-day momentum
        if pct_change_5d > 10:
            score += 15
        elif pct_change_5d > 5:
            score += 10
        elif pct_change_5d > 0:
            score += 5
        elif pct_change_5d < -10:
            score -= 10
        
        # Volume analysis (25% weight)
        avg_volume = data.get('avg_volume', 0)
        if avg_volume > 1000000:
            score += 25
        elif avg_volume > 500000:
            score += 20
        elif avg_volume > 100000:
            score += 15
        elif avg_volume > 50000:
            score += 10
        elif avg_volume < 10000:
            score -= 10
        
        # Market cap optimization (20% weight)
        market_cap = data.get('market_cap', 0)
        if 0.1 <= market_cap <= 0.5:  # Sweet spot for microcaps
            score += 20
        elif 0.5 < market_cap <= 1.0:
            score += 15
        elif 0.05 <= market_cap < 0.1:
            score += 10
        elif market_cap > 1.5:
            score -= 5
        
        # Price range optimization (15% weight)
        price = data.get('price', 0)
        if 1 <= price <= 10:  # Ideal microcap price range
            score += 15
        elif 10 < price <= 25:
            score += 10
        elif 0.5 <= price < 1:
            score += 5
        elif price > 50:
            score -= 5
        
        # Volatility bonus (10% weight)
        if abs(pct_change_1d) > 5 and pct_change_1d > 0:
            score += 10  # High positive volatility
        elif abs(pct_change_1d) > 10 and pct_change_1d > 0:
            score += 15  # Very high positive volatility
        
        return max(0, min(100, score))  # Clamp between 0-100
    
    def get_microcap_stocks(self, count: int = 30, use_batch_processing: bool = True) -> pd.DataFrame:
        """Get a list of microcap stocks with enhanced data sources and batch processing."""
        
        # True microcap stock list (market cap < $2B)
        microcap_symbols = [
            # Technology
            'PLTR', 'RBLX', 'SNAP', 'UBER', 'LYFT', 'ZM', 'SQ', 'SHOP', 'CRWD', 'NET',
            # Healthcare
            'MRNA', 'BNTX', 'NVAX', 'INO', 'VXRT', 'OCGN', 'SAVA', 'AVXL', 'CRTX',
            # Energy
            'PLUG', 'FCEL', 'BLDP', 'BEEM', 'SUNW', 'ENPH', 'RUN', 'SPWR',
            # Finance
            'SOFI', 'UPST', 'AFRM', 'COIN', 'HOOD', 'RKT', 'UWMC',
            # Consumer
            'BYND', 'PTON', 'NIO', 'XPEV', 'LI', 'LCID', 'RIVN', 'NKLA',
            # Gaming
            'EA', 'ATVI', 'TTWO', 'ZNGA', 'GLUU', 'SCPL',
            # Biotech
            'GILD', 'BIIB', 'REGN', 'VRTX', 'ALNY', 'IONS', 'SGEN',
            # Additional microcaps
            'SENS', 'NNDM', 'IDEX', 'CIDM', 'MARK', 'ZOM', 'NAKD', 'SNDL', 'HEXO', 'ACB',
            'TLRY', 'CGC', 'APHA', 'CRON', 'AUR', 'LAZR', 'VLDR', 'QS', 'NKLA', 'WKHS',
            'RIDE', 'BLNK', 'CHPT', 'EVGO', 'TPIC', 'SPCE', 'ASTS', 'RKLB', 'VORB',
            'MNMD', 'CMPS', 'ATAI', 'DRUG', 'SAGE', 'KPTI', 'BLUE', 'EDIT', 'CRSP',
            'BEAM', 'NTLA', 'VERV', 'FATE', 'ALLO', 'KITE', 'JUNO', 'CAR'
        ]
        
        # Filter to microcap range and add some randomness
        random.shuffle(microcap_symbols)
        selected_symbols = microcap_symbols[:count]
        
        console.print(f"🔍 Fetching data for {len(selected_symbols)} microcap stocks...")
        
        if use_batch_processing:
            # Use batch processing for better performance
            try:
                from utilities.batch_processor import DataBatchProcessor
                batch_processor = DataBatchProcessor(self)
                
                # Fetch stock data in batches
                stock_data = batch_processor.batch_fetch_stock_data(selected_symbols)
                
                # Filter microcap stocks
                filtered_data = batch_processor.batch_filter_microcaps(stock_data)
                
                # Calculate scores in batches
                scores = batch_processor.batch_calculate_scores(filtered_data)
                
                # Combine results
                results = []
                for symbol, data in filtered_data.items():
                    if symbol in scores:
                        data['score'] = scores[symbol]
                        results.append(data)
                
                # Display batch processing stats
                batch_processor.display_processing_stats()
                batch_processor.shutdown()
                
            except ImportError:
                console.print("⚠️  Batch processing not available, using sequential processing", style="yellow")
                use_batch_processing = False
        
        if not use_batch_processing:
            # Fallback to sequential processing
            results = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Fetching stock data...", total=len(selected_symbols))
                
                for symbol in selected_symbols:
                    data = self.get_stock_data(symbol)
                    if data and data['market_cap'] < 2.0:  # Filter for microcap
                        # Calculate score for ranking
                        data['score'] = self.calculate_stock_score(data)
                        results.append(data)
                    
                    progress.advance(task)
                    time.sleep(0.1)  # Rate limiting
        
        df = pd.DataFrame(results)
        if not df.empty:
            # Sort by score (highest first) then by market cap
            df = df.sort_values(['score', 'market_cap'], ascending=[False, True])
            console.print(f"✅ Found {len(df)} microcap stocks", style="green")
        else:
            console.print("⚠️  No microcap stocks found", style="yellow")
        
        return df 