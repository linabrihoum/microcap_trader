#!/usr/bin/env python3
"""
Test script for the Enhanced Microcap Trading System
Demonstrates API key detection and data source selection
"""

from dotenv import load_dotenv
import os
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()

def test_api_keys():
    """Test which API keys are available."""
    console.print("🔍 Testing API Key Configuration", style="bold cyan")
    console.print("=" * 50)
    
    # Check Polygon.io
    polygon_key = os.getenv('POLYGON_API_KEY')
    if polygon_key and polygon_key != 'your_polygon_api_key_here':
        console.print("✅ Polygon.io API key found", style="green")
    else:
        console.print("❌ Polygon.io API key not found", style="red")
    
    # Check Finnhub
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    if finnhub_key and finnhub_key != 'your_finnhub_api_key_here':
        console.print("✅ Finnhub API key found", style="green")
    else:
        console.print("❌ Finnhub API key not found", style="red")
    
    # Summary
    if (polygon_key and polygon_key != 'your_polygon_api_key_here') or \
       (finnhub_key and finnhub_key != 'your_finnhub_api_key_here'):
        console.print("\n🎉 Enhanced data sources available!", style="bold green")
        console.print("The system will use Polygon.io and/or Finnhub for better data quality.")
    else:
        console.print("\n⚠️  No API keys found", style="yellow")
        console.print("The system will use yfinance (free) as fallback.")
    
    console.print("\n" + "=" * 50)

def test_enhanced_system():
    """Test the enhanced system."""
    try:
        from enhanced_data_manager import EnhancedDataManager
        
        console.print("🚀 Testing Enhanced Data Manager", style="bold cyan")
        console.print("=" * 50)
        
        manager = EnhancedDataManager()
        
        # Test with a few symbols
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']
        console.print(f"Testing data fetching for: {', '.join(test_symbols)}")
        
        for symbol in test_symbols:
            data = manager.get_stock_data(symbol)
            if data:
                console.print(f"✅ {symbol}: ${data['price']:.2f} ({data['pct_change_1d']:+.2f}%)")
            else:
                console.print(f"❌ {symbol}: No data available")
        
        console.print("\n✅ Enhanced system test completed!", style="green")
        
    except ImportError as e:
        console.print(f"❌ Error importing enhanced system: {e}", style="red")
        console.print("Make sure all dependencies are installed: pip install -r requirements.txt")

def main():
    """Main test function."""
    console.print(Panel.fit(
        "Enhanced Microcap Trading System Test",
        style="bold blue"
    ))
    
    # Test API keys
    test_api_keys()
    
    # Test enhanced system
    test_enhanced_system()
    
    console.print("\n📋 Next Steps:", style="bold cyan")
    console.print("1. If no API keys found, get free keys from:")
    console.print("   - Polygon.io: https://polygon.io/")
    console.print("   - Finnhub: https://finnhub.io/")
    console.print("2. Add keys to your .env file")
    console.print("3. Run: python enhanced_microcap_trader.py update")
    console.print("4. Enjoy better data quality! 🎉")

if __name__ == "__main__":
    main() 