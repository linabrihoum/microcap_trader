#!/usr/bin/env python3
"""
ML Insights Generator
Analyzes weekly research data and generates actionable insights for the trading bot
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import numpy as np

console = Console()

class MLInsightsGenerator:
    """Generates ML insights from weekly research for the trading bot."""
    
    def __init__(self):
        self.insights_folder = "weekly_research/summaries"
        self.trading_history_file = "../machine_learning/trading_history.csv"
        self.portfolio_file = "../data/portfolio.csv"
    
    def analyze_trading_patterns(self):
        """Analyze trading patterns from history and current portfolio."""
        insights = {
            'timestamp': datetime.now().isoformat(),
            'sector_analysis': {},
            'performance_metrics': {},
            'risk_analysis': {},
            'trading_recommendations': [],
            'ml_bot_enhancements': {}
        }
        
        try:
            # Load trading history
            if os.path.exists(self.trading_history_file):
                trading_df = pd.read_csv(self.trading_history_file)
                insights['trading_history_analysis'] = self.analyze_trading_history(trading_df)
            
            # Load current portfolio
            if os.path.exists(self.portfolio_file):
                portfolio_df = pd.read_csv(self.portfolio_file)
                insights['portfolio_analysis'] = self.analyze_portfolio(portfolio_df)
            
            # Generate sector insights
            insights['sector_analysis'] = self.analyze_sector_performance(trading_df, portfolio_df)
            
            # Generate risk insights
            insights['risk_analysis'] = self.analyze_risk_metrics(trading_df, portfolio_df)
            
            # Generate trading recommendations
            insights['trading_recommendations'] = self.generate_trading_recommendations(insights)
            
            # Generate ML bot enhancements
            insights['ml_bot_enhancements'] = self.generate_ml_enhancements(insights)
            
        except Exception as e:
            console.print(f"❌ Error analyzing patterns: {str(e)}", style="red")
        
        return insights
    
    def analyze_trading_history(self, df):
        """Analyze trading history patterns."""
        if df.empty:
            return {}
        
        closed_trades = df[df['status'] == 'CLOSED']
        
        if closed_trades.empty:
            return {}
        
        # Sector performance
        sector_perf = {}
        if 'type_market' in closed_trades.columns:
            sector_perf = closed_trades.groupby('type_market').agg({
                'pnl': ['sum', 'mean', 'count'],
                'pnl_percentage': ['mean', 'std']
            }).round(2)
        
        # Time-based analysis
        if 'hold_days' in closed_trades.columns:
            hold_analysis = {
                'avg_hold_days': closed_trades['hold_days'].mean(),
                'best_hold_period': closed_trades.groupby('hold_days')['pnl_percentage'].mean().idxmax(),
                'quick_wins': len(closed_trades[closed_trades['hold_days'] <= 7])
            }
        else:
            hold_analysis = {}
        
        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(closed_trades[closed_trades['pnl'] > 0]),
            'losing_trades': len(closed_trades[closed_trades['pnl'] < 0]),
            'win_rate': len(closed_trades[closed_trades['pnl'] > 0]) / len(closed_trades) * 100,
            'avg_win': closed_trades[closed_trades['pnl'] > 0]['pnl'].mean(),
            'avg_loss': closed_trades[closed_trades['pnl'] < 0]['pnl'].mean(),
            'profit_factor': abs(closed_trades[closed_trades['pnl'] > 0]['pnl'].sum() / 
                               closed_trades[closed_trades['pnl'] < 0]['pnl'].sum()) if len(closed_trades[closed_trades['pnl'] < 0]) > 0 else float('inf'),
            'sector_performance': sector_perf.to_dict() if not sector_perf.empty else {},
            'hold_analysis': hold_analysis,
            'best_performers': closed_trades.nlargest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'type_market']].to_dict('records'),
            'worst_performers': closed_trades.nsmallest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'type_market']].to_dict('records')
        }
    
    def analyze_portfolio(self, df):
        """Analyze current portfolio performance."""
        if df.empty:
            return {}
        
        # Calculate metrics
        total_invested = (df['buy_price'] * df['shares']).sum()
        current_value = (df['current_price'] * df['shares']).sum()
        total_pnl = df['pnl'].sum()
        pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        # Sector analysis
        sector_analysis = {}
        if 'type_market' in df.columns:
            sector_analysis = df.groupby('type_market').agg({
                'pnl': ['sum', 'mean'],
                'pnl_percentage': 'mean'
            }).round(2)
        
        return {
            'total_positions': len(df),
            'total_invested': total_invested,
            'current_value': current_value,
            'total_pnl': total_pnl,
            'pnl_percentage': pnl_percentage,
            'winning_positions': len(df[df['pnl'] > 0]),
            'losing_positions': len(df[df['pnl'] < 0]),
            'sector_breakdown': sector_analysis.to_dict() if not sector_analysis.empty else {},
            'top_positions': df.nlargest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'type_market']].to_dict('records'),
            'worst_positions': df.nsmallest(3, 'pnl_percentage')[['symbol', 'pnl_percentage', 'type_market']].to_dict('records')
        }
    
    def analyze_sector_performance(self, trading_df, portfolio_df):
        """Analyze sector performance across trading history and current portfolio."""
        sector_insights = {}
        
        # Combine trading history and portfolio for sector analysis
        all_positions = []
        
        if not trading_df.empty and 'type_market' in trading_df.columns:
            closed_trades = trading_df[trading_df['status'] == 'CLOSED']
            all_positions.extend(closed_trades[['symbol', 'pnl_percentage', 'type_market']].to_dict('records'))
        
        if not portfolio_df.empty and 'type_market' in portfolio_df.columns:
            all_positions.extend(portfolio_df[['symbol', 'pnl_percentage', 'type_market']].to_dict('records'))
        
        if all_positions:
            positions_df = pd.DataFrame(all_positions)
            sector_perf = positions_df.groupby('type_market').agg({
                'pnl_percentage': ['mean', 'std', 'count']
            }).round(2)
            
            for sector in sector_perf.index:
                sector_insights[sector] = {
                    'avg_performance': sector_perf.loc[sector, ('pnl_percentage', 'mean')],
                    'volatility': sector_perf.loc[sector, ('pnl_percentage', 'std')],
                    'trade_count': sector_perf.loc[sector, ('pnl_percentage', 'count')],
                    'recommendation': self.get_sector_recommendation(sector, sector_perf.loc[sector])
                }
        
        return sector_insights
    
    def get_sector_recommendation(self, sector, metrics):
        """Get trading recommendation for a sector."""
        avg_perf = metrics[('pnl_percentage', 'mean')]
        volatility = metrics[('pnl_percentage', 'std')]
        count = metrics[('pnl_percentage', 'count')]
        
        if avg_perf > 5 and volatility < 10:
            return "Strong Buy - Consistent positive performance"
        elif avg_perf > 0 and volatility < 15:
            return "Buy - Positive performance with manageable risk"
        elif avg_perf > -5 and volatility < 20:
            return "Hold - Mixed performance, monitor closely"
        else:
            return "Avoid - Poor performance or high volatility"
    
    def analyze_risk_metrics(self, trading_df, portfolio_df):
        """Analyze risk metrics for ML bot enhancement."""
        risk_metrics = {}
        
        # Combine all positions for risk analysis
        all_pnl = []
        
        if not trading_df.empty:
            closed_trades = trading_df[trading_df['status'] == 'CLOSED']
            all_pnl.extend(closed_trades['pnl'].tolist())
        
        if not portfolio_df.empty:
            all_pnl.extend(portfolio_df['pnl'].tolist())
        
        if all_pnl:
            pnl_array = np.array(all_pnl)
            risk_metrics = {
                'total_trades': len(all_pnl),
                'win_rate': len(pnl_array[pnl_array > 0]) / len(pnl_array) * 100,
                'avg_return': pnl_array.mean(),
                'volatility': pnl_array.std(),
                'max_drawdown': pnl_array.min(),
                'max_gain': pnl_array.max(),
                'sharpe_ratio': pnl_array.mean() / pnl_array.std() if pnl_array.std() > 0 else 0,
                'risk_reward_ratio': abs(pnl_array.max() / pnl_array.min()) if pnl_array.min() != 0 else 0
            }
        
        return risk_metrics
    
    def generate_trading_recommendations(self, insights):
        """Generate actionable trading recommendations."""
        recommendations = []
        
        # Sector-based recommendations
        if 'sector_analysis' in insights:
            for sector, data in insights['sector_analysis'].items():
                if data['avg_performance'] > 5:
                    recommendations.append({
                        'type': 'sector_focus',
                        'action': f'Increase exposure to {sector} sector',
                        'reason': f'Strong performance: {data["avg_performance"]:.1f}% average return',
                        'confidence': 'High'
                    })
                elif data['avg_performance'] < -5:
                    recommendations.append({
                        'type': 'sector_avoid',
                        'action': f'Reduce exposure to {sector} sector',
                        'reason': f'Poor performance: {data["avg_performance"]:.1f}% average return',
                        'confidence': 'High'
                    })
        
        # Risk management recommendations
        if 'risk_analysis' in insights:
            risk = insights['risk_analysis']
            if risk.get('win_rate', 0) < 30:
                recommendations.append({
                    'type': 'risk_management',
                    'action': 'Implement stricter stop-losses',
                    'reason': f'Low win rate: {risk["win_rate"]:.1f}%',
                    'confidence': 'High'
                })
            
            if risk.get('volatility', 0) > 10:
                recommendations.append({
                    'type': 'risk_management',
                    'action': 'Reduce position sizes',
                    'reason': f'High volatility: {risk["volatility"]:.1f}',
                    'confidence': 'Medium'
                })
        
        # Performance-based recommendations
        if 'trading_history_analysis' in insights:
            history = insights['trading_history_analysis']
            if history.get('profit_factor', 0) < 1.0:
                recommendations.append({
                    'type': 'strategy_improvement',
                    'action': 'Focus on proven winners',
                    'reason': f'Low profit factor: {history["profit_factor"]:.2f}',
                    'confidence': 'High'
                })
        
        return recommendations
    
    def generate_ml_enhancements(self, insights):
        """Generate ML bot enhancement suggestions."""
        enhancements = {
            'scoring_adjustments': {},
            'sector_weights': {},
            'risk_parameters': {},
            'new_features': []
        }
        
        # Sector-based scoring adjustments
        if 'sector_analysis' in insights:
            for sector, data in insights['sector_analysis'].items():
                if data['avg_performance'] > 5:
                    enhancements['sector_weights'][sector] = 1.5  # Boost high-performing sectors
                elif data['avg_performance'] < -5:
                    enhancements['sector_weights'][sector] = 0.5  # Reduce low-performing sectors
        
        # Risk parameter adjustments
        if 'risk_analysis' in insights:
            risk = insights['risk_analysis']
            if risk.get('win_rate', 0) < 30:
                enhancements['risk_parameters']['stop_loss'] = 0.03  # Tighter stop-loss
                enhancements['risk_parameters']['max_position'] = 0.15  # Smaller positions
            elif risk.get('win_rate', 0) > 60:
                enhancements['risk_parameters']['max_position'] = 0.35  # Larger positions
        
        # New features based on patterns
        if 'trading_history_analysis' in insights:
            history = insights['trading_history_analysis']
            if 'hold_analysis' in history:
                hold_data = history['hold_analysis']
                if hold_data.get('quick_wins', 0) > 0:
                    enhancements['new_features'].append('momentum_scoring')
                if hold_data.get('avg_hold_days', 0) > 10:
                    enhancements['new_features'].append('long_term_trend_analysis')
        
        return enhancements
    
    def save_insights(self, insights):
        """Save insights to JSON file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ml_insights_{timestamp}.json"
            filepath = os.path.join(self.insights_folder, filename)
            
            with open(filepath, 'w') as f:
                json.dump(insights, f, indent=2)
            
            console.print(f"💾 Saved ML insights to {filename}", style="green")
            return filepath
            
        except Exception as e:
            console.print(f"❌ Error saving insights: {str(e)}", style="red")
            return None
    
    def display_insights(self, insights):
        """Display insights in a formatted way."""
        console.print("\n" + "="*80)
        console.print("🤖 ML INSIGHTS GENERATOR", style="bold blue")
        console.print("="*80)
        
        # Display key metrics
        if 'trading_history_analysis' in insights:
            history = insights['trading_history_analysis']
            metrics_table = Table(title="📊 Trading Performance Metrics")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")
            
            metrics_table.add_row("Win Rate", f"{history.get('win_rate', 0):.1f}%")
            metrics_table.add_row("Total Trades", str(history.get('total_trades', 0)))
            metrics_table.add_row("Profit Factor", f"{history.get('profit_factor', 0):.2f}")
            metrics_table.add_row("Average Win", f"${history.get('avg_win', 0):.2f}")
            metrics_table.add_row("Average Loss", f"${history.get('avg_loss', 0):.2f}")
            
            console.print(metrics_table)
        
        # Display sector analysis
        if 'sector_analysis' in insights:
            sector_table = Table(title="🏭 Sector Performance Analysis")
            sector_table.add_column("Sector", style="cyan")
            sector_table.add_column("Avg Performance", style="green")
            sector_table.add_column("Volatility", style="yellow")
            sector_table.add_column("Recommendation", style="blue")
            
            for sector, data in insights['sector_analysis'].items():
                sector_table.add_row(
                    sector,
                    f"{data['avg_performance']:.1f}%",
                    f"{data['volatility']:.1f}%",
                    data['recommendation']
                )
            
            console.print(sector_table)
        
        # Display recommendations
        if 'trading_recommendations' in insights:
            rec_table = Table(title="🎯 Trading Recommendations")
            rec_table.add_column("Type", style="cyan")
            rec_table.add_column("Action", style="green")
            rec_table.add_column("Reason", style="yellow")
            rec_table.add_column("Confidence", style="blue")
            
            for rec in insights['trading_recommendations']:
                rec_table.add_row(
                    rec['type'].replace('_', ' ').title(),
                    rec['action'],
                    rec['reason'],
                    rec['confidence']
                )
            
            console.print(rec_table)

def main():
    """Main function."""
    generator = MLInsightsGenerator()
    
    console.print("🔄 Generating ML insights from trading data...", style="blue")
    
    insights = generator.analyze_trading_patterns()
    
    if insights:
        generator.display_insights(insights)
        filepath = generator.save_insights(insights)
        
        if filepath:
            console.print(f"✅ ML insights generated and saved successfully!", style="green")
            console.print(f"📁 File: {filepath}", style="cyan")
    else:
        console.print("❌ Failed to generate insights", style="red")

if __name__ == "__main__":
    main() 