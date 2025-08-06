#!/usr/bin/env python3
"""
Weekly Aggregator
Combines all daily research from the week into a comprehensive weekly report
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import glob

console = Console()

class WeeklyAggregator:
    """Aggregates daily research into weekly insights."""
    
    def __init__(self):
        self.daily_folder = "daily_research"
        self.weekly_folder = "weekly_research"
        self.ensure_folders()
    
    def ensure_folders(self):
        """Ensure required folders exist."""
        for folder in [self.daily_folder, self.weekly_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                console.print(f"✅ Created {folder} directory", style="green")
    
    def get_week_dates(self):
        """Get the dates for the current week (Monday to Friday)."""
        today = datetime.now()
        # Find Monday of current week
        monday = today - timedelta(days=today.weekday())
        week_dates = []
        
        for i in range(5):  # Monday to Friday
            week_dates.append(monday + timedelta(days=i))
        
        return week_dates
    
    def load_daily_data(self):
        """Load all daily research data from the week."""
        week_dates = self.get_week_dates()
        all_candidates = []
        daily_summaries = []
        
        console.print("📅 Loading daily research from this week...", style="blue")
        
        for date in week_dates:
            date_str = date.strftime('%Y%m%d')
            
            # Try to load daily candidates
            candidates_file = os.path.join(self.daily_folder, f"daily_candidates_{date_str}.json")
            if os.path.exists(candidates_file):
                try:
                    with open(candidates_file, 'r') as f:
                        data = json.load(f)
                        candidates = data.get('candidates', [])
                        all_candidates.extend(candidates)
                        console.print(f"✅ Loaded {len(candidates)} candidates from {date.strftime('%Y-%m-%d')}", style="green")
                except Exception as e:
                    console.print(f"⚠️ Error loading {candidates_file}: {str(e)}", style="yellow")
            
            # Try to load daily summary
            summary_file = os.path.join(self.daily_folder, f"daily_summary_{date_str}.md")
            if os.path.exists(summary_file):
                daily_summaries.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'file': summary_file
                })
        
        return all_candidates, daily_summaries
    
    def analyze_weekly_trends(self, candidates):
        """Analyze trends from the week's candidates."""
        if not candidates:
            return {}
        
        df = pd.DataFrame(candidates)
        
        # Add date column for analysis
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        analysis = {
            'total_candidates': len(candidates),
            'unique_symbols': df['symbol'].nunique(),
            'sector_breakdown': df['sector'].value_counts().to_dict(),
            'avg_score': df['score'].mean(),
            'top_sectors': df.groupby('sector')['score'].mean().sort_values(ascending=False).head(3).to_dict(),
            'top_performers': df.nlargest(10, 'score')[['symbol', 'sector', 'score', 'pct_change_1d', 'pct_change_5d']].to_dict('records'),
            'volume_leaders': df.nlargest(10, 'volume')[['symbol', 'sector', 'volume', 'avg_volume', 'pct_change_1d']].to_dict('records'),
            'momentum_leaders': df.nlargest(10, 'pct_change_1d')[['symbol', 'sector', 'pct_change_1d', 'score']].to_dict('records')
        }
        
        # Daily trends
        daily_trends = df.groupby('date').agg({
            'symbol': 'count',
            'score': 'mean',
            'pct_change_1d': 'mean'
        }).round(2)
        # Convert date objects to strings for JSON serialization
        analysis['daily_trends'] = {str(date): trends.to_dict() for date, trends in daily_trends.iterrows()}
        
        return analysis
    
    def generate_weekly_report(self, candidates, daily_summaries, analysis):
        """Generate comprehensive weekly report."""
        week_start = self.get_week_dates()[0]
        week_end = self.get_week_dates()[-1]
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_filename = f"Week_{week_start.isocalendar()[1]}_Summary_{timestamp}.md"
        report_path = os.path.join(self.weekly_folder, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Week {week_start.isocalendar()[1]} Summary - {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Period:** {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Candidates Analyzed:** {analysis['total_candidates']}\n")
            f.write(f"- **Unique Symbols:** {analysis['unique_symbols']}\n")
            f.write(f"- **Average Score:** {analysis['avg_score']:.1f}\n")
            f.write(f"- **Top Performing Sector:** {list(analysis['top_sectors'].keys())[0] if analysis['top_sectors'] else 'N/A'}\n\n")
            
            # Sector Analysis
            f.write("## Sector Analysis\n\n")
            f.write("| Sector | Count | Avg Score |\n")
            f.write("|--------|-------|-----------|\n")
            
            for sector, count in analysis['sector_breakdown'].items():
                avg_score = analysis['top_sectors'].get(sector, 0)
                f.write(f"| {sector} | {count} | {avg_score:.1f} |\n")
            
            f.write("\n")
            
            # Top Performers
            f.write("## Top 10 Candidates by Score\n\n")
            f.write("| Rank | Symbol | Sector | Score | 1D Change | 5D Change |\n")
            f.write("|------|--------|--------|-------|------------|-----------|\n")
            
            for i, candidate in enumerate(analysis['top_performers'][:10], 1):
                f.write(f"| {i} | {candidate['symbol']} | {candidate['sector']} | {candidate['score']:.1f} | {candidate['pct_change_1d']:+.1f}% | {candidate['pct_change_5d']:+.1f}% |\n")
            
            f.write("\n")
            
            # Volume Leaders
            f.write("## Volume Leaders\n\n")
            f.write("| Rank | Symbol | Sector | Volume | Avg Volume | 1D Change |\n")
            f.write("|------|--------|--------|--------|------------|------------|\n")
            
            for i, candidate in enumerate(analysis['volume_leaders'][:10], 1):
                volume_ratio = candidate['volume'] / candidate['avg_volume']
                f.write(f"| {i} | {candidate['symbol']} | {candidate['sector']} | {candidate['volume']:,.0f} | {volume_ratio:.1f}x | {candidate['pct_change_1d']:+.1f}% |\n")
            
            f.write("\n")
            
            # Momentum Leaders
            f.write("## Momentum Leaders\n\n")
            f.write("| Rank | Symbol | Sector | 1D Change | Score |\n")
            f.write("|------|--------|--------|------------|-------|\n")
            
            for i, candidate in enumerate(analysis['momentum_leaders'][:10], 1):
                f.write(f"| {i} | {candidate['symbol']} | {candidate['sector']} | {candidate['pct_change_1d']:+.1f}% | {candidate['score']:.1f} |\n")
            
            f.write("\n")
            
            # Daily Trends
            f.write("## Daily Trends\n\n")
            f.write("| Date | Candidates | Avg Score | Avg 1D Change |\n")
            f.write("|------|------------|-----------|----------------|\n")
            
            for date, trends in analysis['daily_trends'].items():
                f.write(f"| {date} | {trends['symbol']} | {trends['score']:.1f} | {trends['pct_change_1d']:+.1f}% |\n")
            
            f.write("\n")
            
            # Market Insights
            f.write("## Market Insights\n\n")
            
            # Best performing day
            best_day = max(analysis['daily_trends'].items(), key=lambda x: x[1]['score'])
            f.write(f"- **Best Performing Day:** {best_day[0]} (Avg Score: {best_day[1]['score']:.1f})\n")
            
            # Most active sector
            most_active_sector = max(analysis['sector_breakdown'].items(), key=lambda x: x[1])
            f.write(f"- **Most Active Sector:** {most_active_sector[0]} ({most_active_sector[1]} candidates)\n")
            
            # High momentum stocks
            high_momentum = [c for c in analysis['momentum_leaders'] if c['pct_change_1d'] > 5]
            if high_momentum:
                f.write(f"- **High Momentum Stocks:** {len(high_momentum)} stocks with >5% daily gains\n")
            
            f.write("\n")
            
            # Recommendations
            f.write("## Weekly Recommendations\n\n")
            
            # Sector recommendations
            top_sector = list(analysis['top_sectors'].keys())[0] if analysis['top_sectors'] else None
            if top_sector:
                f.write(f"- **Focus Sector:** {top_sector} - Best average score ({analysis['top_sectors'][top_sector]:.1f})\n")
            
            # Top candidates for next week
            f.write("- **Top Candidates for Next Week:**\n")
            for i, candidate in enumerate(analysis['top_performers'][:5], 1):
                f.write(f"  {i}. {candidate['symbol']} ({candidate['sector']}) - Score: {candidate['score']:.1f}\n")
            
            f.write("\n")
            
            # Daily Summaries
            f.write("## Daily Summaries\n\n")
            for summary in daily_summaries:
                f.write(f"### {summary['date']}\n")
                f.write(f"*[View full report]({summary['file']})*\n\n")
        
        console.print(f"📄 Generated weekly report: {report_filename}", style="green")
        return report_path
    
    def save_weekly_data(self, candidates, analysis):
        """Save weekly aggregated data to JSON for ML processing."""
        timestamp = datetime.now().strftime('%Y%m%d')
        json_filename = f"weekly_data_{timestamp}.json"
        json_path = os.path.join(self.weekly_folder, json_filename)
        
        weekly_data = {
            'week_start': self.get_week_dates()[0].isoformat(),
            'week_end': self.get_week_dates()[-1].isoformat(),
            'total_candidates': len(candidates),
            'analysis': analysis,
            'candidates': candidates
        }
        
        with open(json_path, 'w') as f:
            json.dump(weekly_data, f, indent=2)
        
        console.print(f"💾 Saved weekly data to {json_filename}", style="green")
        return json_path
    
    def aggregate_weekly_research(self):
        """Main function to aggregate weekly research."""
        console.print("🔄 Starting weekly aggregation...", style="blue")
        
        # Load daily data
        candidates, daily_summaries = self.load_daily_data()
        
        if not candidates:
            console.print("❌ No daily research data found for this week", style="red")
            return
        
        # Analyze trends
        analysis = self.analyze_weekly_trends(candidates)
        
        # Generate reports
        report_path = self.generate_weekly_report(candidates, daily_summaries, analysis)
        data_path = self.save_weekly_data(candidates, analysis)
        
        # Display summary
        self.display_summary(analysis)
        
        console.print("✅ Weekly aggregation completed successfully!", style="green")
        console.print(f"📁 Reports saved to: {self.weekly_folder}", style="cyan")
    
    def display_summary(self, analysis):
        """Display a summary of the weekly aggregation."""
        console.print("\n" + "="*80)
        console.print("📊 WEEKLY AGGREGATION SUMMARY", style="bold blue")
        console.print("="*80)
        
        # Key metrics table
        metrics_table = Table(title="📈 Weekly Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        metrics_table.add_row("Total Candidates", str(analysis['total_candidates']))
        metrics_table.add_row("Unique Symbols", str(analysis['unique_symbols']))
        metrics_table.add_row("Average Score", f"{analysis['avg_score']:.1f}")
        metrics_table.add_row("Top Sector", list(analysis['top_sectors'].keys())[0] if analysis['top_sectors'] else 'N/A')
        
        console.print(metrics_table)
        
        # Top performers table
        if analysis['top_performers']:
            top_table = Table(title="🏆 Top 5 Candidates")
            top_table.add_column("Rank", style="cyan")
            top_table.add_column("Symbol", style="green")
            top_table.add_column("Sector", style="yellow")
            top_table.add_column("Score", style="magenta")
            top_table.add_column("1D Change", style="red")
            
            for i, candidate in enumerate(analysis['top_performers'][:5], 1):
                top_table.add_row(
                    str(i),
                    candidate['symbol'],
                    candidate['sector'],
                    f"{candidate['score']:.1f}",
                    f"{candidate['pct_change_1d']:+.1f}%"
                )
            
            console.print(top_table)

def main():
    """Main function."""
    aggregator = WeeklyAggregator()
    aggregator.aggregate_weekly_research()

if __name__ == "__main__":
    main() 