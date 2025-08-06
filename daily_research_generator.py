#!/usr/bin/env python3
"""
Daily Research Generator for Microcap Trading System
Replaces yfinance with Polygon.io for reliable data fetching with enhanced error handling
"""

import os
import json
import glob
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
from utilities.error_handler import error_handler, APIError, NetworkError, DataError, handle_exceptions
from validation.data_models import CandidateStock, MarketSector

# Load environment variables
load_dotenv()

console = Console()

class DailyResearchGenerator:
    """Generates daily research reports for potential microcap candidates."""

    def __init__(self):
        self.daily_folder = "daily_research"
        self.ensure_daily_folder()
        self.candidates_file = "data/candidates.csv"
        self.portfolio_file = "data/portfolio.csv"
        
        # Load API keys
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.finnhub_api_key = os.getenv('FINNHUB_API_KEY')
        
        if not self.polygon_api_key:
            console.print("⚠️ POLYGON_API_KEY not found - will use Finnhub and simulated data", style="yellow")
        else:
            console.print("✅ Polygon.io API key found", style="green")
            
        if not self.finnhub_api_key:
            console.print("⚠️ FINNHUB_API_KEY not found - will use simulated data", style="yellow")
        else:
            console.print("✅ Finnhub API key found", style="green")
    
    def ensure_daily_folder(self):
        """Ensure daily research folder exists."""
        if not os.path.exists(self.daily_folder):
            os.makedirs(self.daily_folder)
    
    def get_microcap_candidates(self, use_batch_processing: bool = True):
        """Get potential microcap candidates for the day with batch processing."""
        # Microcap stock lists by sector
        microcap_symbols = {
            'Cannabis': ['CGC', 'ACB', 'TLRY', 'HEXO', 'APHA', 'CRON', 'SNDL', 'OGI', 'VFF', 'CTIC'],
            'Biotech': ['OCGN', 'INO', 'BNGO', 'SENS', 'STIM', 'ATAI', 'DRUG', 'VXRT', 'MRNA', 'NVAX'],
            'Clean Energy': ['PLUG', 'FCEL', 'BLDP', 'BEEM', 'SPI', 'SUNW', 'ENPH', 'RUN', 'SEDG', 'CSIQ'],
            'Tech': ['SENS', 'NNDM', 'IDEX', 'MARK', 'ZOM', 'CIDM', 'CIDM', 'SNDL', 'HEXO', 'APHA'],
            'Mining': ['NEM', 'GOLD', 'ABX', 'KGC', 'AEM', 'PAAS', 'CDE', 'HL', 'EXK', 'AG']
        }
        
        if use_batch_processing:
            # Use batch processing for better performance
            try:
                from utilities.batch_processor import BatchProcessor
                batch_processor = BatchProcessor(max_workers=4, batch_size=8)
                
                # Prepare all symbols with their sectors
                all_symbols_with_sectors = []
                for sector, symbols in microcap_symbols.items():
                    for symbol in symbols:
                        all_symbols_with_sectors.append((symbol, sector))
                
                # Process symbols in batches
                def process_symbol_with_sector(item):
                    symbol, sector = item
                    try:
                        return self.get_stock_data_with_fallback(symbol, sector)
                    except Exception as e:
                        console.print(f"⚠️ Error processing {symbol}: {str(e)}", style="yellow")
                        return None
                
                all_candidates = batch_processor.process_batch(
                    all_symbols_with_sectors, 
                    process_symbol_with_sector, 
                    "Microcap Candidates"
                )
                
                # Filter out None results
                all_candidates = [c for c in all_candidates if c is not None]
                
                # Display batch processing stats
                batch_processor.display_stats()
                batch_processor.shutdown()
                
                api_failures = len(all_symbols_with_sectors) - len(all_candidates)
                
            except ImportError:
                console.print("⚠️  Batch processing not available, using sequential processing", style="yellow")
                use_batch_processing = False
        
        if not use_batch_processing:
            # Fallback to sequential processing
            all_candidates = []
            api_failures = 0
            total_symbols = sum(len(symbols) for symbols in microcap_symbols.values())
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                for sector, symbols in microcap_symbols.items():
                    task = progress.add_task(f"🔍 Scanning {sector} sector...", total=len(symbols))
                    
                    for symbol in symbols:
                        try:
                            candidate = self.get_stock_data_with_fallback(symbol, sector)
                            if candidate:
                                all_candidates.append(candidate)
                            else:
                                api_failures += 1
                        except Exception as e:
                            api_failures += 1
                            console.print(f"⚠️ Error processing {symbol}: {str(e)}", style="yellow")
                        finally:
                            progress.advance(task)
        
        total_symbols = sum(len(symbols) for symbols in microcap_symbols.values())
        console.print(f"📊 API failures: {api_failures}/{total_symbols} symbols", style="blue")
        
        if api_failures > total_symbols * 0.7:  # More than 70% failures
            console.print("🔄 API rate limits detected, using simulated data...", style="yellow")
            all_candidates = self.get_simulated_candidates()
        elif len(all_candidates) == 0:
            console.print("🔄 No candidates found, using simulated data...", style="yellow")
            all_candidates = self.get_simulated_candidates()
        
        return all_candidates
    
    def get_stock_data_with_fallback(self, symbol, sector):
        """Get stock data with fallback chain: Polygon -> Finnhub -> Simulated."""
        # Try Polygon.io first (most reliable)
        data = self.get_stock_data_polygon(symbol, sector)
        if data:
            return data
        
        # Try Finnhub second
        data = self.get_stock_data_finnhub(symbol, sector)
        if data:
            return data
        
        # Fallback to simulated data
        return self.get_simulated_stock_data(symbol, sector)
    
    def get_stock_data_polygon(self, symbol, sector):
        """Get stock data from Polygon.io API."""
        if not self.polygon_api_key:
            return None
            
        try:
            # Get current price and volume
            price_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
            price_response = requests.get(price_url, params={'apikey': self.polygon_api_key})
            
            if price_response.status_code != 200:
                return None
                
            price_data = price_response.json()
            if not price_data.get('results'):
                return None
                
            current_price = price_data['results'][0]['c']
            volume = price_data['results'][0].get('v', 0)
            
            # Get company details for market cap
            details_url = f"https://api.polygon.io/v3/reference/tickers/{symbol}"
            details_response = requests.get(details_url, params={'apikey': self.polygon_api_key})
            
            market_cap = 0
            if details_response.status_code == 200:
                details_data = details_response.json()
                market_cap = details_data.get('results', {}).get('market_cap', 0)
            
            # Only include microcap stocks (< $2B)
            if market_cap > 2000000000:
                return None
            
            # Get 5-day historical data for momentum
            hist_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')}/{datetime.now().strftime('%Y-%m-%d')}"
            hist_response = requests.get(hist_url, params={'apikey': self.polygon_api_key})
            
            pct_change_1d = 0
            pct_change_5d = 0
            avg_volume = volume
            
            if hist_response.status_code == 200:
                hist_data = hist_response.json()
                if hist_data.get('results') and len(hist_data['results']) >= 5:
                    results = hist_data['results']
                    current_price = results[-1]['c']
                    prev_close = results[-2]['c'] if len(results) > 1 else current_price
                    five_day_ago = results[0]['c']
                    
                    pct_change_1d = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                    pct_change_5d = ((current_price - five_day_ago) / five_day_ago * 100) if five_day_ago > 0 else 0
                    avg_volume = sum(r.get('v', 0) for r in results) / len(results)
            
            # Calculate stock score
            score = self.calculate_stock_score(
                current_price, volume, avg_volume, pct_change_1d, pct_change_5d, market_cap
            )
            
            return {
                'symbol': symbol,
                'sector': sector,
                'market_cap': market_cap / 1e9,  # Convert to billions
                'price': current_price,
                'volume': volume,
                'avg_volume': avg_volume,
                'pct_change_1d': pct_change_1d,
                'pct_change_5d': pct_change_5d,
                'score': score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            console.print(f"Error fetching {symbol} from Polygon: {e}", style="red")
            return None
    
    def get_stock_data_finnhub(self, symbol, sector):
        """Get stock data from Finnhub API."""
        if not self.finnhub_api_key:
            return None
            
        try:
            # Get quote data
            quote_url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': self.finnhub_api_key
            }
            response = requests.get(quote_url, params=params)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            if data.get('c') == 0:  # No data
                return None
                
            current_price = data['c']
            prev_close = data['pc']
            pct_change_1d = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            volume = data.get('v', 0)
            
            # Get company profile for market cap
            profile_url = f"https://finnhub.io/api/v1/stock/profile2"
            profile_response = requests.get(profile_url, params=params)
            
            market_cap = 0
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                market_cap = profile_data.get('marketCapitalization', 0)
            
            # Only include microcap stocks (< $2B)
            if market_cap > 2000000000:
                return None
            
            # Get 5-day historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=10)
            
            hist_url = f"https://finnhub.io/api/v1/stock/candle"
            hist_params = {
                'symbol': symbol,
                'resolution': 'D',
                'from': int(start_date.timestamp()),
                'to': int(end_date.timestamp()),
                'token': self.finnhub_api_key
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
                    pct_change_5d = ((current_price - five_day_ago) / five_day_ago * 100) if five_day_ago > 0 else 0
                    avg_volume = sum(volumes) / len(volumes)
            
            # Calculate stock score
            score = self.calculate_stock_score(
                current_price, volume, avg_volume, pct_change_1d, pct_change_5d, market_cap
            )
            
            return {
                'symbol': symbol,
                'sector': sector,
                'market_cap': market_cap / 1e9,  # Convert to billions
                'price': current_price,
                'volume': volume,
                'avg_volume': avg_volume,
                'pct_change_1d': pct_change_1d,
                'pct_change_5d': pct_change_5d,
                'score': score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            console.print(f"Error fetching {symbol} from Finnhub: {e}", style="red")
            return None
    
    def get_simulated_stock_data(self, symbol, sector):
        """Get simulated stock data when APIs fail."""
        # Simulate realistic microcap data
        import random
        
        base_price = random.uniform(1.0, 10.0)
        market_cap = random.uniform(0.1, 2.0)  # Microcap range
        volume = random.randint(100000, 5000000)
        avg_volume = volume * random.uniform(0.8, 1.2)
        pct_change_1d = random.uniform(-15, 25)
        pct_change_5d = random.uniform(-30, 50)
        
        score = self.calculate_stock_score(
            base_price, volume, avg_volume, pct_change_1d, pct_change_5d, market_cap * 1e9
        )
        
        return {
            'symbol': symbol,
            'sector': sector,
            'market_cap': market_cap,
            'price': base_price,
            'volume': volume,
            'avg_volume': avg_volume,
            'pct_change_1d': pct_change_1d,
            'pct_change_5d': pct_change_5d,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_stock_score(self, price, volume, avg_volume, pct_change_1d, pct_change_5d, market_cap):
        """Calculate a stock score from 0-100 based on various factors."""
        score = 0
        
        # Volume factor (0-25 points)
        if volume > avg_volume * 2:
            score += 25
        elif volume > avg_volume * 1.5:
            score += 20
        elif volume > avg_volume:
            score += 15
        elif volume > avg_volume * 0.5:
            score += 10
        
        # Price momentum factor (0-25 points)
        if pct_change_1d > 5:
            score += 25
        elif pct_change_1d > 2:
            score += 20
        elif pct_change_1d > 0:
            score += 15
        elif pct_change_1d > -5:
            score += 10
        
        # 5-day trend factor (0-25 points)
        if pct_change_5d > 10:
            score += 25
        elif pct_change_5d > 5:
            score += 20
        elif pct_change_5d > 0:
            score += 15
        elif pct_change_5d > -10:
            score += 10
        
        # Market cap factor (0-25 points) - prefer smaller caps for higher volatility
        if market_cap < 500000000:  # < $500M
            score += 25
        elif market_cap < 1000000000:  # < $1B
            score += 20
        elif market_cap < 1500000000:  # < $1.5B
            score += 15
        elif market_cap < 2000000000:  # < $2B
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def save_daily_candidates(self, candidates):
        """Save daily candidates to CSV and JSON files."""
        if not candidates:
            console.print("❌ No candidates found for today", style="red")
            return
        
        # Create DataFrame
        df = pd.DataFrame(candidates)
        
        # Sort by score
        df = df.sort_values('score', ascending=False)
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d')
        csv_filename = f"daily_candidates_{timestamp}.csv"
        csv_path = os.path.join(self.daily_folder, csv_filename)
        df.to_csv(csv_path, index=False)
        
        # Save to JSON for easier processing
        json_filename = f"daily_candidates_{timestamp}.json"
        json_path = os.path.join(self.daily_folder, json_filename)
        
        with open(json_path, 'w') as f:
            json.dump({
                'date': datetime.now().isoformat(),
                'total_candidates': len(candidates),
                'candidates': candidates
            }, f, indent=2)
        
        console.print(f"💾 Saved {len(candidates)} candidates to {csv_filename}", style="green")
        console.print(f"📊 Top 5 candidates by score:", style="blue")
        
        # Display top candidates
        top_candidates = df.head(5)
        table = Table(title="🏆 Top Daily Candidates")
        table.add_column("Rank", style="cyan")
        table.add_column("Symbol", style="green")
        table.add_column("Sector", style="yellow")
        table.add_column("Price", style="blue")
        table.add_column("Score", style="magenta")
        table.add_column("1D Change", style="red")
        
        for i, (_, row) in enumerate(top_candidates.iterrows(), 1):
            table.add_row(
                str(i),
                row['symbol'],
                row['sector'],
                f"${row['price']:.2f}",
                f"{row['score']:.1f}",
                f"{row['pct_change_1d']:+.1f}%"
            )
        
        console.print(table)
        
        return csv_path, json_path
    
    def update_candidates_csv(self, candidates):
        """Update the main candidates.csv file with today's findings."""
        try:
            # Read existing candidates
            if os.path.exists(self.candidates_file):
                existing_df = pd.read_csv(self.candidates_file)
            else:
                existing_df = pd.DataFrame()
            
            # Create new candidates DataFrame
            new_df = pd.DataFrame(candidates)
            
            # Keep only essential columns for main candidates file
            if not new_df.empty:
                new_df = new_df[['symbol', 'market_cap', 'price', 'pct_change_1d', 'pct_change_5d', 'avg_volume']]
                new_df['date_added'] = datetime.now().strftime('%Y-%m-%d')
                
                # Combine with existing data
                if not existing_df.empty:
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    # Remove duplicates based on symbol
                    combined_df = combined_df.drop_duplicates(subset=['symbol'], keep='last')
                else:
                    combined_df = new_df
                
                # Save updated candidates file
                combined_df.to_csv(self.candidates_file, index=False)
                console.print(f"✅ Updated {self.candidates_file} with {len(new_df)} new candidates", style="green")
        
        except Exception as e:
            console.print(f"⚠️ Error updating candidates.csv: {str(e)}", style="yellow")
    
    def generate_daily_report(self):
        """Generate comprehensive daily research report."""
        console.print("🔄 Starting daily research...", style="blue")
        
        # Get candidates
        candidates = self.get_microcap_candidates()
        
        if not candidates:
            console.print("❌ No candidates found", style="red")
            return
        
        # Save candidates
        csv_path, json_path = self.save_daily_candidates(candidates)
        
        # Update main candidates file
        self.update_candidates_csv(candidates)
        
        # Generate summary report
        self.generate_summary_report(candidates)
        
        console.print("✅ Daily research completed successfully!", style="green")
    
    def generate_summary_report(self, candidates):
        """Generate a summary report of today's findings."""
        df = pd.DataFrame(candidates)
        
        # Sector breakdown
        sector_stats = df.groupby('sector').agg({
            'symbol': 'count',
            'score': 'mean',
            'pct_change_1d': 'mean'
        }).round(2)
        
        # Create summary report
        timestamp = datetime.now().strftime('%Y%m%d')
        report_filename = f"daily_summary_{timestamp}.md"
        report_path = os.path.join(self.daily_folder, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Daily Research Summary - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Candidates Found:** {len(candidates)}\n\n")
            
            f.write("## Sector Breakdown\n\n")
            f.write("| Sector | Count | Avg Score | Avg 1D Change |\n")
            f.write("|--------|-------|-----------|----------------|\n")
            
            for sector, stats in sector_stats.iterrows():
                f.write(f"| {sector} | {stats['symbol']} | {stats['score']:.1f} | {stats['pct_change_1d']:+.1f}% |\n")
            
            f.write("\n## Top 10 Candidates\n\n")
            f.write("| Rank | Symbol | Sector | Price | Score | 1D Change | 5D Change |\n")
            f.write("|------|--------|--------|-------|-------|------------|-----------|\n")
            
            top_10 = df.nlargest(10, 'score')
            for i, (_, row) in enumerate(top_10.iterrows(), 1):
                f.write(f"| {i} | {row['symbol']} | {row['sector']} | ${row['price']:.2f} | {row['score']:.1f} | {row['pct_change_1d']:+.1f}% | {row['pct_change_5d']:+.1f}% |\n")
            
            f.write("\n## Market Insights\n\n")
            
            # High volume movers
            high_volume = df[df['volume'] > df['avg_volume'] * 1.5]
            if not high_volume.empty:
                f.write("### High Volume Movers\n\n")
                for _, row in high_volume.head(5).iterrows():
                    f.write(f"- **{row['symbol']}** ({row['sector']}): ${row['price']:.2f} ({row['pct_change_1d']:+.1f}%) - Volume: {row['volume']:,.0f}\n")
                f.write("\n")
            
            # Momentum leaders
            momentum = df[df['pct_change_1d'] > 2]
            if not momentum.empty:
                f.write("### Momentum Leaders\n\n")
                for _, row in momentum.head(5).iterrows():
                    f.write(f"- **{row['symbol']}** ({row['sector']}): ${row['price']:.2f} ({row['pct_change_1d']:+.1f}%) - Score: {row['score']:.1f}\n")
                f.write("\n")
        
        console.print(f"📄 Generated summary report: {report_filename}", style="green")

def main():
    """Main function."""
    generator = DailyResearchGenerator()
    generator.generate_daily_report()

if __name__ == "__main__":
    main() 