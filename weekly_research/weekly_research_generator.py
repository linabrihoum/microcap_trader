#!/usr/bin/env python3
"""
Weekly Research Report Generator
Automatically generates comprehensive weekly analysis reports for the microcap portfolio
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our enhanced trader
from enhanced_microcap_trader import EnhancedMicrocapTrader

console = Console()

class WeeklyResearchGenerator:
    """Generates comprehensive weekly research reports."""
    
    def __init__(self):
        self.trader = EnhancedMicrocapTrader()
        self.weekly_folder = "weekly_research"
        self.ensure_weekly_folder()
    
    def ensure_weekly_folder(self):
        """Ensure the Weekly_Research folder exists."""
        if not os.path.exists(self.weekly_folder):
            os.makedirs(self.weekly_folder)
            console.print(f"✅ Created {self.weekly_folder} directory", style="green")
    
    def get_week_number(self):
        """Get the current week number for the year."""
        today = datetime.now()
        week_number = today.isocalendar()[1]
        return week_number
    
    def calculate_portfolio_metrics(self, portfolio_df):
        """Calculate comprehensive portfolio metrics."""
        if portfolio_df.empty:
            return {}
        
        total_invested = (portfolio_df['buy_price'] * portfolio_df['shares']).sum()
        current_value = (portfolio_df['current_price'] * portfolio_df['shares']).sum()
        total_pnl = portfolio_df['pnl'].sum()
        pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        # Calculate individual position percentages
        portfolio_df['position_value'] = portfolio_df['current_price'] * portfolio_df['shares']
        portfolio_df['position_pct'] = (portfolio_df['position_value'] / current_value * 100)
        
        # Risk metrics
        volatility = portfolio_df['pnl'].std()
        max_drawdown = portfolio_df['pnl'].min()
        best_performer = portfolio_df.loc[portfolio_df['pnl'].idxmax()]
        worst_performer = portfolio_df.loc[portfolio_df['pnl'].idxmin()]
        
        return {
            'total_invested': total_invested,
            'current_value': current_value,
            'total_pnl': total_pnl,
            'pnl_percentage': pnl_percentage,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'position_count': len(portfolio_df)
        }
    
    def analyze_stock(self, symbol, row):
        """Analyze individual stock performance and outlook."""
        # Calculate P&L percentage
        pnl_pct = (row['pnl'] / (row['buy_price'] * row['shares']) * 100)
        
        # Determine status and score
        if pnl_pct >= 10:
            status = "🚀 Strong Performer"
            score = 9
        elif pnl_pct >= 5:
            status = "✅ Positive Momentum"
            score = 7
        elif pnl_pct >= 0:
            status = "📈 Stable"
            score = 6
        elif pnl_pct >= -5:
            status = "⚠️ Under Pressure"
            score = 4
        else:
            status = "🔴 Needs Attention"
            score = 3
        
        # Determine outlook based on performance
        if pnl_pct > 15:
            outlook = "Very Bullish - Strong momentum"
        elif pnl_pct > 5:
            outlook = "Bullish - Positive trend"
        elif pnl_pct > -2:
            outlook = "Neutral - Monitor closely"
        elif pnl_pct > -8:
            outlook = "Cautious - Consider stop loss"
        else:
            outlook = "Bearish - Consider exit"
        
        return {
            'status': status,
            'score': score,
            'outlook': outlook,
            'pnl_pct': pnl_pct
        }
    
    def get_sector_analysis(self, symbol):
        """Get sector-specific analysis."""
        sector_analysis = {
            'SNDL': {
                'sector': 'Cannabis',
                'sentiment': 'Improving',
                'catalysts': ['Legalization momentum', 'Cost-cutting measures', 'Brand consolidation'],
                'risks': ['Regulatory uncertainty', 'High competition', 'Seasonal demand']
            },
            'ATAI': {
                'sector': 'Biotech',
                'sentiment': 'Very Bullish',
                'catalysts': ['Psychedelic therapeutics', 'Mental health crisis', 'Institutional interest'],
                'risks': ['Regulatory approval', 'Long timelines', 'High cash burn']
            },
            'FCEL': {
                'sector': 'Clean Energy',
                'sentiment': 'Neutral',
                'catalysts': ['Government support', 'Energy transition', 'Hydrogen focus'],
                'risks': ['High capital requirements', 'Technology adoption', 'Competition']
            },
            'STIM': {
                'sector': 'Healthcare',
                'sentiment': 'Cautious',
                'catalysts': ['Mental health awareness', 'FDA approvals', 'TMS technology'],
                'risks': ['Reimbursement challenges', 'Market penetration', 'Small cap volatility']
            }
        }
        
        return sector_analysis.get(symbol, {
            'sector': 'Unknown',
            'sentiment': 'Neutral',
            'catalysts': [],
            'risks': []
        })
    
    def generate_weekly_report(self):
        """Generate comprehensive weekly research report."""
        console.print("🔬 Generating Weekly Research Report", style="bold cyan")
        console.print("=" * 50)
        
        # Get current portfolio data
        try:
            portfolio_df = pd.read_csv(self.trader.portfolio_file)
            console.print(f"📊 Loaded portfolio with {len(portfolio_df)} positions", style="green")
        except Exception as e:
            console.print(f"❌ Error loading portfolio: {e}", style="red")
            return
        
        # Calculate metrics
        metrics = self.calculate_portfolio_metrics(portfolio_df)
        
        # Generate report filename
        week_number = self.get_week_number()
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"Week_{week_number}_Summary_{current_date}.md"
        filepath = os.path.join(self.weekly_folder, filename)
        
        # Generate report content
        report_content = self.create_report_content(portfolio_df, metrics, week_number)
        
        # Save report
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            console.print(f"✅ Weekly report saved: {filepath}", style="green")
        except Exception as e:
            console.print(f"❌ Error saving report: {e}", style="red")
            return
        
        # Display summary
        self.display_summary(portfolio_df, metrics, week_number)
    
    def create_report_content(self, portfolio_df, metrics, week_number):
        """Create the complete report content."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        report = []
        report.append(f"# Weekly Deep Research Analysis - Week {week_number}")
        report.append(f"**Date:** {current_date}")
        report.append(f"**Portfolio Status:** Active Microcap Trading System")
        report.append(f"**Total Positions:** {metrics['position_count']}")
        report.append(f"**Total P&L:** ${metrics['total_pnl']:.2f} ({metrics['pnl_percentage']:+.2f}%)")
        report.append("")
        report.append("---")
        report.append("")
        
        # Portfolio Performance Summary
        report.append("## 📊 Portfolio Performance Summary")
        report.append("")
        report.append("### Current Holdings")
        report.append("| Symbol | Shares | Buy Price | Current Price | P&L | P&L % | Market Cap | Sector |")
        report.append("|--------|--------|-----------|---------------|-----|--------|------------|--------|")
        
        for _, row in portfolio_df.iterrows():
            pnl_pct = (row['pnl'] / (row['buy_price'] * row['shares']) * 100)
            sector_info = self.get_sector_analysis(row['symbol'])
            report.append(f"| **{row['symbol']}** | {int(row['shares'])} | ${row['buy_price']:.2f} | **${row['current_price']:.2f}** | **${row['pnl']:+.2f}** | **{pnl_pct:+.2f}%** | $0.XXB | {sector_info['sector']} |")
        
        report.append("")
        report.append("### Portfolio Metrics")
        report.append(f"- **Total Invested:** ${metrics['total_invested']:.2f}")
        report.append(f"- **Current Value:** ${metrics['current_value']:.2f}")
        report.append(f"- **Total P&L:** ${metrics['total_pnl']:+.2f} ({metrics['pnl_percentage']:+.2f}%)")
        report.append(f"- **Best Performer:** {metrics['best_performer']['symbol']} ({metrics['best_performer']['pnl']:+.2f})")
        report.append(f"- **Worst Performer:** {metrics['worst_performer']['symbol']} ({metrics['worst_performer']['pnl']:+.2f})")
        report.append(f"- **Volatility:** ${metrics['volatility']:.2f}")
        report.append("")
        report.append("---")
        report.append("")
        
        # Individual Stock Analysis
        report.append("## 🎯 Individual Stock Analysis")
        report.append("")
        
        for _, row in portfolio_df.iterrows():
            analysis = self.analyze_stock(row['symbol'], row)
            sector_info = self.get_sector_analysis(row['symbol'])
            
            report.append(f"### {len(report) - 30}. **{row['symbol']}** - {sector_info['sector']} Sector")
            report.append(f"**Current Status:** {analysis['status']}")
            report.append(f"**Score:** {analysis['score']}/10")
            report.append("")
            report.append("**Technical Analysis:**")
            report.append(f"- Price: ${row['current_price']:.2f} ({analysis['pnl_pct']:+.2f}% from entry)")
            report.append(f"- Shares: {int(row['shares'])}")
            report.append(f"- Position Value: ${row['current_price'] * row['shares']:.2f}")
            report.append("")
            report.append("**Fundamental Analysis:**")
            report.append("- **Strengths:**")
            for catalyst in sector_info['catalysts']:
                report.append(f"  - {catalyst}")
            report.append("- **Risks:**")
            for risk in sector_info['risks']:
                report.append(f"  - {risk}")
            report.append("")
            report.append("**Trading Strategy:**")
            report.append(f"- **Entry:** ${row['buy_price']:.2f}")
            report.append(f"- **Current:** ${row['current_price']:.2f}")
            report.append(f"- **P&L:** ${row['pnl']:+.2f} ({analysis['pnl_pct']:+.2f}%)")
            report.append("")
            report.append(f"**Weekly Outlook:** {analysis['outlook']}")
            report.append("")
            report.append("---")
            report.append("")
        
        # Trading Recommendations
        report.append("## 🎯 Trading Recommendations")
        report.append("")
        report.append("### Immediate Actions (This Week)")
        
        for _, row in portfolio_df.iterrows():
            analysis = self.analyze_stock(row['symbol'], row)
            if analysis['score'] >= 8:
                action = f"**Hold {row['symbol']}** - Strong momentum, let winners run"
            elif analysis['score'] >= 6:
                action = f"**Monitor {row['symbol']}** - Stable performance, maintain position"
            elif analysis['score'] >= 4:
                action = f"**Watch {row['symbol']}** - Under pressure, set stop loss"
            else:
                action = f"**Evaluate {row['symbol']}** - Consider exit if no recovery"
            report.append(f"{len(report) - 30}. {action}")
        
        report.append("")
        report.append("### Risk Management")
        report.append("- **Total Portfolio Risk:** Medium")
        report.append("- **Diversification:** Good (Multiple sectors)")
        report.append("- **Stop Loss Strategy:** 8-12% per position")
        report.append("- **Take Profit Targets:** 15-25% gains")
        report.append("")
        report.append("---")
        report.append("")
        
        # Next Week's Focus
        report.append("## 🎯 Next Week's Focus")
        report.append("")
        report.append("### Primary Objectives")
        report.append("1. **Monitor strong performers** - Let winners run")
        report.append("2. **Evaluate underperformers** - Set stop losses")
        report.append("3. **Research new opportunities** - Look for microcap candidates")
        report.append("4. **Review position sizing** - Adjust based on performance")
        report.append("")
        report.append("### Research Priorities")
        report.append("1. **Sector analysis** - Monitor sector rotation")
        report.append("2. **Market conditions** - Assess microcap environment")
        report.append("3. **Risk management** - Review stop losses and targets")
        report.append("4. **New opportunities** - Screen for potential additions")
        report.append("")
        report.append("---")
        report.append("")
        
        # Weekly Notes
        report.append("## 📝 Weekly Notes")
        report.append("")
        report.append("### What Worked This Week")
        report.append("- Portfolio diversification reducing risk")
        report.append("- Strong performers showing momentum")
        report.append("- Proper position sizing")
        report.append("")
        report.append("### What Needs Improvement")
        report.append("- Monitor underperformers closely")
        report.append("- Set tighter stop losses")
        report.append("- Consider profit taking on strong performers")
        report.append("")
        report.append("### Lessons Learned")
        report.append("1. **Diversification** - Key to managing microcap risk")
        report.append("2. **Position sizing** - Critical for portfolio balance")
        report.append("3. **Risk management** - Essential for long-term success")
        report.append("")
        report.append("---")
        report.append("")
        
        # Conclusion
        report.append("## 🚀 Conclusion")
        report.append("")
        report.append("This week's portfolio demonstrates the importance of diversification and risk management in microcap investing. The portfolio shows balanced performance across different sectors with proper position sizing.")
        report.append("")
        report.append("**Key Takeaway:** Microcap investing requires patience, research, and strict risk management. The portfolio is well-positioned for continued growth.")
        report.append("")
        report.append("**Next Week's Goal:** Maintain momentum while protecting gains and evaluating new opportunities.")
        report.append("")
        report.append("---")
        report.append("")
        report.append("*Analysis generated by Enhanced Microcap Trading System*")
        report.append(f"*Date: {current_date}*")
        report.append(f"*Portfolio Value: ${metrics['current_value']:.2f}*")
        report.append(f"*Total P&L: ${metrics['total_pnl']:+.2f} ({metrics['pnl_percentage']:+.2f}%)*")
        
        return '\n'.join(report)
    
    def display_summary(self, portfolio_df, metrics, week_number):
        """Display a summary of the generated report."""
        console.print(f"\n📋 Weekly Report Summary - Week {week_number}", style="bold cyan")
        console.print("=" * 50)
        
        # Portfolio summary table
        table = Table(title="Portfolio Summary")
        table.add_column("Symbol", style="cyan")
        table.add_column("Shares", justify="right")
        table.add_column("Current Price", justify="right")
        table.add_column("P&L", justify="right")
        table.add_column("P&L %", justify="right")
        
        for _, row in portfolio_df.iterrows():
            pnl_pct = (row['pnl'] / (row['buy_price'] * row['shares']) * 100)
            pnl_style = "green" if row['pnl'] >= 0 else "red"
            
            table.add_row(
                row['symbol'],
                str(int(row['shares'])),
                f"${row['current_price']:.2f}",
                f"${row['pnl']:+.2f}",
                f"{pnl_pct:+.2f}%",
                style=pnl_style
            )
        
        console.print(table)
        
        # Key metrics
        console.print(f"\n💰 Portfolio Metrics:", style="bold")
        console.print(f"   Total Invested: ${metrics['total_invested']:.2f}")
        console.print(f"   Current Value: ${metrics['current_value']:.2f}")
        console.print(f"   Total P&L: ${metrics['total_pnl']:+.2f} ({metrics['pnl_percentage']:+.2f}%)")
        console.print(f"   Positions: {metrics['position_count']}")
        
        console.print(f"\n✅ Weekly report generated successfully!", style="bold green")
        console.print(f"📁 Location: weekly_research/Week_{week_number}_Summary_{datetime.now().strftime('%Y-%m-%d')}.md")

def main():
    """Main function to generate weekly research report."""
    generator = WeeklyResearchGenerator()
    generator.generate_weekly_report()

if __name__ == "__main__":
    main() 