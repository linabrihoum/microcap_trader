#!/usr/bin/env python3
"""
Example usage of the Microcap Trading System
This script demonstrates how to use the system programmatically.
"""

from microcap_trader_single import MicrocapTrader
from rich.console import Console

console = Console()

def main():
    """Demonstrate the microcap trading system."""
    
    # Initialize the trader
    trader = MicrocapTrader()
    
    console.print("🚀 Microcap Trading System Demo", style="bold cyan")
    console.print("=" * 50)
    
    # Step 1: Run daily update
    console.print("\n1. Running daily update...")
    trader.run_daily_update()
    
    # Step 2: Add some example positions
    console.print("\n2. Adding example positions...")
    example_positions = [
        ("AAPL", 100, 150.00),
        ("MSFT", 50, 300.00),
        ("GOOGL", 25, 2800.00)
    ]
    
    for symbol, shares, price in example_positions:
        trader.add_position(symbol, shares, price)
    
    # Step 3: Show portfolio
    console.print("\n3. Current portfolio:")
    trader.show_portfolio()
    
    # Step 4: Show candidates
    console.print("\n4. Top candidates:")
    trader.show_candidates()
    
    console.print("\n✅ Demo completed! Check the generated files:")
    console.print("- portfolio.csv: Your positions")
    console.print("- candidates.csv: Daily candidates")
    console.print("- daily_report.md: Comprehensive report")


if __name__ == "__main__":
    main() 